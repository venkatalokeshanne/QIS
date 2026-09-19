"""
Triple RSI with Overbought/Oversold Shading -- TrendSpider store indicator by TrendSpider Team.

Registered as "triple_rsi_with_overbought_oversold_shading_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/triple-rsi-with-overbought-oversold-shading/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_fill = G["fill"]
    G_for_every = G["for_every"]
    G_horizontal_line = G["horizontal_line"]
    G_input = G["input"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_rsi = G["rsi"]
    G_describe_indicator("Triple RSI with Overbought/Oversold Shading", "lower")
    myLengths = J.JSArray([7, 14, 28])
    myOverboughtLevel = J.get(G_input, "number")("Overbought Level", 70, J.obj(("min", 50), ("max", 100)))
    myOversoldLevel = J.get(G_input, "number")("Oversold Level", 30, J.obj(("min", 0), ("max", 50)))
    myRsi7 = G_rsi(G_close, J.get(myLengths, 0))
    myRsi14 = G_rsi(G_close, J.get(myLengths, 1))
    myRsi28 = G_rsi(G_close, J.get(myLengths, 2))
    def myAllRSIsAbove(level=J.undefined, *_args):
        def _f1(_r7=J.undefined, _r14=J.undefined, _r28=J.undefined, *_args):
            return (J.gt(_r28, level) if J.truthy(_t1 := (J.gt(_r14, level) if J.truthy(_t2 := J.gt(_r7, level)) else _t2)) else _t1)
        return G_for_every(myRsi7, myRsi14, myRsi28, _f1)
    def myAllRSIsBelow(level=J.undefined, *_args):
        def _f1(_r7=J.undefined, _r14=J.undefined, _r28=J.undefined, *_args):
            return (J.lt(_r28, level) if J.truthy(_t1 := (J.lt(_r14, level) if J.truthy(_t2 := J.lt(_r7, level)) else _t2)) else _t1)
        return G_for_every(myRsi7, myRsi14, myRsi28, _f1)
    def _f1(_r7=J.undefined, _r14=J.undefined, _r28=J.undefined, *_args):
        if ((J.gt(_r7, myOverboughtLevel) and J.gt(_r14, myOverboughtLevel)) and J.gt(_r28, myOverboughtLevel)):
            return myOverboughtLevel
        if ((J.lt(_r7, myOversoldLevel) and J.lt(_r14, myOversoldLevel)) and J.lt(_r28, myOversoldLevel)):
            return myOversoldLevel
        return None
    myShadingSeries = G_for_every(myRsi7, myRsi14, myRsi28, _f1)
    G_paint(myRsi7, J.obj(("color", "blue"), ("name", "RSI 7")))
    G_paint(myRsi14, J.obj(("color", "green"), ("name", "RSI 14")))
    G_paint(myRsi28, J.obj(("color", "red"), ("name", "RSI 28")))
    G_paint(G_horizontal_line(myOverboughtLevel), J.obj(("color", "gray"), ("style", "dotted"), ("name", "Overbought")))
    G_paint(G_horizontal_line(myOversoldLevel), J.obj(("color", "gray"), ("style", "dotted"), ("name", "Oversold")))
    myShadingPainted = G_paint(myShadingSeries, J.obj(("style", "line"), ("hidden", True)))
    G_fill(myShadingPainted, G_paint(G_horizontal_line(myOversoldLevel), J.obj(("hidden", True))), "red", 0.3, "Overbought")
    G_fill(G_paint(G_horizontal_line(myOverboughtLevel), J.obj(("hidden", True))), myShadingPainted, "green", 0.3, "Oversold")
    G_register_signal(myAllRSIsAbove(myOverboughtLevel), "All Overbought")
    G_register_signal(myAllRSIsBelow(myOversoldLevel), "All Oversold")


register_store_indicator(
    script,
    name='triple_rsi_with_overbought_oversold_shading_TS',
    title='Triple RSI with Overbought/Oversold Shading',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/triple-rsi-with-overbought-oversold-shading/',
    position='lower',
    inputs=[{'id': 'overbought_level', 'title': 'Overbought Level', 'type': 'number', 'default': 70}, {'id': 'oversold_level', 'title': 'Oversold Level', 'type': 'number', 'default': 30}],
    outputs=['rsi_7', 'rsi_14', 'rsi_28', 'overbought', 'oversold', 'line_6', 'line_7', 'line_9', 'all_overbought', 'all_oversold'],
    signals=['all_overbought', 'all_oversold'],
    requires=[],
    parity='exact',
)
