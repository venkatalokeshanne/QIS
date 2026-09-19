"""
Momentum with Bands -- TrendSpider store indicator by James Chambers.

Registered as "momentum_with_bands_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/momentum-with-bands/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_fill = G["fill"]
    G_input = G["input"]
    G_paint = G["paint"]
    def calculateSMA(data=J.undefined, length=J.undefined, *_args):
        smaValues = J.JSArray([])
        i = 0
        while J.lt(i, J.get(data, "length")):
            if J.lt(i, J.sub(length, 1)):
                J.get(smaValues, "push")(None)
            else:
                sumValues = 0
                j = 0
                while J.lt(j, length):
                    sumValues = J.add(sumValues, J.get(data, J.sub(i, j)))
                    j = J.inc(j)
                J.get(smaValues, "push")(J.div(sumValues, length))
            i = J.inc(i)
        return smaValues
    def calculateStdDev(data=J.undefined, length=J.undefined, *_args):
        stddevValues = J.JSArray([])
        smaValues = calculateSMA(data, length)
        i = 0
        while J.lt(i, J.get(data, "length")):
            if J.lt(i, J.sub(length, 1)):
                J.get(stddevValues, "push")(None)
            else:
                sumDiffs = 0
                j = 0
                while J.lt(j, length):
                    sumDiffs = J.add(sumDiffs, J.get(G_Math, "pow")(J.sub(J.get(data, J.sub(i, j)), J.get(smaValues, i)), 2))
                    j = J.inc(j)
                J.get(stddevValues, "push")(J.get(G_Math, "sqrt")(J.div(sumDiffs, length)))
            i = J.inc(i)
        return stddevValues
    G_describe_indicator("Momentum with Bollinger Bands v2", "lower", J.obj(("shortName", "MoBB"), ("decimals", 2)))
    momentumLength = G_input("Momentum Length", 14, J.obj(("min", 1), ("max", 100)))
    bbLength = G_input("Bollinger Band Length", 20, J.obj(("min", 1), ("max", 100)))
    bbMultiplier = G_input("Bollinger Bands Multiplier", 2, J.obj(("min", 1), ("max", 5)))
    def _f1(value=J.undefined, index=J.undefined, *_args):
        if J.lt(index, momentumLength):
            return None
        return J.sub(value, J.get(G_close, J.sub(index, momentumLength)))
    momentumValues = J.get(G_close, "map")(_f1)
    smaMomentum = calculateSMA(momentumValues, bbLength)
    stdDevMomentum = calculateStdDev(momentumValues, bbLength)
    def _f2(v=J.undefined, i=J.undefined, *_args):
        return (J.add(v, J.mul(bbMultiplier, J.get(stdDevMomentum, i))) if (v is not None) else None)
    upperBand = J.get(smaMomentum, "map")(_f2)
    def _f3(v=J.undefined, i=J.undefined, *_args):
        return (J.sub(v, J.mul(bbMultiplier, J.get(stdDevMomentum, i))) if (v is not None) else None)
    lowerBand = J.get(smaMomentum, "map")(_f3)
    def _f4(value=J.undefined, index=J.undefined, *_args):
        if (value is None):
            return None
        if J.lt(value, J.get(lowerBand, index)):
            return "green"
        if J.gt(value, J.get(upperBand, index)):
            return "red"
        return "black"
    momentumColors = J.get(momentumValues, "map")(_f4)
    paintedMomentum = G_paint(momentumValues, J.obj(("name", "Momentum"), ("color", momentumColors), ("thickness", 2)))
    paintedUpperBand = G_paint(upperBand, J.obj(("name", "Upper Band"), ("color", "gray"), ("thickness", 1)))
    paintedLowerBand = G_paint(lowerBand, J.obj(("name", "Lower Band"), ("color", "gray"), ("thickness", 1)))
    G_fill(paintedMomentum, paintedUpperBand, "rgba(255, 0, 0, 0.1)")
    G_fill(paintedMomentum, paintedLowerBand, "rgba(0, 255, 0, 0.1)")


register_store_indicator(
    script,
    name='momentum_with_bands_TS',
    title='Momentum with Bands',
    developer='James Chambers',
    url='https://trendspider.com/trading-tools-store/indicators/momentum-with-bands/',
    position='lower',
    inputs=[{'id': 'momentum_length', 'title': 'Momentum Length', 'type': 'number', 'default': 14}, {'id': 'bollinger_band_length', 'title': 'Bollinger Band Length', 'type': 'number', 'default': 20}, {'id': 'bollinger_bands_multiplier', 'title': 'Bollinger Bands Multiplier', 'type': 'number', 'default': 2}],
    outputs=['momentum', 'upper_band', 'lower_band'],
    signals=[],
    requires=[],
    parity='exact',
)
