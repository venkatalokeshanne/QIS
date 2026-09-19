"""
World Bank Indicators - Private Sector -- TrendSpider store indicator by TrendSpider.

Registered as "world_bank_indicators_private_sector_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6a6294-world-bank-indicators-private-sector/)
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
    validIndicatorIds = J.JSArray(["BM.GSR.INSF.ZS", "BX.GSR.INSF.ZS", "BG.GSR.NFSV.GD.ZS", "FS.AST.PRVT.GD.ZS", "IC.CUS.DURS.EX", "IC.ELC.DURS", "IC.ELC.OUTG.ZS", "IC.FRM.BNKS.ZS", "IC.FRM.BRIB.ZS", "IC.FRM.BKWC.ZS", "IC.FRM.CMPU.ZS", "IC.FRM.CORR.ZS", "IC.FRM.DURS", "IC.FRM.FEMM.ZS", "IC.FRM.FEMO.ZS", "IC.FRM.FREG.ZS", "IC.FRM.OUTG.ZS", "IC.FRM.METG.ZS", "IC.GOV.DURS.ZS", "IC.FRM.TRNG.ZS", "IC.TAX.GIFT.ZS", "IC.TAX.METG", "LP.IMP.DURS.MD", "LP.EXP.DURS.MD", "LP.LPI.CUST.XQ", "LP.LPI.INFR.XQ", "LP.LPI.LOGS.XQ", "LP.LPI.ITRN.XQ", "LP.LPI.TIME.XQ", "ST.INT.ARVL", "LP.LPI.TRAC.XQ", "LP.LPI.OVRL.XQ", "ST.INT.DPRT", "ST.INT.TRNX.CD", "ST.INT.RCPT.CD", "ST.INT.RCPT.XP.ZS", "ST.INT.TVLX.CD", "ST.INT.XPND.MP.ZS", "ST.INT.XPND.CD", "ST.INT.TRNR.CD", "ST.INT.TVLR.CD", "TG.VAL.TOTL.GD.ZS", "TM.TAX.MANF.BC.ZS", "TM.QTY.MRCH.XD.WD", "TM.TAX.MANF.SM.AR.ZS", "TM.TAX.MANF.BR.ZS", "TM.TAX.MANF.WM.AR.ZS", "TM.TAX.MRCH.BC.ZS", "TM.TAX.MRCH.BR.ZS", "TM.TAX.MANF.WM.FN.ZS", "TM.TAX.MRCH.SM.AR.ZS", "TM.TAX.MRCH.SM.FN.ZS", "TM.TAX.MRCH.WM.AR.ZS", "TM.TAX.MRCH.WM.FN.ZS", "TM.TAX.MANF.SM.FN.ZS", "TM.TAX.TCOM.BC.ZS", "TM.TAX.TCOM.BR.ZS", "TM.TAX.TCOM.SM.AR.ZS", "TM.TAX.TCOM.SM.FN.ZS", "TM.TAX.TCOM.WM.AR.ZS", "TM.TAX.TCOM.WM.FN.ZS", "TM.VAL.FUEL.ZS.UN", "TM.UVI.MRCH.XD.WD", "TM.VAL.FOOD.ZS.UN", "TM.VAL.ICTG.ZS.UN", "TM.VAL.AGRI.ZS.UN", "TM.VAL.MANF.ZS.UN", "TM.VAL.INSF.ZS.WT", "TM.VAL.MMTL.ZS.UN", "TM.VAL.MRCH.CD.WT", "TM.VAL.MRCH.AL.ZS", "TM.VAL.MRCH.HI.ZS", "TM.VAL.MRCH.R1.ZS", "TM.VAL.MRCH.OR.ZS", "TM.VAL.MRCH.R3.ZS", "TM.VAL.MRCH.R4.ZS", "TM.VAL.MRCH.R2.ZS", "TM.VAL.MRCH.R6.ZS", "TM.VAL.MRCH.R5.ZS", "TM.VAL.MRCH.WL.CD", "TM.VAL.MRCH.RS.ZS", "TM.VAL.OTHR.ZS.WT", "TM.VAL.SERV.CD.WT", "TM.VAL.TRAN.ZS.WT", "TM.VAL.MRCH.XD.WD", "TT.PRI.MRCH.XD.WD", "TM.VAL.TRVL.ZS.WT", "TX.MNF.TECH.ZS.UN", "TX.VAL.AGRI.ZS.UN", "TX.QTY.MRCH.XD.WD", "TX.UVI.MRCH.XD.WD", "TX.VAL.FUEL.ZS.UN", "TX.VAL.FOOD.ZS.UN", "TX.VAL.ICTG.ZS.UN", "TX.VAL.MANF.ZS.UN", "TX.VAL.MMTL.ZS.UN", "TX.VAL.INSF.ZS.WT", "TX.VAL.MRCH.HI.ZS", "TX.VAL.MRCH.AL.ZS", "TX.VAL.MRCH.CD.WT", "TX.VAL.MRCH.R1.ZS", "TX.VAL.MRCH.OR.ZS", "TX.VAL.MRCH.R2.ZS", "TX.VAL.MRCH.R4.ZS", "TX.VAL.MRCH.R5.ZS", "TX.VAL.MRCH.R6.ZS", "TX.VAL.MRCH.RS.ZS", "TX.VAL.MRCH.WL.CD", "TX.VAL.MRCH.XD.WD", "TX.VAL.MRCH.R3.ZS", "TX.VAL.OTHR.ZS.WT", "TX.VAL.TECH.MF.ZS", "TX.VAL.SERV.CD.WT", "TX.VAL.TECH.CD", "TX.VAL.TRAN.ZS.WT", "TX.VAL.TRVL.ZS.WT"])
    data = J.get(G_request, "http")(J.template("https://api.worldbank.org/v2/topic/12/indicator?per_page=1000&format=json"))
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
    G_describe_indicator(J.template("World Bank Indicators - Private Sector"), "lower", J.obj(("citation", indicatorNote), ("shortName", J.template("WBI Private Sector"))))
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
    name='world_bank_indicators_private_sector_TS',
    title='World Bank Indicators - Private Sector',
    developer='TrendSpider',
    url='https://trendspider.com/trading-tools-store/indicators/6a6294-world-bank-indicators-private-sector/',
    position='lower',
    inputs=[{'id': 'indicator', 'title': 'Indicator', 'type': 'select_wide', 'default': 'Indicator TM.VAL.AGRI.ZS.UN', 'options': ['Indicator TM.VAL.AGRI.ZS.UN', 'Indicator TX.VAL.AGRI.ZS.UN', 'Indicator IC.FRM.BNKS.ZS', 'Indicator IC.ELC.DURS', 'Indicator IC.FRM.OUTG.ZS', 'Indicator TM.VAL.FUEL.ZS.UN', 'Indicator TX.VAL.FUEL.ZS.UN', 'Indicator TM.VAL.MMTL.ZS.UN', 'Indicator TX.VAL.MMTL.ZS.UN', 'Indicator BM.GSR.INSF.ZS', 'Indicator BX.GSR.INSF.ZS', 'Indicator BG.GSR.NFSV.GD.ZS', 'Indicator FS.AST.PRVT.GD.ZS', 'Indicator IC.CUS.DURS.EX', 'Indicator IC.ELC.OUTG.ZS', 'Indicator IC.FRM.BRIB.ZS', 'Indicator IC.FRM.BKWC.ZS', 'Indicator IC.FRM.CMPU.ZS', 'Indicator IC.FRM.CORR.ZS', 'Indicator IC.FRM.DURS', 'Indicator IC.FRM.FEMM.ZS', 'Indicator IC.FRM.FEMO.ZS', 'Indicator IC.FRM.FREG.ZS', 'Indicator IC.FRM.METG.ZS', 'Indicator IC.GOV.DURS.ZS', 'Indicator IC.FRM.TRNG.ZS', 'Indicator IC.TAX.GIFT.ZS', 'Indicator IC.TAX.METG', 'Indicator LP.IMP.DURS.MD', 'Indicator LP.EXP.DURS.MD', 'Indicator LP.LPI.CUST.XQ', 'Indicator LP.LPI.INFR.XQ', 'Indicator LP.LPI.LOGS.XQ', 'Indicator LP.LPI.ITRN.XQ', 'Indicator LP.LPI.TIME.XQ', 'Indicator ST.INT.ARVL', 'Indicator LP.LPI.TRAC.XQ', 'Indicator LP.LPI.OVRL.XQ', 'Indicator ST.INT.DPRT', 'Indicator ST.INT.TRNX.CD', 'Indicator ST.INT.RCPT.CD', 'Indicator ST.INT.RCPT.XP.ZS', 'Indicator ST.INT.TVLX.CD', 'Indicator ST.INT.XPND.MP.ZS', 'Indicator ST.INT.XPND.CD', 'Indicator ST.INT.TRNR.CD', 'Indicator ST.INT.TVLR.CD', 'Indicator TG.VAL.TOTL.GD.ZS', 'Indicator TM.TAX.MANF.BC.ZS', 'Indicator TM.QTY.MRCH.XD.WD', 'Indicator TM.TAX.MANF.SM.AR.ZS', 'Indicator TM.TAX.MANF.BR.ZS', 'Indicator TM.TAX.MANF.WM.AR.ZS', 'Indicator TM.TAX.MRCH.BC.ZS', 'Indicator TM.TAX.MRCH.BR.ZS', 'Indicator TM.TAX.MANF.WM.FN.ZS', 'Indicator TM.TAX.MRCH.SM.AR.ZS', 'Indicator TM.TAX.MRCH.SM.FN.ZS', 'Indicator TM.TAX.MRCH.WM.AR.ZS', 'Indicator TM.TAX.MRCH.WM.FN.ZS', 'Indicator TM.TAX.MANF.SM.FN.ZS', 'Indicator TM.TAX.TCOM.BC.ZS', 'Indicator TM.TAX.TCOM.BR.ZS', 'Indicator TM.TAX.TCOM.SM.AR.ZS', 'Indicator TM.TAX.TCOM.SM.FN.ZS', 'Indicator TM.TAX.TCOM.WM.AR.ZS', 'Indicator TM.TAX.TCOM.WM.FN.ZS', 'Indicator TM.UVI.MRCH.XD.WD', 'Indicator TM.VAL.FOOD.ZS.UN', 'Indicator TM.VAL.ICTG.ZS.UN', 'Indicator TM.VAL.MANF.ZS.UN', 'Indicator TM.VAL.INSF.ZS.WT', 'Indicator TM.VAL.MRCH.CD.WT', 'Indicator TM.VAL.MRCH.AL.ZS', 'Indicator TM.VAL.MRCH.HI.ZS', 'Indicator TM.VAL.MRCH.R1.ZS', 'Indicator TM.VAL.MRCH.OR.ZS', 'Indicator TM.VAL.MRCH.R3.ZS', 'Indicator TM.VAL.MRCH.R4.ZS', 'Indicator TM.VAL.MRCH.R2.ZS', 'Indicator TM.VAL.MRCH.R6.ZS', 'Indicator TM.VAL.MRCH.R5.ZS', 'Indicator TM.VAL.MRCH.WL.CD', 'Indicator TM.VAL.MRCH.RS.ZS', 'Indicator TM.VAL.OTHR.ZS.WT', 'Indicator TM.VAL.SERV.CD.WT', 'Indicator TM.VAL.TRAN.ZS.WT', 'Indicator TM.VAL.MRCH.XD.WD', 'Indicator TT.PRI.MRCH.XD.WD', 'Indicator TM.VAL.TRVL.ZS.WT', 'Indicator TX.MNF.TECH.ZS.UN', 'Indicator TX.QTY.MRCH.XD.WD', 'Indicator TX.UVI.MRCH.XD.WD', 'Indicator TX.VAL.FOOD.ZS.UN', 'Indicator TX.VAL.ICTG.ZS.UN', 'Indicator TX.VAL.MANF.ZS.UN', 'Indicator TX.VAL.INSF.ZS.WT', 'Indicator TX.VAL.MRCH.HI.ZS', 'Indicator TX.VAL.MRCH.AL.ZS', 'Indicator TX.VAL.MRCH.CD.WT', 'Indicator TX.VAL.MRCH.R1.ZS', 'Indicator TX.VAL.MRCH.OR.ZS', 'Indicator TX.VAL.MRCH.R2.ZS', 'Indicator TX.VAL.MRCH.R4.ZS', 'Indicator TX.VAL.MRCH.R5.ZS', 'Indicator TX.VAL.MRCH.R6.ZS', 'Indicator TX.VAL.MRCH.RS.ZS', 'Indicator TX.VAL.MRCH.WL.CD', 'Indicator TX.VAL.MRCH.XD.WD', 'Indicator TX.VAL.MRCH.R3.ZS', 'Indicator TX.VAL.OTHR.ZS.WT', 'Indicator TX.VAL.TECH.MF.ZS', 'Indicator TX.VAL.SERV.CD.WT', 'Indicator TX.VAL.TECH.CD', 'Indicator TX.VAL.TRAN.ZS.WT', 'Indicator TX.VAL.TRVL.ZS.WT']}, {'id': 'country', 'title': 'Country', 'type': 'select_wide', 'default': 'United States', 'options': ['Australia', 'Canada', 'China', 'European Union', 'Japan', 'Mexico', 'United Kingdom', 'United States', 'World']}],
    outputs=['line'],
    signals=[],
    requires=['http'],
    parity='exact',
)
