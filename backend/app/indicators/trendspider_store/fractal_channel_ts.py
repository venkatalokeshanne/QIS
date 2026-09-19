"""
Fractal Channel -- TrendSpider store indicator by TrendSpider Team.

Registered as "fractal_channel_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/fractal-channel/)
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
    G_assert = G["assert"]
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_fill = G["fill"]
    G_for_every = G["for_every"]
    G_fractal_high = G["fractal_high"]
    G_fractal_low = G["fractal_low"]
    G_high = G["high"]
    G_input = G["input"]
    G_low = G["low"]
    G_paint = G["paint"]
    G_paint_label_at_line = G["paint_label_at_line"]
    G_series_of = G["series_of"]
    G_describe_indicator("Fractal Channel")
    fractalPeriod = J.get(G_input, "number")("Fractal Period", 5, J.obj(("min", 2), ("max", 10)))
    anchorLookbackStart = 200
    anchorLookbackEnd = 50
    fractals = J.obj(("high", G_fractal_high(G_high, fractalPeriod)), ("low", G_fractal_low(G_low, fractalPeriod)))
    startIndex = J.get(G_Math, "max")(0, J.sub(J.get(G_close, "length"), anchorLookbackStart))
    endIndex = J.sub(J.get(G_close, "length"), anchorLookbackEnd)
    G_assert(J.gt(endIndex, startIndex), "Not enough bars to form anchor window.")
    highestFractalIndex = None
    highestFractalValue = J.neg(G_Infinity)
    lowestFractalIndex = None
    lowestFractalValue = G_Infinity
    i = startIndex
    while J.lt(i, endIndex):
        if ((J.get(J.get(fractals, "high"), i) is not None) and J.gt(J.get(J.get(fractals, "high"), i), highestFractalValue)):
            highestFractalValue = J.get(J.get(fractals, "high"), i)
            highestFractalIndex = i
        if ((J.get(J.get(fractals, "low"), i) is not None) and J.lt(J.get(J.get(fractals, "low"), i), lowestFractalValue)):
            lowestFractalValue = J.get(J.get(fractals, "low"), i)
            lowestFractalIndex = i
        i = J.inc(i)
    G_assert(((lowestFractalIndex is not None) if J.truthy(_t1 := (highestFractalIndex is not None)) else _t1), "No valid fractal high/low found in the 200–50 bars‐ago window.")
    regressionStart = J.get(G_Math, "min")(highestFractalIndex, lowestFractalIndex)
    x = J.JSArray([])
    y = J.JSArray([])
    i_2 = regressionStart
    while J.lt(i_2, J.get(G_close, "length")):
        J.get(x, "push")(J.sub(i_2, regressionStart))
        J.get(y, "push")(J.get(G_close, i_2))
        i_2 = J.inc(i_2)
    n = J.get(x, "length")
    def _f2(a=J.undefined, b=J.undefined, *_args):
        return J.add(a, b)
    sumX = J.get(x, "reduce")(_f2, 0)
    def _f3(a=J.undefined, b=J.undefined, *_args):
        return J.add(a, b)
    sumY = J.get(y, "reduce")(_f3, 0)
    def _f4(acc=J.undefined, xi=J.undefined, idx=J.undefined, *_args):
        return J.add(acc, J.mul(xi, J.get(y, idx)))
    sumXY = J.get(x, "reduce")(_f4, 0)
    def _f5(acc=J.undefined, xi=J.undefined, *_args):
        return J.add(acc, J.mul(xi, xi))
    sumX2 = J.get(x, "reduce")(_f5, 0)
    slope = J.div(J.sub(J.mul(n, sumXY), J.mul(sumX, sumY)), J.sub(J.mul(n, sumX2), J.mul(sumX, sumX)))
    intercept = J.div(J.sub(sumY, J.mul(slope, sumX)), n)
    trendline = G_series_of(None)
    i_3 = regressionStart
    while J.lt(i_3, J.get(G_close, "length")):
        xVal = J.sub(i_3, regressionStart)
        J.set(trendline, i_3, J.add(J.mul(slope, xVal), intercept))
        i_3 = J.inc(i_3)
    G_paint(trendline, J.obj(("name", "Regression Trendline"), ("color", "rgba(255, 255, 255, 0.6)"), ("style", "line"), ("width", 2)))
    priceSeg = J.get(G_close, "slice")(regressionStart)
    trendSeg = J.get(trendline, "slice")(regressionStart)
    def _f6(c=J.undefined, t=J.undefined, *_args):
        return J.get(G_Math, "abs")(J.sub(c, t))
    deviations = G_for_every(priceSeg, trendSeg, _f6)
    def _f7(a=J.undefined, b=J.undefined, *_args):
        return J.add(a, J.mul(b, b))
    stdDev = J.get(G_Math, "sqrt")(J.div(J.get(deviations, "reduce")(_f7, 0), J.get(deviations, "length")))
    def _f8(t=J.undefined, *_args):
        return (J.add(t, stdDev) if (t is not None) else None)
    upperBand = J.get(trendline, "map")(_f8)
    def _f9(t=J.undefined, *_args):
        return (J.sub(t, stdDev) if (t is not None) else None)
    lowerBand = J.get(trendline, "map")(_f9)
    G_paint(upperBand, J.obj(("name", "Upper Band (1 SD)"), ("color", "rgba(211, 211, 211, 0.4)"), ("style", "line"), ("width", 1)))
    G_paint(lowerBand, J.obj(("name", "Lower Band (1 SD)"), ("color", "rgba(211, 211, 211, 0.4)"), ("style", "line"), ("width", 1)))
    G_fill(G_paint(upperBand, J.obj(("hidden", True))), G_paint(lowerBand, J.obj(("hidden", True))), "rgba(211, 211, 211, 0.1)")
    G_paint_label_at_line(G_paint(G_series_of(highestFractalValue), J.obj(("hidden", True))), highestFractalIndex, "Highest Anchor", J.obj(("color", "white"), ("border_color", "red"), ("border_width", 1)))
    G_paint_label_at_line(G_paint(G_series_of(lowestFractalValue), J.obj(("hidden", True))), lowestFractalIndex, "Lowest Anchor", J.obj(("color", "white"), ("border_color", "green"), ("border_width", 1)))
    def _f10(t=J.undefined, *_args):
        return (J.add(t, J.mul(2, stdDev)) if (t is not None) else None)
    upperBand2SD = J.get(trendline, "map")(_f10)
    def _f11(t=J.undefined, *_args):
        return (J.add(t, J.mul(3, stdDev)) if (t is not None) else None)
    upperBand3SD = J.get(trendline, "map")(_f11)
    G_paint(upperBand2SD, J.obj(("name", "Upper Band (2 SD)"), ("color", "red"), ("style", "line"), ("width", 1)))
    G_paint(upperBand3SD, J.obj(("name", "Upper Band (3 SD)"), ("color", "red"), ("style", "line"), ("width", 1)))
    def _f12(t=J.undefined, *_args):
        return (J.sub(t, J.mul(2, stdDev)) if (t is not None) else None)
    lowerBand2SD = J.get(trendline, "map")(_f12)
    def _f13(t=J.undefined, *_args):
        return (J.sub(t, J.mul(3, stdDev)) if (t is not None) else None)
    lowerBand3SD = J.get(trendline, "map")(_f13)
    G_paint(lowerBand2SD, J.obj(("name", "Lower Band (2 SD)"), ("color", "green"), ("style", "line"), ("width", 1)))
    G_paint(lowerBand3SD, J.obj(("name", "Lower Band (3 SD)"), ("color", "green"), ("style", "line"), ("width", 1)))


register_store_indicator(
    script,
    name='fractal_channel_TS',
    title='Fractal Channel',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/fractal-channel/',
    position='price',
    inputs=[{'id': 'fractal_period', 'title': 'Fractal Period', 'type': 'number', 'default': 5}],
    outputs=['regression_trendline', 'upper_band__1_sd_', 'lower_band__1_sd_', 'line_4', 'line_5', 'line_7', 'line_8', 'upper_band__2_sd_', 'upper_band__3_sd_', 'lower_band__2_sd_', 'lower_band__3_sd_'],
    signals=[],
    requires=[],
    parity='exact',
)
