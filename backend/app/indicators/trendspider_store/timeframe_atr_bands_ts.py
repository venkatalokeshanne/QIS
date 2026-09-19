"""
Timeframe ATR Bands -- TrendSpider store indicator by Trade Seekers.

Registered as "timeframe_atr_bands_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68a7cb-timeframe-atr-bands/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_assert = G["assert"]
    G_atr = G["atr"]
    G_bar_at = G["bar_at"]
    G_constants = G["constants"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_fill = G["fill"]
    G_input = G["input"]
    G_interpolate_sparse_series = G["interpolate_sparse_series"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_open = G["open"]
    G_paint = G["paint"]
    G_request = G["request"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    G_describe_indicator("Timeframe ATR Bands", J.obj(("decimals", 2), ("warmup", "500")))
    timeframeInput = J.get(G_input, "select")("Timeframe", "W", J.get(G_constants, "time_frames"))
    atrLengthInput = J.get(G_input, "number")("ATR Length", 52, J.obj(("min", 1), ("max", 500)))
    timeframeData = J.get(G_request, "history")(J.get(G_current, "ticker"), timeframeInput)
    G_assert((not J.truthy(J.get(timeframeData, "error"))), J.template("Error fetching data: ", J.get(timeframeData, "error")))
    avgTrueRange = G_atr(J.get(timeframeData, "high"), J.get(timeframeData, "low"), J.get(timeframeData, "close"), atrLengthInput)
    atrLanded = G_land_points_onto_series(J.get(timeframeData, "time"), avgTrueRange, G_time, "ge")
    atrInterpolated = G_interpolate_sparse_series(atrLanded, "constant")
    midLine = G_series_of(None)
    highLine = G_series_of(None)
    lowLine = G_series_of(None)
    highExtension = G_series_of(None)
    lowExtension = G_series_of(None)
    periodsStart = J.JSArray([])
    i = 0
    while J.lt(i, J.get(G_time, "length")):
        if (J.seq(i, 0) or J.sne(J.get(G_bar_at(J.get(G_time, i), timeframeInput), "session"), J.get(G_bar_at(J.get(G_time, J.sub(i, 1)), timeframeInput), "session"))):
            J.get(periodsStart, "push")(i)
        i = J.inc(i)
    i_2 = 0
    while J.lt(i_2, J.get(periodsStart, "length")):
        startIndex = J.get(periodsStart, i_2)
        endIndex = (J.get(periodsStart, J.add(i_2, 1)) if J.lt(i_2, J.sub(J.get(periodsStart, "length"), 1)) else J.get(G_time, "length"))
        periodOpen = J.get(G_open, startIndex)
        periodAtr = J.get(atrInterpolated, startIndex)
        j = startIndex
        while J.lt(j, endIndex):
            J.set(midLine, j, periodOpen)
            J.set(highLine, j, J.add(periodOpen, J.div(periodAtr, 2)))
            J.set(lowLine, j, J.sub(periodOpen, J.div(periodAtr, 2)))
            J.set(highExtension, j, J.add(periodOpen, periodAtr))
            J.set(lowExtension, j, J.sub(periodOpen, periodAtr))
            j = J.inc(j)
        i_2 = J.inc(i_2)
    midLinePainted = G_paint(midLine, J.obj(("color", "orange"), ("name", "Mid"), ("style", "ladder")))
    highLinePainted = G_paint(highLine, J.obj(("color", "red"), ("name", "High"), ("style", "dotted")))
    lowLinePainted = G_paint(lowLine, J.obj(("color", "green"), ("name", "Low"), ("style", "dotted")))
    highExtensionPainted = G_paint(highExtension, J.obj(("color", "red"), ("name", "High Extension"), ("style", "ladder")))
    lowExtensionPainted = G_paint(lowExtension, J.obj(("color", "green"), ("name", "Low Extension"), ("style", "ladder")))
    G_fill(highLinePainted, highExtensionPainted, "red", 0.05, "High Fill")
    G_fill(lowLinePainted, lowExtensionPainted, "green", 0.05, "Low Fill")


register_store_indicator(
    script,
    name='timeframe_atr_bands_TS',
    title='Timeframe ATR Bands',
    developer='Trade Seekers',
    url='https://trendspider.com/trading-tools-store/indicators/68a7cb-timeframe-atr-bands/',
    position='price',
    inputs=[{'id': 'warmup', 'title': 'Warmup', 'type': 'number', 'default': '500'}, {'id': 'timeframe', 'title': 'Timeframe', 'type': 'select_wide', 'default': 'W', 'options': ['1', '2', '3', '4', '5', '6', '10', '12', '15', '30', '45', '60', '65', '90', '120', '240', '1440', 'D', 'W', 'M', 'Q', 'Y']}, {'id': 'atr_length', 'title': 'ATR Length', 'type': 'number', 'default': 52}],
    outputs=['mid', 'high', 'low', 'high_extension', 'low_extension'],
    signals=[],
    requires=['history'],
    parity='exact',
)
