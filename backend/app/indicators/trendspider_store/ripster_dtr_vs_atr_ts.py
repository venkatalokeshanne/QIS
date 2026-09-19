"""
Ripster DTR vs ATR -- TrendSpider store indicator by Ripster G.

Registered as "ripster_dtr_vs_atr_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/691aba-ripster-dtr-vs-atr/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_assert = G["assert"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_div = G["div"]
    G_ema = G["ema"]
    G_for_every = G["for_every"]
    G_input = G["input"]
    G_mult = G["mult"]
    G_paint_overlay = G["paint_overlay"]
    G_request = G["request"]
    G_sma = G["sma"]
    G_sub = G["sub"]
    G_wildma = G["wildma"]
    G_wma = G["wma"]
    G_describe_indicator("Ripster DTR vs ATR", "price")
    atrLen = J.get(G_input, "number")("ATR Length", 14)
    atrSmooth = J.get(G_input, "select")("Smoothing Type", "RMA", J.JSArray(["EMA", "RMA", "SMA", "WMA"]))
    def roundVal(val=J.undefined, _p1=J.undefined, *_args):
        _t2 = _p1
        if _t2 is J.undefined:
            _t2 = 2
        decimals = _t2
        factor = J.get(G_Math, "pow")(10, decimals)
        return J.mul(J.div(J.get(G_Math, "round")(J.get(G_Math, "abs")(J.mul(val, factor))), factor), J.get(G_Math, "sign")(val))
    timeframe = "D"
    highTFData = J.get(G_request, "history")(J.get(G_current, "ticker"), timeframe)
    G_assert((not J.truthy(J.get(highTFData, "error"))), J.template("Error fetching data: ", J.get(highTFData, "error")))
    def _f1(h=J.undefined, l=J.undefined, c=J.undefined, _prev=J.undefined, i=J.undefined, *_args):
        prevClose = (J.get(J.get(highTFData, "close"), J.sub(i, 1)) if J.gt(i, 0) else c)
        return J.get(G_Math, "max")(J.sub(h, l), J.get(G_Math, "abs")(J.sub(h, prevClose)), J.get(G_Math, "abs")(J.sub(l, prevClose)))
    trSeries = G_for_every(J.get(highTFData, "high"), J.get(highTFData, "low"), J.get(highTFData, "close"), _f1)
    def _f2(*_args):
        if J.seq(atrSmooth, "EMA"):
            return G_ema(trSeries, atrLen)
        if J.seq(atrSmooth, "SMA"):
            return G_sma(trSeries, atrLen)
        if J.seq(atrSmooth, "WMA"):
            return G_wma(trSeries, atrLen)
        return G_wildma(trSeries, atrLen)
    atrSeries = _f2()
    seriesLength = J.get(G_Math, "min")(J.get(J.get(highTFData, "high"), "length"), J.get(J.get(highTFData, "low"), "length"), J.get(atrSeries, "length"))
    highSeries = J.get(J.get(highTFData, "high"), "slice")(J.neg(seriesLength))
    lowSeries = J.get(J.get(highTFData, "low"), "slice")(J.neg(seriesLength))
    avgATR = J.get(atrSeries, "slice")(J.neg(seriesLength))
    dailyTR = G_sub(highSeries, lowSeries)
    dtrPct = G_mult(G_div(dailyTR, avgATR), 100)
    dtrVal = roundVal(J.get(dailyTR, J.sub(J.get(dailyTR, "length"), 1)), 2)
    atrVal = roundVal(J.get(avgATR, J.sub(J.get(avgATR, "length"), 1)), 2)
    finalText = J.template("DTR: ", dtrVal, "   vs   ATR: ", atrVal, "   (", roundVal(J.get(dtrPct, J.sub(J.get(dtrPct, "length"), 1)), 0), "%)")
    atrColor = ("green" if J.le(J.get(dtrPct, J.sub(J.get(dtrPct, "length"), 1)), 70) else ("#d78585" if J.ge(J.get(dtrPct, J.sub(J.get(dtrPct, "length"), 1)), 90) else "#ffd500"))
    textColor = ("black" if J.seq(atrColor, "#ffd500") else "white")
    rows = J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", finalText), ("background", atrColor), ("padding", "10px"), ("color", textColor), ("fontSize", "14px"))])))])
    G_paint_overlay("DTR ATR Overlay", J.obj(("position", "top_right")), J.obj(("border", "1px solid var(--border-color)"), ("borderRadius", "6px"), ("background", "var(--background-color)"), ("rows", rows)))


register_store_indicator(
    script,
    name='ripster_dtr_vs_atr_TS',
    title='Ripster DTR vs ATR',
    developer='Ripster G',
    url='https://trendspider.com/trading-tools-store/indicators/691aba-ripster-dtr-vs-atr/',
    position='price',
    inputs=[{'id': 'atr_length', 'title': 'ATR Length', 'type': 'number', 'default': 14}, {'id': 'smoothing_type', 'title': 'Smoothing Type', 'type': 'select_wide', 'default': 'RMA', 'options': ['EMA', 'RMA', 'SMA', 'WMA']}],
    outputs=[],
    signals=[],
    requires=['history'],
    parity='exact',
)
