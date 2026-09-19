"""
World Bank Indicators - Agriculture & Rural Development -- TrendSpider store indicator by TrendSpider.

Registered as "world_bank_indicators_agriculture_rural_development_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6a6291-world-bank-indicators-agriculture-rural-development/)
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
    validIndicatorIds = J.JSArray(["AG.LND.EL5M.RU.K2", "AG.LND.ARBL.HA.PC", "AG.LND.EL5M.RU.ZS", "AG.CON.FERT.PT.ZS", "AG.LND.AGRI.ZS", "AG.CON.FERT.ZS", "AG.LND.ARBL.ZS", "AG.LND.AGRI.K2", "AG.LND.CREL.HA", "AG.LND.ARBL.HA", "AG.LND.CROP.ZS", "AG.LND.FRST.K2", "AG.LND.FRST.ZS", "AG.LND.PRCP.MM", "AG.LND.IRIG.AG.ZS", "AG.LND.TOTL.RU.K2", "AG.PRD.CREL.MT", "AG.LND.TOTL.K2", "AG.PRD.CROP.XD", "AG.PRD.FOOD.XD", "AG.SRF.TOTL.K2", "AG.PRD.LVSK.XD", "EG.ELC.ACCS.RU.ZS", "AG.YLD.CREL.KG", "EN.POP.EL5M.RU.ZS", "ER.H2O.FWAG.ZS", "NV.AGR.TOTL.CD", "NV.AGR.TOTL.ZS", "SL.AGR.EMPL.MA.ZS", "SL.AGR.EMPL.FE.ZS", "SP.RUR.TOTL", "SL.AGR.EMPL.ZS", "SP.RUR.TOTL.ZG", "TM.VAL.AGRI.ZS.UN", "SP.RUR.TOTL.ZS", "TX.VAL.AGRI.ZS.UN"])
    data = J.get(G_request, "http")(J.template("https://api.worldbank.org/v2/topic/1/indicator?per_page=1000&format=json"))
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
    G_describe_indicator(J.template("World Bank Indicators - Agriculture & Rural Development"), "lower", J.obj(("citation", indicatorNote), ("shortName", J.template("WBI Agriculture"))))
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
    name='world_bank_indicators_agriculture_rural_development_TS',
    title='World Bank Indicators - Agriculture & Rural Development',
    developer='TrendSpider',
    url='https://trendspider.com/trading-tools-store/indicators/6a6291-world-bank-indicators-agriculture-rural-development/',
    position='lower',
    inputs=[{'id': 'indicator', 'title': 'Indicator', 'type': 'select_wide', 'default': 'Indicator AG.LND.EL5M.RU.K2', 'options': ['Indicator AG.LND.EL5M.RU.K2', 'Indicator AG.LND.ARBL.HA.PC', 'Indicator AG.LND.EL5M.RU.ZS', 'Indicator AG.CON.FERT.PT.ZS', 'Indicator AG.LND.AGRI.ZS', 'Indicator AG.CON.FERT.ZS', 'Indicator AG.LND.ARBL.ZS', 'Indicator AG.LND.AGRI.K2', 'Indicator AG.LND.CREL.HA', 'Indicator AG.LND.ARBL.HA', 'Indicator AG.LND.CROP.ZS', 'Indicator AG.LND.FRST.K2', 'Indicator AG.LND.FRST.ZS', 'Indicator AG.LND.PRCP.MM', 'Indicator AG.LND.IRIG.AG.ZS', 'Indicator AG.LND.TOTL.RU.K2', 'Indicator AG.PRD.CREL.MT', 'Indicator AG.LND.TOTL.K2', 'Indicator AG.PRD.CROP.XD', 'Indicator AG.PRD.FOOD.XD', 'Indicator AG.SRF.TOTL.K2', 'Indicator AG.PRD.LVSK.XD', 'Indicator EG.ELC.ACCS.RU.ZS', 'Indicator AG.YLD.CREL.KG', 'Indicator EN.POP.EL5M.RU.ZS', 'Indicator ER.H2O.FWAG.ZS', 'Indicator NV.AGR.TOTL.CD', 'Indicator NV.AGR.TOTL.ZS', 'Indicator SL.AGR.EMPL.MA.ZS', 'Indicator SL.AGR.EMPL.FE.ZS', 'Indicator SP.RUR.TOTL', 'Indicator SL.AGR.EMPL.ZS', 'Indicator SP.RUR.TOTL.ZG', 'Indicator TM.VAL.AGRI.ZS.UN', 'Indicator SP.RUR.TOTL.ZS', 'Indicator TX.VAL.AGRI.ZS.UN']}, {'id': 'country', 'title': 'Country', 'type': 'select_wide', 'default': 'United States', 'options': ['Australia', 'Canada', 'China', 'European Union', 'Japan', 'Mexico', 'United Kingdom', 'United States', 'World']}],
    outputs=['line'],
    signals=[],
    requires=['http'],
    parity='exact',
)
