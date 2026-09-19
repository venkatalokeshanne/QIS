"""
Golden / Death Cross Painter -- TrendSpider store indicator by TrendSpider Team.

Registered as "golden_death_cross_painter_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/golden-death-cross-painter/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_close = G["close"]
    G_color_candles = G["color_candles"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_input = G["input"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_series_of = G["series_of"]
    G_sma = G["sma"]
    G_describe_indicator("Golden/Death Cross Painter")
    fastPeriod = J.get(G_input, "number")("Fast SMA Period", 50, J.obj(("min", 1)))
    slowPeriod = J.get(G_input, "number")("Slow SMA Period", 200, J.obj(("min", 1)))
    myGoldenColor = J.get(G_input, "color")("Golden Cross Color", "gold")
    myDeathColor = J.get(G_input, "color")("Death Cross Color", "red")
    myNeutralColor = J.get(G_input, "color")("Neutral Color", "grey")
    fastSMA = G_sma(G_close, fastPeriod)
    slowSMA = G_sma(G_close, slowPeriod)
    G_paint(fastSMA, J.obj(("name", "Fast SMA"), ("color", "blue")))
    G_paint(slowSMA, J.obj(("name", "Slow SMA"), ("color", "purple")))
    myLastCrossState = "none"
    def myGetCrossState(fast=J.undefined, slow=J.undefined, *_args):
        if J.gt(fast, slow):
            return "golden"
        if J.lt(fast, slow):
            return "death"
        return "none"
    myGoldenSignal = G_series_of(False)
    myDeathSignal = G_series_of(False)
    myNeutralSignal = G_series_of(True)
    def _f1(c=J.undefined, f=J.undefined, s=J.undefined, prevColor=J.undefined, i=J.undefined, *_args):
        nonlocal myLastCrossState
        myCurrentCrossState = myGetCrossState(f, s)
        if J.sne(myCurrentCrossState, myLastCrossState):
            myLastCrossState = myCurrentCrossState
        if ((J.seq(myLastCrossState, "golden") and J.gt(c, f)) and J.gt(c, s)):
            J.set(myGoldenSignal, i, True)
            J.set(myDeathSignal, i, False)
            J.set(myNeutralSignal, i, False)
            return myGoldenColor
        if ((J.seq(myLastCrossState, "death") and J.lt(c, f)) and J.lt(c, s)):
            J.set(myGoldenSignal, i, False)
            J.set(myDeathSignal, i, True)
            J.set(myNeutralSignal, i, False)
            return myDeathColor
        J.set(myGoldenSignal, i, False)
        J.set(myDeathSignal, i, False)
        J.set(myNeutralSignal, i, True)
        return myNeutralColor
    myCandleColors = G_for_every(G_close, fastSMA, slowSMA, _f1)
    G_register_signal(myGoldenSignal, "Golden Cross Bullish")
    G_register_signal(myDeathSignal, "Death Cross Bearish")
    G_register_signal(myNeutralSignal, "Neutral")
    G_color_candles(myCandleColors)


register_store_indicator(
    script,
    name='golden_death_cross_painter_TS',
    title='Golden / Death Cross Painter',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/golden-death-cross-painter/',
    position='price',
    inputs=[{'id': 'fast_sma_period', 'title': 'Fast SMA Period', 'type': 'number', 'default': 50}, {'id': 'slow_sma_period', 'title': 'Slow SMA Period', 'type': 'number', 'default': 200}, {'id': 'golden_cross_color', 'title': 'Golden Cross Color', 'type': 'color', 'default': 'gold'}, {'id': 'death_cross_color', 'title': 'Death Cross Color', 'type': 'color', 'default': 'red'}, {'id': 'neutral_color', 'title': 'Neutral Color', 'type': 'color', 'default': 'grey'}],
    outputs=['fast_sma', 'slow_sma', 'golden_cross_bullish', 'death_cross_bearish', 'neutral', 'cdl'],
    signals=['golden_cross_bullish', 'death_cross_bearish', 'neutral'],
    requires=[],
    parity='exact',
)
