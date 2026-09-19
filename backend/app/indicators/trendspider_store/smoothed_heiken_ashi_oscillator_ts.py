"""
Smoothed Heiken Ashi Oscillator -- TrendSpider store indicator by Dan Ushman.

Registered as "smoothed_heiken_ashi_oscillator_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/smoothed-heiken-ashi-oscillator/)
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
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_high = G["high"]
    G_indicators = G["indicators"]
    G_input = G["input"]
    G_low = G["low"]
    G_open = G["open"]
    G_paint = G["paint"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    G_describe_indicator("Smoothed HA Histogram", "lower")
    beforeMAType = G_input("Before MA", "ema", J.get(G_constants, "ma_types"))
    afterMAType = G_input("After MA", "ema", J.get(G_constants, "ma_types"))
    smoothLength = G_input("Before Smooth", 5, J.obj(("min", 1), ("max", 100)))
    afterSmoothLength = G_input("After Smooth", 5, J.obj(("min", 1), ("max", 100)))
    smoothOpen = J.get(G_indicators, beforeMAType)(G_open, smoothLength)
    smoothHigh = J.get(G_indicators, beforeMAType)(G_high, smoothLength)
    smoothLow = J.get(G_indicators, beforeMAType)(G_low, smoothLength)
    smoothClose = J.get(G_indicators, beforeMAType)(G_close, smoothLength)
    haOpenSeries = G_series_of(None)
    haHighSeries = G_series_of(None)
    haLowSeries = G_series_of(None)
    haCloseSeries = G_series_of(None)
    candleIndex = 0
    while J.lt(candleIndex, J.get(G_time, "length")):
        haClose = J.div(J.add(J.add(J.add(J.get(smoothOpen, candleIndex), J.get(smoothHigh, candleIndex)), J.get(smoothLow, candleIndex)), J.get(smoothClose, candleIndex)), 4)
        haOpen = (J.div(J.add(J.get(haOpenSeries, J.sub(candleIndex, 1)), J.get(haCloseSeries, J.sub(candleIndex, 1))), 2) if J.truthy(J.get(haOpenSeries, J.sub(candleIndex, 1))) else J.div(J.add(J.get(smoothOpen, candleIndex), J.get(smoothClose, candleIndex)), 2))
        haHigh = J.get(G_Math, "max")(J.get(smoothHigh, candleIndex), haClose, haOpen)
        haLow = J.get(G_Math, "min")(J.get(smoothLow, candleIndex), haClose, haOpen)
        J.set(haOpenSeries, candleIndex, haOpen)
        J.set(haCloseSeries, candleIndex, haClose)
        J.set(haHighSeries, candleIndex, haHigh)
        J.set(haLowSeries, candleIndex, haLow)
        candleIndex = J.add(candleIndex, 1)
    haSmoothOpenSeries = J.get(G_indicators, afterMAType)(haOpenSeries, afterSmoothLength)
    haSmoothCloseSeries = J.get(G_indicators, afterMAType)(haCloseSeries, afterSmoothLength)
    histogram = G_series_of(None)
    i = 0
    while J.lt(i, J.get(haSmoothOpenSeries, "length")):
        if J.gt(J.get(haSmoothCloseSeries, i), J.get(haSmoothOpenSeries, i)):
            J.set(histogram, i, 1)
        else:
            J.set(histogram, i, (-1))
        i = J.inc(i)
    def _f1(value=J.undefined, *_args):
        return ("#eeeeee" if J.gt(value, 0) else "#eeeeee")
    G_paint(histogram, J.obj(("style", "histogram"), ("color", J.get(histogram, "map")(_f1)), ("width", 2)))


register_store_indicator(
    script,
    name='smoothed_heiken_ashi_oscillator_TS',
    title='Smoothed Heiken Ashi Oscillator',
    developer='Dan Ushman',
    url='https://trendspider.com/trading-tools-store/indicators/smoothed-heiken-ashi-oscillator/',
    position='lower',
    inputs=[{'id': 'before_ma', 'title': 'Before MA', 'type': 'select_wide', 'default': 'ema', 'options': ['ema', 'sma', 'wildma', 'vwma', 'wma', 'hullma', 'kama', 'alma', 'twap']}, {'id': 'after_ma', 'title': 'After MA', 'type': 'select_wide', 'default': 'ema', 'options': ['ema', 'sma', 'wildma', 'vwma', 'wma', 'hullma', 'kama', 'alma', 'twap']}, {'id': 'before_smooth', 'title': 'Before Smooth', 'type': 'number', 'default': 5}, {'id': 'after_smooth', 'title': 'After Smooth', 'type': 'number', 'default': 5}],
    outputs=['line_1'],
    signals=[],
    requires=[],
    parity='exact',
)
