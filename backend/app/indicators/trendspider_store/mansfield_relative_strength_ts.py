"""
Mansfield relative strength -- TrendSpider store indicator by TrendSpider Team.

Registered as "mansfield_relative_strength_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/mansfield-relative-strength/)
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
    G_constants = G["constants"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_div = G["div"]
    G_horizontal_line = G["horizontal_line"]
    G_indicators = G["indicators"]
    G_input = G["input"]
    G_interpolate_sparse_series = G["interpolate_sparse_series"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_mult = G["mult"]
    G_paint = G["paint"]
    G_request = G["request"]
    G_sub = G["sub"]
    G_time = G["time"]
    G_describe_indicator("Mansfield Relative Strength", "lower", J.obj(("decimals", 3), ("shortName", "RSM"), ("mainColorInheritFrom", "line")))
    indexSymbol = J.get(G_input, "symbol")("Index")
    dLength = J.get(G_input, "number")("Daily length", 200, J.obj(("min", 1)))
    wLength = J.get(G_input, "number")("Weekly length", 52, J.obj(("min", 1)))
    mLength = J.get(G_input, "number")("Monthly length", 10, J.obj(("min", 1)))
    oLength = J.get(G_input, "number")("Other periods length", 52, J.obj(("min", 1)))
    length = J.undefined
    _t1 = J.get(G_constants, "resolution")
    if J.seq(_t1, "D"):
        _t2 = 0
    elif J.seq(_t1, "W"):
        _t2 = 1
    elif J.seq(_t1, "M"):
        _t2 = 2
    else:
        _t2 = 3
    _c3 = False
    for _once in (0,):
        if _t2 <= 0:
            length = dLength
            break
        if _t2 <= 1:
            length = wLength
            break
        if _t2 <= 2:
            length = mLength
            break
        if _t2 <= 3:
            length = oLength
        pass
    maType = G_input("MA type", "sma", J.get(G_constants, "ma_types"))
    computeMA = J.get(G_indicators, maType)
    higherResolution = J.get(J.obj(("1", "2"), ("2", "4"), ("3", "6"), ("4", "10"), ("5", "10"), ("6", "12"), ("10", "30"), ("12", "30"), ("15", "30"), ("30", "60"), ("45", "90"), ("60", "120"), ("65", "240"), ("90", "240"), ("120", "240"), ("240", "1440"), ("1440", "D"), ("D", "W"), ("W", "M"), ("M", "Q"), ("Q", "Y"), ("Y", "Y")), J.get(G_constants, "resolution"))
    indexData = J.get(G_request, "history")(indexSymbol, higherResolution, J.obj(("ext_session", J.get(G_current, "is_ext_hours"))))
    indexClose = G_land_points_onto_series(J.get(indexData, "time"), J.get(indexData, "close"), G_time, "ge")
    lastClose = J.get(G_interpolate_sparse_series(indexClose, "constant"), J.sub(J.get(G_close, "length"), 1))
    J.set(indexClose, J.sub(J.get(G_close, "length"), 1), lastClose)
    rsd = G_mult(G_div(G_close, G_interpolate_sparse_series(indexClose, "constant")), 100)
    rsdMa = computeMA(rsd, length)
    rsm = G_mult(G_sub(G_div(rsd, rsdMa), 1), 100)
    G_paint(rsm, "Line", "#1e5879")
    zeroLine = G_horizontal_line(0)
    G_paint(zeroLine, "Zero", "#2595f3", "dotted")
    G_color_cloud(rsm, zeroLine, "#9fe2dc", "#ffb2b0")


register_store_indicator(
    script,
    name='mansfield_relative_strength_TS',
    title='Mansfield relative strength',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/mansfield-relative-strength/',
    position='lower',
    inputs=[{'id': 'sym-index', 'title': 'Index', 'type': 'symbol-search', 'default': 'SPY'}, {'id': 'daily_length', 'title': 'Daily length', 'type': 'number', 'default': 200}, {'id': 'weekly_length', 'title': 'Weekly length', 'type': 'number', 'default': 52}, {'id': 'monthly_length', 'title': 'Monthly length', 'type': 'number', 'default': 10}, {'id': 'other_periods_length', 'title': 'Other periods length', 'type': 'number', 'default': 52}, {'id': 'ma_type', 'title': 'MA type', 'type': 'select_wide', 'default': 'sma', 'options': ['ema', 'sma', 'wildma', 'vwma', 'wma', 'hullma', 'kama', 'alma', 'twap']}],
    outputs=['line', 'zero', 'line_3', 'line_4', 'line_6', 'line_7'],
    signals=[],
    requires=['history'],
    parity='exact',
)
