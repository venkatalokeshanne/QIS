"""
Analyst Ratings on Chart -- TrendSpider store indicator by TrendSpider Team.

Registered as "analyst_ratings_on_chart_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/analyst-ratings-on-chart/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Array = G["Array"]
    G_Error = G["Error"]
    G_color_candles = G["color_candles"]
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_paint = G["paint"]
    G_request = G["request"]
    G_time = G["time"]
    G_describe_indicator("Analyst Estimates: Reports")
    ratings = J.get(G_request, "analyst_ratings")(J.get(G_constants, "ticker"))
    if (not J.truthy(J.get(G_Array, "isArray")(ratings))):
        raise J.js_throw(G_Error("No Analyst reports for a given symbol"))
    def _f1(item=J.undefined, *_args):
        return J.eq(J.get(item, "ratingCurrent"), "buy")
    buys = J.get(ratings, "filter")(_f1)
    def _f2(item=J.undefined, *_args):
        return J.eq(J.get(item, "ratingCurrent"), "sell")
    sells = J.get(ratings, "filter")(_f2)
    def _f3(item=J.undefined, *_args):
        return J.eq(J.get(item, "ratingCurrent"), "hold")
    holds = J.get(ratings, "filter")(_f3)
    def landReportsOntoCurrentCandles(reports=J.undefined, *_args):
        def _f1(item=J.undefined, *_args):
            return J.get(item, "timestamp")
        def _f2(report=J.undefined, *_args):
            return J.JSArray([report])
        def _f3(existingReports=J.undefined, newReport=J.undefined, *_args):
            return J.JSArray([*J.spread(existingReports), J.get(newReport, 0)])
        return G_land_points_onto_series(J.get(reports, "map")(_f1), J.get(reports, "map")(_f2), G_time, "ge", _f3)
    buysLanded = landReportsOntoCurrentCandles(buys)
    sellsLanded = landReportsOntoCurrentCandles(sells)
    holdsLanded = landReportsOntoCurrentCandles(holds)
    def _f4(b=J.undefined, s=J.undefined, h=J.undefined, *_args):
        def _f2(report=J.undefined, *_args):
            return (_t1 if J.truthy(_t1 := J.eq(J.get(report, "ratingPrior"), "hold")) else J.eq(J.get(report, "ratingPrior"), "sell"))
        bIsUpgrade = (J.get(b, "some")(_f2) if J.truthy(_t1 := b) else _t1)
        def _f4(report=J.undefined, *_args):
            return J.eq(J.get(report, "ratingPrior"), "sell")
        hIsUpgrade = (J.get(h, "some")(_f4) if J.truthy(_t3 := h) else _t3)
        if (J.truthy(bIsUpgrade) or J.truthy(hIsUpgrade)):
            return "blue"
        def _f6(report=J.undefined, *_args):
            return (_t1 if J.truthy(_t1 := J.eq(J.get(report, "ratingPrior"), "hold")) else J.eq(J.get(report, "ratingPrior"), "buy"))
        sIsDowngrade = (J.get(s, "some")(_f6) if J.truthy(_t5 := s) else _t5)
        def _f8(report=J.undefined, *_args):
            return J.eq(J.get(report, "ratingPrior"), "buy")
        hIsDowngrade = (J.get(h, "some")(_f8) if J.truthy(_t7 := h) else _t7)
        if (J.truthy(sIsDowngrade) or J.truthy(hIsDowngrade)):
            return "black"
    candleColor = G_for_every(buysLanded, sellsLanded, holdsLanded, _f4)
    G_color_candles(candleColor)
    def _f5(n=J.undefined, *_args):
        return (J.template("▲", J.get(n, "length")) if (n is not None) else None)
    buyLabels = J.get(buysLanded, "map")(_f5)
    def _f6(n=J.undefined, *_args):
        return (J.template("▼", J.get(n, "length")) if (n is not None) else None)
    sellLabels = J.get(sellsLanded, "map")(_f6)
    G_paint(buyLabels, J.obj(("style", "labels_above"), ("color", "green"), ("backgroundBorderRadius", 4), ("backgroundColor", "green")))
    G_paint(sellLabels, J.obj(("style", "labels_below"), ("color", "red"), ("backgroundBorderRadius", 4), ("backgroundColor", "red")))


register_store_indicator(
    script,
    name='analyst_ratings_on_chart_TS',
    title='Analyst Ratings on Chart',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/analyst-ratings-on-chart/',
    position='price',
    inputs=[],
    outputs=['cdl', 'line_2', 'line_3'],
    signals=[],
    requires=['analyst_ratings'],
    parity='exact',
)
