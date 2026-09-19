"""
Analyst Targets by Price -- TrendSpider store indicator by TrendSpider Team.

Registered as "analyst_targets_by_price_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/analyst-targets-by-price/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Array = G["Array"]
    G_Math = G["Math"]
    G_Object = G["Object"]
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_fill = G["fill"]
    G_input = G["input"]
    G_paint = G["paint"]
    G_parseFloat = G["parseFloat"]
    G_request = G["request"]
    G_series_of = G["series_of"]
    G_describe_indicator("Analyst Price Targets")
    J.get(G_input, "number")("offset", 30, J.obj(("hidden", True)))
    BUCKETS = 20
    STRIP_WIDTH_CANDLES = 25
    ratings = J.get(G_request, "analyst_ratings")(J.get(G_constants, "ticker"))
    def _f1(result=J.undefined, report=J.undefined, *_args):
        if (not J.truthy(G_parseFloat(J.get(report, "pTarget")))):
            return result
        J.set(result, J.get(report, "analystCompany"), report)
        return result
    lastReportsByAnalyst = J.get(ratings, "reduce")(_f1, J.obj())
    lastReports = J.get(G_Object, "values")(lastReportsByAnalyst)
    def _f2(report=J.undefined, *_args):
        return J.pos(J.get(report, "pTarget"))
    priceTargets = J.get(lastReports, "map")(_f2)
    maxTarget = J.get(G_Math, "max")(*J.spread(priceTargets))
    minTarget = J.get(G_Math, "min")(*J.spread(priceTargets))
    bucketSize = J.div(J.sub(maxTarget, minTarget), BUCKETS)
    reportsByBucket = J.obj()
    for report in J.iter_of(lastReports):
        bucketIndex = J.get(G_Math, "round")(J.div(J.sub(J.get(report, "pTarget"), minTarget), bucketSize))
        if (not J.truthy(J.get(reportsByBucket, bucketIndex))):
            J.set(reportsByBucket, bucketIndex, 0)
        J.set(reportsByBucket, bucketIndex, J.add(J.get(reportsByBucket, bucketIndex), 1))
    maxReportsAtBucket = J.get(G_Math, "max")(*J.spread(J.get(G_Object, "values")(reportsByBucket)))
    bucketIndex_2 = 0
    while J.lt(bucketIndex_2, BUCKETS):
        if (not J.truthy(J.get(reportsByBucket, "hasOwnProperty")(bucketIndex_2))):
            G_fill(G_paint(G_series_of(None), J.obj(("hidden", True))), G_paint(G_series_of(None), J.obj(("hidden", True))), "#00dcff")
            bucketIndex_2 = J.add(bucketIndex_2, 1)
            continue
        levelValueNormalized = J.div(J.get(reportsByBucket, bucketIndex_2), maxReportsAtBucket)
        progressLengthInCandles = J.get(G_Math, "round")(J.mul(STRIP_WIDTH_CANDLES, levelValueNormalized))
        if J.seq(progressLengthInCandles, 0):
            G_fill(G_paint(G_series_of(None), J.obj(("hidden", True))), G_paint(G_series_of(None), J.obj(("hidden", True))), "#00dcff")
            bucketIndex_2 = J.add(bucketIndex_2, 1)
            continue
        margin = J.div(bucketSize, 20)
        topPrice = J.add(minTarget, J.mul(J.add(bucketIndex_2, 1), bucketSize))
        top = J.get(G_series_of(None), "slice")(0, J.neg(progressLengthInCandles))
        def _f3(*_args):
            return topPrice
        J.get(top, "push")(*J.spread(J.get(J.JSArray([*J.spread(G_Array(progressLengthInCandles))]), "map")(_f3)))
        bottomPrice = J.add(J.add(minTarget, margin), J.mul(bucketIndex_2, bucketSize))
        bottom = J.get(G_series_of(None), "slice")(0, J.neg(progressLengthInCandles))
        def _f4(*_args):
            return bottomPrice
        J.get(bottom, "push")(*J.spread(J.get(J.JSArray([*J.spread(G_Array(progressLengthInCandles))]), "map")(_f4)))
        G_fill(G_paint(top, J.obj(("hidden", True))), G_paint(bottom, J.obj(("hidden", True))), "#00dcff")
        bucketIndex_2 = J.add(bucketIndex_2, 1)
    wick = G_series_of(None)
    J.set(wick, J.sub(J.get(wick, "length"), 1), J.obj(("high", maxTarget), ("low", minTarget)))
    G_paint(wick, J.obj(("color", "blue"), ("style", "columnrange"), ("editorHidden", True)))


register_store_indicator(
    script,
    name='analyst_targets_by_price_TS',
    title='Analyst Targets by Price',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/analyst-targets-by-price/',
    position='price',
    inputs=[],
    outputs=['line_1', 'line_2', 'line_4', 'line_5', 'line_7', 'line_8', 'line_10', 'line_11', 'line_13', 'line_14', 'line_16', 'line_17', 'line_19', 'line_20', 'line_22', 'line_23', 'line_25', 'line_26', 'line_28', 'line_29', 'line_31', 'line_32', 'line_34', 'line_35', 'line_37', 'line_38', 'line_40', 'line_41', 'line_43', 'line_44', 'line_46', 'line_47', 'line_49', 'line_50', 'line_52', 'line_53', 'line_55', 'line_56', 'line_58', 'line_59', 'line_61'],
    signals=[],
    requires=['analyst_ratings'],
    parity='exact',
)
