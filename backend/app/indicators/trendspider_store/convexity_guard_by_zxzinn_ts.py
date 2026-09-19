"""
Convexity Guard by zxzinn -- TrendSpider store indicator by Chao Chin Chang.

Registered as "convexity_guard_by_zxzinn_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6aa82c-convexity-guard-by-zxzinn/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Array = G["Array"]
    G_Math = G["Math"]
    G_NaN = G["NaN"]
    G_Number = G["Number"]
    G_String = G["String"]
    G_assert = G["assert"]
    G_close = G["close"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_input = G["input"]
    G_library = G["library"]
    G_low = G["low"]
    G_paint = G["paint"]
    G_paint_overlay = G["paint_overlay"]
    G_register_signal = G["register_signal"]
    G_request = G["request"]
    G_series_of = G["series_of"]
    G_shift = G["shift"]
    G_time = G["time"]
    G_volume = G["volume"]
    G_describe_indicator("Convexity Guard by zxzinn", "price", J.obj(("shortName", "Convexity Guard"), ("warmup", 120)))
    lookback = J.get(G_input, "number")("Lookback bars", 5, J.obj(("min", 2), ("max", 30)))
    threshold = J.get(G_input, "number")("Event threshold %", 0.55, J.obj(("min", 0.1), ("max", 5)))
    resetLevel = J.get(G_input, "number")("Reset threshold", 0.35, J.obj(("min", 0.1), ("max", 0.9)))
    showLabels = J.get(G_input, "select")("Event labels", "Yes", J.JSArray(["Yes", "No"]))
    maxSpread = J.get(G_input, "number")("Max leg spread %", 18, J.obj(("min", 1), ("max", 100)))
    moment = G_library("moment-timezone")
    TZ = "America/New_York"
    sessionVwap = G_series_of(None)
    day = None
    pv = 0
    vol = 0
    i_2 = 0
    while J.lt(i_2, J.get(G_close, "length")):
        stamp_2 = J.get(moment(J.mul(J.get(G_time, i_2), 1000)), "tz")(TZ)
        key = J.get(stamp_2, "format")("YYYY-MM-DD")
        if J.sne(key, day):
            day = key
            pv = 0
            vol = 0
        minute = J.add(J.mul(J.get(stamp_2, "hour")(), 60), J.get(stamp_2, "minute")())
        if (J.lt(minute, 570) or J.ge(minute, 960)):
            J.set(sessionVwap, i_2, None)
            i_2 = J.inc(i_2)
            continue
        barVol = (J.get(G_volume, i_2) if J.truthy(J.get(G_Number, "isFinite")(J.get(G_volume, i_2))) else 0)
        pv = J.add(pv, J.mul(J.div(J.add(J.add(J.get(G_high, i_2), J.get(G_low, i_2)), J.get(G_close, i_2)), 3), barVol))
        vol = J.add(vol, barVol)
        J.set(sessionVwap, i_2, (J.div(pv, vol) if J.gt(vol, 0) else None))
        i_2 = J.inc(i_2)
    prior = G_shift(G_close, lookback)
    def _f1(c=J.undefined, p=J.undefined, *_args):
        return (J.div(J.sub(c, p), p) if (J.truthy(J.get(G_Number, "isFinite")(p)) and J.gt(p, 0)) else None)
    move = G_for_every(G_close, prior, _f1)
    event = G_series_of(False)
    reset = G_series_of(False)
    labels = G_series_of(None)
    i_3 = 0
    while J.lt(i_3, J.get(G_close, "length")):
        stamp_3 = J.get(moment(J.mul(J.get(G_time, i_3), 1000)), "tz")(TZ)
        h = J.get(stamp_3, "hour")()
        m = J.get(stamp_3, "minute")()
        inWindow = (J.lt(h, 16) if J.truthy(_t2 := (_t3 if J.truthy(_t3 := J.gt(h, 14)) else (J.ge(m, 30) if J.truthy(_t4 := J.seq(h, 14)) else _t4))) else _t2)
        J.set(event, i_3, (J.ge(J.get(G_Math, "abs")(J.get(move, i_3)), J.div(threshold, 100)) if J.truthy(_t5 := (J.get(G_Number, "isFinite")(J.get(move, i_3)) if J.truthy(_t6 := inWindow) else _t6)) else _t5))
        if J.truthy(J.get(event, i_3)):
            hi = J.get(G_Math, "max")(*J.spread(J.get(G_high, "slice")(J.get(G_Math, "max")(0, J.add(J.sub(i_3, lookback), 1)), J.add(i_3, 1))))
            lo = J.get(G_Math, "min")(*J.spread(J.get(G_low, "slice")(J.get(G_Math, "max")(0, J.add(J.sub(i_3, lookback), 1)), J.add(i_3, 1))))
            loc = (J.div(J.sub(J.get(G_close, i_3), lo), J.sub(hi, lo)) if J.gt(hi, lo) else 0.5)
            J.set(reset, i_3, (_t7 if J.truthy(_t7 := (J.le(loc, J.sub(1, resetLevel)) if J.truthy(_t8 := J.gt(J.get(move, i_3), 0)) else _t8)) else (J.ge(loc, resetLevel) if J.truthy(_t9 := J.lt(J.get(move, i_3), 0)) else _t9)))
        J.set(labels, i_3, (("VOL EVENT<br/>RESET" if J.truthy(J.get(reset, i_3)) else "VOL EVENT") if (J.seq(showLabels, "Yes") and J.truthy(J.get(event, i_3))) else None))
        i_3 = J.inc(i_3)
    G_paint(sessionVwap, J.obj(("name", "Session VWAP"), ("color", "#9C7CFF"), ("style", "line"), ("thickness", 1)))
    G_paint(labels, J.obj(("name", "Vol event"), ("style", "labels_above"), ("color", "#E8EEF8"), ("backgroundColor", "#7C6CF2"), ("backgroundBorderRadius", 5), ("fontSize", 7)))
    G_register_signal(event, "Research volatility")
    G_register_signal(reset, "Research range reset")
    def num(value=J.undefined, *_args):
        n = G_Number(J.get(J.get(G_String(("" if (J.nullish(value)) else value)), "replace")(J.regex("[$,%]", "g"), ""), "replace")(J.regex(",", "g"), ""))
        return (n if J.truthy(J.get(G_Number, "isFinite")(n)) else G_NaN)
    opt = J.obj(("ok", False), ("expiry", "—"), ("strike", G_NaN), ("cb", G_NaN), ("ca", G_NaN), ("pb", G_NaN), ("pa", G_NaN), ("ratio", G_NaN), ("cSpread", G_NaN), ("pSpread", G_NaN), ("oiRatio", G_NaN))
    try:
        ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/134 Safari/537.36"
        asset = ("etf" if J.seq(J.get(G_current, "assetType"), "etf") else "stocks")
        url = J.add(J.add(J.add(J.add("https://api.nasdaq.com/api/quote/", J.get(G_current, "symbol")), "/option-chain?assetclass="), asset), "&limit=1000")
        response = J.get(G_request, "http")(url, 300, J.obj(("user-agent", ua), ("accept", "application/json")))
        rows = (J.get(J.get(J.get(response, "data"), "table"), "rows") if J.truthy(_t10 := (J.get(J.get(response, "data"), "table") if J.truthy(_t11 := (J.get(response, "data") if J.truthy(_t12 := response) else _t12)) else _t11)) else _t10)
        G_assert(J.get(G_Array, "isArray")(rows), "Options unavailable")
        def _f13(r=J.undefined, *_args):
            return (J.get(G_Number, "isFinite")(num(J.get(r, "strike"))) if J.truthy(_t1 := J.get(r, "expiryDate")) else _t1)
        valid = J.get(rows, "filter")(_f13)
        G_assert(J.gt(J.get(valid, "length"), 0), "No option rows")
        def _f14(r=J.undefined, *_args):
            return J.seq(J.get(r, "expiryDate"), expiry)
        def _f15(a=J.undefined, b=J.undefined, *_args):
            return J.sub(num(J.get(a, "strike")), num(J.get(b, "strike")))
        expiry = J.get(J.get(valid, 0), "expiryDate")
        sameExpiry = J.get(J.get(valid, "filter")(_f14), "sort")(_f15)
        spot = J.get(G_close, J.sub(J.get(G_close, "length"), 1))
        def _f16(a=J.undefined, b=J.undefined, *_args):
            return (b if J.lt(J.get(G_Math, "abs")(J.sub(num(J.get(b, "strike")), spot)), J.get(G_Math, "abs")(J.sub(num(J.get(a, "strike")), spot))) else a)
        atm = J.get(sameExpiry, "reduce")(_f16, J.get(sameExpiry, 0))
        cb = num(J.get(atm, "c_Bid"))
        ca = num(J.get(atm, "c_Ask"))
        pb = num(J.get(atm, "p_Bid"))
        pa = num(J.get(atm, "p_Ask"))
        cm = J.div(J.add(cb, ca), 2)
        pm = J.div(J.add(pb, pa), 2)
        quoteOk = (J.ge(pa, pb) if J.truthy(_t17 := (J.ge(ca, cb) if J.truthy(_t18 := (J.gt(pa, 0) if J.truthy(_t19 := (J.gt(ca, 0) if J.truthy(_t20 := (J.ge(pb, 0) if J.truthy(_t21 := (J.ge(cb, 0) if J.truthy(_t22 := J.get(J.JSArray([cb, ca, pb, pa]), "every")(J.get(G_Number, "isFinite"))) else _t22)) else _t21)) else _t20)) else _t19)) else _t18)) else _t17)
        atmIndex = J.get(sameExpiry, "indexOf")(atm)
        nearby = J.get(sameExpiry, "slice")(J.get(G_Math, "max")(0, J.sub(atmIndex, 3)), J.add(atmIndex, 4))
        def _f23(s=J.undefined, r=J.undefined, *_args):
            return J.add(s, (_t1 if J.truthy(_t1 := num(J.get(r, "c_Openinterest"))) else 0))
        callOi = J.get(nearby, "reduce")(_f23, 0)
        def _f24(s=J.undefined, r=J.undefined, *_args):
            return J.add(s, (_t1 if J.truthy(_t1 := num(J.get(r, "p_Openinterest"))) else 0))
        putOi = J.get(nearby, "reduce")(_f24, 0)
        opt = J.obj(("ok", quoteOk), ("expiry", expiry), ("strike", num(J.get(atm, "strike"))), ("cb", cb), ("ca", ca), ("pb", pb), ("pa", pa), ("ratio", J.div(J.add(ca, pa), spot)), ("cSpread", (J.div(J.sub(ca, cb), cm) if J.gt(cm, 0) else G_NaN)), ("pSpread", (J.div(J.sub(pa, pb), pm) if J.gt(pm, 0) else G_NaN)), ("oiRatio", (J.div(putOi, callOi) if J.gt(callOi, 0) else G_NaN)))
    except Exception as _e25:
        e = J.catch_value(_e25)
        pass
    i = J.sub(J.get(G_close, "length"), 1)
    stamp = J.get(moment(J.mul(J.get(G_time, i), 1000)), "tz")(TZ)
    def pct(v=J.undefined, *_args):
        return (J.add(J.get(J.mul(v, 100), "toFixed")(2), "%") if J.truthy(J.get(G_Number, "isFinite")(v)) else "—")
    def cell(text=J.undefined, _p1=J.undefined, *_args):
        _t2 = _p1
        if _t2 is J.undefined:
            _t2 = "#E8EEF8"
        color = _t2
        return J.obj(("text", text), ("color", color), ("padding", 7))
    vwapDistance = (J.div(J.sub(J.get(G_close, i), J.get(sessionVwap, i)), J.get(G_close, i)) if J.truthy(J.get(G_Number, "isFinite")(J.get(sessionVwap, i))) else G_NaN)
    spreadsPass = (J.le(J.get(opt, "pSpread"), J.div(maxSpread, 100)) if J.truthy(_t26 := (J.le(J.get(opt, "cSpread"), J.div(maxSpread, 100)) if J.truthy(_t27 := J.get(opt, "ok")) else _t27)) else _t26)
    status = ("OPTIONS DATA UNAVAILABLE" if (not J.truthy(J.get(opt, "ok"))) else ("RESEARCH ONLY · QUOTE AGE UNKNOWN" if J.truthy(spreadsPass) else "WIDE MARKET · DO NOT EXECUTE"))
    G_paint_overlay("CGPanel", J.obj(("position", "top_right"), ("offset_y", 18), ("order", "above_all")), J.obj(("background", "#0B1220"), ("border", "1px solid #26354D"), ("rows", J.JSArray([J.obj(("cells", J.JSArray([cell("CONVEXITY GUARD", "#44D7E8"), cell("zxzinn research", "#8EA0B8")]))), J.obj(("cells", J.JSArray([cell(("VOLATILITY RESET" if J.truthy(J.get(reset, i)) else ("VOLATILITY EVENT" if J.truthy(J.get(event, i)) else "NO EVENT")), ("#9C7CFF" if J.truthy(J.get(reset, i)) else ("#FFBD59" if J.truthy(J.get(event, i)) else "#8EA0B8"))), cell(J.add(J.get(stamp, "format")("HH:mm"), " ET"))]))), J.obj(("cells", J.JSArray([cell(J.add(J.add(lookback, "-bar move: "), pct(J.get(move, i)))), cell(J.add("VWAP distance: ", pct(vwapDistance)))]))), J.obj(("cells", J.JSArray([cell(J.add(J.add(J.add("ATM ", (J.get(opt, "strike") if J.truthy(J.get(G_Number, "isFinite")(J.get(opt, "strike"))) else "—")), " · "), J.get(opt, "expiry"))), cell(J.add("Ask premium/spot: ", pct(J.get(opt, "ratio"))), "#44D7E8")]))), J.obj(("cells", J.JSArray([cell(J.add(J.add(J.add(J.add(J.add("Call bid/ask ", (J.get(J.get(opt, "cb"), "toFixed")(2) if J.truthy(J.get(G_Number, "isFinite")(J.get(opt, "cb"))) else "—")), " × "), (J.get(J.get(opt, "ca"), "toFixed")(2) if J.truthy(J.get(G_Number, "isFinite")(J.get(opt, "ca"))) else "—")), "<br/>spread "), pct(J.get(opt, "cSpread")))), cell(J.add(J.add(J.add(J.add(J.add("Put bid/ask ", (J.get(J.get(opt, "pb"), "toFixed")(2) if J.truthy(J.get(G_Number, "isFinite")(J.get(opt, "pb"))) else "—")), " × "), (J.get(J.get(opt, "pa"), "toFixed")(2) if J.truthy(J.get(G_Number, "isFinite")(J.get(opt, "pa"))) else "—")), "<br/>spread "), pct(J.get(opt, "pSpread"))))]))), J.obj(("cells", J.JSArray([cell(J.add("Nearby put/call OI: ", (J.get(J.get(opt, "oiRatio"), "toFixed")(2) if J.truthy(J.get(G_Number, "isFinite")(J.get(opt, "oiRatio"))) else "—")), "#9C7CFF"), cell(("Range reset detected" if J.truthy(J.get(reset, i)) else "No range reset"), ("#9C7CFF" if J.truthy(J.get(reset, i)) else "#8EA0B8"))]))), J.obj(("cells", J.JSArray([J.obj(*J.obj_spread(cell(status, ("#FFBD59" if J.truthy(spreadsPass) else "#FF6577"))), ("colspan", 2), ("textAlign", "center"))]))), J.obj(("cells", J.JSArray([J.obj(*J.obj_spread(cell("Research only · no order instruction", "#8EA0B8")), ("colspan", 2), ("textAlign", "center"))])))]))))


register_store_indicator(
    script,
    name='convexity_guard_by_zxzinn_TS',
    title='Convexity Guard by zxzinn',
    developer='Chao Chin Chang',
    url='https://trendspider.com/trading-tools-store/indicators/6aa82c-convexity-guard-by-zxzinn/',
    position='price',
    inputs=[{'id': 'warmup', 'title': 'Warmup', 'type': 'number', 'default': 120}, {'id': 'lookback_bars', 'title': 'Lookback bars', 'type': 'number', 'default': 5}, {'id': 'event_threshold__', 'title': 'Event threshold %', 'type': 'number', 'default': 0.55}, {'id': 'reset_threshold', 'title': 'Reset threshold', 'type': 'number', 'default': 0.35}, {'id': 'event_labels', 'title': 'Event labels', 'type': 'select_wide', 'default': 'Yes', 'options': ['Yes', 'No']}, {'id': 'max_leg_spread__', 'title': 'Max leg spread %', 'type': 'number', 'default': 18}],
    outputs=['session_vwap', 'vol_event', 'research_volatility', 'research_range_reset'],
    signals=['research_volatility', 'research_range_reset'],
    requires=['http'],
    parity='exact',
)
