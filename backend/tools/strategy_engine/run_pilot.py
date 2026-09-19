"""
Populate the historical database for a set of tickers:
bars -> market/ticker/premarket regime histories -> strategy evaluations.

usage (from backend/):
  python tools/strategy_engine/run_pilot.py INFQ AAPL TSLA SPY QQQ [--years 2] [--skip-fetch]
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.strategy_engine import pipeline as P  # noqa: E402
from app.strategy_engine.models import Timeframe  # noqa: E402
from app.strategy_engine.registry import default_registry  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("tickers", nargs="+")
    ap.add_argument("--years", type=float, default=2.0)
    ap.add_argument("--skip-fetch", action="store_true")
    ap.add_argument("--end", default=None)
    a = ap.parse_args()
    end = dt.date.fromisoformat(a.end) if a.end else dt.date.today()
    start = end - dt.timedelta(days=int(365.25 * a.years))
    tickers = [t.upper() for t in a.tickers]
    tfs = sorted({tf for s in default_registry().all() for tf in s.timeframes}, key=lambda t: t.minutes)
    t0 = time.time()
    if not a.skip_fetch:
        print(f"[{time.time()-t0:6.0f}s] fetching bars {start}..{end} for {tickers} timeframes {[str(t) for t in tfs]}", flush=True)
        rep = P.ensure_bars(sorted(set(tickers) | {"SPY", "QQQ", "IWM"}), tfs, start, end)
        for k, v in rep.items():
            print("   ", k, v, flush=True)
    print(f"[{time.time()-t0:6.0f}s] market history rows: {P.build_market_history()}", flush=True)
    for t in tickers:
        print(f"[{time.time()-t0:6.0f}s] {t}: ticker history {P.build_ticker_history(t)}, premarket history "
              f"{P.build_premarket_history(t)}", flush=True)
    for t in tickers:
        print(f"[{time.time()-t0:6.0f}s] evaluating {t}", flush=True)
        P.evaluate_ticker(t, progress=lambda m: print(m, flush=True))
    print(f"[{time.time()-t0:6.0f}s] done", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
