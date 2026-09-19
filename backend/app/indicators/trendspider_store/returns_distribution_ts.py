"""
Returns Distribution -- TrendSpider store indicator by Dr. Goose.

Registered as "returns_distribution_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68a091-returns-distribution/)
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
    G_assert = G["assert"]
    G_close = G["close"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_input = G["input"]
    G_paint_overlay = G["paint_overlay"]
    G_describe_indicator("Returns Distribution #TSBuild25", J.obj(("shortName", "Returns Dist")))
    inputs = J.obj(("lookback", J.get(G_input, "number")("Lookback (0 = All)", 0, J.obj(("min", 0)))), ("bins", J.get(G_input, "number")("Histogram Bins", 30, J.obj(("min", 10), ("max", 50)))), ("color_positive", J.get(G_input, "color")("Positive Color", "rgba(0, 230, 118, 0.85)")), ("color_negative", J.get(G_input, "color")("Negative Color", "rgba(255, 23, 68, 0.85)")), ("color_current", J.get(G_input, "color")("Current Bar Color", "#03A9F4")))
    returns = J.JSArray([])
    i = 1
    while J.lt(i, J.get(G_close, "length")):
        J.get(returns, "push")(J.mul(J.sub(J.div(J.get(G_close, i), J.get(G_close, J.sub(i, 1))), 1), 100))
        i = J.inc(i)
    historicalReturns = (J.get(returns, "slice")(J.sub(J.neg(J.get(inputs, "lookback")), 1), (-1)) if J.gt(J.get(inputs, "lookback"), 0) else J.get(returns, "slice")(0, (-1)))
    G_assert(J.gt(J.get(historicalReturns, "length"), 1), "Not enough historical data to build distribution.")
    n = J.get(historicalReturns, "length")
    def _f1(a=J.undefined, b=J.undefined, *_args):
        return J.add(a, b)
    mean = J.div(J.get(historicalReturns, "reduce")(_f1, 0), n)
    def _f2(a=J.undefined, b=J.undefined, *_args):
        return J.add(a, J.mul(J.sub(b, mean), J.sub(b, mean)))
    var_samp = J.div(J.get(historicalReturns, "reduce")(_f2, 0), J.get(G_Math, "max")(J.sub(n, 1), 1))
    stdDev = J.get(G_Math, "sqrt")(J.get(G_Math, "max")(var_samp, 0))
    maxHist = J.get(G_Math, "max")(*J.spread(historicalReturns))
    minHist = J.get(G_Math, "min")(*J.spread(historicalReturns))
    currentReturn = J.get(returns, J.sub(J.get(returns, "length"), 1))
    minReturn = J.get(G_Math, "min")(minHist, currentReturn)
    maxReturn = J.get(G_Math, "max")(maxHist, currentReturn)
    isNewExtremeHigh = J.gt(currentReturn, maxHist)
    isNewExtremeLow = J.lt(currentReturn, minHist)
    numBins = (J.get(inputs, "bins") if J.gt(J.get(inputs, "bins"), 0) else J.get(G_Math, "max")(10, J.get(G_Math, "ceil")(J.get(G_Math, "sqrt")(n))))
    span = J.get(G_Math, "max")(J.sub(maxReturn, minReturn), 0.01)
    binSize = J.div(span, numBins)
    bins = J.get(G_Array(numBins), "fill")(0)
    binLabels = J.JSArray([])
    i_2 = 0
    while J.lt(i_2, numBins):
        binStart = J.add(minReturn, J.mul(i_2, binSize))
        binEnd = J.add(binStart, binSize)
        J.get(binLabels, "push")(J.add(J.get(binStart, "toFixed")(2), "%"))
        j = 0
        while J.lt(j, n):
            r = J.get(historicalReturns, j)
            if (J.ge(r, binStart) and (J.lt(r, binEnd) or (J.seq(i_2, J.sub(numBins, 1)) and J.le(r, binEnd)))):
                J.update_member(bins, i_2, J.inc, True)
            j = J.inc(j)
        i_2 = J.inc(i_2)
    currentBinIndex = (-1)
    if J.gt(binSize, 0):
        idx = J.get(G_Math, "floor")(J.div(J.sub(currentReturn, minReturn), binSize))
        currentBinIndex = J.get(G_Math, "max")(0, J.get(G_Math, "min")(J.sub(numBins, 1), idx))
    def _f3(__=J.undefined, i_3=J.undefined, *_args):
        if J.seq(i_3, currentBinIndex):
            return J.get(inputs, "color_current")
        binCenter = J.add(minReturn, J.mul(J.add(i_3, 0.5), binSize))
        return (J.get(inputs, "color_positive") if J.ge(binCenter, 0) else J.get(inputs, "color_negative"))
    def _f4(__=J.undefined, i_3=J.undefined, *_args):
        return (("#FFD166" if (J.truthy(isNewExtremeHigh) or J.truthy(isNewExtremeLow)) else "#FFFFFF") if J.seq(i_3, currentBinIndex) else "#2A2F3A")
    def _f5(__=J.undefined, i_3=J.undefined, *_args):
        return ((2 if (J.truthy(isNewExtremeHigh) or J.truthy(isNewExtremeLow)) else 1.5) if J.seq(i_3, currentBinIndex) else 0.5)
    distributionChart = J.obj(("width", "320px"), ("height", "140px"), ("type", "bar"), ("options", J.obj(("scales", J.obj(("y", J.obj(("display", False))), ("x", J.obj(("ticks", J.obj(("autoSkip", True), ("maxRotation", 0), ("minRotation", 0), ("font", J.obj(("size", 9))), ("color", "#C9CED6"))), ("grid", J.obj(("display", False))))))), ("plugins", J.obj(("legend", J.obj(("display", False))))), ("layout", J.obj(("padding", J.obj(("top", 8))))))), ("data", J.obj(("labels", binLabels), ("datasets", J.JSArray([J.obj(("data", bins), ("backgroundColor", J.get(bins, "map")(_f3)), ("borderColor", J.get(bins, "map")(_f4)), ("borderWidth", J.get(bins, "map")(_f5)), ("borderRadius", 2))])))))
    def titleCell(text=J.undefined, *_args):
        return J.obj(("text", text), ("fontWeight", 600), ("color", "#E7EBF3"), ("padding", "8px 10px"), ("fontSize", 13))
    def statCell(label=J.undefined, value=J.undefined, *_args):
        return J.obj(("text", J.template("<span style=\"opacity:0.85\">", label, "</span><span style=\"float:right;font-weight:600\">", value, "</span>")), ("color", "#D3D7DF"), ("padding", "6px 10px"), ("fontSize", 12))
    def keyCell(text=J.undefined, color=J.undefined, *_args):
        return J.obj(("text", text), ("fontWeight", 700), ("fontSize", 13), ("color", color), ("padding", "8px 10px"), ("textAlign", "center"))
    SEPARATOR = J.obj(("text", ""), ("colspan", 2), ("borderBottom", "1px solid #2A2F3A"), ("padding", "2px 0"))
    titleText = (J.template(J.get(G_current, "ticker"), " Returns Distribution") if J.gt(J.get(inputs, "lookback"), 0) else J.template(J.get(G_current, "ticker"), " Returns Distribution"))
    extremeTag = (" (NEW MAX)" if J.truthy(isNewExtremeHigh) else (" (NEW MIN)" if J.truthy(isNewExtremeLow) else ""))
    J.JSArray([J.obj(*J.obj_spread(keyCell(J.template("Current: ", J.get(currentReturn, "toFixed")(2), "%", extremeTag), J.get(inputs, "color_current"))), ("colspan", 2))])
    G_paint_overlay("Table", J.obj(("position", "bottom_right"), ("order", "above_all")), J.obj(("fontSize", 12), ("border", "1px solid #2A2F3A"), ("background", "rgba(16, 18, 24, 0.92)"), ("borderRadius", "10px"), ("boxShadow", "0 8px 24px rgba(0,0,0,0.35)"), ("rows", J.JSArray([J.obj(("cells", J.JSArray([J.obj(*J.obj_spread(titleCell(titleText)), ("colspan", 2), ("textAlign", "center"))]))), J.obj(("cells", J.JSArray([SEPARATOR]))), J.obj(("cells", J.JSArray([J.obj(("chart", distributionChart), ("colspan", 2))]))), J.obj(("cells", J.JSArray([SEPARATOR]))), J.obj(("cells", J.JSArray([statCell("Mean: ", J.template(J.get(mean, "toFixed")(2), "%")), statCell("Std Dev: ", J.template(J.get(stdDev, "toFixed")(2), "%"))]))), J.obj(("cells", J.JSArray([statCell("Max: ", J.template(J.get(maxReturn, "toFixed")(2), "%")), statCell("Min: ", J.template(J.get(minReturn, "toFixed")(2), "%"))]))), J.obj(("cells", J.JSArray([J.obj(*J.obj_spread(keyCell(J.template("Current: ", J.get(currentReturn, "toFixed")(2), "%"), J.get(inputs, "color_current"))), ("colspan", 2))])))]))))


register_store_indicator(
    script,
    name='returns_distribution_TS',
    title='Returns Distribution',
    developer='Dr. Goose',
    url='https://trendspider.com/trading-tools-store/indicators/68a091-returns-distribution/',
    position='price',
    inputs=[{'id': 'lookback__0___all_', 'title': 'Lookback (0 = All)', 'type': 'number', 'default': 0}, {'id': 'histogram_bins', 'title': 'Histogram Bins', 'type': 'number', 'default': 30}, {'id': 'positive_color', 'title': 'Positive Color', 'type': 'color', 'default': 'rgba(0, 230, 118, 0.85)'}, {'id': 'negative_color', 'title': 'Negative Color', 'type': 'color', 'default': 'rgba(255, 23, 68, 0.85)'}, {'id': 'current_bar_color', 'title': 'Current Bar Color', 'type': 'color', 'default': '#03A9F4'}],
    outputs=[],
    signals=[],
    requires=[],
    parity='exact',
)
