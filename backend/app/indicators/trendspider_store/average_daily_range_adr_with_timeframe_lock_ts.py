"""
Average Daily Range (ADR) with Timeframe Lock -- TrendSpider store indicator by TrendSpider Team.

Registered as "average_daily_range_adr_with_timeframe_lock_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/average-daily-range-adr-with-timeframe-lock/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_add = G["add"]
    G_assert = G["assert"]
    G_close = G["close"]
    G_constants = G["constants"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_input = G["input"]
    G_interpolate_sparse_series = G["interpolate_sparse_series"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_paint = G["paint"]
    G_paint_label_at_line = G["paint_label_at_line"]
    G_request = G["request"]
    G_sma = G["sma"]
    G_sub = G["sub"]
    G_time = G["time"]
    G_describe_indicator("Average Daily Range (ADR) with Timeframe Lock")
    adrPeriod = J.get(G_input, "number")("ADR Period", 14, J.obj(("min", 1)))
    adrHighColor = J.get(G_input, "color")("ADR High Color", "green")
    adrLowColor = J.get(G_input, "color")("ADR Low Color", "red")
    lineStyle = J.get(G_input, "select")("Line Style", "line", J.JSArray(["line", "dotted", "ladder"]))
    showLabels = J.get(G_input, "boolean")("Show ADR Labels", True)
    lockedTimeframe = J.get(G_input, "select")("Locked Timeframe", "D", J.get(G_constants, "time_frames"))
    def calculateADR(high=J.undefined, low=J.undefined, length=J.undefined, *_args):
        ranges = G_sub(high, low)
        return G_sma(ranges, length)
    lockedData = J.get(G_request, "history")(J.get(G_current, "ticker"), lockedTimeframe)
    G_assert((not J.truthy(J.get(lockedData, "error"))), J.template("Error fetching data: ", J.get(lockedData, "error")))
    myADR = calculateADR(J.get(lockedData, "high"), J.get(lockedData, "low"), adrPeriod)
    adrHigh = G_add(J.get(lockedData, "open"), myADR)
    adrLow = G_sub(J.get(lockedData, "open"), myADR)
    myAdrHigh = G_land_points_onto_series(J.get(lockedData, "time"), adrHigh, G_time, "le")
    myAdrLow = G_land_points_onto_series(J.get(lockedData, "time"), adrLow, G_time, "le")
    interpolatedAdrHigh = G_interpolate_sparse_series(myAdrHigh, "constant")
    interpolatedAdrLow = G_interpolate_sparse_series(myAdrLow, "constant")
    G_paint(interpolatedAdrHigh, J.obj(("color", adrHighColor), ("name", "ADR High"), ("style", lineStyle)))
    G_paint(interpolatedAdrLow, J.obj(("color", adrLowColor), ("name", "ADR Low"), ("style", lineStyle)))
    if J.truthy(showLabels):
        lastIndex = J.sub(J.get(G_close, "length"), 1)
        lastLockedIndex = J.sub(J.get(J.get(lockedData, "time"), "length"), 1)
        lastADR = J.get(myADR, lastLockedIndex)
        G_paint_label_at_line(G_paint(interpolatedAdrHigh, J.obj(("hidden", True))), lastIndex, J.template("ADR High: ", J.get(lastADR, "toFixed")(2)), J.obj(("color", adrHighColor), ("vertical_align", "bottom")))
        G_paint_label_at_line(G_paint(interpolatedAdrLow, J.obj(("hidden", True))), lastIndex, J.template("ADR Low: ", J.get(lastADR, "toFixed")(2)), J.obj(("color", adrLowColor), ("vertical_align", "top")))


register_store_indicator(
    script,
    name='average_daily_range_adr_with_timeframe_lock_TS',
    title='Average Daily Range (ADR) with Timeframe Lock',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/average-daily-range-adr-with-timeframe-lock/',
    position='price',
    inputs=[{'id': 'adr_period', 'title': 'ADR Period', 'type': 'number', 'default': 14}, {'id': 'adr_high_color', 'title': 'ADR High Color', 'type': 'color', 'default': 'green'}, {'id': 'adr_low_color', 'title': 'ADR Low Color', 'type': 'color', 'default': 'red'}, {'id': 'line_style', 'title': 'Line Style', 'type': 'select_wide', 'default': 'line', 'options': ['line', 'dotted', 'ladder']}, {'id': 'show_adr_labels', 'title': 'Show ADR Labels', 'type': 'boolean', 'default': True}, {'id': 'locked_timeframe', 'title': 'Locked Timeframe', 'type': 'select_wide', 'default': 'D', 'options': ['1', '2', '3', '4', '5', '6', '10', '12', '15', '30', '45', '60', '65', '90', '120', '240', '1440', 'D', 'W', 'M', 'Q', 'Y']}],
    outputs=['adr_high', 'adr_low', 'line_3', 'line_4'],
    signals=[],
    requires=['history'],
    parity='exact',
)
