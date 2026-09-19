"""
ANTR Crossover -- TrendSpider store indicator by Peter Robbins.

Registered as "antr_crossover_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68abbf-antr-crossover/)
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
    G_input = G["input"]
    G_low = G["low"]
    G_mult = G["mult"]
    G_paint = G["paint"]
    G_sma = G["sma"]
    G_sub = G["sub"]
    G_describe_indicator("ANTR Crossover", "lower")
    smaLengthLong = J.get(G_input, "number")("MA Length Long", 20, J.obj(("min", 1)))
    smaLengthShort = J.get(G_input, "number")("MA Length Short", 5, J.obj(("min", 1)))
    normalizedATR = G_mult(G_div(G_sub(G_high, G_low), G_close), 100)
    smantrLong = G_sma(normalizedATR, smaLengthLong)
    smantrShort = G_sma(normalizedATR, smaLengthShort)
    G_paint(smantrLong, J.obj(("name", "ANTR Long %"), ("color", "cyan")))
    G_paint(smantrShort, J.obj(("name", "ANTR Short %"), ("color", "white")))


register_store_indicator(
    script,
    name='antr_crossover_TS',
    title='ANTR Crossover',
    developer='Peter Robbins',
    url='https://trendspider.com/trading-tools-store/indicators/68abbf-antr-crossover/',
    position='lower',
    inputs=[{'id': 'ma_length_long', 'title': 'MA Length Long', 'type': 'number', 'default': 20}, {'id': 'ma_length_short', 'title': 'MA Length Short', 'type': 'number', 'default': 5}],
    outputs=['antr_long__', 'antr_short__'],
    signals=[],
    requires=[],
    parity='exact',
)
