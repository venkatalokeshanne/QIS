"""
AERIS -- TrendSpider store indicator by Grant Pratt.

Registered as "aeris_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68ab35-aeris/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_add = G["add"]
    G_atr = G["atr"]
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_div = G["div"]
    G_ema = G["ema"]
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_input = G["input"]
    G_low = G["low"]
    G_mult = G["mult"]
    G_open = G["open"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_series_of = G["series_of"]
    G_sma = G["sma"]
    G_stdev = G["stdev"]
    G_sub = G["sub"]
    def zscore(s=J.undefined, n=J.undefined, *_args):
        m = G_sma(s, n)
        sd = G_stdev(s, n)
        return G_div(G_sub(s, m), G_add(sd, G_series_of(1.0e-9)))
    def clamp3(s=J.undefined, *_args):
        def _f1(x=J.undefined, *_args):
            return (None if (J.nullish(x)) else (3 if J.gt(x, 3) else ((-3) if J.lt(x, (-3)) else x)))
        return G_for_every(s, _f1)
    def to100(sZ=J.undefined, *_args):
        cz = clamp3(sZ)
        return G_add(G_mult(G_div(cz, G_series_of(3)), G_series_of(50)), G_series_of(50))
    def absS(s=J.undefined, *_args):
        def _f1(x=J.undefined, *_args):
            return (None if (J.nullish(x)) else J.get(G_Math, "abs")(x))
        return G_for_every(s, _f1)
    def sqrtS(s=J.undefined, *_args):
        def _f1(x=J.undefined, *_args):
            return (None if (J.nullish(x)) else J.get(G_Math, "sqrt")(x))
        return G_for_every(s, _f1)
    def guide(val=J.undefined, name=J.undefined, *_args):
        G_paint(G_series_of(val), J.obj(("name", name), ("color", cG), ("style", "dotted")))
    G_describe_indicator("AERIS", "lower", J.obj(("warmup", 300)))
    fastLen = J.get(G_input, "number")("EMA fast", 21, J.obj(("min", 1), ("max", 500)))
    slowLen = J.get(G_input, "number")("EMA slow", 89, J.obj(("min", 1), ("max", 500)))
    atrLen = J.get(G_input, "number")("ATR len", 14, J.obj(("min", 1), ("max", 500)))
    zLen = J.get(G_input, "number")("Z len", 100, J.obj(("min", 20), ("max", 1000)))
    thLong = J.get(G_input, "number")("Go long", 65, J.obj(("min", 0), ("max", 100)))
    thShort = J.get(G_input, "number")("Go short", 35, J.obj(("min", 0), ("max", 100)))
    scoreAsLine = J.get(G_input, "boolean")("Score as line", True)
    showParts = J.get(G_input, "boolean")("Show parts", False)
    lineWidth = J.get(G_input, "number")("Line width", 2, J.obj(("min", 1), ("max", 5)))
    cUp = J.get(G_input, "color")("Up col", "#00c853")
    cDn = J.get(G_input, "color")("Dn col", "#d32f2f")
    cMid = J.get(G_input, "color")("Mid col", "#9e9e9e")
    cA = J.get(G_input, "color")("A col", "#42a5f5")
    cE = J.get(G_input, "color")("E col", "#ffa000")
    cT = J.get(G_input, "color")("T col", "#ab47bc")
    cN = J.get(G_input, "color")("N col", "#26a69a")
    cG = J.get(G_input, "color")("Guide", "#616161")
    rng = G_sub(G_high, G_low)
    body = G_sub(G_close, G_open)
    atrV = G_atr(atrLen)
    def _f1(o=J.undefined, c=J.undefined, *_args):
        return (o if J.gt(o, c) else c)
    upRef = G_for_every(G_open, G_close, _f1)
    def _f2(o=J.undefined, c=J.undefined, *_args):
        return (o if J.lt(o, c) else c)
    dnRef = G_for_every(G_open, G_close, _f2)
    upW = G_sub(G_high, upRef)
    dnW = G_sub(dnRef, G_low)
    wickBias = G_div(G_sub(dnW, upW), G_add(rng, G_series_of(1.0e-9)))
    bodyBias = G_div(body, G_add(rng, G_series_of(1.0e-9)))
    asymRaw = G_add(G_mult(G_series_of(0.6), wickBias), G_mult(G_series_of(0.4), bodyBias))
    asymZ = zscore(asymRaw, zLen)
    effBar = G_div(absS(body), G_add(rng, G_series_of(1.0e-9)))
    effZ = zscore(effBar, zLen)
    emaF = G_ema(G_close, fastLen)
    emaS = G_ema(G_close, slowLen)
    tiltR = G_div(G_sub(emaF, emaS), G_add(atrV, G_series_of(1.0e-9)))
    tiltZ = zscore(tiltR, zLen)
    bodyRMS = sqrtS(G_ema(G_mult(body, body), 10))
    energyR = G_div(bodyRMS, G_add(atrV, G_series_of(1.0e-9)))
    def _f3(b=J.undefined, *_args):
        return (None if (J.nullish(b)) else (1 if J.ge(b, 0) else (-1)))
    signedE = G_mult(energyR, G_for_every(body, _f3))
    energyZ = zscore(signedE, zLen)
    wA = G_series_of(0.2)
    wE = G_series_of(0.25)
    wT = G_series_of(0.35)
    wN = G_series_of(0.2)
    compZ = G_add(G_add(G_mult(asymZ, wA), G_mult(effZ, wE)), G_add(G_mult(tiltZ, wT), G_mult(energyZ, wN)))
    score = to100(compZ)
    guide(35, "Guide: 35")
    guide(50, "Guide: 50")
    guide(65, "Guide: 65")
    if J.truthy(scoreAsLine):
        def _f4(s=J.undefined, *_args):
            return (None if (J.nullish(s)) else (cUp if J.ge(s, 65) else (cDn if J.le(s, 35) else cMid)))
        colLine = G_for_every(score, _f4)
        G_paint(score, J.obj(("name", "AERIS score (line)"), ("style", "line"), ("thickness", lineWidth), ("color", colLine)))
    else:
        def _f5(s=J.undefined, *_args):
            return (None if (J.nullish(s)) else (cUp if J.ge(s, 65) else (cDn if J.le(s, 35) else cMid)))
        colHist = G_for_every(score, _f5)
        G_paint(score, J.obj(("name", "AERIS score (hist)"), ("style", "column"), ("color", colHist)))
    if J.truthy(showParts):
        G_paint(to100(asymZ), J.obj(("name", "Asym 0..100"), ("style", "line"), ("color", cA), ("thickness", 2)))
        G_paint(to100(effZ), J.obj(("name", "Eff  0..100"), ("style", "line"), ("color", cE), ("thickness", 2)))
        G_paint(to100(tiltZ), J.obj(("name", "Tilt 0..100"), ("style", "line"), ("color", cT), ("thickness", 2)))
        G_paint(to100(energyZ), J.obj(("name", "Ener 0..100"), ("style", "line"), ("color", cN), ("thickness", 2)))
    def _f6(s=J.undefined, *_args):
        return (1 if ((not J.nullish(s)) and J.lt(s, thLong)) else 0)
    wasBelowLong = G_ema(G_for_every(score, _f6), 2)
    def _f7(s=J.undefined, *_args):
        return (1 if ((not J.nullish(s)) and J.gt(s, thShort)) else 0)
    wasAboveShort = G_ema(G_for_every(score, _f7), 2)
    def _f8(s=J.undefined, w=J.undefined, *_args):
        return ((J.ge(s, thLong) if J.truthy(_t3 := (not J.nullish(s))) else _t3) if J.truthy(_t1 := (J.gt(w, 0.5) if J.truthy(_t2 := (not J.nullish(w))) else _t2)) else _t1)
    G_register_signal(G_for_every(score, wasBelowLong, _f8), "AERIS LONG")
    def _f9(s=J.undefined, w=J.undefined, *_args):
        return ((J.le(s, thShort) if J.truthy(_t3 := (not J.nullish(s))) else _t3) if J.truthy(_t1 := (J.gt(w, 0.5) if J.truthy(_t2 := (not J.nullish(w))) else _t2)) else _t1)
    G_register_signal(G_for_every(score, wasAboveShort, _f9), "AERIS SHORT")
    def _f10(t=J.undefined, *_args):
        return (J.ge(t, 60) if J.truthy(_t1 := (not J.nullish(t))) else _t1)
    G_register_signal(G_for_every(to100(tiltZ), _f10), "AERIS TILT STRONG")
    def _f11(e=J.undefined, *_args):
        return (J.ge(e, 60) if J.truthy(_t1 := (not J.nullish(e))) else _t1)
    G_register_signal(G_for_every(to100(effZ), _f11), "AERIS EFF STRAIGHT")
    def _f12(a=J.undefined, *_args):
        return (J.ge(a, 60) if J.truthy(_t1 := (not J.nullish(a))) else _t1)
    G_register_signal(G_for_every(to100(asymZ), _f12), "AERIS ASYM BUY")
    def _f13(n=J.undefined, *_args):
        return (J.ge(n, 60) if J.truthy(_t1 := (not J.nullish(n))) else _t1)
    G_register_signal(G_for_every(to100(energyZ), _f13), "AERIS ENERGY BUY")
    def _f14(t=J.undefined, *_args):
        return (J.le(t, 40) if J.truthy(_t1 := (not J.nullish(t))) else _t1)
    G_register_signal(G_for_every(to100(tiltZ), _f14), "AERIS TILT WEAK")
    def _f15(e=J.undefined, *_args):
        return (J.le(e, 40) if J.truthy(_t1 := (not J.nullish(e))) else _t1)
    G_register_signal(G_for_every(to100(effZ), _f15), "AERIS EFF CHOP")
    def _f16(a=J.undefined, *_args):
        return (J.le(a, 40) if J.truthy(_t1 := (not J.nullish(a))) else _t1)
    G_register_signal(G_for_every(to100(asymZ), _f16), "AERIS ASYM SELL")
    def _f17(n=J.undefined, *_args):
        return (J.le(n, 40) if J.truthy(_t1 := (not J.nullish(n))) else _t1)
    G_register_signal(G_for_every(to100(energyZ), _f17), "AERIS ENERGY SELL")


register_store_indicator(
    script,
    name='aeris_TS',
    title='AERIS',
    developer='Grant Pratt',
    url='https://trendspider.com/trading-tools-store/indicators/68ab35-aeris/',
    position='lower',
    inputs=[{'id': 'warmup', 'title': 'Warmup', 'type': 'number', 'default': 300}, {'id': 'ema_fast', 'title': 'EMA fast', 'type': 'number', 'default': 21}, {'id': 'ema_slow', 'title': 'EMA slow', 'type': 'number', 'default': 89}, {'id': 'atr_len', 'title': 'ATR len', 'type': 'number', 'default': 14}, {'id': 'z_len', 'title': 'Z len', 'type': 'number', 'default': 100}, {'id': 'go_long', 'title': 'Go long', 'type': 'number', 'default': 65}, {'id': 'go_short', 'title': 'Go short', 'type': 'number', 'default': 35}, {'id': 'score_as_line', 'title': 'Score as line', 'type': 'boolean', 'default': True}, {'id': 'show_parts', 'title': 'Show parts', 'type': 'boolean', 'default': False}, {'id': 'line_width', 'title': 'Line width', 'type': 'number', 'default': 2}, {'id': 'up_col', 'title': 'Up col', 'type': 'color', 'default': '#00c853'}, {'id': 'dn_col', 'title': 'Dn col', 'type': 'color', 'default': '#d32f2f'}, {'id': 'mid_col', 'title': 'Mid col', 'type': 'color', 'default': '#9e9e9e'}, {'id': 'a_col', 'title': 'A col', 'type': 'color', 'default': '#42a5f5'}, {'id': 'e_col', 'title': 'E col', 'type': 'color', 'default': '#ffa000'}, {'id': 't_col', 'title': 'T col', 'type': 'color', 'default': '#ab47bc'}, {'id': 'n_col', 'title': 'N col', 'type': 'color', 'default': '#26a69a'}, {'id': 'guide', 'title': 'Guide', 'type': 'color', 'default': '#616161'}],
    outputs=['guide__35', 'guide__50', 'guide__65', 'aeris_score__line_', 'aeris_long', 'aeris_short', 'aeris_tilt_strong', 'aeris_eff_straight', 'aeris_asym_buy', 'aeris_energy_buy', 'aeris_tilt_weak', 'aeris_eff_chop', 'aeris_asym_sell', 'aeris_energy_sell'],
    signals=['aeris_long', 'aeris_short', 'aeris_tilt_strong', 'aeris_eff_straight', 'aeris_asym_buy', 'aeris_energy_buy', 'aeris_tilt_weak', 'aeris_eff_chop', 'aeris_asym_sell', 'aeris_energy_sell'],
    requires=[],
    parity='exact',
)
