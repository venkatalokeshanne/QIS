"""
At-A-Glance Overlay -- TrendSpider store indicator by Connor Robbins.

Registered as "at_a_glance_overlay_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68abda-at-a-glance-overlay/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_assert = G["assert"]
    G_close = G["close"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_input = G["input"]
    G_low = G["low"]
    G_open = G["open"]
    G_paint_overlay = G["paint_overlay"]
    G_request = G["request"]
    G_shift = G["shift"]
    G_sma = G["sma"]
    G_sub = G["sub"]
    G_describe_indicator("At-A-Glance Overlay")
    def getLastValue(series=J.undefined, *_args):
        i = J.sub(J.get(series, "length"), 1)
        while J.ge(i, 0):
            if (J.get(series, i) is not None):
                return J.get(series, i)
            i = J.dec(i)
        return None
    def formatPercentage(value=J.undefined, *_args):
        return J.add(J.get(J.mul(value, 100), "toFixed")(2), "%")
    def myFormatValue(value=J.undefined, *_args):
        return J.add(J.get(value, "toFixed")(2), "%")
    priceMovementShort = G_sub(G_close, G_shift(G_close, 5))
    priceMovementMed = G_sub(G_close, G_shift(G_close, 20))
    priceMovementLong = G_sub(G_close, G_shift(G_close, 60))
    def _f1(p=J.undefined, *_args):
        return ("green" if J.gt(p, 0) else "red")
    color5 = G_for_every(priceMovementShort, _f1)
    def _f2(p=J.undefined, *_args):
        return ("green" if J.gt(p, 0) else "red")
    color20 = G_for_every(priceMovementMed, _f2)
    def _f3(p=J.undefined, *_args):
        return ("green" if J.gt(p, 0) else "red")
    color60 = G_for_every(priceMovementLong, _f3)
    volatilityShortPeriod = J.get(G_input, "number")("Volatility Short Period", 20, J.obj(("min", 1)))
    volatilityLongPeriod = J.get(G_input, "number")("Volatility Long Period", 250, J.obj(("min", 1)))
    def _f4(h=J.undefined, l=J.undefined, c=J.undefined, *_args):
        return J.mul(J.div(J.sub(h, l), c), 100)
    myRangePercentage = G_for_every(G_high, G_low, G_close, _f4)
    myShortAvgRange = G_sma(myRangePercentage, volatilityShortPeriod)
    myLongAvgRange = G_sma(myRangePercentage, volatilityLongPeriod)
    myCurrentRange = J.get(myRangePercentage, J.sub(J.get(myRangePercentage, "length"), 1))
    myCurrentShortAvg = J.get(myShortAvgRange, J.sub(J.get(myShortAvgRange, "length"), 1))
    myCurrentLongAvg = J.get(myLongAvgRange, J.sub(J.get(myLongAvgRange, "length"), 1))
    indexTicker = J.get(G_input, "symbol")("Index Ticker", "SPY")
    indexData = J.get(G_request, "history")(indexTicker, "D")
    G_assert((not J.truthy(J.get(indexData, "error"))), J.template("Error fetching data for ", indexTicker, ": ", J.get(indexData, "error")))
    lastClose = J.get(J.get(indexData, "close"), J.sub(J.get(J.get(indexData, "close"), "length"), 1))
    prevClose = J.get(J.get(indexData, "close"), J.sub(J.get(J.get(indexData, "close"), "length"), 2))
    percentMove = J.div(J.sub(lastClose, prevClose), prevClose)
    def calculateDailyMove(open=J.undefined, close=J.undefined, *_args):
        return J.div(J.sub(close, open), open)
    currentDayOpen = J.get(G_open, J.sub(J.get(G_open, "length"), 1))
    currentDayClose = J.get(G_close, J.sub(J.get(G_close, "length"), 1))
    dailyMovePercentage = calculateDailyMove(currentDayOpen, currentDayClose)
    G_paint_overlay("Overlay", J.obj(("position", "top_right"), ("offset_x", (-60)), ("offset_y", 20)), J.obj(("rows", J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", "Price Movement"), ("color", "var(--text-color)"))]))), J.obj(("cells", J.JSArray([J.obj(("chart", J.obj(("width", "100px"), ("height", "30px"), ("type", "bubble"), ("options", J.obj(("scales", J.obj(("x", J.obj(("display", False))), ("y", J.obj(("display", False))))), ("plugins", J.obj(("legend", J.obj(("display", False))))))), ("data", J.obj(("datasets", J.JSArray([J.obj(("data", J.JSArray([J.obj(("x", 0), ("y", 0), ("r", 10)), J.obj(("x", 1), ("y", 0), ("r", 10)), J.obj(("x", 2), ("y", 0), ("r", 10))])), ("backgroundColor", J.JSArray([J.get(color5, J.sub(J.get(color5, "length"), 1)), J.get(color20, J.sub(J.get(color20, "length"), 1)), J.get(color60, J.sub(J.get(color60, "length"), 1))])))])))))))]))), J.obj(("cells", J.JSArray([J.obj(("text", " 5d    20d    60d"), ("color", "var(--text-color)"))]))), J.obj(("cells", J.JSArray([J.obj(("text", " "), ("color", "var(--text-color)"))]))), J.obj(("cells", J.JSArray([J.obj(("text", "Period Volatility"), ("color", "var(--text-color)"))]))), J.obj(("cells", J.JSArray([J.obj(("text", J.template("Current:")), ("color", "var(--text-color)")), J.obj(("text", J.template(myFormatValue(myCurrentRange))), ("color", ("green" if J.ge(myCurrentRange, 0) else "red")))]))), J.obj(("cells", J.JSArray([J.obj(("text", J.template(volatilityShortPeriod, "-bar Avg:")), ("color", "var(--text-color)")), J.obj(("text", J.template(myFormatValue(myCurrentShortAvg))), ("color", ("green" if J.ge(myCurrentShortAvg, 0) else "red")))]))), J.obj(("cells", J.JSArray([J.obj(("text", J.template(volatilityLongPeriod, "-bar Avg:")), ("color", "var(--text-color)")), J.obj(("text", J.template(myFormatValue(myCurrentLongAvg))), ("color", ("green" if J.ge(myCurrentLongAvg, 0) else "red")))]))), J.obj(("cells", J.JSArray([J.obj(("text", " "), ("color", "var(--text-color)"))]))), J.obj(("cells", J.JSArray([J.obj(("text", "Index Comparison"), ("color", "var(--text-color)"))]))), J.obj(("cells", J.JSArray([J.obj(("text", J.template(J.get(G_current, "ticker"), " Day Move:")), ("color", "var(--text-color)")), J.obj(("text", J.template(formatPercentage(dailyMovePercentage))), ("color", ("green" if J.ge(percentMove, 0) else "red")))]))), J.obj(("cells", J.JSArray([J.obj(("text", J.template(indexTicker, " Day Move:")), ("color", "var(--text-color)")), J.obj(("text", J.template(formatPercentage(percentMove))), ("color", ("green" if J.ge(percentMove, 0) else "red")))])))]))))


register_store_indicator(
    script,
    name='at_a_glance_overlay_TS',
    title='At-A-Glance Overlay',
    developer='Connor Robbins',
    url='https://trendspider.com/trading-tools-store/indicators/68abda-at-a-glance-overlay/',
    position='price',
    inputs=[{'id': 'volatility_short_period', 'title': 'Volatility Short Period', 'type': 'number', 'default': 20}, {'id': 'volatility_long_period', 'title': 'Volatility Long Period', 'type': 'number', 'default': 250}, {'id': 'sym-index_ticker', 'title': 'Index Ticker', 'type': 'symbol-search', 'default': 'SPY'}],
    outputs=[],
    signals=[],
    requires=['history'],
    parity='exact',
)
