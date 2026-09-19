"""
Normalized Range Crossover -- TrendSpider store indicator by Connor Robbins.

Registered as "normalized_range_crossover_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68abc8-normalized-range-crossover/)
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
    G_div = G["div"]
    G_high = G["high"]
    G_highest = G["highest"]
    G_input = G["input"]
    G_low = G["low"]
    G_lowest = G["lowest"]
    G_mult = G["mult"]
    G_paint = G["paint"]
    G_sma = G["sma"]
    G_sub = G["sub"]
    G_describe_indicator("Normalized Range Crossover", "lower")
    twoWeekPeriod = J.get(G_input, "number")("Trading Days in Period", 10, J.obj(("min", 1), ("max", 100)))
    highestHigh = G_highest(G_high, twoWeekPeriod)
    lowestLow = G_lowest(G_low, twoWeekPeriod)
    range = G_sub(highestHigh, lowestLow)
    normalizedRange = G_div(range, G_close)
    normalizedRangePercentage = G_mult(normalizedRange, 100)
    smaPeriod = J.get(G_input, "number")("SMA Period", 14, J.obj(("min", 1), ("max", 100)))
    normalizedRangeSMA = G_sma(normalizedRangePercentage, smaPeriod)
    G_paint(normalizedRangePercentage, J.obj(("name", "Normalized Range %"), ("color", "cyan"), ("style", "dotted")))
    G_paint(normalizedRangeSMA, J.obj(("name", "SMA of Normalized Range %"), ("color", "magenta")))


register_store_indicator(
    script,
    name='normalized_range_crossover_TS',
    title='Normalized Range Crossover',
    developer='Connor Robbins',
    url='https://trendspider.com/trading-tools-store/indicators/68abc8-normalized-range-crossover/',
    position='lower',
    inputs=[{'id': 'trading_days_in_period', 'title': 'Trading Days in Period', 'type': 'number', 'default': 10}, {'id': 'sma_period', 'title': 'SMA Period', 'type': 'number', 'default': 14}],
    outputs=['normalized_range__', 'sma_of_normalized_range__'],
    signals=[],
    requires=[],
    parity='exact',
)
