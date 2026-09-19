"""
World Bank Indicators - Gender -- TrendSpider store indicator by TrendSpider.

Registered as "world_bank_indicators_gender_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6a6298-world-bank-indicators-gender/)
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
    validIndicatorIds = J.JSArray(["IC.FRM.FEMM.ZS", "IC.FRM.FEMO.ZS", "SE.ENR.PRIM.FM.ZS", "SE.ENR.PRSC.FM.ZS", "SE.ENR.SECO.FM.ZS", "SE.PRE.ENRR.FE", "SE.PRE.ENRR.MA", "SE.PRM.CMPT.FE.ZS", "SE.ENR.TERT.FM.ZS", "SE.PRM.CMPT.MA.ZS", "SE.PRM.CUAT.FE.ZS", "SE.PRM.CUAT.ZS", "SE.PRM.CUAT.MA.ZS", "SE.PRM.ENRR.FE", "SE.PRM.ENRL.FE.ZS", "SE.PRM.ENRR.MA", "SE.PRM.GINT.FE.ZS", "SE.PRM.GINT.MA.ZS", "SE.PRM.NENR.FE", "SE.PRM.NINT.MA.ZS", "SE.PRM.NINT.FE.ZS", "SE.PRM.NENR.MA", "SE.PRM.PRS5.MA.ZS", "SE.PRM.PRS5.FE.ZS", "SE.PRM.REPT.FE.ZS", "SE.PRM.REPT.MA.ZS", "SE.PRM.TCAQ.MA.ZS", "SE.PRM.TENR.FE", "SE.PRM.TCAQ.FE.ZS", "SE.PRM.TCHR.FE.ZS", "SE.PRM.TENR.MA", "SE.PRM.UNER.FE", "SE.SCH.LIFE.MA", "SE.PRM.UNER.MA", "SE.SEC.CUAT.LO.FE.ZS", "SE.SCH.LIFE.FE", "SE.SEC.CUAT.LO.MA.ZS", "SE.SEC.CUAT.PO.ZS", "SE.SEC.CUAT.PO.FE.ZS", "SE.SEC.CUAT.PO.MA.ZS", "SE.SEC.CUAT.LO.ZS", "SE.SEC.CUAT.UP.MA.ZS", "SE.SEC.CUAT.UP.FE.ZS", "SE.SEC.ENRL.FE.ZS", "SE.SEC.ENRL.GC.FE.ZS", "SE.SEC.CUAT.UP.ZS", "SE.SEC.ENRR.FE", "SE.SEC.ENRR.MA", "SE.SEC.NENR.FE", "SE.SEC.NENR.MA", "SE.SEC.PROG.FE.ZS", "SE.SEC.TCHR.FE.ZS", "SE.SEC.PROG.MA.ZS", "SE.TER.CUAT.BA.FE.ZS", "SE.TER.CUAT.BA.ZS", "SE.TER.CUAT.DO.FE.ZS", "SE.TER.CUAT.BA.MA.ZS", "SE.TER.CUAT.DO.ZS", "SE.TER.CUAT.DO.MA.ZS", "SE.TER.CUAT.MS.FE.ZS", "SE.TER.CUAT.MS.MA.ZS", "SE.TER.CUAT.MS.ZS", "SE.TER.ENRR.FE", "SE.TER.CUAT.ST.ZS", "SE.TER.CUAT.ST.MA.ZS", "SE.TER.CUAT.ST.FE.ZS", "SE.TER.ENRR.MA", "SG.GEN.MNST.ZS", "SG.GEN.PARL.ZS", "SG.GEN.TECH.ZS", "SG.POP.MIGR.FE.ZS", "SG.TIM.UWRK.FE", "SG.TIM.UWRK.MA", "SH.DYN.AIDS.FE.ZS", "SH.MMR.RISK.ZS", "SH.MMR.RISK", "SH.PRV.SMOK.MA", "SH.STA.BRTC.ZS", "SH.STA.MALN.FE.ZS", "SH.PRV.SMOK.FE", "SH.STA.MALN.MA.ZS", "SH.STA.MMRT", "SH.STA.MMRT.NE", "SH.STA.OB18.MA.ZS", "SH.STA.OB18.FE.ZS", "SL.AGR.EMPL.FE.ZS", "SL.EMP.1524.SP.MA.ZS", "SL.AGR.EMPL.MA.ZS", "SL.EMP.MPYR.FE.ZS", "SL.EMP.1524.SP.FE.ZS", "SL.EMP.MPYR.MA.ZS", "SL.EMP.OWAC.FE.ZS", "SL.EMP.OWAC.MA.ZS", "SL.EMP.SELF.FE.ZS", "SL.EMP.SELF.MA.ZS", "SL.EMP.TOTL.SP.FE.ZS", "SL.EMP.UNDR.FE.ZS", "SL.EMP.UNDR.MA.ZS", "SL.EMP.TOTL.SP.MA.ZS", "SL.EMP.VULN.MA.ZS", "SL.EMP.WORK.FE.ZS", "SL.EMP.VULN.FE.ZS", "SL.EMP.WORK.MA.ZS", "SL.FAM.WORK.FE.ZS", "SL.FAM.WORK.MA.ZS", "SL.IND.EMPL.FE.ZS", "SL.IND.EMPL.MA.ZS", "SL.SRV.EMPL.FE.ZS", "SL.SRV.EMPL.MA.ZS", "SL.TLF.CACT.FE.ZS", "SL.TLF.PART.FE.ZS", "SL.TLF.CACT.MA.ZS", "SL.TLF.PART.MA.ZS", "SL.UEM.1524.FE.ZS", "SL.TLF.TOTL.FE.IN", "SL.UEM.1524.FM.NE.ZS", "SL.TLF.TOTL.FE.ZS", "SL.UEM.1524.FM.ZS", "SL.UEM.1524.MA.ZS", "SL.UEM.TOTL.FE.ZS", "SP.ADO.TFRT", "SL.UEM.TOTL.MA.ZS", "SP.DYN.AMRT.FE", "SP.DYN.CONU.ZS", "SP.DYN.LE00.FE.IN", "SP.DYN.AMRT.MA", "SP.DYN.LE00.MA.IN", "SP.DYN.LE60.FE.IN", "SP.DYN.SMAM.MA", "SP.DYN.SMAM.FE", "SP.DYN.LE60.MA.IN", "SP.DYN.TO65.FE.ZS", "SP.DYN.TFRT.IN", "SP.DYN.TO65.MA.ZS", "SP.POP.AG00.FE.IN", "SP.POP.AG01.FE.IN", "SP.POP.AG00.MA.IN", "SP.POP.AG01.MA.IN", "SP.POP.AG02.FE.IN", "SP.POP.AG02.MA.IN", "SP.POP.AG03.FE.IN", "SP.POP.AG03.MA.IN", "SP.POP.AG04.MA.IN", "SP.POP.AG04.FE.IN", "SP.POP.AG05.MA.IN", "SP.POP.AG05.FE.IN", "SP.RUR.TOTL.FE.ZS", "SP.URB.TOTL.FE.ZS", "SP.RUR.TOTL.MA.ZS", "SP.URB.TOTL.MA.ZS"])
    data = J.get(G_request, "http")(J.template("https://api.worldbank.org/v2/topic/17/indicator?per_page=1000&format=json"))
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
    G_describe_indicator(J.template("World Bank Indicators - Gender"), "lower", J.obj(("citation", indicatorNote), ("shortName", J.template("WBI Gender"))))
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
    name='world_bank_indicators_gender_TS',
    title='World Bank Indicators - Gender',
    developer='TrendSpider',
    url='https://trendspider.com/trading-tools-store/indicators/6a6298-world-bank-indicators-gender/',
    position='lower',
    inputs=[{'id': 'indicator', 'title': 'Indicator', 'type': 'select_wide', 'default': 'Indicator SL.AGR.EMPL.MA.ZS', 'options': ['Indicator SL.AGR.EMPL.MA.ZS', 'Indicator SL.AGR.EMPL.FE.ZS', 'Indicator SE.ENR.PRSC.FM.ZS', 'Indicator SH.STA.MMRT', 'Indicator IC.FRM.FEMM.ZS', 'Indicator IC.FRM.FEMO.ZS', 'Indicator SL.EMP.1524.SP.MA.ZS', 'Indicator SL.EMP.1524.SP.FE.ZS', 'Indicator SL.EMP.MPYR.FE.ZS', 'Indicator SL.EMP.MPYR.MA.ZS', 'Indicator SL.EMP.SELF.MA.ZS', 'Indicator SL.EMP.SELF.FE.ZS', 'Indicator SL.EMP.TOTL.SP.MA.ZS', 'Indicator SL.EMP.TOTL.SP.FE.ZS', 'Indicator SL.EMP.VULN.FE.ZS', 'Indicator SL.EMP.WORK.FE.ZS', 'Indicator SL.EMP.VULN.MA.ZS', 'Indicator SL.EMP.WORK.MA.ZS', 'Indicator SL.FAM.WORK.FE.ZS', 'Indicator SL.FAM.WORK.MA.ZS', 'Indicator SL.IND.EMPL.MA.ZS', 'Indicator SL.IND.EMPL.FE.ZS', 'Indicator SL.SRV.EMPL.FE.ZS', 'Indicator SL.SRV.EMPL.MA.ZS', 'Indicator SL.TLF.CACT.FE.ZS', 'Indicator SL.TLF.CACT.MA.ZS', 'Indicator SL.TLF.PART.MA.ZS', 'Indicator SL.TLF.PART.FE.ZS', 'Indicator SL.TLF.TOTL.FE.ZS', 'Indicator SL.UEM.1524.FE.ZS', 'Indicator SL.UEM.1524.MA.ZS', 'Indicator SL.UEM.TOTL.FE.ZS', 'Indicator SL.UEM.TOTL.MA.ZS', 'Indicator SH.DYN.AIDS.FE.ZS', 'Indicator SH.MMR.RISK', 'Indicator SH.MMR.RISK.ZS', 'Indicator SH.PRV.SMOK.FE', 'Indicator SH.PRV.SMOK.MA', 'Indicator SH.STA.BRTC.ZS', 'Indicator SH.STA.MALN.FE.ZS', 'Indicator SH.STA.MALN.MA.ZS', 'Indicator SH.STA.MMRT.NE', 'Indicator SP.DYN.AMRT.FE', 'Indicator SP.ADO.TFRT', 'Indicator SP.DYN.AMRT.MA', 'Indicator SP.DYN.CONU.ZS', 'Indicator SP.DYN.LE00.FE.IN', 'Indicator SP.DYN.TFRT.IN', 'Indicator SP.DYN.LE00.MA.IN', 'Indicator SP.DYN.TO65.FE.ZS', 'Indicator SP.DYN.TO65.MA.ZS', 'Indicator SE.ENR.PRIM.FM.ZS', 'Indicator SE.ENR.SECO.FM.ZS', 'Indicator SE.PRE.ENRR.FE', 'Indicator SE.PRE.ENRR.MA', 'Indicator SE.PRM.CMPT.FE.ZS', 'Indicator SE.ENR.TERT.FM.ZS', 'Indicator SE.PRM.CMPT.MA.ZS', 'Indicator SE.PRM.CUAT.FE.ZS', 'Indicator SE.PRM.CUAT.ZS', 'Indicator SE.PRM.CUAT.MA.ZS', 'Indicator SE.PRM.ENRR.FE', 'Indicator SE.PRM.ENRL.FE.ZS', 'Indicator SE.PRM.ENRR.MA', 'Indicator SE.PRM.GINT.FE.ZS', 'Indicator SE.PRM.GINT.MA.ZS', 'Indicator SE.PRM.NENR.FE', 'Indicator SE.PRM.NINT.MA.ZS', 'Indicator SE.PRM.NINT.FE.ZS', 'Indicator SE.PRM.NENR.MA', 'Indicator SE.PRM.PRS5.MA.ZS', 'Indicator SE.PRM.PRS5.FE.ZS', 'Indicator SE.PRM.REPT.FE.ZS', 'Indicator SE.PRM.REPT.MA.ZS', 'Indicator SE.PRM.TCAQ.MA.ZS', 'Indicator SE.PRM.TENR.FE', 'Indicator SE.PRM.TCAQ.FE.ZS', 'Indicator SE.PRM.TCHR.FE.ZS', 'Indicator SE.PRM.TENR.MA', 'Indicator SE.PRM.UNER.FE', 'Indicator SE.SCH.LIFE.MA', 'Indicator SE.PRM.UNER.MA', 'Indicator SE.SEC.CUAT.LO.FE.ZS', 'Indicator SE.SCH.LIFE.FE', 'Indicator SE.SEC.CUAT.LO.MA.ZS', 'Indicator SE.SEC.CUAT.PO.ZS', 'Indicator SE.SEC.CUAT.PO.FE.ZS', 'Indicator SE.SEC.CUAT.PO.MA.ZS', 'Indicator SE.SEC.CUAT.LO.ZS', 'Indicator SE.SEC.CUAT.UP.MA.ZS', 'Indicator SE.SEC.CUAT.UP.FE.ZS', 'Indicator SE.SEC.ENRL.FE.ZS', 'Indicator SE.SEC.ENRL.GC.FE.ZS', 'Indicator SE.SEC.CUAT.UP.ZS', 'Indicator SE.SEC.ENRR.FE', 'Indicator SE.SEC.ENRR.MA', 'Indicator SE.SEC.NENR.FE', 'Indicator SE.SEC.NENR.MA', 'Indicator SE.SEC.PROG.FE.ZS', 'Indicator SE.SEC.TCHR.FE.ZS', 'Indicator SE.SEC.PROG.MA.ZS', 'Indicator SE.TER.CUAT.BA.FE.ZS', 'Indicator SE.TER.CUAT.BA.ZS', 'Indicator SE.TER.CUAT.DO.FE.ZS', 'Indicator SE.TER.CUAT.BA.MA.ZS', 'Indicator SE.TER.CUAT.DO.ZS', 'Indicator SE.TER.CUAT.DO.MA.ZS', 'Indicator SE.TER.CUAT.MS.FE.ZS', 'Indicator SE.TER.CUAT.MS.MA.ZS', 'Indicator SE.TER.CUAT.MS.ZS', 'Indicator SE.TER.ENRR.FE', 'Indicator SE.TER.CUAT.ST.ZS', 'Indicator SE.TER.CUAT.ST.MA.ZS', 'Indicator SE.TER.CUAT.ST.FE.ZS', 'Indicator SE.TER.ENRR.MA', 'Indicator SG.GEN.MNST.ZS', 'Indicator SG.GEN.PARL.ZS', 'Indicator SG.GEN.TECH.ZS', 'Indicator SG.POP.MIGR.FE.ZS', 'Indicator SG.TIM.UWRK.FE', 'Indicator SG.TIM.UWRK.MA', 'Indicator SH.STA.OB18.MA.ZS', 'Indicator SH.STA.OB18.FE.ZS', 'Indicator SL.EMP.OWAC.FE.ZS', 'Indicator SL.EMP.OWAC.MA.ZS', 'Indicator SL.EMP.UNDR.FE.ZS', 'Indicator SL.EMP.UNDR.MA.ZS', 'Indicator SL.TLF.TOTL.FE.IN', 'Indicator SL.UEM.1524.FM.NE.ZS', 'Indicator SL.UEM.1524.FM.ZS', 'Indicator SP.DYN.LE60.FE.IN', 'Indicator SP.DYN.SMAM.MA', 'Indicator SP.DYN.SMAM.FE', 'Indicator SP.DYN.LE60.MA.IN', 'Indicator SP.POP.AG00.FE.IN', 'Indicator SP.POP.AG01.FE.IN', 'Indicator SP.POP.AG00.MA.IN', 'Indicator SP.POP.AG01.MA.IN', 'Indicator SP.POP.AG02.FE.IN', 'Indicator SP.POP.AG02.MA.IN', 'Indicator SP.POP.AG03.FE.IN', 'Indicator SP.POP.AG03.MA.IN', 'Indicator SP.POP.AG04.MA.IN', 'Indicator SP.POP.AG04.FE.IN', 'Indicator SP.POP.AG05.MA.IN', 'Indicator SP.POP.AG05.FE.IN', 'Indicator SP.RUR.TOTL.FE.ZS', 'Indicator SP.URB.TOTL.FE.ZS', 'Indicator SP.RUR.TOTL.MA.ZS', 'Indicator SP.URB.TOTL.MA.ZS']}, {'id': 'country', 'title': 'Country', 'type': 'select_wide', 'default': 'United States', 'options': ['Australia', 'Canada', 'China', 'European Union', 'Japan', 'Mexico', 'United Kingdom', 'United States', 'World']}],
    outputs=['line'],
    signals=[],
    requires=['http'],
    parity='exact',
)
