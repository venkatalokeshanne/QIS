"""
Bottom Catcher Performance -- TrendSpider store indicator by Rock Regan.

Registered as "bottom_catcher_performance_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/69b5fd-bottom-catcher-performance/)
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
    G_describe_indicator = G["describe_indicator"]
    G_high = G["high"]
    G_highest = G["highest"]
    G_input = G["input"]
    G_low = G["low"]
    G_lowest = G["lowest"]
    G_open = G["open"]
    G_paint = G["paint"]
    G_paint_label_at_line = G["paint_label_at_line"]
    G_register_signal = G["register_signal"]
    G_sma = G["sma"]
    G_volume = G["volume"]
    G_describe_indicator("Bottom Catcher Performance ", "lower", J.obj(("shortName", "\ud83c\udfafBC Performance 1.1")))
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
    lineWidth = J.get(G_input, "number")("Line Width", 2, J.obj(("min", 1), ("max", 5), ("step", 1)))
    signalThreshold = J.get(G_input, "number")("Signal Threshold %", 2, J.obj(("min", 0), ("step", 0.1)))
    signalRecencyBars = J.get(G_input, "number")("Signal Recency (bars)", 20, J.obj(("min", 1), ("step", 1)))
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
    G_register_signal(isBC, "BC Signal")
    def _f19(*_args):
        return None
    changePercent = J.get(G_close, "map")(_f19)
    def _f20(*_args):
        return False
    thresholdCrossed = J.get(G_close, "map")(_f20)
    lastBCIdx = (-1)
    lastBCPrice = None
    cycleThresholdHit = False
    i_2 = 0
    while J.lt(i_2, J.get(G_close, "length")):
        if J.truthy(J.get(isBC, i_2)):
            lastBCIdx = i_2
            lastBCPrice = J.get(G_close, i_2)
            cycleThresholdHit = False
        if (lastBCPrice is not None):
            J.set(changePercent, i_2, J.mul(J.div(J.sub(J.get(G_close, i_2), lastBCPrice), lastBCPrice), 100))
            if ((not J.truthy(cycleThresholdHit)) and J.ge(J.get(G_Math, "abs")(J.get(changePercent, i_2)), signalThreshold)):
                J.set(thresholdCrossed, i_2, True)
                cycleThresholdHit = True
        i_2 = J.inc(i_2)
    def _f21(value=J.undefined, *_args):
        if (value is None):
            return "#666666"
        return ("#32CD32" if J.ge(value, 0) else "#FF0000")
    changeColor = J.get(changePercent, "map")(_f21)
    myPaintedLine = G_paint(changePercent, J.obj(("name", "%"), ("style", "line"), ("color", changeColor), ("lineWidth", lineWidth)))
    lastIndex = J.sub(J.get(changePercent, "length"), 1)
    lastValue = J.get(changePercent, lastIndex)
    if (lastValue is not None):
        labelText = J.add(J.add(("+" if J.ge(lastValue, 0) else ""), J.get(lastValue, "toFixed")(2)), "%")
        labelColor = ("#008000" if J.ge(lastValue, 0) else "#FF0000")
        G_paint_label_at_line(myPaintedLine, lastIndex, labelText, J.obj(("color", "white"), ("background_color", labelColor), ("border_radius", 3), ("halo", False), ("vertical_align", "middle")))
    def _f22(crossed=J.undefined, i_3=J.undefined, *_args):
        if (not J.truthy(crossed)):
            return False
        barsSinceBC = J.sub(i_3, lastBCIdx)
        return True
    thresholdSignal = J.get(thresholdCrossed, "map")(_f22)
    def _f23(*_args):
        return False
    finalThresholdSignal = J.get(G_close, "map")(_f23)
    trackBCIdx = (-1)
    i_3 = 0
    while J.lt(i_3, J.get(G_close, "length")):
        if J.truthy(J.get(isBC, i_3)):
            trackBCIdx = i_3
        if J.truthy(J.get(thresholdCrossed, i_3)):
            barsSinceBC = J.sub(i_3, trackBCIdx)
            if J.le(barsSinceBC, signalRecencyBars):
                J.set(finalThresholdSignal, i_3, True)
        i_3 = J.inc(i_3)
    G_register_signal(finalThresholdSignal, "BC Threshold Cross Signal")


register_store_indicator(
    script,
    name='bottom_catcher_performance_TS',
    title='Bottom Catcher Performance',
    developer='Rock Regan',
    url='https://trendspider.com/trading-tools-store/indicators/69b5fd-bottom-catcher-performance/',
    position='lower',
    inputs=[{'id': 'volume_ma_length', 'title': 'Volume MA Length', 'type': 'number', 'default': 50}, {'id': 'stochastic_length', 'title': 'Stochastic Length', 'type': 'number', 'default': 14}, {'id': '_k_smoothing', 'title': '%K Smoothing', 'type': 'number', 'default': 3}, {'id': 'band1_lower', 'title': 'Band1 Lower', 'type': 'number', 'default': 10}, {'id': 'band1_upper', 'title': 'Band1 Upper', 'type': 'number', 'default': 20}, {'id': 'band2_lower', 'title': 'Band2 Lower', 'type': 'number', 'default': 50}, {'id': 'band2_upper', 'title': 'Band2 Upper', 'type': 'number', 'default': 60}, {'id': 'atr_length', 'title': 'ATR Length', 'type': 'number', 'default': 14}, {'id': 'body___atr_x', 'title': 'Body ≥ ATR x', 'type': 'number', 'default': 0.6}, {'id': 'rvol_threshold', 'title': 'RVOL Threshold', 'type': 'number', 'default': 1.3}, {'id': 'prev_vol_cap_mult', 'title': 'Prev Vol Cap Mult', 'type': 'number', 'default': 1.5}, {'id': 'allow_capitulation___10k_', 'title': 'Allow Capitulation (<10K)', 'type': 'boolean', 'default': False}, {'id': 'cooldown__bars_', 'title': 'Cooldown (bars)', 'type': 'number', 'default': 3}, {'id': 'line_width', 'title': 'Line Width', 'type': 'number', 'default': 2}, {'id': 'signal_threshold__', 'title': 'Signal Threshold %', 'type': 'number', 'default': 2}, {'id': 'signal_recency__bars_', 'title': 'Signal Recency (bars)', 'type': 'number', 'default': 20}],
    outputs=['bc_signal', '_', 'bc_threshold_cross_signal'],
    signals=['bc_signal', 'bc_threshold_cross_signal'],
    requires=[],
    parity='exact',
)
