"""
World Bank Indicators - Poverty -- TrendSpider store indicator by TrendSpider.

Registered as "world_bank_indicators_poverty_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6a6294-world-bank-indicators-poverty/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Date = G["Date"]
    G_Object = G["Object"]
    G_assert = G["assert"]
    G_describe_indicator = G["describe_indicator"]
    G_input = G["input"]
    G_interpolate_sparse_series = G["interpolate_sparse_series"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_paint = G["paint"]
    G_parseInt = G["parseInt"]
    G_request = G["request"]
    G_time = G["time"]
    countries = J.obj(("Australia", "AUS"), ("Canada", "CAN"), ("China", "CHN"), ("European Union", "EUU"), ("Japan", "JPN"), ("Mexico", "MEX"), ("United Kingdom", "GBR"), ("United States", "USA"), ("World", "WLD"))
    validIndicatorIds = J.JSArray(["SI.DST.03RD.20", "EN.POP.SLUM.UR.ZS", "SI.DST.04TH.20", "SI.DST.02ND.20", "SI.DST.05TH.20", "SI.DST.50MD", "SI.DST.10TH.10", "SI.DST.FRST.10", "SI.DST.FRST.20", "SI.POV.DDAY", "SI.POV.GAPS", "SI.POV.LMIC", "SI.POV.GINI", "SI.POV.LMIC.GP", "SI.POV.UMIC", "SI.POV.UMIC.GP", "SI.SPR.PC40.ZG", "SI.SPR.PC40", "SI.SPR.PCAP", "SI.SPR.PCAP.ZG"])
    data = J.get(G_request, "http")(J.template("https://api.worldbank.org/v2/topic/11/indicator?per_page=1000&format=json"))
    def _f1(indicator=J.undefined, *_args):
        return J.get(validIndicatorIds, "includes")(J.get(indicator, "id"))
    currentTopicIndicators = J.get(J.get(data, 1), "filter")(_f1)
    def _f2(indicator=J.undefined, *_args):
        return J.get(indicator, "name")
    indicatorTitles = J.get(currentTopicIndicators, "map")(_f2)
    currentIndicatorTitle = J.get(G_input, "select")("Indicator", J.get(indicatorTitles, 0), indicatorTitles)
    def _f3(indicator=J.undefined, *_args):
        return J.eq(J.get(indicator, "name"), currentIndicatorTitle)
    currentIndicator = J.get(currentTopicIndicators, "find")(_f3)
    indicatorId = J.get(currentIndicator, "id")
    def _f4(str=J.undefined, *_args):
        return (J.add(J.get(str, "slice")(0, J.sub(80, 3)), "...") if J.gt(J.get(str, "length"), 80) else str)
    indicatorNote = _f4(J.get(currentIndicator, "sourceNote"))
    G_describe_indicator(J.template("World Bank Indicators - Poverty"), "lower", J.obj(("citation", indicatorNote), ("shortName", J.template("WBI Poverty"))))
    country = J.get(G_input, "select")("Country", "United States", J.get(G_Object, "keys")(countries))
    indicatorData = J.get(G_request, "http")(J.template("https://api.worldbank.org/v2/country/", J.get(countries, country), "/indicator/", indicatorId, "?format=json&per_page=20000"))
    def _f6(d=J.undefined, *_args):
        return (J.sne(J.get(d, "value"), "") if J.truthy(_t1 := (J.get(d, "value") is not None)) else _t1)
    G_assert((J.get(J.get(indicatorData, 1), "some")(_f6) if J.truthy(_t5 := J.get(indicatorData, 1)) else _t5), J.template("The selected indicator doesn't return any data for \"", country, "\"."))
    def _f7(record=J.undefined, *_args):
        year = G_parseInt(J.get(record, "date"))
        milliseconds = J.get(G_Date, "UTC")(year, 0, 1)
        return J.div(milliseconds, 1000)
    indicatorTimestamps = J.get(J.get(J.get(indicatorData, 1), "map")(_f7), "reverse")()
    def _f8(record=J.undefined, *_args):
        return (_t1 if J.truthy(_t1 := J.pos(J.get(record, "value"))) else None)
    indicatorValues = J.get(J.get(J.get(indicatorData, 1), "map")(_f8), "reverse")()
    def _f9(a=J.undefined, v=J.undefined, i=J.undefined, *_args):
        return (a := (i if (v is not None) else a))
    lastIndexWithValue = J.get(indicatorValues, "reduce")(_f9, 0)
    isLastValueOlderThanCandles = J.lt(J.get(indicatorTimestamps, lastIndexWithValue), J.get(G_time, 0))
    if J.truthy(isLastValueOlderThanCandles):
        J.get(indicatorTimestamps, "push")(J.get(G_time, 0))
        J.get(indicatorValues, "push")(J.get(indicatorValues, lastIndexWithValue))
    indicatorLine = G_interpolate_sparse_series(G_land_points_onto_series(indicatorTimestamps, G_interpolate_sparse_series(indicatorValues), G_time, "ge"), "constant")
    G_paint(indicatorLine, "Line", "#469e48")


register_store_indicator(
    script,
    name='world_bank_indicators_poverty_TS',
    title='World Bank Indicators - Poverty',
    developer='TrendSpider',
    url='https://trendspider.com/trading-tools-store/indicators/6a6294-world-bank-indicators-poverty/',
    position='lower',
    inputs=[{'id': 'indicator', 'title': 'Indicator', 'type': 'select_wide', 'default': 'Indicator SI.DST.FRST.20', 'options': ['Indicator SI.DST.FRST.20', 'Indicator SI.POV.DDAY', 'Indicator SI.DST.03RD.20', 'Indicator EN.POP.SLUM.UR.ZS', 'Indicator SI.DST.04TH.20', 'Indicator SI.DST.02ND.20', 'Indicator SI.DST.05TH.20', 'Indicator SI.DST.50MD', 'Indicator SI.DST.10TH.10', 'Indicator SI.DST.FRST.10', 'Indicator SI.POV.GAPS', 'Indicator SI.POV.LMIC', 'Indicator SI.POV.GINI', 'Indicator SI.POV.LMIC.GP', 'Indicator SI.POV.UMIC', 'Indicator SI.POV.UMIC.GP', 'Indicator SI.SPR.PC40.ZG', 'Indicator SI.SPR.PC40', 'Indicator SI.SPR.PCAP', 'Indicator SI.SPR.PCAP.ZG']}, {'id': 'country', 'title': 'Country', 'type': 'select_wide', 'default': 'United States', 'options': ['Australia', 'Canada', 'China', 'European Union', 'Japan', 'Mexico', 'United Kingdom', 'United States', 'World']}],
    outputs=['line'],
    signals=[],
    requires=['http'],
    parity='exact',
)
