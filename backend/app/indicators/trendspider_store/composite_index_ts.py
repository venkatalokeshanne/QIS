"""
Composite Index -- TrendSpider store indicator by TrendSpider Team.

Registered as "composite_index_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/composite-index/)
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
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_input = G["input"]
    G_momentum = G["momentum"]
    G_paint = G["paint"]
    G_prices = G["prices"]
    G_rsi = G["rsi"]
    G_sma = G["sma"]
    G_describe_indicator("Composite index", "lower")
    priceSource = G_input("Price source", "close", J.get(G_constants, "price_source_options"))
    rsiLength = G_input("RSI Length", 14)
    rsiMomLength = G_input("RSI Momentum Length", 9)
    rsiMaLength = G_input("RSI MA Length", 3)
    maLength = G_input("SMA Length", 3)
    fastLength = G_input("Fast Length", 13)
    slowLength = G_input("Slow Length", 33)
    price = J.get(G_prices, priceSource)
    rsiMo9 = G_momentum(G_rsi(price, rsiLength), rsiMomLength)
    rsi3 = G_sma(G_rsi(G_close, rsiMaLength), maLength)
    indicatorLine = G_add(rsiMo9, rsi3)
    G_paint(indicatorLine, "Plot1", "#ff0000")
    G_paint(G_sma(indicatorLine, fastLength), "Plot2", "#008000")
    G_paint(G_sma(indicatorLine, slowLength), "Plot3", "#ff7f00")


register_store_indicator(
    script,
    name='composite_index_TS',
    title='Composite Index',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/composite-index/',
    position='lower',
    inputs=[{'id': 'price_source', 'title': 'Price source', 'type': 'select_wide', 'default': 'close', 'options': ['open', 'high', 'low', 'close', 'hl2', 'oc2', 'hlc3', 'ohlc4', 'wclose']}, {'id': 'rsi_length', 'title': 'RSI Length', 'type': 'number', 'default': 14}, {'id': 'rsi_momentum_length', 'title': 'RSI Momentum Length', 'type': 'number', 'default': 9}, {'id': 'rsi_ma_length', 'title': 'RSI MA Length', 'type': 'number', 'default': 3}, {'id': 'sma_length', 'title': 'SMA Length', 'type': 'number', 'default': 3}, {'id': 'fast_length', 'title': 'Fast Length', 'type': 'number', 'default': 13}, {'id': 'slow_length', 'title': 'Slow Length', 'type': 'number', 'default': 33}],
    outputs=['plot1', 'plot2', 'plot3'],
    signals=[],
    requires=[],
    parity='exact',
)
