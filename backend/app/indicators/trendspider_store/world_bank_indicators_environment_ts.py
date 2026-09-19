"""
World Bank Indicators - Environment -- TrendSpider store indicator by TrendSpider.

Registered as "world_bank_indicators_environment_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6a6296-world-bank-indicators-environment/)
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
    validIndicatorIds = J.JSArray(["AG.LND.EL5M.RU.ZS", "AG.LND.EL5M.RU.K2", "AG.LND.AGRI.ZS", "AG.LND.FRST.K2", "AG.LND.FRST.ZS", "AG.LND.ARBL.ZS", "AG.LND.PRCP.MM", "AG.LND.EL5M.ZS", "AG.LND.TOTL.K2", "AG.LND.TOTL.RU.K2", "AG.SRF.TOTL.K2", "AG.LND.EL5M.UR.ZS", "AG.LND.TOTL.UR.K2", "AG.LND.EL5M.UR.K2", "EG.CFT.ACCS.RU.ZS", "EG.EGY.PRIM.PP.KD", "EG.CFT.ACCS.UR.ZS", "EG.CFT.ACCS.ZS", "EG.ELC.FOSL.ZS", "EG.ELC.ACCS.ZS", "EG.ELC.RNEW.ZS", "EG.ELC.RNWX.ZS", "EG.ELC.RNWX.KH", "EG.FEC.RNEW.ZS", "EN.ATM.PM25.MC.T2.ZS", "EN.ATM.PM25.MC.M3", "EN.ATM.PM25.MC.T1.ZS", "EN.ATM.PM25.MC.T3.ZS", "EN.ATM.PM25.MC.ZS", "EN.BIR.THRD.NO", "EN.CLC.DRSK.XQ", "EN.CLC.MDAT.ZS", "EN.FSH.THRD.NO", "EN.GHG.ALL.LU.MT.CE.AR5", "EN.GHG.ALL.MT.CE.AR5", "EN.GHG.CH4.AG.MT.CE.AR5", "EN.GHG.CH4.FE.MT.CE.AR5", "EN.GHG.CH4.IC.MT.CE.AR5", "EN.GHG.CH4.MT.CE.AR5", "EN.GHG.CH4.IP.MT.CE.AR5", "EN.GHG.CH4.BU.MT.CE.AR5", "EN.GHG.CH4.PI.MT.CE.AR5", "EN.GHG.CH4.TR.MT.CE.AR5", "EN.GHG.CH4.ZG.AR5", "EN.GHG.ALL.PC.CE.AR5", "EN.GHG.CH4.WA.MT.CE.AR5", "EN.GHG.CO2.AG.MT.CE.AR5", "EN.GHG.CO2.BU.MT.CE.AR5", "EN.GHG.CO2.FE.MT.CE.AR5", "EN.GHG.CO2.LU.DF.MT.CE.AR5", "EN.GHG.CO2.IC.MT.CE.AR5", "EN.GHG.CO2.LU.FL.MT.CE.AR5", "EN.GHG.CO2.IP.MT.CE.AR5", "EN.GHG.CO2.LU.OS.MT.CE.AR5", "EN.GHG.CO2.PC.CE.AR5", "EN.GHG.CO2.PI.MT.CE.AR5", "EN.GHG.CO2.RT.GDP.KD", "EN.GHG.CO2.RT.GDP.PP.KD", "EN.GHG.CO2.TR.MT.CE.AR5", "EN.GHG.CO2.LU.OL.MT.CE.AR5", "EN.GHG.FGAS.IP.MT.CE.AR5", "EN.GHG.N2O.AG.MT.CE.AR5", "EN.GHG.CO2.ZG.AR5", "EN.GHG.N2O.BU.MT.CE.AR5", "EN.GHG.CO2.WA.MT.CE.AR5", "EN.GHG.N2O.IC.MT.CE.AR5", "EN.GHG.N2O.FE.MT.CE.AR5", "EN.GHG.N2O.MT.CE.AR5", "EN.GHG.N2O.IP.MT.CE.AR5", "EN.GHG.N2O.PI.MT.CE.AR5", "EN.GHG.N2O.WA.MT.CE.AR5", "EN.GHG.CO2.MT.CE.AR5", "EN.GHG.N2O.TR.MT.CE.AR5", "EN.GHG.TOT.ZG.AR5", "EN.GHG.N2O.ZG.AR5", "EN.HPT.THRD.NO", "EN.MAM.THRD.NO", "EN.POP.EL5M.UR.ZS", "EN.POP.EL5M.RU.ZS", "EN.POP.EL5M.ZS", "EN.POP.SLUM.UR.ZS", "ER.FSH.CAPT.MT", "ER.FSH.AQUA.MT", "ER.FSH.PROD.MT", "ER.GDP.FWTL.M3.KD", "ER.H2O.FWAG.ZS", "ER.H2O.FWDM.ZS", "ER.H2O.FWTL.ZS", "ER.H2O.FWST.ZS", "ER.H2O.FWIN.ZS", "ER.H2O.FWTL.K3", "ER.H2O.INTR.K3", "ER.LND.PTLD.ZS", "ER.H2O.INTR.PC", "ER.MRN.PTMR.ZS", "NY.ADJ.AEDU.GN.ZS", "ER.PTD.TOTL.ZS", "NY.ADJ.DCO2.GN.ZS", "NY.ADJ.AEDU.CD", "NY.ADJ.DCO2.CD", "NY.ADJ.DFOR.CD", "NY.ADJ.DKAP.CD", "NY.ADJ.DFOR.GN.ZS", "NY.ADJ.DKAP.GN.ZS", "NY.ADJ.DMIN.CD", "NY.ADJ.DMIN.GN.ZS", "NY.ADJ.DNGY.CD", "NY.ADJ.DNGY.GN.ZS", "NY.ADJ.ICTR.GN.ZS", "NY.ADJ.DPEM.GN.ZS", "NY.ADJ.SVNG.CD", "NY.ADJ.NNAT.GN.ZS", "NY.ADJ.SVNG.GN.ZS", "NY.ADJ.SVNX.CD", "NY.ADJ.NNAT.CD", "NY.ADJ.SVNX.GN.ZS", "NY.ADJ.DPEM.CD", "NY.GDP.COAL.RT.ZS", "NY.GDP.MINR.RT.ZS", "NY.GDP.NGAS.RT.ZS", "NY.GDP.FRST.RT.ZS", "NY.GDP.PETR.RT.ZS", "NY.GDP.TOTL.RT.ZS", "SH.H2O.BASW.UR.ZS", "SH.H2O.BASW.RU.ZS", "SH.H2O.BASW.ZS", "SH.STA.BASS.RU.ZS", "SH.STA.BASS.UR.ZS", "SH.STA.AIRP.P5", "SH.H2O.SMDW.ZS", "SH.STA.BASS.ZS", "SH.STA.ODFC.RU.ZS", "SH.STA.POIS.P5", "SH.H2O.SMDW.UR.ZS", "SH.STA.ODFC.ZS", "SH.STA.ODFC.UR.ZS", "SH.STA.POIS.P5.FE", "SH.STA.SMSS.ZS", "SH.STA.POIS.P5.MA", "SH.STA.WASH.P5", "SH.STA.SMSS.UR.ZS", "EN.GHG.CO2.LU.MT.CE.AR5"])
    data = J.get(G_request, "http")(J.template("https://api.worldbank.org/v2/topic/6/indicator?per_page=1000&format=json"))
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
    G_describe_indicator(J.template("World Bank Indicators - Environment"), "lower", J.obj(("citation", indicatorNote), ("shortName", J.template("WBI Environment"))))
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
    name='world_bank_indicators_environment_TS',
    title='World Bank Indicators - Environment',
    developer='TrendSpider',
    url='https://trendspider.com/trading-tools-store/indicators/6a6296-world-bank-indicators-environment/',
    position='lower',
    inputs=[{'id': 'indicator', 'title': 'Indicator', 'type': 'select_wide', 'default': 'Indicator AG.LND.EL5M.RU.K2', 'options': ['Indicator AG.LND.EL5M.RU.K2', 'Indicator AG.LND.EL5M.RU.ZS', 'Indicator AG.LND.AGRI.ZS', 'Indicator AG.LND.ARBL.ZS', 'Indicator AG.LND.FRST.K2', 'Indicator AG.LND.FRST.ZS', 'Indicator AG.LND.PRCP.MM', 'Indicator AG.LND.TOTL.RU.K2', 'Indicator AG.LND.TOTL.K2', 'Indicator AG.SRF.TOTL.K2', 'Indicator EN.POP.EL5M.RU.ZS', 'Indicator ER.H2O.FWAG.ZS', 'Indicator EG.ELC.FOSL.ZS', 'Indicator EG.ELC.ACCS.ZS', 'Indicator EG.ELC.RNEW.ZS', 'Indicator EG.EGY.PRIM.PP.KD', 'Indicator EG.ELC.RNWX.KH', 'Indicator EG.ELC.RNWX.ZS', 'Indicator EG.FEC.RNEW.ZS', 'Indicator NY.ADJ.DMIN.CD', 'Indicator NY.ADJ.DNGY.CD', 'Indicator NY.ADJ.DMIN.GN.ZS', 'Indicator NY.ADJ.DNGY.GN.ZS', 'Indicator NY.GDP.MINR.RT.ZS', 'Indicator NY.GDP.PETR.RT.ZS', 'Indicator NY.GDP.NGAS.RT.ZS', 'Indicator NY.GDP.TOTL.RT.ZS', 'Indicator EN.POP.SLUM.UR.ZS', 'Indicator ER.H2O.FWDM.ZS', 'Indicator ER.H2O.FWIN.ZS', 'Indicator ER.H2O.FWTL.K3', 'Indicator ER.H2O.FWTL.ZS', 'Indicator ER.H2O.INTR.PC', 'Indicator ER.H2O.INTR.K3', 'Indicator AG.LND.EL5M.ZS', 'Indicator AG.LND.EL5M.UR.ZS', 'Indicator AG.LND.TOTL.UR.K2', 'Indicator AG.LND.EL5M.UR.K2', 'Indicator EG.CFT.ACCS.RU.ZS', 'Indicator EG.CFT.ACCS.UR.ZS', 'Indicator EG.CFT.ACCS.ZS', 'Indicator EN.ATM.PM25.MC.T2.ZS', 'Indicator EN.ATM.PM25.MC.M3', 'Indicator EN.ATM.PM25.MC.T1.ZS', 'Indicator EN.ATM.PM25.MC.T3.ZS', 'Indicator EN.ATM.PM25.MC.ZS', 'Indicator EN.BIR.THRD.NO', 'Indicator EN.CLC.DRSK.XQ', 'Indicator EN.CLC.MDAT.ZS', 'Indicator EN.FSH.THRD.NO', 'Indicator EN.GHG.ALL.LU.MT.CE.AR5', 'Indicator EN.GHG.ALL.MT.CE.AR5', 'Indicator EN.GHG.CH4.AG.MT.CE.AR5', 'Indicator EN.GHG.CH4.FE.MT.CE.AR5', 'Indicator EN.GHG.CH4.IC.MT.CE.AR5', 'Indicator EN.GHG.CH4.MT.CE.AR5', 'Indicator EN.GHG.CH4.IP.MT.CE.AR5', 'Indicator EN.GHG.CH4.BU.MT.CE.AR5', 'Indicator EN.GHG.CH4.PI.MT.CE.AR5', 'Indicator EN.GHG.CH4.TR.MT.CE.AR5', 'Indicator EN.GHG.CH4.ZG.AR5', 'Indicator EN.GHG.ALL.PC.CE.AR5', 'Indicator EN.GHG.CH4.WA.MT.CE.AR5', 'Indicator EN.GHG.CO2.AG.MT.CE.AR5', 'Indicator EN.GHG.CO2.BU.MT.CE.AR5', 'Indicator EN.GHG.CO2.FE.MT.CE.AR5', 'Indicator EN.GHG.CO2.LU.DF.MT.CE.AR5', 'Indicator EN.GHG.CO2.IC.MT.CE.AR5', 'Indicator EN.GHG.CO2.LU.FL.MT.CE.AR5', 'Indicator EN.GHG.CO2.IP.MT.CE.AR5', 'Indicator EN.GHG.CO2.LU.OS.MT.CE.AR5', 'Indicator EN.GHG.CO2.PC.CE.AR5', 'Indicator EN.GHG.CO2.PI.MT.CE.AR5', 'Indicator EN.GHG.CO2.RT.GDP.KD', 'Indicator EN.GHG.CO2.RT.GDP.PP.KD', 'Indicator EN.GHG.CO2.TR.MT.CE.AR5', 'Indicator EN.GHG.CO2.LU.OL.MT.CE.AR5', 'Indicator EN.GHG.FGAS.IP.MT.CE.AR5', 'Indicator EN.GHG.N2O.AG.MT.CE.AR5', 'Indicator EN.GHG.CO2.ZG.AR5', 'Indicator EN.GHG.N2O.BU.MT.CE.AR5', 'Indicator EN.GHG.CO2.WA.MT.CE.AR5', 'Indicator EN.GHG.N2O.IC.MT.CE.AR5', 'Indicator EN.GHG.N2O.FE.MT.CE.AR5', 'Indicator EN.GHG.N2O.MT.CE.AR5', 'Indicator EN.GHG.N2O.IP.MT.CE.AR5', 'Indicator EN.GHG.N2O.PI.MT.CE.AR5', 'Indicator EN.GHG.N2O.WA.MT.CE.AR5', 'Indicator EN.GHG.CO2.MT.CE.AR5', 'Indicator EN.GHG.N2O.TR.MT.CE.AR5', 'Indicator EN.GHG.TOT.ZG.AR5', 'Indicator EN.GHG.N2O.ZG.AR5', 'Indicator EN.HPT.THRD.NO', 'Indicator EN.MAM.THRD.NO', 'Indicator EN.POP.EL5M.UR.ZS', 'Indicator EN.POP.EL5M.ZS', 'Indicator ER.FSH.CAPT.MT', 'Indicator ER.FSH.AQUA.MT', 'Indicator ER.FSH.PROD.MT', 'Indicator ER.GDP.FWTL.M3.KD', 'Indicator ER.H2O.FWST.ZS', 'Indicator ER.LND.PTLD.ZS', 'Indicator ER.MRN.PTMR.ZS', 'Indicator NY.ADJ.AEDU.GN.ZS', 'Indicator ER.PTD.TOTL.ZS', 'Indicator NY.ADJ.DCO2.GN.ZS', 'Indicator NY.ADJ.AEDU.CD', 'Indicator NY.ADJ.DCO2.CD', 'Indicator NY.ADJ.DFOR.CD', 'Indicator NY.ADJ.DKAP.CD', 'Indicator NY.ADJ.DFOR.GN.ZS', 'Indicator NY.ADJ.DKAP.GN.ZS', 'Indicator NY.ADJ.ICTR.GN.ZS', 'Indicator NY.ADJ.DPEM.GN.ZS', 'Indicator NY.ADJ.SVNG.CD', 'Indicator NY.ADJ.NNAT.GN.ZS', 'Indicator NY.ADJ.SVNG.GN.ZS', 'Indicator NY.ADJ.SVNX.CD', 'Indicator NY.ADJ.NNAT.CD', 'Indicator NY.ADJ.SVNX.GN.ZS', 'Indicator NY.ADJ.DPEM.CD', 'Indicator NY.GDP.COAL.RT.ZS', 'Indicator NY.GDP.FRST.RT.ZS', 'Indicator SH.H2O.BASW.UR.ZS', 'Indicator SH.H2O.BASW.RU.ZS', 'Indicator SH.H2O.BASW.ZS', 'Indicator SH.STA.BASS.RU.ZS', 'Indicator SH.STA.BASS.UR.ZS', 'Indicator SH.STA.AIRP.P5', 'Indicator SH.H2O.SMDW.ZS', 'Indicator SH.STA.BASS.ZS', 'Indicator SH.STA.ODFC.RU.ZS', 'Indicator SH.STA.POIS.P5', 'Indicator SH.H2O.SMDW.UR.ZS', 'Indicator SH.STA.ODFC.ZS', 'Indicator SH.STA.ODFC.UR.ZS', 'Indicator SH.STA.POIS.P5.FE', 'Indicator SH.STA.SMSS.ZS', 'Indicator SH.STA.POIS.P5.MA', 'Indicator SH.STA.WASH.P5', 'Indicator SH.STA.SMSS.UR.ZS', 'Indicator EN.GHG.CO2.LU.MT.CE.AR5']}, {'id': 'country', 'title': 'Country', 'type': 'select_wide', 'default': 'United States', 'options': ['Australia', 'Canada', 'China', 'European Union', 'Japan', 'Mexico', 'United Kingdom', 'United States', 'World']}],
    outputs=['line'],
    signals=[],
    requires=['http'],
    parity='exact',
)
