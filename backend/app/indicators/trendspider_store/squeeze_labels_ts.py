"""
Squeeze Labels -- TrendSpider store indicator by TrendSpider Team.

Registered as "squeeze_labels_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/squeeze-labels/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_add = G["add"]
    G_atr = G["atr"]
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_input = G["input"]
    G_mult = G["mult"]
    G_paint = G["paint"]
    G_sma = G["sma"]
    G_stdev = G["stdev"]
    G_sub = G["sub"]
    G_describe_indicator("Squeeze Labels")
    bbLength = J.get(G_input, "number")("Bollinger Length", 20, J.obj(("min", 1)))
    bbMultiplier = J.get(G_input, "number")("Bollinger Multiplier", 2, J.obj(("min", 0.1)))
    kcLength = J.get(G_input, "number")("Keltner Length", 20, J.obj(("min", 1)))
    kcMultiplier = J.get(G_input, "number")("Keltner Multiplier", 2, J.obj(("min", 0.1)))
    bbMiddle = G_sma(G_close, bbLength)
    bbDev = G_mult(G_stdev(G_close, bbLength), bbMultiplier)
    bbUpper = G_add(bbMiddle, bbDev)
    bbLower = G_sub(bbMiddle, bbDev)
    kcMiddle = G_sma(G_close, kcLength)
    kcDev = G_mult(G_atr(14), kcMultiplier)
    kcUpper = G_add(kcMiddle, kcDev)
    kcLower = G_sub(kcMiddle, kcDev)
    def _f1(_bbUp=J.undefined, _bbLow=J.undefined, _kcUp=J.undefined, _kcLow=J.undefined, *_args):
        if (J.lt(_bbUp, _kcUp) and J.gt(_bbLow, _kcLow)):
            return "\ud83c\udf4b"
        elif (J.gt(_bbUp, _kcUp) and J.lt(_bbLow, _kcLow)):
            return "\ud83e\uddc3"
        return None
    mySqueezeCondition = G_for_every(bbUpper, bbLower, kcUpper, kcLower, _f1)
    def removeDuplicates(arr=J.undefined, *_args):
        def _f1(value=J.undefined, index=J.undefined, array=J.undefined, *_args):
            if (J.seq(index, 0) or J.sne(value, J.get(array, J.sub(index, 1)))):
                return value
            return None
        return J.get(arr, "map")(_f1)
    myUniqueCondition = removeDuplicates(mySqueezeCondition)
    G_paint(myUniqueCondition, J.obj(("style", "labels_above"), ("name", "Squeeze Indicator")))


register_store_indicator(
    script,
    name='squeeze_labels_TS',
    title='Squeeze Labels',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/squeeze-labels/',
    position='price',
    inputs=[{'id': 'bollinger_length', 'title': 'Bollinger Length', 'type': 'number', 'default': 20}, {'id': 'bollinger_multiplier', 'title': 'Bollinger Multiplier', 'type': 'number', 'default': 2}, {'id': 'keltner_length', 'title': 'Keltner Length', 'type': 'number', 'default': 20}, {'id': 'keltner_multiplier', 'title': 'Keltner Multiplier', 'type': 'number', 'default': 2}],
    outputs=['squeeze_indicator'],
    signals=[],
    requires=[],
    parity='exact',
)
