"""
Day-by-day backtest of the selection engine (see app/strategy_engine/engine_backtest.py).

usage (from backend/):
  python tools/strategy_engine/run_engine_backtest.py AAPL TSLA SPY QQQ INFQ \
      --start 2024-10-01 --end 2026-09-18 [--refresh weekly] [--out data/strategy_engine/engine_backtest]
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
import warnings
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

TIMEFRAMES = ("5m", "15m", "30m", "65m", "1h", "2h", "1D")


def run_one(ticker: str, start: str, end: str, refresh: str) -> dict:
    warnings.filterwarnings("ignore")
    from app.strategy_engine.data.store import BarStore
    from app.strategy_engine.engine_backtest import EngineBacktester, buy_and_hold
    from app.strategy_engine.models import Timeframe

    s, e = dt.date.fromisoformat(start), dt.date.fromisoformat(end)
    t0 = time.time()
    bt = EngineBacktester(refresh=refresh)
    decisions = bt.decisions(ticker, [Timeframe.parse(x) for x in TIMEFRAMES], s, e,
                             progress=lambda m: print(f"[{time.time() - t0:6.0f}s] {m}", flush=True))
    return {"ticker": ticker, "start": start, "end": end, "refresh": refresh, "seconds": round(time.time() - t0),
            "buy_and_hold": buy_and_hold(BarStore(), ticker, s, e),
            "summary": bt.simulate(ticker, decisions, s, e),
            "decisions": [asdict(d) for d in decisions]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("tickers", nargs="+")
    ap.add_argument("--start", default="2024-10-01")
    ap.add_argument("--end", default="2026-09-18")
    ap.add_argument("--refresh", default="weekly", choices=["weekly", "daily"])
    ap.add_argument("--out", default="data/strategy_engine/engine_backtest")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    with ProcessPoolExecutor(max_workers=min(len(a.tickers), 5)) as pool:
        futures = {t: pool.submit(run_one, t.upper(), a.start, a.end, a.refresh) for t in a.tickers}
        for t, f in futures.items():
            res = f.result()
            (out / f"{t.upper()}_{a.refresh}.json").write_text(json.dumps(res, default=str, indent=1))
            print(f"{t.upper()} done in {res['seconds']}s; buy&hold {res['buy_and_hold']}", flush=True)
            for tf, s in res["summary"].items():
                print(f"  {tf:>4} " + " | ".join(f"{p} n={s[p]['trade_count']} PF={s[p]['profit_factor']} sum={s[p]['sum_return']}"
                                              for p in ("ENGINE", "ENGINE_TOP1", "NO_REGIME", "ALL_STRATEGIES")), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
