"""
Build app/strategy_engine/catalog/strategies.json from the ported
TrendSpider strategies (app/strategies/trendspider/models) and the user's
own strategy classification (trendspider-automation/config/
strategy_classification.json, 2026-08-25).

The mapping from the user's family/setup to the engine's family taxonomy
is written out per strategy in FAMILY_MAP below -- a transparent, editable
table rather than inferred rules. Every judgment call is visible here.

Existing ids are preserved across rebuilds (ids never get reused), so a
logged decision keeps pointing at the same strategy.

usage (from backend/): python tools/strategy_engine/build_catalog.py
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BACKEND))

from app.strategies.registry import discover_strategies, strategy_registry  # noqa: E402

CATALOG = BACKEND / "app" / "strategy_engine" / "catalog" / "strategies.json"
CLASSIFICATION = BACKEND.parent / "trendspider-automation" / "config" / "strategy_classification.json"
if not CLASSIFICATION.exists():
    CLASSIFICATION = Path(r"C:\Users\annev\Downloads\trendspider-automation\config\strategy_classification.json")

T, B, MR, R, V, O, L, S = ("TREND_FOLLOWING", "BREAKOUT_MOMENTUM", "MEAN_REVERSION", "REVERSAL",
                           "VWAP_INTRADAY", "OSCILLATOR_MOMENTUM", "LONG_TERM_BREAKOUT", "SPECIAL_ASSET_SPECIFIC")

# slug (without "ts_") -> (primary family, secondary families, allowed tickers or None)
# The user's own classification is shown in the trailing comment.
FAMILY_MAP = {
    "1_hr_webster_power_trend_long": (T, [], None),                 # Trend / Trend continuation
    "20_50_sma_cross_long_daily": (T, [], None),                    # Moving Average / Crossover
    "30min_ema_cross_strategy": (T, [], None),                      # Moving Average / Crossover
    "5_20_ema_bull_cross_long_1_hour": (T, [], None),               # Moving Average / Crossover
    "8_21_ema_cross_long_daily": (T, [], None),                     # Moving Average / Crossover
    "8_21_ema_cross_strategy": (T, [], None),                       # Moving Average / Crossover
    "aapl_15m_rvol_reversal": (R, [S], ["AAPL"]),                   # Volume/Reversal / RVOL reversal
    "aapl_8_21_ema_cross_strategy": (T, [S], ["AAPL"]),             # (unclassified; built-in "AAPL 8/21 EMA Cross")
    "any_bullish_ma_cross_long_1_hour": (T, [], None),              # Moving Average / Crossover
    "arnaud_legoux_momentum_strategy": (T, [O], None),              # Momentum / Trend-momentum
    "basic_30m_ema_cross_strategy": (T, [], None),                  # (unclassified; built-in EMA cross)
    "bb_kc_squeeze_ttm_breakout_strategy": (B, [], None),           # Volatility/Breakout / Squeeze breakout
    "bband_breakdown": (B, [], None),                               # Bollinger / Breakdown
    "blood_in_the_streets_long_weekly": (R, [L], None),             # Trend / Long trend (buys capitulation)
    "bollinger_band_breakout_strategy": (B, [], None),              # Bollinger/Breakout / Breakout
    "bullish_fakeout_1_hour_long": (R, [], None),                   # Reversal / Failed breakdown
    "daily_stock_pick_liberation_day_weekly_strategy": (T, [], None),     # Event/Trend / Event strategy
    "daily_stock_pick_tesla_strategy_daily": (T, [S], ["TSLA"]),    # Trend / Stock-specific
    "daily_stock_pick_vwap_strategy": (V, [], None),                # VWAP / VWAP
    "death_cross_strategy": (T, [], None),                          # Moving Average / Bearish crossover
    "dema_strategy": (T, [], None),                                 # Moving Average / Trend
    "donchian_channel_long_30_min": (B, [], None),                  # Breakout / Channel breakout
    "donchian_channel_scalper_15m": (B, [], None),                  # Breakout / Channel breakout
    "donchian_crawl": (B, [T], None),                               # Breakout/Trend / Channel trend
    "double_bollinger_band_strat": (MR, [], None),                  # Bollinger / Volatility-reversion
    "earnings_run_up_long_daily": (B, [], None),                    # Event / Earnings momentum
    "earnings_runup": (B, [], None),                                # Event / Earnings momentum
    "ema_psar_trend_following": (T, [], None),                      # Trend / Trend following
    "golden_cross_strategy": (L, [T], None),                        # Moving Average / Bullish crossover (50/200)
    "golden_cross_trader_long_daily": (L, [T], None),               # Moving Average / Bullish crossover (50/200)
    "guppy_moving_average_strat": (T, [], None),                    # Trend/MA / MA trend
    "hammer_breakout_long_strategy": (B, [R], None),                # Candlestick/Breakout / Hammer breakout
    "high_volume_hammer": (R, [], None),                            # Candlestick/Volume / Hammer + volume
    "hilbert_transform_long_strategy": (T, [], None),               # Trend / Adaptive trend
    "hull_crossover_strategy": (T, [], None),                       # Moving Average / Crossover
    "ichimoku_oversold_long_30_min": (R, [], None),                 # Ichimoku/Reversal / Oversold reversal
    "inside_bar_break_long": (B, [], None),                         # Breakout / Inside-bar breakout
    "keltner_channel_bounce": (MR, [], None),                       # Mean Reversion / Channel bounce
    "least_squares_moving_average_strategy": (T, [], None),         # Moving Average / Trend
    "macd_bull_cross_below_0_long_1_hour": (O, [], None),           # MACD/Momentum / Bullish crossover
    "macd_cross_long_daily": (O, [], None),                         # MACD / Crossover
    "macd_momentum_strategy": (O, [], None),                        # MACD/Momentum / Momentum
    "mesa_adaptive_long_strategy": (T, [], None),                   # Adaptive Trend / Trend
    "moving_average_cloud_strategy": (T, [], None),                 # Moving Average / Trend
    "moving_average_w_variable_period_long_strategy": (T, [], None),     # Moving Average / Adaptive trend
    "nflx_and_chats_long_1_hour": (T, [S], ["NFLX"]),               # Stock-specific / Long
    "nflx_squeeze_breakout_on_volume_1hr": (B, [S], ["NFLX"]),      # Volatility/Volume / Squeeze breakout
    "orb_long_15_min": (B, [], None),                               # ORB/Breakout / Opening breakout
    "orb_trading_strategy_backtest_3r_long": (B, [], None),         # ORB/Breakout / Opening breakout
    "orb_trading_strategy_backtest_3r_short": (B, [], None),        # ORB/Breakdown / Opening breakdown
    "psar_bullish_strategy": (T, [], None),                         # Trend / PSAR trend
    "qqq_vwap_rush": (V, [S], ["QQQ"]),                             # VWAP / VWAP momentum
    "reversal_candle_long_strategy": (R, [], None),                 # Reversal / Candlestick reversal
    "reversal_candle_on_volume_15m": (R, [], None),                 # Reversal/Volume / Volume reversal
    "reversal_candle_with_momentum_long_strategy": (R, [O], None),    # Reversal/Momentum / Momentum reversal
    "rsi_bollinger_bands_volatility_strategy": (MR, [], None),      # Mean Reversion / Oversold-reversion
    "rsi_macd_williams_r": (O, [], None),                           # Oscillator / Multi-indicator
    "rsi_momentum": (O, [], None),                                  # RSI/Momentum / Momentum
    "rvol_breakout_strategy": (B, [], None),                        # Volume/Breakout / Relative-volume breakout
    "rvol_reversal_long_15_min": (R, [], None),                     # Volume/Reversal / Relative-volume reversal
    "sell_in_may_and_go_away_long_monthly": (L, [], None),          # Seasonal / Seasonal trend
    "smoothed_moving_average_long_strategy": (T, [], None),         # Moving Average / Trend
    "sq_bollinger_band_short": (MR, [S], ["SQ", "XYZ"]),            # Bollinger/Short / Breakdown-reversion (Block: SQ -> XYZ)
    "standard_william_vix_fix_strategy": (R, [], None),             # Volatility/Reversal / Volatility reversal
    "stochastic_w_100sma_strategy": (O, [T], None),                 # Oscillator/Trend / Trend + oscillator
    "supertrend_scalper_long_30_min": (T, [], None),                # Trend / Scalping
    "supertrend_swing_long_4_hour": (T, [], None),                  # Trend / Swing trend
    "tdi_long_strategy": (O, [T], None),                            # Oscillator/Trend / Trend-momentum
    "tema_strategy": (T, [], None),                                 # Moving Average / Trend
    "tsla_21_ema_pullback_long": (T, [S], ["TSLA"]),                # Pullback / EMA pullback
    "turtle_trader_long_daily_both_systems": (L, [B], None),        # Breakout/Trend / Turtle breakout
    "turtle_traders_long_daily": (L, [B], None),                    # Breakout/Trend / Turtle breakout
    "twap_strategy": (MR, [V], None),                               # Execution/Mean Reversion / TWAP
    "udow_15_min_money_maker": (B, [S], ["UDOW"]),                  # Momentum/ETF / Intraday momentum
    "vortex_bullish_momentum_strategy": (T, [O], None),             # Momentum / Trend-momentum
    "vwap_scalper_long_30_min": (V, [], None),                      # VWAP / VWAP scalping
    "vwma_bullish_crossover_strategy": (T, [], None),               # Volume/MA / Volume-weighted crossover
    "weekly_anchored_obv_strategy_65min": (T, [], None),            # Volume/Trend / OBV trend
    "weinstein_stage_2_breakout_long_weekly": (L, [B], None),       # Breakout/Trend / Stage breakout
    "williams_r_momentum_strategy": (O, [], None),                  # Oscillator/Momentum / Momentum
    "zero_lag_ma_long_strategy": (T, [], None),                     # Moving Average / Trend
}

EVENT_STRATEGIES = {"earnings_run_up_long_daily", "earnings_runup"}

AUTHORED_TF = {"1min": "1m", "5min": "5m", "15min": "15m", "30min": "30m", "65min": "65m", "60min": "1h",
               "120min": "2h", "240min": "4h", "1day": "1D", "1week": "1W", "1month": "1M"}


def main() -> int:
    discover_strategies()
    classification = json.loads(CLASSIFICATION.read_text(encoding="utf-8"))["categories"] if CLASSIFICATION.exists() else {}
    existing = json.loads(CATALOG.read_text(encoding="utf-8")) if CATALOG.exists() else {"strategies": []}
    ids = {s["slug"]: s["id"] for s in existing["strategies"]}
    next_id = max(ids.values(), default=0) + 1

    ts = {n: c for n, c in strategy_registry.all().items() if n.startswith("ts_")}
    missing = sorted(set(n[3:] for n in ts) - set(FAMILY_MAP))
    extra = sorted(set(FAMILY_MAP) - set(n[3:] for n in ts))
    if missing or extra:
        print("FAMILY_MAP out of sync -- missing:", missing, "unknown:", extra)
        return 1

    entries = []
    for slug, cls in sorted(ts.items()):
        s = cls()
        model = s.MODEL
        key = slug[3:]
        primary, secondary, tickers = FAMILY_MAP[key]
        opts = model.get("_backtestOptions") or {}
        tf = AUTHORED_TF[s.metadata.default_params["source_timeframe"]]
        intraday = tf in ("1m", "5m", "15m", "30m", "65m", "1h", "2h", "4h")
        supported, reason = s.support_status()
        name = model.get("name", slug)
        if slug not in ids:
            ids[slug] = next_id
            next_id += 1
        entries.append({
            "id": ids[slug],
            "slug": slug,
            "name": name,
            "family": primary,
            "secondary_families": secondary,
            "direction": str(opts.get("strategyDirection", "long")).upper(),
            # The authored timeframe. Other timeframes are only added here
            # deliberately (edit the catalog), never assumed.
            "timeframes": [tf],
            "asset_scope": "SPECIFIC_TICKER" if tickers else "EQUITY",
            "allowed_tickers": tickers or [],
            "session": "RTH" if intraday else "DAILY",
            "minimum_data": "INTRADAY" if intraday else "DAILY",
            "uses_premarket": intraday,
            "requires_premarket_data": False,
            "requires_event_data": key in EVENT_STRATEGIES,
            "runnable": supported,
            "not_runnable_reason": "" if supported else reason,
            "source": "TrendSpider (ported)",
            "classification": classification.get(name, {}),
        })

    CATALOG.parent.mkdir(parents=True, exist_ok=True)
    catalog = {
        "version": date.today().isoformat() + f"-{len(entries)}",
        "_comment": "Generated by tools/strategy_engine/build_catalog.py; edit timeframes/tickers here or in FAMILY_MAP.",
        "strategies": sorted(entries, key=lambda e: e["id"]),
    }
    CATALOG.write_text(json.dumps(catalog, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(entries)} strategies -> {CATALOG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
