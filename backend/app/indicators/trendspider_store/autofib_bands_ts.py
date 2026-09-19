"""
AutoFib Bands -- TrendSpider store indicator by Chirag Patnaik.

Registered as "autofib_bands_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68a1fd-autofib-bands/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_add = G["add"]
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_fill = G["fill"]
    G_highest = G["highest"]
    G_input = G["input"]
    G_lowest = G["lowest"]
    G_mult = G["mult"]
    G_paint = G["paint"]
    G_series_of = G["series_of"]
    G_sub = G["sub"]
    G_describe_indicator("AutoFib Bands")
    fiblength = J.get(G_input, "number")("Fibonacci Lookback Length", 265, J.obj(("min", 1)))
    maxr = G_highest(G_close, fiblength)
    minr = G_lowest(G_close, fiblength)
    ranr = G_sub(maxr, minr)
    Level_100 = maxr
    Level_764 = G_sub(maxr, G_mult(G_series_of(0.236), ranr))
    Level_618 = G_sub(maxr, G_mult(G_series_of(0.382), ranr))
    Level_500 = G_sub(maxr, G_mult(G_series_of(0.5), ranr))
    Level_382 = G_add(minr, G_mult(G_series_of(0.382), ranr))
    Level_236 = G_add(minr, G_mult(G_series_of(0.236), ranr))
    Level_0 = minr
    Level_100_painted = G_paint(Level_100, J.obj(("color", "black"), ("name", "Level 100")))
    Level_764_painted = G_paint(Level_764, J.obj(("color", "#3399FF"), ("name", "Level 76.4")))
    Level_618_painted = G_paint(Level_618, J.obj(("color", "blue"), ("name", "Level 61.8")))
    Level_500_painted = G_paint(Level_500, J.obj(("color", "lime"), ("name", "Level 50.0")))
    Level_382_painted = G_paint(Level_382, J.obj(("color", "green"), ("name", "Level 38.2")))
    Level_236_painted = G_paint(Level_236, J.obj(("color", "red"), ("name", "Level 23.6")))
    Level_0_painted = G_paint(Level_0, J.obj(("color", "black"), ("name", "Level 0")))
    G_fill(Level_100_painted, Level_764_painted, "red", 0.1)
    G_fill(Level_764_painted, Level_618_painted, "#3399FF", 0.1)
    G_fill(Level_618_painted, Level_500_painted, "lime", 0.1)
    G_fill(Level_500_painted, Level_382_painted, "lime", 0.1)
    G_fill(Level_382_painted, Level_236_painted, "#3399FF", 0.1)
    G_fill(Level_236_painted, Level_0_painted, "red", 0.1)


register_store_indicator(
    script,
    name='autofib_bands_TS',
    title='AutoFib Bands',
    developer='Chirag Patnaik',
    url='https://trendspider.com/trading-tools-store/indicators/68a1fd-autofib-bands/',
    position='price',
    inputs=[{'id': 'fibonacci_lookback_length', 'title': 'Fibonacci Lookback Length', 'type': 'number', 'default': 265}],
    outputs=['level_100', 'level_76_4', 'level_61_8', 'level_50_0', 'level_38_2', 'level_23_6', 'level_0'],
    signals=[],
    requires=[],
    parity='exact',
)
