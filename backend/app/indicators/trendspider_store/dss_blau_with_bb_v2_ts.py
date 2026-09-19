"""
DSS Blau with BB - V2 -- TrendSpider store indicator by QXEM.

Registered as "dss_blau_with_bb_v2_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/683625-dss-blau-with-bb-v2/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_add = G["add"]
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_div = G["div"]
    G_ema = G["ema"]
    G_fill = G["fill"]
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_highest = G["highest"]
    G_input = G["input"]
    G_low = G["low"]
    G_lowest = G["lowest"]
    G_mult = G["mult"]
    G_paint = G["paint"]
    G_stdev = G["stdev"]
    G_sub = G["sub"]
    G_describe_indicator("DSS Blau with BB - V2", "lower")
    myFastLength = J.get(G_input, "number")("Fast Length", 10, J.obj(("min", 1)))
    mySlowLength = J.get(G_input, "number")("Slow Length", 15, J.obj(("min", 1)))
    mySmoothing = J.get(G_input, "number")("Smoothing", 5, J.obj(("min", 1)))
    myHighestHigh = G_highest(G_high, myFastLength)
    myLowestLow = G_lowest(G_low, myFastLength)
    myCloseMinusLow = G_sub(G_close, myLowestLow)
    myHighMinusLow = G_sub(myHighestHigh, myLowestLow)
    myFirstSmoothNumerator = G_ema(myCloseMinusLow, mySlowLength)
    myFirstSmoothDenominator = G_ema(myHighMinusLow, mySlowLength)
    myDoubleSmoothNumerator = G_ema(myFirstSmoothNumerator, mySmoothing)
    myDoubleSmoothDenominator = G_ema(myFirstSmoothDenominator, mySmoothing)
    myDSS = G_mult(G_div(myDoubleSmoothNumerator, myDoubleSmoothDenominator), 100)
    mySignalLine = G_ema(myDSS, mySmoothing)
    myBBLength = J.get(G_input, "number")("BB Length", 20, J.obj(("min", 1)))
    myBBMultiplier = J.get(G_input, "number")("BB Multiplier", 1, J.obj(("min", 0.1), ("max", 5), ("step", 0.1)))
    myBBMid = G_ema(myDSS, myBBLength)
    myBBDev = G_mult(G_stdev(myDSS, myBBLength), myBBMultiplier)
    myBBUpper = G_add(myBBMid, myBBDev)
    myBBLower = G_sub(myBBMid, myBBDev)
    myBBColor = J.get(G_input, "color")("BB Color", "#555555")
    myFillColor = J.get(G_input, "color")("BB Fill Color", "#eeeeee")
    myDSSAboveColor = J.get(G_input, "color")("DSS Above Color", "white")
    myDSSBelowColor = J.get(G_input, "color")("DSS Below Color", "yellow")
    myBBUpperPainted = G_paint(myBBUpper, J.obj(("color", myBBColor), ("name", "BB Upper"), ("style", "line")))
    myBBLowerPainted = G_paint(myBBLower, J.obj(("color", myBBColor), ("name", "BB Lower"), ("style", "line")))
    def _f1(_signal=J.undefined, _dss=J.undefined, *_args):
        return (myDSSAboveColor if J.gt(_signal, _dss) else myDSSBelowColor)
    mySignalColor = G_for_every(mySignalLine, myDSS, _f1)
    G_paint(myDSS, J.obj(("color", mySignalColor), ("name", "DSS")))
    G_paint(mySignalLine, J.obj(("color", mySignalColor), ("name", "Signal")))
    G_fill(myBBUpperPainted, myBBLowerPainted, myFillColor, 0.3)


register_store_indicator(
    script,
    name='dss_blau_with_bb_v2_TS',
    title='DSS Blau with BB - V2',
    developer='QXEM',
    url='https://trendspider.com/trading-tools-store/indicators/683625-dss-blau-with-bb-v2/',
    position='lower',
    inputs=[{'id': 'fast_length', 'title': 'Fast Length', 'type': 'number', 'default': 10}, {'id': 'slow_length', 'title': 'Slow Length', 'type': 'number', 'default': 15}, {'id': 'smoothing', 'title': 'Smoothing', 'type': 'number', 'default': 5}, {'id': 'bb_length', 'title': 'BB Length', 'type': 'number', 'default': 20}, {'id': 'bb_multiplier', 'title': 'BB Multiplier', 'type': 'number', 'default': 1}, {'id': 'bb_color', 'title': 'BB Color', 'type': 'color', 'default': '#555555'}, {'id': 'bb_fill_color', 'title': 'BB Fill Color', 'type': 'color', 'default': '#eeeeee'}, {'id': 'dss_above_color', 'title': 'DSS Above Color', 'type': 'color', 'default': 'white'}, {'id': 'dss_below_color', 'title': 'DSS Below Color', 'type': 'color', 'default': 'yellow'}],
    outputs=['bb_upper', 'bb_lower', 'dss', 'signal'],
    signals=[],
    requires=[],
    parity='exact',
)
