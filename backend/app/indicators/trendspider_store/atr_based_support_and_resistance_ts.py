"""
ATR Based Support and Resistance -- TrendSpider store indicator by Kodexius.

Registered as "atr_based_support_and_resistance_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68ebfc-atr-based-support-and-resistance/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_atr = G["atr"]
    G_close = G["close"]
    G_color_candles = G["color_candles"]
    G_describe_indicator = G["describe_indicator"]
    G_fill = G["fill"]
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_input = G["input"]
    G_low = G["low"]
    G_mult = G["mult"]
    G_open = G["open"]
    G_paint = G["paint"]
    G_series_of = G["series_of"]
    G_describe_indicator("ATR Based Support and Resistance")
    atrPeriod = J.get(G_input, "number")("ATR Length", 21, J.obj(("min", 1), ("max", 100)))
    atrMultiplier = J.get(G_input, "number")("ATR Multiplier", 1.718, J.obj(("min", 0.1), ("max", 10)))
    lineLength = J.get(G_input, "number")("Horizontal Line Length", 50, J.obj(("min", 1), ("max", 500)))
    wickPercent = J.get(G_input, "number")("Wick %", 70, J.obj(("min", 0), ("max", 100)))
    downLineStyle = J.get(G_input, "select")("Down Zone Line Style", "line", J.JSArray(["line", "dotted"]))
    downBorderColor = J.get(G_input, "color")("Down Zone Border Color", "rgba(255, 0, 0, 0.2)")
    downBgColor = J.get(G_input, "color")("Down Zone Background Color", "rgba(255, 0, 0, 0.7)")
    upLineStyle = J.get(G_input, "select")("Up Zone Line Style", "line", J.JSArray(["line", "dotted"]))
    upBorderColor = J.get(G_input, "color")("Up Zone Border Color", "rgba(0, 255, 0, 0.2)")
    upBgColor = J.get(G_input, "color")("Up Zone Background Color", "rgba(0, 255, 0, 0.7)")
    myAtr = G_atr(G_high, G_low, G_close, atrPeriod)
    myAtrMultiplied = G_mult(myAtr, atrMultiplier)
    def _f1(_h=J.undefined, _l=J.undefined, _c=J.undefined, _prev=J.undefined, _i=J.undefined, *_args):
        if J.seq(_i, 0):
            return J.sub(_h, _l)
        prevClose = J.get(G_close, J.sub(_i, 1))
        return J.get(G_Math, "max")(J.sub(_h, _l), J.get(G_Math, "abs")(J.sub(_h, prevClose)), J.get(G_Math, "abs")(J.sub(_l, prevClose)))
    myTrueRange = G_for_every(G_high, G_low, G_close, _f1)
    def _f2(_tr=J.undefined, _c=J.undefined, _o=J.undefined, _atrMult=J.undefined, _prev=J.undefined, _i=J.undefined, *_args):
        if J.seq(_i, 0):
            return False
        prevTr = J.get(myTrueRange, J.sub(_i, 1))
        prevAtr = J.get(myAtr, J.sub(_i, 1))
        return (J.le(prevTr, prevAtr) if J.truthy(_t1 := (J.gt(_c, _o) if J.truthy(_t2 := J.ge(_tr, _atrMult)) else _t2)) else _t1)
    myImpulseUp = G_for_every(myTrueRange, G_close, G_open, myAtrMultiplied, _f2)
    def _f3(_tr=J.undefined, _c=J.undefined, _o=J.undefined, _atrMult=J.undefined, _prev=J.undefined, _i=J.undefined, *_args):
        if J.seq(_i, 0):
            return False
        prevTr = J.get(myTrueRange, J.sub(_i, 1))
        prevAtr = J.get(myAtr, J.sub(_i, 1))
        return (J.le(prevTr, prevAtr) if J.truthy(_t1 := (J.lt(_c, _o) if J.truthy(_t2 := J.ge(_tr, _atrMult)) else _t2)) else _t1)
    myImpulseDown = G_for_every(myTrueRange, G_close, G_open, myAtrMultiplied, _f3)
    def _f4(_up=J.undefined, _down=J.undefined, *_args):
        if J.truthy(_up):
            return "green"
        if J.truthy(_down):
            return "red"
        return None
    myCandleColors = G_for_every(myImpulseUp, myImpulseDown, _f4)
    G_color_candles(myCandleColors)
    def _f5(_up=J.undefined, *_args):
        return ("·" if J.truthy(_up) else None)
    myImpulseUpMarkers = G_for_every(myImpulseUp, _f5)
    def _f6(_down=J.undefined, *_args):
        return ("·" if J.truthy(_down) else None)
    myImpulseDownMarkers = G_for_every(myImpulseDown, _f6)
    G_paint(myImpulseUpMarkers, J.obj(("style", "labels_below"), ("color", "green"), ("name", "Impulse Up")))
    G_paint(myImpulseDownMarkers, J.obj(("style", "labels_above"), ("color", "red"), ("name", "Impulse Down")))
    totalPercentCalc = J.mul(wickPercent, 0.01)
    myDownZoneTop = G_series_of(None)
    myDownZoneBottom = G_series_of(None)
    i = 0
    while J.lt(i, J.get(G_close, "length")):
        if J.truthy(J.get(myImpulseDown, i)):
            impulseDownWick = J.sub(J.get(G_high, i), J.get(G_open, i))
            wickPercentValue = J.div(impulseDownWick, J.get(myTrueRange, i))
            if J.le(wickPercentValue, totalPercentCalc):
                J.set(myDownZoneTop, i, J.get(G_high, i))
                J.set(myDownZoneBottom, i, J.get(G_open, i))
                j = 1
                while (J.le(j, lineLength) and J.lt(J.add(i, j), J.get(G_close, "length"))):
                    J.set(myDownZoneTop, J.add(i, j), J.get(G_high, i))
                    J.set(myDownZoneBottom, J.add(i, j), J.get(G_open, i))
                    j = J.inc(j)
        i = J.inc(i)
    myUpZoneTop = G_series_of(None)
    myUpZoneBottom = G_series_of(None)
    i_2 = 0
    while J.lt(i_2, J.get(G_close, "length")):
        if J.truthy(J.get(myImpulseUp, i_2)):
            impulseUpWick = J.sub(J.get(G_open, i_2), J.get(G_low, i_2))
            wickPercentValue_2 = J.div(impulseUpWick, J.get(myTrueRange, i_2))
            if J.le(wickPercentValue_2, totalPercentCalc):
                J.set(myUpZoneTop, i_2, J.get(G_open, i_2))
                J.set(myUpZoneBottom, i_2, J.get(G_low, i_2))
                j_2 = 1
                while (J.le(j_2, lineLength) and J.lt(J.add(i_2, j_2), J.get(G_close, "length"))):
                    J.set(myUpZoneTop, J.add(i_2, j_2), J.get(G_open, i_2))
                    J.set(myUpZoneBottom, J.add(i_2, j_2), J.get(G_low, i_2))
                    j_2 = J.inc(j_2)
        i_2 = J.inc(i_2)
    downTopLine = G_paint(myDownZoneTop, J.obj(("style", downLineStyle), ("color", downBorderColor), ("name", "Down Zone Top"), ("hidden", True)))
    downBottomLine = G_paint(myDownZoneBottom, J.obj(("style", downLineStyle), ("color", downBorderColor), ("name", "Down Zone Bottom"), ("hidden", True)))
    G_fill(downTopLine, downBottomLine, downBgColor, 0.7, "Down Supply Zone")
    upTopLine = G_paint(myUpZoneTop, J.obj(("style", upLineStyle), ("color", upBorderColor), ("name", "Up Zone Top"), ("hidden", True)))
    upBottomLine = G_paint(myUpZoneBottom, J.obj(("style", upLineStyle), ("color", upBorderColor), ("name", "Up Zone Bottom"), ("hidden", True)))
    G_fill(upTopLine, upBottomLine, upBgColor, 0.7, "Up Demand Zone")


register_store_indicator(
    script,
    name='atr_based_support_and_resistance_TS',
    title='ATR Based Support and Resistance',
    developer='Kodexius',
    url='https://trendspider.com/trading-tools-store/indicators/68ebfc-atr-based-support-and-resistance/',
    position='price',
    inputs=[{'id': 'atr_length', 'title': 'ATR Length', 'type': 'number', 'default': 21}, {'id': 'atr_multiplier', 'title': 'ATR Multiplier', 'type': 'number', 'default': 1.718}, {'id': 'horizontal_line_length', 'title': 'Horizontal Line Length', 'type': 'number', 'default': 50}, {'id': 'wick__', 'title': 'Wick %', 'type': 'number', 'default': 70}, {'id': 'down_zone_line_style', 'title': 'Down Zone Line Style', 'type': 'select_wide', 'default': 'line', 'options': ['line', 'dotted']}, {'id': 'down_zone_border_color', 'title': 'Down Zone Border Color', 'type': 'color', 'default': 'rgba(255, 0, 0, 0.2)'}, {'id': 'down_zone_background_color', 'title': 'Down Zone Background Color', 'type': 'color', 'default': 'rgba(255, 0, 0, 0.7)'}, {'id': 'up_zone_line_style', 'title': 'Up Zone Line Style', 'type': 'select_wide', 'default': 'line', 'options': ['line', 'dotted']}, {'id': 'up_zone_border_color', 'title': 'Up Zone Border Color', 'type': 'color', 'default': 'rgba(0, 255, 0, 0.2)'}, {'id': 'up_zone_background_color', 'title': 'Up Zone Background Color', 'type': 'color', 'default': 'rgba(0, 255, 0, 0.7)'}],
    outputs=['cdl', 'impulse_up', 'impulse_down', 'down_zone_top', 'down_zone_bottom', 'up_zone_top', 'up_zone_bottom'],
    signals=[],
    requires=[],
    parity='exact',
)
