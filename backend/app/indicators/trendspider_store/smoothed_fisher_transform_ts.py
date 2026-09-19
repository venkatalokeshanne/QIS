"""
Smoothed Fisher Transform -- TrendSpider store indicator by James Chambers.

Registered as "smoothed_fisher_transform_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/smoothed-fisher-transform/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_add = G["add"]
    G_describe_indicator = G["describe_indicator"]
    G_div = G["div"]
    G_ema = G["ema"]
    G_high = G["high"]
    G_input = G["input"]
    G_low = G["low"]
    G_mult = G["mult"]
    G_paint = G["paint"]
    G_sliding_window_function = G["sliding_window_function"]
    G_sub = G["sub"]
    G_describe_indicator("Smoothed Fisher Transform", "lower", J.obj(("decimals", 3), ("shortName", "SFT")))
    rangePeriods = G_input("Range Periods", 30, J.obj(("min", 1), ("max", 200)))
    priceSmoothing = G_input("Price Smoothing", 0.3, J.obj(("min", 0), ("max", 1)))
    indexSmoothing = G_input("Index Smoothing", 0.3, J.obj(("min", 0), ("max", 1)))
    emaLength = G_input("EMA Length", 20, J.obj(("min", 1), ("max", 100)))
    emaLength2 = G_input("EMA Length 2", 5, J.obj(("min", 1), ("max", 100)))
    def _f1(values=J.undefined, *_args):
        return J.get(G_Math, "max")(*J.spread(values))
    highestHigh = G_sliding_window_function(G_high, rangePeriods, _f1)
    def _f2(values=J.undefined, *_args):
        return J.get(G_Math, "min")(*J.spread(values))
    lowestLow = G_sliding_window_function(G_low, rangePeriods, _f2)
    midPrice = G_div(G_add(G_high, G_low), 2)
    greatestRange = G_sub(highestHigh, lowestLow)
    priceLocation = G_sub(G_div(G_mult(G_sub(midPrice, lowestLow), 2), greatestRange), 1)
    def _f3(window=J.undefined, *_args):
        extMapBuffer = J.add(J.mul(priceSmoothing, J.get(window, 1)), J.mul(J.sub(1, priceSmoothing), J.get(window, 0)))
        return J.get(G_Math, "min")(J.get(G_Math, "max")(extMapBuffer, (-0.99)), 0.99)
    smoothedLocation = G_sliding_window_function(priceLocation, 2, _f3)
    def _f4(values=J.undefined, *_args):
        return J.get(G_Math, "log")(J.div(J.add(1, J.get(values, 0)), J.sub(1, J.get(values, 0))))
    fishIndex = G_sliding_window_function(smoothedLocation, 1, _f4)
    def _f5(window=J.undefined, *_args):
        return J.add(J.mul(indexSmoothing, J.get(window, 1)), J.mul(J.sub(1, indexSmoothing), J.get(window, 0)))
    smoothedFish = G_sliding_window_function(fishIndex, 2, _f5)
    ema1 = G_ema(smoothedFish, emaLength)
    ema2 = G_ema(smoothedFish, emaLength2)
    G_paint(ema1, "EMA 1", "#00FFFF")
    G_paint(ema2, "EMA 2", "#FFFFFF")
    G_paint(smoothedFish, "Fish Histogram", ("green" if J.gt(J.get(smoothedFish, J.sub(J.get(smoothedFish, "length"), 1)), 0) else "red"), "histogram")


register_store_indicator(
    script,
    name='smoothed_fisher_transform_TS',
    title='Smoothed Fisher Transform',
    developer='James Chambers',
    url='https://trendspider.com/trading-tools-store/indicators/smoothed-fisher-transform/',
    position='lower',
    inputs=[{'id': 'range_periods', 'title': 'Range Periods', 'type': 'number', 'default': 30}, {'id': 'price_smoothing', 'title': 'Price Smoothing', 'type': 'number', 'default': 0.3}, {'id': 'index_smoothing', 'title': 'Index Smoothing', 'type': 'number', 'default': 0.3}, {'id': 'ema_length', 'title': 'EMA Length', 'type': 'number', 'default': 20}, {'id': 'ema_length_2', 'title': 'EMA Length 2', 'type': 'number', 'default': 5}],
    outputs=['ema_1', 'ema_2', 'fish_histogram'],
    signals=[],
    requires=[],
    parity='exact',
)
