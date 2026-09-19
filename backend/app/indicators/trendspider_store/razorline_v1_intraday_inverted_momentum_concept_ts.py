"""
RAZORLINE v1 — Intraday Inverted Momentum (Concept) -- TrendSpider store indicator by James Chellis.

Registered as "razorline_v1_intraday_inverted_momentum_concept_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/689fe5-razorline-v1-intraday-inverted-momentum-concept/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Array = G["Array"]
    G_Infinity = G["Infinity"]
    G_Math = G["Math"]
    G_atr = G["atr"]
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_ema = G["ema"]
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_input = G["input"]
    G_isFinite = G["isFinite"]
    G_low = G["low"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_series_of = G["series_of"]
    G_shift = G["shift"]
    def abs(x=J.undefined, *_args):
        return (J.neg(x) if J.lt(x, 0) else x)
    def sign(x=J.undefined, *_args):
        return (1 if J.gt(x, 0) else ((-1) if J.lt(x, 0) else 0))
    def pctileWin(src=J.undefined, len=J.undefined, p=J.undefined, *_args):
        out = G_series_of(None)
        n = J.get(src, "length")
        i = 0
        while J.lt(i, n):
            f = J.get(G_Math, "max")(0, J.add(J.sub(i, len), 1))
            tmp = J.JSArray([])
            j = f
            while J.le(j, i):
                v = J.get(src, j)
                if ((not J.nullish(v)) and J.truthy(G_isFinite(v))):
                    J.get(tmp, "push")(v)
                j = J.inc(j)
            if (not J.truthy(J.get(tmp, "length"))):
                J.set(out, i, None)
                i = J.inc(i)
                continue
            def _f1(a=J.undefined, b=J.undefined, *_args):
                return J.sub(a, b)
            J.get(tmp, "sort")(_f1)
            idx = J.get(G_Math, "round")(J.mul(J.div(p, 100), J.sub(J.get(tmp, "length"), 1)))
            J.set(out, i, J.get(tmp, J.get(G_Math, "max")(0, J.get(G_Math, "min")(J.sub(J.get(tmp, "length"), 1), idx))))
            i = J.inc(i)
        return out
    def scaleVal(v=J.undefined, cap=J.undefined, span_2=J.undefined, *_args):
        c = J.get(G_Math, "max")(1.0e-9, (_t1 if J.truthy(_t1 := cap) else 0))
        x = J.get(G_Math, "max")(J.neg(c), J.get(G_Math, "min")(c, (_t2 if J.truthy(_t2 := v) else 0)))
        return J.mul(J.div(x, c), span_2)
    def rollMin(a=J.undefined, len=J.undefined, *_args):
        out = G_series_of(None)
        n = J.get(a, "length")
        i = 0
        while J.lt(i, n):
            m = G_Infinity
            f = J.get(G_Math, "max")(0, J.add(J.sub(i, len), 1))
            j = f
            while J.le(j, i):
                if J.lt(J.get(a, j), m):
                    m = J.get(a, j)
                j = J.inc(j)
            J.set(out, i, (None if J.seq(m, G_Infinity) else m))
            i = J.inc(i)
        return out
    def rollMax(a=J.undefined, len=J.undefined, *_args):
        out = G_series_of(None)
        n = J.get(a, "length")
        i = 0
        while J.lt(i, n):
            m = J.neg(G_Infinity)
            f = J.get(G_Math, "max")(0, J.add(J.sub(i, len), 1))
            j = f
            while J.le(j, i):
                if J.gt(J.get(a, j), m):
                    m = J.get(a, j)
                j = J.inc(j)
            J.set(out, i, (None if J.seq(m, J.neg(G_Infinity)) else m))
            i = J.inc(i)
        return out
    def arrowPoints(sig=J.undefined, wantLong=J.undefined, *_args):
        pts = J.get(G_Array(N), "fill")(None)
        off = J.mul(J.div(scalePct, 100), 0.18)
        i_6 = 1
        while J.lt(i_6, N):
            if (not J.truthy(J.get(sig, J.sub(i_6, 1)))):
                i_6 = J.inc(i_6)
                continue
            if J.truthy(strict):
                sA = (_t1 if J.truthy(_t1 := J.get(slopeAbs, J.sub(i_6, 1))) else 0)
                st = (_t2 if J.truthy(_t2 := J.get(stretch, J.sub(i_6, 1))) else 0)
                if (not (J.ge(sA, gateSlopeT) or J.ge(st, gateStretch))):
                    i_6 = J.inc(i_6)
                    continue
            prev = J.get(G_close, J.sub(i_6, 1))
            a = (_t3 if J.truthy(_t3 := J.get(atrV, i_6)) else 0)
            okAdv = (J.le(J.div(J.sub(prev, (_t4 if J.truthy(_t4 := J.get(G_low, i_6)) else prev)), J.get(G_Math, "max")(1.0e-9, a)), maeCap) if J.truthy(wantLong) else J.le(J.div(J.sub((_t5 if J.truthy(_t5 := J.get(G_high, i_6)) else prev), prev), J.get(G_Math, "max")(1.0e-9, a)), maeCap))
            moved = (J.gt(J.get(G_close, i_6), prev) if J.truthy(wantLong) else J.lt(J.get(G_close, i_6), prev))
            if (J.truthy(moved) and J.truthy(okAdv)):
                y = J.add((0 if J.nullish(_t6 := J.get(paneInv, i_6)) else _t6), (off if J.truthy(wantLong) else J.neg(off)))
                J.set(pts, i_6, J.obj(("y", y), ("marker", J.obj(("enabled", True), ("radius", 6), ("symbol", ("triangle" if J.truthy(wantLong) else "triangle-down")), ("fillColor", (longClr if J.truthy(wantLong) else shortClr)), ("lineColor", "#ffffff"), ("lineWidth", 1)))))
            i_6 = J.inc(i_6)
        return pts
    G_describe_indicator("RAZORLINE v1 — Intraday Inverted Momentum (Concept)", "lower", J.obj(("shortName", "RAZORLINE"), ("warmup", 300)))
    preset = J.get(G_input, "select")("Preset", "Intraday", J.JSArray(["Scalp", "Intraday", "Swing"]))
    momLenD = 18
    smoothED = 5
    atrLenD = 14
    adaptLenD = 70
    pHighD = 81
    pInnerD = 66
    refLenD = 70
    refSmoothD = 4
    slopeEpsD = 0.0009
    hystBoostD = 1.55
    if J.seq(preset, "Scalp"):
        momLenD = 12
        smoothED = 4
        adaptLenD = 55
        pHighD = 83
        pInnerD = 69
        refLenD = 55
        refSmoothD = 3
        slopeEpsD = 0.0011
        hystBoostD = 1.65
    if J.seq(preset, "Swing"):
        momLenD = 24
        smoothED = 6
        adaptLenD = 100
        pHighD = 78
        pInnerD = 62
        refLenD = 100
        refSmoothD = 5
        slopeEpsD = 0.0006
        hystBoostD = 1.4
    momLen = G_input("Momentum Len", momLenD)
    smoothE = G_input("Smooth EMA", smoothED)
    atrLen = G_input("ATR Len", atrLenD)
    adaptLen = G_input("Adaptive Window", adaptLenD)
    pHigh = G_input("Extreme %", pHighD)
    pInner = G_input("Inner %", pInnerD)
    showRef = J.get(G_input, "boolean")("Show Mirror Ref", True)
    refLen = G_input("Mirror Ref Len", refLenD)
    refSmooth = G_input("Mirror Smooth", refSmoothD)
    showArrows = J.get(G_input, "boolean")("Show Arrows (strong suggestion)", True)
    shadeExtremes = J.get(G_input, "boolean")("Shade Extremes", False)
    maeCap = G_input("MAE Cap ATR", 0.5)
    needCurl = J.get(G_input, "boolean")("Need Curl Turn", True)
    strict = J.get(G_input, "boolean")("Strict Gate (trend filter)", False)
    gateEMALen = G_input("Gate EMA", 50)
    gateSlopeN = G_input("Gate Slope N", 5)
    gateSlopeT = G_input("Gate Slope Thr", 0.002)
    gateStretch = G_input("Gate Stretch ATR", 1)
    scalePct = G_input("Scale %", 2)
    bandInClr = J.get(G_input, "color")("Inner Band", "#666666")
    bandOutClr = J.get(G_input, "color")("Outer Band", "#444444")
    refClr = J.get(G_input, "color")("Mirror Ref", "#9AA0A6")
    upClr = J.get(G_input, "color")("Line UP (red)", "#ff4d4f")
    dnClr = J.get(G_input, "color")("Line DN (green)", "#2fcc56")
    flatClr = J.get(G_input, "color")("Line Flat", "#aaaaaa")
    spineClr = J.get(G_input, "color")("Backbone", "#7f7f7f")
    slopeEps = G_input("Flat Slope Eps", slopeEpsD)
    hystBoost = G_input("Hysteresis x", hystBoostD)
    refCrossUpClr = J.get(G_input, "color")("Ref Cross Up (bearish)", "#ff4d4f")
    refCrossDnClr = J.get(G_input, "color")("Ref Cross Down (bullish)", "#2fcc56")
    refSnapClr = J.get(G_input, "color")("Ref Snap Risk", "#FFD84D")
    longClr = J.get(G_input, "color")("Arrow Long", "#2fcc56")
    shortClr = J.get(G_input, "color")("Arrow Short", "#ff4d4f")
    atrV = G_atr(atrLen)
    def _f1(c=J.undefined, pc=J.undefined, a=J.undefined, *_args):
        return (J.div(J.sub(c, pc), a) if ((not J.nullish(pc)) and J.gt(a, 0)) else 0)
    momRaw = G_for_every(G_close, G_shift(G_close, momLen), atrV, _f1)
    def _f2(v=J.undefined, *_args):
        return J.neg(v)
    invRaw = G_for_every(momRaw, _f2)
    invSm = G_ema(invRaw, smoothE)
    def _f3(a=J.undefined, b=J.undefined, *_args):
        return J.sub((0 if J.nullish(_t1 := a) else _t1), (0 if J.nullish(_t2 := (a if J.nullish(_t3 := b) else _t3)) else _t2))
    slope = G_for_every(invSm, G_shift(invSm, 1), _f3)
    def _f4(v=J.undefined, *_args):
        return abs((_t1 if J.truthy(_t1 := v) else 0))
    absCore = G_for_every(invSm, _f4)
    thrOut = pctileWin(absCore, adaptLen, pHigh)
    thrIn = pctileWin(absCore, adaptLen, pInner)
    rMin = rollMin(G_close, refLen)
    rMax = rollMax(G_close, refLen)
    def _f5(c=J.undefined, lo_2=J.undefined, hi_2=J.undefined, *_args):
        rng = (J.sub(hi_2, lo_2) if ((not J.nullish(hi_2)) and (not J.nullish(lo_2))) else None)
        if (not J.gt(rng, 0)):
            return 0
        return J.sub(J.mul(J.div(J.sub(c, lo_2), rng), 2), 1)
    refNorm = G_for_every(G_close, rMin, rMax, _f5)
    def _f6(v=J.undefined, *_args):
        return J.neg(v)
    refInv = G_for_every(refNorm, _f6)
    refLine = G_ema(refInv, refSmooth)
    gateEMA = G_ema(G_close, gateEMALen)
    def _f7(a=J.undefined, b=J.undefined, *_args):
        ref = (0 if J.nullish(_t1 := (a if J.nullish(_t2 := b) else _t2)) else _t1)
        dv = J.sub((0 if J.nullish(_t3 := a) else _t3), ref)
        px = J.get(G_Math, "max")(1.0e-9, (_t4 if J.truthy(_t4 := J.get(G_close, 0)) else 1))
        return J.div(abs(dv), px)
    slopeAbs = G_for_every(gateEMA, G_shift(gateEMA, gateSlopeN), _f7)
    def _f8(c=J.undefined, e=J.undefined, a=J.undefined, *_args):
        return (J.div(abs(J.sub(c, (c if J.nullish(_t1 := e) else _t1))), a) if J.gt(a, 0) else 0)
    stretch = G_for_every(G_close, G_ema(G_close, 20), atrV, _f8)
    span = J.div(scalePct, 100)
    N = J.get(G_close, "length")
    paneInv = G_series_of(None)
    paneRef = G_series_of(None)
    bandInP = G_series_of(None)
    bandInM = G_series_of(None)
    bandOutP = G_series_of(None)
    bandOutM = G_series_of(None)
    i = 0
    while J.lt(i, N):
        cap = (1 if J.nullish(_t9 := J.get(thrOut, i)) else _t9)
        tin = (0 if J.nullish(_t10 := J.get(thrIn, i)) else _t10)
        tout = (0 if J.nullish(_t11 := J.get(thrOut, i)) else _t11)
        J.set(paneInv, i, scaleVal(J.get(invSm, i), cap, span))
        J.set(bandInP, i, scaleVal(tin, cap, span))
        J.set(bandInM, i, scaleVal(J.neg(tin), cap, span))
        J.set(bandOutP, i, scaleVal(tout, cap, span))
        J.set(bandOutM, i, scaleVal(J.neg(tout), cap, span))
        J.set(paneRef, i, J.mul((0 if J.nullish(_t12 := J.get(refLine, i)) else _t12), span))
        i = J.inc(i)
    if J.truthy(shadeExtremes):
        shade = G_series_of(0)
        scol = G_series_of("#00000000")
        h = J.mul(0.12, span)
        i_2 = 0
        while J.lt(i_2, N):
            isExtreme = J.ge(abs((_t13 if J.truthy(_t13 := J.get(invSm, i_2)) else 0)), (_t14 if J.truthy(_t14 := J.get(thrOut, i_2)) else G_Infinity))
            if J.truthy(isExtreme):
                up = J.gt((0 if J.nullish(_t15 := J.get(invSm, i_2)) else _t15), 0)
                J.set(shade, i_2, (h if J.truthy(up) else J.neg(h)))
                J.set(scol, i_2, ("rgba(255,77,79,0.12)" if J.truthy(up) else "rgba(47,204,86,0.12)"))
            i_2 = J.inc(i_2)
        G_paint(shade, J.obj(("style", "histogram"), ("name", "RZR_Shade"), ("color", scol)))
    G_paint(bandOutP, J.obj(("style", "line"), ("name", "RZR_OutP"), ("color", bandOutClr), ("width", 1)))
    G_paint(bandOutM, J.obj(("style", "line"), ("name", "RZR_OutM"), ("color", bandOutClr), ("width", 1)))
    G_paint(bandInP, J.obj(("style", "line"), ("name", "RZR_InP"), ("color", bandInClr), ("width", 1)))
    G_paint(bandInM, J.obj(("style", "line"), ("name", "RZR_InM"), ("color", bandInClr), ("width", 1)))
    G_paint(paneInv, J.obj(("style", "line"), ("name", "RZR_Backbone"), ("color", spineClr), ("width", 1)))
    upSeg = J.get(G_Array(N), "fill")(None)
    dnSeg = J.get(G_Array(N), "fill")(None)
    flSeg = J.get(G_Array(N), "fill")(None)
    state = 0
    hi = J.mul(slopeEps, hystBoost)
    lo = J.neg(hi)
    i_3 = 1
    while J.lt(i_3, N):
        s = (_t16 if J.truthy(_t16 := J.get(slope, i_3)) else 0)
        if J.gt(s, hi):
            state = J.pos(1)
        elif J.lt(s, lo):
            state = (-1)
        elif J.le(abs(s), slopeEps):
            state = 0
        if J.seq(state, J.pos(1)):
            J.set(upSeg, i_3, J.get(paneInv, i_3))
            if (J.nullish(J.get(upSeg, J.sub(i_3, 1)))):
                J.set(upSeg, J.sub(i_3, 1), J.get(paneInv, J.sub(i_3, 1)))
        elif J.seq(state, (-1)):
            J.set(dnSeg, i_3, J.get(paneInv, i_3))
            if (J.nullish(J.get(dnSeg, J.sub(i_3, 1)))):
                J.set(dnSeg, J.sub(i_3, 1), J.get(paneInv, J.sub(i_3, 1)))
        else:
            J.set(flSeg, i_3, J.get(paneInv, i_3))
            if (J.nullish(J.get(flSeg, J.sub(i_3, 1)))):
                J.set(flSeg, J.sub(i_3, 1), J.get(paneInv, J.sub(i_3, 1)))
        i_3 = J.inc(i_3)
    G_paint(upSeg, J.obj(("style", "line"), ("name", "RZR_Line_UP"), ("color", upClr), ("width", 2)))
    G_paint(dnSeg, J.obj(("style", "line"), ("name", "RZR_Line_DN"), ("color", dnClr), ("width", 2)))
    G_paint(flSeg, J.obj(("style", "line"), ("name", "RZR_Line_FL"), ("color", flatClr), ("width", 2)))
    if J.truthy(showRef):
        G_paint(paneRef, J.obj(("style", "line"), ("name", "RZR_Ref"), ("color", refClr), ("width", 1), ("dashStyle", "dash")))
        crossUpPts = J.get(G_Array(N), "fill")(None)
        crossDnPts = J.get(G_Array(N), "fill")(None)
        snapRiskPts = J.get(G_Array(N), "fill")(None)
        i_4 = 1
        while J.lt(i_4, N):
            dPrev = J.sub((0 if J.nullish(_t17 := J.get(invSm, J.sub(i_4, 1))) else _t17), (0 if J.nullish(_t18 := J.get(refLine, J.sub(i_4, 1))) else _t18))
            dNow = J.sub((0 if J.nullish(_t19 := J.get(invSm, i_4)) else _t19), (0 if J.nullish(_t20 := J.get(refLine, i_4)) else _t20))
            if ((J.sne(sign(dPrev), 0) and J.sne(sign(dNow), 0)) and J.sne(sign(dPrev), sign(dNow))):
                if (J.lt(dPrev, 0) and J.gt(dNow, 0)):
                    J.set(crossUpPts, i_4, J.obj(("y", J.get(paneRef, i_4)), ("marker", J.obj(("enabled", True), ("radius", 4), ("symbol", "circle"), ("fillColor", refCrossUpClr), ("lineWidth", 0)))))
                if (J.gt(dPrev, 0) and J.lt(dNow, 0)):
                    J.set(crossDnPts, i_4, J.obj(("y", J.get(paneRef, i_4)), ("marker", J.obj(("enabled", True), ("radius", 4), ("symbol", "circle"), ("fillColor", refCrossDnClr), ("lineWidth", 0)))))
            extremeNow = J.ge(abs((_t21 if J.truthy(_t21 := J.get(invSm, i_4)) else 0)), (_t22 if J.truthy(_t22 := J.get(thrOut, i_4)) else G_Infinity))
            extremePrev = J.ge(abs((_t23 if J.truthy(_t23 := J.get(invSm, J.sub(i_4, 1))) else 0)), (_t24 if J.truthy(_t24 := J.get(thrOut, J.sub(i_4, 1))) else G_Infinity))
            distPrev = J.get(G_Math, "abs")(dPrev)
            distNow = J.get(G_Math, "abs")(dNow)
            if ((J.truthy(extremePrev) and J.truthy(extremeNow)) and J.lt(distNow, distPrev)):
                J.set(snapRiskPts, i_4, J.obj(("y", J.get(paneRef, i_4)), ("marker", J.obj(("enabled", True), ("radius", 4), ("symbol", "circle"), ("fillColor", refSnapClr), ("lineWidth", 0)))))
            i_4 = J.inc(i_4)
        G_paint(crossUpPts, J.obj(("name", "RZR_RefCrossUp"), ("color", "transparent")))
        G_paint(crossDnPts, J.obj(("name", "RZR_RefCrossDn"), ("color", "transparent")))
        G_paint(snapRiskPts, J.obj(("name", "RZR_RefSnap"), ("color", "transparent")))
    isPeak = G_series_of(0)
    isTrough = G_series_of(0)
    i_5 = 1
    while J.lt(i_5, J.sub(N, 1)):
        v0 = J.get(invSm, J.sub(i_5, 1))
        v1 = J.get(invSm, i_5)
        v2 = J.get(invSm, J.add(i_5, 1))
        extreme = J.ge(abs((_t25 if J.truthy(_t25 := v1) else 0)), (_t26 if J.truthy(_t26 := J.get(thrOut, i_5)) else 0))
        curlP = (J.lt(J.sub(v2, v1), 0) if J.truthy(needCurl) else True)
        curlT = (J.gt(J.sub(v2, v1), 0) if J.truthy(needCurl) else True)
        if (((J.truthy(extreme) and J.gt(v1, v0)) and J.gt(v1, v2)) and J.truthy(curlP)):
            J.set(isPeak, i_5, 1)
        if (((J.truthy(extreme) and J.lt(v1, v0)) and J.lt(v1, v2)) and J.truthy(curlT)):
            J.set(isTrough, i_5, 1)
        i_5 = J.inc(i_5)
    if J.truthy(showArrows):
        longPts = arrowPoints(isPeak, True)
        shortPts = arrowPoints(isTrough, False)
        G_paint(longPts, J.obj(("name", "RZR_Long"), ("color", "transparent")))
        G_paint(shortPts, J.obj(("name", "RZR_Short"), ("color", "transparent")))
    def _f27(v=J.undefined, *_args):
        return (not (not J.truthy(v)))
    G_register_signal(G_for_every(isPeak, _f27), "RZR Long (arrow)")
    def _f28(v=J.undefined, *_args):
        return (not (not J.truthy(v)))
    G_register_signal(G_for_every(isTrough, _f28), "RZR Short (arrow)")
    def _f29(ps=J.undefined, pr=J.undefined, cs=J.undefined, cr=J.undefined, *_args):
        a = J.sub((0 if J.nullish(_t1 := ps) else _t1), (0 if J.nullish(_t2 := pr) else _t2))
        b = J.sub((0 if J.nullish(_t3 := cs) else _t3), (0 if J.nullish(_t4 := cr) else _t4))
        return (J.gt(b, 0) if J.truthy(_t5 := (J.lt(a, 0) if J.truthy(_t6 := (J.sne(sign(a), sign(b)) if J.truthy(_t7 := (J.sne(sign(b), 0) if J.truthy(_t8 := J.sne(sign(a), 0)) else _t8)) else _t7)) else _t6)) else _t5)
    refCrossUpSig = G_for_every(G_shift(invSm, 1), G_shift(refLine, 1), invSm, refLine, _f29)
    def _f30(ps=J.undefined, pr=J.undefined, cs=J.undefined, cr=J.undefined, *_args):
        a = J.sub((0 if J.nullish(_t1 := ps) else _t1), (0 if J.nullish(_t2 := pr) else _t2))
        b = J.sub((0 if J.nullish(_t3 := cs) else _t3), (0 if J.nullish(_t4 := cr) else _t4))
        return (J.lt(b, 0) if J.truthy(_t5 := (J.gt(a, 0) if J.truthy(_t6 := (J.sne(sign(a), sign(b)) if J.truthy(_t7 := (J.sne(sign(b), 0) if J.truthy(_t8 := J.sne(sign(a), 0)) else _t8)) else _t7)) else _t6)) else _t5)
    refCrossDnSig = G_for_every(G_shift(invSm, 1), G_shift(refLine, 1), invSm, refLine, _f30)
    def _f31(p=J.undefined, c=J.undefined, pt=J.undefined, ct=J.undefined, *_args):
        exPrev = J.ge(abs((_t1 if J.truthy(_t1 := p) else 0)), (_t2 if J.truthy(_t2 := pt) else G_Infinity))
        exNow = J.ge(abs((_t3 if J.truthy(_t3 := c) else 0)), (_t4 if J.truthy(_t4 := ct) else G_Infinity))
        return (exNow if J.truthy(_t5 := exPrev) else _t5)
    snapRiskSig = G_for_every(G_shift(invSm, 1), invSm, G_shift(thrOut, 1), thrOut, _f31)
    G_register_signal(refCrossUpSig, "RZR Ref Cross Up (bearish confirm)")
    G_register_signal(refCrossDnSig, "RZR Ref Cross Down (bullish confirm)")
    G_register_signal(snapRiskSig, "RZR Snap Risk (extreme continuation)")


register_store_indicator(
    script,
    name='razorline_v1_intraday_inverted_momentum_concept_TS',
    title='RAZORLINE v1 — Intraday Inverted Momentum (Concept)',
    developer='James Chellis',
    url='https://trendspider.com/trading-tools-store/indicators/689fe5-razorline-v1-intraday-inverted-momentum-concept/',
    position='lower',
    inputs=[{'id': 'warmup', 'title': 'Warmup', 'type': 'number', 'default': 300}, {'id': 'preset', 'title': 'Preset', 'type': 'select_wide', 'default': 'Intraday', 'options': ['Scalp', 'Intraday', 'Swing']}, {'id': 'momentum_len', 'title': 'Momentum Len', 'type': 'number', 'default': 18}, {'id': 'smooth_ema', 'title': 'Smooth EMA', 'type': 'number', 'default': 5}, {'id': 'atr_len', 'title': 'ATR Len', 'type': 'number', 'default': 14}, {'id': 'adaptive_window', 'title': 'Adaptive Window', 'type': 'number', 'default': 70}, {'id': 'extreme__', 'title': 'Extreme %', 'type': 'number', 'default': 81}, {'id': 'inner__', 'title': 'Inner %', 'type': 'number', 'default': 66}, {'id': 'show_mirror_ref', 'title': 'Show Mirror Ref', 'type': 'boolean', 'default': True}, {'id': 'mirror_ref_len', 'title': 'Mirror Ref Len', 'type': 'number', 'default': 70}, {'id': 'mirror_smooth', 'title': 'Mirror Smooth', 'type': 'number', 'default': 4}, {'id': 'show_arrows__strong_suggestion_', 'title': 'Show Arrows (strong suggestion)', 'type': 'boolean', 'default': True}, {'id': 'shade_extremes', 'title': 'Shade Extremes', 'type': 'boolean', 'default': False}, {'id': 'mae_cap_atr', 'title': 'MAE Cap ATR', 'type': 'number', 'default': 0.5}, {'id': 'need_curl_turn', 'title': 'Need Curl Turn', 'type': 'boolean', 'default': True}, {'id': 'strict_gate__trend_filter_', 'title': 'Strict Gate (trend filter)', 'type': 'boolean', 'default': False}, {'id': 'gate_ema', 'title': 'Gate EMA', 'type': 'number', 'default': 50}, {'id': 'gate_slope_n', 'title': 'Gate Slope N', 'type': 'number', 'default': 5}, {'id': 'gate_slope_thr', 'title': 'Gate Slope Thr', 'type': 'number', 'default': 0.002}, {'id': 'gate_stretch_atr', 'title': 'Gate Stretch ATR', 'type': 'number', 'default': 1}, {'id': 'scale__', 'title': 'Scale %', 'type': 'number', 'default': 2}, {'id': 'inner_band', 'title': 'Inner Band', 'type': 'color', 'default': '#666666'}, {'id': 'outer_band', 'title': 'Outer Band', 'type': 'color', 'default': '#444444'}, {'id': 'mirror_ref', 'title': 'Mirror Ref', 'type': 'color', 'default': '#9AA0A6'}, {'id': 'line_up__red_', 'title': 'Line UP (red)', 'type': 'color', 'default': '#ff4d4f'}, {'id': 'line_dn__green_', 'title': 'Line DN (green)', 'type': 'color', 'default': '#2fcc56'}, {'id': 'line_flat', 'title': 'Line Flat', 'type': 'color', 'default': '#aaaaaa'}, {'id': 'backbone', 'title': 'Backbone', 'type': 'color', 'default': '#7f7f7f'}, {'id': 'flat_slope_eps', 'title': 'Flat Slope Eps', 'type': 'number', 'default': 0.0009}, {'id': 'hysteresis_x', 'title': 'Hysteresis x', 'type': 'number', 'default': 1.55}, {'id': 'ref_cross_up__bearish_', 'title': 'Ref Cross Up (bearish)', 'type': 'color', 'default': '#ff4d4f'}, {'id': 'ref_cross_down__bullish_', 'title': 'Ref Cross Down (bullish)', 'type': 'color', 'default': '#2fcc56'}, {'id': 'ref_snap_risk', 'title': 'Ref Snap Risk', 'type': 'color', 'default': '#FFD84D'}, {'id': 'arrow_long', 'title': 'Arrow Long', 'type': 'color', 'default': '#2fcc56'}, {'id': 'arrow_short', 'title': 'Arrow Short', 'type': 'color', 'default': '#ff4d4f'}],
    outputs=['rzr_outp', 'rzr_outm', 'rzr_inp', 'rzr_inm', 'rzr_backbone', 'rzr_line_up', 'rzr_line_dn', 'rzr_line_fl', 'rzr_ref', 'rzr_refcrossup', 'rzr_refcrossdn', 'rzr_refsnap', 'rzr_long', 'rzr_short', 'rzr_long__arrow_', 'rzr_short__arrow_', 'rzr_ref_cross_up__bearish_confirm_', 'rzr_ref_cross_down__bullish_confirm_', 'rzr_snap_risk__extreme_continuation_'],
    signals=['rzr_long__arrow_', 'rzr_short__arrow_', 'rzr_ref_cross_up__bearish_confirm_', 'rzr_ref_cross_down__bullish_confirm_', 'rzr_snap_risk__extreme_continuation_'],
    requires=[],
    parity='exact',
)
