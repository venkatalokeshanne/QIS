"""
LinkLine -- TrendSpider store indicator by James Chellis.

Registered as "linkline_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68a004-linkline/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_ema = G["ema"]
    G_high = G["high"]
    G_input = G["input"]
    G_low = G["low"]
    G_open = G["open"]
    G_paint = G["paint"]
    G_series_of = G["series_of"]
    def sign(x=J.undefined, *_args):
        return (1 if J.gt(x, 0) else ((-1) if J.lt(x, 0) else 0))
    def tanh(x=J.undefined, *_args):
        e2x = J.get(G_Math, "exp")(J.mul(2, J.get(G_Math, "abs")(x)))
        t = J.div(J.sub(e2x, 1), J.add(e2x, 1))
        return (t if J.ge(x, 0) else J.neg(t))
    G_describe_indicator("LinkLine", "overlay", J.obj(("shortName", "LinkLine")))
    haLen = J.get(G_input, "number")("HA Smoothing", 50, J.obj(("min", 10), ("max", 200)))
    haLen2 = J.get(G_input, "number")("HA Secondary", 20, J.obj(("min", 5), ("max", 100)))
    oscLen = J.get(G_input, "number")("Strength Lookback", 14, J.obj(("min", 5), ("max", 100)))
    sigmaLevel = J.get(G_input, "number")("Strong @ σ", 1, J.obj(("min", 0.3), ("max", 3), ("step", 0.1)))
    bpsMult = J.get(G_input, "number")("Bias Units (bps)", 10000, J.obj(("min", 1000), ("max", 20000), ("step", 1000)))
    baseWidth = J.get(G_input, "number")("Base Width", 1, J.obj(("min", 1), ("max", 5)))
    strongWidth = J.get(G_input, "number")("Strong Width", 3, J.obj(("min", 1), ("max", 8)))
    midWidth = J.get(G_input, "number")("Mid Width", 1, J.obj(("min", 0), ("max", 3)))
    bullColor = J.get(G_input, "color")("Bull Color", "#23D18B")
    bearColor = J.get(G_input, "color")("Bear Color", "#FF5A5F")
    neutralColor = J.get(G_input, "color")("Neutral", "#A0A4B8")
    midColor = J.get(G_input, "color")("Midline", "#BAC2DE")
    sO = G_ema(G_open, haLen)
    sH = G_ema(G_high, haLen)
    sL = G_ema(G_low, haLen)
    sC = G_ema(G_close, haLen)
    haClose = G_series_of(0)
    xOpen = G_series_of(0)
    i_2 = 0
    while J.lt(i_2, J.get(G_close, "length")):
        J.set(haClose, i_2, J.div(J.add(J.add(J.add(J.get(sO, i_2), J.get(sH, i_2)), J.get(sL, i_2)), J.get(sC, i_2)), 4))
        J.set(xOpen, i_2, J.div(J.add(J.get(sO, i_2), J.get(sC, i_2)), 2))
        i_2 = J.inc(i_2)
    haOpen = G_series_of(0)
    i_3 = 0
    while J.lt(i_3, J.get(G_close, "length")):
        J.set(haOpen, i_3, (J.get(xOpen, i_3) if J.seq(i_3, 0) else J.div(J.add(J.get(haOpen, J.sub(i_3, 1)), J.get(haClose, J.sub(i_3, 1))), 2)))
        i_3 = J.inc(i_3)
    haHigh = G_series_of(0)
    haLow = G_series_of(0)
    i_4 = 0
    while J.lt(i_4, J.get(G_close, "length")):
        J.set(haHigh, i_4, J.get(G_Math, "max")(J.get(sH, i_4), J.get(G_Math, "max")(J.get(haOpen, i_4), J.get(haClose, i_4))))
        J.set(haLow, i_4, J.get(G_Math, "min")(J.get(sL, i_4), J.get(G_Math, "min")(J.get(haOpen, i_4), J.get(haClose, i_4))))
        i_4 = J.inc(i_4)
    haOpen2 = G_ema(haOpen, haLen2)
    haClose2 = G_ema(haClose, haLen2)
    haHigh2 = G_ema(haHigh, haLen2)
    haLow2 = G_ema(haLow, haLen2)
    midLine = G_series_of(0)
    i_5 = 0
    while J.lt(i_5, J.get(G_close, "length")):
        J.set(midLine, i_5, J.div(J.add(J.get(haHigh2, i_5), J.get(haLow2, i_5)), 2))
        i_5 = J.inc(i_5)
    biasOsc = G_series_of(0)
    i_6 = 0
    while J.lt(i_6, J.get(G_close, "length")):
        base = J.get(haOpen2, i_6)
        J.set(biasOsc, i_6, (J.mul(J.div(J.sub(J.get(haClose2, i_6), base), base), bpsMult) if J.sne(base, 0) else 0))
        i_6 = J.inc(i_6)
    mean = G_ema(biasOsc, oscLen)
    varRaw = G_series_of(0)
    i_7 = 0
    while J.lt(i_7, J.get(G_close, "length")):
        d = J.sub(J.get(biasOsc, i_7), J.get(mean, i_7))
        J.set(varRaw, i_7, J.mul(d, d))
        i_7 = J.inc(i_7)
    varEma = G_ema(varRaw, oscLen)
    std = G_series_of(0)
    i_8 = 0
    while J.lt(i_8, J.get(G_close, "length")):
        J.set(std, i_8, J.get(G_Math, "sqrt")(J.get(G_Math, "max")(J.get(varEma, i_8), 1.0e-12)))
        i_8 = J.inc(i_8)
    zScore = G_series_of(0)
    i_9 = 0
    while J.lt(i_9, J.get(G_close, "length")):
        J.set(zScore, i_9, (J.div(J.get(biasOsc, i_9), J.get(std, i_9)) if J.gt(J.get(std, i_9), 0) else 0))
        i_9 = J.inc(i_9)
    strength = G_series_of(0)
    dir = G_series_of(0)
    i_10 = 0
    while J.lt(i_10, J.get(G_close, "length")):
        J.set(dir, i_10, sign(J.get(biasOsc, i_10)))
        J.set(strength, i_10, J.get(G_Math, "round")(J.mul(100, J.get(G_Math, "abs")(tanh(J.get(zScore, i_10))))))
        i_10 = J.inc(i_10)
    upColors = G_series_of(bullColor)
    downColors = G_series_of(bearColor)
    useColorsU = G_series_of(neutralColor)
    useColorsL = G_series_of(neutralColor)
    widthsU = G_series_of(baseWidth)
    widthsL = G_series_of(baseWidth)
    widthsM = G_series_of(midWidth)
    i_11 = 0
    while J.lt(i_11, J.get(G_close, "length")):
        strong = J.ge(J.get(G_Math, "abs")(J.get(zScore, i_11)), sigmaLevel)
        d_2 = J.get(dir, i_11)
        col = (bullColor if J.gt(d_2, 0) else (bearColor if J.lt(d_2, 0) else neutralColor))
        J.set(useColorsU, i_11, col)
        J.set(useColorsL, i_11, col)
        J.set(widthsU, i_11, (strongWidth if J.truthy(strong) else baseWidth))
        J.set(widthsL, i_11, (strongWidth if J.truthy(strong) else baseWidth))
        J.set(widthsM, i_11, (J.get(G_Math, "max")(midWidth, baseWidth) if J.truthy(strong) else midWidth))
        i_11 = J.inc(i_11)
    G_paint(haHigh2, J.obj(("name", "LinkLine Upper"), ("color", useColorsU), ("style", "line"), ("width", widthsU), ("opacity", 0.95)))
    G_paint(haLow2, J.obj(("name", "LinkLine Lower"), ("color", useColorsL), ("style", "line"), ("width", widthsL), ("opacity", 0.95)))
    G_paint(midLine, J.obj(("name", "LinkLine Mid"), ("color", midColor), ("style", "line"), ("width", widthsM), ("opacity", 0.65)))
    i = J.sub(J.get(G_close, "length"), 1)
    return J.obj(("dir", J.get(dir, i)), ("z", J.get(zScore, i)), ("strength", J.get(strength, i)), ("strong", J.ge(J.get(G_Math, "abs")(J.get(zScore, i)), sigmaLevel)), ("upper", J.get(haHigh2, i)), ("lower", J.get(haLow2, i)), ("mid", J.get(midLine, i)))


register_store_indicator(
    script,
    name='linkline_TS',
    title='LinkLine',
    developer='James Chellis',
    url='https://trendspider.com/trading-tools-store/indicators/68a004-linkline/',
    position='price',
    inputs=[{'id': 'ha_smoothing', 'title': 'HA Smoothing', 'type': 'number', 'default': 50}, {'id': 'ha_secondary', 'title': 'HA Secondary', 'type': 'number', 'default': 20}, {'id': 'strength_lookback', 'title': 'Strength Lookback', 'type': 'number', 'default': 14}, {'id': 'strong____', 'title': 'Strong @ σ', 'type': 'number', 'default': 1}, {'id': 'bias_units__bps_', 'title': 'Bias Units (bps)', 'type': 'number', 'default': 10000}, {'id': 'base_width', 'title': 'Base Width', 'type': 'number', 'default': 1}, {'id': 'strong_width', 'title': 'Strong Width', 'type': 'number', 'default': 3}, {'id': 'mid_width', 'title': 'Mid Width', 'type': 'number', 'default': 1}, {'id': 'bull_color', 'title': 'Bull Color', 'type': 'color', 'default': '#23D18B'}, {'id': 'bear_color', 'title': 'Bear Color', 'type': 'color', 'default': '#FF5A5F'}, {'id': 'neutral', 'title': 'Neutral', 'type': 'color', 'default': '#A0A4B8'}, {'id': 'midline', 'title': 'Midline', 'type': 'color', 'default': '#BAC2DE'}],
    outputs=['linkline_upper', 'linkline_lower', 'linkline_mid'],
    signals=[],
    requires=[],
    parity='exact',
)
