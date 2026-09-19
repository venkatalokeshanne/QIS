"""
Price/Rate-Spread Meta-Ratio -- TrendSpider store indicator by QXEM.

Registered as "price_rate_spread_meta_ratio_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/698a03-price-rate-spread-meta-ratio/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_assert = G["assert"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_div = G["div"]
    G_fill = G["fill"]
    G_for_every = G["for_every"]
    G_horizontal_line = G["horizontal_line"]
    G_input = G["input"]
    G_interpolate_sparse_series = G["interpolate_sparse_series"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_paint = G["paint"]
    G_request = G["request"]
    G_rsi = G["rsi"]
    G_time = G["time"]
    G_describe_indicator("Price/Rate-Spread Meta-Ratio", "lower")
    symbol1 = J.get(G_input, "symbol")("Equity Index", "$SPX")
    symbol2 = J.get(G_input, "symbol")("Rate Index 1 (Numerator)", "$TYX")
    symbol3 = J.get(G_input, "symbol")("Rate Index 2 (Denominator)", "$FVX")
    data1 = J.get(G_request, "history")(symbol1, J.get(G_current, "resolution"))
    G_assert((not J.truthy(J.get(data1, "error"))), J.add(J.add(J.add("Error fetching ", symbol1), " data: "), J.get(data1, "error")))
    data2 = J.get(G_request, "history")(symbol2, J.get(G_current, "resolution"))
    G_assert((not J.truthy(J.get(data2, "error"))), J.add(J.add(J.add("Error fetching ", symbol2), " data: "), J.get(data2, "error")))
    data3 = J.get(G_request, "history")(symbol3, J.get(G_current, "resolution"))
    G_assert((not J.truthy(J.get(data3, "error"))), J.add(J.add(J.add("Error fetching ", symbol3), " data: "), J.get(data3, "error")))
    landed1 = G_land_points_onto_series(J.get(data1, "time"), J.get(data1, "close"), G_time, "ge")
    landed2 = G_land_points_onto_series(J.get(data2, "time"), J.get(data2, "close"), G_time, "ge")
    landed3 = G_land_points_onto_series(J.get(data3, "time"), J.get(data3, "close"), G_time, "ge")
    interpolated1 = G_interpolate_sparse_series(landed1, "constant")
    interpolated2 = G_interpolate_sparse_series(landed2, "constant")
    interpolated3 = G_interpolate_sparse_series(landed3, "constant")
    yieldRatio = G_div(interpolated2, interpolated3)
    myCrashRisk = G_div(interpolated1, yieldRatio)
    rsiLength = J.get(G_input, "number")("RSI Length", 14, J.obj(("min", 1), ("max", 300)))
    myRsi = G_rsi(myCrashRisk, rsiLength)
    overboughtLevel = J.get(G_input, "number")("Overbought Level", 70, J.obj(("min", 1), ("max", 99)))
    oversoldLevel = J.get(G_input, "number")("Oversold Level", 30, J.obj(("min", 1), ("max", 99)))
    neutralLevel = J.get(G_input, "number")("Neutral Level", 50, J.obj(("min", 1), ("max", 99)))
    def _f1(_rsi=J.undefined, *_args):
        if J.ge(_rsi, overboughtLevel):
            return "red"
        if J.le(_rsi, oversoldLevel):
            return "green"
        return "white"
    myRsiColor = G_for_every(myRsi, _f1)
    def _f2(_rsi=J.undefined, *_args):
        return (_rsi if J.ge(_rsi, overboughtLevel) else None)
    overboughtRegion = G_for_every(myRsi, _f2)
    def _f3(_rsi=J.undefined, *_args):
        return (_rsi if J.le(_rsi, oversoldLevel) else None)
    oversoldRegion = G_for_every(myRsi, _f3)
    myRsiLine = G_paint(myRsi, J.obj(("name", "RSI"), ("color", myRsiColor)))
    overboughtLine = G_paint(G_horizontal_line(overboughtLevel), J.obj(("name", "Overbought"), ("color", "grey"), ("style", "dotted")))
    oversoldLine = G_paint(G_horizontal_line(oversoldLevel), J.obj(("name", "Oversold"), ("color", "grey"), ("style", "dotted")))
    G_paint(G_horizontal_line(neutralLevel), J.obj(("name", "Neutral"), ("color", "grey"), ("style", "dotted")))
    G_fill(G_paint(overboughtRegion, J.obj(("style", "line"), ("hidden", True))), overboughtLine, "red", 0.2)
    G_fill(oversoldLine, G_paint(oversoldRegion, J.obj(("style", "line"), ("hidden", True))), "green", 0.2)


register_store_indicator(
    script,
    name='price_rate_spread_meta_ratio_TS',
    title='Price/Rate-Spread Meta-Ratio',
    developer='QXEM',
    url='https://trendspider.com/trading-tools-store/indicators/698a03-price-rate-spread-meta-ratio/',
    position='lower',
    inputs=[{'id': 'sym-equity_index', 'title': 'Equity Index', 'type': 'symbol-search', 'default': '$SPX'}, {'id': 'sym-rate_index_1__numerator_', 'title': 'Rate Index 1 (Numerator)', 'type': 'symbol-search', 'default': '$TYX'}, {'id': 'sym-rate_index_2__denominator_', 'title': 'Rate Index 2 (Denominator)', 'type': 'symbol-search', 'default': '$FVX'}, {'id': 'rsi_length', 'title': 'RSI Length', 'type': 'number', 'default': 14}, {'id': 'overbought_level', 'title': 'Overbought Level', 'type': 'number', 'default': 70}, {'id': 'oversold_level', 'title': 'Oversold Level', 'type': 'number', 'default': 30}, {'id': 'neutral_level', 'title': 'Neutral Level', 'type': 'number', 'default': 50}],
    outputs=['rsi', 'overbought', 'oversold', 'neutral', 'line_6', 'line_8'],
    signals=[],
    requires=['history'],
    parity='exact',
)
