"""
ZenAlgo · Mars -- TrendSpider store indicator by ZenAlgo.

Registered as "zenalgo_mars_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6aaa7d-zenalgo-%c2%b7-mars/)
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
    G_Number = G["Number"]
    G_Promise = G["Promise"]
    G_String = G["String"]
    G_bar_at = G["bar_at"]
    G_close = G["close"]
    G_color_cloud = G["color_cloud"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_fill = G["fill"]
    G_high = G["high"]
    G_input = G["input"]
    G_library = G["library"]
    G_low = G["low"]
    G_paint = G["paint"]
    G_paint_label_at_line = G["paint_label_at_line"]
    G_paint_overlay = G["paint_overlay"]
    G_register_signal = G["register_signal"]
    G_request = G["request"]
    G_time = G["time"]
    G_volume = G["volume"]
    def averageSeries(values=J.undefined, length=J.undefined, _p1=J.undefined, *_args):
        _t2 = _p1
        if _t2 is J.undefined:
            _t2 = False
        exponential = _t2
        result = J.get(G_Array(J.get(values, "length")), "fill")(None)
        total = 0
        previous = None
        queue = J.JSArray([])
        alpha = J.div(2, J.add(length, 1))
        index = 0
        while J.lt(index, J.get(values, "length")):
            value = J.get(values, index)
            if (not J.truthy(finite(value))):
                index = J.inc(index)
                continue
            if J.truthy(exponential):
                previous = (value if (previous is None) else J.add(J.mul(alpha, value), J.mul(J.sub(1, alpha), previous)))
                J.set(result, index, previous)
            else:
                J.get(queue, "push")(value)
                total = J.add(total, value)
                if J.gt(J.get(queue, "length"), length):
                    total = J.sub(total, J.get(queue, "shift")())
                if J.seq(J.get(queue, "length"), length):
                    J.set(result, index, J.div(total, length))
            index = J.inc(index)
        return result
    def wilderRsi(values=J.undefined, length=J.undefined, *_args):
        result = J.get(G_Array(J.get(values, "length")), "fill")(None)
        gain = 0
        loss = 0
        count = 0
        previous = None
        index = 0
        while J.lt(index, J.get(values, "length")):
            if (not J.truthy(finite(J.get(values, index)))):
                index = J.inc(index)
                continue
            if (previous is None):
                previous = J.get(values, index)
                index = J.inc(index)
                continue
            change = J.sub(J.get(values, index), previous)
            previous = J.get(values, index)
            up = J.get(G_Math, "max")(change, 0)
            down = J.get(G_Math, "max")(J.neg(change), 0)
            if J.lt(count, length):
                gain = J.add(gain, up)
                loss = J.add(loss, down)
                count = J.inc(count)
                if J.lt(count, length):
                    index = J.inc(index)
                    continue
                gain = J.div(gain, length)
                loss = J.div(loss, length)
            else:
                gain = J.div(J.add(J.mul(gain, J.sub(length, 1)), up), length)
                loss = J.div(J.add(J.mul(loss, J.sub(length, 1)), down), length)
            J.set(result, index, (100 if J.seq(loss, 0) else (0 if J.seq(gain, 0) else J.sub(100, J.div(100, J.add(1, J.div(gain, loss)))))))
            index = J.inc(index)
        return result
    def findDivergences(oscillator=J.undefined, lows=J.undefined, highs=J.undefined, left=J.undefined, right=J.undefined, minimum=J.undefined, maximum=J.undefined, *_args):
        events = J.JSArray([])
        previousLow = None
        previousHigh = None
        confirmation = J.add(left, right)
        while J.lt(confirmation, J.get(oscillator, "length")):
            pivot = J.sub(confirmation, right)
            value = J.get(oscillator, pivot)
            if (not J.truthy(finite(value))):
                confirmation = J.inc(confirmation)
                continue
            isLow = True
            isHigh = True
            index = J.sub(pivot, left)
            while J.le(index, confirmation):
                if J.seq(index, pivot):
                    index = J.inc(index)
                    continue
                other = J.get(oscillator, index)
                if (not J.truthy(finite(other))):
                    isLow = False
                    isHigh = False
                    break
                if J.truthy((J.lt(other, value) if J.lt(index, pivot) else J.le(other, value))):
                    isLow = False
                if J.truthy((J.gt(other, value) if J.lt(index, pivot) else J.ge(other, value))):
                    isHigh = False
                index = J.inc(index)
            for side in J.iter_of(J.JSArray(["low", "high"])):
                if J.truthy(((not J.truthy(isLow)) if J.seq(side, "low") else (not J.truthy(isHigh)))):
                    continue
                previous = (previousLow if J.seq(side, "low") else previousHigh)
                price = (lows if J.seq(side, "low") else highs)
                if (((previous is not None) and J.truthy(finite(J.get(price, pivot)))) and J.truthy(finite(J.get(price, previous)))):
                    barsSincePrevious = J.sub(J.sub(pivot, previous), 1)
                    if (J.ge(barsSincePrevious, minimum) and J.le(barsSincePrevious, maximum)):
                        priceChange = J.sub(J.get(price, pivot), J.get(price, previous))
                        oscillatorChange = J.sub(value, J.get(oscillator, previous))
                        type_ = None
                        if ((J.seq(side, "low") and J.lt(priceChange, 0)) and J.gt(oscillatorChange, 0)):
                            type_ = "regularBull"
                        if ((J.seq(side, "low") and J.gt(priceChange, 0)) and J.lt(oscillatorChange, 0)):
                            type_ = "hiddenBull"
                        if ((J.seq(side, "high") and J.gt(priceChange, 0)) and J.lt(oscillatorChange, 0)):
                            type_ = "regularBear"
                        if ((J.seq(side, "high") and J.lt(priceChange, 0)) and J.gt(oscillatorChange, 0)):
                            type_ = "hiddenBear"
                        if J.truthy(type_):
                            J.get(events, "push")(J.obj(("type", type_), ("pivot", pivot), ("previous", previous), ("confirmation", confirmation)))
                if J.seq(side, "low"):
                    previousLow = pivot
                else:
                    previousHigh = pivot
            confirmation = J.inc(confirmation)
        return events
    def sessionVwap(*_args):
        result = empty()
        session = None
        weighted = 0
        totalVolume = 0
        completeSession = False
        index = 0
        while J.lt(index, J.get(G_close, "length")):
            start = J.get(G_bar_at(J.get(G_time, index), "D", (J.get(G_current, "ext_session") if J.truthy(J.get(G_current, "is_ext_hours")) else J.get(G_current, "session"))), "sessionStartsAt")
            if J.sne(start, session):
                completeSession = (_t1 if J.truthy(_t1 := (session is not None)) else J.seq(J.get(G_time, index), start))
                session = start
                weighted = 0
                totalVolume = 0
            if ((((J.truthy(finite(J.get(G_volume, index))) and J.gt(J.get(G_volume, index), 0)) and J.truthy(finite(J.get(G_high, index)))) and J.truthy(finite(J.get(G_low, index)))) and J.truthy(finite(J.get(G_close, index)))):
                weighted = J.add(weighted, J.mul(J.div(J.add(J.add(J.get(G_high, index), J.get(G_low, index)), J.get(G_close, index)), 3), J.get(G_volume, index)))
                totalVolume = J.add(totalVolume, J.get(G_volume, index))
            if (J.truthy(completeSession) and J.gt(totalVolume, 0)):
                J.set(result, index, J.div(weighted, totalVolume))
            index = J.inc(index)
        return result
    G_describe_indicator("ZenAlgo · Mars", "lower", J.obj(("decimals", 2), ("shortName", "MARS"), ("mainColorInheritFrom", "Mars")))
    sourceSettings = J.get(G_input, "group")("Source")
    preset = J.get(sourceSettings, "select")("Preset", "Traditional", J.JSArray(["Traditional", "Fast", "Custom"]))
    customRsiLength = J.get(sourceSettings, "number")("Custom RSI length", 14, J.obj(("min", 1), ("max", 200)))
    customMaLength = J.get(sourceSettings, "number")("Custom MA length", 14, J.obj(("min", 1), ("max", 200)))
    customSignalLength = J.get(sourceSettings, "number")("Custom signal length", 9, J.obj(("min", 1), ("max", 200)))
    rsiLength = (J.get(G_Math, "round")(customRsiLength) if J.seq(preset, "Custom") else (7 if J.seq(preset, "Fast") else 14))
    maLength = (J.get(G_Math, "round")(customMaLength) if J.seq(preset, "Custom") else (7 if J.seq(preset, "Fast") else 14))
    signalLength = (J.get(G_Math, "round")(customSignalLength) if J.seq(preset, "Custom") else (3 if J.seq(preset, "Fast") else 9))
    divergenceSettings = J.get(G_input, "group")("Divergences")
    pivotLeft = J.get(G_Math, "round")(J.get(divergenceSettings, "number")("Pivot left", 5, J.obj(("min", 1), ("max", 50))))
    pivotRight = J.get(G_Math, "round")(J.get(divergenceSettings, "number")("Pivot right", 5, J.obj(("min", 1), ("max", 50))))
    minRangeInput = J.get(G_Math, "round")(J.get(divergenceSettings, "number")("Minimum pivot range", 5, J.obj(("min", 1), ("max", 500))))
    maxRangeInput = J.get(G_Math, "round")(J.get(divergenceSettings, "number")("Maximum pivot range", 60, J.obj(("min", 2), ("max", 500))))
    minRange = J.get(G_Math, "min")(minRangeInput, J.sub(maxRangeInput, 1))
    maxRange = J.get(G_Math, "max")(maxRangeInput, J.add(minRange, 1))
    divergenceHistory = J.get(divergenceSettings, "select")("Divergence placement", "Confirmation", J.JSArray(["Confirmation", "Pivot history"]))
    biasSettings = J.get(G_input, "group")("Bias")
    biasLookback = J.get(G_Math, "round")(J.get(biasSettings, "number")("Signal bias smoothing", 1, J.obj(("min", 1), ("max", 200))))
    zoneLookback = J.get(G_Math, "round")(J.get(biasSettings, "number")("Zone lookback", 100, J.obj(("min", 1), ("max", 1000))))
    normalBiasRatio = J.get(biasSettings, "number")("Bias ratio", 1.2, J.obj(("min", 1), ("max", 10)))
    fullBiasRatio = J.get(G_Math, "max")(normalBiasRatio, J.get(biasSettings, "number")("Full bias ratio", 1.8, J.obj(("min", 1), ("max", 10))))
    visualSettings = J.get(G_input, "group")("Appearance")
    appearance = J.get(visualSettings, "select")("Detail", "Signature", J.JSArray(["Minimal", "Signature"]))
    bullColor = J.get(visualSettings, "color")("Bullish color", "#3FC0DC")
    bearColor = J.get(visualSettings, "color")("Bearish color", "#A477FF")
    showConfirmationLabels = J.get(visualSettings, "boolean")("Confirmation labels", True)
    showDashboard = J.get(visualSettings, "boolean")("Dashboard", False)
    showTimeframes = J.get(visualSettings, "boolean")("Timeframe matrix", True)
    showSignalLegend = J.get(visualSettings, "boolean")("Signal legend", False)
    dashboardPosition = J.get(visualSettings, "select")("Dashboard position", "bottom_left", J.JSArray(["top_right", "bottom_right", "top_left", "bottom_left"]))
    dashboardSize = J.get(visualSettings, "select")("Dashboard size", "Compact", J.JSArray(["Compact", "Comfortable"]))
    muted = "#8E9CB3"
    warningColor = "#F5BE70"
    surface = "#101827"
    tinycolor = G_library("tinycolor2")
    def alphaColor(color=J.undefined, alpha=J.undefined, *_args):
        return J.get(J.get(tinycolor(color), "setAlpha")(alpha), "toRgbString")()
    def empty(*_args):
        return J.get(G_Array(J.get(G_close, "length")), "fill")(None)
    def finite(value=J.undefined, *_args):
        return (J.get(G_Number, "isFinite")(value) if J.truthy(_t1 := J.seq(J.typeof(value), "number")) else _t1)
    marsRsi = wilderRsi(G_close, rsiLength)
    mars = averageSeries(marsRsi, maLength)
    signal = averageSeries(mars, signalLength, True)
    bias = averageSeries(mars, biasLookback)
    def _f1(value=J.undefined, index=J.undefined, *_args):
        return (J.sub(value, J.get(signal, index)) if (J.truthy(finite(value)) and J.truthy(finite(J.get(signal, index)))) else None)
    spread = J.get(mars, "map")(_f1)
    dailyVwap = sessionVwap()
    def _f2(value=J.undefined, index=J.undefined, *_args):
        return ((bullColor if J.ge(value, J.get(signal, index)) else bearColor) if (J.truthy(finite(value)) and J.truthy(finite(J.get(signal, index)))) else muted)
    directionColors = J.get(mars, "map")(_f2)
    def _f3(value=J.undefined, index=J.undefined, *_args):
        if (not J.truthy(finite(value))):
            return muted
        rising_2 = (J.gt(value, J.get(spread, J.sub(index, 1))) if J.truthy(_t1 := finite(J.get(spread, J.sub(index, 1)))) else _t1)
        return alphaColor((bullColor if J.gt(value, 0) else bearColor), (1 if J.truthy(rising_2) else 0.4))
    histogramColors = J.get(spread, "map")(_f3)
    flags = J.obj()
    for name in J.iter_of(J.JSArray(["crossUp", "crossDown", "regularBull", "hiddenBull", "regularBear", "hiddenBear", "strongBull", "strongBear", "warningBull", "warningBear", "launchBull", "launchBear"])):
        J.set(flags, name, J.get(G_Array(J.get(G_close, "length")), "fill")(False))
    index = 1
    while J.lt(index, J.get(G_close, "length")):
        if (not J.truthy(J.get(J.JSArray([J.get(mars, index), J.get(mars, J.sub(index, 1)), J.get(signal, index), J.get(signal, J.sub(index, 1))]), "every")(finite))):
            index = J.inc(index)
            continue
        J.set(J.get(flags, "crossUp"), index, (J.le(J.get(mars, J.sub(index, 1)), J.get(signal, J.sub(index, 1))) if J.truthy(_t4 := J.gt(J.get(mars, index), J.get(signal, index))) else _t4))
        J.set(J.get(flags, "crossDown"), index, (J.ge(J.get(mars, J.sub(index, 1)), J.get(signal, J.sub(index, 1))) if J.truthy(_t5 := J.lt(J.get(mars, index), J.get(signal, index))) else _t5))
        hasVwap = (J.gt(J.get(G_volume, index), 0) if J.truthy(_t6 := (finite(J.get(G_volume, index)) if J.truthy(_t7 := finite(J.get(dailyVwap, index))) else _t7)) else _t6)
        J.set(J.get(flags, "launchBull"), index, (J.gt(J.get(G_close, index), J.get(dailyVwap, index)) if J.truthy(_t8 := (J.gt(J.get(spread, index), J.get(spread, J.sub(index, 1))) if J.truthy(_t9 := (J.le(J.get(mars, J.sub(index, 1)), 50) if J.truthy(_t10 := (J.gt(J.get(mars, index), 50) if J.truthy(_t11 := hasVwap) else _t11)) else _t10)) else _t9)) else _t8))
        J.set(J.get(flags, "launchBear"), index, (J.lt(J.get(G_close, index), J.get(dailyVwap, index)) if J.truthy(_t12 := (J.lt(J.get(spread, index), J.get(spread, J.sub(index, 1))) if J.truthy(_t13 := (J.ge(J.get(mars, J.sub(index, 1)), 50) if J.truthy(_t14 := (J.lt(J.get(mars, index), 50) if J.truthy(_t15 := hasVwap) else _t15)) else _t14)) else _t13)) else _t12))
        index = J.inc(index)
    divergences = findDivergences(mars, G_low, G_high, pivotLeft, pivotRight, minRange, maxRange)
    for event in J.iter_of(divergences):
        J.set(J.get(flags, J.get(event, "type")), J.get(event, "confirmation"), True)
    index_2 = 0
    while J.lt(index_2, J.get(G_close, "length")):
        J.set(J.get(flags, "strongBull"), index_2, (J.get(J.get(flags, "hiddenBull"), index_2) if J.truthy(_t16 := (J.gt(J.get(bias, index_2), 50) if J.truthy(_t17 := finite(J.get(bias, index_2))) else _t17)) else _t16))
        J.set(J.get(flags, "strongBear"), index_2, (J.get(J.get(flags, "hiddenBear"), index_2) if J.truthy(_t18 := (J.lt(J.get(bias, index_2), 50) if J.truthy(_t19 := finite(J.get(bias, index_2))) else _t19)) else _t18))
        J.set(J.get(flags, "warningBull"), index_2, (J.get(J.get(flags, "regularBull"), index_2) if J.truthy(_t20 := (J.lt(J.get(bias, index_2), 50) if J.truthy(_t21 := finite(J.get(bias, index_2))) else _t21)) else _t20))
        J.set(J.get(flags, "warningBear"), index_2, (J.get(J.get(flags, "regularBear"), index_2) if J.truthy(_t22 := (J.gt(J.get(bias, index_2), 50) if J.truthy(_t23 := finite(J.get(bias, index_2))) else _t23)) else _t22))
        index_2 = J.inc(index_2)
    decoration = J.obj(("hideInLegend", True), ("hideInScriptEditor", True), ("editorHidden", True))
    signature = J.seq(appearance, "Signature")
    G_paint(J.get(G_Array(J.get(G_close, "length")), "fill")(100), J.obj(("name", "Scale top"), ("color", "#00000000"), *J.obj_spread(decoration)))
    G_paint(J.get(G_Array(J.get(G_close, "length")), "fill")(0), J.obj(("name", "Scale bottom"), ("color", "#00000000"), *J.obj_spread(decoration)))
    upperLine = G_paint(J.get(G_Array(J.get(G_close, "length")), "fill")(70), J.obj(("name", "Upper zone"), ("color", "#A477FF55"), ("thickness", 1), *J.obj_spread(decoration)))
    lowerLine = G_paint(J.get(G_Array(J.get(G_close, "length")), "fill")(30), J.obj(("name", "Lower zone"), ("color", "#3FC0DC55"), ("thickness", 1), *J.obj_spread(decoration)))
    G_fill(upperLine, lowerLine, "#6E65C9", (0.055 if J.truthy(signature) else 0), "Mars atmosphere")
    G_paint(J.get(G_Array(J.get(G_close, "length")), "fill")(50), J.obj(("name", "Equilibrium"), ("color", "#8E9CB344"), ("style", "dotted"), ("thickness", 1), *J.obj_spread(decoration)))
    def _f24(value=J.undefined, *_args):
        return (J.obj(("high", J.get(G_Math, "max")(50, J.add(50, J.mul(value, (3 if J.seq(preset, "Fast") else 1))))), ("low", J.get(G_Math, "min")(50, J.add(50, J.mul(value, (3 if J.seq(preset, "Fast") else 1)))))) if J.truthy(finite(value)) else None)
    G_paint(J.get(spread, "map")(_f24), J.obj(("name", "Momentum histogram"), ("style", "columnrange"), ("color", histogramColors), *J.obj_spread(decoration)))
    def _f25(color=J.undefined, *_args):
        return alphaColor(color, 0.09)
    G_paint((mars if J.truthy(signature) else empty()), J.obj(("name", "Mars halo"), ("color", J.get(directionColors, "map")(_f25)), ("thickness", 9), *J.obj_spread(decoration)))
    marsLine = G_paint(mars, J.obj(("name", "Mars"), ("color", directionColors), ("thickness", 3), ("lastValueLabelEnabled", True)))
    signalLine = G_paint(signal, J.obj(("name", "Signal"), ("color", directionColors), ("thickness", 1), ("lastValueLabelEnabled", True)))
    G_color_cloud(mars, signal, bullColor, bearColor, "Bull momentum ribbon", "Bear momentum ribbon", (0.16 if J.truthy(signature) else 0))
    divergenceBullPoints = empty()
    divergenceBearPoints = empty()
    for event_2 in J.iter_of(divergences):
        index_3 = (J.get(event_2, "pivot") if J.seq(divergenceHistory, "Pivot history") else J.get(event_2, "confirmation"))
        J.set((divergenceBullPoints if J.truthy(J.get(J.get(event_2, "type"), "endsWith")("Bull")) else divergenceBearPoints), index_3, J.get(mars, index_3))
    bullPointsLine = G_paint(divergenceBullPoints, J.obj(("name", "Bullish divergence"), ("color", bullColor), ("style", "dotted"), ("thickness", 3), *J.obj_spread(decoration)))
    bearPointsLine = G_paint(divergenceBearPoints, J.obj(("name", "Bearish divergence"), ("color", bearColor), ("style", "dotted"), ("thickness", 3), *J.obj_spread(decoration)))
    for event_3 in J.iter_of(J.get(divergences, "slice")((-80))):
        bullish = J.get(J.get(event_3, "type"), "endsWith")("Bull")
        index_4 = (J.get(event_3, "pivot") if J.seq(divergenceHistory, "Pivot history") else J.get(event_3, "confirmation"))
        G_paint_label_at_line((bullPointsLine if J.truthy(bullish) else bearPointsLine), index_4, ("R" if J.truthy(J.get(J.get(event_3, "type"), "startsWith")("regular")) else "H"), J.obj(("color", (bullColor if J.truthy(bullish) else bearColor)), ("background_color", surface), ("border_color", (bullColor if J.truthy(bullish) else bearColor)), ("border_width", 1), ("border_radius", 3), ("vertical_align", ("bottom" if J.truthy(bullish) else "top"))))
    def _f26(active=J.undefined, index_5=J.undefined, *_args):
        return (J.get(mars, index_5) if J.truthy(active) else None)
    G_paint(J.get(J.get(flags, "crossUp"), "map")(_f26), J.obj(("name", "Bullish crossover"), ("style", "dotted"), ("marker", "circle"), ("color", bullColor), ("thickness", 3), *J.obj_spread(decoration)))
    def _f27(active=J.undefined, index_5=J.undefined, *_args):
        return (J.get(mars, index_5) if J.truthy(active) else None)
    G_paint(J.get(J.get(flags, "crossDown"), "map")(_f27), J.obj(("name", "Bearish crossover"), ("style", "dotted"), ("marker", "circle"), ("color", bearColor), ("thickness", 3), *J.obj_spread(decoration)))
    def _f28(active=J.undefined, *_args):
        return (10 if J.truthy(active) else None)
    G_paint(J.get(J.get(flags, "strongBull"), "map")(_f28), J.obj(("name", "Strong bull marker"), ("style", "dotted"), ("marker", "diamond"), ("color", bullColor), ("thickness", 5), *J.obj_spread(decoration)))
    def _f29(active=J.undefined, *_args):
        return (90 if J.truthy(active) else None)
    G_paint(J.get(J.get(flags, "strongBear"), "map")(_f29), J.obj(("name", "Strong bear marker"), ("style", "dotted"), ("marker", "diamond"), ("color", bearColor), ("thickness", 5), *J.obj_spread(decoration)))
    def _f30(active=J.undefined, *_args):
        return (10 if J.truthy(active) else None)
    G_paint(J.get(J.get(flags, "warningBull"), "map")(_f30), J.obj(("name", "Bull warning marker"), ("style", "dotted"), ("marker", "triangle"), ("color", warningColor), ("thickness", 4), *J.obj_spread(decoration)))
    def _f31(active=J.undefined, *_args):
        return (90 if J.truthy(active) else None)
    G_paint(J.get(J.get(flags, "warningBear"), "map")(_f31), J.obj(("name", "Bear warning marker"), ("style", "dotted"), ("marker", "triangle-down"), ("color", warningColor), ("thickness", 4), *J.obj_spread(decoration)))
    def _f32(active=J.undefined, *_args):
        return (4 if J.truthy(active) else None)
    G_paint(J.get(J.get(flags, "launchBull"), "map")(_f32), J.obj(("name", "Bull launch marker"), ("style", "dotted"), ("marker", "triangle"), ("color", bullColor), ("thickness", 4), *J.obj_spread(decoration)))
    def _f33(active=J.undefined, *_args):
        return (96 if J.truthy(active) else None)
    G_paint(J.get(J.get(flags, "launchBear"), "map")(_f33), J.obj(("name", "Bear launch marker"), ("style", "dotted"), ("marker", "triangle-down"), ("color", bearColor), ("thickness", 4), *J.obj_spread(decoration)))
    def _f34(active=J.undefined, index_5=J.undefined, *_args):
        return (18 if (J.truthy(showConfirmationLabels) and (J.truthy(active) or J.truthy(J.get(J.get(flags, "strongBull"), index_5)))) else None)
    bullConfirmationLine = G_paint(J.get(J.get(flags, "launchBull"), "map")(_f34), J.obj(("name", "Bull confirmation anchor"), ("style", "dotted"), ("color", "#00000000"), ("thickness", 1), ("ignoreWhenScaling", True), *J.obj_spread(decoration)))
    def _f35(active=J.undefined, index_5=J.undefined, *_args):
        return (82 if (J.truthy(showConfirmationLabels) and (J.truthy(active) or J.truthy(J.get(J.get(flags, "strongBear"), index_5)))) else None)
    bearConfirmationLine = G_paint(J.get(J.get(flags, "launchBear"), "map")(_f35), J.obj(("name", "Bear confirmation anchor"), ("style", "dotted"), ("color", "#00000000"), ("thickness", 1), ("ignoreWhenScaling", True), *J.obj_spread(decoration)))
    confirmationLabels = J.JSArray([])
    if J.truthy(showConfirmationLabels):
        index_5 = 0
        while J.lt(index_5, J.get(G_close, "length")):
            if (J.truthy(J.get(J.get(flags, "launchBull"), index_5)) or J.truthy(J.get(J.get(flags, "strongBull"), index_5))):
                J.get(confirmationLabels, "push")(J.obj(("index", index_5), ("bullish", True), ("launch", J.get(J.get(flags, "launchBull"), index_5))))
            if (J.truthy(J.get(J.get(flags, "launchBear"), index_5)) or J.truthy(J.get(J.get(flags, "strongBear"), index_5))):
                J.get(confirmationLabels, "push")(J.obj(("index", index_5), ("bullish", False), ("launch", J.get(J.get(flags, "launchBear"), index_5))))
            index_5 = J.inc(index_5)
    for event_4 in J.iter_of(J.get(confirmationLabels, "slice")((-80))):
        color = (bullColor if J.truthy(J.get(event_4, "bullish")) else bearColor)
        G_paint_label_at_line((bullConfirmationLine if J.truthy(J.get(event_4, "bullish")) else bearConfirmationLine), J.get(event_4, "index"), J.template(("MARS" if J.truthy(J.get(event_4, "launch")) else "H"), " ", ("↑" if J.truthy(J.get(event_4, "bullish")) else "↓")), J.obj(("color", color), ("background_color", surface), ("border_color", color), ("border_width", 1), ("border_radius", 3), ("vertical_align", ("top" if J.truthy(J.get(event_4, "bullish")) else "bottom"))))
    G_register_signal(J.get(flags, "crossUp"), "Mars crossed above Signal")
    G_register_signal(J.get(flags, "crossDown"), "Mars crossed below Signal")
    G_register_signal(J.get(flags, "regularBull"), "Regular bullish divergence confirmed")
    G_register_signal(J.get(flags, "hiddenBull"), "Hidden bullish divergence confirmed")
    G_register_signal(J.get(flags, "regularBear"), "Regular bearish divergence confirmed")
    G_register_signal(J.get(flags, "hiddenBear"), "Hidden bearish divergence confirmed")
    G_register_signal(J.get(flags, "strongBull"), "Strong bull")
    G_register_signal(J.get(flags, "strongBear"), "Strong bear")
    G_register_signal(J.get(flags, "warningBull"), "Bullish warning")
    G_register_signal(J.get(flags, "warningBear"), "Bearish warning")
    G_register_signal(J.get(flags, "launchBull"), "Bull launch with session VWAP")
    G_register_signal(J.get(flags, "launchBear"), "Bear launch with session VWAP")
    last = J.sub(J.get(G_close, "length"), 1)
    def fmt(value=J.undefined, *_args):
        return (J.get(value, "toFixed")(1) if J.truthy(finite(value)) else "—")
    zoneSample = J.get(J.get(mars, "slice")(J.get(G_Math, "max")(0, J.sub(J.get(G_close, "length"), zoneLookback))), "filter")(finite)
    def _f36(value=J.undefined, *_args):
        return J.gt(value, 70)
    def _f37(value=J.undefined, *_args):
        return J.gt(value, 50)
    def _f38(value=J.undefined, *_args):
        return J.lt(value, 50)
    def _f39(value=J.undefined, *_args):
        return J.lt(value, 30)
    zones = J.obj(("above70", J.get(J.get(zoneSample, "filter")(_f36), "length")), ("above50", J.get(J.get(zoneSample, "filter")(_f37), "length")), ("below50", J.get(J.get(zoneSample, "filter")(_f38), "length")), ("below30", J.get(J.get(zoneSample, "filter")(_f39), "length")))
    trendBias = ("WARMING UP" if J.seq(J.get(zoneSample, "length"), 0) else ("FULL BULL" if J.gt(J.get(zones, "above50"), J.mul(fullBiasRatio, J.get(zones, "below50"))) else ("FULL BEAR" if J.gt(J.get(zones, "below50"), J.mul(fullBiasRatio, J.get(zones, "above50"))) else ("BULL" if J.gt(J.get(zones, "above50"), J.mul(normalBiasRatio, J.get(zones, "below50"))) else ("BEAR" if J.gt(J.get(zones, "below50"), J.mul(normalBiasRatio, J.get(zones, "above50"))) else "BALANCED")))))
    biasColor = (bullColor if J.truthy(J.get(trendBias, "includes")("BULL")) else (bearColor if J.truthy(J.get(trendBias, "includes")("BEAR")) else muted))
    rising = (("RISING" if J.gt(J.get(mars, last), J.get(mars, J.sub(last, 1))) else ("FALLING" if J.lt(J.get(mars, last), J.get(mars, J.sub(last, 1))) else "FLAT")) if (J.truthy(finite(J.get(mars, last))) and J.truthy(finite(J.get(mars, J.sub(last, 1))))) else "WARMING UP")
    def cell(text=J.undefined, _p1=J.undefined, _p3=J.undefined, *_args):
        _t2 = _p1
        if _t2 is J.undefined:
            _t2 = "#E6EDF7"
        color_2 = _t2
        _t4 = _p3
        if _t4 is J.undefined:
            _t4 = J.obj()
        extra = _t4
        return J.obj(("text", text), ("color", color_2), ("padding", "5px 9px"), *J.obj_spread(extra))
    rows = J.JSArray([])
    if J.truthy(showDashboard):
        J.get(rows, "push")(J.obj(("cells", J.JSArray([cell("ZENALGO / MARS", "#E6EDF7", J.obj(("colspan", 4), ("fontSize", "12px"), ("fontWeight", "700"), ("letterSpacing", "3px"), ("padding", "12px 10px"), ("borderBottom", "1px solid #FFFFFF14")))]))))
        J.get(rows, "push")(J.obj(("cells", J.JSArray([cell(trendBias, biasColor, J.obj(("colspan", 2), ("fontSize", ("18px" if J.seq(dashboardSize, "Compact") else "24px")), ("fontWeight", "700"))), cell(rising, muted, J.obj(("colspan", 2), ("textAlign", "right"), ("fontSize", "10px")))]))))
        J.get(rows, "push")(J.obj(("cells", J.JSArray([cell("MARS", muted), cell(fmt(J.get(mars, last)), J.get(directionColors, last)), cell("SIGNAL", muted), cell(fmt(J.get(signal, last)), "#D8E2F0")]))))
        bullShare = (J.get(G_Math, "round")(J.mul(J.div(J.get(zones, "above50"), J.get(zoneSample, "length")), 100)) if J.truthy(J.get(zoneSample, "length")) else 0)
        J.get(rows, "push")(J.obj(("cells", J.JSArray([cell((J.template(bullShare, "% above 50 · ", J.get(zoneSample, "length"), " bars") if J.truthy(J.get(zoneSample, "length")) else "Waiting for history"), muted, J.obj(("colspan", 4), ("fontSize", "10px"), ("borderBottom", J.template("3px solid ", biasColor))))]))))
        if J.truthy(signature):
            J.get(rows, "push")(J.obj(("cells", J.JSArray([cell(">70", bearColor), cell(G_String(J.get(zones, "above70"))), cell("<30", bullColor), cell(G_String(J.get(zones, "below30")))]))))
    timeframeSpecs = J.JSArray([J.JSArray(["1", "1m"]), J.JSArray(["5", "5m"]), J.JSArray(["15", "15m"]), J.JSArray(["60", "1h"]), J.JSArray(["240", "4h"]), J.JSArray(["D", "1D"])])
    def _f40(_p1=J.undefined, *_args):
        _t2 = J.iter_of(_p1)
        resolution = (_t2[0] if 0 < len(_t2) else J.undefined)
        label = (_t2[1] if 1 < len(_t2) else J.undefined)
        try:
            chartType = (J.get(G_current, "chart_type") if J.truthy(J.get(J.JSArray(["heikinashi", "rainfall"]), "includes")(J.get(G_current, "chart_type"))) else "candles")
            data = (J.obj(("close", G_close)) if J.seq(G_String(J.get(G_current, "resolution")), resolution) else J.get(G_request, "history")(J.get(G_current, "ticker"), resolution, J.obj(("chart_type", chartType), ("ext_session", J.get(G_current, "is_ext_hours")))))
            if (((not J.truthy(data)) or J.truthy(J.get(data, "error"))) or (not J.truthy(J.get(G_Array, "isArray")(J.get(data, "close"))))):
                return J.obj(("label", label), ("error", True))
            values = wilderRsi(J.get(data, "close"), rsiLength)
            averages = averageSeries(values, rsiLength)
            index_6 = J.sub(J.get(J.get(data, "close"), "length"), 1)
            return J.obj(("label", label), ("rsi", J.get(values, index_6)), ("ma", J.get(averages, index_6)))
        except Exception as _e3:
            error = J.catch_value(_e3)
            return J.obj(("label", label), ("error", True))
    timeframeRows = (J.get(G_Promise, "all")(J.get(timeframeSpecs, "map")(_f40)) if (J.truthy(showDashboard) and J.truthy(showTimeframes)) else J.JSArray([]))
    if (J.truthy(showDashboard) and J.truthy(showTimeframes)):
        J.get(rows, "push")(J.obj(("cells", J.JSArray([cell("TF · LIVE", muted), cell("RSI", muted), cell("MA", muted), cell("TREND", muted)]))))
        for item in J.iter_of(timeframeRows):
            ready = (finite(J.get(item, "ma")) if J.truthy(_t41 := (finite(J.get(item, "rsi")) if J.truthy(_t42 := (not J.truthy(J.get(item, "error")))) else _t42)) else _t41)
            trend = (("RISING" if J.gt(J.get(item, "rsi"), J.get(item, "ma")) else ("FALLING" if J.lt(J.get(item, "rsi"), J.get(item, "ma")) else "FLAT")) if J.truthy(ready) else "N/A")
            color_2 = (bullColor if J.seq(trend, "RISING") else (bearColor if J.seq(trend, "FALLING") else muted))
            J.get(rows, "push")(J.obj(("cells", J.JSArray([cell(J.get(item, "label"), "#D8E2F0"), cell(fmt(J.get(item, "rsi"))), cell(fmt(J.get(item, "ma")), muted), cell(trend, color_2, J.obj(("fontSize", "10px")))]))))
    if J.truthy(showDashboard):
        vwapStatus = ("VWAP ACTIVE" if J.truthy(finite(J.get(dailyVwap, last))) else "VWAP N/A")
        J.get(rows, "push")(J.obj(("cells", J.JSArray([cell(J.template(J.get(preset, "toUpperCase")(), " · ", vwapStatus), muted, J.obj(("colspan", 4), ("fontSize", "9px"), ("paddingTop", "10px"), ("borderTop", "1px solid #FFFFFF14")))]))))
        J.get(rows, "push")(J.obj(("cells", J.JSArray([cell((J.template("R / H drawn ", pivotRight, " bars back after confirmation") if J.seq(divergenceHistory, "Pivot history") else J.template("R reversal · H continuation · confirmed +", pivotRight)), muted, J.obj(("colspan", 4), ("fontSize", "9px")))]))))
        if J.truthy(showSignalLegend):
            for _t43 in J.iter_of(J.JSArray([J.JSArray(["R · Regular divergence / potential reversal", muted]), J.JSArray(["H · Hidden divergence / potential continuation", muted]), J.JSArray(["MARS ↑ / ↓ · Cross 50 + momentum + VWAP", muted]), J.JSArray(["H ↑ / ↓ · Hidden divergence aligned with bias", muted]), J.JSArray(["◆ · Strong continuation condition", muted]), J.JSArray(["Amber ▲ / ▼ · Divergence opposing bias", warningColor])])):
                _t44 = J.iter_of(_t43)
                text = (_t44[0] if 0 < len(_t44) else J.undefined)
                color_3 = (_t44[1] if 1 < len(_t44) else J.undefined)
                J.get(rows, "push")(J.obj(("cells", J.JSArray([cell(text, color_3, J.obj(("colspan", 4), ("fontSize", "10px")))]))))
    for position in J.iter_of(J.JSArray(["top_right", "bottom_right", "top_left", "bottom_left"])):
        active = (J.seq(dashboardPosition, position) if J.truthy(_t45 := showDashboard) else _t45)
        G_paint_overlay(J.template("Mars dashboard ", position), J.obj(("position", position), ("parent", "chart"), ("order", "above_all")), (J.obj(("fontFamily", "Arial, sans-serif"), ("fontSize", ("11px" if J.seq(dashboardSize, "Compact") else "12px")), ("background", "linear-gradient(145deg, #111C2CF2, #101321F2)"), ("border", "1px solid #586B8A55"), ("borderRadius", "10px"), ("borderSpacing", "0"), ("boxShadow", "0 10px 32px #00000033"), ("overflow", "hidden"), ("rows", rows)) if J.truthy(active) else J.obj(("rows", J.JSArray([])))))


register_store_indicator(
    script,
    name='zenalgo_mars_TS',
    title='ZenAlgo · Mars',
    developer='ZenAlgo',
    url='https://trendspider.com/trading-tools-store/indicators/6aaa7d-zenalgo-%c2%b7-mars/',
    position='lower',
    inputs=[{'id': 'g-source__preset', 'title': 'Preset', 'type': 'select_wide', 'default': 'Traditional', 'options': ['Traditional', 'Fast', 'Custom']}, {'id': 'g-source__custom_rsi_length', 'title': 'Custom RSI length', 'type': 'number', 'default': 14}, {'id': 'g-source__custom_ma_length', 'title': 'Custom MA length', 'type': 'number', 'default': 14}, {'id': 'g-source__custom_signal_length', 'title': 'Custom signal length', 'type': 'number', 'default': 9}, {'id': 'g-divergences__pivot_left', 'title': 'Pivot left', 'type': 'number', 'default': 5}, {'id': 'g-divergences__pivot_right', 'title': 'Pivot right', 'type': 'number', 'default': 5}, {'id': 'g-divergences__minimum_pivot_range', 'title': 'Minimum pivot range', 'type': 'number', 'default': 5}, {'id': 'g-divergences__maximum_pivot_range', 'title': 'Maximum pivot range', 'type': 'number', 'default': 60}, {'id': 'g-divergences__divergence_placement', 'title': 'Divergence placement', 'type': 'select_wide', 'default': 'Confirmation', 'options': ['Confirmation', 'Pivot history']}, {'id': 'g-bias__signal_bias_smoothing', 'title': 'Signal bias smoothing', 'type': 'number', 'default': 1}, {'id': 'g-bias__zone_lookback', 'title': 'Zone lookback', 'type': 'number', 'default': 100}, {'id': 'g-bias__bias_ratio', 'title': 'Bias ratio', 'type': 'number', 'default': 1.2}, {'id': 'g-bias__full_bias_ratio', 'title': 'Full bias ratio', 'type': 'number', 'default': 1.8}, {'id': 'g-appearance__detail', 'title': 'Detail', 'type': 'select_wide', 'default': 'Signature', 'options': ['Minimal', 'Signature']}, {'id': 'g-appearance__bullish_color', 'title': 'Bullish color', 'type': 'color', 'default': '#3FC0DC'}, {'id': 'g-appearance__bearish_color', 'title': 'Bearish color', 'type': 'color', 'default': '#A477FF'}, {'id': 'g-appearance__confirmation_labels', 'title': 'Confirmation labels', 'type': 'boolean', 'default': True}, {'id': 'g-appearance__dashboard', 'title': 'Dashboard', 'type': 'boolean', 'default': False}, {'id': 'g-appearance__timeframe_matrix', 'title': 'Timeframe matrix', 'type': 'boolean', 'default': True}, {'id': 'g-appearance__signal_legend', 'title': 'Signal legend', 'type': 'boolean', 'default': False}, {'id': 'g-appearance__dashboard_position', 'title': 'Dashboard position', 'type': 'select_wide', 'default': 'bottom_left', 'options': ['top_right', 'bottom_right', 'top_left', 'bottom_left']}, {'id': 'g-appearance__dashboard_size', 'title': 'Dashboard size', 'type': 'select_wide', 'default': 'Compact', 'options': ['Compact', 'Comfortable']}],
    outputs=['scale_top', 'scale_bottom', 'upper_zone', 'lower_zone', 'equilibrium', 'momentum_histogram', 'mars_halo', 'mars', 'signal', 'line_15', 'line_16', 'line_18', 'line_19', 'bullish_divergence', 'bearish_divergence', 'bullish_crossover', 'bearish_crossover', 'strong_bull_marker', 'strong_bear_marker', 'bull_warning_marker', 'bear_warning_marker', 'bull_launch_marker', 'bear_launch_marker', 'bull_confirmation_anchor', 'bear_confirmation_anchor', 'mars_crossed_above_signal', 'mars_crossed_below_signal', 'regular_bullish_divergence_confirmed', 'hidden_bullish_divergence_confirmed', 'regular_bearish_divergence_confirmed', 'hidden_bearish_divergence_confirmed', 'strong_bull', 'strong_bear', 'bullish_warning', 'bearish_warning', 'bull_launch_with_session_vwap', 'bear_launch_with_session_vwap'],
    signals=['mars_crossed_above_signal', 'mars_crossed_below_signal', 'regular_bullish_divergence_confirmed', 'hidden_bullish_divergence_confirmed', 'regular_bearish_divergence_confirmed', 'hidden_bearish_divergence_confirmed', 'strong_bull', 'strong_bear', 'bullish_warning', 'bearish_warning', 'bull_launch_with_session_vwap', 'bear_launch_with_session_vwap'],
    requires=['history'],
    parity='exact',
)
