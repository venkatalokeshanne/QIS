"""
Generate app/indicators/trendspider_store/<name>_ts.py from the store scripts.

Each module = the script's JavaScript translated to Python
(transpile.js) + a register_store_indicator(...) call carrying the
script's inputs/outputs (read by running the translation once) and its
parity status against TrendSpider's engine (oracle/parity_report.json).

usage (from backend/): python tools/ts_store/build_modules.py
"""

from __future__ import annotations

import html
import json
import re
import subprocess
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(Path(__file__).resolve().parent / "oracle"))

from compare import RecordingProvider, load_ts_daily  # noqa: E402

from app.indicators.trendspider_store._runtime import js as J  # noqa: E402
from app.indicators.trendspider_store._runtime.api import ScriptContext, ScriptResult, make_globals  # noqa: E402

TOOLS = Path(__file__).resolve().parent
CLEAN = TOOLS / "clean"
DEST = BACKEND / "app" / "indicators" / "trendspider_store"
INDEX = json.loads((TOOLS / "index.json").read_text(encoding="utf-8"))
REPORT_PATH = TOOLS / "oracle" / "parity_report.json"


def snake(s):
    s = re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_").lower()
    return re.sub(r"_+", "_", s)


def transpile(path):
    r = subprocess.run(["node", str(TOOLS / "transpile.js"), str(path)], capture_output=True, text=True, encoding="utf-8")
    if r.returncode:
        raise RuntimeError(r.stderr)
    return r.stdout


def metadata_from_run(code, stem):
    ns = {}
    exec(compile("from app.indicators.trendspider_store._runtime import js as J\n" + code, f"<{stem}>", "exec"), ns)
    bars = load_ts_daily(300)
    ctx = ScriptContext(bars, ticker="AAPL", resolution="D", provider=RecordingProvider("AAPL", "D", bars))
    res = ScriptResult()
    g = make_globals(ctx, res)
    error = None
    try:
        ns["script"](g)
    except Exception as exc:  # inputs declared before the failure are still recorded
        error = f"{type(exc).__name__}: {exc}"
    inputs = []
    for i in res.meta["inputs"]:
        if J.truthy(i.get("hidden", J.undefined)) and i.get("id") != "warmup":
            continue
        spec = {"id": i["id"], "title": i.get("title", i["id"]), "type": i.get("type", "number"), "default": i.get("value")}
        if "options" in i:
            spec["options"] = [o["value"] for o in i["options"]]
        inputs.append(_plain(spec))
    ap = res.meta["appearance"]
    outputs = [k for k in res.out if not k.endswith("_color") and ap.get(k, {}).get("rendererType") != "visualGrid"
               and not J.truthy(ap.get(k, {}).get("isProjection", J.undefined))]
    signals = [k for k in res.out if J.truthy(ap.get(k, {}).get("isSignalSeries", J.undefined))]
    return inputs, outputs, signals, bool(res.meta.get("lower")), error


def _plain(v):
    if isinstance(v, dict):
        return {k: _plain(x) for k, x in v.items()}
    if isinstance(v, list):
        return [_plain(x) for x in v]
    if v is J.undefined:
        return None
    return v


def main():
    report = json.loads(REPORT_PATH.read_text()) if REPORT_PATH.exists() else {}
    for old in DEST.glob("*_ts.py"):
        old.unlink()
    used = {}
    summary = {}
    for path in sorted(CLEAN.glob("*.js")):
        stem = path.stem
        info = dict(INDEX.get(stem, {"title": stem, "developer": "", "url": ""}))
        info["title"] = html.unescape(info["title"])
        info["developer"] = html.unescape(info.get("developer") or "")
        base = snake(info["title"]) or snake(stem)
        if base in used:
            base = f"{base}_{snake(stem.split('-')[0])}"
        used[base] = stem
        name = f"{base}_TS"
        modname = f"{base}_ts" if base[0].isalpha() else f"ts_{base}_ts"
        code = transpile(path)
        inputs, outputs, signals, lower, err = metadata_from_run(code, stem)
        src = path.read_text(encoding="utf-8")
        requires = sorted(set(re.findall(r"request\.(\w+)", src)))
        statuses = {k.split("@")[1]: v["status"] for k, v in report.items() if k.split("@")[0] == stem}
        if statuses and all(s == "OK" for s in statuses.values()):
            parity = "exact"
        elif statuses:
            parity = ", ".join(f"{d}: {s}" for d, s in sorted(statuses.items()))
        else:
            parity = "unverified"
        header = f'''"""
{info["title"]} -- TrendSpider store indicator by {info.get("developer") or "unknown"}.

Registered as "{name}". Translated line-for-line from the script's
published JavaScript ({info.get("url", "")})
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
{parity}.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

'''
        footer = f"""

register_store_indicator(
    script,
    name={name!r},
    title={info["title"]!r},
    developer={info.get("developer", "")!r},
    url={info.get("url", "")!r},
    position={"lower" if lower else "price"!r},
    inputs={inputs!r},
    outputs={outputs!r},
    signals={signals!r},
    requires={requires!r},
    parity={parity!r},
)
"""
        (DEST / f"{modname}.py").write_text(header + code + footer, encoding="utf-8")
        summary[name] = {"module": modname, "parity": parity, "requires": requires, "outputs": len(outputs),
                         "metadata_run_error": err}
    (TOOLS / "build_summary.json").write_text(json.dumps(summary, indent=1))
    print(f"wrote {len(summary)} modules")


if __name__ == "__main__":
    main()
