"""
Swing Detector -- TrendSpider store indicator by TrendSpider.

Registered as "swing_detector_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6877e1-swing-detector/)
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
    G_high = G["high"]
    G_input = G["input"]
    G_low = G["low"]
    G_register_signal = G["register_signal"]
    G_series_of = G["series_of"]
    G_describe_indicator("Swing Detector")
    swingType = J.get(G_input, "select")("Swing Type", "Both", J.JSArray(["Bullish", "Bearish", "Both"]))
    myBullishSwing = G_series_of(False)
    myBearishSwing = G_series_of(False)
    i = 2
    while J.lt(i, J.get(G_close, "length")):
        if ((((J.seq(swingType, "Bullish") or J.seq(swingType, "Both")) and J.lt(J.get(G_low, J.sub(i, 1)), J.get(G_low, J.sub(i, 2)))) and J.gt(J.get(G_close, J.sub(i, 1)), J.get(G_low, J.sub(i, 2)))) and J.gt(J.get(G_close, i), J.get(G_high, J.sub(i, 1)))):
            J.set(myBullishSwing, J.sub(i, 2), True)
            J.set(myBullishSwing, J.sub(i, 1), True)
            J.set(myBullishSwing, i, True)
        elif ((((J.seq(swingType, "Bearish") or J.seq(swingType, "Both")) and J.gt(J.get(G_high, J.sub(i, 1)), J.get(G_high, J.sub(i, 2)))) and J.lt(J.get(G_close, J.sub(i, 1)), J.get(G_high, J.sub(i, 2)))) and J.lt(J.get(G_close, i), J.get(G_low, J.sub(i, 1)))):
            J.set(myBearishSwing, J.sub(i, 2), True)
            J.set(myBearishSwing, J.sub(i, 1), True)
            J.set(myBearishSwing, i, True)
        i = J.inc(i)
    def _f1(_bull=J.undefined, _bear=J.undefined, *_args):
        if (J.truthy(_bull) and (J.seq(swingType, "Bullish") or J.seq(swingType, "Both"))):
            return "#39FF14"
        if (J.truthy(_bear) and (J.seq(swingType, "Bearish") or J.seq(swingType, "Both"))):
            return "#FF3131"
        return "grey"
    myCandleColors = G_for_every(myBullishSwing, myBearishSwing, _f1)
    G_color_candles(myCandleColors)
    G_register_signal(myBullishSwing, "Bullish Swing")
    G_register_signal(myBearishSwing, "Bearish Swing")


register_store_indicator(
    script,
    name='swing_detector_TS',
    title='Swing Detector',
    developer='TrendSpider',
    url='https://trendspider.com/trading-tools-store/indicators/6877e1-swing-detector/',
    position='price',
    inputs=[{'id': 'swing_type', 'title': 'Swing Type', 'type': 'select_wide', 'default': 'Both', 'options': ['Bullish', 'Bearish', 'Both']}],
    outputs=['cdl', 'bullish_swing', 'bearish_swing'],
    signals=['bullish_swing', 'bearish_swing'],
    requires=[],
    parity='exact',
)
