"""
Opening Range Breakout Strategy -- TrendSpider store indicator by TrendSpider Team.

Registered as "opening_range_breakout_strategy_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/opening-range-breakout-strategy/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Infinity = G["Infinity"]
    G_atr = G["atr"]
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_high = G["high"]
    G_input = G["input"]
    G_low = G["low"]
    G_open = G["open"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    G_time_of = G["time_of"]
    def getOpeningRangeHighLow(*_args):
        openingRangeHighs_2 = G_series_of(None)
        openingRangeLows_2 = G_series_of(None)
        currentDay = None
        openingRangeHigh = J.neg(G_Infinity)
        openingRangeLow = G_Infinity
        i = 0
        while J.lt(i, J.get(G_time, "length")):
            date = G_time_of(J.get(G_time, i))
            day = J.get(date, "dayOfYear")
            if J.sne(day, currentDay):
                currentDay = day
                openingRangeHigh = J.neg(G_Infinity)
                openingRangeLow = G_Infinity
            if ((J.gt(J.get(date, "hours"), startHour) or (J.seq(J.get(date, "hours"), startHour) and J.ge(J.get(date, "minutes"), startMinute))) and (J.lt(J.get(date, "hours"), endHour) or (J.seq(J.get(date, "hours"), endHour) and J.le(J.get(date, "minutes"), endMinute)))):
                if J.gt(J.get(G_high, i), openingRangeHigh):
                    openingRangeHigh = J.get(G_high, i)
                if J.lt(J.get(G_low, i), openingRangeLow):
                    openingRangeLow = J.get(G_low, i)
            J.set(openingRangeHighs_2, i, openingRangeHigh)
            J.set(openingRangeLows_2, i, openingRangeLow)
            i = J.inc(i)
        return J.obj(("openingRangeHighs", openingRangeHighs_2), ("openingRangeLows", openingRangeLows_2))
    G_describe_indicator("Opening Range Breakout Strategy with ATR", "price")
    startHour = J.get(G_input, "number")("Start Hour", 9, J.obj(("min", 0), ("max", 23)))
    startMinute = J.get(G_input, "number")("Start Minute", 30, J.obj(("min", 0), ("max", 59)))
    endHour = J.get(G_input, "number")("End Hour", 10, J.obj(("min", 0), ("max", 23)))
    endMinute = J.get(G_input, "number")("End Minute", 30, J.obj(("min", 0), ("max", 59)))
    atrLength = J.get(G_input, "number")("ATR Length", 14, J.obj(("min", 1), ("max", 50)))
    atrMultiplier = J.get(G_input, "number")("ATR Multiplier", 2, J.obj(("min", 0.5), ("max", 10), ("step", 0.1)))
    tradeStartHour = 10
    tradeStartMinute = 30
    tradeEndHour = 15
    tradeEndMinute = 30
    atrValues = G_atr(G_close, G_high, G_low, atrLength)
    inTrade = False
    entryPrice = 0
    stopLossLevel = 0
    takeProfitLevel = 0
    buyLabels = G_series_of(None)
    sellLabels = G_series_of(None)
    stopLossLine = G_series_of(None)
    takeProfitLine = G_series_of(None)
    _t1 = J.require_object(getOpeningRangeHighLow())
    openingRangeHighs = J.get(_t1, "openingRangeHighs")
    openingRangeLows = J.get(_t1, "openingRangeLows")
    G_paint(openingRangeHighs, J.obj(("style", "line"), ("color", "red"), ("thickness", 2), ("name", "Opening Range High")))
    G_paint(openingRangeLows, J.obj(("style", "line"), ("color", "blue"), ("thickness", 2), ("name", "Opening Range Low")))
    i = atrLength
    while J.lt(i, J.get(G_close, "length")):
        date = G_time_of(J.get(G_time, i))
        isInTradingWindow = ((_t5 if J.truthy(_t5 := J.lt(J.get(date, "hours"), tradeEndHour)) else (J.le(J.get(date, "minutes"), tradeEndMinute) if J.truthy(_t6 := J.seq(J.get(date, "hours"), tradeEndHour)) else _t6)) if J.truthy(_t2 := (_t3 if J.truthy(_t3 := J.gt(J.get(date, "hours"), tradeStartHour)) else (J.ge(J.get(date, "minutes"), tradeStartMinute) if J.truthy(_t4 := J.seq(J.get(date, "hours"), tradeStartHour)) else _t4))) else _t2)
        if ((((not J.truthy(inTrade)) and J.truthy(isInTradingWindow)) and J.lt(J.get(G_close, J.sub(i, 1)), J.get(openingRangeHighs, J.sub(i, 1)))) and J.gt(J.get(G_close, i), J.get(openingRangeHighs, i))):
            inTrade = True
            entryPrice = J.get(G_open, J.add(i, 1))
            atrValue = J.get(atrValues, i)
            stopLossLevel = J.sub(entryPrice, J.mul(atrMultiplier, atrValue))
            takeProfitLevel = J.add(entryPrice, J.mul(atrMultiplier, atrValue))
            J.set(buyLabels, J.add(i, 1), "Buy")
            J.set(stopLossLine, J.add(i, 1), stopLossLevel)
            J.set(takeProfitLine, J.add(i, 1), takeProfitLevel)
        if J.truthy(inTrade):
            if J.le(J.get(G_close, i), stopLossLevel):
                inTrade = False
                J.set(sellLabels, i, "Sell (SL)")
            if J.ge(J.get(G_close, i), takeProfitLevel):
                inTrade = False
                J.set(sellLabels, i, "Sell (TP)")
            J.set(stopLossLine, i, stopLossLevel)
            J.set(takeProfitLine, i, takeProfitLevel)
        i = J.inc(i)
    G_paint(stopLossLine, J.obj(("name", "Stop Loss"), ("color", "red"), ("style", "line"), ("thickness", 1)))
    G_paint(takeProfitLine, J.obj(("name", "Take Profit"), ("color", "green"), ("style", "line"), ("thickness", 1)))
    G_paint(buyLabels, J.obj(("style", "labels_below"), ("backgroundColor", "green"), ("color", "green")))
    G_paint(sellLabels, J.obj(("style", "labels_above"), ("backgroundColor", "red"), ("color", "red")))
    G_register_signal(buyLabels, "Buy")
    G_register_signal(sellLabels, "Sell")


register_store_indicator(
    script,
    name='opening_range_breakout_strategy_TS',
    title='Opening Range Breakout Strategy',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/opening-range-breakout-strategy/',
    position='price',
    inputs=[{'id': 'start_hour', 'title': 'Start Hour', 'type': 'number', 'default': 9}, {'id': 'start_minute', 'title': 'Start Minute', 'type': 'number', 'default': 30}, {'id': 'end_hour', 'title': 'End Hour', 'type': 'number', 'default': 10}, {'id': 'end_minute', 'title': 'End Minute', 'type': 'number', 'default': 30}, {'id': 'atr_length', 'title': 'ATR Length', 'type': 'number', 'default': 14}, {'id': 'atr_multiplier', 'title': 'ATR Multiplier', 'type': 'number', 'default': 2}],
    outputs=['opening_range_high', 'opening_range_low', 'stop_loss', 'take_profit', 'line_5', 'line_6', 'buy', 'sell'],
    signals=['buy', 'sell'],
    requires=[],
    parity='exact',
)
