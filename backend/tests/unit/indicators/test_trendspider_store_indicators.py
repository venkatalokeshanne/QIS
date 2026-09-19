"""The *_TS indicators (TrendSpider store scripts translated to Python).

Golden values in tests/fixtures/ts_store_golden.json were produced by
running the ORIGINAL JavaScript through TrendSpider's own scripting engine
(tools/ts_store/oracle); the translations must reproduce them exactly.
The full 291-script parity sweep is tools/ts_store/oracle/compare.py.
"""

import json
import math
from pathlib import Path

import pandas as pd
import pytest

from app.indicators.registry import discover_indicators, indicator_registry
from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.api import ScriptContext, run_script

GOLDEN = json.loads((Path(__file__).resolve().parents[2] / "fixtures" / "ts_store_golden.json").read_text(encoding="utf-8"))
REGISTERED = {
    "bull-bear-power": "bull_bear_power_TS",
    "composite-index": "composite_index_TS",
    "inside-candle-highlighter": "inside_candle_highlighter_TS",
    "candlestick-pattern-detection-emojis": "candlestick_pattern_detection_emojis_TS",
    "rsi-with-sma": "rsi_with_sma_TS",
}


@pytest.fixture(scope="module", autouse=True)
def _discovered():
    discover_indicators()


def test_every_store_script_is_registered_with_ts_suffix():
    names = [n for n in indicator_registry.names() if n.endswith("_TS")]
    assert len(names) == 291
    meta = indicator_registry.get("composite_index_TS")().metadata
    assert meta.category == "trendspider_store"
    assert meta.default_params["rsi_length"] == 14  # TrendSpider's input id for "RSI Length"


def _same(js_value, py_value):
    if isinstance(js_value, dict) and "__num" in js_value:
        js_value = float(js_value["__num"])
    if py_value is J.undefined or py_value is J.HOLE:
        py_value = None
    if isinstance(py_value, str):
        py_value = J.from_utf16(py_value)
    if isinstance(js_value, float) and isinstance(py_value, (int, float)) and math.isnan(js_value):
        return math.isnan(py_value)
    if isinstance(js_value, bool) or isinstance(py_value, bool):
        return js_value is py_value
    return js_value == py_value


@pytest.mark.parametrize("case", GOLDEN["cases"], ids=[c["script"] for c in GOLDEN["cases"]])
def test_translation_reproduces_trendspiders_engine_exactly(case):
    cls = indicator_registry.get(REGISTERED[case["script"]])
    res = run_script(cls.TS_SCRIPT, ScriptContext(case["bars"], ticker="AAPL", resolution=case["resolution"]))
    assert set(res.out) == set(case["series"])
    for sid, expected in case["series"].items():
        got = res.out[sid]
        assert len(got) == len(expected), sid
        bad = [i for i, (a, b) in enumerate(zip(expected, got)) if not _same(a, b)]
        assert not bad, f"{sid}: first difference at {bad[0]}: TrendSpider {expected[bad[0]]!r} vs {got[bad[0]]!r}"


def test_calculate_adds_prefixed_columns_and_honours_params():
    case = next(c for c in GOLDEN["cases"] if c["script"] == "bull-bear-power")
    b = case["bars"]
    idx = pd.to_datetime(b["time"], unit="s").tz_localize("UTC").tz_convert("America/New_York").tz_localize(None).normalize()
    df = pd.DataFrame({k: b[k] for k in ("open", "high", "low", "close", "volume")}, index=idx)
    ind = indicator_registry.get("bull_bear_power_TS")()
    out = ind.calculate(df, {})
    col = "bull_bear_power_TS__bbpower"
    assert col in out and len(out) == len(df)
    assert out[col].dropna().tolist() == [v for v in case["series"]["bbpower"] if v is not None]
    # a different input changes the result (params reach the script)
    other = ind.calculate(df, {"length": 5})
    assert not out[col].equals(other[col])


@pytest.mark.parametrize("unit", ["s", "ms", "us", "ns"])
def test_bar_times_are_unix_seconds_whatever_the_index_resolution(unit):
    """pandas 3 stores DatetimeIndex in varying units; Twelve Data frames
    arrive in microseconds. Session/time-of-day scripts need real times."""
    from app.indicators.trendspider_store._runtime.indicator import frame_to_bars

    idx = pd.DatetimeIndex(["2026-09-17 09:30", "2026-09-17 09:45"]).as_unit(unit)
    df = pd.DataFrame({"open": [1.0, 2], "high": [1.0, 2], "low": [1.0, 2], "close": [1.0, 2], "volume": [1, 2]}, index=idx)
    assert frame_to_bars(df, "15")["time"] == [1789651800, 1789652700]  # 09:30 / 09:45 ET
