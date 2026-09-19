"""
Current Market Cap Multi-ticker -- TrendSpider store indicator by TrendSpider.

Registered as "current_market_cap_multi_ticker_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6a90a8-current-market-cap-multi-ticker/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_close = G["close"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_input = G["input"]
    G_interpolate_sparse_series = G["interpolate_sparse_series"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_paint = G["paint"]
    G_paint_label_at_line = G["paint_label_at_line"]
    G_request = G["request"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    G_describe_indicator("Current Market Cap Multi-ticker", "lower")
    quarters = J.get(G_input, "number")("Quarters", 40, J.obj(("min", 1), ("max", 40)))
    myTicker2 = J.get(G_input, "symbol")("Ticker 2", "NVDA")
    myTicker3 = J.get(G_input, "symbol")("Ticker 3", "GOOG")
    myTicker4 = J.get(G_input, "symbol")("Ticker 4", "MSFT")
    myTicker5 = J.get(G_input, "symbol")("Ticker 5", "AMZN")
    def computeMarketCap(myTickerSymbol=J.undefined, *_args):
        myFundamentalData = J.get(G_request, "fundamental")(myTickerSymbol, J.JSArray(["shares_basic_bs"]), quarters)
        if J.truthy(J.get(myFundamentalData, "error")):
            return J.obj(("error", J.get(myFundamentalData, "error")))
        mySharesData = (_t1 if J.truthy(_t1 := J.get(myFundamentalData, "shares_basic_bs")) else J.JSArray([]))
        if J.seq(J.get(mySharesData, "length"), 0):
            return J.obj(("error", "No shares outstanding data available"))
        def _f2(r=J.undefined, *_args):
            return J.get(r, "reportdate")
        mySharesTimestamps = J.get(mySharesData, "map")(_f2)
        def _f3(r=J.undefined, *_args):
            return J.get(r, "value")
        mySharesValues = J.get(mySharesData, "map")(_f3)
        myHistoryData = J.get(G_request, "history")(myTickerSymbol, J.get(G_current, "resolution"))
        if J.truthy(J.get(myHistoryData, "error")):
            return J.obj(("error", J.get(myHistoryData, "error")))
        mySharesLanded = G_land_points_onto_series(mySharesTimestamps, mySharesValues, J.get(myHistoryData, "time"), "le")
        mySharesInterpolated = G_interpolate_sparse_series(mySharesLanded, "constant")
        def _f4(c=J.undefined, s=J.undefined, *_args):
            if ((s is None) or (s is J.undefined)):
                return None
            return J.mul(c, s)
        myMarketCapOnOtherTF = G_for_every(J.get(myHistoryData, "close"), mySharesInterpolated, _f4)
        myMarketCapLanded = G_land_points_onto_series(J.get(myHistoryData, "time"), myMarketCapOnOtherTF, G_time, "ge")
        return J.obj(("marketCap", G_interpolate_sparse_series(myMarketCapLanded, "constant")))
    myResult1 = computeMarketCap(J.get(G_current, "ticker"))
    myLine1 = G_paint((G_series_of(None) if J.truthy(J.get(myResult1, "error")) else J.get(myResult1, "marketCap")), J.obj(("name", "Market Cap (Ticker 1)"), ("color", "#2E86DE"), ("thickness", 3)))
    myResult2 = computeMarketCap(myTicker2)
    myResult3 = computeMarketCap(myTicker3)
    myResult4 = computeMarketCap(myTicker4)
    myResult5 = computeMarketCap(myTicker5)
    myLine2 = G_paint((G_series_of(None) if J.truthy(J.get(myResult2, "error")) else J.get(myResult2, "marketCap")), J.obj(("name", "Market Cap (Ticker 2)"), ("color", "#10AC84"), ("thickness", 3)))
    myLine3 = G_paint((G_series_of(None) if J.truthy(J.get(myResult3, "error")) else J.get(myResult3, "marketCap")), J.obj(("name", "Market Cap (Ticker 3)"), ("color", "#EE5A6F"), ("thickness", 3)))
    myLine4 = G_paint((G_series_of(None) if J.truthy(J.get(myResult4, "error")) else J.get(myResult4, "marketCap")), J.obj(("name", "Market Cap (Ticker 4)"), ("color", "#F79F1F"), ("thickness", 3)))
    myLine5 = G_paint((G_series_of(None) if J.truthy(J.get(myResult5, "error")) else J.get(myResult5, "marketCap")), J.obj(("name", "Market Cap (Ticker 5)"), ("color", "#A3CB38"), ("thickness", 3)))
    myLastIndex = J.sub(J.get(G_close, "length"), 1)
    myValidLabels = J.JSArray([])
    if (((not J.truthy(J.get(myResult1, "error"))) and (J.get(J.get(myResult1, "marketCap"), myLastIndex) is not None)) and (J.get(J.get(myResult1, "marketCap"), myLastIndex) is not J.undefined)):
        J.get(myValidLabels, "push")(J.obj(("line", myLine1), ("ticker", J.get(G_current, "ticker")), ("value", J.get(J.get(myResult1, "marketCap"), myLastIndex)), ("color", "#2E86DE")))
    if (((not J.truthy(J.get(myResult2, "error"))) and (J.get(J.get(myResult2, "marketCap"), myLastIndex) is not None)) and (J.get(J.get(myResult2, "marketCap"), myLastIndex) is not J.undefined)):
        J.get(myValidLabels, "push")(J.obj(("line", myLine2), ("ticker", myTicker2), ("value", J.get(J.get(myResult2, "marketCap"), myLastIndex)), ("color", "#10AC84")))
    if (((not J.truthy(J.get(myResult3, "error"))) and (J.get(J.get(myResult3, "marketCap"), myLastIndex) is not None)) and (J.get(J.get(myResult3, "marketCap"), myLastIndex) is not J.undefined)):
        J.get(myValidLabels, "push")(J.obj(("line", myLine3), ("ticker", myTicker3), ("value", J.get(J.get(myResult3, "marketCap"), myLastIndex)), ("color", "#EE5A6F")))
    if (((not J.truthy(J.get(myResult4, "error"))) and (J.get(J.get(myResult4, "marketCap"), myLastIndex) is not None)) and (J.get(J.get(myResult4, "marketCap"), myLastIndex) is not J.undefined)):
        J.get(myValidLabels, "push")(J.obj(("line", myLine4), ("ticker", myTicker4), ("value", J.get(J.get(myResult4, "marketCap"), myLastIndex)), ("color", "#F79F1F")))
    if (((not J.truthy(J.get(myResult5, "error"))) and (J.get(J.get(myResult5, "marketCap"), myLastIndex) is not None)) and (J.get(J.get(myResult5, "marketCap"), myLastIndex) is not J.undefined)):
        J.get(myValidLabels, "push")(J.obj(("line", myLine5), ("ticker", myTicker5), ("value", J.get(J.get(myResult5, "marketCap"), myLastIndex)), ("color", "#A3CB38")))
    def _f1(a=J.undefined, b=J.undefined, *_args):
        return J.sub(J.get(b, "value"), J.get(a, "value"))
    J.get(myValidLabels, "sort")(_f1)
    myVerticalAlignments = J.JSArray(["top", "middle", "bottom", "top", "middle"])
    i = 0
    while J.lt(i, J.get(myValidLabels, "length")):
        myLabel = J.get(myValidLabels, i)
        myAlignment = (_t2 if J.truthy(_t2 := J.get(myVerticalAlignments, i)) else "middle")
        G_paint_label_at_line(J.get(myLabel, "line"), myLastIndex, J.get(myLabel, "ticker"), J.obj(("color", J.get(myLabel, "color")), ("vertical_align", myAlignment), ("background_color", "rgba(0, 0, 0, 0.7)"), ("border_radius", 3), ("halo", True)))
        i = J.add(i, 1)


register_store_indicator(
    script,
    name='current_market_cap_multi_ticker_TS',
    title='Current Market Cap Multi-ticker',
    developer='TrendSpider',
    url='https://trendspider.com/trading-tools-store/indicators/6a90a8-current-market-cap-multi-ticker/',
    position='lower',
    inputs=[{'id': 'quarters', 'title': 'Quarters', 'type': 'number', 'default': 40}, {'id': 'sym-ticker_2', 'title': 'Ticker 2', 'type': 'symbol-search', 'default': 'NVDA'}, {'id': 'sym-ticker_3', 'title': 'Ticker 3', 'type': 'symbol-search', 'default': 'GOOG'}, {'id': 'sym-ticker_4', 'title': 'Ticker 4', 'type': 'symbol-search', 'default': 'MSFT'}, {'id': 'sym-ticker_5', 'title': 'Ticker 5', 'type': 'symbol-search', 'default': 'AMZN'}],
    outputs=['market_cap__ticker_1_', 'market_cap__ticker_2_', 'market_cap__ticker_3_', 'market_cap__ticker_4_', 'market_cap__ticker_5_'],
    signals=[],
    requires=['fundamental', 'history'],
    parity='exact',
)
