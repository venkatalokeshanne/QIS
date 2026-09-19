"""
MA Slope Strategy -- TrendSpider store indicator by TrendSpider Team.

Registered as "ma_slope_strategy_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/ma-slope-strategy/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_alma = G["alma"]
    G_close = G["close"]
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_ema = G["ema"]
    G_for_every = G["for_every"]
    G_hullma = G["hullma"]
    G_input = G["input"]
    G_kama = G["kama"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_shift = G["shift"]
    G_sma = G["sma"]
    G_twap = G["twap"]
    G_vwma = G["vwma"]
    G_wildma = G["wildma"]
    G_wma = G["wma"]
    def computeMA(type_=J.undefined, data=J.undefined, length=J.undefined, *_args):
        if J.seq(type_, "ema"):
            return G_ema(data, length)
        if J.seq(type_, "sma"):
            return G_sma(data, length)
        if J.seq(type_, "wma"):
            return G_wma(data, length)
        if J.seq(type_, "hullma"):
            return G_hullma(data, length)
        if J.seq(type_, "twap"):
            return G_twap(data, length)
        if J.seq(type_, "alma"):
            return G_alma(data, length)
        if J.seq(type_, "kama"):
            return G_kama(data, length)
        if J.seq(type_, "vwma"):
            return G_vwma(data, length)
        if J.seq(type_, "wildma"):
            return G_wildma(data, length)
        return G_ema(data, length)
    G_describe_indicator("MA Slope Strategy", "price")
    maLength = J.get(G_input, "number")("MA Length", 14, J.obj(("min", 2), ("max", 100)))
    maType = G_input("MA Type", "ema", J.get(G_constants, "ma_types"))
    degreeThreshold = J.get(G_input, "number")("Degree Threshold", 30, J.obj(("min", 1), ("max", 90)))
    slopeSmoothing = J.get(G_input, "number")("Slope Smoothing", 3, J.obj(("min", 1), ("max", 10)))
    ma = computeMA(maType, G_close, maLength)
    def _f1(current=J.undefined, previous=J.undefined, *_args):
        return J.div(J.sub(current, previous), 1)
    rawSlope = G_for_every(ma, G_shift(ma, 1), _f1)
    smoothedSlope = G_ema(rawSlope, slopeSmoothing)
    def _f2(slopeVal=J.undefined, *_args):
        return J.mul(J.get(G_Math, "atan")(slopeVal), J.div(180, J.get(G_Math, "PI")))
    slopeInDegrees = J.get(smoothedSlope, "map")(_f2)
    def _f3(degree=J.undefined, *_args):
        absDegree = J.get(G_Math, "abs")(degree)
        if J.lt(absDegree, 5):
            return "gray"
        if J.gt(degree, 0):
            greenIntensity = J.get(G_Math, "min")(255, J.add(J.get(G_Math, "round")(J.mul(J.div(absDegree, degreeThreshold), 200)), 55))
            return J.template("rgba(0, ", greenIntensity, ", 0, 1)")
        else:
            redIntensity = J.get(G_Math, "min")(255, J.add(J.get(G_Math, "round")(J.mul(J.div(absDegree, degreeThreshold), 200)), 55))
            return J.template("rgba(", redIntensity, ", 0, 0, 1)")
    maColors = J.get(slopeInDegrees, "map")(_f3)
    G_paint(ma, J.obj(("name", "Enhanced MA with Slope Colors"), ("color", maColors), ("thickness", 2)))
    def _f4(degree=J.undefined, *_args):
        return (True if J.lt(J.get(G_Math, "abs")(degree), 5) else False)
    graySignal = J.get(slopeInDegrees, "map")(_f4)
    def _f5(degree=J.undefined, *_args):
        return (True if (J.gt(degree, 0) and J.ge(J.get(G_Math, "abs")(degree), 5)) else False)
    greenSignal = J.get(slopeInDegrees, "map")(_f5)
    def _f6(degree=J.undefined, *_args):
        return (True if (J.lt(degree, 0) and J.ge(J.get(G_Math, "abs")(degree), 5)) else False)
    redSignal = J.get(slopeInDegrees, "map")(_f6)
    G_register_signal(graySignal, "MA Slope Flat")
    G_register_signal(greenSignal, "MA Slope Up")
    G_register_signal(redSignal, "MA Slope Down")


register_store_indicator(
    script,
    name='ma_slope_strategy_TS',
    title='MA Slope Strategy',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/ma-slope-strategy/',
    position='price',
    inputs=[{'id': 'ma_length', 'title': 'MA Length', 'type': 'number', 'default': 14}, {'id': 'ma_type', 'title': 'MA Type', 'type': 'select_wide', 'default': 'ema', 'options': ['ema', 'sma', 'wildma', 'vwma', 'wma', 'hullma', 'kama', 'alma', 'twap']}, {'id': 'degree_threshold', 'title': 'Degree Threshold', 'type': 'number', 'default': 30}, {'id': 'slope_smoothing', 'title': 'Slope Smoothing', 'type': 'number', 'default': 3}],
    outputs=['enhanced_ma_with_slope_colors', 'ma_slope_flat', 'ma_slope_up', 'ma_slope_down'],
    signals=['ma_slope_flat', 'ma_slope_up', 'ma_slope_down'],
    requires=[],
    parity='exact',
)
