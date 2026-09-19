"""
Analyst Estimates History -- TrendSpider store indicator by TrendSpider Team.

Registered as "analyst_estimates_history_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/analyst-estimates-history/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Array = G["Array"]
    G_Object = G["Object"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_input = G["input"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_library = G["library"]
    G_paint = G["paint"]
    G_request = G["request"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    def loadDataInPages(_p1=J.undefined, *_args):
        _t2 = _p1
        if _t2 is J.undefined:
            _t2 = 3
        maxPages = _t2
        data = J.JSArray([])
        mostDistantTimestamp = None
        pageIndex = 0
        while J.lt(pageIndex, maxPages):
            currentPageContent = (J.get(G_request, "analyst_ratings")(J.get(G_current, "ticker")) if J.seq(pageIndex, 0) else J.get(G_request, "analyst_ratings")(J.get(G_current, "ticker"), J.obj(("filters", J.JSArray([J.obj(("field", "timestamp"), ("filter", "less"), ("value", mostDistantTimestamp))])))))
            if (((not J.truthy(currentPageContent)) or J.truthy(J.get(currentPageContent, "error"))) or J.seq(J.get(currentPageContent, "length"), 0)):
                break
            mostDistantTimestamp = J.get(J.get(currentPageContent, 0), "timestamp")
            data = J.get(data, "concat")(currentPageContent)
            pageIndex = J.add(pageIndex, 1)
        def _f3(a=J.undefined, b=J.undefined, *_args):
            return J.sub(J.get(a, "timestamp"), J.get(b, "timestamp"))
        return J.get(data, "sort")(_f3)
    G_describe_indicator("Analyst Estimates History", J.obj(("warmup", 1200)))
    jstat = G_library("jstat")
    REPORT_RELEVANCE_DAYS = J.get(G_input, "number")("Report life time days", 120, J.obj(("min", 30), ("max", 600)))
    aeData = loadDataInPages(2)
    def _f1(record=J.undefined, *_args):
        return J.get(record, "timestamp")
    def _f2(existingPointValue=J.undefined, newPointValue=J.undefined, *_args):
        if (not J.truthy(existingPointValue)):
            return J.JSArray([newPointValue])
        return (J.JSArray([*J.spread(existingPointValue), newPointValue]) if J.truthy(J.get(G_Array, "isArray")(existingPointValue)) else J.JSArray([existingPointValue, newPointValue]))
    dataLanded = G_land_points_onto_series(J.get(aeData, "map")(_f1), aeData, G_time, "ge", _f2)
    maxEstimate = G_series_of(None)
    minEstimate = G_series_of(None)
    midEstimate = G_series_of(None)
    medianEstimate = G_series_of(None)
    lastReportByAnalyst = J.obj()
    lastMaxEstimate = None
    lastMinEstimate = None
    lastMidEstimate = None
    lastMedianEstimate = None
    candleIndex = 0
    while J.lt(candleIndex, J.get(G_time, "length")):
        reportsAtThatCandle = J.get(dataLanded, candleIndex)
        if J.truthy(reportsAtThatCandle):
            if (not J.truthy(J.get(G_Array, "isArray")(reportsAtThatCandle))):
                reportsAtThatCandle = J.JSArray([reportsAtThatCandle])
            for report in J.iter_of(reportsAtThatCandle):
                J.set(lastReportByAnalyst, J.get(report, "analystPerson"), report)
        lastReportsByAnalysts = J.get(G_Object, "values")(lastReportByAnalyst)
        def _f3(report_2=J.undefined, *_args):
            return (J.lt(J.sub(J.get(G_time, candleIndex), J.get(report_2, "timestamp")), J.mul(J.mul(REPORT_RELEVANCE_DAYS, 1440), 60)) if J.truthy(_t1 := J.gt(J.get(report_2, "pTarget"), 0)) else _t1)
        def _f4(report_2=J.undefined, *_args):
            return J.get(report_2, "pTarget")
        allEstimatesRelevantSoFar = J.get(J.get(lastReportsByAnalysts, "filter")(_f3), "map")(_f4)
        if J.gt(J.get(allEstimatesRelevantSoFar, "length"), 0):
            lastMaxEstimate = J.get(jstat, "max")(allEstimatesRelevantSoFar)
            lastMinEstimate = J.get(jstat, "min")(allEstimatesRelevantSoFar)
            lastMidEstimate = (_t5 if J.truthy(_t5 := J.get(jstat, "mean")(allEstimatesRelevantSoFar)) else lastMidEstimate)
            lastMedianEstimate = (_t6 if J.truthy(_t6 := J.get(jstat, "median")(allEstimatesRelevantSoFar)) else lastMedianEstimate)
        J.set(maxEstimate, candleIndex, lastMaxEstimate)
        J.set(minEstimate, candleIndex, lastMinEstimate)
        J.set(midEstimate, candleIndex, lastMidEstimate)
        J.set(medianEstimate, candleIndex, lastMedianEstimate)
        candleIndex = J.add(candleIndex, 1)
    G_paint(maxEstimate, J.obj(("name", "Max"), ("color", "lime"), ("ignoreWhenScaling", True)))
    G_paint(midEstimate, J.obj(("name", "Average"), ("color", "#ccc"), ("ignoreWhenScaling", True)))
    G_paint(medianEstimate, J.obj(("name", "Median"), ("color", "#777"), ("ignoreWhenScaling", True)))
    G_paint(minEstimate, J.obj(("name", "Min"), ("color", "red"), ("ignoreWhenScaling", True)))


register_store_indicator(
    script,
    name='analyst_estimates_history_TS',
    title='Analyst Estimates History',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/analyst-estimates-history/',
    position='price',
    inputs=[{'id': 'warmup', 'title': 'Warmup', 'type': 'number', 'default': 1200}, {'id': 'report_life_time_days', 'title': 'Report life time days', 'type': 'number', 'default': 120}],
    outputs=['max', 'average', 'median', 'min'],
    signals=[],
    requires=['analyst_ratings'],
    parity='exact',
)
