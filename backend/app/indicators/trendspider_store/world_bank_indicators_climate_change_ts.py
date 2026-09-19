"""
World Bank Indicators - Climate Change -- TrendSpider store indicator by TrendSpider.

Registered as "world_bank_indicators_climate_change_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6a6299-world-bank-indicators-climate-change/)
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
    validIndicatorIds = J.JSArray(["AG.LND.EL5M.UR.K2", "AG.LND.AGRI.ZS", "AG.LND.AGRI.K2", "AG.LND.ARBL.ZS", "AG.LND.EL5M.RU.K2", "AG.LND.EL5M.RU.ZS", "AG.LND.EL5M.UR.ZS", "AG.LND.FRST.ZS", "AG.LND.EL5M.ZS", "AG.LND.FRST.K2", "AG.LND.IRIG.AG.ZS", "AG.LND.PRCP.MM", "BX.KLT.DINV.WD.GD.ZS", "EG.ELC.COAL.ZS", "AG.YLD.CREL.KG", "EG.ELC.ACCS.ZS", "EG.ELC.NGAS.ZS", "EG.ELC.HYRO.ZS", "EG.ELC.NUCL.ZS", "EG.ELC.RNEW.ZS", "EG.ELC.PETR.ZS", "EG.ELC.RNWX.KH", "EG.ELC.RNWX.ZS", "EG.FEC.RNEW.ZS", "EG.USE.COMM.GD.PP.KD", "EG.USE.ELEC.KH.PC", "EG.USE.PCAP.KG.OE", "EN.CLC.DRSK.XQ", "EN.CLC.MDAT.ZS", "EN.POP.EL5M.RU.ZS", "EN.URB.MCTY.TL.ZS", "EN.POP.EL5M.ZS", "ER.H2O.FWTL.K3", "EN.POP.EL5M.UR.ZS", "ER.H2O.FWTL.ZS", "ER.LND.PTLD.ZS", "ER.PTD.TOTL.ZS", "ER.MRN.PTMR.ZS", "SE.ENR.PRSC.FM.ZS", "SH.DYN.MORT", "NV.AGR.TOTL.ZS", "SE.PRM.CMPT.ZS", "SH.STA.MALN.ZS", "SI.POV.DDAY", "SP.POP.GROW", "SP.URB.GROW", "SP.URB.TOTL.IN.ZS", "SP.POP.TOTL", "SP.URB.TOTL"])
    data = J.get(G_request, "http")(J.template("https://api.worldbank.org/v2/topic/19/indicator?per_page=1000&format=json"))
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
    G_describe_indicator(J.template("World Bank Indicators - Climate Change"), "lower", J.obj(("citation", indicatorNote), ("shortName", J.template("WBI Climate"))))
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
    name='world_bank_indicators_climate_change_TS',
    title='World Bank Indicators - Climate Change',
    developer='TrendSpider',
    url='https://trendspider.com/trading-tools-store/indicators/6a6299-world-bank-indicators-climate-change/',
    position='lower',
    inputs=[{'id': 'indicator', 'title': 'Indicator', 'type': 'select_wide', 'default': 'Indicator AG.LND.EL5M.RU.K2', 'options': ['Indicator AG.LND.EL5M.RU.K2', 'Indicator AG.LND.EL5M.RU.ZS', 'Indicator AG.LND.AGRI.ZS', 'Indicator AG.LND.ARBL.ZS', 'Indicator AG.LND.AGRI.K2', 'Indicator AG.LND.FRST.K2', 'Indicator AG.LND.FRST.ZS', 'Indicator AG.LND.PRCP.MM', 'Indicator AG.LND.IRIG.AG.ZS', 'Indicator AG.YLD.CREL.KG', 'Indicator EN.POP.EL5M.RU.ZS', 'Indicator NV.AGR.TOTL.ZS', 'Indicator SH.DYN.MORT', 'Indicator SE.ENR.PRSC.FM.ZS', 'Indicator SE.PRM.CMPT.ZS', 'Indicator SI.POV.DDAY', 'Indicator EG.ELC.ACCS.ZS', 'Indicator EG.ELC.NGAS.ZS', 'Indicator EG.ELC.COAL.ZS', 'Indicator EG.ELC.HYRO.ZS', 'Indicator EG.ELC.NUCL.ZS', 'Indicator EG.ELC.PETR.ZS', 'Indicator EG.ELC.RNEW.ZS', 'Indicator EG.ELC.RNWX.KH', 'Indicator EG.ELC.RNWX.ZS', 'Indicator EG.FEC.RNEW.ZS', 'Indicator EG.USE.COMM.GD.PP.KD', 'Indicator EG.USE.PCAP.KG.OE', 'Indicator EG.USE.ELEC.KH.PC', 'Indicator ER.H2O.FWTL.K3', 'Indicator ER.H2O.FWTL.ZS', 'Indicator AG.LND.EL5M.ZS', 'Indicator AG.LND.EL5M.UR.ZS', 'Indicator AG.LND.EL5M.UR.K2', 'Indicator EN.CLC.DRSK.XQ', 'Indicator EN.CLC.MDAT.ZS', 'Indicator EN.POP.EL5M.UR.ZS', 'Indicator EN.POP.EL5M.ZS', 'Indicator ER.LND.PTLD.ZS', 'Indicator ER.MRN.PTMR.ZS', 'Indicator ER.PTD.TOTL.ZS', 'Indicator BX.KLT.DINV.WD.GD.ZS', 'Indicator SH.STA.MALN.ZS', 'Indicator SP.POP.GROW', 'Indicator SP.POP.TOTL', 'Indicator EN.URB.MCTY.TL.ZS', 'Indicator SP.URB.GROW', 'Indicator SP.URB.TOTL', 'Indicator SP.URB.TOTL.IN.ZS']}, {'id': 'country', 'title': 'Country', 'type': 'select_wide', 'default': 'United States', 'options': ['Australia', 'Canada', 'China', 'European Union', 'Japan', 'Mexico', 'United Kingdom', 'United States', 'World']}],
    outputs=['line'],
    signals=[],
    requires=['http'],
    parity='exact',
)
