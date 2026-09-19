"""
Parity check: translated Python vs TrendSpider's own engine.

For each store script and each test dataset:
  1. run the Python translation (recording every request.history() call),
  2. run the original JS through TrendSpider's engine (oracle/run_batch.js)
     with the same bars and the same histories,
  3. require every output series to match value-for-value.

usage (from backend/):
  python tools/ts_store/oracle/compare.py [--only name ...] [--datasets aapl_d,syn_5m] [--limit N]
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import random
import subprocess
import sys
import time
import traceback
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.indicators.trendspider_store._runtime import js as J  # noqa: E402
from app.indicators.trendspider_store._runtime import sessions  # noqa: E402
from app.indicators.trendspider_store._runtime.api import REGULAR_SESSION, ScriptContext, run_script  # noqa: E402

TOOLS = Path(__file__).resolve().parents[1]
CLEAN = TOOLS / "clean"
OUT_PY = TOOLS / "out_py"
WORK = TOOLS / "oracle" / "work"
TS_BARS = Path(r"C:\Users\annev\Downloads\trendspider-automation\data\extraction\bars")


# ----------------------------------------------------------------------------
# datasets
# ----------------------------------------------------------------------------


def _bars_from_rows(rows):
    return {
        "time": [int(r[0] // 1000) for r in rows],
        "open": [r[1] for r in rows],
        "high": [r[2] for r in rows],
        "low": [r[3] for r in rows],
        "close": [r[4] for r in rows],
        "volume": [r[5] for r in rows],
    }


def load_ts_daily(n=800):
    d = json.loads((TS_BARS / "AAPL_D.json").read_text(encoding="utf-8"))
    return _bars_from_rows(d["bars"][-n:])


def synthetic_intraday(days=25, minutes=5, seed=7, start="2026-06-01"):
    import datetime as dt
    from zoneinfo import ZoneInfo

    rnd = random.Random(seed)
    tz = ZoneInfo("America/New_York")
    d = dt.date.fromisoformat(start)
    rows = []
    price = 150.0
    while len(set(r[0] // 86400000 for r in rows)) < days:
        if d.weekday() < 5:
            t = dt.datetime(d.year, d.month, d.day, 9, 30, tzinfo=tz)
            end = dt.datetime(d.year, d.month, d.day, 16, 0, tzinfo=tz)
            while t < end:
                o = price
                c = max(1.0, o * (1 + rnd.gauss(0, 0.0025)))
                h = max(o, c) * (1 + abs(rnd.gauss(0, 0.001)))
                lo = min(o, c) * (1 - abs(rnd.gauss(0, 0.001)))
                v = int(abs(rnd.gauss(50000, 20000))) + 100
                rows.append([int(t.timestamp() * 1000), round(o, 4), round(h, 4), round(lo, 4), round(c, 4), v])
                price = c
                t += dt.timedelta(minutes=minutes)
        d += dt.timedelta(days=1)
    return _bars_from_rows(rows)


DATASETS = {
    "aapl_d": lambda: ("AAPL", "D", load_ts_daily()),
    "syn_5m": lambda: ("AAPL", "5", synthetic_intraday()),
}

TF_MINUTES = {"D": 1440, "1440": 1440, "W": 10080, "M": 43200, "Q": 129600, "Y": 525600}


def _tf_minutes(res):
    res = str(res).upper()
    if res in TF_MINUTES:
        return TF_MINUTES[res]
    try:
        return float(res)
    except ValueError:
        return None


def resample(bars, res):
    groups = {}
    order = []
    for i, t in enumerate(bars["time"]):
        key = sessions.bar_at(res, REGULAR_SESSION, t * 1000, greedy_daily=True)
        if key is None:
            continue
        if key not in groups:
            groups[key] = [key // 1000, bars["open"][i], bars["high"][i], bars["low"][i], bars["close"][i], bars["volume"][i]]
            order.append(key)
        else:
            g = groups[key]
            g[2] = max(g[2], bars["high"][i])
            g[3] = min(g[3], bars["low"][i])
            g[4] = bars["close"][i]
            g[5] += bars["volume"][i]
    return {k: [groups[o][j] for o in order] for j, k in enumerate(["time", "open", "high", "low", "close", "volume"])}


def synthetic_like(bars, ticker):
    seed = int(hashlib.md5(ticker.encode()).hexdigest()[:8], 16)
    rnd = random.Random(seed)
    price = 50 + seed % 400
    out = {k: [] for k in ("time", "open", "high", "low", "close", "volume")}
    for t in bars["time"]:
        o = price
        c = max(0.5, o * (1 + rnd.gauss(0, 0.012)))
        out["time"].append(t)
        out["open"].append(round(o, 4))
        out["close"].append(round(c, 4))
        out["high"].append(round(max(o, c) * (1 + abs(rnd.gauss(0, 0.004))), 4))
        out["low"].append(round(min(o, c) * (1 - abs(rnd.gauss(0, 0.004))), 4))
        out["volume"].append(int(abs(rnd.gauss(1e6, 3e5))) + 1)
        price = c
    return out


class RecordingProvider:
    def __init__(self, ticker, res, bars):
        self.ticker, self.res, self.bars = ticker, res, bars
        self.served = {}
        self.alt = {}

    def alt_data(self, kind, *args):
        from altdata_fixtures import fixture

        res = fixture(kind, args, self.bars)
        self.alt.setdefault(kind, []).append(res)
        return res

    def history(self, ticker, resolution, ext_session=False, chart_type="candles", base=None):
        key = f"{ticker}|{resolution}"
        if key in self.served:
            return self.served[key]
        want = _tf_minutes(resolution)
        have = _tf_minutes(self.res)
        base = self.bars
        if want is not None and have is not None and want > have:
            base = resample(self.bars, resolution if resolution not in ("1440",) else "D")
        src = base if ticker.upper() == self.ticker.upper() else synthetic_like(base, ticker.upper())
        self.served[key] = src
        return src


# ----------------------------------------------------------------------------
# running
# ----------------------------------------------------------------------------


def load_py(stem):
    path = OUT_PY / f"{stem}.py"
    spec = importlib.util.spec_from_file_location(f"ts_out_{abs(hash(stem))}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.script


def run_python(stem, ticker, res, bars):
    prov = RecordingProvider(ticker, res, bars)
    ctx = ScriptContext(bars, ticker=ticker, resolution=res, provider=prov,
                        symbol_info={"sector": "Technology", "industry": "Consumer Electronics", "type": "stock"})
    t0 = time.perf_counter()
    try:
        r = run_script(load_py(stem), ctx)
        err = None
        series = r.out
        inputs = list(r.meta["inputs"])
    except J.Unsupported as exc:
        return {"error": f"UNSUPPORTED: {exc}", "series": {}, "histories": prov.served, "alt": prov.alt,
                "secs": time.perf_counter() - t0}
    except J.JSError as exc:
        err = J.to_str(J.get(exc.value, "message")) if isinstance(exc.value, dict) else J.to_str(exc.value)
        series, inputs = {}, []
    except Exception as exc:  # a translation/runtime bug, not script behavior
        return {"error": f"PYTHON CRASH: {type(exc).__name__}: {exc}", "trace": traceback.format_exc(), "series": {},
                "histories": prov.served, "secs": time.perf_counter() - t0}
    return {"error": err, "series": series, "inputs": inputs, "histories": prov.served, "alt": prov.alt,
            "secs": time.perf_counter() - t0}


def _norm(v):
    if isinstance(v, dict):
        if "__num" in v:
            return float(v["__num"])
        if "__undef" in v:
            return None
        if "y" in v:
            return _norm(v["y"])
        return "<object>"
    if v is J.undefined or v is J.HOLE:
        return None
    if isinstance(v, J.JSObject):
        if "y" in v:
            return _norm(v["y"])
        return "<object>"
    if isinstance(v, (list, tuple)):
        return "<array>"
    if isinstance(v, str):
        return J.from_utf16(v)
    return v


def same(a, b):
    a, b = _norm(a), _norm(b)
    if isinstance(a, bool) or isinstance(b, bool):
        return a is b or (a == b and type(a) is type(b))
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        if a != a and b != b:
            return True
        return a == b
    return a == b


def compare(py, js):
    if js.get("error") or py.get("error"):
        if js.get("error") and py.get("error"):
            return "both-error", f"js: {js['error'][:90]} | py: {py['error'][:90]}"
        return "MISMATCH", f"error only on one side -- js: {js.get('error')} | py: {py.get('error')}"
    ks, ps = js["series"], py["series"]
    if set(ks) != set(ps):
        return "MISMATCH", f"series ids differ: js-only {sorted(set(ks) - set(ps))} py-only {sorted(set(ps) - set(ks))}"
    ulp = None
    for k in ks:
        a, b = ks[k], ps[k]
        if len(a) != len(b):
            return "MISMATCH", f"{k}: length js {len(a)} py {len(b)}"
        for i, (x, y) in enumerate(zip(a, b)):
            if not same(x, y):
                nx, ny = _norm(x), _norm(y)
                if (isinstance(nx, float) and isinstance(ny, (int, float)) and not isinstance(ny, bool)
                        and math.isfinite(nx) and abs(nx - ny) <= 1e-12 * max(1.0, abs(nx))):
                    ulp = ulp or f"{k}[{i}]: js {nx!r} py {ny!r}"
                    continue
                return "MISMATCH", f"{k}[{i}]: js {nx!r} py {ny!r}"
    if ulp:
        return "ULP", "last-bit float differences only, first at " + ulp
    return "OK", f"{len(ks)} series"


def check_one(stem, dataset_names):
    """Python + oracle + compare for one script (runs in its own process)."""
    ds = {name: DATASETS[name]() for name in dataset_names}
    jobs, pys = [], {}
    for name, (ticker, res, bars) in ds.items():
        jid = f"{stem}@{name}"
        py = run_python(stem, ticker, res, bars)
        pys[jid] = py
        jobs.append({"id": jid, "script": str(CLEAN / f"{stem}.js"), "bars": bars, "ticker": ticker,
                     "resolution": res, "histories": dict(py["histories"]), "alt": py.get("alt", {})})
    jobs_path, res_path = WORK / f"{stem}.jobs.json", WORK / f"{stem}.results.json"
    jobs_path.write_text(json.dumps(jobs), encoding="utf-8")
    subprocess.run(["node", str(TOOLS / "oracle" / "run_batch.js"), str(jobs_path), str(res_path)], check=True,
                   env={**__import__("os").environ, "TZ": "America/New_York"}, timeout=240)
    results = {r["id"]: r for r in json.loads(res_path.read_text(encoding="utf-8"))}
    out = {}
    for jid, py in pys.items():
        status, detail = compare(py, results[jid])
        if py.get("error", "") and py["error"].startswith(("UNSUPPORTED", "PYTHON CRASH")):
            status = py["error"].split(":")[0]
        out[jid] = {"status": status, "detail": detail, "py_secs": round(py["secs"], 2), "trace": py.get("trace", "")[-1500:]}
    jobs_path.unlink(missing_ok=True)
    res_path.unlink(missing_ok=True)
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    import concurrent.futures as cf
    import os

    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--datasets", default="aapl_d,syn_5m")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--worker")
    ap.add_argument("--report", default=str(TOOLS / "oracle" / "parity_report.json"))
    args = ap.parse_args()
    WORK.mkdir(parents=True, exist_ok=True)
    if args.worker:
        print(json.dumps(check_one(args.worker, args.datasets.split(","))))
        return
    stems = sorted(p.stem for p in OUT_PY.glob("*.py"))
    if args.only:
        stems = [s for s in stems if any(o in s for o in args.only)]
    if args.limit:
        stems = stems[: args.limit]
    report = json.loads(Path(args.report).read_text(encoding="utf-8")) if (args.only and Path(args.report).exists()) else {}

    def run(stem):
        try:
            r = subprocess.run([sys.executable, __file__, "--worker", stem, "--datasets", args.datasets],
                               capture_output=True, text=True, timeout=args.timeout, cwd=str(BACKEND), encoding="utf-8")
            if r.returncode:
                return {f"{stem}@*": {"status": "HARNESS ERROR", "detail": r.stderr[-800:], "py_secs": 0, "trace": ""}}
            return json.loads(r.stdout.strip().splitlines()[-1])
        except subprocess.TimeoutExpired:
            return {f"{stem}@*": {"status": "TIMEOUT", "detail": f"> {args.timeout}s", "py_secs": args.timeout, "trace": ""}}

    counts = {}
    with cf.ThreadPoolExecutor(args.jobs) as pool:
        for res in pool.map(run, stems):
            for jid, r in res.items():
                report = {k: v for k, v in report.items() if not (jid.endswith("@*") and k.startswith(jid[:-1]))}
                report[jid] = r
                if r["status"] != "OK":
                    print(f"{r['status']:14s} {jid}: {r['detail'][:230]}", flush=True)
    for r in report.values():
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    Path(args.report).write_text(json.dumps(report, indent=1), encoding="utf-8")
    print("SUMMARY", counts)


if __name__ == "__main__":
    main()
