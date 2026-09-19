"""
Ripster Trend Labels -- TrendSpider store indicator by Ripster G.

Registered as "ripster_trend_labels_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/691aba-ripster-trend-labels/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_assert = G["assert"]
    G_constants = G["constants"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_ema = G["ema"]
    G_fill = G["fill"]
    G_input = G["input"]
    G_interpolate_sparse_series = G["interpolate_sparse_series"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_paint = G["paint"]
    G_paint_overlay = G["paint_overlay"]
    G_request = G["request"]
    G_series_of = G["series_of"]
    G_session_of = G["session_of"]
    G_time = G["time"]
    G_describe_indicator("Ripster Trend Labels", "price")
    myShowPremarketLevels = J.get(G_input, "boolean")("Show Premarket Levels", False)
    myShowCloud3450 = J.get(G_input, "boolean")("Show 34/50 Cloud", False)
    myShowCloud512 = J.get(G_input, "boolean")("Show 5/12 Cloud", False)
    myData = J.get(G_request, "history")(J.get(G_current, "ticker"), "10", J.obj(("ext_session", True)))
    G_assert((not J.truthy(J.get(myData, "error"))), J.template("Error fetching 10-min data: ", J.get(myData, "error")))
    myEma50 = G_ema(J.get(myData, "close"), 50)
    myEma12 = G_ema(J.get(myData, "close"), 12)
    myEma34 = G_ema(J.get(myData, "close"), 34)
    myEma5 = G_ema(J.get(myData, "close"), 5)
    myLastIndex = J.sub(J.get(J.get(myData, "close"), "length"), 1)
    myCurrentPrice = J.get(J.get(myData, "close"), myLastIndex)
    myCurrentEma50 = J.get(myEma50, myLastIndex)
    myCurrentEma12 = J.get(myEma12, myLastIndex)
    extHoursData = J.get(G_request, "history")(J.get(G_constants, "ticker"), "30", J.obj(("ext_session", True)))
    G_assert((not J.truthy(J.get(extHoursData, "error"))), J.template("Error fetching 30-min ext hours data: ", J.get(extHoursData, "error")))
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
    lastSession = G_session_of(J.get(G_time, J.sub(J.get(G_time, "length"), 1)), J.get(G_constants, "resolution"))
    todaysPremarketRange = J.get(preMarketRangeByDay, J.get(lastSession, "session"))
    myPremarketHigh = J.undefined
    myPremarketLow = J.undefined
    if J.truthy(todaysPremarketRange):
        myPremarketHigh = J.get(todaysPremarketRange, "high")
        myPremarketLow = J.get(todaysPremarketRange, "low")
    else:
        myPremarketHigh = myCurrentPrice
        myPremarketLow = myCurrentPrice
    myPriceAction = J.undefined
    if J.gt(myCurrentPrice, myPremarketHigh):
        myPriceAction = "Bullish Trend"
    elif J.lt(myCurrentPrice, myPremarketLow):
        myPriceAction = "Bearish Trend"
    else:
        myPriceAction = "Chop Range"
    myRipsterCloud1 = ("Bullish" if J.gt(myCurrentPrice, myCurrentEma50) else "Bearish")
    myRipsterCloud2 = ("Bullish" if J.gt(myCurrentPrice, myCurrentEma12) else "Bearish")
    myBullishColor = "#12d962"
    myBearishColor = "#ff4976"
    myNeutralColor = "#f0b90b"
    myBackgroundColor = "#008080"
    myTextColor = "#FFFFFF"
    todaySessionStart = J.get(lastSession, "session")
    sessionStartIndex = None
    i = 0
    while J.lt(i, J.get(G_time, "length")):
        candleSession = G_session_of(J.get(G_time, i), J.get(G_constants, "resolution"))
        if J.seq(J.get(candleSession, "session"), todaySessionStart):
            sessionStartIndex = i
            break
        i = J.add(i, 1)
    myPremarketHighSeries = G_series_of(None)
    myPremarketLowSeries = G_series_of(None)
    if (J.truthy(myShowPremarketLevels) and (sessionStartIndex is not None)):
        i_2 = sessionStartIndex
        while J.lt(i_2, J.get(G_time, "length")):
            J.set(myPremarketHighSeries, i_2, myPremarketHigh)
            J.set(myPremarketLowSeries, i_2, myPremarketLow)
            i_2 = J.add(i_2, 1)
    G_paint(myPremarketHighSeries, J.obj(("name", "Premarket High"), ("color", myBullishColor), ("style", "dotted"), ("width", 2)))
    G_paint(myPremarketLowSeries, J.obj(("name", "Premarket Low"), ("color", myBearishColor), ("style", "dotted"), ("width", 2)))
    myEma34Landed = G_land_points_onto_series(J.get(myData, "time"), myEma34, G_time, "ge")
    myEma34Interpolated = G_interpolate_sparse_series(myEma34Landed, "constant")
    myEma50Landed = G_land_points_onto_series(J.get(myData, "time"), myEma50, G_time, "ge")
    myEma50Interpolated = G_interpolate_sparse_series(myEma50Landed, "constant")
    myEma5Landed = G_land_points_onto_series(J.get(myData, "time"), myEma5, G_time, "ge")
    myEma5Interpolated = G_interpolate_sparse_series(myEma5Landed, "constant")
    myEma12Landed = G_land_points_onto_series(J.get(myData, "time"), myEma12, G_time, "ge")
    myEma12Interpolated = G_interpolate_sparse_series(myEma12Landed, "constant")
    myEma34ToPaint = (myEma34Interpolated if J.truthy(myShowCloud3450) else G_series_of(None))
    myEma50ToPaint = (myEma50Interpolated if J.truthy(myShowCloud3450) else G_series_of(None))
    myLine34 = G_paint(myEma34ToPaint, J.obj(("name", "EMA 34"), ("color", "#2196F3"), ("style", "line"), ("width", 2)))
    myLine50 = G_paint(myEma50ToPaint, J.obj(("name", "EMA 50"), ("color", "#9C27B0"), ("style", "line"), ("width", 2)))
    G_fill(myLine34, myLine50, "#2196F3", 0.2)
    myEma5ToPaint = (myEma5Interpolated if J.truthy(myShowCloud512) else G_series_of(None))
    myEma12ToPaint = (myEma12Interpolated if J.truthy(myShowCloud512) else G_series_of(None))
    myLine5 = G_paint(myEma5ToPaint, J.obj(("name", "EMA 5"), ("color", "#FF9800"), ("style", "line"), ("width", 2)))
    myLine12 = G_paint(myEma12ToPaint, J.obj(("name", "EMA 12"), ("color", "#4CAF50"), ("style", "line"), ("width", 2)))
    G_fill(myLine5, myLine12, "#FF9800", 0.2)
    G_paint_overlay("Ripster Trend Labels v2", J.obj(("position", "top_right"), ("order", "above_all")), J.obj(("paddingLeft", 20), ("paddingRight", 70), ("paddingTop", 2), ("paddingBottom", 10), ("rows", J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", "Price Action"), ("color", myTextColor), ("background", myBackgroundColor), ("padding", "5px 10px"), ("fontSize", "14px")), J.obj(("text", myPriceAction), ("color", "black"), ("background", (myBullishColor if J.seq(myPriceAction, "Bullish Trend") else (myBearishColor if J.seq(myPriceAction, "Bearish Trend") else myNeutralColor))), ("padding", "5px 10px"), ("fontWeight", "bold"), ("fontSize", "14px"))]))), J.obj(("cells", J.JSArray([J.obj(("text", "Ripster Clouds 34/50"), ("color", myTextColor), ("background", myBackgroundColor), ("padding", "5px 10px"), ("fontSize", "14px")), J.obj(("text", myRipsterCloud1), ("color", "black"), ("background", (myBullishColor if J.seq(myRipsterCloud1, "Bullish") else myBearishColor)), ("padding", "5px 10px"), ("fontWeight", "bold"), ("fontSize", "14px"))]))), J.obj(("cells", J.JSArray([J.obj(("text", "Ripster Clouds 5/12"), ("color", myTextColor), ("background", myBackgroundColor), ("padding", "5px 10px"), ("fontSize", "14px")), J.obj(("text", myRipsterCloud2), ("color", "black"), ("background", (myBullishColor if J.seq(myRipsterCloud2, "Bullish") else myBearishColor)), ("padding", "5px 10px"), ("fontWeight", "bold"), ("fontSize", "14px"))])))]))))


register_store_indicator(
    script,
    name='ripster_trend_labels_TS',
    title='Ripster Trend Labels',
    developer='Ripster G',
    url='https://trendspider.com/trading-tools-store/indicators/691aba-ripster-trend-labels/',
    position='price',
    inputs=[{'id': 'show_premarket_levels', 'title': 'Show Premarket Levels', 'type': 'boolean', 'default': False}, {'id': 'show_34_50_cloud', 'title': 'Show 34/50 Cloud', 'type': 'boolean', 'default': False}, {'id': 'show_5_12_cloud', 'title': 'Show 5/12 Cloud', 'type': 'boolean', 'default': False}],
    outputs=['premarket_high', 'premarket_low', 'ema_34', 'ema_50', 'ema_5', 'ema_12'],
    signals=[],
    requires=['history'],
    parity='exact',
)
