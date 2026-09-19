"""
Pivot High and Low -- TrendSpider store indicator by Mohamed Algendy.

Registered as "pivot_high_and_low_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/69cd72-pivot-high-and-low/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_describe_indicator = G["describe_indicator"]
    G_high = G["high"]
    G_input = G["input"]
    G_low = G["low"]
    G_paint = G["paint"]
    G_pivot_high = G["pivot_high"]
    G_pivot_low = G["pivot_low"]
    G_describe_indicator("Pivot High and Low")
    leftBars = J.get(G_input, "number")("Left Bars", 5, J.obj(("min", 1), ("max", 50)))
    rightBars = J.get(G_input, "number")("Right Bars", 5, J.obj(("min", 1), ("max", 50)))
    pivotHighs = G_pivot_high(G_high, leftBars, rightBars)
    pivotLows = G_pivot_low(G_low, leftBars, rightBars)
    G_paint(pivotHighs, J.obj(("style", "labels_above"), ("color", "#2ca599"), ("name", "Pivot High"), ("thickness", 10)))
    G_paint(pivotLows, J.obj(("style", "labels_below"), ("color", "#ee5451"), ("name", "Pivot Low"), ("thickness", 10)))


register_store_indicator(
    script,
    name='pivot_high_and_low_TS',
    title='Pivot High and Low',
    developer='Mohamed Algendy',
    url='https://trendspider.com/trading-tools-store/indicators/69cd72-pivot-high-and-low/',
    position='price',
    inputs=[{'id': 'left_bars', 'title': 'Left Bars', 'type': 'number', 'default': 5}, {'id': 'right_bars', 'title': 'Right Bars', 'type': 'number', 'default': 5}],
    outputs=['pivot_high', 'pivot_low'],
    signals=[],
    requires=[],
    parity='exact',
)
