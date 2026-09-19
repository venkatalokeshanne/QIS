"""
ZenAlgo - ADX -- TrendSpider store indicator by ZenAlgo.

Registered as "zenalgo_adx_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6a2056-zenalgo-adx/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Infinity = G["Infinity"]
    G_Math = G["Math"]
    G_Number = G["Number"]
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_ema = G["ema"]
    G_fill = G["fill"]
    G_high = G["high"]
    G_horizontal_line = G["horizontal_line"]
    G_input = G["input"]
    G_low = G["low"]
    G_paint = G["paint"]
    G_paint_label_at_line = G["paint_label_at_line"]
    G_paint_overlay = G["paint_overlay"]
    G_parseInt = G["parseInt"]
    G_register_signal = G["register_signal"]
    G_series_of = G["series_of"]
    G_sma = G["sma"]
    def emptySeries(_p1=J.undefined, *_args):
        _t2 = _p1
        if _t2 is J.undefined:
            _t2 = None
        value = _t2
        return G_series_of(value)
    def nvl(value=J.undefined, _p1=J.undefined, *_args):
        _t2 = _p1
        if _t2 is J.undefined:
            _t2 = 0
        fallback = _t2
        return (fallback if ((J.nullish(value)) or J.truthy(J.get(G_Number, "isNaN")(value))) else value)
    def movingAverage(source=J.undefined, length=J.undefined, type_=J.undefined, *_args):
        return (G_ema(source, length) if J.seq(type_, "EMA") else G_sma(source, length))
    def crossover(a=J.undefined, b=J.undefined, index=J.undefined, *_args):
        return (J.le(J.get(a, J.sub(index, 1)), J.get(b, J.sub(index, 1))) if J.truthy(_t1 := (J.gt(J.get(a, index), J.get(b, index)) if J.truthy(_t2 := ((not J.nullish(J.get(b, J.sub(index, 1)))) if J.truthy(_t3 := ((not J.nullish(J.get(a, J.sub(index, 1)))) if J.truthy(_t4 := ((not J.nullish(J.get(b, index))) if J.truthy(_t5 := ((not J.nullish(J.get(a, index))) if J.truthy(_t6 := J.gt(index, 0)) else _t6)) else _t5)) else _t4)) else _t3)) else _t2)) else _t1)
    def crossunder(a=J.undefined, b=J.undefined, index=J.undefined, *_args):
        return (J.ge(J.get(a, J.sub(index, 1)), J.get(b, J.sub(index, 1))) if J.truthy(_t1 := (J.lt(J.get(a, index), J.get(b, index)) if J.truthy(_t2 := ((not J.nullish(J.get(b, J.sub(index, 1)))) if J.truthy(_t3 := ((not J.nullish(J.get(a, J.sub(index, 1)))) if J.truthy(_t4 := ((not J.nullish(J.get(b, index))) if J.truthy(_t5 := ((not J.nullish(J.get(a, index))) if J.truthy(_t6 := J.gt(index, 0)) else _t6)) else _t5)) else _t4)) else _t3)) else _t2)) else _t1)
    def crossoverValue(source=J.undefined, level=J.undefined, index=J.undefined, *_args):
        return (J.le(J.get(source, J.sub(index, 1)), level) if J.truthy(_t1 := (J.gt(J.get(source, index), level) if J.truthy(_t2 := ((not J.nullish(J.get(source, J.sub(index, 1)))) if J.truthy(_t3 := ((not J.nullish(J.get(source, index))) if J.truthy(_t4 := J.gt(index, 0)) else _t4)) else _t3)) else _t2)) else _t1)
    def crossunderValue(source=J.undefined, level=J.undefined, index=J.undefined, *_args):
        return (J.ge(J.get(source, J.sub(index, 1)), level) if J.truthy(_t1 := (J.lt(J.get(source, index), level) if J.truthy(_t2 := ((not J.nullish(J.get(source, J.sub(index, 1)))) if J.truthy(_t3 := ((not J.nullish(J.get(source, index))) if J.truthy(_t4 := J.gt(index, 0)) else _t4)) else _t3)) else _t2)) else _t1)
    def constantWhen(condition=J.undefined, value=J.undefined, *_args):
        def _f1(active=J.undefined, *_args):
            return (value if J.truthy(active) else None)
        return J.get(condition, "map")(_f1)
    def offsetMarker(condition=J.undefined, values=J.undefined, barsBack=J.undefined, *_args):
        result = emptySeries()
        i = 0
        while J.lt(i, J.get(G_close, "length")):
            if (not J.truthy(J.get(condition, i))):
                i = J.inc(i)
                continue
            targetIndex = J.sub(i, barsBack)
            if J.ge(targetIndex, 0):
                J.set(result, targetIndex, J.get(values, i))
            i = J.inc(i)
        return result
    def offsetSeries(values=J.undefined, barsBack=J.undefined, *_args):
        result = emptySeries()
        i = 0
        while J.lt(i, J.get(G_close, "length")):
            if (J.nullish(J.get(values, i))):
                i = J.inc(i)
                continue
            targetIndex = J.sub(i, barsBack)
            if J.ge(targetIndex, 0):
                J.set(result, targetIndex, J.get(values, i))
            i = J.inc(i)
        return result
    def valueWhenLatestSeries(condition=J.undefined, values=J.undefined, *_args):
        result = emptySeries()
        latest = None
        i = 0
        while J.lt(i, J.get(G_close, "length")):
            if J.truthy(J.get(condition, i)):
                latest = J.get(values, i)
            J.set(result, i, latest)
            i = J.inc(i)
        return result
    def minMaxOfSeries(seriesList=J.undefined, *_args):
        minValue = G_Infinity
        maxValue = J.neg(G_Infinity)
        for source in J.iter_of(seriesList):
            i = 0
            while J.lt(i, J.get(source, "length")):
                value = J.get(source, i)
                if ((J.nullish(value)) or J.truthy(J.get(G_Number, "isNaN")(value))):
                    i = J.inc(i)
                    continue
                minValue = J.get(G_Math, "min")(minValue, value)
                maxValue = J.get(G_Math, "max")(maxValue, value)
                i = J.inc(i)
        if (J.seq(minValue, G_Infinity) or J.seq(maxValue, J.neg(G_Infinity))):
            return J.obj(("minValue", 0), ("maxValue", 100))
        return J.obj(("minValue", minValue), ("maxValue", maxValue))
    def addLineSegment(target=J.undefined, startIndex=J.undefined, startValue=J.undefined, endIndex=J.undefined, endValue=J.undefined, *_args):
        if (((((J.nullish(startIndex)) or (J.nullish(endIndex))) or (J.nullish(startValue))) or (J.nullish(endValue))) or J.le(endIndex, startIndex)):
            return J.undefined
        length = J.sub(endIndex, startIndex)
        i = startIndex
        while J.le(i, endIndex):
            progress = J.div(J.sub(i, startIndex), length)
            J.set(target, i, J.add(startValue, J.mul(J.sub(endValue, startValue), progress)))
            i = J.inc(i)
    def colorWithAlpha(hex=J.undefined, alpha=J.undefined, *_args):
        clean = J.get(hex, "replace")("#", "")
        r = G_parseInt(J.get(clean, "slice")(0, 2), 16)
        g = G_parseInt(J.get(clean, "slice")(2, 4), 16)
        b = G_parseInt(J.get(clean, "slice")(4, 6), 16)
        return J.template("rgba(", r, ",", g, ",", b, ",", alpha, ")")
    def adxBullColor(value=J.undefined, *_args):
        if J.le(value, 20):
            return colorWithAlpha(zenColorBullish, 0.2)
        if J.le(value, 40):
            return colorWithAlpha(zenColorBullish, 0.4)
        if J.le(value, 60):
            return colorWithAlpha(zenColorBullish, 0.6)
        if J.le(value, 80):
            return colorWithAlpha(zenColorBullish, 0.8)
        return zenColorBullish
    def adxBearColor(value=J.undefined, *_args):
        if J.le(value, 20):
            return colorWithAlpha(zenColorBearish, 0.2)
        if J.le(value, 40):
            return colorWithAlpha(zenColorBearish, 0.4)
        if J.le(value, 60):
            return colorWithAlpha(zenColorBearish, 0.6)
        if J.le(value, 80):
            return colorWithAlpha(zenColorBearish, 0.8)
        return zenColorBearish
    def diBullColor(value=J.undefined, *_args):
        if J.le(value, 20):
            return colorWithAlpha(zenColorBullish, 0.2)
        if J.le(value, 30):
            return colorWithAlpha(zenColorBullish, 0.4)
        if J.le(value, 40):
            return colorWithAlpha(zenColorBullish, 0.6)
        if J.le(value, 50):
            return colorWithAlpha(zenColorBullish, 0.8)
        return zenColorBullish
    def diBearColor(value=J.undefined, *_args):
        if J.le(value, 20):
            return colorWithAlpha(zenColorBearish, 0.2)
        if J.le(value, 30):
            return colorWithAlpha(zenColorBearish, 0.4)
        if J.le(value, 40):
            return colorWithAlpha(zenColorBearish, 0.6)
        if J.le(value, 50):
            return colorWithAlpha(zenColorBearish, 0.8)
        return zenColorBearish
    def topFractal(source=J.undefined, index=J.undefined, *_args):
        return (J.gt(J.get(source, J.sub(index, 2)), J.get(source, index)) if J.truthy(_t1 := (J.gt(J.get(source, J.sub(index, 2)), J.get(source, J.sub(index, 1))) if J.truthy(_t2 := (J.lt(J.get(source, J.sub(index, 3)), J.get(source, J.sub(index, 2))) if J.truthy(_t3 := (J.lt(J.get(source, J.sub(index, 4)), J.get(source, J.sub(index, 2))) if J.truthy(_t4 := J.ge(index, 4)) else _t4)) else _t3)) else _t2)) else _t1)
    def bottomFractal(source=J.undefined, index=J.undefined, *_args):
        return (J.lt(J.get(source, J.sub(index, 2)), J.get(source, index)) if J.truthy(_t1 := (J.lt(J.get(source, J.sub(index, 2)), J.get(source, J.sub(index, 1))) if J.truthy(_t2 := (J.gt(J.get(source, J.sub(index, 3)), J.get(source, J.sub(index, 2))) if J.truthy(_t3 := (J.gt(J.get(source, J.sub(index, 4)), J.get(source, J.sub(index, 2))) if J.truthy(_t4 := J.ge(index, 4)) else _t4)) else _t3)) else _t2)) else _t1)
    def strengthText(value=J.undefined, *_args):
        if J.le(value, 20):
            return "Weak"
        if J.le(value, 40):
            return "Moderate"
        if J.le(value, 60):
            return "Strong"
        if J.le(value, 80):
            return "Very Strong"
        return "Extreme"
    def diStrengthText(value=J.undefined, *_args):
        distance = J.get(G_Math, "abs")(J.sub(value, threshold))
        if J.le(distance, 5):
            return "Weak"
        if J.le(distance, 15):
            return "Moderate"
        return "Strong"
    def trendText(series=J.undefined, index=J.undefined, *_args):
        if ((J.le(index, 0) or (J.nullish(J.get(series, index)))) or (J.nullish(J.get(series, J.sub(index, 1))))):
            return "Neutral"
        if J.gt(J.get(series, index), J.get(series, J.sub(index, 1))):
            return "Rising"
        if J.lt(J.get(series, index), J.get(series, J.sub(index, 1))):
            return "Falling"
        return "Neutral"
    def powerDynamicsText(index=J.undefined, *_args):
        adxNow = J.get(adxValue, index)
        if ((((J.le(index, 0) or (J.nullish(adxNow))) or (J.nullish(J.get(diPlus, index)))) or (J.nullish(J.get(diMinus, index)))) or (J.nullish(J.get(diValue, index)))):
            return "Neutral"
        adxRising = J.gt(adxNow, J.get(adxValue, J.sub(index, 1)))
        adxFalling = J.lt(adxNow, J.get(adxValue, J.sub(index, 1)))
        plusRising = J.gt(J.get(diPlus, index), J.get(diPlus, J.sub(index, 1)))
        minusRising = J.gt(J.get(diMinus, index), J.get(diMinus, J.sub(index, 1)))
        power = strengthText(adxNow)
        if ((J.truthy(adxFalling) and J.truthy(minusRising)) and J.le(J.get(diValue, index), threshold)):
            return J.template(power, " Bears are losing power")
        if ((J.truthy(adxRising) and J.truthy(minusRising)) and J.le(J.get(diValue, index), threshold)):
            return J.template(power, " Bears are gaining power")
        if ((J.truthy(adxFalling) and J.truthy(plusRising)) and J.gt(J.get(diValue, index), threshold)):
            return J.template(power, " Bulls are losing power")
        if ((J.truthy(adxRising) and J.truthy(plusRising)) and J.gt(J.get(diValue, index), threshold)):
            return J.template(power, " Bulls are gaining power")
        return "Neutral"
    G_describe_indicator("ZenAlgo - ADX", "lower", J.obj(("shortName", "ZenAlgo - ADX"), ("warmup", 500), ("mainColorInheritFrom", "ADX")))
    zenColorBullish = "#3FC0DC"
    zenColorBearish = "#7D0757"
    zenColorNeutral = "#25073B"
    zenColorBullishSoft = "#84DFF1"
    zenColorBearishSoft = "#B84794"
    zenColorSignal = "#72074f"
    len = J.get(G_input, "number")("Length", 7, J.obj(("min", 1)))
    threshold = J.get(G_input, "number")("Threshold", 25, J.obj(("min", 1)))
    adxSignalLength = J.get(G_input, "number")("ADX Signal Len", 3, J.obj(("min", 1)))
    adxSignalType = J.get(G_input, "select")("ADX Signal MA", "SMA", J.JSArray(["SMA", "EMA"]))
    enableDivergences = J.get(G_input, "boolean")("Enable Divergences", True)
    showLabels = J.get(G_input, "boolean")("Show Div Labels", True)
    plotOffset = J.get(G_input, "number")("Div Label Offset", 0.5, J.obj(("min", 0)))
    showTable = J.get(G_input, "boolean")("Show Table", True)
    tableSize = J.get(G_input, "select")("Table Size", "Small", J.JSArray(["Small", "Normal", "Large"]))
    tablePosition = J.get(G_input, "select")("Table Position", "Top-Right", J.JSArray(["Top-Left", "Top-Right", "Bottom-Left", "Bottom-Right"]))
    trueRange = emptySeries()
    directionalMovementPlus = emptySeries()
    directionalMovementMinus = emptySeries()
    i = 0
    while J.lt(i, J.get(G_close, "length")):
        prevClose = (J.get(G_close, J.sub(i, 1)) if J.gt(i, 0) else 0)
        prevHigh = (J.get(G_high, J.sub(i, 1)) if J.gt(i, 0) else 0)
        prevLow = (J.get(G_low, J.sub(i, 1)) if J.gt(i, 0) else 0)
        J.set(trueRange, i, J.get(G_Math, "max")(J.sub(J.get(G_high, i), J.get(G_low, i)), J.get(G_Math, "abs")(J.sub(J.get(G_high, i), prevClose)), J.get(G_Math, "abs")(J.sub(J.get(G_low, i), prevClose))))
        J.set(directionalMovementPlus, i, (J.get(G_Math, "max")(J.sub(J.get(G_high, i), prevHigh), 0) if J.gt(J.sub(J.get(G_high, i), prevHigh), J.sub(prevLow, J.get(G_low, i))) else 0))
        J.set(directionalMovementMinus, i, (J.get(G_Math, "max")(J.sub(prevLow, J.get(G_low, i)), 0) if J.gt(J.sub(prevLow, J.get(G_low, i)), J.sub(J.get(G_high, i), prevHigh)) else 0))
        i = J.inc(i)
    smoothedTrueRange = emptySeries()
    smoothedDirectionalMovementPlus = emptySeries()
    smoothedDirectionalMovementMinus = emptySeries()
    i_2 = 0
    while J.lt(i_2, J.get(G_close, "length")):
        J.set(smoothedTrueRange, i_2, J.add(J.sub(nvl(J.get(smoothedTrueRange, J.sub(i_2, 1))), J.div(nvl(J.get(smoothedTrueRange, J.sub(i_2, 1))), len)), J.get(trueRange, i_2)))
        J.set(smoothedDirectionalMovementPlus, i_2, J.add(J.sub(nvl(J.get(smoothedDirectionalMovementPlus, J.sub(i_2, 1))), J.div(nvl(J.get(smoothedDirectionalMovementPlus, J.sub(i_2, 1))), len)), J.get(directionalMovementPlus, i_2)))
        J.set(smoothedDirectionalMovementMinus, i_2, J.add(J.sub(nvl(J.get(smoothedDirectionalMovementMinus, J.sub(i_2, 1))), J.div(nvl(J.get(smoothedDirectionalMovementMinus, J.sub(i_2, 1))), len)), J.get(directionalMovementMinus, i_2)))
        i_2 = J.inc(i_2)
    def _f1(value=J.undefined, i_3=J.undefined, *_args):
        return (J.mul(J.div(value, J.get(smoothedTrueRange, i_3)), 100) if J.sne(J.get(smoothedTrueRange, i_3), 0) else None)
    diPlus = J.get(smoothedDirectionalMovementPlus, "map")(_f1)
    def _f2(value=J.undefined, i_3=J.undefined, *_args):
        return (J.mul(J.div(value, J.get(smoothedTrueRange, i_3)), 100) if J.sne(J.get(smoothedTrueRange, i_3), 0) else None)
    diMinus = J.get(smoothedDirectionalMovementMinus, "map")(_f2)
    def _f3(value=J.undefined, i_3=J.undefined, *_args):
        return (J.mul(J.div(J.get(G_Math, "abs")(J.sub(value, J.get(diMinus, i_3))), J.add(value, J.get(diMinus, i_3))), 100) if (((not J.nullish(value)) and (not J.nullish(J.get(diMinus, i_3)))) and J.sne(J.add(value, J.get(diMinus, i_3)), 0)) else None)
    dx = J.get(diPlus, "map")(_f3)
    adxValue = G_sma(dx, len)
    def _f4(value=J.undefined, i_3=J.undefined, *_args):
        return (J.add(25, J.sub(value, J.get(diMinus, i_3))) if ((not J.nullish(value)) and (not J.nullish(J.get(diMinus, i_3)))) else None)
    diValue = J.get(diPlus, "map")(_f4)
    adxSignalMA = movingAverage(adxValue, adxSignalLength, adxSignalType)
    def _f5(value=J.undefined, i_3=J.undefined, *_args):
        return crossover(adxValue, adxSignalMA, i_3)
    adxBullishCross = J.get(adxValue, "map")(_f5)
    def _f6(value=J.undefined, i_3=J.undefined, *_args):
        return crossunder(adxValue, adxSignalMA, i_3)
    adxBearishCross = J.get(adxValue, "map")(_f6)
    def _f7(value=J.undefined, i_3=J.undefined, *_args):
        return (J.gt(value, 25) if J.truthy(_t1 := crossoverValue(diValue, 25, i_3)) else _t1)
    bullishDiCrossAbove = J.get(diValue, "map")(_f7)
    def _f8(value=J.undefined, i_3=J.undefined, *_args):
        return (J.lt(value, 25) if J.truthy(_t1 := crossunderValue(diValue, 25, i_3)) else _t1)
    bearishDiCrossBelow = J.get(diValue, "map")(_f8)
    def _f9(value=J.undefined, i_3=J.undefined, *_args):
        return (J.gt(J.get(adxValue, i_3), J.get(adxValue, J.sub(i_3, 1))) if J.truthy(_t1 := (J.gt(value, J.get(diPlus, J.sub(i_3, 1))) if J.truthy(_t2 := (J.gt(J.get(adxValue, i_3), threshold) if J.truthy(_t3 := (J.gt(value, J.get(diMinus, i_3)) if J.truthy(_t4 := crossover(diPlus, diMinus, i_3)) else _t4)) else _t3)) else _t2)) else _t1)
    bullishSignal = J.get(diPlus, "map")(_f9)
    def _f10(value=J.undefined, i_3=J.undefined, *_args):
        return (J.gt(J.get(adxValue, i_3), J.get(adxValue, J.sub(i_3, 1))) if J.truthy(_t1 := (J.gt(value, J.get(diMinus, J.sub(i_3, 1))) if J.truthy(_t2 := (J.gt(J.get(adxValue, i_3), threshold) if J.truthy(_t3 := (J.gt(value, J.get(diPlus, i_3)) if J.truthy(_t4 := crossover(diMinus, diPlus, i_3)) else _t4)) else _t3)) else _t2)) else _t1)
    bearishSignal = J.get(diMinus, "map")(_f10)
    def _f11(value=J.undefined, i_3=J.undefined, *_args):
        return (adxBullColor((_t1 if J.truthy(_t1 := value) else 0)) if J.ge(J.get(diValue, i_3), 25) else adxBearColor((_t2 if J.truthy(_t2 := value) else 0)))
    adxLineColor = J.get(adxValue, "map")(_f11)
    def _f12(value=J.undefined, i_3=J.undefined, *_args):
        return (diBullColor((_t1 if J.truthy(_t1 := value) else 0)) if J.gt(J.get(diValue, i_3), threshold) else diBearColor((_t2 if J.truthy(_t2 := value) else 0)))
    diLineColor = J.get(adxValue, "map")(_f12)
    def _f13(value=J.undefined, *_args):
        return (None if (J.nullish(value)) else J.obj(("high", J.get(G_Math, "max")(value, threshold)), ("low", J.get(G_Math, "min")(value, threshold))))
    diHistogramRange = J.get(diValue, "map")(_f13)
    indicatorRange = minMaxOfSeries(J.JSArray([diValue, adxValue, adxSignalMA]))
    markerPadding = J.get(G_Math, "max")(2, J.mul(J.sub(J.get(indicatorRange, "maxValue"), J.get(indicatorRange, "minValue")), 0.04))
    bottomMarker = J.sub(J.get(indicatorRange, "minValue"), markerPadding)
    topMarker = J.add(J.get(indicatorRange, "maxValue"), markerPadding)
    G_paint(diHistogramRange, J.obj(("name", "DI Histogram"), ("style", "columnrange"), ("color", diLineColor), ("thickness", 8)))
    G_paint(diValue, J.obj(("name", "DI Line"), ("style", "line"), ("color", diLineColor), ("thickness", 2)))
    adxPaint = G_paint(adxValue, J.obj(("name", "ADX"), ("style", "line"), ("color", adxLineColor), ("thickness", 3)))
    G_paint(adxSignalMA, J.obj(("name", "ADX Signal MA"), ("style", "line"), ("color", zenColorSignal), ("thickness", 2)))
    G_paint(G_horizontal_line(threshold), J.obj(("name", "Threshold"), ("style", "line"), ("color", "rgba(255,255,255,0.35)"), ("thickness", 1)))
    G_paint(G_horizontal_line(70), J.obj(("name", "70"), ("style", "line"), ("color", "rgba(255,255,255,0.16)"), ("thickness", 1)))
    G_paint(G_horizontal_line(80), J.obj(("name", "80"), ("style", "line"), ("color", "rgba(255,255,255,0.16)"), ("thickness", 1)))
    G_paint(G_horizontal_line(90), J.obj(("name", "90"), ("style", "line"), ("color", "rgba(255,255,255,0.16)"), ("thickness", 1)))
    G_paint(G_horizontal_line(100), J.obj(("name", "100"), ("style", "line"), ("color", "rgba(255,255,255,0.16)"), ("thickness", 1)))
    fill70 = G_paint(G_horizontal_line(70), J.obj(("name", "Fill 70 Base"), ("hidden", True), ("style", "line"), ("color", "#3A0D32")))
    fill80 = G_paint(G_horizontal_line(80), J.obj(("name", "Fill 80 Base"), ("hidden", True), ("style", "line"), ("color", "#5A144C")))
    fill90 = G_paint(G_horizontal_line(90), J.obj(("name", "Fill 90 Base"), ("hidden", True), ("style", "line"), ("color", "#7D1B69")))
    fill100 = G_paint(G_horizontal_line(100), J.obj(("name", "Fill 100 Base"), ("hidden", True), ("style", "line"), ("color", "#7D1B69")))
    G_fill(fill70, fill80, "#3A0D32")
    G_fill(fill80, fill90, "#5A144C")
    G_fill(fill90, fill100, "#7D1B69")
    def _f14(value=J.undefined, i_3=J.undefined, *_args):
        return (adxBearColor((_t1 if J.truthy(_t1 := value) else 0)) if J.le(J.get(diValue, i_3), 25) else adxBullColor((_t2 if J.truthy(_t2 := value) else 0)))
    G_paint(offsetMarker(adxBullishCross, adxValue, 1), J.obj(("name", "ADX Bullish Cross"), ("style", "dotted"), ("color", J.get(adxValue, "map")(_f14)), ("thickness", 4)))
    def _f15(value=J.undefined, i_3=J.undefined, *_args):
        return (adxBearColor((_t1 if J.truthy(_t1 := value) else 0)) if J.ge(J.get(diValue, i_3), 25) else adxBullColor((_t2 if J.truthy(_t2 := value) else 0)))
    G_paint(offsetMarker(adxBearishCross, adxValue, 1), J.obj(("name", "ADX Bearish Cross"), ("style", "dotted"), ("color", J.get(adxValue, "map")(_f15)), ("thickness", 4)))
    def _f16(value=J.undefined, *_args):
        return adxBullColor((_t1 if J.truthy(_t1 := value) else 0))
    G_paint(constantWhen(bullishDiCrossAbove, bottomMarker), J.obj(("name", "DI Cross Above 25"), ("style", "dotted"), ("color", J.get(adxValue, "map")(_f16)), ("thickness", 6)))
    def _f17(value=J.undefined, *_args):
        return adxBearColor((_t1 if J.truthy(_t1 := value) else 0))
    G_paint(constantWhen(bearishDiCrossBelow, topMarker), J.obj(("name", "DI Cross Below 25"), ("style", "dotted"), ("color", J.get(adxValue, "map")(_f17)), ("thickness", 6)))
    def _f18(value=J.undefined, i_3=J.undefined, *_args):
        return topFractal(diValue, i_3)
    isFractalTopDI = J.get(diValue, "map")(_f18)
    def _f19(value=J.undefined, i_3=J.undefined, *_args):
        return bottomFractal(diValue, i_3)
    isFractalBotDI = J.get(diValue, "map")(_f19)
    regularBearishDivDI = emptySeries(False)
    hiddenBearishDivDI = emptySeries(False)
    regularBullishDivDI = emptySeries(False)
    hiddenBullishDivDI = emptySeries(False)
    regularBearLine = emptySeries()
    hiddenBearLine = emptySeries()
    regularBullLine = emptySeries()
    hiddenBullLine = emptySeries()
    regularBearLabelAnchor = emptySeries()
    hiddenBearLabelAnchor = emptySeries()
    regularBullLabelAnchor = emptySeries()
    hiddenBullLabelAnchor = emptySeries()
    previousTopIndex = None
    previousTopDI = None
    previousTopHigh = None
    previousBottomIndex = None
    previousBottomDI = None
    previousBottomLow = None
    i_3 = 4
    while J.lt(i_3, J.get(G_close, "length")):
        if J.truthy(J.get(isFractalTopDI, i_3)):
            pivotIndex = J.sub(i_3, 2)
            pivotDI = J.get(diValue, pivotIndex)
            pivotHigh = J.get(G_high, pivotIndex)
            regularBearish = (J.lt(pivotDI, previousTopDI) if J.truthy(_t20 := (J.gt(pivotHigh, previousTopHigh) if J.truthy(_t21 := ((not J.nullish(previousTopHigh)) if J.truthy(_t22 := ((not J.nullish(previousTopDI)) if J.truthy(_t23 := enableDivergences) else _t23)) else _t22)) else _t21)) else _t20)
            hiddenBearish = (J.gt(pivotDI, previousTopDI) if J.truthy(_t24 := (J.lt(pivotHigh, previousTopHigh) if J.truthy(_t25 := ((not J.nullish(previousTopHigh)) if J.truthy(_t26 := ((not J.nullish(previousTopDI)) if J.truthy(_t27 := enableDivergences) else _t27)) else _t26)) else _t25)) else _t24)
            J.set(regularBearishDivDI, pivotIndex, regularBearish)
            J.set(hiddenBearishDivDI, pivotIndex, hiddenBearish)
            if J.truthy(regularBearish):
                addLineSegment(regularBearLine, previousTopIndex, previousTopDI, pivotIndex, pivotDI)
                if (not J.nullish(J.get(diValue, J.sub(i_3, 1)))):
                    J.set(regularBearLabelAnchor, pivotIndex, J.add(J.get(diValue, J.sub(i_3, 1)), plotOffset))
            if J.truthy(hiddenBearish):
                addLineSegment(hiddenBearLine, previousTopIndex, previousTopDI, pivotIndex, pivotDI)
                if (not J.nullish(J.get(diValue, J.sub(i_3, 1)))):
                    J.set(hiddenBearLabelAnchor, pivotIndex, J.add(J.get(diValue, J.sub(i_3, 1)), plotOffset))
            previousTopIndex = pivotIndex
            previousTopDI = pivotDI
            previousTopHigh = pivotHigh
        if J.truthy(J.get(isFractalBotDI, i_3)):
            pivotIndex_2 = J.sub(i_3, 2)
            pivotDI_2 = J.get(diValue, pivotIndex_2)
            pivotLow = J.get(G_low, pivotIndex_2)
            regularBullish = (J.gt(pivotDI_2, previousBottomDI) if J.truthy(_t28 := (J.lt(pivotLow, previousBottomLow) if J.truthy(_t29 := ((not J.nullish(previousBottomLow)) if J.truthy(_t30 := ((not J.nullish(previousBottomDI)) if J.truthy(_t31 := enableDivergences) else _t31)) else _t30)) else _t29)) else _t28)
            hiddenBullish = (J.lt(pivotDI_2, previousBottomDI) if J.truthy(_t32 := (J.gt(pivotLow, previousBottomLow) if J.truthy(_t33 := ((not J.nullish(previousBottomLow)) if J.truthy(_t34 := ((not J.nullish(previousBottomDI)) if J.truthy(_t35 := enableDivergences) else _t35)) else _t34)) else _t33)) else _t32)
            J.set(regularBullishDivDI, pivotIndex_2, regularBullish)
            J.set(hiddenBullishDivDI, pivotIndex_2, hiddenBullish)
            if J.truthy(regularBullish):
                addLineSegment(regularBullLine, previousBottomIndex, previousBottomDI, pivotIndex_2, pivotDI_2)
                if (not J.nullish(J.get(diValue, J.sub(i_3, 1)))):
                    J.set(regularBullLabelAnchor, pivotIndex_2, J.sub(J.get(diValue, J.sub(i_3, 1)), plotOffset))
            if J.truthy(hiddenBullish):
                addLineSegment(hiddenBullLine, previousBottomIndex, previousBottomDI, pivotIndex_2, pivotDI_2)
                if (not J.nullish(J.get(diValue, J.sub(i_3, 1)))):
                    J.set(hiddenBullLabelAnchor, pivotIndex_2, J.sub(J.get(diValue, J.sub(i_3, 1)), plotOffset))
            previousBottomIndex = pivotIndex_2
            previousBottomDI = pivotDI_2
            previousBottomLow = pivotLow
        i_3 = J.inc(i_3)
    regularBearDivPaint = G_paint(regularBearLine, J.obj(("name", "Regular Bearish Divergences DI"), ("style", "line"), ("color", zenColorBearish), ("thickness", 2)))
    hiddenBearDivPaint = G_paint(hiddenBearLine, J.obj(("name", "Hidden Bearish Divergences DI"), ("style", "line"), ("color", zenColorBearishSoft), ("thickness", 2)))
    regularBullDivPaint = G_paint(regularBullLine, J.obj(("name", "Regular Bullish Divergences DI"), ("style", "line"), ("color", zenColorBullish), ("thickness", 2)))
    hiddenBullDivPaint = G_paint(hiddenBullLine, J.obj(("name", "Hidden Bullish Divergences DI"), ("style", "line"), ("color", zenColorBullishSoft), ("thickness", 2)))
    regularBearLabelPaint = G_paint(regularBearLabelAnchor, J.obj(("name", "Regular Bear Div Label Anchor"), ("style", "dotted"), ("color", "rgba(0,0,0,0)"), ("thickness", 1), ("hideInLegend", True)))
    hiddenBearLabelPaint = G_paint(hiddenBearLabelAnchor, J.obj(("name", "Hidden Bear Div Label Anchor"), ("style", "dotted"), ("color", "rgba(0,0,0,0)"), ("thickness", 1), ("hideInLegend", True)))
    regularBullLabelPaint = G_paint(regularBullLabelAnchor, J.obj(("name", "Regular Bull Div Label Anchor"), ("style", "dotted"), ("color", "rgba(0,0,0,0)"), ("thickness", 1), ("hideInLegend", True)))
    hiddenBullLabelPaint = G_paint(hiddenBullLabelAnchor, J.obj(("name", "Hidden Bull Div Label Anchor"), ("style", "dotted"), ("color", "rgba(0,0,0,0)"), ("thickness", 1), ("hideInLegend", True)))
    i_4 = 0
    while J.lt(i_4, J.get(G_close, "length")):
        if (J.truthy(showLabels) and (not J.nullish(J.get(regularBearLabelAnchor, i_4)))):
            G_paint_label_at_line(regularBearLabelPaint, i_4, "R", J.obj(("color", "white"), ("background_color", zenColorBearish), ("vertical_align", "top")))
        if (J.truthy(showLabels) and (not J.nullish(J.get(hiddenBearLabelAnchor, i_4)))):
            G_paint_label_at_line(hiddenBearLabelPaint, i_4, "H", J.obj(("color", "white"), ("background_color", zenColorBearishSoft), ("vertical_align", "top")))
        if (J.truthy(showLabels) and (not J.nullish(J.get(regularBullLabelAnchor, i_4)))):
            G_paint_label_at_line(regularBullLabelPaint, i_4, "R", J.obj(("color", "black"), ("background_color", zenColorBullish), ("vertical_align", "bottom")))
        if (J.truthy(showLabels) and (not J.nullish(J.get(hiddenBullLabelAnchor, i_4)))):
            G_paint_label_at_line(hiddenBullLabelPaint, i_4, "H", J.obj(("color", "black"), ("background_color", zenColorBullishSoft), ("vertical_align", "bottom")))
        i_4 = J.inc(i_4)
    def _f36(value=J.undefined, i_5=J.undefined, *_args):
        return (J.gt(J.get(diValue, i_5), 25) if J.truthy(_t1 := (J.gt(J.get(diPlus, i_5), J.get(diPlus, J.sub(i_5, 1))) if J.truthy(_t2 := (J.gt(value, J.get(adxValue, J.sub(i_5, 1))) if J.truthy(_t3 := J.gt(i_5, 0)) else _t3)) else _t2)) else _t1)
    bullishAdxDiPlus = J.get(adxValue, "map")(_f36)
    def _f37(value=J.undefined, i_5=J.undefined, *_args):
        return (J.lt(J.get(diValue, i_5), 25) if J.truthy(_t1 := (J.gt(J.get(diMinus, i_5), J.get(diMinus, J.sub(i_5, 1))) if J.truthy(_t2 := (J.gt(value, J.get(adxValue, J.sub(i_5, 1))) if J.truthy(_t3 := J.gt(i_5, 0)) else _t3)) else _t2)) else _t1)
    bearishAdxDiMinus = J.get(adxValue, "map")(_f37)
    def _f38(value=J.undefined, i_5=J.undefined, *_args):
        return (bottomMarker if (J.truthy(value) and J.le(J.get(adxValue, i_5), 20)) else None)
    G_paint(J.get(bullishAdxDiPlus, "map")(_f38), J.obj(("name", "Rising Bull DI Weak"), ("style", "dotted"), ("color", adxLineColor), ("thickness", 3)))
    def _f39(value=J.undefined, i_5=J.undefined, *_args):
        return (bottomMarker if ((J.truthy(value) and J.gt(J.get(adxValue, i_5), 20)) and J.le(J.get(adxValue, i_5), 40)) else None)
    G_paint(J.get(bullishAdxDiPlus, "map")(_f39), J.obj(("name", "Rising Bull DI Moderate"), ("style", "dotted"), ("color", adxLineColor), ("thickness", 3)))
    def _f40(value=J.undefined, i_5=J.undefined, *_args):
        return (bottomMarker if ((J.truthy(value) and J.gt(J.get(adxValue, i_5), 40)) and J.le(J.get(adxValue, i_5), 60)) else None)
    G_paint(J.get(bullishAdxDiPlus, "map")(_f40), J.obj(("name", "Rising Bull DI Strong"), ("style", "dotted"), ("color", adxLineColor), ("thickness", 5)))
    def _f41(value=J.undefined, i_5=J.undefined, *_args):
        return (bottomMarker if ((J.truthy(value) and J.gt(J.get(adxValue, i_5), 60)) and J.le(J.get(adxValue, i_5), 80)) else None)
    G_paint(J.get(bullishAdxDiPlus, "map")(_f41), J.obj(("name", "Rising Bull DI Very Strong"), ("style", "dotted"), ("color", adxLineColor), ("thickness", 7)))
    def _f42(value=J.undefined, i_5=J.undefined, *_args):
        return (bottomMarker if (J.truthy(value) and J.gt(J.get(adxValue, i_5), 80)) else None)
    G_paint(J.get(bullishAdxDiPlus, "map")(_f42), J.obj(("name", "Rising Bull DI Extreme"), ("style", "dotted"), ("color", adxLineColor), ("thickness", 9)))
    def _f43(value=J.undefined, i_5=J.undefined, *_args):
        return (topMarker if (J.truthy(value) and J.le(J.get(adxValue, i_5), 20)) else None)
    G_paint(J.get(bearishAdxDiMinus, "map")(_f43), J.obj(("name", "Rising Bear DI Weak"), ("style", "dotted"), ("color", adxLineColor), ("thickness", 3)))
    def _f44(value=J.undefined, i_5=J.undefined, *_args):
        return (topMarker if ((J.truthy(value) and J.gt(J.get(adxValue, i_5), 20)) and J.le(J.get(adxValue, i_5), 40)) else None)
    G_paint(J.get(bearishAdxDiMinus, "map")(_f44), J.obj(("name", "Rising Bear DI Moderate"), ("style", "dotted"), ("color", adxLineColor), ("thickness", 3)))
    def _f45(value=J.undefined, i_5=J.undefined, *_args):
        return (topMarker if ((J.truthy(value) and J.gt(J.get(adxValue, i_5), 40)) and J.le(J.get(adxValue, i_5), 60)) else None)
    G_paint(J.get(bearishAdxDiMinus, "map")(_f45), J.obj(("name", "Rising Bear DI Strong"), ("style", "dotted"), ("color", adxLineColor), ("thickness", 5)))
    def _f46(value=J.undefined, i_5=J.undefined, *_args):
        return (topMarker if ((J.truthy(value) and J.gt(J.get(adxValue, i_5), 60)) and J.le(J.get(adxValue, i_5), 80)) else None)
    G_paint(J.get(bearishAdxDiMinus, "map")(_f46), J.obj(("name", "Rising Bear DI Very Strong"), ("style", "dotted"), ("color", adxLineColor), ("thickness", 7)))
    def _f47(value=J.undefined, i_5=J.undefined, *_args):
        return (topMarker if (J.truthy(value) and J.gt(J.get(adxValue, i_5), 80)) else None)
    G_paint(J.get(bearishAdxDiMinus, "map")(_f47), J.obj(("name", "Rising Bear DI Extreme"), ("style", "dotted"), ("color", adxLineColor), ("thickness", 9)))
    if J.truthy(showTable):
        last = J.sub(J.get(G_close, "length"), 1)
        fontSize = ("12px" if J.seq(tableSize, "Small") else ("16px" if J.seq(tableSize, "Large") else "14px"))
        position = ("top_left" if J.seq(tablePosition, "Top-Left") else ("bottom_left" if J.seq(tablePosition, "Bottom-Left") else ("bottom_right" if J.seq(tablePosition, "Bottom-Right") else "top_right")))
        adxCellColor = (adxBullColor((_t48 if J.truthy(_t48 := J.get(adxValue, last)) else 0)) if J.ge(J.get(diValue, last), 25) else adxBearColor((_t49 if J.truthy(_t49 := J.get(adxValue, last)) else 0)))
        diCellColor = (diBullColor((_t50 if J.truthy(_t50 := J.get(adxValue, last)) else 0)) if J.gt(J.get(diValue, last), threshold) else diBearColor((_t51 if J.truthy(_t51 := J.get(adxValue, last)) else 0)))
        def legendCell(text=J.undefined, *_args):
            return J.obj(("text", text), ("color", "white"), ("backgroundColor", "transparent"), ("fontSize", fontSize), ("textAlign", "center"), ("padding", "2px 6px"))
        def valueCell(text=J.undefined, backgroundColor=J.undefined, *_args):
            return J.obj(("text", text), ("color", "white"), ("backgroundColor", backgroundColor), ("fontSize", fontSize), ("textAlign", "center"), ("padding", "2px 6px"))
        G_paint_overlay("ADX DI Table", J.obj(("position", position), ("offset_y", 25), ("order", "above_all")), J.obj(("rows", J.JSArray([J.obj(("cells", J.JSArray([legendCell("ADX"), valueCell(J.get((_t52 if J.truthy(_t52 := J.get(adxValue, last)) else 0), "toFixed")(1), adxCellColor)]))), J.obj(("cells", J.JSArray([legendCell("ADX"), valueCell(strengthText((_t53 if J.truthy(_t53 := J.get(adxValue, last)) else 0)), adxCellColor)]))), J.obj(("cells", J.JSArray([legendCell("ADX"), valueCell(trendText(adxValue, last), adxCellColor)]))), J.obj(("cells", J.JSArray([legendCell("DI"), valueCell(J.get((_t54 if J.truthy(_t54 := J.get(diValue, last)) else 0), "toFixed")(1), diCellColor)]))), J.obj(("cells", J.JSArray([legendCell("DI"), valueCell(diStrengthText((_t55 if J.truthy(_t55 := J.get(diValue, last)) else 0)), diCellColor)]))), J.obj(("cells", J.JSArray([legendCell("DI"), valueCell(trendText(diValue, last), diCellColor)]))), J.obj(("cells", J.JSArray([legendCell("Dynamics"), valueCell(powerDynamicsText(last), (adxBearColor((_t56 if J.truthy(_t56 := J.get(adxValue, last)) else 0)) if J.le(J.get(diValue, last), threshold) else diCellColor))])))]))))
    G_register_signal(bullishSignal, "ADX Bullish DI Cross")
    G_register_signal(bearishSignal, "ADX Bearish DI Cross")
    G_register_signal(adxBullishCross, "ADX Bullish Signal Cross")
    G_register_signal(adxBearishCross, "ADX Bearish Signal Cross")


register_store_indicator(
    script,
    name='zenalgo_adx_TS',
    title='ZenAlgo - ADX',
    developer='ZenAlgo',
    url='https://trendspider.com/trading-tools-store/indicators/6a2056-zenalgo-adx/',
    position='lower',
    inputs=[{'id': 'warmup', 'title': 'Warmup', 'type': 'number', 'default': 500}, {'id': 'length', 'title': 'Length', 'type': 'number', 'default': 7}, {'id': 'threshold', 'title': 'Threshold', 'type': 'number', 'default': 25}, {'id': 'adx_signal_len', 'title': 'ADX Signal Len', 'type': 'number', 'default': 3}, {'id': 'adx_signal_ma', 'title': 'ADX Signal MA', 'type': 'select_wide', 'default': 'SMA', 'options': ['SMA', 'EMA']}, {'id': 'enable_divergences', 'title': 'Enable Divergences', 'type': 'boolean', 'default': True}, {'id': 'show_div_labels', 'title': 'Show Div Labels', 'type': 'boolean', 'default': True}, {'id': 'div_label_offset', 'title': 'Div Label Offset', 'type': 'number', 'default': 0.5}, {'id': 'show_table', 'title': 'Show Table', 'type': 'boolean', 'default': True}, {'id': 'table_size', 'title': 'Table Size', 'type': 'select_wide', 'default': 'Small', 'options': ['Small', 'Normal', 'Large']}, {'id': 'table_position', 'title': 'Table Position', 'type': 'select_wide', 'default': 'Top-Right', 'options': ['Top-Left', 'Top-Right', 'Bottom-Left', 'Bottom-Right']}],
    outputs=['di_histogram', 'di_line', 'adx', 'adx_signal_ma', 'threshold', '70', '80', '90', '100', 'fill_70_base', 'fill_80_base', 'fill_90_base', 'fill_100_base', 'adx_bullish_cross', 'adx_bearish_cross', 'di_cross_above_25', 'di_cross_below_25', 'regular_bearish_divergences_di', 'hidden_bearish_divergences_di', 'regular_bullish_divergences_di', 'hidden_bullish_divergences_di', 'regular_bear_div_label_anchor', 'hidden_bear_div_label_anchor', 'regular_bull_div_label_anchor', 'hidden_bull_div_label_anchor', 'rising_bull_di_weak', 'rising_bull_di_moderate', 'rising_bull_di_strong', 'rising_bull_di_very_strong', 'rising_bull_di_extreme', 'rising_bear_di_weak', 'rising_bear_di_moderate', 'rising_bear_di_strong', 'rising_bear_di_very_strong', 'rising_bear_di_extreme', 'adx_bullish_di_cross', 'adx_bearish_di_cross', 'adx_bullish_signal_cross', 'adx_bearish_signal_cross'],
    signals=['adx_bullish_di_cross', 'adx_bearish_di_cross', 'adx_bullish_signal_cross', 'adx_bearish_signal_cross'],
    requires=[],
    parity='exact',
)
