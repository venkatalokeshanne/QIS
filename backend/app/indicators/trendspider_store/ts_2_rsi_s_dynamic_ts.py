"""
2 RSI's Dynamic -- TrendSpider store indicator by James Chambers.

Registered as "2_rsi_s_dynamic_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/2-rsis-dyanmic/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_input = G["input"]
    G_interpolate_sparse_series = G["interpolate_sparse_series"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_paint = G["paint"]
    G_request = G["request"]
    G_rsi = G["rsi"]
    G_time = G["time"]
    G_describe_indicator("2 RSIs Dynamic", "lower")
    symbol1 = J.get(G_input, "symbol")("Symbol1 (Custom)", "SPY")
    symbol2 = J.get(G_current, "ticker")
    rsiLength = J.get(G_input, "number")("RSI Length", 14, J.obj(("min", 1), ("max", 100)))
    data1 = J.get(G_request, "history")(symbol1, J.get(G_current, "resolution"))
    data2 = J.get(G_request, "history")(symbol2, J.get(G_current, "resolution"))
    rsi1 = G_rsi(J.get(data1, "close"), rsiLength)
    G_paint(G_interpolate_sparse_series(G_land_points_onto_series(J.get(data1, "time"), rsi1, G_time), "constant"), J.obj(("name", "RSI1 (Custom)"), ("color", "red")))
    rsi2 = G_rsi(J.get(data2, "close"), rsiLength)
    G_paint(G_interpolate_sparse_series(G_land_points_onto_series(J.get(data2, "time"), rsi2, G_time), "constant"), J.obj(("name", "RSI2 (Chart Symbol)"), ("color", "blue")))


register_store_indicator(
    script,
    name='2_rsi_s_dynamic_TS',
    title="2 RSI's Dynamic",
    developer='James Chambers',
    url='https://trendspider.com/trading-tools-store/indicators/2-rsis-dyanmic/',
    position='lower',
    inputs=[{'id': 'sym-symbol1__custom_', 'title': 'Symbol1 (Custom)', 'type': 'symbol-search', 'default': 'SPY'}, {'id': 'rsi_length', 'title': 'RSI Length', 'type': 'number', 'default': 14}],
    outputs=['rsi1__custom_', 'rsi2__chart_symbol_'],
    signals=[],
    requires=['history'],
    parity='exact',
)
