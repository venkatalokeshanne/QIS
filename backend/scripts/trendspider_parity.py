"""
Parity harness: does QIS reproduce TrendSpider's own backtest?

Runs a ported TrendSpider strategy through QIS on the same symbol and
timeframe, then puts the result next to the number TrendSpider actually
recorded for that (strategy, ticker, timeframe, depth) in the
trendspider-automation results database.

Exact equality is not the bar and shouldn't be: the two engines are fed
by different data vendors (TwelveData here, TrendSpider's own feed
there), so bars, splits/dividend adjustment and session boundaries all
differ slightly. What this checks is whether the SHAPE matches --
comparable trade counts and same-signed returns -- which is what tells
you the rules were ported correctly, as opposed to a subtly wrong
condition that still "works".

Run:
    python scripts/trendspider_parity.py                       # default sample
    python scripts/trendspider_parity.py --strategy ts_8_21_ema_cross_long_daily
    python scripts/trendspider_parity.py --ticker AAPL --timeframe Daily --depth 3000
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from functools import lru_cache
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Go through the same path a real backtest uses: fetch_historical_bars
# alone returns a RangeIndex with a `date` COLUMN, and it is
# normalize_ohlcv (inside fetch_backtest_bars) that installs the
# DatetimeIndex every session-aware indicator needs -- VWAP, TWAP,
# opening range and anchored OBV all fail without it.
import pandas as pd  # noqa: E402

from app.services.backtest_data import fetch_backtest_bars  # noqa: E402
from app.domain.interfaces.strategy import TradeDirection  # noqa: E402
from app.strategies.registry import discover_strategies, get_strategy, strategy_registry  # noqa: E402

RESULTS_DB = Path(r"C:\Users\annev\Downloads\trendspider-automation\data\queue.db")

# TrendSpider's timeframe label -> the interval string TwelveData wants.
TF_TO_INTERVAL = {"5m": "5min", "15m": "15min", "1H": "1h", "Daily": "1day"}


def trendspider_result(strategy_title: str, ticker: str, timeframe: str, depth: int) -> dict | None:
    conn = sqlite3.connect(f"file:{RESULTS_DB}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            """SELECT trade_count, net_profit_pct, win_rate, sharpe, max_drawdown
               FROM results
               WHERE strategy_name = ? AND ticker = ? AND timeframe = ? AND depth = ?""",
            (strategy_title, ticker, timeframe, depth),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


BARS_DIR = RESULTS_DB.parent / "extraction" / "bars"

# TrendSpider timeframe label -> the resolution the bar extractor saved under.
TF_TO_RESOLUTION = {"Daily": "D", "1H": "60", "15m": "15", "5m": "5"}


@lru_cache(maxsize=8)
def _trendspider_bars(ticker: str, resolution: str):
    """TrendSpider's OWN bars, pulled via its ChartDataConnection (see
    trendspider-automation/scripts/extract_chart_bars.py).

    Using these removes the data variable entirely: on identical bars,
    any remaining difference against TrendSpider's recorded result is a
    RULE difference -- the only kind worth chasing.
    """
    path = BARS_DIR / f"{ticker}_{resolution}.json"
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    frame = pd.DataFrame(payload["bars"], columns=payload["columns"])
    # Timestamps are epoch-ms at session start in UTC. QIS's session-aware
    # indicators work off local exchange time, so convert to US/Eastern and
    # drop the tz, matching how normalize_ohlcv presents bars.
    index = (
        pd.to_datetime(frame["timestamp_ms"], unit="ms", utc=True)
        .dt.tz_convert("America/New_York")
        .dt.tz_localize(None)
    )
    frame = frame.drop(columns=["timestamp_ms"]).set_index(index)
    frame.index.name = "timestamp"
    return frame.astype(float)


@lru_cache(maxsize=8)
def _cached_bars(ticker: str, interval: str, depth: int, extended: bool):
    return fetch_backtest_bars(
        ticker, interval=interval, outputsize=depth, include_extended_hours=extended
    )


def run_one(slug: str, ticker: str, timeframe: str, depth: int, use_ts_bars: bool = False) -> dict:
    strategy = get_strategy(slug)
    supported, reason = strategy.support_status()
    if not supported:
        return {"slug": slug, "skipped": f"unsupported: {reason[:70]}"}

    title = strategy.MODEL["name"]
    reference = trendspider_result(title, ticker, timeframe, depth)
    if not reference:
        return {"slug": slug, "skipped": f"no TrendSpider row for {ticker}/{timeframe}/{depth}"}

    interval = TF_TO_INTERVAL[timeframe]
    execution = strategy.recommended_execution()
    # `depth` is a bar count in TrendSpider, so ask for the same number of
    # bars rather than a date range -- that is what defines the window.
    # Every strategy in a sweep asks for the same bars, so fetch once --
    # otherwise a 69-strategy run makes 69 identical API calls.
    bars = None
    if use_ts_bars:
        bars = _trendspider_bars(ticker, TF_TO_RESOLUTION[timeframe])
        if bars is None:
            return {"slug": slug,
                    "skipped": f"no extracted TrendSpider bars for {ticker}/{timeframe}"}
    if bars is None:
        bars = _cached_bars(ticker, interval, depth, execution.include_extended_hours)
    bars.attrs["symbol"] = ticker.upper()
    trades = strategy.run(bars, {}, execution)

    # COMPOUNDED return, because that is what TrendSpider's
    # net_profit_pct reports (an equity curve, not a sum of trade
    # percentages). Summing instead understates it badly -- on the
    # 8/21 EMA Daily check, summing gave 221.7% against TrendSpider's
    # 556.3%, while compounding the same trades gave 512.1%.
    equity = 1.0
    for trade in trades:
        if trade.entry_price and trade.exit_price:
            move = (trade.exit_price - trade.entry_price) / trade.entry_price
            # A short profits when price FALLS, so its return is the
            # negation. Using the long formula for both flips the sign on
            # every short strategy -- which is exactly why Death Cross and
            # SQ Bollinger Band Short showed matching trade counts and win
            # rates but opposite-signed returns.
            if trade.direction == TradeDirection.SHORT:
                move = -move
            equity *= 1 + move
    net_pct = (equity - 1) * 100
    wins = [t for t in trades if (t.pnl or 0) > 0]

    return {
        "slug": slug,
        "title": title,
        "bars": len(bars),
        "qis_trades": len(trades),
        "ts_trades": reference["trade_count"],
        "qis_net_pct": round(net_pct, 1),
        "ts_net_pct": reference["net_profit_pct"],
        "qis_win_rate": round(100 * len(wins) / len(trades), 1) if trades else 0.0,
        "ts_win_rate": reference["win_rate"],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strategy", default=None, help="slug; default = a sample of runnable ones")
    ap.add_argument("--ticker", default="AAPL")
    ap.add_argument("--timeframe", default="Daily", choices=list(TF_TO_INTERVAL))
    ap.add_argument("--depth", type=int, default=3000)
    ap.add_argument("--limit", type=int, default=6)
    ap.add_argument("--ts-bars", action="store_true",
                    help="run on TrendSpider's OWN extracted bars instead of TwelveData")
    args = ap.parse_args()

    discover_strategies()
    if args.strategy:
        slugs = [args.strategy]
    else:
        slugs = [
            name
            for name, cls in sorted(strategy_registry.all().items())
            if name.startswith("ts_") and cls().support_status()[0]
        ][: args.limit]

    print(f"{'strategy':<42} {'bars':>5} {'QIS tr':>7} {'TS tr':>6} "
          f"{'QIS net%':>9} {'TS net%':>9} {'QIS win%':>9} {'TS win%':>8}  match")
    print("-" * 112)
    close_matches = total = 0
    for slug in slugs:
        try:
            result = run_one(slug, args.ticker, args.timeframe, args.depth, args.ts_bars)
        except Exception as exc:  # noqa: BLE001 - a harness; report and continue
            print(f"{slug[:41]:<42} ERROR {type(exc).__name__}: {str(exc)[:45]}")
            continue
        if "skipped" in result:
            print(f"{slug[:41]:<42} -- {result['skipped']}")
            continue
        # "Close" = trade count within 10% (or 2 trades) of TrendSpider's.
        # Trade count is the sharpest test of whether the RULES were
        # ported right; net% additionally carries the data-vendor gap.
        ts_n, qis_n = result["ts_trades"], result["qis_trades"]
        is_close = ts_n is not None and (
            abs(qis_n - ts_n) <= max(2, 0.10 * ts_n)
        )
        total += 1
        close_matches += bool(is_close)

        def cell(value, width):
            return f"{value:>{width}}" if value is not None else f"{'--':>{width}}"

        print(
            f"{result['slug'][:41]:<42} {result['bars']:>5} {result['qis_trades']:>7} "
            f"{cell(result['ts_trades'], 6)} {result['qis_net_pct']:>9} "
            f"{cell(result['ts_net_pct'], 9)} {result['qis_win_rate']:>9} "
            f"{cell(result['ts_win_rate'], 8)}  {'OK' if is_close else 'diff'}"
        )

    if total:
        print("-" * 112)
        print(f"trade count within 10%: {close_matches}/{total} "
              f"({100 * close_matches / total:.0f}%)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
