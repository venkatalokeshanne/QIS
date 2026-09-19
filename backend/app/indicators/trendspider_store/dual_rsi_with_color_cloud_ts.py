"""
Dual RSI with Color Cloud -- TrendSpider store indicator by James Chambers.

Registered as "dual_rsi_with_color_cloud_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/dual-rsi-with-color-cloud/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_close = G["close"]
    G_color_cloud = G["color_cloud"]
    G_describe_indicator = G["describe_indicator"]
    G_input = G["input"]
    G_paint = G["paint"]
    G_rsi = G["rsi"]
    G_describe_indicator("Dual RSI with Color Cloud", "lower")
    rsiLength14 = G_input("RSI Length (14)", 14, J.obj(("min", 1), ("max", 100)))
    rsiLength50 = G_input("RSI Length (50)", 50, J.obj(("min", 1), ("max", 100)))
    rsi14 = G_rsi(G_close, rsiLength14)
    rsi50 = G_rsi(G_close, rsiLength50)
    paintedRsi14 = G_paint(rsi14, J.obj(("style", "line"), ("color", "blue"), ("name", "RSI (14)")))
    paintedRsi50 = G_paint(rsi50, J.obj(("style", "line"), ("color", "black"), ("name", "RSI (50)")))
    G_color_cloud(rsi14, rsi50, "green", "red")


register_store_indicator(
    script,
    name='dual_rsi_with_color_cloud_TS',
    title='Dual RSI with Color Cloud',
    developer='James Chambers',
    url='https://trendspider.com/trading-tools-store/indicators/dual-rsi-with-color-cloud/',
    position='lower',
    inputs=[{'id': 'rsi_length__14_', 'title': 'RSI Length (14)', 'type': 'number', 'default': 14}, {'id': 'rsi_length__50_', 'title': 'RSI Length (50)', 'type': 'number', 'default': 50}],
    outputs=['rsi__14_', 'rsi__50_', 'line_3', 'line_4', 'line_6', 'line_7'],
    signals=[],
    requires=[],
    parity='exact',
)
