"""
Options Gravity Map (Pin Risk + Magneto-Flow) -- TrendSpider store indicator by Feliks Ba\u0144ka.

Registered as "options_gravity_map_pin_risk_magneto_flow_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68a611-options-gravity-map-pin-risk-magneto-flow/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Array = G["Array"]
    G_Infinity = G["Infinity"]
    G_Math = G["Math"]
    G_Number = G["Number"]
    G_close = G["close"]
    G_color_candles = G["color_candles"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_ema = G["ema"]
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_horizontal_line = G["horizontal_line"]
    G_input = G["input"]
    G_isFinite = G["isFinite"]
    G_low = G["low"]
    G_paint = G["paint"]
    G_paint_overlay = G["paint_overlay"]
    G_register_signal = G["register_signal"]
    G_request = G["request"]
    G_series_of = G["series_of"]
    def move(s=J.undefined, k=J.undefined, *_args):
        o = G_series_of(None)
        i = 0
        while J.lt(i, J.get(s, "length")):
            j = J.sub(i, k)
            J.set(o, i, (J.get(s, j) if J.ge(j, 0) else None))
            i = J.inc(i)
        return o
    def bandWidthAt(i=J.undefined, *_args):
        if J.seq(bandMode, "ATR ×"):
            a = J.get(atrCalc, i)
            return (J.mul(a, bandATRx) if (not J.nullish(a)) else None)
        return bandAbs
    def sortByStrikes(*_args):
        i_4 = 1
        while J.lt(i_4, J.get(strikes, "length")):
            j = i_4
            sk = J.get(strikes, i_4)
            sz_2 = J.get(sizes, i_4)
            ca = J.get(calls, i_4)
            pu = J.get(puts, i_4)
            while (J.gt(j, 0) and J.gt(J.get(strikes, J.sub(j, 1)), sk)):
                J.set(strikes, j, J.get(strikes, J.sub(j, 1)))
                J.set(sizes, j, J.get(sizes, J.sub(j, 1)))
                J.set(calls, j, J.get(calls, J.sub(j, 1)))
                J.set(puts, j, J.get(puts, J.sub(j, 1)))
                j = J.dec(j)
            J.set(strikes, j, sk)
            J.set(sizes, j, sz_2)
            J.set(calls, j, ca)
            J.set(puts, j, pu)
            i_4 = J.inc(i_4)
    G_describe_indicator("Options Gravity Map (Pin Risk + Magneto-Flow) #TSBuild25", "price", J.obj(("shortName", "OptGravity"), ("decimals", 2)))
    gSrc = "① Source & Filters"
    gBand = "② Band/Potential"
    gVis = "③ Visuals"
    gSig = "④ Signals"
    srcMode = J.get(G_input, "select")("Source", "Options", J.JSArray(["Options", "Grid", "Manual"]), J.obj(("group", gSrc)))
    topN = J.get(G_input, "number")("Top N strikes (by size)", 5, J.obj(("min", 1), ("max", 15), ("step", 1), ("group", gSrc)))
    minSize = J.get(G_input, "number")("Min option size", 1, J.obj(("min", 1), ("step", 1), ("group", gSrc)))
    useCALL = J.get(G_input, "boolean")("Include CALL", True, J.obj(("group", gSrc)))
    usePUT = J.get(G_input, "boolean")("Include PUT", True, J.obj(("group", gSrc)))
    mCount = J.get(G_input, "number")("Manual: count (0–4)", 0, J.obj(("min", 0), ("max", 4), ("step", 1), ("group", gSrc)))
    ms1 = J.get(G_input, "number")("S1", 0, J.obj(("group", gSrc)))
    ms2 = J.get(G_input, "number")("S2", 0, J.obj(("group", gSrc)))
    ms3 = J.get(G_input, "number")("S3", 0, J.obj(("group", gSrc)))
    ms4 = J.get(G_input, "number")("S4", 0, J.obj(("group", gSrc)))
    bandMode = J.get(G_input, "select")("Band width mode", "Absolute", J.JSArray(["Absolute", "ATR ×"]), J.obj(("group", gBand)))
    bandAbs = J.get(G_input, "number")("Band ±Abs", 2, J.obj(("min", 0.05), ("step", 0.05), ("group", gBand)))
    atrLen = J.get(G_input, "number")("ATR Len (if ATR ×)", 14, J.obj(("min", 2), ("step", 1), ("group", gBand)))
    bandATRx = J.get(G_input, "number")("Band ATR ×", 0.5, J.obj(("min", 0.05), ("step", 0.05), ("group", gBand)))
    alpha = J.get(G_input, "number")("Gravity falloff α", 1.5, J.obj(("min", 0.5), ("step", 0.1), ("group", gBand)))
    potScale = J.get(G_input, "number")("Potential scale (0–100≈max)", 100, J.obj(("min", 10), ("step", 5), ("group", gBand)))
    showWalls = J.get(G_input, "boolean")("Show top-N walls", True, J.obj(("group", gVis)))
    tintPins = J.get(G_input, "boolean")("Tint candles when pin risk high", True, J.obj(("group", gVis)))
    showBary = J.get(G_input, "boolean")("Show options barycenter line", True, J.obj(("group", gVis)))
    showMagnet = J.get(G_input, "boolean")("Show Magnet label", True, J.obj(("group", gVis)))
    showDots = J.get(G_input, "boolean")("Show dots when inside any band", False, J.obj(("group", gVis)))
    pinZ = J.get(G_input, "number")("Pin Risk threshold (0–100)", 60, J.obj(("min", 1), ("max", 100), ("step", 1), ("group", gSig)))
    flowThr = J.get(G_input, "number")("Flow threshold (|value|)", 10, J.obj(("min", 1), ("step", 1), ("group", gSig)))
    nearMagAbs = J.get(G_input, "number")("Near-Magnet distance (abs)", 1, J.obj(("min", 0.01), ("step", 0.01), ("group", gSig)))
    prevClose = move(G_close, 1)
    def _f1(h=J.undefined, l=J.undefined, pc=J.undefined, i=J.undefined, *_args):
        if J.seq(i, 0):
            return None
        a = (J.get(G_Math, "abs")(J.sub(h, l)) if ((not J.nullish(h)) and (not J.nullish(l))) else None)
        b = (J.get(G_Math, "abs")(J.sub(h, pc)) if ((not J.nullish(h)) and (not J.nullish(pc))) else None)
        c = (J.get(G_Math, "abs")(J.sub(l, pc)) if ((not J.nullish(l)) and (not J.nullish(pc))) else None)
        m = J.get(G_Math, "max")((J.neg(G_Infinity) if (J.nullish(a)) else a), (J.neg(G_Infinity) if (J.nullish(b)) else b), (J.neg(G_Infinity) if (J.nullish(c)) else c))
        return (None if J.seq(m, J.neg(G_Infinity)) else m)
    tr = G_for_every(G_high, G_low, prevClose, _f1)
    atrCalc = G_ema(tr, atrLen)
    strikes = J.JSArray([])
    sizes = J.JSArray([])
    calls = J.JSArray([])
    puts = J.JSArray([])
    infoTxt = ""
    usedOptions = False
    if J.seq(srcMode, "Options"):
        try:
            opt = J.get(G_request, "unusual_options")(J.get(G_current, "ticker"))
            if ((J.truthy(opt) and J.truthy(J.get(G_Array, "isArray")(opt))) and J.gt(J.get(opt, "length"), 0)):
                agg = J.obj()
                i = 0
                while J.lt(i, J.get(opt, "length")):
                    o = J.get(opt, i)
                    if (not J.truthy(o)):
                        i = J.inc(i)
                        continue
                    k = G_Number(J.get(o, "strike"))
                    t = J.get(o, "type")
                    sz = G_Number(J.get(o, "size"))
                    if ((not J.truthy(G_isFinite(k))) or (not J.truthy(G_isFinite(sz)))):
                        i = J.inc(i)
                        continue
                    if J.lt(sz, minSize):
                        i = J.inc(i)
                        continue
                    if ((J.seq(t, "CALL") and (not J.truthy(useCALL))) or (J.seq(t, "PUT") and (not J.truthy(usePUT)))):
                        i = J.inc(i)
                        continue
                    if (J.nullish(J.get(agg, k))):
                        J.set(agg, k, J.obj(("total", 0), ("calls", 0), ("puts", 0)))
                    _t2 = J.get(agg, k)
                    J.set(_t2, "total", J.add(J.get(_t2, "total"), sz))
                    if J.seq(t, "CALL"):
                        _t3 = J.get(agg, k)
                        J.set(_t3, "calls", J.add(J.get(_t3, "calls"), sz))
                    if J.seq(t, "PUT"):
                        _t4 = J.get(agg, k)
                        J.set(_t4, "puts", J.add(J.get(_t4, "puts"), sz))
                    i = J.inc(i)
                rows = J.JSArray([])
                for ks in J.iter_in(agg):
                    J.get(rows, "push")(J.obj(("k", G_Number(ks)), ("t", J.get(J.get(agg, ks), "total")), ("c", J.get(J.get(agg, ks), "calls")), ("p", J.get(J.get(agg, ks), "puts"))))
                def _f5(a=J.undefined, b=J.undefined, *_args):
                    return J.sub(J.get(b, "t"), J.get(a, "t"))
                J.get(rows, "sort")(_f5)
                take = J.get(G_Math, "min")(topN, J.get(rows, "length"))
                i_2 = 0
                while J.lt(i_2, take):
                    J.get(strikes, "push")(J.get(J.get(rows, i_2), "k"))
                    J.get(sizes, "push")(J.get(J.get(rows, i_2), "t"))
                    J.get(calls, "push")(J.get(J.get(rows, i_2), "c"))
                    J.get(puts, "push")(J.get(J.get(rows, i_2), "p"))
                    i_2 = J.inc(i_2)
                usedOptions = J.gt(J.get(strikes, "length"), 0)
                infoTxt = (J.template("Options walls (top ", take, ")") if J.truthy(usedOptions) else "No qualifying options — grid fallback")
            else:
                infoTxt = "No unusual options — grid fallback"
        except Exception as _e6:
            e = J.catch_value(_e6)
            infoTxt = "Options fetch error — grid fallback"
    if ((not J.truthy(usedOptions)) and J.seq(srcMode, "Manual")):
        arr = J.JSArray([ms1, ms2, ms3, ms4])
        N = J.get(G_Math, "min")(mCount, J.get(arr, "length"))
        i_3 = 0
        while J.lt(i_3, N):
            v = J.get(arr, i_3)
            if (((not J.nullish(v)) and J.truthy(G_isFinite(v))) and J.gt(v, 0)):
                J.get(strikes, "push")(v)
                J.get(sizes, "push")(1)
                J.get(calls, "push")(0)
                J.get(puts, "push")(0)
            i_3 = J.inc(i_3)
        infoTxt = J.template("Manual walls (", J.get(strikes, "length"), ")")
    if J.seq(J.get(strikes, "length"), 0):
        last = J.get(G_close, J.sub(J.get(G_close, "length"), 1))
        if (not J.nullish(last)):
            step = J.get(G_Math, "max")(0.0001, J.mul(last, 0.05))
            base = J.mul(J.get(G_Math, "round")(J.div(last, step)), step)
            strikes = J.JSArray([J.sub(base, step), base, J.add(base, step)])
            sizes = J.JSArray([1, 1, 1])
            calls = J.JSArray([1, 0, 0])
            puts = J.JSArray([0, 1, 1])
            infoTxt = ("Grid (3-nearest)" if J.seq(srcMode, "Grid") else (_t7 if J.truthy(_t7 := infoTxt) else "Fallback: Grid (3-nearest)"))
    sortByStrikes()
    totalSize = 0
    weighted = 0
    i_4 = 0
    while J.lt(i_4, J.get(strikes, "length")):
        if J.truthy(G_isFinite(J.get(sizes, i_4))):
            totalSize = J.add(totalSize, J.get(sizes, i_4))
            weighted = J.add(weighted, J.mul(J.get(strikes, i_4), J.get(sizes, i_4)))
        i_4 = J.inc(i_4)
    bary = (J.div(weighted, totalSize) if J.gt(totalSize, 0) else None)
    eps = 1.0e-9
    def _f8(_c=J.undefined, _p=J.undefined, i_5=J.undefined, *_args):
        p = J.get(G_close, i_5)
        if (J.nullish(p)):
            return None
        W = bandWidthAt(i_5)
        if (J.nullish(W)):
            return None
        total = 0
        j = 0
        while J.lt(j, J.get(strikes, "length")):
            d = J.div(J.get(G_Math, "abs")(J.sub(p, J.get(strikes, j))), J.add(W, eps))
            total = J.add(total, J.div(J.get(sizes, j), J.get(G_Math, "pow")(J.add(1, d), alpha)))
            j = J.inc(j)
        return (J.mul(J.div(total, totalSize), potScale) if J.gt(totalSize, 0) else None)
    potential = G_for_every(G_close, _f8)
    def _f9(_c=J.undefined, _p=J.undefined, i_5=J.undefined, *_args):
        p = J.get(G_close, i_5)
        if (J.nullish(p)):
            return None
        W = bandWidthAt(i_5)
        if (J.nullish(W)):
            return None
        g = 0
        j = 0
        while J.lt(j, J.get(strikes, "length")):
            s = (1 if J.ge(J.get(strikes, j), p) else (-1))
            d = J.div(J.get(G_Math, "abs")(J.sub(p, J.get(strikes, j))), J.add(W, eps))
            g = J.add(g, J.div(J.mul(J.get(sizes, j), s), J.get(G_Math, "pow")(J.add(1, d), J.add(alpha, 1))))
            j = J.inc(j)
        return (J.mul(J.div(g, totalSize), J.div(potScale, 2)) if J.gt(totalSize, 0) else None)
    flow = G_for_every(G_close, _f9)
    if J.truthy(showWalls):
        i_5 = 0
        while J.lt(i_5, J.get(strikes, "length")):
            domCall = J.ge(J.get(calls, i_5), J.get(puts, i_5))
            col = ("#4DA3FF" if J.truthy(domCall) else "#E05A5A")
            G_paint(G_horizontal_line(J.get(strikes, i_5)), J.obj(("name", J.template("Wall ", J.get(G_Number(J.get(strikes, i_5)), "toFixed")(2))), ("color", col), ("style", "dotted")))
            def _f10(_c=J.undefined, _p=J.undefined, ii=J.undefined, *_args):
                w = bandWidthAt(ii)
                return (None if (J.nullish(w)) else J.add(J.get(strikes, i_5), w))
            up = G_for_every(G_close, _f10)
            def _f11(_c=J.undefined, _p=J.undefined, ii=J.undefined, *_args):
                w = bandWidthAt(ii)
                return (None if (J.nullish(w)) else J.sub(J.get(strikes, i_5), w))
            dn = G_for_every(G_close, _f11)
            G_paint(up, J.obj(("name", ""), ("color", col), ("style", "dotted")))
            G_paint(dn, J.obj(("name", ""), ("color", col), ("style", "dotted")))
            def _f12(c=J.undefined, u=J.undefined, d=J.undefined, *_args):
                return ((J.ge(c, d) if J.truthy(_t1 := J.le(c, u)) else _t1) if (((not J.nullish(c)) and (not J.nullish(u))) and (not J.nullish(d))) else False)
            inBand = G_for_every(G_close, up, dn, _f12)
            if J.truthy(showDots):
                def _f13(b=J.undefined, ii=J.undefined, *_args):
                    return (J.get(G_close, ii) if J.truthy(b) else None)
                dots = G_for_every(inBand, _f13)
                G_paint(dots, J.obj(("name", ""), ("color", "#FFB000"), ("style", "dots"), ("thickness", 3)))
            i_5 = J.inc(i_5)
    if (J.truthy(showBary) and (not J.nullish(bary))):
        G_paint(G_horizontal_line(bary), J.obj(("name", "Barycenter"), ("color", "#C0C0C0"), ("style", "line")))
    if J.truthy(tintPins):
        def _f14(v_2=J.undefined, *_args):
            if (J.nullish(v_2)):
                return None
            return ("#E9D7FF" if J.ge(v_2, pinZ) else None)
        tint = G_for_every(potential, _f14)
        G_color_candles(tint)
    lastC = J.get(G_close, J.sub(J.get(G_close, "length"), 1))
    bestLevel = None
    bestDist = None
    if ((not J.nullish(lastC)) and J.gt(J.get(strikes, "length"), 0)):
        i_6 = 0
        while J.lt(i_6, J.get(strikes, "length")):
            d = J.get(G_Math, "abs")(J.sub(lastC, J.get(strikes, i_6)))
            if ((J.nullish(bestDist)) or J.lt(d, bestDist)):
                bestDist = d
                bestLevel = J.get(strikes, i_6)
            i_6 = J.inc(i_6)
    magnetText = (J.template("Magnet ", ("↑" if J.gt(bestLevel, lastC) else ("↓" if J.lt(bestLevel, lastC) else "•")), " ", J.get(G_Number(bestLevel), "toFixed")(2), "  (Δ=", J.get(G_Number(bestDist), "toFixed")(2), ")") if ((not J.nullish(bestLevel)) and (not J.nullish(bestDist))) else "Magnet: n/a")
    G_paint_overlay("magnet_overlay", J.obj(("position", "top_right")), J.obj(("rows", (J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", magnetText), ("color", "var(--text-color)"), ("padding", 6), ("border", "solid var(--border-color) 1px"))])))]) if J.truthy(showMagnet) else J.JSArray([])))))
    def _f15(v_2=J.undefined, *_args):
        return (J.ge(v_2, pinZ) if J.truthy(_t1 := (not J.nullish(v_2))) else _t1)
    pinHigh = G_for_every(potential, _f15)
    G_register_signal(pinHigh, "OptGrav: Pin Risk High")
    def _f16(v_2=J.undefined, *_args):
        return (J.ge(v_2, flowThr) if J.truthy(_t1 := (not J.nullish(v_2))) else _t1)
    upFlow = G_for_every(flow, _f16)
    def _f17(v_2=J.undefined, *_args):
        return (J.le(v_2, J.neg(flowThr)) if J.truthy(_t1 := (not J.nullish(v_2))) else _t1)
    downFlow = G_for_every(flow, _f17)
    G_register_signal(upFlow, "OptGrav: Up-Flow (options pull up)")
    G_register_signal(downFlow, "OptGrav: Down-Flow (options pull down)")
    def _f18(c=J.undefined, *_args):
        if ((J.nullish(c)) or J.seq(J.get(strikes, "length"), 0)):
            return False
        dmin = None
        i_7 = 0
        while J.lt(i_7, J.get(strikes, "length")):
            d_2 = J.get(G_Math, "abs")(J.sub(c, J.get(strikes, i_7)))
            if ((J.nullish(dmin)) or J.lt(d_2, dmin)):
                dmin = d_2
            i_7 = J.inc(i_7)
        return (J.le(dmin, nearMagAbs) if J.truthy(_t1 := (not J.nullish(dmin))) else _t1)
    nearMag = G_for_every(G_close, _f18)
    G_register_signal(nearMag, "OptGrav: Near Magnet (≤ distance)")


register_store_indicator(
    script,
    name='options_gravity_map_pin_risk_magneto_flow_TS',
    title='Options Gravity Map (Pin Risk + Magneto-Flow)',
    developer='Feliks Ba\\u0144ka',
    url='https://trendspider.com/trading-tools-store/indicators/68a611-options-gravity-map-pin-risk-magneto-flow/',
    position='price',
    inputs=[{'id': 'source', 'title': 'Source', 'type': 'select_wide', 'default': 'Options', 'options': ['Options', 'Grid', 'Manual']}, {'id': 'top_n_strikes__by_size_', 'title': 'Top N strikes (by size)', 'type': 'number', 'default': 5}, {'id': 'min_option_size', 'title': 'Min option size', 'type': 'number', 'default': 1}, {'id': 'include_call', 'title': 'Include CALL', 'type': 'boolean', 'default': True}, {'id': 'include_put', 'title': 'Include PUT', 'type': 'boolean', 'default': True}, {'id': 'manual__count__0_4_', 'title': 'Manual: count (0–4)', 'type': 'number', 'default': 0}, {'id': 's1', 'title': 'S1', 'type': 'number', 'default': 0}, {'id': 's2', 'title': 'S2', 'type': 'number', 'default': 0}, {'id': 's3', 'title': 'S3', 'type': 'number', 'default': 0}, {'id': 's4', 'title': 'S4', 'type': 'number', 'default': 0}, {'id': 'band_width_mode', 'title': 'Band width mode', 'type': 'select_wide', 'default': 'Absolute', 'options': ['Absolute', 'ATR ×']}, {'id': 'band__abs', 'title': 'Band ±Abs', 'type': 'number', 'default': 2}, {'id': 'atr_len__if_atr___', 'title': 'ATR Len (if ATR ×)', 'type': 'number', 'default': 14}, {'id': 'band_atr__', 'title': 'Band ATR ×', 'type': 'number', 'default': 0.5}, {'id': 'gravity_falloff__', 'title': 'Gravity falloff α', 'type': 'number', 'default': 1.5}, {'id': 'potential_scale__0_100_max_', 'title': 'Potential scale (0–100≈max)', 'type': 'number', 'default': 100}, {'id': 'show_top_n_walls', 'title': 'Show top-N walls', 'type': 'boolean', 'default': True}, {'id': 'tint_candles_when_pin_risk_high', 'title': 'Tint candles when pin risk high', 'type': 'boolean', 'default': True}, {'id': 'show_options_barycenter_line', 'title': 'Show options barycenter line', 'type': 'boolean', 'default': True}, {'id': 'show_magnet_label', 'title': 'Show Magnet label', 'type': 'boolean', 'default': True}, {'id': 'show_dots_when_inside_any_band', 'title': 'Show dots when inside any band', 'type': 'boolean', 'default': False}, {'id': 'pin_risk_threshold__0_100_', 'title': 'Pin Risk threshold (0–100)', 'type': 'number', 'default': 60}, {'id': 'flow_threshold___value__', 'title': 'Flow threshold (|value|)', 'type': 'number', 'default': 10}, {'id': 'near_magnet_distance__abs_', 'title': 'Near-Magnet distance (abs)', 'type': 'number', 'default': 1}],
    outputs=['wall_251_00', 'line_2', 'line_3', 'wall_289_00', 'line_5', 'line_6', 'wall_293_00', 'line_8', 'line_9', 'wall_298_00', 'line_11', 'line_12', 'wall_343_00', 'line_14', 'line_15', 'barycenter', 'cdl', 'optgrav__pin_risk_high', 'optgrav__up_flow__options_pull_up_', 'optgrav__down_flow__options_pull_down_', 'optgrav__near_magnet____distance_'],
    signals=['optgrav__pin_risk_high', 'optgrav__up_flow__options_pull_up_', 'optgrav__down_flow__options_pull_down_', 'optgrav__near_magnet____distance_'],
    requires=['unusual_options'],
    parity='exact',
)
