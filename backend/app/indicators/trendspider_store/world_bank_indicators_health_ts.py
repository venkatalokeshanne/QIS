"""
World Bank Indicators - Health -- TrendSpider store indicator by TrendSpider.

Registered as "world_bank_indicators_health_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6a6296-world-bank-indicators-health/)
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
    validIndicatorIds = J.JSArray(["SH.ALC.PCAP.FE.LI", "SH.ALC.PCAP.LI", "SH.ALC.PCAP.MA.LI", "SH.ANM.CHLD.ZS", "SH.ANM.ALLW.ZS", "SH.DTH.INJR.ZS", "SH.ANM.NPRG.ZS", "SH.DTH.COMM.ZS", "SH.DTH.IMRT.MA", "SH.DTH.IMRT.FE", "SH.DTH.IMRT", "SH.DTH.MORT", "SH.DTH.MORT.FE", "SH.DTH.MORT.MA", "SH.DTH.NCOM.ZS", "SH.DTH.NMRT", "SH.DTH.STLB", "SH.DYN.AIDS.FE.ZS", "SH.DYN.MORT", "SH.DYN.MORT.FE", "SH.DYN.MORT.MA", "SH.DYN.NCOM.FE.ZS", "SH.DYN.NCOM.MA.ZS", "SH.DYN.NCOM.ZS", "SH.DYN.NMRT", "SH.DYN.STLB", "SH.H2O.BASW.RU.ZS", "SH.H2O.BASW.UR.ZS", "SH.H2O.BASW.ZS", "SH.H2O.SMDW.UR.ZS", "SH.H2O.SMDW.ZS", "SH.IMM.HEPB", "SH.IMM.IDPT", "SH.IMM.MEAS", "SH.IMM.MEA2", "SH.MED.BEDS.ZS", "SH.MED.NUMW.P3", "SH.MED.PHYS.ZS", "SH.MED.SAOP.P5", "SH.MMR.RISK", "SH.MMR.RISK.ZS", "SH.MMR.DTHS", "SH.PRG.ANEM", "SH.PRV.SMOK", "SH.PRV.SMOK.FE", "SH.PRV.SMOK.MA", "SH.SGR.PROC.P5", "SH.SGR.CRSK.ZS", "SH.SGR.IRSK.ZS", "SH.STA.AIRP.FE.P5", "SH.STA.AIRP.MA.P5", "SH.STA.AIRP.P5", "SH.STA.BASS.UR.ZS", "SH.STA.BASS.RU.ZS", "SH.STA.BASS.ZS", "SH.STA.BFED.ZS", "SH.STA.BRTC.ZS", "SH.STA.BRTW.ZS", "SH.STA.DIAB.ZS", "SH.STA.MALN.FE.ZS", "SH.STA.MALN.MA.ZS", "SH.STA.MMRT", "SH.STA.MMRT.NE", "SH.STA.ODFC.RU.ZS", "SH.STA.MALN.ZS", "SH.STA.ODFC.UR.ZS", "SH.STA.ODFC.ZS", "SH.STA.OWGH.FE.ZS", "SH.STA.OWGH.MA.ZS", "SH.STA.OWGH.ME.ZS", "SH.STA.POIS.P5", "SH.STA.OWGH.ZS", "SH.STA.POIS.P5.MA", "SH.STA.POIS.P5.FE", "SH.STA.SMSS.ZS", "SH.STA.SMSS.UR.ZS", "SH.STA.STNT.FE.ZS", "SH.STA.STNT.MA.ZS", "SH.STA.STNT.ME.ZS", "SH.STA.STNT.ZS", "SH.STA.SUIC.MA.P5", "SH.STA.SUIC.FE.P5", "SH.STA.SUIC.P5", "SH.STA.TRAF.P5", "SH.STA.WASH.P5", "SH.STA.WAST.FE.ZS", "SH.STA.WAST.MA.ZS", "SH.STA.WAST.ZS", "SH.SVR.WAST.FE.ZS", "SH.TBS.CURE.ZS", "SH.SVR.WAST.MA.ZS", "SH.SVR.WAST.ZS", "SH.TBS.DTEC.ZS", "SH.TBS.INCD", "SH.UHC.NOP1.CG", "SH.UHC.NOP1.ZG", "SH.UHC.NOP1.TO", "SH.UHC.NOP2.TO", "SH.UHC.NOP2.ZG", "SH.UHC.NOP2.CG", "SH.UHC.OOPC.10.TO", "SH.UHC.OOPC.25.TO", "SH.XPD.CHEX.PC.CD", "SH.XPD.CHEX.GD.ZS", "SH.XPD.CHEX.PP.CD", "SH.XPD.EHEX.PC.CD", "SH.XPD.EHEX.PP.CD", "SH.XPD.GHED.GD.ZS", "SH.XPD.GHED.CH.ZS", "SH.XPD.GHED.PC.CD", "SH.XPD.GHED.GE.ZS", "SH.XPD.EHEX.CH.ZS", "SH.XPD.OOPC.CH.ZS", "SH.XPD.OOPC.PC.CD", "SH.XPD.GHED.PP.CD", "SH.XPD.OOPC.PP.CD", "SH.XPD.PVTD.CH.ZS", "SH.XPD.PVTD.PC.CD", "SH.XPD.PVTD.PP.CD", "SM.POP.NETM", "SM.POP.TOTL.ZS", "SM.POP.TOTL", "SN.ITK.DEFC.ZS", "SN.ITK.MSFI.ZS", "SN.ITK.SVFI.ZS", "SP.DYN.AMRT.FE", "SP.ADO.TFRT", "SP.DYN.AMRT.MA", "SP.DYN.CBRT.IN", "SP.DYN.CDRT.IN", "SP.DYN.CONM.ZS", "SP.DYN.IMRT.IN", "SP.DYN.IMRT.FE.IN", "SP.DYN.CONU.ZS", "SP.DYN.IMRT.MA.IN", "SP.DYN.LE00.IN", "SP.DYN.LE00.FE.IN", "SP.DYN.TFRT.IN", "SP.DYN.LE00.MA.IN", "SP.DYN.TO65.FE.ZS", "SP.DYN.TO65.MA.ZS", "SP.POP.0004.FE.5Y", "SP.POP.0014.FE.IN", "SP.POP.0004.MA.5Y", "SP.POP.0014.FE.ZS", "SP.POP.0014.MA.IN", "SP.POP.0014.TO", "SP.POP.0014.TO.ZS", "SP.POP.0509.FE.5Y", "SP.POP.0509.MA.5Y", "SP.POP.1014.MA.5Y", "SP.POP.1519.MA.5Y", "SP.POP.1519.FE.5Y", "SP.POP.1564.FE.ZS", "SP.POP.0014.MA.ZS", "SP.POP.1564.FE.IN", "SP.POP.1564.MA.IN", "SP.POP.1564.MA.ZS", "SP.POP.1564.TO", "SP.POP.2024.FE.5Y", "SP.POP.1564.TO.ZS", "SP.POP.2529.FE.5Y", "SP.POP.2529.MA.5Y", "SP.POP.1014.FE.5Y", "SP.POP.2024.MA.5Y", "SP.POP.3034.FE.5Y", "SP.POP.3034.MA.5Y", "SP.POP.3539.FE.5Y", "SP.POP.4044.MA.5Y", "SP.POP.3539.MA.5Y", "SP.POP.4549.MA.5Y", "SP.POP.4549.FE.5Y", "SP.POP.4044.FE.5Y", "SP.POP.5054.FE.5Y", "SP.POP.5054.MA.5Y", "SP.POP.5559.MA.5Y", "SP.POP.6064.FE.5Y", "SP.POP.5559.FE.5Y", "SP.POP.6064.MA.5Y", "SP.POP.6569.MA.5Y", "SP.POP.6569.FE.5Y", "SP.POP.65UP.FE.IN", "SP.POP.65UP.FE.ZS", "SP.POP.65UP.TO", "SP.POP.7074.FE.5Y", "SP.POP.65UP.MA.IN", "SP.POP.7074.MA.5Y", "SP.POP.65UP.MA.ZS", "SP.POP.7579.FE.5Y", "SP.POP.80UP.FE", "SP.POP.7579.MA.5Y", "SP.POP.80UP.FE.5Y", "SP.POP.80UP.MA.5Y", "SP.POP.BRTH.MF", "SP.POP.DPND", "SP.POP.DPND.OL", "SP.POP.GROW", "SP.POP.DPND.YG", "SP.POP.TOTL", "SP.POP.TOTL.MA.IN", "SP.POP.TOTL.FE.ZS", "SP.POP.TOTL.MA.ZS", "SP.POP.TOTL.FE.IN", "SP.REG.BRTH.FE.ZS", "SP.POP.65UP.TO.ZS", "SP.REG.BRTH.MA.ZS", "SP.REG.BRTH.ZS", "SP.REG.DTHS.ZS", "SP.UWT.TFRT"])
    data = J.get(G_request, "http")(J.template("https://api.worldbank.org/v2/topic/8/indicator?per_page=1000&format=json"))
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
    G_describe_indicator(J.template("World Bank Indicators - Health"), "lower", J.obj(("citation", indicatorNote), ("shortName", J.template("WBI Health"))))
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
    name='world_bank_indicators_health_TS',
    title='World Bank Indicators - Health',
    developer='TrendSpider',
    url='https://trendspider.com/trading-tools-store/indicators/6a6296-world-bank-indicators-health/',
    position='lower',
    inputs=[{'id': 'indicator', 'title': 'Indicator', 'type': 'select_wide', 'default': 'Indicator SH.DYN.MORT', 'options': ['Indicator SH.DYN.MORT', 'Indicator SH.STA.MMRT', 'Indicator SH.STA.STNT.ZS', 'Indicator SH.TBS.INCD', 'Indicator SM.POP.NETM', 'Indicator SH.H2O.BASW.UR.ZS', 'Indicator SH.H2O.BASW.RU.ZS', 'Indicator SH.H2O.BASW.ZS', 'Indicator SH.STA.BASS.RU.ZS', 'Indicator SH.STA.BASS.UR.ZS', 'Indicator SH.STA.AIRP.P5', 'Indicator SH.H2O.SMDW.ZS', 'Indicator SH.STA.BASS.ZS', 'Indicator SH.STA.ODFC.RU.ZS', 'Indicator SH.STA.POIS.P5', 'Indicator SH.H2O.SMDW.UR.ZS', 'Indicator SH.STA.ODFC.ZS', 'Indicator SH.STA.ODFC.UR.ZS', 'Indicator SH.STA.POIS.P5.FE', 'Indicator SH.STA.SMSS.ZS', 'Indicator SH.STA.POIS.P5.MA', 'Indicator SH.STA.WASH.P5', 'Indicator SH.STA.SMSS.UR.ZS', 'Indicator SM.POP.TOTL', 'Indicator SM.POP.TOTL.ZS', 'Indicator SH.ALC.PCAP.FE.LI', 'Indicator SH.ALC.PCAP.LI', 'Indicator SH.ALC.PCAP.MA.LI', 'Indicator SH.ANM.CHLD.ZS', 'Indicator SH.ANM.ALLW.ZS', 'Indicator SH.DTH.INJR.ZS', 'Indicator SH.ANM.NPRG.ZS', 'Indicator SH.DTH.COMM.ZS', 'Indicator SH.DTH.IMRT.MA', 'Indicator SH.DTH.IMRT.FE', 'Indicator SH.DTH.IMRT', 'Indicator SH.DTH.MORT', 'Indicator SH.DTH.MORT.FE', 'Indicator SH.DTH.MORT.MA', 'Indicator SH.DTH.NCOM.ZS', 'Indicator SH.DTH.NMRT', 'Indicator SH.DTH.STLB', 'Indicator SH.DYN.AIDS.FE.ZS', 'Indicator SH.DYN.MORT.FE', 'Indicator SH.DYN.MORT.MA', 'Indicator SH.DYN.NCOM.FE.ZS', 'Indicator SH.DYN.NCOM.MA.ZS', 'Indicator SH.DYN.NCOM.ZS', 'Indicator SH.DYN.NMRT', 'Indicator SH.DYN.STLB', 'Indicator SH.IMM.HEPB', 'Indicator SH.IMM.IDPT', 'Indicator SH.IMM.MEAS', 'Indicator SH.IMM.MEA2', 'Indicator SH.MED.BEDS.ZS', 'Indicator SH.MED.NUMW.P3', 'Indicator SH.MED.PHYS.ZS', 'Indicator SH.MED.SAOP.P5', 'Indicator SH.MMR.RISK', 'Indicator SH.MMR.RISK.ZS', 'Indicator SH.MMR.DTHS', 'Indicator SH.PRG.ANEM', 'Indicator SH.PRV.SMOK', 'Indicator SH.PRV.SMOK.FE', 'Indicator SH.PRV.SMOK.MA', 'Indicator SH.SGR.PROC.P5', 'Indicator SH.SGR.CRSK.ZS', 'Indicator SH.SGR.IRSK.ZS', 'Indicator SH.STA.AIRP.FE.P5', 'Indicator SH.STA.AIRP.MA.P5', 'Indicator SH.STA.BFED.ZS', 'Indicator SH.STA.BRTC.ZS', 'Indicator SH.STA.BRTW.ZS', 'Indicator SH.STA.DIAB.ZS', 'Indicator SH.STA.MALN.FE.ZS', 'Indicator SH.STA.MALN.MA.ZS', 'Indicator SH.STA.MMRT.NE', 'Indicator SH.STA.MALN.ZS', 'Indicator SH.STA.OWGH.FE.ZS', 'Indicator SH.STA.OWGH.MA.ZS', 'Indicator SH.STA.OWGH.ME.ZS', 'Indicator SH.STA.OWGH.ZS', 'Indicator SH.STA.STNT.FE.ZS', 'Indicator SH.STA.STNT.MA.ZS', 'Indicator SH.STA.STNT.ME.ZS', 'Indicator SH.STA.SUIC.MA.P5', 'Indicator SH.STA.SUIC.FE.P5', 'Indicator SH.STA.SUIC.P5', 'Indicator SH.STA.TRAF.P5', 'Indicator SH.STA.WAST.FE.ZS', 'Indicator SH.STA.WAST.MA.ZS', 'Indicator SH.STA.WAST.ZS', 'Indicator SH.SVR.WAST.FE.ZS', 'Indicator SH.TBS.CURE.ZS', 'Indicator SH.SVR.WAST.MA.ZS', 'Indicator SH.SVR.WAST.ZS', 'Indicator SH.TBS.DTEC.ZS', 'Indicator SH.UHC.NOP1.CG', 'Indicator SH.UHC.NOP1.ZG', 'Indicator SH.UHC.NOP1.TO', 'Indicator SH.UHC.NOP2.TO', 'Indicator SH.UHC.NOP2.ZG', 'Indicator SH.UHC.NOP2.CG', 'Indicator SH.UHC.OOPC.10.TO', 'Indicator SH.UHC.OOPC.25.TO', 'Indicator SH.XPD.CHEX.PC.CD', 'Indicator SH.XPD.CHEX.GD.ZS', 'Indicator SH.XPD.CHEX.PP.CD', 'Indicator SH.XPD.EHEX.PC.CD', 'Indicator SH.XPD.EHEX.PP.CD', 'Indicator SH.XPD.GHED.GD.ZS', 'Indicator SH.XPD.GHED.CH.ZS', 'Indicator SH.XPD.GHED.PC.CD', 'Indicator SH.XPD.GHED.GE.ZS', 'Indicator SH.XPD.EHEX.CH.ZS', 'Indicator SH.XPD.OOPC.CH.ZS', 'Indicator SH.XPD.OOPC.PC.CD', 'Indicator SH.XPD.GHED.PP.CD', 'Indicator SH.XPD.OOPC.PP.CD', 'Indicator SH.XPD.PVTD.CH.ZS', 'Indicator SH.XPD.PVTD.PC.CD', 'Indicator SH.XPD.PVTD.PP.CD', 'Indicator SN.ITK.DEFC.ZS', 'Indicator SN.ITK.MSFI.ZS', 'Indicator SN.ITK.SVFI.ZS', 'Indicator SP.DYN.AMRT.FE', 'Indicator SP.ADO.TFRT', 'Indicator SP.DYN.AMRT.MA', 'Indicator SP.DYN.CBRT.IN', 'Indicator SP.DYN.CDRT.IN', 'Indicator SP.DYN.CONM.ZS', 'Indicator SP.DYN.IMRT.IN', 'Indicator SP.DYN.IMRT.FE.IN', 'Indicator SP.DYN.CONU.ZS', 'Indicator SP.DYN.IMRT.MA.IN', 'Indicator SP.DYN.LE00.IN', 'Indicator SP.DYN.LE00.FE.IN', 'Indicator SP.DYN.TFRT.IN', 'Indicator SP.DYN.LE00.MA.IN', 'Indicator SP.DYN.TO65.FE.ZS', 'Indicator SP.DYN.TO65.MA.ZS', 'Indicator SP.POP.0004.FE.5Y', 'Indicator SP.POP.0014.FE.IN', 'Indicator SP.POP.0004.MA.5Y', 'Indicator SP.POP.0014.FE.ZS', 'Indicator SP.POP.0014.MA.IN', 'Indicator SP.POP.0014.TO', 'Indicator SP.POP.0014.TO.ZS', 'Indicator SP.POP.0509.FE.5Y', 'Indicator SP.POP.0509.MA.5Y', 'Indicator SP.POP.1014.MA.5Y', 'Indicator SP.POP.1519.MA.5Y', 'Indicator SP.POP.1519.FE.5Y', 'Indicator SP.POP.1564.FE.ZS', 'Indicator SP.POP.0014.MA.ZS', 'Indicator SP.POP.1564.FE.IN', 'Indicator SP.POP.1564.MA.IN', 'Indicator SP.POP.1564.MA.ZS', 'Indicator SP.POP.1564.TO', 'Indicator SP.POP.2024.FE.5Y', 'Indicator SP.POP.1564.TO.ZS', 'Indicator SP.POP.2529.FE.5Y', 'Indicator SP.POP.2529.MA.5Y', 'Indicator SP.POP.1014.FE.5Y', 'Indicator SP.POP.2024.MA.5Y', 'Indicator SP.POP.3034.FE.5Y', 'Indicator SP.POP.3034.MA.5Y', 'Indicator SP.POP.3539.FE.5Y', 'Indicator SP.POP.4044.MA.5Y', 'Indicator SP.POP.3539.MA.5Y', 'Indicator SP.POP.4549.MA.5Y', 'Indicator SP.POP.4549.FE.5Y', 'Indicator SP.POP.4044.FE.5Y', 'Indicator SP.POP.5054.FE.5Y', 'Indicator SP.POP.5054.MA.5Y', 'Indicator SP.POP.5559.MA.5Y', 'Indicator SP.POP.6064.FE.5Y', 'Indicator SP.POP.5559.FE.5Y', 'Indicator SP.POP.6064.MA.5Y', 'Indicator SP.POP.6569.MA.5Y', 'Indicator SP.POP.6569.FE.5Y', 'Indicator SP.POP.65UP.FE.IN', 'Indicator SP.POP.65UP.FE.ZS', 'Indicator SP.POP.65UP.TO', 'Indicator SP.POP.7074.FE.5Y', 'Indicator SP.POP.65UP.MA.IN', 'Indicator SP.POP.7074.MA.5Y', 'Indicator SP.POP.65UP.MA.ZS', 'Indicator SP.POP.7579.FE.5Y', 'Indicator SP.POP.80UP.FE', 'Indicator SP.POP.7579.MA.5Y', 'Indicator SP.POP.80UP.FE.5Y', 'Indicator SP.POP.80UP.MA.5Y', 'Indicator SP.POP.BRTH.MF', 'Indicator SP.POP.DPND', 'Indicator SP.POP.DPND.OL', 'Indicator SP.POP.GROW', 'Indicator SP.POP.DPND.YG', 'Indicator SP.POP.TOTL', 'Indicator SP.POP.TOTL.MA.IN', 'Indicator SP.POP.TOTL.FE.ZS', 'Indicator SP.POP.TOTL.MA.ZS', 'Indicator SP.POP.TOTL.FE.IN', 'Indicator SP.REG.BRTH.FE.ZS', 'Indicator SP.POP.65UP.TO.ZS', 'Indicator SP.REG.BRTH.MA.ZS', 'Indicator SP.REG.BRTH.ZS', 'Indicator SP.REG.DTHS.ZS', 'Indicator SP.UWT.TFRT']}, {'id': 'country', 'title': 'Country', 'type': 'select_wide', 'default': 'United States', 'options': ['Australia', 'Canada', 'China', 'European Union', 'Japan', 'Mexico', 'United Kingdom', 'United States', 'World']}],
    outputs=['line'],
    signals=[],
    requires=['http'],
    parity='exact',
)
