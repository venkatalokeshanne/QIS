"""
Build the historical backtest database the selection engine learns from:
every catalog strategy, every ticker, one timeframe, day by day.

usage (from backend/):
  python tools/strategy_forecast/build_backtests.py --timeframe 15m --tickers AAPL TSLA SPY QQQ INFQ
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


def main() -> int:
    warnings.filterwarnings("ignore")
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeframe", default="15m")
    ap.add_argument("--tickers", nargs="+", default=["AAPL", "TSLA", "SPY", "QQQ", "INFQ"])
    a = ap.parse_args()

    from app.strategy_forecast.backtests import build
    from app.strategy_engine.models import Timeframe

    t0 = time.time()
    result = build([t.upper() for t in a.tickers], Timeframe.parse(a.timeframe),
                   progress=lambda m: print(f"[{time.time() - t0:6.0f}s] {m}", flush=True))
    print(json.dumps(result, indent=1), flush=True)
    print(f"done in {time.time() - t0:.0f}s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
