"""
Bottom Catcher Signal (HTF) -- TrendSpider store indicator by Rock Regan.

Registered as "bottom_catcher_signal_htf_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68abb6-bottom-catcher-signal-htf/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_String = G["String"]
    G_atr = G["atr"]
    G_close = G["close"]
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_high = G["high"]
    G_highest = G["highest"]
    G_input = G["input"]
    G_library = G["library"]
    G_low = G["low"]
    G_lowest = G["lowest"]
    G_open = G["open"]
    G_paint = G["paint"]
    G_paint_overlay = G["paint_overlay"]
    G_parseInt = G["parseInt"]
    G_register_signal = G["register_signal"]
    G_sma = G["sma"]
    G_time = G["time"]
    G_volume = G["volume"]
    def scaleVal(n=J.undefined, *_args):
        return J.get(G_Math, "max")(1, J.get(G_Math, "round")(J.div(J.mul(n, uiScale), 100)))
    def px(n=J.undefined, *_args):
        return J.add(scaleVal(n), "px")
    def pad(v=J.undefined, h=J.undefined, *_args):
        return J.add(J.add(px(v), " "), px(h))
    def toMs(ts=J.undefined, *_args):
        if ((ts is None) or (ts is J.undefined)):
            return ts
        return (J.mul(ts, 1000) if J.lt(ts, 100000000000) else ts)
    def formatMMDDYYYY(ts=J.undefined, *_args):
        ms = toMs(ts)
        return J.get(moment(ms), "format")("MM-DD-YYYY")
    def barCloseMs(i_2=J.undefined, *_args):
        openMs = toMs(J.get(G_time, i_2))
        resStr = G_String(J.get(G_constants, "resolution"))
        m = moment(openMs)
        if J.truthy(J.get(J.regex("^d+$", ""), "test")(resStr)):
            mins = G_parseInt(resStr, 10)
            return J.get(J.get(J.get(m, "add")(mins, "minutes"), "subtract")(1, "second"), "valueOf")()
        if J.seq(resStr, "D"):
            return J.get(J.get(m, "endOf")("day"), "valueOf")()
        if J.seq(resStr, "W"):
            return J.get(J.get(m, "endOf")("week"), "valueOf")()
        if J.seq(resStr, "M"):
            return J.get(J.get(m, "endOf")("month"), "valueOf")()
        return J.get(J.get(m, "endOf")("day"), "valueOf")()
    G_describe_indicator("Bottom Catcher Signal (HTF)", J.obj(("shortName", "\ud83c\udfaf BC v3.1")))
    volMaLength = J.get(G_input, "number")("Volume MA Length", 50, J.obj(("min", 10), ("step", 1)))
    stochLen = J.get(G_input, "number")("Stochastic Length", 14, J.obj(("min", 5), ("step", 1)))
    stochKSmooth = J.get(G_input, "number")("%K Smoothing", 3, J.obj(("min", 1), ("step", 1)))
    bcBandLower1 = J.get(G_input, "number")("Band1 Lower", 10, J.obj(("min", 0), ("step", 1)))
    bcBandUpper1 = J.get(G_input, "number")("Band1 Upper", 20, J.obj(("min", 1), ("step", 1)))
    bcBandLower2 = J.get(G_input, "number")("Band2 Lower", 50, J.obj(("min", 0), ("step", 1)))
    bcBandUpper2 = J.get(G_input, "number")("Band2 Upper", 60, J.obj(("min", 1), ("step", 1)))
    atrLen = J.get(G_input, "number")("ATR Length", 14, J.obj(("min", 5), ("step", 1)))
    bodyAtrMultiplier = J.get(G_input, "number")("Body ≥ ATR x", 0.6, J.obj(("min", 0.1), ("step", 0.05)))
    rvolThreshold = J.get(G_input, "number")("RVOL Threshold", 1.3, J.obj(("min", 0.5), ("step", 0.05)))
    prevVolCapMult = J.get(G_input, "number")("Prev Vol Cap Mult", 1.5, J.obj(("min", 0.5), ("step", 0.1)))
    allowCapitulation = J.get(G_input, "boolean")("Allow Capitulation (<10K)", False)
    cooldownBars = J.get(G_input, "number")("Cooldown (bars)", 3, J.obj(("min", 0), ("step", 1)))
    labelColor = J.get(G_input, "color")("BC Label Color", "white")
    labelBgColor = J.get(G_input, "color")("BC Background Color", "#6200FF")
    labelOffset = J.get(G_input, "number")("BC Label Offset (px)", 40, J.obj(("min", 0), ("step", 1)))
    moment = G_library("moment-timezone")
    showTable = J.get(G_input, "boolean")("Show BC Tracker Table", True)
    useBarCloseDate = J.get(G_input, "boolean")("Table Date = Bar Close", True)
    scaleChoice = G_input("UI Scale", "100%", J.JSArray(["60%", "75%", "100%", "125%", "150%"]))
    uiScale = G_parseInt(scaleChoice, 10)
    volSma50 = G_sma(G_volume, volMaLength)
    atrArr = G_atr(atrLen)
    loArr = G_lowest(G_low, stochLen)
    hiArr = G_highest(G_high, stochLen)
    def _f1(c=J.undefined, i=J.undefined, *_args):
        return (J.div(J.mul(100, J.sub(c, J.get(loArr, i))), J.sub(J.get(hiArr, i), J.get(loArr, i))) if J.sne(J.sub(J.get(hiArr, i), J.get(loArr, i)), 0) else 0)
    kRaw = J.get(G_close, "map")(_f1)
    kSmooth = G_sma(kRaw, stochKSmooth)
    def _f2(v=J.undefined, i=J.undefined, *_args):
        return (J.div(v, J.get(volSma50, i)) if J.gt(J.get(volSma50, i), 0) else 0)
    rvol = J.get(G_volume, "map")(_f2)
    def _f3(c=J.undefined, i=J.undefined, *_args):
        return J.get(G_Math, "abs")(J.sub(c, J.get(G_open, i)))
    bodyAbs = J.get(G_close, "map")(_f3)
    def _f4(c=J.undefined, i=J.undefined, *_args):
        return J.ge(J.get(bodyAbs, i), J.mul(bodyAtrMultiplier, J.get(atrArr, i)))
    bodyIsBig = J.get(G_close, "map")(_f4)
    def _f5(k=J.undefined, i=J.undefined, *_args):
        return (_t1 if J.truthy(_t1 := (J.lt(k, bcBandUpper1) if J.truthy(_t2 := J.ge(k, bcBandLower1)) else _t2)) else (J.lt(k, bcBandUpper2) if J.truthy(_t3 := J.ge(k, bcBandLower2)) else _t3))
    inBand = J.get(kSmooth, "map")(_f5)
    def _f6(k=J.undefined, i=J.undefined, *_args):
        return (J.gt(k, J.get(kSmooth, J.sub(i, 1))) if J.gt(i, 0) else False)
    kRising = J.get(kSmooth, "map")(_f6)
    def _f7(*_args):
        return False
    isBC = J.get(G_close, "map")(_f7)
    lastSig = (-1)
    i = 1
    while J.lt(i, J.get(G_close, "length")):
        bullishCandle = J.gt(J.get(G_close, i), J.get(G_open, i))
        controlledVol = J.le(J.get(G_volume, i), J.mul(prevVolCapMult, J.get(G_volume, J.sub(i, 1))))
        rvolPass = J.ge(J.get(rvol, i), rvolThreshold)
        capitulationOK = (J.gt(J.get(G_volume, i), J.get(G_volume, J.sub(i, 1))) if J.truthy(_t8 := (J.lt(J.get(kSmooth, i), 10) if J.truthy(_t9 := allowCapitulation) else _t9)) else _t8)
        volumePass = (_t10 if J.truthy(_t10 := (controlledVol if J.truthy(_t11 := rvolPass) else _t11)) else capitulationOK)
        momentumOK = (J.get(kRising, i) if J.truthy(_t12 := J.get(inBand, i)) else _t12)
        progressOK = J.gt(J.get(G_close, i), J.get(G_close, J.sub(i, 1)))
        cooled = (_t13 if J.truthy(_t13 := J.seq(lastSig, (-1))) else J.gt(J.sub(i, lastSig), cooldownBars))
        cond = (cooled if J.truthy(_t14 := (progressOK if J.truthy(_t15 := (momentumOK if J.truthy(_t16 := (volumePass if J.truthy(_t17 := (J.get(bodyIsBig, i) if J.truthy(_t18 := bullishCandle) else _t18)) else _t17)) else _t16)) else _t15)) else _t14)
        if J.truthy(cond):
            J.set(isBC, i, True)
            lastSig = i
        i = J.inc(i)
    def _f19(v=J.undefined, i_2=J.undefined, *_args):
        return (J.template("\ud83c\udfafBC ", J.get(J.get(G_close, i_2), "toLocaleString")(J.undefined, J.obj(("minimumFractionDigits", 2), ("maximumFractionDigits", 2)))) if J.truthy(v) else None)
    G_paint(J.get(isBC, "map")(_f19), J.obj(("name", "Bottom Catch (HTF)"), ("style", "labels_below"), ("verticalOffset", labelOffset), ("color", labelColor), ("backgroundColor", labelBgColor), ("backgroundOpacity", 0.9)))
    G_register_signal(isBC, "Bottom Catch Signal (HTF)")
    myLastBCPrice = None
    myLastBCIndex = (-1)
    i_2 = J.sub(J.get(G_close, "length"), 1)
    while J.ge(i_2, 0):
        if J.truthy(J.get(isBC, i_2)):
            myLastBCPrice = J.get(G_close, i_2)
            myLastBCIndex = i_2
            break
        i_2 = J.dec(i_2)
    myCurrentPrice = J.get(G_close, J.sub(J.get(G_close, "length"), 1))
    myChangePercent = (J.mul(J.div(J.sub(myCurrentPrice, myLastBCPrice), myLastBCPrice), 100) if J.truthy(myLastBCPrice) else None)
    myLastBCDate = "N/A"
    if J.ge(myLastBCIndex, 0):
        myLastBCDate = (formatMMDDYYYY(barCloseMs(myLastBCIndex)) if J.truthy(useBarCloseDate) else formatMMDDYYYY(J.get(G_time, myLastBCIndex)))
    def formatCurrency(num=J.undefined, *_args):
        if ((num is None) or (num is J.undefined)):
            return "N/A"
        return J.add("$", J.get(J.get(num, "toFixed")(2), "replace")(J.regex("B(?=(d{3})+(?!d))", "g"), ","))
    def formatNumber(num=J.undefined, *_args):
        return ("N/A" if ((num is None) or (num is J.undefined)) else J.get(G_String(num), "replace")(J.regex("B(?=(d{3})+(?!d))", "g"), ","))
    dateModeStatus = ("(Close)" if J.truthy(useBarCloseDate) else "(Open)")
    headerBg = labelBgColor
    rowBg = "rgba(42, 53, 59, 0.9)"
    rows = J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", J.template("\ud83c\udfaf BC Valid ", dateModeStatus)), ("fontWeight", "bold"), ("color", "white"), ("background", headerBg), ("padding", pad(8, 12)), ("fontSize", scaleVal(13)), ("align", "center"), ("colspan", 2))]))), J.obj(("cells", J.JSArray([J.obj(("text", "Date"), ("fontWeight", "bold"), ("color", "white"), ("background", rowBg), ("padding", pad(6, 10))), J.obj(("text", myLastBCDate), ("color", "white"), ("background", rowBg), ("padding", pad(6, 10)), ("fontWeight", "bold"))]))), J.obj(("cells", J.JSArray([J.obj(("text", "BC Price"), ("fontWeight", "bold"), ("color", "white"), ("background", rowBg), ("padding", pad(6, 10))), J.obj(("text", formatCurrency(myLastBCPrice)), ("color", "white"), ("background", rowBg), ("padding", pad(6, 10)), ("fontWeight", "bold"))]))), J.obj(("cells", J.JSArray([J.obj(("text", "Current"), ("fontWeight", "bold"), ("color", "white"), ("background", rowBg), ("padding", pad(6, 10))), J.obj(("text", formatCurrency(myCurrentPrice)), ("color", "white"), ("background", rowBg), ("padding", pad(6, 10)), ("fontWeight", "bold"))]))), J.obj(("cells", J.JSArray([J.obj(("text", "P&L %"), ("fontWeight", "bold"), ("color", "white"), ("background", rowBg), ("padding", pad(6, 10))), J.obj(("text", (J.add(formatNumber(J.get(myChangePercent, "toFixed")(2)), "%") if (myChangePercent is not None) else "N/A")), ("color", "white"), ("background", (("rgba(0, 150, 0, 0.8)" if J.gt(myChangePercent, 0) else ("rgba(220, 20, 20, 0.8)" if J.lt(myChangePercent, 0) else "rgba(128, 128, 128, 0.7)")) if (myChangePercent is not None) else "rgba(128, 128, 128, 0.7)")), ("padding", pad(6, 10)), ("fontWeight", "bold"), ("fontSize", scaleVal(12)))])))])
    G_paint_overlay("BC Tracker", J.obj(("position", "bottom_right"), ("order", "above_all"), ("offset_x", (-25)), ("offset_y", 0)), (J.obj(("fontSize", scaleVal(12)), ("border", J.add("2px solid ", labelBgColor)), ("background", "rgba(0, 0, 0, 0.7)"), ("borderRadius", px(6)), ("rows", rows)) if J.truthy(showTable) else J.obj(("fontSize", 1), ("border", "none"), ("background", "transparent"), ("rows", J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", ""), ("padding", "0px"), ("background", "transparent"))])))])))))


register_store_indicator(
    script,
    name='bottom_catcher_signal_htf_TS',
    title='Bottom Catcher Signal (HTF)',
    developer='Rock Regan',
    url='https://trendspider.com/trading-tools-store/indicators/68abb6-bottom-catcher-signal-htf/',
    position='price',
    inputs=[{'id': 'volume_ma_length', 'title': 'Volume MA Length', 'type': 'number', 'default': 50}, {'id': 'stochastic_length', 'title': 'Stochastic Length', 'type': 'number', 'default': 14}, {'id': '_k_smoothing', 'title': '%K Smoothing', 'type': 'number', 'default': 3}, {'id': 'band1_lower', 'title': 'Band1 Lower', 'type': 'number', 'default': 10}, {'id': 'band1_upper', 'title': 'Band1 Upper', 'type': 'number', 'default': 20}, {'id': 'band2_lower', 'title': 'Band2 Lower', 'type': 'number', 'default': 50}, {'id': 'band2_upper', 'title': 'Band2 Upper', 'type': 'number', 'default': 60}, {'id': 'atr_length', 'title': 'ATR Length', 'type': 'number', 'default': 14}, {'id': 'body___atr_x', 'title': 'Body ≥ ATR x', 'type': 'number', 'default': 0.6}, {'id': 'rvol_threshold', 'title': 'RVOL Threshold', 'type': 'number', 'default': 1.3}, {'id': 'prev_vol_cap_mult', 'title': 'Prev Vol Cap Mult', 'type': 'number', 'default': 1.5}, {'id': 'allow_capitulation___10k_', 'title': 'Allow Capitulation (<10K)', 'type': 'boolean', 'default': False}, {'id': 'cooldown__bars_', 'title': 'Cooldown (bars)', 'type': 'number', 'default': 3}, {'id': 'bc_label_color', 'title': 'BC Label Color', 'type': 'color', 'default': 'white'}, {'id': 'bc_background_color', 'title': 'BC Background Color', 'type': 'color', 'default': '#6200FF'}, {'id': 'bc_label_offset__px_', 'title': 'BC Label Offset (px)', 'type': 'number', 'default': 40}, {'id': 'show_bc_tracker_table', 'title': 'Show BC Tracker Table', 'type': 'boolean', 'default': True}, {'id': 'table_date___bar_close', 'title': 'Table Date = Bar Close', 'type': 'boolean', 'default': True}, {'id': 'ui_scale', 'title': 'UI Scale', 'type': 'select_wide', 'default': '100%', 'options': ['60%', '75%', '100%', '125%', '150%']}],
    outputs=['bottom_catch__htf_', 'bottom_catch_signal__htf_'],
    signals=['bottom_catch_signal__htf_'],
    requires=[],
    parity='exact',
)
