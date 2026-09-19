"""
Post Market Change% (Anchored) -- TrendSpider store indicator by TrendSpider Team.

Registered as "post_market_change_anchored_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/post-market-change-anchored/)
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
    G_horizontal_line = G["horizontal_line"]
    G_paint = G["paint"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    G_time_of = G["time_of"]
    def calculatePercentageChange(currentPrice=J.undefined, openPrice=J.undefined, *_args):
        return J.mul(J.div(J.sub(currentPrice, openPrice), openPrice), 100)
    G_describe_indicator("Post-Market Change % (Anchored)", "lower", J.obj(("shortName", "PostM Change%"), ("decimals", "by_symbol_2x")))
    preMarketOpenHour = 16
    percentChangeSeries = G_series_of(None)
    preMarketOpenPrice = None
    anchorCandleFound = False
    currentDay = None
    i = 0
    while J.lt(i, J.get(G_time, "length")):
        date = G_time_of(J.get(G_time, i))
        day = J.get(date, "dayOfYear")
        if J.sne(day, currentDay):
            currentDay = day
            preMarketOpenPrice = None
            anchorCandleFound = False
        if ((not J.truthy(anchorCandleFound)) and J.ge(J.get(date, "hours"), preMarketOpenHour)):
            preMarketOpenPrice = J.get(G_close, i)
            anchorCandleFound = True
        if (preMarketOpenPrice is not None):
            J.set(percentChangeSeries, i, calculatePercentageChange(J.get(G_close, i), preMarketOpenPrice))
        else:
            J.set(percentChangeSeries, i, None)
        i = J.inc(i)
    G_paint(percentChangeSeries, J.obj(("name", "PostM Change %"), ("color", "#ff0000"), ("thickness", 2), ("style", "line")))
    G_paint(G_horizontal_line(0), "Zero Level", "black")


register_store_indicator(
    script,
    name='post_market_change_anchored_TS',
    title='Post Market Change% (Anchored)',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/post-market-change-anchored/',
    position='lower',
    inputs=[],
    outputs=['postm_change__', 'zero_level'],
    signals=[],
    requires=[],
    parity='exact',
)
