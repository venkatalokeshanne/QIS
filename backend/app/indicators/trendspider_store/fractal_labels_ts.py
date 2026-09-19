"""
Fractal Labels -- TrendSpider store indicator by TrendSpider Team.

Registered as "fractal_labels_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/fractal-labels/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_String = G["String"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_fractal_high = G["fractal_high"]
    G_fractal_low = G["fractal_low"]
    G_high = G["high"]
    G_input = G["input"]
    G_low = G["low"]
    G_paint = G["paint"]
    G_describe_indicator("Fractal Labels with Recent Lines (H,L)", "price")
    myFractalLength = J.get(G_input, "number")("Fractal Length", 21, J.obj(("min", 3)))
    myNumRecentFractals = J.get(G_input, "number")("Number of Recent Fractals", 20, J.obj(("min", 1), ("max", 50)))
    myFractalHighs = G_fractal_high(G_high, myFractalLength)
    myFractalLows = G_fractal_low(G_low, myFractalLength)
    def assignLetters(fractals=J.undefined, *_args):
        recentFractals = J.JSArray([])
        letterCode = 65
        i = J.sub(J.get(fractals, "length"), 1)
        while (J.ge(i, 0) and J.lt(J.get(recentFractals, "length"), myNumRecentFractals)):
            if (J.get(fractals, i) is not None):
                J.get(recentFractals, "push")(J.obj(("index", i), ("value", J.get(fractals, i)), ("letter", J.get(G_String, "fromCharCode")(letterCode))))
                letterCode = J.inc(letterCode)
            i = J.dec(i)
        return recentFractals
    myRecentHighs = assignLetters(myFractalHighs)
    myRecentLows = assignLetters(myFractalLows)
    def _f1(_h=J.undefined, _prevH=J.undefined, _i=J.undefined, *_args):
        if (_h is None):
            return None
        def _f1(rh=J.undefined, *_args):
            return J.seq(J.get(rh, "index"), _i)
        recentHigh = J.get(myRecentHighs, "find")(_f1)
        if J.truthy(recentHigh):
            return J.template("H-", J.get(recentHigh, "letter"))
        return None
    myFractalHighsLabels = G_for_every(myFractalHighs, _f1)
    def _f2(_l=J.undefined, _prevL=J.undefined, _i=J.undefined, *_args):
        if (_l is None):
            return None
        def _f1(rl=J.undefined, *_args):
            return J.seq(J.get(rl, "index"), _i)
        recentLow = J.get(myRecentLows, "find")(_f1)
        if J.truthy(recentLow):
            return J.template("L-", J.get(recentLow, "letter"))
        return None
    myFractalLowsLabels = G_for_every(myFractalLows, _f2)
    G_paint(myFractalHighsLabels, J.obj(("style", "labels_above"), ("color", "blue")))
    G_paint(myFractalLowsLabels, J.obj(("style", "labels_below"), ("color", "red")))


register_store_indicator(
    script,
    name='fractal_labels_TS',
    title='Fractal Labels',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/fractal-labels/',
    position='price',
    inputs=[{'id': 'fractal_length', 'title': 'Fractal Length', 'type': 'number', 'default': 21}, {'id': 'number_of_recent_fractals', 'title': 'Number of Recent Fractals', 'type': 'number', 'default': 20}],
    outputs=['line_1', 'line_2'],
    signals=[],
    requires=[],
    parity='exact',
)
