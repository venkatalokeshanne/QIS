"""
Pre-Market Range -- TrendSpider store indicator by James Chambers.

Registered as "pre_market_range_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/pre-market-range/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_paint = G["paint"]
    G_request = G["request"]
    G_series_of = G["series_of"]
    G_session_of = G["session_of"]
    G_time = G["time"]
    G_describe_indicator("Pre-market range")
    extHoursData = J.get(G_request, "history")(J.get(G_constants, "ticker"), "30", J.obj(("ext_session", True)))
    preMarketRangeByDay = J.obj()
    extHoursIndex = 0
    while J.lt(extHoursIndex, J.get(J.get(extHoursData, "time"), "length")):
        sessionAtCandle = G_session_of(J.get(J.get(extHoursData, "time"), extHoursIndex), J.get(G_constants, "resolution"), J.get(G_constants, "ext_session_premarket"))
        dayOfCandle = J.get(sessionAtCandle, "session")
        if (not J.truthy(J.get(preMarketRangeByDay, dayOfCandle))):
            J.set(preMarketRangeByDay, dayOfCandle, J.obj(("high", J.get(J.get(extHoursData, "high"), extHoursIndex)), ("low", J.get(J.get(extHoursData, "low"), extHoursIndex))))
        else:
            J.set(J.get(preMarketRangeByDay, dayOfCandle), "high", J.get(G_Math, "max")(J.get(J.get(preMarketRangeByDay, dayOfCandle), "high"), J.get(J.get(extHoursData, "high"), extHoursIndex)))
            J.set(J.get(preMarketRangeByDay, dayOfCandle), "low", J.get(G_Math, "min")(J.get(J.get(preMarketRangeByDay, dayOfCandle), "low"), J.get(J.get(extHoursData, "low"), extHoursIndex)))
        extHoursIndex = J.add(extHoursIndex, 1)
    rangeHigh = G_series_of(None)
    rangeLow = G_series_of(None)
    lastSession = G_session_of(J.get(G_time, J.sub(J.get(G_time, "length"), 1)), J.get(G_constants, "resolution"))
    candleIndex = 0
    while J.lt(candleIndex, J.get(G_time, "length")):
        sessionAtCandle_2 = G_session_of(J.get(G_time, candleIndex), J.get(G_constants, "resolution"))
        isLastSession = J.eq(J.get(sessionAtCandle_2, "session"), J.get(lastSession, "session"))
        extHoursRange = J.get(preMarketRangeByDay, J.get(sessionAtCandle_2, "session"))
        if (J.truthy(isLastSession) and J.truthy(extHoursRange)):
            J.set(rangeHigh, candleIndex, J.get(extHoursRange, "high"))
            J.set(rangeLow, candleIndex, J.get(extHoursRange, "low"))
        if (J.ne(J.get(rangeHigh, candleIndex), J.get(rangeHigh, J.sub(candleIndex, 1))) or J.ne(J.get(rangeLow, candleIndex), J.get(rangeLow, J.sub(candleIndex, 1)))):
            J.set(rangeHigh, J.sub(candleIndex, 1), None)
            J.set(rangeLow, J.sub(candleIndex, 1), None)
        candleIndex = J.add(candleIndex, 1)
    G_paint(rangeHigh, J.obj(("style", "ladder"), ("color", "black")))
    G_paint(rangeLow, J.obj(("style", "ladder"), ("color", "black")))


register_store_indicator(
    script,
    name='pre_market_range_TS',
    title='Pre-Market Range',
    developer='James Chambers',
    url='https://trendspider.com/trading-tools-store/indicators/pre-market-range/',
    position='price',
    inputs=[],
    outputs=['line_1', 'line_2'],
    signals=[],
    requires=['history'],
    parity='exact',
)
