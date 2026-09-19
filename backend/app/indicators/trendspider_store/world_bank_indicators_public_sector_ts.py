"""
World Bank Indicators - Public Sector -- TrendSpider store indicator by TrendSpider + Partner.

Registered as "world_bank_indicators_public_sector_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6a7ccf-world-bank-indicators-public-sector/)
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
    validIndicatorIds = J.JSArray(["GC.AST.TOTL.GD.ZS", "GC.AST.TOTL.CN", "GC.DOD.TOTL.CN", "GC.DOD.TOTL.GD.ZS", "GC.LBL.TOTL.CN", "GC.NFN.TOTL.CN", "GC.LBL.TOTL.GD.ZS", "GC.NFN.TOTL.GD.ZS", "GC.NLD.TOTL.CN", "GC.NLD.TOTL.GD.ZS", "GC.REV.GOTR.CN", "GC.REV.SOCL.ZS", "GC.REV.XGRT.CN", "GC.REV.SOCL.CN", "GC.REV.GOTR.ZS", "GC.REV.XGRT.GD.ZS", "GC.TAX.GSRV.CN", "GC.TAX.GSRV.RV.ZS", "GC.TAX.IMPT.CN", "GC.TAX.IMPT.ZS", "GC.TAX.GSRV.VA.ZS", "GC.TAX.INTT.CN", "GC.TAX.OTHR.CN", "GC.TAX.OTHR.RV.ZS", "GC.TAX.TOTL.CN", "GC.TAX.INTT.RV.ZS", "GC.TAX.TOTL.GD.ZS", "GC.TAX.YPKG.CN", "GC.TAX.YPKG.RV.ZS", "GC.TAX.YPKG.ZS", "GC.XPN.COMP.ZS", "GC.XPN.GSRV.CN", "GC.XPN.GSRV.ZS", "GC.XPN.COMP.CN", "GC.XPN.INTP.CN", "GC.XPN.INTP.ZS", "GC.XPN.OTHR.CN", "GC.XPN.INTP.RV.ZS", "GC.XPN.OTHR.ZS", "GC.XPN.TOTL.CN", "GC.XPN.TOTL.GD.ZS", "GC.XPN.TRFT.ZS", "GC.XPN.TRFT.CN", "HD.HCI.OVRL.FE", "HD.HCI.OVRL", "HD.HCI.OVRL.LB", "HD.HCI.OVRL.LB.MA", "HD.HCI.OVRL.MA", "HD.HCI.OVRL.LB.FE", "HD.HCI.OVRL.UB.FE", "HD.HCI.OVRL.UB.MA", "HD.HCI.OVRL.UB", "IQ.SPI.OVRL", "IQ.SPI.PIL1", "IQ.SPI.PIL5", "IQ.SPI.PIL3", "IQ.SPI.PIL4", "MS.MIL.MPRT.KD", "MS.MIL.TOTL.TF.ZS", "MS.MIL.XPND.CD", "MS.MIL.XPND.CN", "MS.MIL.TOTL.P1", "MS.MIL.XPND.GD.ZS", "MS.MIL.XPND.ZS", "IQ.SPI.PIL2", "MS.MIL.XPRT.KD", "SG.GEN.PARL.ZS", "VC.BTL.DETH", "VC.IDP.NWDS", "VC.IHR.PSRC.FE.P5", "VC.IHR.PSRC.P5", "VC.IHR.PSRC.MA.P5"])
    data = J.get(G_request, "http")(J.template("https://api.worldbank.org/v2/topic/13/indicator?per_page=1000&format=json"))
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
    G_describe_indicator(J.template("World Bank Indicators - Public Sector"), "lower", J.obj(("citation", indicatorNote), ("shortName", J.template("WBI Public Sector"))))
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
    name='world_bank_indicators_public_sector_TS',
    title='World Bank Indicators - Public Sector',
    developer='TrendSpider + Partner',
    url='https://trendspider.com/trading-tools-store/indicators/6a7ccf-world-bank-indicators-public-sector/',
    position='lower',
    inputs=[{'id': 'indicator', 'title': 'Indicator', 'type': 'select_wide', 'default': 'Indicator SG.GEN.PARL.ZS', 'options': ['Indicator SG.GEN.PARL.ZS', 'Indicator GC.TAX.IMPT.ZS', 'Indicator MS.MIL.MPRT.KD', 'Indicator MS.MIL.XPRT.KD', 'Indicator GC.XPN.TOTL.GD.ZS', 'Indicator GC.DOD.TOTL.GD.ZS', 'Indicator GC.REV.XGRT.GD.ZS', 'Indicator GC.AST.TOTL.GD.ZS', 'Indicator GC.AST.TOTL.CN', 'Indicator GC.DOD.TOTL.CN', 'Indicator GC.LBL.TOTL.CN', 'Indicator GC.NFN.TOTL.CN', 'Indicator GC.LBL.TOTL.GD.ZS', 'Indicator GC.NFN.TOTL.GD.ZS', 'Indicator GC.NLD.TOTL.CN', 'Indicator GC.NLD.TOTL.GD.ZS', 'Indicator GC.REV.GOTR.CN', 'Indicator GC.REV.SOCL.ZS', 'Indicator GC.REV.XGRT.CN', 'Indicator GC.REV.SOCL.CN', 'Indicator GC.REV.GOTR.ZS', 'Indicator GC.TAX.GSRV.CN', 'Indicator GC.TAX.GSRV.RV.ZS', 'Indicator GC.TAX.IMPT.CN', 'Indicator GC.TAX.GSRV.VA.ZS', 'Indicator GC.TAX.INTT.CN', 'Indicator GC.TAX.OTHR.CN', 'Indicator GC.TAX.OTHR.RV.ZS', 'Indicator GC.TAX.TOTL.CN', 'Indicator GC.TAX.INTT.RV.ZS', 'Indicator GC.TAX.TOTL.GD.ZS', 'Indicator GC.TAX.YPKG.CN', 'Indicator GC.TAX.YPKG.RV.ZS', 'Indicator GC.TAX.YPKG.ZS', 'Indicator GC.XPN.COMP.ZS', 'Indicator GC.XPN.GSRV.CN', 'Indicator GC.XPN.GSRV.ZS', 'Indicator GC.XPN.COMP.CN', 'Indicator GC.XPN.INTP.CN', 'Indicator GC.XPN.INTP.ZS', 'Indicator GC.XPN.OTHR.CN', 'Indicator GC.XPN.INTP.RV.ZS', 'Indicator GC.XPN.OTHR.ZS', 'Indicator GC.XPN.TOTL.CN', 'Indicator GC.XPN.TRFT.ZS', 'Indicator GC.XPN.TRFT.CN', 'Indicator HD.HCI.OVRL.FE', 'Indicator HD.HCI.OVRL', 'Indicator HD.HCI.OVRL.LB', 'Indicator HD.HCI.OVRL.LB.MA', 'Indicator HD.HCI.OVRL.MA', 'Indicator HD.HCI.OVRL.LB.FE', 'Indicator HD.HCI.OVRL.UB.FE', 'Indicator HD.HCI.OVRL.UB.MA', 'Indicator HD.HCI.OVRL.UB', 'Indicator IQ.SPI.OVRL', 'Indicator IQ.SPI.PIL1', 'Indicator IQ.SPI.PIL5', 'Indicator IQ.SPI.PIL3', 'Indicator IQ.SPI.PIL4', 'Indicator MS.MIL.TOTL.TF.ZS', 'Indicator MS.MIL.XPND.CD', 'Indicator MS.MIL.XPND.CN', 'Indicator MS.MIL.TOTL.P1', 'Indicator MS.MIL.XPND.GD.ZS', 'Indicator MS.MIL.XPND.ZS', 'Indicator IQ.SPI.PIL2', 'Indicator VC.BTL.DETH', 'Indicator VC.IDP.NWDS', 'Indicator VC.IHR.PSRC.FE.P5', 'Indicator VC.IHR.PSRC.P5', 'Indicator VC.IHR.PSRC.MA.P5']}, {'id': 'country', 'title': 'Country', 'type': 'select_wide', 'default': 'United States', 'options': ['Australia', 'Canada', 'China', 'European Union', 'Japan', 'Mexico', 'United Kingdom', 'United States', 'World']}],
    outputs=['line'],
    signals=[],
    requires=['http'],
    parity='exact',
)
