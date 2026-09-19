"""
Dorsey relative strength -- TrendSpider store indicator by TrendSpider Team.

Registered as "dorsey_relative_strength_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/dorsey-relative-strength/)
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
    G_div = G["div"]
    G_input = G["input"]
    G_interpolate_sparse_series = G["interpolate_sparse_series"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_mult = G["mult"]
    G_paint = G["paint"]
    G_request = G["request"]
    G_time = G["time"]
    G_describe_indicator("Dorsey Relative Strength", "lower", J.obj(("decimals", 3), ("shortName", "RSD")))
    indexSymbol = J.get(G_input, "symbol")("Index")
    higherResolution = J.get(J.obj(("1", "2"), ("2", "4"), ("3", "6"), ("4", "10"), ("5", "10"), ("6", "12"), ("10", "30"), ("12", "30"), ("15", "30"), ("30", "60"), ("45", "90"), ("60", "120"), ("65", "240"), ("90", "240"), ("120", "240"), ("240", "1440"), ("1440", "D"), ("D", "W"), ("W", "M"), ("M", "Q"), ("Q", "Y"), ("Y", "Y")), J.get(G_constants, "resolution"))
    indexData = J.get(G_request, "history")(indexSymbol, higherResolution, J.obj(("ext_session", J.eq(J.get(J.get(G_constants, "session"), "lengthMinutes"), J.get(J.get(G_constants, "ext_session"), "lengthMinutes")))))
    indexClose = G_land_points_onto_series(J.get(indexData, "time"), J.get(indexData, "close"), G_time, "ge")
    rsd = G_mult(G_div(G_close, G_interpolate_sparse_series(indexClose, "constant")), 100)
    G_paint(rsd, J.obj(("name", "Line"), ("color", "grey"), ("thickness", 5)))


register_store_indicator(
    script,
    name='dorsey_relative_strength_TS',
    title='Dorsey relative strength',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/dorsey-relative-strength/',
    position='lower',
    inputs=[{'id': 'sym-index', 'title': 'Index', 'type': 'symbol-search', 'default': 'SPY'}],
    outputs=['line'],
    signals=[],
    requires=['history'],
    parity='exact',
)
