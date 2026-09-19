"""
Daily Candles over Intraday Candles -- TrendSpider store indicator by TrendSpider Team.

Registered as "daily_candles_over_intraday_candles_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/daily-candles-over-intraday-candles/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
aapl_d: both-error, syn_5m: OK.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_fill = G["fill"]
    G_high = G["high"]
    G_line = G["line"]
    G_low = G["low"]
    G_open = G["open"]
    G_paint = G["paint"]
    G_series_of = G["series_of"]
    G_session_of = G["session_of"]
    G_time = G["time"]
    def paintCandle(dailyCandle=J.undefined, firstIndex_2=J.undefined, lastIndex=J.undefined, topLinesStorage=J.undefined, bottomLinesStorage=J.undefined, *_args):
        bodyTop = J.get(G_Math, "max")(J.get(dailyCandle, "open"), J.get(dailyCandle, "close"))
        bodyBottom = J.get(G_Math, "min")(J.get(dailyCandle, "open"), J.get(dailyCandle, "close"))
        middleIndex = J.get(G_Math, "floor")(J.div(J.add(lastIndex, firstIndex_2), 2))
        bigTopLine = G_line(firstIndex_2, bodyTop, lastIndex, bodyTop, False)
        J.set(bigTopLine, middleIndex, J.get(dailyCandle, "high"))
        J.set(bigTopLine, J.add(middleIndex, 1), J.get(dailyCandle, "high"))
        bigBottomLine = G_line(firstIndex_2, bodyBottom, lastIndex, bodyBottom, False)
        J.set(bigBottomLine, middleIndex, J.get(dailyCandle, "low"))
        J.set(bigBottomLine, J.add(middleIndex, 1), J.get(dailyCandle, "low"))
        candleIndex = firstIndex_2
        while J.le(candleIndex, lastIndex):
            J.set(topLinesStorage, candleIndex, J.get(bigTopLine, candleIndex))
            J.set(bottomLinesStorage, candleIndex, J.get(bigBottomLine, candleIndex))
            candleIndex = J.add(candleIndex, 1)
    G_describe_indicator("Daily candles")
    topGreenLines = G_series_of(None)
    bottomGreenLines = G_series_of(None)
    topRedLines = G_series_of(None)
    bottomRedLines = G_series_of(None)
    firstIndex = 0
    candleIndex = 1
    while J.lt(candleIndex, J.get(G_close, "length")):
        sessionChanged = J.sne(J.get(G_session_of(J.get(G_time, candleIndex)), "session"), J.get(G_session_of(J.get(G_time, J.sub(candleIndex, 1))), "session"))
        if ((not J.truthy(sessionChanged)) and J.ne(candleIndex, J.sub(J.get(G_close, "length"), 1))):
            candleIndex = J.inc(candleIndex)
            continue
        lastIndex = J.sub(candleIndex, 1)
        dailyCandle = J.obj(("open", J.get(G_open, firstIndex)), ("high", J.get(G_Math, "max")(*J.spread(J.get(G_high, "slice")(firstIndex, J.add(lastIndex, 1))))), ("low", J.get(G_Math, "min")(*J.spread(J.get(G_low, "slice")(firstIndex, J.add(lastIndex, 1))))), ("close", J.get(G_close, lastIndex)))
        if J.gt(J.get(dailyCandle, "close"), J.get(dailyCandle, "open")):
            paintCandle(dailyCandle, firstIndex, lastIndex, topGreenLines, bottomGreenLines)
        else:
            paintCandle(dailyCandle, firstIndex, lastIndex, topRedLines, bottomRedLines)
        firstIndex = candleIndex
        candleIndex = J.inc(candleIndex)
    G_fill(G_paint(topGreenLines, "Green top", "green", "ladder"), G_paint(bottomGreenLines, "Green bottom", "green", "ladder"), "green")
    G_fill(G_paint(topRedLines, "Red top", "red", "ladder"), G_paint(bottomRedLines, "Red bottom", "red", "ladder"), "red")


register_store_indicator(
    script,
    name='daily_candles_over_intraday_candles_TS',
    title='Daily Candles over Intraday Candles',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/daily-candles-over-intraday-candles/',
    position='price',
    inputs=[],
    outputs=[],
    signals=[],
    requires=[],
    parity='aapl_d: both-error, syn_5m: OK',
)
