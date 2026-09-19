"""
DMW Levels -- TrendSpider store indicator by TrendSpider Team.

Registered as "dmw_levels_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/dmw-levels-move-to-main-account/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_fill = G["fill"]
    G_input = G["input"]
    G_interpolate_sparse_series = G["interpolate_sparse_series"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_market = G["market"]
    G_paint = G["paint"]
    G_request = G["request"]
    G_series_of = G["series_of"]
    G_time_of = G["time_of"]
    def lineWithLabel(level=J.undefined, dataPointTime=J.undefined, label=J.undefined, _p1=J.undefined, *_args):
        _t2 = _p1
        if _t2 is J.undefined:
            _t2 = "lt"
        landingMechanic = _t2
        seriesLanded = (G_interpolate_sparse_series(G_land_points_onto_series(J.JSArray([dataPointTime]), J.JSArray([level]), J.get(G_market, "time"), landingMechanic), "constant") if J.gt(dataPointTime, J.get(J.get(G_market, "time"), 0)) else G_series_of(level))
        series = J.JSArray([*J.spread(J.get(seriesLanded, "slice")(0, (-1))), J.obj(("y", level), ("dataLabels", J.obj(("enabled", True), ("color", labelColor), ("format", label))))])
        return G_paint(series, J.obj(("name", label), ("color", "white"), ("ignoreWhenScaling", True)))
    G_describe_indicator("DMW Levels")
    showMonthly = J.get(G_input, "boolean")("Monthly", True)
    showWeekly = J.get(G_input, "boolean")("Weekly", True)
    showDaily = J.get(G_input, "boolean")("Daily", True)
    showPremarket = J.get(G_input, "boolean")("Pre.M", True)
    labelColor = J.get(G_input, "color")("Labels", "blue")
    M_TITLE = "M.Close"
    W_TITLE = "W.Close"
    D_TITLE = "D.Close"
    EXT_HIGH_TITLE = "Pre.High"
    EXT_LOW_TITLE = "Pre.Low"
    if J.truthy(showMonthly):
        monthly = J.get(G_request, "history")(J.get(G_current, "ticker"), "M")
        lineWithLabel(J.get(J.get(monthly, "close"), J.sub(J.get(J.get(monthly, "close"), "length"), 2)), J.get(J.get(monthly, "time"), J.sub(J.get(J.get(monthly, "time"), "length"), 1)), M_TITLE)
    else:
        G_paint(G_series_of(None), J.obj(("name", M_TITLE)))
    if J.truthy(showWeekly):
        weekly = J.get(G_request, "history")(J.get(G_current, "ticker"), "W")
        lineWithLabel(J.get(J.get(weekly, "close"), J.sub(J.get(J.get(weekly, "close"), "length"), 2)), J.get(J.get(weekly, "time"), J.sub(J.get(J.get(weekly, "time"), "length"), 1)), W_TITLE)
    else:
        G_paint(G_series_of(None), J.obj(("name", W_TITLE)))
    if J.truthy(showDaily):
        daily = J.get(G_request, "history")(J.get(G_current, "ticker"), "D")
        lineWithLabel(J.get(J.get(daily, "close"), J.sub(J.get(J.get(daily, "close"), "length"), 2)), J.get(J.get(daily, "time"), J.sub(J.get(J.get(daily, "time"), "length"), 1)), D_TITLE)
    else:
        G_paint(G_series_of(None), J.obj(("name", D_TITLE)))
    if J.truthy(showPremarket):
        intradayExt = J.get(G_request, "history")(J.get(G_current, "ticker"), "30", J.obj(("ext_session", True)))
        lastKnownExtSessionCandles = J.JSArray([])
        lastKnownMarkerCandleTimestamp = None
        anyExtSessionCandleFaced = False
        extSession = J.get(G_current, "ext_session")
        marketSession = J.get(G_current, "session")
        index = 0
        while J.lt(index, J.get(J.get(intradayExt, "time"), "length")):
            indexNormalized = J.sub(J.sub(J.get(J.get(intradayExt, "time"), "length"), 1), index)
            candleTime = J.get(J.get(intradayExt, "time"), indexNormalized)
            timeParsed = G_time_of(candleTime)
            isExtSession = ((_t4 if J.truthy(_t4 := J.lt(J.get(timeParsed, "hours"), J.get(J.get(marketSession, "start"), "hours"))) else (J.lt(J.get(timeParsed, "minutes"), J.get(J.get(marketSession, "start"), "minutes")) if J.truthy(_t5 := J.eq(J.get(timeParsed, "hours"), J.get(J.get(marketSession, "start"), "hours"))) else _t5)) if J.truthy(_t1 := (_t2 if J.truthy(_t2 := J.gt(J.get(timeParsed, "hours"), J.get(J.get(extSession, "start"), "hours"))) else (J.ge(J.get(timeParsed, "minutes"), J.get(J.get(extSession, "start"), "minutes")) if J.truthy(_t3 := J.eq(J.get(timeParsed, "hours"), J.get(J.get(extSession, "start"), "hours"))) else _t3))) else _t1)
            if J.truthy(isExtSession):
                anyExtSessionCandleFaced = True
                J.get(lastKnownExtSessionCandles, "push")(J.obj(("high", J.get(J.get(intradayExt, "high"), indexNormalized)), ("low", J.get(J.get(intradayExt, "low"), indexNormalized)), ("time", candleTime)))
            else:
                if J.truthy(anyExtSessionCandleFaced):
                    break
                lastKnownMarkerCandleTimestamp = J.get(J.get(intradayExt, "time"), indexNormalized)
            index = J.add(index, 1)
        def _f6(candle=J.undefined, *_args):
            return J.get(candle, "high")
        premarketHigh = J.get(G_Math, "max")(*J.spread(J.get(lastKnownExtSessionCandles, "map")(_f6)))
        def _f7(candle=J.undefined, *_args):
            return J.get(candle, "low")
        premarketLow = J.get(G_Math, "min")(*J.spread(J.get(lastKnownExtSessionCandles, "map")(_f7)))
        G_fill(lineWithLabel(premarketHigh, lastKnownMarkerCandleTimestamp, EXT_HIGH_TITLE, "eq"), lineWithLabel(premarketLow, lastKnownMarkerCandleTimestamp, EXT_LOW_TITLE, "eq"), "orange")
    else:
        G_paint(G_series_of(None), J.obj(("name", D_TITLE)))


register_store_indicator(
    script,
    name='dmw_levels_TS',
    title='DMW Levels',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/dmw-levels-move-to-main-account/',
    position='price',
    inputs=[{'id': 'monthly', 'title': 'Monthly', 'type': 'boolean', 'default': True}, {'id': 'weekly', 'title': 'Weekly', 'type': 'boolean', 'default': True}, {'id': 'daily', 'title': 'Daily', 'type': 'boolean', 'default': True}, {'id': 'pre_m', 'title': 'Pre.M', 'type': 'boolean', 'default': True}, {'id': 'labels', 'title': 'Labels', 'type': 'color', 'default': 'blue'}],
    outputs=['m_close', 'w_close', 'd_close', 'pre_high', 'pre_low'],
    signals=[],
    requires=['history'],
    parity='exact',
)
