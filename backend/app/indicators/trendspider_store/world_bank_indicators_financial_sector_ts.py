"""
World Bank Indicators - Financial Sector -- TrendSpider store indicator by TrendSpider.

Registered as "world_bank_indicators_financial_sector_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6a6296-world-bank-indicators-financial-sector/)
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
    validIndicatorIds = J.JSArray(["BM.KLT.DINV.CD.WD", "BX.TRF.PWKR.CD.DT", "BX.TRF.PWKR.DT.GD.ZS", "BM.KLT.DINV.WD.GD.ZS", "BN.KLT.DINV.CD", "BX.KLT.DINV.WD.GD.ZS", "BX.KLT.DINV.CD.WD", "BM.TRF.PWKR.CD.DT", "BX.PEF.TOTL.CD.WD", "CM.MKT.INDX.ZG", "BN.KLT.PTXL.CD", "CM.MKT.LDOM.NO", "CM.MKT.LCAP.CD", "CM.MKT.LCAP.GD.ZS", "CM.MKT.TRAD.CD", "CM.MKT.TRNR", "FB.ATM.TOTL.P5", "CM.MKT.TRAD.GD.ZS", "FB.BNK.CAPA.ZS", "FB.CBK.BRCH.P5", "FD.AST.PRVT.GD.ZS", "FM.AST.CGOV.ZG.M3", "FB.AST.NPER.ZS", "FD.RES.LIQU.AS.ZS", "FI.RES.XGLD.CD", "FI.RES.TOTL.MO", "FM.AST.DOMO.ZG.M3", "FI.RES.TOTL.CD", "FM.AST.DOMS.CN", "FM.AST.PRVT.GD.ZS", "FM.LBL.BMNY.CN", "FM.LBL.BMNY.GD.ZS", "FM.LBL.BMNY.ZG", "FM.AST.PRVT.ZG.M3", "FP.CPI.TOTL", "FM.LBL.BMNY.IR.ZS", "FP.CPI.TOTL.ZG", "FM.AST.NFRG.CN", "FR.INR.LEND", "FR.INR.RINR", "FS.AST.DOMO.GD.ZS", "FS.AST.CGOV.GD.ZS", "FR.INR.RISK", "FS.AST.PRVT.GD.ZS", "FX.OWN.TOTL.40.ZS", "FX.OWN.TOTL.FE.ZS", "FX.OWN.TOTL.60.ZS", "FX.OWN.TOTL.OL.ZS", "FX.OWN.TOTL.MA.ZS", "FX.OWN.TOTL.SO.ZS", "FX.OWN.TOTL.YG.ZS", "FX.OWN.TOTL.ZS", "GFDD.AI.02", "FX.OWN.TOTL.PL.ZS", "FS.AST.DOMS.GD.ZS", "GFDD.AI.06", "GFDD.AI.05", "GFDD.AI.07", "GFDD.AI.10", "GFDD.AI.08", "GFDD.AI.11", "GFDD.AI.12", "GFDD.AI.15", "GFDD.AI.13", "GFDD.AI.16", "GFDD.AI.20", "GFDD.AI.14", "GFDD.AI.21", "GFDD.AI.19", "GFDD.AI.18", "GFDD.AI.23", "GFDD.AI.17", "GFDD.AI.22", "GFDD.AI.09", "GFDD.AI.25", "GFDD.AI.26", "GFDD.AM.02", "GFDD.AM.01", "GFDD.DI.01", "GFDD.DI.02", "GFDD.DI.06", "GFDD.DI.03", "GFDD.DI.05", "GFDD.DI.07", "GFDD.DI.04", "GFDD.DI.08", "GFDD.DI.11", "GFDD.DI.12", "GFDD.DI.10", "GFDD.DI.13", "GFDD.DM.01", "GFDD.DM.02", "GFDD.DI.14", "GFDD.DI.09", "GFDD.DM.08", "GFDD.DM.09", "GFDD.DM.10", "GFDD.DM.07", "GFDD.DM.06", "GFDD.DM.05", "GFDD.EI.01", "GFDD.EI.03", "GFDD.EI.05", "GFDD.EI.06", "GFDD.EI.07", "GFDD.EI.09", "GFDD.EI.08", "GFDD.EI.04", "GFDD.OI.01", "GFDD.OI.02", "GFDD.EM.01", "GFDD.EI.10", "GFDD.OI.06", "GFDD.OI.07", "GFDD.OI.08", "GFDD.OI.09", "GFDD.OI.12", "GFDD.OI.10", "GFDD.OI.13", "GFDD.OI.11", "GFDD.OI.16", "GFDD.OI.14", "GFDD.OI.15", "GFDD.OI.18", "GFDD.OI.17", "GFDD.OI.19", "GFDD.SI.01", "GFDD.OM.02", "GFDD.SI.03", "GFDD.SI.02", "GFDD.SI.05", "GFDD.SI.06", "GFDD.SI.04", "GFDD.OM.01", "GFDD.SM.01", "GFDD.SI.07", "NY.GDP.DEFL.KD.ZG.AD", "NY.GDP.DEFL.ZS.AD", "PA.NUS.FCRF", "PX.REX.REER", "PA.NUS.ATLS", "SI.RMT.COST.OB.ZS", "SM.POP.TOTL", "SM.POP.TOTL.ZS", "SM.POP.NETM"])
    data = J.get(G_request, "http")(J.template("https://api.worldbank.org/v2/topic/7/indicator?per_page=1000&format=json"))
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
    G_describe_indicator(J.template("World Bank Indicators - Financial Sector"), "lower", J.obj(("citation", indicatorNote), ("shortName", J.template("WBI Finance"))))
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
    name='world_bank_indicators_financial_sector_TS',
    title='World Bank Indicators - Financial Sector',
    developer='TrendSpider',
    url='https://trendspider.com/trading-tools-store/indicators/6a6296-world-bank-indicators-financial-sector/',
    position='lower',
    inputs=[{'id': 'indicator', 'title': 'Indicator', 'type': 'select_wide', 'default': 'Indicator SM.POP.NETM', 'options': ['Indicator SM.POP.NETM', 'Indicator FS.AST.PRVT.GD.ZS', 'Indicator BM.KLT.DINV.CD.WD', 'Indicator BX.TRF.PWKR.CD.DT', 'Indicator BX.TRF.PWKR.DT.GD.ZS', 'Indicator BM.KLT.DINV.WD.GD.ZS', 'Indicator BN.KLT.DINV.CD', 'Indicator BX.KLT.DINV.WD.GD.ZS', 'Indicator BX.KLT.DINV.CD.WD', 'Indicator BM.TRF.PWKR.CD.DT', 'Indicator BX.PEF.TOTL.CD.WD', 'Indicator CM.MKT.INDX.ZG', 'Indicator BN.KLT.PTXL.CD', 'Indicator CM.MKT.LDOM.NO', 'Indicator CM.MKT.LCAP.CD', 'Indicator CM.MKT.LCAP.GD.ZS', 'Indicator CM.MKT.TRAD.CD', 'Indicator CM.MKT.TRNR', 'Indicator FB.ATM.TOTL.P5', 'Indicator CM.MKT.TRAD.GD.ZS', 'Indicator FB.BNK.CAPA.ZS', 'Indicator FB.CBK.BRCH.P5', 'Indicator FD.AST.PRVT.GD.ZS', 'Indicator FM.AST.CGOV.ZG.M3', 'Indicator FB.AST.NPER.ZS', 'Indicator FD.RES.LIQU.AS.ZS', 'Indicator FI.RES.XGLD.CD', 'Indicator FI.RES.TOTL.MO', 'Indicator FM.AST.DOMO.ZG.M3', 'Indicator FI.RES.TOTL.CD', 'Indicator FM.AST.DOMS.CN', 'Indicator FM.AST.PRVT.GD.ZS', 'Indicator FM.LBL.BMNY.CN', 'Indicator FM.LBL.BMNY.GD.ZS', 'Indicator FM.LBL.BMNY.ZG', 'Indicator FM.AST.PRVT.ZG.M3', 'Indicator FP.CPI.TOTL', 'Indicator FM.LBL.BMNY.IR.ZS', 'Indicator FP.CPI.TOTL.ZG', 'Indicator FM.AST.NFRG.CN', 'Indicator FR.INR.LEND', 'Indicator FR.INR.RINR', 'Indicator FS.AST.DOMO.GD.ZS', 'Indicator FS.AST.CGOV.GD.ZS', 'Indicator FR.INR.RISK', 'Indicator FX.OWN.TOTL.40.ZS', 'Indicator FX.OWN.TOTL.FE.ZS', 'Indicator FX.OWN.TOTL.60.ZS', 'Indicator FX.OWN.TOTL.OL.ZS', 'Indicator FX.OWN.TOTL.MA.ZS', 'Indicator FX.OWN.TOTL.SO.ZS', 'Indicator FX.OWN.TOTL.YG.ZS', 'Indicator FX.OWN.TOTL.ZS', 'Indicator FX.OWN.TOTL.PL.ZS', 'Indicator FS.AST.DOMS.GD.ZS', 'Indicator NY.GDP.DEFL.KD.ZG.AD', 'Indicator NY.GDP.DEFL.ZS.AD', 'Indicator PA.NUS.FCRF', 'Indicator PX.REX.REER', 'Indicator PA.NUS.ATLS', 'Indicator SI.RMT.COST.OB.ZS', 'Indicator SM.POP.TOTL', 'Indicator SM.POP.TOTL.ZS']}, {'id': 'country', 'title': 'Country', 'type': 'select_wide', 'default': 'United States', 'options': ['Australia', 'Canada', 'China', 'European Union', 'Japan', 'Mexico', 'United Kingdom', 'United States', 'World']}],
    outputs=['line'],
    signals=[],
    requires=['http'],
    parity='exact',
)
