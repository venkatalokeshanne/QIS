"""
News Articles per Daily Candle -- TrendSpider store indicator by TrendSpider Team.

Registered as "news_articles_per_daily_candle_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/news-articles-per-daily-candle/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
aapl_d: OK, syn_5m: both-error.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Error = G["Error"]
    G_Object = G["Object"]
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_library = G["library"]
    G_paint = G["paint"]
    G_request = G["request"]
    G_time = G["time"]
    G_describe_indicator("News per day")
    if J.ne(J.get(G_constants, "resolution"), "D"):
        raise J.js_throw(G_Error("This script works on Daily time frame only"))
    moment = G_library("moment-timezone")
    BIG_DAY_RECORDS_MULTIPLIER = 2
    def dayAtTimestamp(timestamp=J.undefined, *_args):
        return J.get(moment(J.mul(timestamp, 1000)), "format")("DD MMM YYYY")
    news = J.get(G_request, "news")(J.get(G_constants, "ticker"))
    newsByDay = J.obj()
    for newsRecord in J.iter_of(news):
        day = dayAtTimestamp(J.get(newsRecord, "timestamp"))
        if (not J.truthy(J.get(newsByDay, day))):
            J.set(newsByDay, day, 0)
        J.set(newsByDay, day, J.add(J.get(newsByDay, day), 1))
    def _f1(result=J.undefined, records=J.undefined, *_args):
        return J.add(result, records)
    averageNewsPerDay = J.div(J.get(J.get(G_Object, "values")(newsByDay), "reduce")(_f1, 0), J.get(J.get(G_Object, "values")(newsByDay), "length"))
    bigDayMinNews = J.mul(BIG_DAY_RECORDS_MULTIPLIER, averageNewsPerDay)
    def _f2(timestamp=J.undefined, *_args):
        newsThatDay = J.get(newsByDay, dayAtTimestamp(timestamp))
        if J.gt(newsThatDay, bigDayMinNews):
            return newsThatDay
    bigNewsDays = G_for_every(G_time, _f2)
    def _f3(timestamp=J.undefined, *_args):
        newsThatDay = J.get(newsByDay, dayAtTimestamp(timestamp))
        if J.le(newsThatDay, bigDayMinNews):
            return newsThatDay
    normalNewsDays = G_for_every(G_time, _f3)
    G_paint(bigNewsDays, J.obj(("style", "labels_above"), ("backgroundColor", "blue"), ("color", "blue")))
    G_paint(normalNewsDays, J.obj(("style", "labels_above")))


register_store_indicator(
    script,
    name='news_articles_per_daily_candle_TS',
    title='News Articles per Daily Candle',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/news-articles-per-daily-candle/',
    position='price',
    inputs=[],
    outputs=['line_1', 'line_2'],
    signals=[],
    requires=['news'],
    parity='aapl_d: OK, syn_5m: both-error',
)
