"""
MA Channel -- TrendSpider store indicator by Chirag Patnaik.

Registered as "ma_channel_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6971bc-ma-channel/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_close = G["close"]
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_fill = G["fill"]
    G_high = G["high"]
    G_indicators = G["indicators"]
    G_input = G["input"]
    G_low = G["low"]
    G_paint = G["paint"]
    G_describe_indicator("MA Channel")
    maType = J.get(G_input, "select")("MA Type", "sma", J.get(G_constants, "ma_types"))
    length = J.get(G_input, "number")("Length", 20, J.obj(("min", 1), ("max", 300)))
    computeMA = J.get(G_indicators, maType)
    maHigh = computeMA(G_high, length)
    maClose = computeMA(G_close, length)
    maLow = computeMA(G_low, length)
    G_paint(maHigh, J.obj(("name", "MA High"), ("color", "#2962ff"), ("style", "line")))
    G_paint(maClose, J.obj(("name", "MA Close"), ("color", "#787b86"), ("style", "line")))
    G_paint(maLow, J.obj(("name", "MA Low"), ("color", "#f23645"), ("style", "line")))
    G_fill(G_paint(maHigh, J.obj(("hidden", True))), G_paint(maClose, J.obj(("hidden", True))), "#2962ff", 0.1)
    G_fill(G_paint(maClose, J.obj(("hidden", True))), G_paint(maLow, J.obj(("hidden", True))), "#f23645", 0.1)


register_store_indicator(
    script,
    name='ma_channel_TS',
    title='MA Channel',
    developer='Chirag Patnaik',
    url='https://trendspider.com/trading-tools-store/indicators/6971bc-ma-channel/',
    position='price',
    inputs=[{'id': 'ma_type', 'title': 'MA Type', 'type': 'select_wide', 'default': 'sma', 'options': ['ema', 'sma', 'wildma', 'vwma', 'wma', 'hullma', 'kama', 'alma', 'twap']}, {'id': 'length', 'title': 'Length', 'type': 'number', 'default': 20}],
    outputs=['ma_high', 'ma_close', 'ma_low', 'line_4', 'line_5', 'line_7', 'line_8'],
    signals=[],
    requires=[],
    parity='exact',
)
