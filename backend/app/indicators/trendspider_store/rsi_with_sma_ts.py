"""
RSI with SMA -- TrendSpider store indicator by James Chambers.

Registered as "rsi_with_sma_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/rsi-with-sma/)
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
    G_fill = G["fill"]
    G_horizontal_line = G["horizontal_line"]
    G_input = G["input"]
    G_paint = G["paint"]
    G_rsi = G["rsi"]
    G_sma = G["sma"]
    G_describe_indicator("RSI with SMA", "lower")
    oversold = G_input("Oversold", 30, J.obj(("min", 20), ("max", 100)))
    overbought = G_input("Overbought", 70, J.obj(("min", 20), ("max", 100)))
    mid = G_input("Mid", 50, J.obj(("min", 20), ("max", 100)))
    rsiLength = G_input("RSI Length", 14, J.obj(("min", 1), ("max", 100)))
    smaLength = G_input("SMA Length", 8, J.obj(("min", 1), ("max", 100)))
    rsiValues = G_rsi(G_close, rsiLength)
    smaValues = G_sma(rsiValues, smaLength)
    G_paint(G_horizontal_line(mid), "Mid", "gray")
    G_fill(G_paint(G_horizontal_line(overbought), "Overbought", "gray"), G_paint(G_horizontal_line(oversold), "Oversold", "gray"), "#cfe2f3", 0.2)
    G_paint(rsiValues, "RSI", "black")
    G_paint(smaValues, "RSI SMA", "blue")


register_store_indicator(
    script,
    name='rsi_with_sma_TS',
    title='RSI with SMA',
    developer='James Chambers',
    url='https://trendspider.com/trading-tools-store/indicators/rsi-with-sma/',
    position='lower',
    inputs=[{'id': 'oversold', 'title': 'Oversold', 'type': 'number', 'default': 30}, {'id': 'overbought', 'title': 'Overbought', 'type': 'number', 'default': 70}, {'id': 'mid', 'title': 'Mid', 'type': 'number', 'default': 50}, {'id': 'rsi_length', 'title': 'RSI Length', 'type': 'number', 'default': 14}, {'id': 'sma_length', 'title': 'SMA Length', 'type': 'number', 'default': 8}],
    outputs=['mid', 'overbought', 'oversold', 'rsi', 'rsi_sma'],
    signals=[],
    requires=[],
    parity='exact',
)
