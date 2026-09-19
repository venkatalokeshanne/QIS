"""
Analyst Estimates: Analyst Consensus -- TrendSpider store indicator by TrendSpider Team.

Registered as "analyst_estimates_analyst_consensus_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/analyst-ratings-over-time/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_close = G["close"]
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_paint = G["paint"]
    G_request = G["request"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    G_describe_indicator("Analyst Estimates: Analyst Consensus", "lower")
    COLOR_BUY_DOMINATING = "#22ab94"
    COLOR_BUY = "#a0dcd2"
    COLOR_SELL_DOMINATING = "#e31d1d"
    COLOR_SELL = "#d8a2a2"
    COLOR_HOLD = "#a9a9a9"
    ratingSeries = J.obj(("buy", G_series_of(0)), ("sell", G_series_of(0)), ("hold", G_series_of(0)))
    ratings = J.get(G_request, "analyst_ratings")(J.get(G_constants, "ticker"))
    def _f1(item=J.undefined, *_args):
        return J.get(item, "timestamp")
    def _f2(rating=J.undefined, *_args):
        return J.JSArray([rating])
    def _f3(existingRatings=J.undefined, newRating=J.undefined, *_args):
        return J.JSArray([*J.spread(existingRatings), J.get(newRating, 0)])
    ratingsLanded = G_land_points_onto_series(J.get(ratings, "map")(_f1), J.get(ratings, "map")(_f2), G_time, "ge", _f3)
    analystsAlreadyPainted = J.JSArray([])
    candleIndex = 1
    while J.lt(candleIndex, J.get(G_close, "length")):
        J.set(J.get(ratingSeries, "buy"), candleIndex, J.get(J.get(ratingSeries, "buy"), J.sub(candleIndex, 1)))
        J.set(J.get(ratingSeries, "sell"), candleIndex, J.get(J.get(ratingSeries, "sell"), J.sub(candleIndex, 1)))
        J.set(J.get(ratingSeries, "hold"), candleIndex, J.get(J.get(ratingSeries, "hold"), J.sub(candleIndex, 1)))
        ratings_2 = (_t4 if J.truthy(_t4 := J.get(ratingsLanded, candleIndex)) else J.JSArray([]))
        def _f5(rating=J.undefined, *_args):
            J.update_member(J.get(ratingSeries, J.get(rating, "ratingCurrent")), candleIndex, J.inc, True)
            if (J.truthy(J.get(rating, "ratingPrior")) and J.truthy(J.get(analystsAlreadyPainted, "includes")(J.get(rating, "analystCompany")))):
                J.update_member(J.get(ratingSeries, J.get(rating, "ratingPrior")), candleIndex, J.dec, True)
            J.get(analystsAlreadyPainted, "push")(J.get(rating, "analystCompany"))
        J.get(ratings_2, "forEach")(_f5)
        candleIndex = J.inc(candleIndex)
    def _f6(buys=J.undefined, sells=J.undefined, *_args):
        return (COLOR_BUY_DOMINATING if J.gt(buys, sells) else COLOR_BUY)
    buyColors = G_for_every(J.get(ratingSeries, "buy"), J.get(ratingSeries, "sell"), _f6)
    G_paint(J.get(ratingSeries, "buy"), J.obj(("style", "stacked_histogram"), ("name", "Buy"), ("stacking", "percent"), ("padding", 0), ("color", buyColors)))
    def _f7(buys=J.undefined, sells=J.undefined, *_args):
        return (COLOR_SELL_DOMINATING if J.gt(sells, buys) else COLOR_SELL)
    sellColors = G_for_every(J.get(ratingSeries, "buy"), J.get(ratingSeries, "sell"), _f7)
    G_paint(J.get(ratingSeries, "sell"), J.obj(("style", "stacked_histogram"), ("name", "Sell"), ("stacking", "percent"), ("padding", 0), ("color", sellColors)))
    G_paint(J.get(ratingSeries, "hold"), J.obj(("style", "stacked_histogram"), ("name", "Hold"), ("color", COLOR_HOLD), ("stacking", "percent"), ("padding", 0)))


register_store_indicator(
    script,
    name='analyst_estimates_analyst_consensus_TS',
    title='Analyst Estimates: Analyst Consensus',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/analyst-ratings-over-time/',
    position='lower',
    inputs=[],
    outputs=['buy', 'sell', 'hold'],
    signals=[],
    requires=['analyst_ratings'],
    parity='exact',
)
