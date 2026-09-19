"""
Global Market Session -- TrendSpider store indicator by TrendSpider Team.

Registered as "global_market_session_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/global-market-session/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_fill = G["fill"]
    G_high = G["high"]
    G_horizontal_line = G["horizontal_line"]
    G_input = G["input"]
    G_low = G["low"]
    G_open = G["open"]
    G_paint = G["paint"]
    G_paint_label_at_line = G["paint_label_at_line"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    G_time_of = G["time_of"]
    G_describe_indicator("Global Market Session Indicator")
    def _f1(market=J.undefined, *_args):
        return J.obj(*J.obj_spread(market), ("enabled", J.get(G_input, "boolean")(J.get(market, "name"), True)))
    markets = J.get(J.JSArray([J.obj(("name", "Sydney"), ("opening", 16), ("closing", 1)), J.obj(("name", "Tokyo"), ("opening", 19), ("closing", 4)), J.obj(("name", "London"), ("opening", 2), ("closing", 11)), J.obj(("name", "NY"), ("opening", 8), ("closing", 17))]), "map")(_f1)
    def _f2(market=J.undefined, *_args):
        return J.get(market, "name")
    marketsNames = J.get(markets, "map")(_f2)
    priceLevelsMarketIndex = J.get(marketsNames, "indexOf")(J.get(G_input, "select")("Levels of", "None", J.JSArray(["None", *J.spread(marketsNames)])))
    labels = G_series_of(None)
    openingTop = G_series_of(None)
    openingBottom = G_series_of(None)
    closingTop = G_series_of(None)
    closingBottom = G_series_of(None)
    newDayTop = G_series_of(None)
    newDayBottom = G_series_of(None)
    areaTop = J.mul(1000, J.get(G_close, J.sub(J.get(G_close, "length"), 1)))
    def checkTimeAndUpdateLines(currentIndex=J.undefined, targetTime=J.undefined, name=J.undefined, topSeries=J.undefined, bottomSeries=J.undefined, *_args):
        if (J.eq(J.get(G_time_of(J.get(G_time, currentIndex)), "hours"), targetTime) and J.ne(J.get(G_time_of(J.get(G_time, J.sub(currentIndex, 1))), "hours"), targetTime)):
            J.set(labels, currentIndex, name)
            J.set(topSeries, J.sub(currentIndex, 1), areaTop)
            J.set(topSeries, currentIndex, areaTop)
            J.set(topSeries, J.add(currentIndex, 1), areaTop)
            J.set(bottomSeries, J.sub(currentIndex, 1), J.neg(areaTop))
            J.set(bottomSeries, currentIndex, J.neg(areaTop))
            J.set(bottomSeries, J.add(currentIndex, 1), J.neg(areaTop))
            return True
        return False
    candleIndex = 1
    while J.lt(candleIndex, J.sub(J.get(G_close, "length"), 1)):
        marketIndex = 0
        while J.lt(marketIndex, J.get(markets, "length")):
            _t3 = J.require_object(J.get(markets, marketIndex))
            name = J.get(_t3, "name")
            opening = J.get(_t3, "opening")
            closing = J.get(_t3, "closing")
            enabled = J.get(_t3, "enabled")
            if J.truthy(enabled):
                if J.truthy(checkTimeAndUpdateLines(candleIndex, opening, J.template(name, "_O"), openingTop, openingBottom)):
                    J.set(J.get(markets, marketIndex), "isOpen", True)
                    J.set(J.get(markets, marketIndex), "openIndex", candleIndex)
                    J.set(J.get(markets, marketIndex), "highIndex", candleIndex)
                    J.set(J.get(markets, marketIndex), "lowIndex", candleIndex)
                if J.truthy(checkTimeAndUpdateLines(candleIndex, closing, J.template(name, "_C"), closingTop, closingBottom)):
                    J.set(J.get(markets, marketIndex), "closeIndex", candleIndex)
                    J.set(J.get(markets, marketIndex), "isOpen", False)
                if J.truthy(J.get(J.get(markets, marketIndex), "isOpen")):
                    if J.gt(J.get(G_high, candleIndex), J.get(G_high, J.get(J.get(markets, marketIndex), "highIndex"))):
                        J.set(J.get(markets, marketIndex), "highIndex", candleIndex)
                    if J.lt(J.get(G_low, candleIndex), J.get(G_low, J.get(J.get(markets, marketIndex), "lowIndex"))):
                        J.set(J.get(markets, marketIndex), "lowIndex", candleIndex)
            marketIndex = J.inc(marketIndex)
        checkTimeAndUpdateLines(candleIndex, 0, "New24Hrs", newDayTop, newDayBottom)
        candleIndex = J.inc(candleIndex)
    G_paint(labels, J.obj(("style", "labels_above"), ("name", "Labels")))
    G_fill(G_paint(openingTop, J.obj(("hidden", True))), G_paint(openingBottom, J.obj(("hidden", True))), "darkGreen", J.undefined, "Exchange Open")
    G_fill(G_paint(closingTop, J.obj(("hidden", True))), G_paint(closingBottom, J.obj(("hidden", True))), "red", J.undefined, "Exchange Close")
    G_fill(G_paint(newDayTop, J.obj(("hidden", True))), G_paint(newDayBottom, J.obj(("hidden", True))), "black", J.undefined, "New 24Hrs")
    levelsLines = J.obj(("open", G_series_of(None)), ("high", G_series_of(None)), ("low", G_series_of(None)), ("close", G_series_of(None)))
    selectedMarketName = ""
    if J.sne(priceLevelsMarketIndex, (-1)):
        _t4 = J.require_object(J.get(markets, priceLevelsMarketIndex))
        openIndex = J.get(_t4, "openIndex")
        highIndex = J.get(_t4, "highIndex")
        lowIndex = J.get(_t4, "lowIndex")
        closeIndex = J.get(_t4, "closeIndex")
        name_2 = J.get(_t4, "name")
        selectedMarketName = name_2
        J.set(levelsLines, "open", G_horizontal_line(J.get(G_open, openIndex), openIndex))
        J.set(levelsLines, "high", G_horizontal_line(J.get(G_high, highIndex), highIndex))
        J.set(levelsLines, "low", G_horizontal_line(J.get(G_low, lowIndex), lowIndex))
        J.set(levelsLines, "close", G_horizontal_line(J.get(G_close, closeIndex), closeIndex))
    G_paint_label_at_line(G_paint(J.get(levelsLines, "open"), J.obj(("name", "Open"), ("color", "black"), ("style", "dotted"))), J.sub(J.get(G_close, "length"), 1), J.template(selectedMarketName, " Open"))
    G_paint_label_at_line(G_paint(J.get(levelsLines, "high"), J.obj(("name", "High"), ("color", "green"), ("thickness", 2))), J.sub(J.get(G_close, "length"), 1), J.template(selectedMarketName, " High"))
    G_paint_label_at_line(G_paint(J.get(levelsLines, "low"), J.obj(("name", "Low"), ("color", "red"), ("thickness", 2))), J.sub(J.get(G_close, "length"), 1), J.template(selectedMarketName, " Low"))
    G_paint_label_at_line(G_paint(J.get(levelsLines, "close"), J.obj(("name", "Close"), ("color", "black"), ("style", "dotted"))), J.sub(J.get(G_close, "length"), 1), J.template(selectedMarketName, " Close"))


register_store_indicator(
    script,
    name='global_market_session_TS',
    title='Global Market Session',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/global-market-session/',
    position='price',
    inputs=[{'id': 'sydney', 'title': 'Sydney', 'type': 'boolean', 'default': True}, {'id': 'tokyo', 'title': 'Tokyo', 'type': 'boolean', 'default': True}, {'id': 'london', 'title': 'London', 'type': 'boolean', 'default': True}, {'id': 'ny', 'title': 'NY', 'type': 'boolean', 'default': True}, {'id': 'levels_of', 'title': 'Levels of', 'type': 'select_wide', 'default': 'None', 'options': ['None', 'Sydney', 'Tokyo', 'London', 'NY']}],
    outputs=['labels', 'line_2', 'line_3', 'line_5', 'line_6', 'line_8', 'line_9', 'open', 'high', 'low', 'close'],
    signals=[],
    requires=[],
    parity='exact',
)
