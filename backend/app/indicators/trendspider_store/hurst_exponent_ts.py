"""
Hurst Exponent -- TrendSpider store indicator by Dr. Goose.

Registered as "hurst_exponent_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/689a32-hurst-exponent-tsbuild25/)
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
    G_for_every = G["for_every"]
    G_input = G["input"]
    G_paint = G["paint"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    def constant_series(val=J.undefined, *_args):
        out = G_series_of(None)
        i = 0
        while J.lt(i, J.get(G_time, "length")):
            J.set(out, i, val)
            i = J.add(i, 1)
        return out
    def rolling_low(src=J.undefined, len=J.undefined, *_args):
        out = G_series_of(None)
        i = 0
        while J.lt(i, J.get(src, "length")):
            if J.ge(J.add(i, 1), len):
                lo = J.pos(G_Infinity)
                j = J.add(J.sub(i, len), 1)
                while J.le(j, i):
                    if ((not J.nullish(J.get(src, j))) and J.lt(J.get(src, j), lo)):
                        lo = J.get(src, j)
                    j = J.add(j, 1)
                J.set(out, i, (None if J.seq(lo, J.pos(G_Infinity)) else lo))
            else:
                J.set(out, i, None)
            i = J.add(i, 1)
        return out
    def rolling_high(src=J.undefined, len=J.undefined, *_args):
        out = G_series_of(None)
        i = 0
        while J.lt(i, J.get(src, "length")):
            if J.ge(J.add(i, 1), len):
                hi = J.neg(G_Infinity)
                j = J.add(J.sub(i, len), 1)
                while J.le(j, i):
                    if ((not J.nullish(J.get(src, j))) and J.gt(J.get(src, j), hi)):
                        hi = J.get(src, j)
                    j = J.add(j, 1)
                J.set(out, i, (None if J.seq(hi, J.neg(G_Infinity)) else hi))
            else:
                J.set(out, i, None)
            i = J.add(i, 1)
        return out
    def butterworth(inputSeries=J.undefined, period=J.undefined, *_args):
        a1 = J.get(G_Math, "exp")(J.div(J.neg(J.get(G_Math, "PI")), period))
        a2 = J.mul(a1, a1)
        b1 = J.mul(J.mul(2, a1), J.get(G_Math, "cos")(J.div(J.get(G_Math, "PI"), period)))
        b2 = J.neg(a2)
        b0 = J.div(J.add(J.sub(1, b1), a2), 2)
        y = G_series_of(None)
        i = 0
        while J.lt(i, J.get(inputSeries, "length")):
            x0 = (J.get(inputSeries, i) if (not J.nullish(J.get(inputSeries, i))) else (J.get(inputSeries, J.sub(i, 1)) if J.gt(i, 0) else None))
            x1 = ((J.get(inputSeries, J.sub(i, 1)) if (not J.nullish(J.get(inputSeries, J.sub(i, 1)))) else x0) if J.gt(i, 0) else x0)
            y_1 = ((J.get(y, J.sub(i, 1)) if (not J.nullish(J.get(y, J.sub(i, 1)))) else 0) if J.gt(i, 0) else 0)
            y_2 = ((J.get(y, J.sub(i, 2)) if (not J.nullish(J.get(y, J.sub(i, 2)))) else 0) if J.gt(i, 1) else 0)
            J.set(y, i, (None if ((J.nullish(x0)) or (J.nullish(x1))) else J.add(J.add(J.add(J.mul(b0, x0), J.mul(b0, x1)), J.mul(b1, y_1)), J.mul(b2, y_2))))
            i = J.add(i, 1)
        return y
    def paint_const(val=J.undefined, label=J.undefined, color=J.undefined, *_args):
        G_paint(constant_series(val), J.obj(("name", J.template(label, " (", J.get(G_Number(val), "toFixed")(3), ")")), ("color", color), ("thickness", 1)))
    G_describe_indicator("Hurst Exponent #TSBuild25", "lower", J.obj(("decimals", 3), ("shortName", "Hurst Exp")))
    lookbackN = G_input("Lookback", 60, J.obj(("min", 2), ("step", 2)))
    bwPeriod = G_input("Butterworth Smoothing Period", 10, J.obj(("min", 2), ("step", 0.5)))
    showRawHurst = J.get(G_input, "boolean")("Show Hurst Exponent (raw)", False)
    displayMode = G_input("Smoothed Hurst Display", "Histogram", J.JSArray(["Line", "Histogram"]))
    lineWidth = G_input("Line/Bar Thickness", 2, J.obj(("min", 1), ("max", 4)))
    lowerThresh = G_input("Lower Threshold", 0.4, J.obj(("min", 0.01), ("step", 0.01)))
    upperThresh = G_input("Upper Threshold", 0.6, J.obj(("min", 0.01), ("step", 0.01)))
    ymin = rolling_low(G_close, lookbackN)
    ymax = rolling_high(G_close, lookbackN)
    hurst = G_series_of(None)
    LOG2 = J.get(G_Math, "log")(2)
    i = 0
    while J.lt(i, J.get(G_time, "length")):
        if ((J.lt(J.add(i, 1), lookbackN) or (J.nullish(J.get(ymin, i)))) or (J.nullish(J.get(ymax, i)))):
            J.set(hurst, i, None)
            i = J.add(i, 1)
            continue
        yMin = J.get(ymin, i)
        yMax = J.get(ymax, i)
        yscl = J.sub(yMax, yMin)
        lengthVal = J.undefined
        if (J.lt(lookbackN, 2) or J.seq(yMax, yMin)):
            lengthVal = 1
        else:
            acc = 0
            dx2 = J.div(1, J.mul(lookbackN, lookbackN))
            j = 1
            while J.le(j, J.sub(lookbackN, 1)):
                yj = (J.get(G_close, J.sub(i, j)) if (not J.nullish(J.get(G_close, J.sub(i, j)))) else J.get(G_close, J.add(J.sub(i, j), 1)))
                yj_1 = J.get(G_close, J.add(J.sub(i, j), 1))
                dy = (J.div(J.sub(yj, yj_1), yscl) if J.sne(yscl, 0) else 0)
                acc = J.add(acc, J.get(G_Math, "sqrt")(J.add(dx2, J.mul(dy, dy))))
                j = J.add(j, 1)
            lengthVal = acc
        FDI = J.add(1, J.div(J.add(J.get(G_Math, "log")(lengthVal), LOG2), J.get(G_Math, "log")(J.mul(2, lookbackN))))
        J.set(hurst, i, J.sub(2, FDI))
        i = J.add(i, 1)
    smoothed = butterworth(hurst, bwPeriod)
    strongTrend = "#00BFFF"
    weakTrend = "#4682B4"
    weakRevert = "#FFA500"
    strongRevert = "#FF0000"
    def _f1(v=J.undefined, *_args):
        if (J.nullish(v)):
            return "#999999"
        if J.gt(v, upperThresh):
            return strongTrend
        if J.gt(v, 0.5):
            return weakTrend
        if J.lt(v, lowerThresh):
            return strongRevert
        return weakRevert
    smoothedColors = G_for_every(smoothed, _f1)
    def _f2(v=J.undefined, *_args):
        return ("#00FF00" if ((not J.nullish(v)) and J.gt(v, 0.5)) else "#FF0000")
    rawColors = G_for_every(hurst, _f2)
    MID = 0.5
    def _f3(v=J.undefined, *_args):
        return (None if (J.nullish(v)) else J.sub(v, MID))
    smoothedDev = G_for_every(smoothed, _f3)
    upperDev = J.sub(upperThresh, MID)
    lowerDev = J.sub(lowerThresh, MID)
    isLine = J.seq(displayMode, "Line")
    midGuideVal = (MID if J.truthy(isLine) else 0)
    upperGuideVal = (upperThresh if J.truthy(isLine) else upperDev)
    lowerGuideVal = (lowerThresh if J.truthy(isLine) else lowerDev)
    midGuideLabel = ("Guide: Mid" if J.truthy(isLine) else "Guide: Zero (centered)")
    upperGuideLabel = ("Guide: Upper" if J.truthy(isLine) else "Guide: +Dev")
    lowerGuideLabel = ("Guide: Lower" if J.truthy(isLine) else "Guide: -Dev")
    paint_const(midGuideVal, midGuideLabel, "#787878")
    paint_const(upperGuideVal, upperGuideLabel, "#888888")
    paint_const(lowerGuideVal, lowerGuideLabel, "#888888")
    G_paint((hurst if J.truthy(showRawHurst) else G_series_of(None)), J.obj(("name", "Hurst (raw)"), ("color", rawColors), ("thickness", lineWidth), ("style", "line")))
    mainPlot = (smoothed if J.truthy(isLine) else smoothedDev)
    mainStyle = ("line" if J.truthy(isLine) else "histogram")
    mainName = ("Smoothed Hurst" if J.truthy(isLine) else "Smoothed Hurst (Hist, centered)")
    G_paint(mainPlot, J.obj(("name", mainName), ("color", smoothedColors), ("thickness", lineWidth), ("style", mainStyle)))


register_store_indicator(
    script,
    name='hurst_exponent_TS',
    title='Hurst Exponent',
    developer='Dr. Goose',
    url='https://trendspider.com/trading-tools-store/indicators/689a32-hurst-exponent-tsbuild25/',
    position='lower',
    inputs=[{'id': 'lookback', 'title': 'Lookback', 'type': 'number', 'default': 60}, {'id': 'butterworth_smoothing_period', 'title': 'Butterworth Smoothing Period', 'type': 'number', 'default': 10}, {'id': 'show_hurst_exponent__raw_', 'title': 'Show Hurst Exponent (raw)', 'type': 'boolean', 'default': False}, {'id': 'smoothed_hurst_display', 'title': 'Smoothed Hurst Display', 'type': 'select_wide', 'default': 'Histogram', 'options': ['Line', 'Histogram']}, {'id': 'line_bar_thickness', 'title': 'Line/Bar Thickness', 'type': 'number', 'default': 2}, {'id': 'lower_threshold', 'title': 'Lower Threshold', 'type': 'number', 'default': 0.4}, {'id': 'upper_threshold', 'title': 'Upper Threshold', 'type': 'number', 'default': 0.6}],
    outputs=['guide__zero__centered___0_000_', 'guide___dev__0_100_', 'guide___dev___0_100_', 'hurst__raw_', 'smoothed_hurst__hist__centered_'],
    signals=[],
    requires=[],
    parity='exact',
)
