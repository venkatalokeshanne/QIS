"""
Balloon Raindrop Painter -- TrendSpider store indicator by TrendSpider Team.

Registered as "balloon_raindrop_painter_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/volatility-based-stop-loss-2/)
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
    G_volume = G["volume"]
    G_describe_indicator("Balloon Raindrop Painter")
    volumeThreshold = J.get(G_input, "number")("Volume Imbalance Threshold", 2, J.obj(("min", 1.1), ("max", 10)))
    def calculateVWAP(high=J.undefined, low=J.undefined, volume=J.undefined, *_args):
        avgPrice = J.div(J.add(high, low), 2)
        return J.div(J.mul(avgPrice, volume), volume)
    def _f1(h=J.undefined, l=J.undefined, v=J.undefined, *_args):
        return calculateVWAP(h, l, v)
    myVwap = G_for_every(G_high, G_low, G_volume, _f1)
    def _f2(c=J.undefined, l=J.undefined, v=J.undefined, vol=J.undefined, *_args):
        return (J.div(J.mul(vol, J.sub(v, l)), J.sub(c, l)) if J.gt(v, l) else vol)
    lowVolume = G_for_every(G_close, G_low, myVwap, G_volume, _f2)
    def _f3(c=J.undefined, h=J.undefined, v=J.undefined, vol=J.undefined, *_args):
        return (J.div(J.mul(vol, J.sub(h, v)), J.sub(h, c)) if J.lt(v, h) else vol)
    highVolume = G_for_every(G_close, G_high, myVwap, G_volume, _f3)
    def _f4(lv=J.undefined, hv=J.undefined, *_args):
        if J.gt(hv, J.mul(lv, volumeThreshold)):
            return "#00FF00"
        elif J.gt(lv, J.mul(hv, volumeThreshold)):
            return "#FF0000"
        else:
            return "#808080"
    candleColor = G_for_every(lowVolume, highVolume, _f4)
    G_color_candles(candleColor)
    def _f5(lv=J.undefined, hv=J.undefined, *_args):
        return (1 if J.gt(hv, J.mul(lv, volumeThreshold)) else 0)
    bullishBalloon = G_for_every(lowVolume, highVolume, _f5)
    def _f6(lv=J.undefined, hv=J.undefined, *_args):
        return (1 if J.gt(lv, J.mul(hv, volumeThreshold)) else 0)
    bearishBalloon = G_for_every(lowVolume, highVolume, _f6)
    G_register_signal(bullishBalloon, "Bullish Balloon")
    G_register_signal(bearishBalloon, "Bearish Balloon")


register_store_indicator(
    script,
    name='balloon_raindrop_painter_TS',
    title='Balloon Raindrop Painter',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/volatility-based-stop-loss-2/',
    position='price',
    inputs=[{'id': 'volume_imbalance_threshold', 'title': 'Volume Imbalance Threshold', 'type': 'number', 'default': 2}],
    outputs=['cdl', 'bullish_balloon', 'bearish_balloon'],
    signals=['bullish_balloon', 'bearish_balloon'],
    requires=[],
    parity='exact',
)
