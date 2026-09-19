"""
World Bank Indicators - Social Protection & Labor -- TrendSpider store indicator by TrendSpider.

Registered as "world_bank_indicators_social_protection_labor_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6a6295-world-bank-indicators-social-protection-labor/)
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
    validIndicatorIds = J.JSArray(["SL.AGR.EMPL.MA.ZS", "SL.EMP.1524.SP.FE.NE.ZS", "SL.AGR.EMPL.ZS", "SL.AGR.EMPL.FE.ZS", "SL.EMP.1524.SP.MA.NE.ZS", "SL.EMP.1524.SP.MA.ZS", "SL.EMP.1524.SP.FE.ZS", "SL.EMP.1524.SP.ZS", "SL.EMP.MPYR.FE.ZS", "SL.EMP.MPYR.MA.ZS", "SL.EMP.MPYR.ZS", "SL.EMP.SELF.MA.ZS", "SL.EMP.SELF.ZS", "SL.EMP.SELF.FE.ZS", "SL.EMP.TOTL.SP.FE.NE.ZS", "SL.EMP.TOTL.SP.MA.NE.ZS", "SL.EMP.SMGT.FE.ZS", "SL.EMP.1524.SP.NE.ZS", "SL.EMP.TOTL.SP.MA.ZS", "SL.EMP.TOTL.SP.ZS", "SL.EMP.TOTL.SP.FE.ZS", "SL.EMP.TOTL.SP.NE.ZS", "SL.EMP.VULN.FE.ZS", "SL.EMP.VULN.ZS", "SL.EMP.WORK.FE.ZS", "SL.EMP.VULN.MA.ZS", "SL.EMP.WORK.ZS", "SL.EMP.WORK.MA.ZS", "SL.FAM.WORK.FE.ZS", "SL.FAM.WORK.MA.ZS", "SL.FAM.WORK.ZS", "SL.GDP.PCAP.EM.KD", "SL.IND.EMPL.MA.ZS", "SL.IND.EMPL.ZS", "SL.IND.EMPL.FE.ZS", "SL.SRV.EMPL.FE.ZS", "SL.SRV.EMPL.ZS", "SL.SRV.EMPL.MA.ZS", "SL.TLF.ACTI.1524.FE.ZS", "SL.TLF.ACTI.1524.MA.NE.ZS", "SL.TLF.ACTI.1524.FE.NE.ZS", "SL.TLF.ACTI.1524.MA.ZS", "SL.TLF.ACTI.1524.NE.ZS", "SL.TLF.ACTI.1524.ZS", "SL.TLF.ACTI.FE.ZS", "SL.TLF.ACTI.ZS", "SL.TLF.ACTI.MA.ZS", "SL.TLF.ADVN.FE.ZS", "SL.TLF.ADVN.MA.ZS", "SL.TLF.BASC.FE.ZS", "SL.TLF.BASC.MA.ZS", "SL.TLF.ADVN.ZS", "SL.TLF.BASC.ZS", "SL.TLF.CACT.FE.NE.ZS", "SL.TLF.CACT.FE.ZS", "SL.TLF.CACT.MA.NE.ZS", "SL.TLF.CACT.FM.ZS", "SL.TLF.CACT.MA.ZS", "SL.TLF.CACT.NE.ZS", "SL.TLF.INTM.FE.ZS", "SL.TLF.CACT.ZS", "SL.TLF.INTM.MA.ZS", "SL.TLF.INTM.ZS", "SL.TLF.PART.MA.ZS", "SL.TLF.PART.FE.ZS", "SL.TLF.CACT.FM.NE.ZS", "SL.TLF.PART.ZS", "SL.UEM.1524.FE.NE.ZS", "SL.TLF.TOTL.FE.ZS", "SL.TLF.TOTL.IN", "SL.UEM.1524.FE.ZS", "SL.UEM.1524.MA.ZS", "SL.UEM.1524.MA.NE.ZS", "SL.UEM.1524.ZS", "SL.UEM.ADVN.MA.ZS", "SL.UEM.ADVN.FE.ZS", "SL.UEM.ADVN.ZS", "SL.UEM.1524.NE.ZS", "SL.UEM.INTM.FE.ZS", "SL.UEM.BASC.FE.ZS", "SL.UEM.BASC.ZS", "SL.UEM.BASC.MA.ZS", "SL.UEM.INTM.ZS", "SL.UEM.INTM.MA.ZS", "SL.UEM.NEET.FE.ME.ZS", "SL.UEM.NEET.FE.ZS", "SL.UEM.NEET.ZS", "SL.UEM.NEET.ME.ZS", "SL.UEM.NEET.MA.ZS", "SL.UEM.NEET.MA.ME.ZS", "SL.UEM.TOTL.FE.ZS", "SL.UEM.TOTL.MA.NE.ZS", "SL.UEM.TOTL.ZS", "SL.UEM.TOTL.MA.ZS", "SL.UEM.TOTL.NE.ZS", "SL.UEM.TOTL.FE.NE.ZS"])
    data = J.get(G_request, "http")(J.template("https://api.worldbank.org/v2/topic/10/indicator?per_page=3000&format=json"))
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
    G_describe_indicator(J.template("World Bank Indicators - Social Protection & Labor"), "lower", J.obj(("citation", indicatorNote), ("shortName", J.template("WBI Labor"))))
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
    name='world_bank_indicators_social_protection_labor_TS',
    title='World Bank Indicators - Social Protection & Labor',
    developer='TrendSpider',
    url='https://trendspider.com/trading-tools-store/indicators/6a6295-world-bank-indicators-social-protection-labor/',
    position='lower',
    inputs=[{'id': 'indicator', 'title': 'Indicator', 'type': 'select_wide', 'default': 'Indicator SL.AGR.EMPL.MA.ZS', 'options': ['Indicator SL.AGR.EMPL.MA.ZS', 'Indicator SL.AGR.EMPL.FE.ZS', 'Indicator SL.AGR.EMPL.ZS', 'Indicator SL.EMP.VULN.ZS', 'Indicator SL.EMP.1524.SP.FE.NE.ZS', 'Indicator SL.EMP.1524.SP.MA.NE.ZS', 'Indicator SL.EMP.1524.SP.MA.ZS', 'Indicator SL.EMP.1524.SP.FE.ZS', 'Indicator SL.EMP.1524.SP.ZS', 'Indicator SL.EMP.MPYR.FE.ZS', 'Indicator SL.EMP.MPYR.MA.ZS', 'Indicator SL.EMP.MPYR.ZS', 'Indicator SL.EMP.SELF.MA.ZS', 'Indicator SL.EMP.SELF.ZS', 'Indicator SL.EMP.SELF.FE.ZS', 'Indicator SL.EMP.TOTL.SP.FE.NE.ZS', 'Indicator SL.EMP.TOTL.SP.MA.NE.ZS', 'Indicator SL.EMP.SMGT.FE.ZS', 'Indicator SL.EMP.1524.SP.NE.ZS', 'Indicator SL.EMP.TOTL.SP.MA.ZS', 'Indicator SL.EMP.TOTL.SP.ZS', 'Indicator SL.EMP.TOTL.SP.FE.ZS', 'Indicator SL.EMP.TOTL.SP.NE.ZS', 'Indicator SL.EMP.VULN.FE.ZS', 'Indicator SL.EMP.WORK.FE.ZS', 'Indicator SL.EMP.VULN.MA.ZS', 'Indicator SL.EMP.WORK.ZS', 'Indicator SL.EMP.WORK.MA.ZS', 'Indicator SL.FAM.WORK.FE.ZS', 'Indicator SL.FAM.WORK.MA.ZS', 'Indicator SL.FAM.WORK.ZS', 'Indicator SL.GDP.PCAP.EM.KD', 'Indicator SL.IND.EMPL.MA.ZS', 'Indicator SL.IND.EMPL.ZS', 'Indicator SL.IND.EMPL.FE.ZS', 'Indicator SL.SRV.EMPL.FE.ZS', 'Indicator SL.SRV.EMPL.ZS', 'Indicator SL.SRV.EMPL.MA.ZS', 'Indicator SL.TLF.ACTI.1524.FE.ZS', 'Indicator SL.TLF.ACTI.1524.MA.NE.ZS', 'Indicator SL.TLF.ACTI.1524.FE.NE.ZS', 'Indicator SL.TLF.ACTI.1524.MA.ZS', 'Indicator SL.TLF.ACTI.1524.NE.ZS', 'Indicator SL.TLF.ACTI.1524.ZS', 'Indicator SL.TLF.ACTI.FE.ZS', 'Indicator SL.TLF.ACTI.ZS', 'Indicator SL.TLF.ACTI.MA.ZS', 'Indicator SL.TLF.ADVN.FE.ZS', 'Indicator SL.TLF.ADVN.MA.ZS', 'Indicator SL.TLF.BASC.FE.ZS', 'Indicator SL.TLF.BASC.MA.ZS', 'Indicator SL.TLF.ADVN.ZS', 'Indicator SL.TLF.BASC.ZS', 'Indicator SL.TLF.CACT.FE.NE.ZS', 'Indicator SL.TLF.CACT.FE.ZS', 'Indicator SL.TLF.CACT.MA.NE.ZS', 'Indicator SL.TLF.CACT.FM.ZS', 'Indicator SL.TLF.CACT.MA.ZS', 'Indicator SL.TLF.CACT.NE.ZS', 'Indicator SL.TLF.INTM.FE.ZS', 'Indicator SL.TLF.CACT.ZS', 'Indicator SL.TLF.INTM.MA.ZS', 'Indicator SL.TLF.INTM.ZS', 'Indicator SL.TLF.PART.MA.ZS', 'Indicator SL.TLF.PART.FE.ZS', 'Indicator SL.TLF.CACT.FM.NE.ZS', 'Indicator SL.TLF.PART.ZS', 'Indicator SL.UEM.1524.FE.NE.ZS', 'Indicator SL.TLF.TOTL.FE.ZS', 'Indicator SL.TLF.TOTL.IN', 'Indicator SL.UEM.1524.FE.ZS', 'Indicator SL.UEM.1524.MA.ZS', 'Indicator SL.UEM.1524.MA.NE.ZS', 'Indicator SL.UEM.1524.ZS', 'Indicator SL.UEM.ADVN.MA.ZS', 'Indicator SL.UEM.ADVN.FE.ZS', 'Indicator SL.UEM.ADVN.ZS', 'Indicator SL.UEM.1524.NE.ZS', 'Indicator SL.UEM.INTM.FE.ZS', 'Indicator SL.UEM.BASC.FE.ZS', 'Indicator SL.UEM.BASC.ZS', 'Indicator SL.UEM.BASC.MA.ZS', 'Indicator SL.UEM.INTM.ZS', 'Indicator SL.UEM.INTM.MA.ZS', 'Indicator SL.UEM.NEET.FE.ME.ZS', 'Indicator SL.UEM.NEET.FE.ZS', 'Indicator SL.UEM.NEET.ZS', 'Indicator SL.UEM.NEET.ME.ZS', 'Indicator SL.UEM.NEET.MA.ZS', 'Indicator SL.UEM.NEET.MA.ME.ZS', 'Indicator SL.UEM.TOTL.FE.ZS', 'Indicator SL.UEM.TOTL.MA.NE.ZS', 'Indicator SL.UEM.TOTL.ZS', 'Indicator SL.UEM.TOTL.MA.ZS', 'Indicator SL.UEM.TOTL.NE.ZS', 'Indicator SL.UEM.TOTL.FE.NE.ZS']}, {'id': 'country', 'title': 'Country', 'type': 'select_wide', 'default': 'United States', 'options': ['Australia', 'Canada', 'China', 'European Union', 'Japan', 'Mexico', 'United Kingdom', 'United States', 'World']}],
    outputs=['line'],
    signals=[],
    requires=['http'],
    parity='exact',
)
