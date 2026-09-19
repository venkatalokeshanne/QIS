"""
Highest Volume Candle -- TrendSpider store indicator by TrendSpider Team.

Registered as "highest_volume_candle_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/highest-volume-candle/)
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
    G_close = G["close"]
    G_color_candles = G["color_candles"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_input = G["input"]
    G_paint = G["paint"]
    G_paint_label_at_line = G["paint_label_at_line"]
    G_register_signal = G["register_signal"]
    G_volume = G["volume"]
    G_describe_indicator("Highest Volume Candle")
    lookback = J.get(G_input, "number")("Lookback Period", 50, J.obj(("min", 1)))
    def findHighestVolumeIndex(volumeSeries=J.undefined, length=J.undefined, *_args):
        maxVolume = J.neg(G_Infinity)
        maxIndex = (-1)
        i = J.sub(J.get(volumeSeries, "length"), length)
        while J.lt(i, J.get(volumeSeries, "length")):
            if J.gt(J.get(volumeSeries, i), maxVolume):
                maxVolume = J.get(volumeSeries, i)
                maxIndex = i
            i = J.inc(i)
        return maxIndex
    highestVolumeIndex = findHighestVolumeIndex(G_volume, J.get(G_Math, "min")(lookback, J.get(G_volume, "length")))
    def _f1(_c=J.undefined, _p=J.undefined, i=J.undefined, *_args):
        return ("yellow" if J.seq(i, highestVolumeIndex) else None)
    candleColors = G_for_every(G_close, _f1)
    G_color_candles(candleColors)
    G_paint_label_at_line(G_paint(G_close, J.obj(("hidden", True))), highestVolumeIndex, "Highest Volume", J.obj(("color", "black"), ("background_color", "yellow")))
    def _f2(_c=J.undefined, _p=J.undefined, i=J.undefined, *_args):
        return (1 if J.seq(i, highestVolumeIndex) else 0)
    highestVolumeSignal = G_for_every(G_close, _f2)
    G_register_signal(highestVolumeSignal, "Highest Volume Candle")


register_store_indicator(
    script,
    name='highest_volume_candle_TS',
    title='Highest Volume Candle',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/highest-volume-candle/',
    position='price',
    inputs=[{'id': 'lookback_period', 'title': 'Lookback Period', 'type': 'number', 'default': 50}],
    outputs=['cdl', 'line_2', 'highest_volume_candle'],
    signals=['highest_volume_candle'],
    requires=[],
    parity='exact',
)
