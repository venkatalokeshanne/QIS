"""
Seasonality Moving Average -- TrendSpider store indicator by TrendSpider Team.

Registered as "seasonality_moving_average_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/seasonality-moving-average/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
aapl_d: both-error, syn_5m: both-error.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_assert = G["assert"]
    G_close = G["close"]
    G_constants = G["constants"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_indicators = G["indicators"]
    G_input = G["input"]
    G_library = G["library"]
    G_paint = G["paint"]
    G_paint_label_at_line = G["paint_label_at_line"]
    G_request = G["request"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    G_describe_indicator("Seasonality Moving Average")
    maLength = J.get(G_input, "number")("MA Length", 20, J.obj(("min", 1)))
    maType = J.get(G_input, "select")("MA Type", "sma", J.get(G_constants, "ma_types"))
    computeMA = J.get(G_indicators, maType)
    ma = computeMA(G_close, maLength)
    moment = G_library("moment-timezone")
    seasonalityData = J.get(G_request, "seasonality")(J.get(G_current, "ticker"), "week_of_year", "change")
    G_assert((not J.truthy(J.get(seasonalityData, "error"))), J.template("Error fetching seasonality data: ", J.get(seasonalityData, "error")))
    def _f1(week=J.undefined, *_args):
        weekData = J.get(J.get(seasonalityData, "dataByCategory"), week)
        def _f1(d=J.undefined, *_args):
            return J.gt(J.get(d, "value"), 0)
        winCount = J.get(J.get(weekData, "filter")(_f1), "length")
        return J.mul(J.div(winCount, J.get(weekData, "length")), 100)
    weeklyWinRates = J.get(J.get(seasonalityData, "categories"), "map")(_f1)
    def getColor(winRate=J.undefined, *_args):
        if J.ge(winRate, 75):
            return "#00FF00"
        if J.ge(winRate, 51):
            return "#008000"
        if J.ge(winRate, 25):
            return "#FF0000"
        return "#FF00FF"
    def _f2(_t=J.undefined, *_args):
        weekOfYear = J.sub(J.get(moment(J.mul(_t, 1000)), "week")(), 1)
        winRate = J.get(weeklyWinRates, weekOfYear)
        return getColor(winRate)
    myColor = G_for_every(G_time, _f2)
    G_paint(ma, J.obj(("name", "MA"), ("color", myColor)))
    G_paint_label_at_line(G_paint(G_series_of(None), J.obj(("hidden", True))), J.sub(J.get(G_close, "length"), 1), "MA Color Legend:n≥75%: Bright Greenn51-74%: Greenn25-50%: Redn<25%: Bright Red", J.obj(("vertical_align", "top")))


register_store_indicator(
    script,
    name='seasonality_moving_average_TS',
    title='Seasonality Moving Average',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/seasonality-moving-average/',
    position='price',
    inputs=[{'id': 'ma_length', 'title': 'MA Length', 'type': 'number', 'default': 20}, {'id': 'ma_type', 'title': 'MA Type', 'type': 'select_wide', 'default': 'sma', 'options': ['ema', 'sma', 'wildma', 'vwma', 'wma', 'hullma', 'kama', 'alma', 'twap']}],
    outputs=[],
    signals=[],
    requires=['seasonality'],
    parity='aapl_d: both-error, syn_5m: both-error',
)
