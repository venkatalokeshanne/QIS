"""
Trend Strength Candles -- TrendSpider store indicator by Dr. Goose.

Registered as "trend_strength_candles_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/689cdc-trend-strength-candles-tsbuild25/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Infinity = G["Infinity"]
    G_Math = G["Math"]
    G_close = G["close"]
    G_color_candles = G["color_candles"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_highest = G["highest"]
    G_input = G["input"]
    G_low = G["low"]
    G_lowest = G["lowest"]
    G_parseInt = G["parseInt"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    def clamp01(t=J.undefined, *_args):
        return J.get(G_Math, "max")(0, J.get(G_Math, "min")(1, t))
    def hex_to_rgb(hex=J.undefined, *_args):
        h = J.get(hex, "replace")("#", "")
        r_2 = G_parseInt(J.get(h, "substring")(0, 2), 16)
        g = G_parseInt(J.get(h, "substring")(2, 4), 16)
        b = G_parseInt(J.get(h, "substring")(4, 6), 16)
        return J.obj(("r", r_2), ("g", g), ("b", b))
    def rgb_to_hex(r_2=J.undefined, g=J.undefined, b=J.undefined, *_args):
        def to2(n=J.undefined, *_args):
            s = J.get(J.get(J.get(G_Math, "round")(J.get(G_Math, "max")(0, J.get(G_Math, "min")(255, n))), "toString")(16), "toUpperCase")()
            return (J.add("0", s) if J.seq(J.get(s, "length"), 1) else s)
        return J.add(J.add(J.add("#", to2(r_2)), to2(g)), to2(b))
    def lerp_color(c1=J.undefined, c2=J.undefined, t=J.undefined, *_args):
        a = hex_to_rgb(c1)
        b = hex_to_rgb(c2)
        r_2 = J.add(J.get(a, "r"), J.mul(J.sub(J.get(b, "r"), J.get(a, "r")), t))
        g = J.add(J.get(a, "g"), J.mul(J.sub(J.get(b, "g"), J.get(a, "g")), t))
        bl = J.add(J.get(a, "b"), J.mul(J.sub(J.get(b, "b"), J.get(a, "b")), t))
        return rgb_to_hex(r_2, g, bl)
    def color_from_gradient(v=J.undefined, lo_2=J.undefined, hi_2=J.undefined, cLo=J.undefined, cHi=J.undefined, *_args):
        if (((J.nullish(v)) or (J.nullish(lo_2))) or (J.nullish(hi_2))):
            return None
        t = clamp01(J.div(J.sub(v, lo_2), J.sub(hi_2, lo_2)))
        return lerp_color(cLo, cHi, t)
    G_describe_indicator("Trend Strength Candles #TSBuild25", "price", J.obj(("decimals", 2), ("shortName", "Trend Strength")))
    GRP_METHOD = "① Trend Method"
    GRP_PC = "② Price Change"
    GRP_EMA = "③ EMA Slope"
    GRP_MA = "④ MA Distance"
    GRP_NORM = "⑤ Normalization"
    method = J.get(G_input, "select")("Method", "Price Change", J.JSArray(["Price Change", "EMA Slope", "MA Distance"]), J.obj(("group", GRP_METHOD)))
    pcLookback = J.get(G_input, "number")("Lookback", 20, J.obj(("min", 1), ("step", 1), ("group", GRP_PC)))
    emaLen = J.get(G_input, "number")("EMA Len", 21, J.obj(("min", 2), ("step", 1), ("group", GRP_EMA)))
    emaSlopeSmooth = J.get(G_input, "number")("Slope Smooth", 5, J.obj(("min", 1), ("step", 1), ("group", GRP_EMA)))
    ma1Type = J.get(G_input, "select")("MA1 Type", "EMA", J.JSArray(["EMA", "SMA"]), J.obj(("group", GRP_MA)))
    ma1Len = J.get(G_input, "number")("MA1 Len", 20, J.obj(("min", 1), ("step", 1), ("group", GRP_MA)))
    ma2Type = J.get(G_input, "select")("MA2 Type", "SMA", J.JSArray(["EMA", "SMA"]), J.obj(("group", GRP_MA)))
    ma2Len = J.get(G_input, "number")("MA2 Len", 50, J.obj(("min", 1), ("step", 1), ("group", GRP_MA)))
    atrLen = J.get(G_input, "number")("ATR Len", 14, J.obj(("min", 1), ("step", 1), ("group", GRP_NORM)))
    normLen = J.get(G_input, "number")("Normalize Window", 100, J.obj(("min", 10), ("step", 5), ("group", GRP_NORM)))
    def shift_series(series=J.undefined, k=J.undefined, *_args):
        out = G_series_of(None)
        i = 0
        while J.lt(i, J.get(series, "length")):
            j = J.sub(i, k)
            J.set(out, i, (J.get(series, j) if J.ge(j, 0) else None))
            i = J.add(i, 1)
        return out
    def sma_ts(series=J.undefined, length=J.undefined, *_args):
        out = G_series_of(None)
        acc = 0
        cnt = 0
        i = 0
        while J.lt(i, J.get(series, "length")):
            v = J.get(series, i)
            if (not J.nullish(v)):
                acc = J.add(acc, v)
                cnt = J.add(cnt, 1)
            if J.ge(i, length):
                oldv = J.get(series, J.sub(i, length))
                if (not J.nullish(oldv)):
                    acc = J.sub(acc, oldv)
                    cnt = J.sub(cnt, 1)
            J.set(out, i, (J.div(acc, cnt) if (J.ge(J.add(i, 1), length) and J.gt(cnt, 0)) else None))
            i = J.add(i, 1)
        return out
    def ema_ts(series=J.undefined, length=J.undefined, *_args):
        out = G_series_of(None)
        if J.lt(length, 1):
            return out
        a = J.div(2, J.add(length, 1))
        prev = None
        i = 0
        while J.lt(i, J.get(series, "length")):
            v = J.get(series, i)
            if (J.nullish(v)):
                J.set(out, i, (J.get(out, J.sub(i, 1)) if J.gt(i, 0) else None))
                i = J.add(i, 1)
                continue
            if (J.nullish(prev)):
                prev = v
                J.set(out, i, v)
            else:
                prev = J.add(J.mul(a, v), J.mul(J.sub(1, a), prev))
                J.set(out, i, prev)
            i = J.add(i, 1)
        return out
    def moving_average_ts(series=J.undefined, length=J.undefined, type_=J.undefined, *_args):
        return (ema_ts(series, length) if J.seq(type_, "EMA") else sma_ts(series, length))
    prevClose = shift_series(G_close, 1)
    def _f1(_h=J.undefined, _l=J.undefined, _pc=J.undefined, _prev=J.undefined, i=J.undefined, *_args):
        if J.seq(i, 0):
            return None
        hl = (J.get(G_Math, "abs")(J.sub(J.get(G_high, i), J.get(G_low, i))) if ((not J.nullish(J.get(G_high, i))) and (not J.nullish(J.get(G_low, i)))) else None)
        hc = (J.get(G_Math, "abs")(J.sub(J.get(G_high, i), J.get(prevClose, i))) if ((not J.nullish(J.get(G_high, i))) and (not J.nullish(J.get(prevClose, i)))) else None)
        lc = (J.get(G_Math, "abs")(J.sub(J.get(G_low, i), J.get(prevClose, i))) if ((not J.nullish(J.get(G_low, i))) and (not J.nullish(J.get(prevClose, i)))) else None)
        a = (J.neg(G_Infinity) if (J.nullish(hl)) else hl)
        b = (J.neg(G_Infinity) if (J.nullish(hc)) else hc)
        c = (J.neg(G_Infinity) if (J.nullish(lc)) else lc)
        m = J.get(G_Math, "max")(a, b, c)
        return (None if J.seq(m, J.neg(G_Infinity)) else m)
    trSeries = G_for_every(G_high, G_low, prevClose, _f1)
    atr_ts = ema_ts(trSeries, atrLen)
    pcPrev = shift_series(G_close, pcLookback)
    def _f2(_c=J.undefined, _p=J.undefined, _a=J.undefined, _prev=J.undefined, i=J.undefined, *_args):
        diff = (J.sub(J.get(G_close, i), J.get(pcPrev, i)) if ((not J.nullish(J.get(G_close, i))) and (not J.nullish(J.get(pcPrev, i)))) else None)
        a = J.get(atr_ts, i)
        if (((J.nullish(diff)) or (J.nullish(a))) or J.seq(a, 0)):
            return None
        return J.div(diff, a)
    raw_pc = G_for_every(G_close, pcPrev, atr_ts, _f2)
    emaSeries = ema_ts(G_close, emaLen)
    emaPrev = shift_series(emaSeries, 1)
    def _f3(_e=J.undefined, _ep=J.undefined, _a=J.undefined, _prev=J.undefined, i=J.undefined, *_args):
        chg = (J.sub(J.get(emaSeries, i), J.get(emaPrev, i)) if ((not J.nullish(J.get(emaSeries, i))) and (not J.nullish(J.get(emaPrev, i)))) else None)
        a = J.get(atr_ts, i)
        if (((J.nullish(chg)) or (J.nullish(a))) or J.seq(a, 0)):
            return None
        return J.div(chg, a)
    raw_ema_slope = G_for_every(emaSeries, emaPrev, atr_ts, _f3)
    raw_ema_slope_sm = sma_ts(raw_ema_slope, emaSlopeSmooth)
    ma1 = moving_average_ts(G_close, ma1Len, ma1Type)
    ma2 = moving_average_ts(G_close, ma2Len, ma2Type)
    def _f4(_m1=J.undefined, _m2=J.undefined, _a=J.undefined, _prev=J.undefined, i=J.undefined, *_args):
        m1 = J.get(ma1, i)
        m2 = J.get(ma2, i)
        a = J.get(atr_ts, i)
        if ((((J.nullish(m1)) or (J.nullish(m2))) or (J.nullish(a))) or J.seq(a, 0)):
            return None
        return J.div(J.sub(m1, m2), a)
    raw_ma_dist = G_for_every(ma1, ma2, atr_ts, _f4)
    rawScore = G_series_of(None)
    i = 0
    while J.lt(i, J.get(G_time, "length")):
        if J.seq(method, "Price Change"):
            J.set(rawScore, i, J.get(raw_pc, i))
        elif J.seq(method, "EMA Slope"):
            J.set(rawScore, i, J.get(raw_ema_slope_sm, i))
        else:
            J.set(rawScore, i, J.get(raw_ma_dist, i))
        i = J.add(i, 1)
    hiRaw = G_highest(rawScore, normLen)
    loRaw = G_lowest(rawScore, normLen)
    trendScore = G_series_of(None)
    i_2 = 0
    while J.lt(i_2, J.get(G_time, "length")):
        r = J.get(rawScore, i_2)
        hi = J.get(hiRaw, i_2)
        lo = J.get(loRaw, i_2)
        if (((J.nullish(r)) or (J.nullish(hi))) or (J.nullish(lo))):
            J.set(trendScore, i_2, None)
            i_2 = J.add(i_2, 1)
            continue
        rng = J.sub(hi, lo)
        norm = (J.sub(J.mul(2, J.div(J.sub(r, lo), rng)), 1) if J.gt(rng, 0) else 0)
        J.set(trendScore, i_2, J.mul(norm, 100))
        i_2 = J.add(i_2, 1)
    colorStrongDown = "#FF007A"
    colorMildDown = "#FF7F50"
    colorNeutral = "#C6C5C5"
    colorMildUp = "#39FF14"
    colorStrongUp = "#00FFFF"
    def _f5(_s=J.undefined, _prev=J.undefined, i_3=J.undefined, *_args):
        s = J.get(trendScore, i_3)
        c = None
        if (J.nullish(s)):
            c = None
        elif J.le(s, (-50)):
            c = color_from_gradient(s, (-100), (-50), colorStrongDown, colorMildDown)
        elif J.le(s, 0):
            c = color_from_gradient(s, (-50), 0, colorMildDown, colorNeutral)
        elif J.le(s, 50):
            c = color_from_gradient(s, 0, 50, colorNeutral, colorMildUp)
        else:
            c = color_from_gradient(s, 50, 100, colorMildUp, colorStrongUp)
        if J.seq(i_3, 0):
            return (c if (not J.nullish(c)) else colorNeutral)
        return (c if (not J.nullish(c)) else _prev)
    myColors = G_for_every(trendScore, _f5)
    G_color_candles(myColors)


register_store_indicator(
    script,
    name='trend_strength_candles_TS',
    title='Trend Strength Candles',
    developer='Dr. Goose',
    url='https://trendspider.com/trading-tools-store/indicators/689cdc-trend-strength-candles-tsbuild25/',
    position='price',
    inputs=[{'id': 'method', 'title': 'Method', 'type': 'select_wide', 'default': 'Price Change', 'options': ['Price Change', 'EMA Slope', 'MA Distance']}, {'id': 'lookback', 'title': 'Lookback', 'type': 'number', 'default': 20}, {'id': 'ema_len', 'title': 'EMA Len', 'type': 'number', 'default': 21}, {'id': 'slope_smooth', 'title': 'Slope Smooth', 'type': 'number', 'default': 5}, {'id': 'ma1_type', 'title': 'MA1 Type', 'type': 'select_wide', 'default': 'EMA', 'options': ['EMA', 'SMA']}, {'id': 'ma1_len', 'title': 'MA1 Len', 'type': 'number', 'default': 20}, {'id': 'ma2_type', 'title': 'MA2 Type', 'type': 'select_wide', 'default': 'SMA', 'options': ['EMA', 'SMA']}, {'id': 'ma2_len', 'title': 'MA2 Len', 'type': 'number', 'default': 50}, {'id': 'atr_len', 'title': 'ATR Len', 'type': 'number', 'default': 14}, {'id': 'normalize_window', 'title': 'Normalize Window', 'type': 'number', 'default': 100}],
    outputs=['cdl'],
    signals=[],
    requires=[],
    parity='exact',
)
