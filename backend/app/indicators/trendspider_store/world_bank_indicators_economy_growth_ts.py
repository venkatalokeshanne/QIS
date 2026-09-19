"""
World Bank Indicators - Economy & Growth -- TrendSpider store indicator by TrendSpider.

Registered as "world_bank_indicators_economy_growth_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6a7ccf-world-bank-indicators-economy-growth/)
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
    validIndicatorIds = J.JSArray(["BG.GSR.NFSV.GD.ZS", "BM.GSR.CMCP.ZS", "BM.GSR.GNFS.CD", "BM.GSR.FCTY.CD", "BM.GSR.INSF.ZS", "BM.GSR.MRCH.CD", "BM.GSR.ROYL.CD", "BM.GSR.NFSV.CD", "BM.GSR.TRAN.ZS", "BM.GSR.TOTL.CD", "BM.KLT.DINV.CD.WD", "BM.KLT.DINV.WD.GD.ZS", "BM.GSR.TRVL.ZS", "BM.TRF.PRVT.CD", "BM.TRF.PWKR.CD.DT", "BN.CAB.XOKA.CD", "BN.CAB.XOKA.GD.ZS", "BN.GSR.FCTY.CD", "BN.FIN.TOTL.CD", "BN.GSR.GNFS.CD", "BN.GSR.MRCH.CD", "BN.KAC.EOMS.CD", "BN.KLT.DINV.CD", "BN.KLT.PTXL.CD", "BN.RES.INCL.CD", "BN.TRF.CURR.CD", "BX.GSR.CCIS.CD", "BX.GSR.CCIS.ZS", "BX.GSR.FCTY.CD", "BX.GSR.GNFS.CD", "BX.GSR.CMCP.ZS", "BX.GSR.INSF.ZS", "BX.GSR.MRCH.CD", "BX.GSR.ROYL.CD", "BX.GSR.TOTL.CD", "BX.GSR.NFSV.CD", "BX.GSR.TRAN.ZS", "BX.GSR.TRVL.ZS", "BX.PEF.TOTL.CD.WD", "BX.KLT.DINV.WD.GD.ZS", "BX.KLT.DINV.CD.WD", "BX.TRF.CURR.CD", "BX.TRF.PWKR.DT.GD.ZS", "BX.TRF.PWKR.CD.DT", "FI.RES.XGLD.CD", "FI.RES.TOTL.CD", "GC.XPN.TOTL.GD.ZS", "GC.DOD.TOTL.GD.ZS", "FP.CPI.TOTL.ZG", "NE.CON.GOVT.KD", "NE.CON.GOVT.CD", "NE.CON.GOVT.KD.ZG", "NE.CON.GOVT.CN", "GC.REV.XGRT.GD.ZS", "NE.CON.GOVT.KN", "BN.TRF.KOGT.CD", "NE.CON.GOVT.ZS", "NE.CON.PRVT.CN", "NE.CON.PRVT.CD", "NE.CON.PRVT.KD", "NE.CON.PRVT.KD.ZG", "NE.CON.PRVT.KN", "NE.CON.PRVT.CN.AD", "NE.CON.PRVT.PC.KD.ZG", "NE.CON.PRVT.PC.KD", "NE.CON.PRVT.ZS", "NE.CON.PRVT.PP.KD", "NE.CON.PRVT.PP.CD", "NE.CON.TOTL.CD", "NE.CON.TOTL.CN", "NE.CON.TOTL.KN", "NE.CON.TOTL.KD", "NE.CON.TOTL.ZS", "NE.DAB.DEFL.ZS", "NE.CON.TOTL.KD.ZG", "NE.DAB.TOTL.CN", "NE.DAB.TOTL.KN", "NE.DAB.TOTL.CD", "NE.DAB.TOTL.ZS", "NE.DAB.TOTL.KD", "NE.EXP.GNFS.CD", "NE.EXP.GNFS.KD", "NE.EXP.GNFS.CN", "NE.EXP.GNFS.KD.ZG", "NE.GDI.FTOT.CD", "NE.GDI.FTOT.CN", "NE.GDI.FTOT.KD", "NE.EXP.GNFS.KN", "NE.GDI.FTOT.KD.ZG", "NE.GDI.FTOT.ZS", "NE.GDI.FTOT.KN", "NE.EXP.GNFS.ZS", "NE.GDI.STKB.KN", "NE.GDI.STKB.CD", "NE.GDI.STKB.CN", "NE.GDI.TOTL.CN", "NE.GDI.TOTL.CD", "NE.GDI.TOTL.KN", "NE.GDI.TOTL.KD", "NE.GDI.TOTL.KD.ZG", "NE.IMP.GNFS.CD", "NE.GDI.TOTL.ZS", "NE.IMP.GNFS.KN", "NE.IMP.GNFS.CN", "NE.IMP.GNFS.KD", "NE.RSB.GNFS.CD", "NE.IMP.GNFS.KD.ZG", "NV.AGR.EMPL.KD", "NE.IMP.GNFS.ZS", "NE.RSB.GNFS.KN", "NE.RSB.GNFS.CN", "NV.AGR.TOTL.CD", "NV.AGR.TOTL.KD", "NE.TRD.GNFS.ZS", "NV.AGR.TOTL.CN", "NE.RSB.GNFS.ZS", "NV.IND.MANF.CD", "NV.IND.MANF.ZS", "NV.AGR.TOTL.ZS", "NV.IND.EMPL.KD", "NV.IND.MANF.KD", "NV.IND.MANF.CN", "NV.IND.TOTL.CD", "NV.IND.TOTL.CN", "NV.IND.TOTL.KD", "NV.IND.TOTL.ZS", "NV.MNF.CHEM.ZS.UN", "NV.MNF.MTRN.ZS.UN", "NV.MNF.TECH.ZS.UN", "NV.MNF.FBTO.ZS.UN", "NV.SRV.EMPL.KD", "NV.MNF.OTHR.ZS.UN", "NV.MNF.TXTL.ZS.UN", "NV.SRV.TOTL.CN", "NV.SRV.TOTL.KD", "NV.SRV.TOTL.ZS", "NV.SRV.TOTL.CD", "NY.ADJ.AEDU.CD", "NY.ADJ.DCO2.GN.ZS", "NY.ADJ.DFOR.CD", "NY.ADJ.DCO2.CD", "NY.ADJ.DFOR.GN.ZS", "NY.ADJ.DMIN.CD", "NY.ADJ.DKAP.CD", "NY.ADJ.AEDU.GN.ZS", "NY.ADJ.DKAP.GN.ZS", "NY.ADJ.DRES.GN.ZS", "NY.ADJ.DNGY.GN.ZS", "NY.ADJ.NNAT.CD", "NY.ADJ.DPEM.CD", "NY.ADJ.DNGY.CD", "NY.ADJ.DMIN.GN.ZS", "NY.ADJ.DPEM.GN.ZS", "NY.ADJ.ICTR.GN.ZS", "NY.ADJ.NNTY.KD", "NY.ADJ.NNAT.GN.ZS", "NY.ADJ.NNTY.CD", "NY.ADJ.NNTY.KD.ZG", "NY.ADJ.NNTY.PC.KD", "NY.ADJ.NNTY.PC.KD.ZG", "NY.ADJ.SVNG.GN.ZS", "NY.ADJ.SVNG.CD", "NY.ADJ.NNTY.PC.CD", "NY.ADJ.SVNX.CD", "NY.ADJ.SVNX.GN.ZS", "NY.GDP.DEFL.ZS", "NY.GDP.DEFL.KD.ZG", "NY.EXP.CAPM.KN", "NY.GDP.DISC.CN", "NY.GDP.DISC.KN", "NY.GDP.FCST.CD", "NY.GDP.MKTP.CD", "NY.GDP.FCST.KD", "NY.GDP.FCST.CN", "NY.GDP.MKTP.CN", "NY.GDP.MKTP.CN.AD", "NY.GDP.MKTP.KD", "NY.GDP.MKTP.KD.ZG", "NY.GDP.MKTP.KN", "NY.GDP.MKTP.PP.CD", "NY.GDP.PCAP.CD", "NY.GDP.MKTP.PP.KD", "NY.GDP.PCAP.CN", "NY.GDP.PCAP.KD", "NY.GDP.PCAP.KD.ZG", "NY.GDP.PCAP.PP.KD", "NY.GDS.TOTL.CD", "NY.GDP.PCAP.PP.CD", "NY.GDP.PCAP.KN", "NY.GDS.TOTL.CN", "NY.GDS.TOTL.ZS", "NY.GDY.TOTL.KN", "NY.GNP.ATLS.CD", "NY.GNP.MKTP.CN", "NY.GNP.MKTP.CN.AD", "NY.GNP.MKTP.CD", "NY.GNP.MKTP.KD", "NY.GNP.MKTP.PP.KD", "NY.GNP.PCAP.CD", "NY.GNP.MKTP.KD.ZG", "NY.GNP.MKTP.PP.CD", "NY.GNP.MKTP.KN", "NY.GNP.PCAP.CN", "NY.GNP.PCAP.KD", "NY.GNP.PCAP.KD.ZG", "NY.GNP.PCAP.PP.CD", "NY.GNP.PCAP.PP.KD", "NY.GNS.ICTR.CD", "NY.GNS.ICTR.GN.ZS", "NY.GNS.ICTR.CN", "NY.GNP.PCAP.KN", "NY.GNS.ICTR.ZS", "NY.GSR.NFCY.CD", "NY.GSR.NFCY.CN", "NY.GSR.NFCY.KN", "NY.TAX.NIND.CD", "NY.TAX.NIND.CN", "NY.TRF.NCTR.CD", "NY.TTF.GNFS.KN", "NY.TRF.NCTR.KN", "NY.TRF.NCTR.CN", "PA.NUS.ATLS", "PA.NUS.PPP", "PA.NUS.PRVT.PP"])
    data = J.get(G_request, "http")(J.template("https://api.worldbank.org/v2/topic/3/indicator?per_page=1000&format=json"))
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
    G_describe_indicator(J.template("World Bank Indicators - Economy & Growth"), "lower", J.obj(("citation", indicatorNote), ("shortName", J.template("WBI Economy"))))
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
    name='world_bank_indicators_economy_growth_TS',
    title='World Bank Indicators - Economy & Growth',
    developer='TrendSpider',
    url='https://trendspider.com/trading-tools-store/indicators/6a7ccf-world-bank-indicators-economy-growth/',
    position='lower',
    inputs=[{'id': 'indicator', 'title': 'Indicator', 'type': 'select_wide', 'default': 'Indicator NV.AGR.TOTL.CD', 'options': ['Indicator NV.AGR.TOTL.CD', 'Indicator NV.AGR.TOTL.ZS', 'Indicator NY.ADJ.DMIN.CD', 'Indicator NY.ADJ.DNGY.CD', 'Indicator NY.ADJ.DMIN.GN.ZS', 'Indicator NY.ADJ.DRES.GN.ZS', 'Indicator NY.ADJ.DNGY.GN.ZS', 'Indicator BM.GSR.INSF.ZS', 'Indicator BX.GSR.INSF.ZS', 'Indicator BG.GSR.NFSV.GD.ZS', 'Indicator BX.GSR.CCIS.CD', 'Indicator BX.GSR.CCIS.ZS', 'Indicator NY.ADJ.AEDU.GN.ZS', 'Indicator NY.ADJ.DCO2.GN.ZS', 'Indicator NY.ADJ.AEDU.CD', 'Indicator NY.ADJ.DCO2.CD', 'Indicator NY.ADJ.DFOR.CD', 'Indicator NY.ADJ.DKAP.CD', 'Indicator NY.ADJ.DFOR.GN.ZS', 'Indicator NY.ADJ.DKAP.GN.ZS', 'Indicator NY.ADJ.ICTR.GN.ZS', 'Indicator NY.ADJ.DPEM.GN.ZS', 'Indicator NY.ADJ.SVNG.CD', 'Indicator NY.ADJ.NNAT.GN.ZS', 'Indicator NY.ADJ.SVNG.GN.ZS', 'Indicator NY.ADJ.SVNX.CD', 'Indicator NY.ADJ.NNAT.CD', 'Indicator NY.ADJ.SVNX.GN.ZS', 'Indicator NY.ADJ.DPEM.CD', 'Indicator BM.KLT.DINV.CD.WD', 'Indicator BX.TRF.PWKR.CD.DT', 'Indicator BX.TRF.PWKR.DT.GD.ZS', 'Indicator BM.KLT.DINV.WD.GD.ZS', 'Indicator BN.KLT.DINV.CD', 'Indicator BX.KLT.DINV.WD.GD.ZS', 'Indicator BX.KLT.DINV.CD.WD', 'Indicator BM.TRF.PWKR.CD.DT', 'Indicator BX.PEF.TOTL.CD.WD', 'Indicator BN.KLT.PTXL.CD', 'Indicator FI.RES.XGLD.CD', 'Indicator FI.RES.TOTL.CD', 'Indicator FP.CPI.TOTL.ZG', 'Indicator PA.NUS.ATLS', 'Indicator BM.GSR.TOTL.CD', 'Indicator BN.CAB.XOKA.CD', 'Indicator BX.GSR.TOTL.CD', 'Indicator NY.GNP.MKTP.CD', 'Indicator BM.GSR.GNFS.CD', 'Indicator BM.GSR.CMCP.ZS', 'Indicator BM.GSR.MRCH.CD', 'Indicator BM.GSR.NFSV.CD', 'Indicator BN.GSR.GNFS.CD', 'Indicator BM.GSR.TRVL.ZS', 'Indicator BM.GSR.TRAN.ZS', 'Indicator BN.GSR.MRCH.CD', 'Indicator BX.GSR.CMCP.ZS', 'Indicator BX.GSR.GNFS.CD', 'Indicator BX.GSR.NFSV.CD', 'Indicator BX.GSR.MRCH.CD', 'Indicator BX.GSR.TRAN.ZS', 'Indicator BX.GSR.TRVL.ZS', 'Indicator NE.EXP.GNFS.CD', 'Indicator NE.EXP.GNFS.KD', 'Indicator NE.EXP.GNFS.KD.ZG', 'Indicator NE.EXP.GNFS.ZS', 'Indicator NE.IMP.GNFS.KD', 'Indicator NE.IMP.GNFS.CD', 'Indicator NE.IMP.GNFS.KD.ZG', 'Indicator NE.RSB.GNFS.ZS', 'Indicator NE.IMP.GNFS.ZS', 'Indicator NE.RSB.GNFS.CD', 'Indicator NE.TRD.GNFS.ZS', 'Indicator NY.EXP.CAPM.KN', 'Indicator BM.GSR.FCTY.CD', 'Indicator BM.GSR.ROYL.CD', 'Indicator BM.TRF.PRVT.CD', 'Indicator BN.CAB.XOKA.GD.ZS', 'Indicator BN.GSR.FCTY.CD', 'Indicator BN.FIN.TOTL.CD', 'Indicator BN.KAC.EOMS.CD', 'Indicator BN.RES.INCL.CD', 'Indicator BN.TRF.CURR.CD', 'Indicator BX.GSR.FCTY.CD', 'Indicator BX.GSR.ROYL.CD', 'Indicator BX.TRF.CURR.CD', 'Indicator GC.XPN.TOTL.GD.ZS', 'Indicator GC.DOD.TOTL.GD.ZS', 'Indicator NE.CON.GOVT.KD', 'Indicator NE.CON.GOVT.CD', 'Indicator NE.CON.GOVT.KD.ZG', 'Indicator NE.CON.GOVT.CN', 'Indicator GC.REV.XGRT.GD.ZS', 'Indicator NE.CON.GOVT.KN', 'Indicator BN.TRF.KOGT.CD', 'Indicator NE.CON.GOVT.ZS', 'Indicator NE.CON.PRVT.CN', 'Indicator NE.CON.PRVT.CD', 'Indicator NE.CON.PRVT.KD', 'Indicator NE.CON.PRVT.KD.ZG', 'Indicator NE.CON.PRVT.KN', 'Indicator NE.CON.PRVT.CN.AD', 'Indicator NE.CON.PRVT.PC.KD.ZG', 'Indicator NE.CON.PRVT.PC.KD', 'Indicator NE.CON.PRVT.ZS', 'Indicator NE.CON.PRVT.PP.KD', 'Indicator NE.CON.PRVT.PP.CD', 'Indicator NE.CON.TOTL.CD', 'Indicator NE.CON.TOTL.CN', 'Indicator NE.CON.TOTL.KN', 'Indicator NE.CON.TOTL.KD', 'Indicator NE.CON.TOTL.ZS', 'Indicator NE.DAB.DEFL.ZS', 'Indicator NE.CON.TOTL.KD.ZG', 'Indicator NE.DAB.TOTL.CN', 'Indicator NE.DAB.TOTL.KN', 'Indicator NE.DAB.TOTL.CD', 'Indicator NE.DAB.TOTL.ZS', 'Indicator NE.DAB.TOTL.KD', 'Indicator NE.EXP.GNFS.CN', 'Indicator NE.GDI.FTOT.CD', 'Indicator NE.GDI.FTOT.CN', 'Indicator NE.GDI.FTOT.KD', 'Indicator NE.EXP.GNFS.KN', 'Indicator NE.GDI.FTOT.KD.ZG', 'Indicator NE.GDI.FTOT.ZS', 'Indicator NE.GDI.FTOT.KN', 'Indicator NE.GDI.STKB.KN', 'Indicator NE.GDI.STKB.CD', 'Indicator NE.GDI.STKB.CN', 'Indicator NE.GDI.TOTL.CN', 'Indicator NE.GDI.TOTL.CD', 'Indicator NE.GDI.TOTL.KN', 'Indicator NE.GDI.TOTL.KD', 'Indicator NE.GDI.TOTL.KD.ZG', 'Indicator NE.GDI.TOTL.ZS', 'Indicator NE.IMP.GNFS.KN', 'Indicator NE.IMP.GNFS.CN', 'Indicator NV.AGR.EMPL.KD', 'Indicator NE.RSB.GNFS.KN', 'Indicator NE.RSB.GNFS.CN', 'Indicator NV.AGR.TOTL.KD', 'Indicator NV.AGR.TOTL.CN', 'Indicator NV.IND.MANF.CD', 'Indicator NV.IND.MANF.ZS', 'Indicator NV.IND.EMPL.KD', 'Indicator NV.IND.MANF.KD', 'Indicator NV.IND.MANF.CN', 'Indicator NV.IND.TOTL.CD', 'Indicator NV.IND.TOTL.CN', 'Indicator NV.IND.TOTL.KD', 'Indicator NV.IND.TOTL.ZS', 'Indicator NV.MNF.CHEM.ZS.UN', 'Indicator NV.MNF.MTRN.ZS.UN', 'Indicator NV.MNF.TECH.ZS.UN', 'Indicator NV.MNF.FBTO.ZS.UN', 'Indicator NV.SRV.EMPL.KD', 'Indicator NV.MNF.OTHR.ZS.UN', 'Indicator NV.MNF.TXTL.ZS.UN', 'Indicator NV.SRV.TOTL.CN', 'Indicator NV.SRV.TOTL.KD', 'Indicator NV.SRV.TOTL.ZS', 'Indicator NV.SRV.TOTL.CD', 'Indicator NY.ADJ.NNTY.KD', 'Indicator NY.ADJ.NNTY.CD', 'Indicator NY.ADJ.NNTY.KD.ZG', 'Indicator NY.ADJ.NNTY.PC.KD', 'Indicator NY.ADJ.NNTY.PC.KD.ZG', 'Indicator NY.ADJ.NNTY.PC.CD', 'Indicator NY.GDP.DEFL.ZS', 'Indicator NY.GDP.DEFL.KD.ZG', 'Indicator NY.GDP.DISC.CN', 'Indicator NY.GDP.DISC.KN', 'Indicator NY.GDP.FCST.CD', 'Indicator NY.GDP.MKTP.CD', 'Indicator NY.GDP.FCST.KD', 'Indicator NY.GDP.FCST.CN', 'Indicator NY.GDP.MKTP.CN', 'Indicator NY.GDP.MKTP.CN.AD', 'Indicator NY.GDP.MKTP.KD', 'Indicator NY.GDP.MKTP.KD.ZG', 'Indicator NY.GDP.MKTP.KN', 'Indicator NY.GDP.MKTP.PP.CD', 'Indicator NY.GDP.PCAP.CD', 'Indicator NY.GDP.MKTP.PP.KD', 'Indicator NY.GDP.PCAP.CN', 'Indicator NY.GDP.PCAP.KD', 'Indicator NY.GDP.PCAP.KD.ZG', 'Indicator NY.GDP.PCAP.PP.KD', 'Indicator NY.GDS.TOTL.CD', 'Indicator NY.GDP.PCAP.PP.CD', 'Indicator NY.GDP.PCAP.KN', 'Indicator NY.GDS.TOTL.CN', 'Indicator NY.GDS.TOTL.ZS', 'Indicator NY.GDY.TOTL.KN', 'Indicator NY.GNP.ATLS.CD', 'Indicator NY.GNP.MKTP.CN', 'Indicator NY.GNP.MKTP.CN.AD', 'Indicator NY.GNP.MKTP.KD', 'Indicator NY.GNP.MKTP.PP.KD', 'Indicator NY.GNP.PCAP.CD', 'Indicator NY.GNP.MKTP.KD.ZG', 'Indicator NY.GNP.MKTP.PP.CD', 'Indicator NY.GNP.MKTP.KN', 'Indicator NY.GNP.PCAP.CN', 'Indicator NY.GNP.PCAP.KD', 'Indicator NY.GNP.PCAP.KD.ZG', 'Indicator NY.GNP.PCAP.PP.CD', 'Indicator NY.GNP.PCAP.PP.KD', 'Indicator NY.GNS.ICTR.CD', 'Indicator NY.GNS.ICTR.GN.ZS', 'Indicator NY.GNS.ICTR.CN', 'Indicator NY.GNP.PCAP.KN', 'Indicator NY.GNS.ICTR.ZS', 'Indicator NY.GSR.NFCY.CD', 'Indicator NY.GSR.NFCY.CN', 'Indicator NY.GSR.NFCY.KN', 'Indicator NY.TAX.NIND.CD', 'Indicator NY.TAX.NIND.CN', 'Indicator NY.TRF.NCTR.CD', 'Indicator NY.TTF.GNFS.KN', 'Indicator NY.TRF.NCTR.KN', 'Indicator NY.TRF.NCTR.CN', 'Indicator PA.NUS.PPP', 'Indicator PA.NUS.PRVT.PP']}, {'id': 'country', 'title': 'Country', 'type': 'select_wide', 'default': 'United States', 'options': ['Australia', 'Canada', 'China', 'European Union', 'Japan', 'Mexico', 'United Kingdom', 'United States', 'World']}],
    outputs=['line'],
    signals=[],
    requires=['http'],
    parity='exact',
)
