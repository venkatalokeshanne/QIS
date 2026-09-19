"""
LRS Fib Squeeze+ -- TrendSpider store indicator by Gustivus.

Registered as "lrs_fib_squeeze_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/689b9a-lrs-fib-squeeze/)
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
    G_atr = G["atr"]
    G_close = G["close"]
    G_constants = G["constants"]
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
    G_market = G["market"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_series_of = G["series_of"]
    G_sliding_window_function = G["sliding_window_function"]
    G_sma = G["sma"]
    G_sub = G["sub"]
    G_describe_indicator("LRS Fib Squeeze+", "lower", J.obj(("decimals", "by_symbol_+4"), ("shortName", "LRS+")))
    length = J.get(G_input, "number")("Length", 20, J.obj(("min", 2), ("max", 199)))
    priceSrc = J.get(G_input, "select")("Price source", "close", J.get(G_constants, "price_source_options"))
    price = J.get(G_market, priceSrc)
    closeOnlySel = J.get(G_input, "select")("Close-Only Mode", "Off", J.JSArray(["Off", "On"]))
    closeOnly = J.seq(closeOnlySel, "On")
    invLen = J.get(G_input, "number")("Inversion Lookback", 8, J.obj(("min", 3), ("max", 50), ("step", 1)))
    invMinPk = J.get(G_input, "number")("Inversion Min |Hist|", 0.4, J.obj(("min", 0), ("max", 10), ("step", 0.05)))
    invMinTurn = J.get(G_input, "number")("Inversion Min Turn (abs)", 0.08, J.obj(("min", 0), ("max", 10), ("step", 0.01)))
    invTolPct = J.get(G_input, "number")("Inversion Peak Tolerance %", 0.15, J.obj(("min", 0), ("max", 0.5), ("step", 0.01)))
    invMaxAge = J.get(G_input, "number")("Inversion Max Age (bars)", 3, J.obj(("min", 1), ("max", 10), ("step", 1)))
    invSmoothN = J.get(G_input, "number")("Inversion Smooth EMA", 3, J.obj(("min", 1), ("max", 10), ("step", 1)))
    fib236 = J.get(G_input, "number")("Fib 23.6%", 0.236, J.obj(("min", 0), ("max", 1), ("step", 0.001)))
    fib382 = J.get(G_input, "number")("Fib 38.2%", 0.382, J.obj(("min", 0), ("max", 1), ("step", 0.001)))
    fib500 = J.get(G_input, "number")("Fib 50.0%", 0.5, J.obj(("min", 0), ("max", 1), ("step", 0.001)))
    fib618 = J.get(G_input, "number")("Fib 61.8%", 0.618, J.obj(("min", 0), ("max", 1), ("step", 0.001)))
    fib786 = J.get(G_input, "number")("Fib 78.6%", 0.786, J.obj(("min", 0), ("max", 1), ("step", 0.001)))
    squeezeThreshold = J.get(G_input, "number")("Squeeze Threshold (fixed)", 0.3, J.obj(("min", 0), ("max", 1), ("step", 0.01)))
    slopeLineThickness = J.get(G_input, "number")("Slope Line Thickness", 3, J.obj(("min", 1), ("max", 5), ("step", 1)))
    volLen = J.get(G_input, "number")("Slope Vol Lookback", 20, J.obj(("min", 5), ("max", 300), ("step", 1)))
    bandK = J.get(G_input, "number")("Slope Band Mult", 2, J.obj(("min", 0.5), ("max", 5), ("step", 0.1)))
    bandType = J.get(G_input, "select")("Band Type", "StdDev", J.JSArray(["StdDev", "MAD"]))
    madLen = J.get(G_input, "number")("MAD Len", 20, J.obj(("min", 5), ("max", 300), ("step", 1)))
    thresholdMode = J.get(G_input, "select")("Threshold Mode", "Adaptive (z-score)", J.JSArray(["Fixed", "Adaptive (z-score)", "Adaptive (percentile)"]))
    zLen = J.get(G_input, "number")("Adaptive Lookback (z)", 100, J.obj(("min", 20), ("max", 500), ("step", 1)))
    zCut = J.get(G_input, "number")("Adaptive Cut (z)", (-0.5), J.obj(("min", (-3)), ("max", 3), ("step", 0.1)))
    prLen = J.get(G_input, "number")("Percentile Lookback", 100, J.obj(("min", 30), ("max", 500), ("step", 5)))
    pctCut = J.get(G_input, "number")("Percentile Cut (0..1)", 0.2, J.obj(("min", 0.05), ("max", 0.5), ("step", 0.01)))
    minImpulse = J.get(G_input, "number")("Min Hist Impulse", 0.15, J.obj(("min", 0), ("max", 5), ("step", 0.01)))
    histScale = J.get(G_input, "number")("Hist Scale", 0.2, J.obj(("min", 0.01), ("max", 5), ("step", 0.01)))
    histCap = J.get(G_input, "number")("Hist Cap (abs)", 3, J.obj(("min", 0.1), ("max", 50), ("step", 0.1)))
    histDead = J.get(G_input, "number")("Hist Deadzone", 0.05, J.obj(("min", 0), ("max", 2), ("step", 0.01)))
    histSmooth = J.get(G_input, "number")("Hist Smooth EMA", 3, J.obj(("min", 1), ("max", 20), ("step", 1)))
    signStreak = J.get(G_input, "number")("Min Sign Streak", 2, J.obj(("min", 0), ("max", 5), ("step", 1)))
    paintSmoothSel = J.get(G_input, "select")("Paint Smoothed Histogram", "On", J.JSArray(["On", "Off"]))
    paintSmoothed = J.seq(paintSmoothSel, "On")
    useSmoothSel = J.get(G_input, "select")("Use Smoothed Hist For Signals", "On", J.JSArray(["On", "Off"]))
    useSmoothedForSignals = J.seq(useSmoothSel, "On")
    signVoteLen = J.get(G_input, "number")("Sign Vote Window", 3, J.obj(("min", 1), ("max", 5), ("step", 1)))
    signVotePct = J.get(G_input, "number")("Sign Vote Majority %", 0.6, J.obj(("min", 0.5), ("max", 1), ("step", 0.05)))
    revBlock = J.get(G_input, "number")("Reversal Block Bars", 0, J.obj(("min", 0), ("max", 5), ("step", 1)))
    def rollingStd(series=J.undefined, win=J.undefined, *_args):
        def _f1(vals=J.undefined, *_args):
            n = J.get(vals, "length")
            if J.seq(n, 0):
                return 0
            tot = 0
            i = 0
            while J.lt(i, n):
                tot = J.add(tot, J.get(vals, i))
                i = J.inc(i)
            mean = J.div(tot, n)
            vari = 0
            i_2 = 0
            while J.lt(i_2, n):
                d = J.sub(J.get(vals, i_2), mean)
                vari = J.add(vari, J.mul(d, d))
                i_2 = J.inc(i_2)
            return J.get(G_Math, "sqrt")(J.div(vari, J.get(G_Math, "max")(1, J.sub(n, 1))))
        return G_sliding_window_function(series, win, _f1)
    def lrSlope(values=J.undefined, *_args):
        xSum = 0
        ySum = 0
        xySum = 0
        xxSum = 0
        n = J.get(values, "length")
        i = 0
        while J.lt(i, n):
            xSum = J.add(xSum, i)
            ySum = J.add(ySum, J.get(values, i))
            xySum = J.add(xySum, J.mul(i, J.get(values, i)))
            xxSum = J.add(xxSum, J.mul(i, i))
            i = J.inc(i)
        num = J.sub(J.mul(n, xySum), J.mul(xSum, ySum))
        den = J.sub(J.mul(n, xxSum), J.mul(xSum, xSum))
        return (0 if J.seq(den, 0) else J.div(num, den))
    def fibOnRange(h=J.undefined, l=J.undefined, f=J.undefined, *_args):
        return J.add(l, J.mul(J.sub(h, l), f))
    def lag1(series=J.undefined, *_args):
        def _f1(vals=J.undefined, *_args):
            return J.get(vals, 0)
        return G_sliding_window_function(series, 2, _f1)
    def CO(series=J.undefined, *_args):
        return (lag1(series) if J.truthy(closeOnly) else series)
    slope = G_sliding_window_function(price, length, lrSlope)
    rollHi = G_highest(slope, length)
    rollLo = G_lowest(slope, length)
    slopeRange = G_sub(rollHi, rollLo)
    def _f1(h=J.undefined, l=J.undefined, *_args):
        return fibOnRange(h, l, fib236)
    fib236S = G_for_every(rollHi, rollLo, _f1)
    def _f2(h=J.undefined, l=J.undefined, *_args):
        return fibOnRange(h, l, fib382)
    fib382S = G_for_every(rollHi, rollLo, _f2)
    def _f3(h=J.undefined, l=J.undefined, *_args):
        return fibOnRange(h, l, fib500)
    fib500S = G_for_every(rollHi, rollLo, _f3)
    def _f4(h=J.undefined, l=J.undefined, *_args):
        return fibOnRange(h, l, fib618)
    fib618S = G_for_every(rollHi, rollLo, _f4)
    def _f5(h=J.undefined, l=J.undefined, *_args):
        return fibOnRange(h, l, fib786)
    fib786S = G_for_every(rollHi, rollLo, _f5)
    myAtr = G_atr(G_high, G_low, G_close, length)
    normalizedRange = G_div(slopeRange, myAtr)
    nrMean = G_sma(normalizedRange, zLen)
    nrStd = rollingStd(normalizedRange, zLen)
    nrZ = G_div(G_sub(normalizedRange, nrMean), nrStd)
    def _f6(vals=J.undefined, *_args):
        last = J.get(vals, J.sub(J.get(vals, "length"), 1))
        cnt = 0
        i = 0
        while J.lt(i, J.get(vals, "length")):
            if J.le(J.get(vals, i), last):
                cnt = J.inc(cnt)
            i = J.inc(i)
        return J.div(cnt, J.get(vals, "length"))
    nrRank = G_sliding_window_function(normalizedRange, prLen, _f6)
    squeezeBase = J.undefined
    squeezeOn = J.undefined
    if J.seq(thresholdMode, "Adaptive (z-score)"):
        squeezeBase = nrZ
        def _f7(z=J.undefined, *_args):
            return J.lt(z, zCut)
        squeezeOn = G_for_every(nrZ, _f7)
    elif J.seq(thresholdMode, "Adaptive (percentile)"):
        def _f8(r=J.undefined, *_args):
            return J.sub(r, pctCut)
        squeezeBase = G_for_every(nrRank, _f8)
        def _f9(r=J.undefined, *_args):
            return J.le(r, pctCut)
        squeezeOn = G_for_every(nrRank, _f9)
    else:
        squeezeBase = G_sub(normalizedRange, squeezeThreshold)
        def _f10(v=J.undefined, *_args):
            return J.lt(v, squeezeThreshold)
        squeezeOn = G_for_every(normalizedRange, _f10)
    slopeMom = G_sub(slope, G_ema(slope, 2))
    def _f11(v=J.undefined, *_args):
        return J.get(G_Math, "abs")(v)
    magRaw = G_for_every(squeezeBase, _f11)
    def _f12(m=J.undefined, *_args):
        return (1 if J.ge(m, 0) else (-1))
    signSeries = G_for_every(slopeMom, _f12)
    def _f13(sz=J.undefined, sg=J.undefined, *_args):
        return J.mul(sz, sg)
    histRaw = G_for_every(magRaw, signSeries, _f13)
    def _f14(v=J.undefined, *_args):
        return (None if (J.nullish(v)) else (0 if J.lt(J.get(G_Math, "abs")(v), histDead) else v))
    histDZ = G_for_every(histRaw, _f14)
    def _f15(v=J.undefined, *_args):
        return J.get(G_Math, "abs")(v)
    magDZ = G_for_every(histDZ, _f15)
    magSm = G_ema(magDZ, histSmooth)
    def _f16(v=J.undefined, *_args):
        return (1 if J.gt(v, 0) else ((-1) if J.lt(v, 0) else 0))
    signRawS = G_for_every(histDZ, _f16)
    N = J.get(G_Math, "max")(1, signVoteLen)
    TH = J.get(G_Math, "ceil")(J.mul(N, J.get(G_Math, "max")(0.5, J.get(G_Math, "min")(1, signVotePct))))
    def _f17(vals=J.undefined, *_args):
        s = 0
        i = 0
        while J.lt(i, J.get(vals, "length")):
            s = J.add(s, (_t1 if J.truthy(_t1 := J.get(vals, i)) else 0))
            i = J.inc(i)
        return s
    signSumN = G_sliding_window_function(signRawS, N, _f17)
    def _f18(sum=J.undefined, *_args):
        if J.ge(sum, TH):
            return 1
        if J.le(sum, J.neg(TH)):
            return (-1)
        return 0
    decidedSign = G_for_every(signSumN, _f18)
    def _f19(vals=J.undefined, *_args):
        i = J.sub(J.get(vals, "length"), 1)
        while J.ge(i, 0):
            v = J.get(vals, i)
            if (J.seq(v, 1) or J.seq(v, (-1))):
                return v
            i = J.dec(i)
        return 0
    stickySign = G_sliding_window_function(decidedSign, J.add(N, 1), _f19)
    def _f20(m=J.undefined, s=J.undefined, *_args):
        return J.mul(m, s)
    histSmoothSeries = G_for_every(magSm, stickySign, _f20)
    histForPaint = (histSmoothSeries if J.truthy(paintSmoothed) else histRaw)
    histForLogic0 = (histSmoothSeries if J.truthy(useSmoothedForSignals) else histRaw)
    slope_CO = CO(slope)
    def _f21(m=J.undefined, s=J.undefined, *_args):
        return J.add(m, J.mul(bandK, s))
    upperBand_CO = CO(G_for_every(G_ema(slope, volLen), rollingStd(slope, volLen), _f21))
    def _f22(m=J.undefined, s=J.undefined, *_args):
        return J.sub(m, J.mul(bandK, s))
    lowerBand_CO = CO(G_for_every(G_ema(slope, volLen), rollingStd(slope, volLen), _f22))
    squeezeOn_CO = CO(squeezeOn)
    histForPaint_CO = CO(histForPaint)
    histForLogic = CO(histForLogic0)
    def _f23(v=J.undefined, *_args):
        return J.mul(v, histScale)
    histScaled = G_for_every(histForPaint_CO, _f23)
    def _f24(v=J.undefined, *_args):
        if (J.nullish(v)):
            return None
        cap = histCap
        return (cap if J.gt(v, cap) else (J.neg(cap) if J.lt(v, J.neg(cap)) else v))
    squeezeHist = G_for_every(histScaled, _f24)
    slopeMean = G_ema(slope, volLen)
    slopeStd = rollingStd(slope, volLen)
    def _f25(m=J.undefined, s=J.undefined, *_args):
        return J.add(m, J.mul(bandK, s))
    upperStd = G_for_every(slopeMean, slopeStd, _f25)
    def _f26(m=J.undefined, s=J.undefined, *_args):
        return J.sub(m, J.mul(bandK, s))
    lowerStd = G_for_every(slopeMean, slopeStd, _f26)
    slopeEMA = G_ema(slope, madLen)
    def _f27(s=J.undefined, m=J.undefined, *_args):
        return J.get(G_Math, "abs")(J.sub(s, m))
    absDev = G_for_every(slope, slopeEMA, _f27)
    mad = G_ema(absDev, madLen)
    def _f28(m=J.undefined, d=J.undefined, *_args):
        return J.add(m, J.mul(bandK, d))
    upperMAD = G_for_every(slopeEMA, mad, _f28)
    def _f29(m=J.undefined, d=J.undefined, *_args):
        return J.sub(m, J.mul(bandK, d))
    lowerMAD = G_for_every(slopeEMA, mad, _f29)
    usingMAD = J.seq(bandType, "MAD")
    upperBand = CO((upperMAD if J.truthy(usingMAD) else upperStd))
    lowerBand = CO((lowerMAD if J.truthy(usingMAD) else lowerStd))
    def _f30(s=J.undefined, *_args):
        return ("red" if J.truthy(s) else "blue")
    slopeColor = G_for_every(squeezeOn_CO, _f30)
    G_paint(slope_CO, J.obj(("name", "Slope"), ("color", slopeColor), ("width", slopeLineThickness)))
    G_paint(upperBand, J.obj(("name", "Slope Upper Band"), ("color", "gray"), ("style", "line"), ("width", 1)))
    G_paint(lowerBand, J.obj(("name", "Slope Lower Band"), ("color", "gray"), ("style", "line"), ("width", 1)))
    G_paint(squeezeHist, J.obj(("name", "Squeeze Histogram"), ("style", "histogram")))
    G_paint(CO(fib236S), J.obj(("name", "Fib 23.6%"), ("color", "silver"), ("width", 1)))
    G_paint(CO(fib382S), J.obj(("name", "Fib 38.2%"), ("color", "silver"), ("width", 1)))
    G_paint(CO(fib500S), J.obj(("name", "Fib 50.0%"), ("color", "silver"), ("width", 1)))
    G_paint(CO(fib618S), J.obj(("name", "Fib 61.8%"), ("color", "silver"), ("width", 1)))
    G_paint(CO(fib786S), J.obj(("name", "Fib 78.6%"), ("color", "silver"), ("width", 1)))
    def _f31(vals=J.undefined, *_args):
        return J.get(vals, 0)
    prevHist = G_sliding_window_function(histForLogic, 2, _f31)
    def _f32(c=J.undefined, p=J.undefined, *_args):
        return (J.gt(c, 0) if J.truthy(_t1 := J.le(p, 0)) else _t1)
    expansionUp = G_for_every(histForLogic, prevHist, _f32)
    def _f33(c=J.undefined, p=J.undefined, *_args):
        return (J.lt(c, 0) if J.truthy(_t1 := J.ge(p, 0)) else _t1)
    expansionDown = G_for_every(histForLogic, prevHist, _f33)
    def _f34(c=J.undefined, p=J.undefined, *_args):
        return (J.ge(J.get(G_Math, "abs")(c), minImpulse) if J.truthy(_t1 := (J.gt(c, 0) if J.truthy(_t2 := J.le(p, 0)) else _t2)) else _t1)
    strongUp = G_for_every(histForLogic, prevHist, _f34)
    def _f35(c=J.undefined, p=J.undefined, *_args):
        return (J.ge(J.get(G_Math, "abs")(c), minImpulse) if J.truthy(_t1 := (J.lt(c, 0) if J.truthy(_t2 := J.ge(p, 0)) else _t2)) else _t1)
    strongDown = G_for_every(histForLogic, prevHist, _f35)
    histDet = G_ema(histForLogic, invSmoothN)
    def _f36(vals=J.undefined, *_args):
        n = J.get(vals, "length")
        if J.lt(n, 3):
            return None
        prev = J.get(vals, J.sub(n, 2))
        curr = J.get(vals, J.sub(n, 1))
        if ((J.nullish(prev)) or (J.nullish(curr))):
            return None
        maxV = J.neg(G_Infinity)
        minV = G_Infinity
        idxMax = (-1)
        idxMin = (-1)
        i = 0
        while J.lt(i, J.sub(n, 1)):
            v = J.get(vals, i)
            if (J.nullish(v)):
                i = J.inc(i)
                continue
            if J.gt(v, maxV):
                maxV = v
                idxMax = i
            if J.lt(v, minV):
                minV = v
                idxMin = i
            i = J.inc(i)
        if (J.lt(idxMax, 0) and J.lt(idxMin, 0)):
            return None
        tolUp = J.mul(J.get(G_Math, "abs")(maxV), invTolPct)
        tolDown = J.mul(J.get(G_Math, "abs")(minV), invTolPct)
        ageMax = (J.sub(J.sub(n, 1), idxMax) if J.ge(idxMax, 0) else G_Infinity)
        ageMin = (J.sub(J.sub(n, 1), idxMin) if J.ge(idxMin, 0) else G_Infinity)
        prevAbs = J.get(G_Math, "abs")(prev)
        turnedDown = J.ge(J.sub(prev, curr), invMinTurn)
        turnedUp = J.ge(J.sub(curr, prev), invMinTurn)
        nearMax = (J.ge(prev, J.sub(maxV, tolUp)) if J.truthy(_t1 := J.gt(maxV, 0)) else _t1)
        recentMax = J.le(ageMax, invMaxAge)
        invDown = (turnedDown if J.truthy(_t2 := (J.ge(prevAbs, invMinPk) if J.truthy(_t3 := (recentMax if J.truthy(_t4 := (nearMax if J.truthy(_t5 := J.gt(prev, 0)) else _t5)) else _t4)) else _t3)) else _t2)
        nearMin = (J.le(prev, J.add(minV, tolDown)) if J.truthy(_t6 := J.lt(minV, 0)) else _t6)
        recentMin = J.le(ageMin, invMaxAge)
        invUp = (turnedUp if J.truthy(_t7 := (J.ge(prevAbs, invMinPk) if J.truthy(_t8 := (recentMin if J.truthy(_t9 := (nearMin if J.truthy(_t10 := J.lt(prev, 0)) else _t10)) else _t9)) else _t8)) else _t7)
        if J.truthy(invDown):
            return 1
        if J.truthy(invUp):
            return (-1)
        return None
    invFlag = G_sliding_window_function(histDet, J.get(G_Math, "max")(invLen, 3), _f36)
    def _f37(f=J.undefined, *_args):
        return (1 if J.seq(f, 1) else None)
    inversionDown = G_for_every(invFlag, _f37)
    def _f38(f=J.undefined, *_args):
        return (1 if J.seq(f, (-1)) else None)
    inversionUp = G_for_every(invFlag, _f38)
    invShadeBars = J.get(G_input, "number")("Inversion Shade Bars", 2, J.obj(("min", 1), ("max", 10), ("step", 1)))
    invShadeHeight = J.get(G_input, "number")("Inversion Shade Height", 0, J.obj(("min", 0), ("max", 50), ("step", 0.1)))
    H = (invShadeHeight if J.gt(invShadeHeight, 0) else histCap)
    def _f39(v=J.undefined, *_args):
        return (1 if J.truthy(v) else 0)
    invDnNum = G_for_every(inversionDown, _f39)
    def _f40(v=J.undefined, *_args):
        return (1 if J.truthy(v) else 0)
    invUpNum = G_for_every(inversionUp, _f40)
    def _f41(v=J.undefined, *_args):
        return (1 if J.gt(v, 0) else None)
    invDnShade = G_for_every(G_highest(invDnNum, invShadeBars), _f41)
    def _f42(v=J.undefined, *_args):
        return (1 if J.gt(v, 0) else None)
    invUpShade = G_for_every(G_highest(invUpNum, invShadeBars), _f42)
    zero = G_series_of(0)
    posH = G_series_of(H)
    negH = G_series_of(J.neg(H))
    def _f43(s=J.undefined, ph=J.undefined, *_args):
        return (ph if J.truthy(s) else None)
    topDn = G_for_every(invDnShade, posH, _f43)
    def _f44(s=J.undefined, z=J.undefined, *_args):
        return (z if J.truthy(s) else None)
    botDn = G_for_every(invDnShade, zero, _f44)
    def _f45(s=J.undefined, z=J.undefined, *_args):
        return (z if J.truthy(s) else None)
    topUp = G_for_every(invUpShade, zero, _f45)
    def _f46(s=J.undefined, nh=J.undefined, *_args):
        return (nh if J.truthy(s) else None)
    botUp = G_for_every(invUpShade, negH, _f46)
    pTopDn = G_paint(CO(topDn), J.obj(("hidden", True)))
    pBotDn = G_paint(CO(botDn), J.obj(("hidden", True)))
    G_fill(pTopDn, pBotDn, "crimson")
    pTopUp = G_paint(CO(topUp), J.obj(("hidden", True)))
    pBotUp = G_paint(CO(botUp), J.obj(("hidden", True)))
    G_fill(pTopUp, pBotUp, "seagreen")
    def toNum(s=J.undefined, *_args):
        def _f1(v=J.undefined, *_args):
            return (1 if J.truthy(v) else 0)
        return G_for_every(s, _f1)
    expUpNum = toNum(expansionUp)
    expDnNum = toNum(expansionDown)
    invUpNumB = toNum(inversionUp)
    invDnNumB = toNum(inversionDown)
    def makeRecent(numSeries=J.undefined, n=J.undefined, *_args):
        def _f1(v=J.undefined, *_args):
            return (1 if J.gt(v, 0) else 0)
        return (G_for_every(G_highest(numSeries, n), _f1) if J.gt(n, 0) else G_series_of(0))
    recentExpUp = CO(makeRecent(expUpNum, revBlock))
    recentExpDn = CO(makeRecent(expDnNum, revBlock))
    recentInvUp = CO(makeRecent(invUpNumB, revBlock))
    recentInvDn = CO(makeRecent(invDnNumB, revBlock))
    def _f47(sig=J.undefined, opp=J.undefined, *_args):
        return (1 if (J.truthy(sig) and J.seq(opp, 0)) else None)
    expansionUp_blk = G_for_every(expansionUp, recentExpDn, _f47)
    def _f48(sig=J.undefined, opp=J.undefined, *_args):
        return (1 if (J.truthy(sig) and J.seq(opp, 0)) else None)
    expansionDown_blk = G_for_every(expansionDown, recentExpUp, _f48)
    def _f49(sig=J.undefined, opp=J.undefined, *_args):
        return (1 if (J.truthy(sig) and J.seq(opp, 0)) else None)
    inversionUp_blk = G_for_every(inversionUp, recentInvDn, _f49)
    def _f50(sig=J.undefined, opp=J.undefined, *_args):
        return (1 if (J.truthy(sig) and J.seq(opp, 0)) else None)
    inversionDown_blk = G_for_every(inversionDown, recentInvUp, _f50)
    G_register_signal(squeezeOn_CO, "Squeeze On")
    def _f51(v=J.undefined, *_args):
        return (not J.truthy(v))
    G_register_signal(G_for_every(squeezeOn_CO, _f51), "Squeeze Off")
    G_register_signal(expansionUp, "Expansion Up")
    G_register_signal(expansionDown, "Expansion Down")
    G_register_signal(strongUp, "Expansion Up (strong)")
    G_register_signal(strongDown, "Expansion Down (strong)")
    G_register_signal(inversionUp, "Inversion Up")
    G_register_signal(inversionDown, "Inversion Down")


register_store_indicator(
    script,
    name='lrs_fib_squeeze_TS',
    title='LRS Fib Squeeze+',
    developer='Gustivus',
    url='https://trendspider.com/trading-tools-store/indicators/689b9a-lrs-fib-squeeze/',
    position='lower',
    inputs=[{'id': 'length', 'title': 'Length', 'type': 'number', 'default': 20}, {'id': 'price_source', 'title': 'Price source', 'type': 'select_wide', 'default': 'close', 'options': ['open', 'high', 'low', 'close', 'hl2', 'oc2', 'hlc3', 'ohlc4', 'wclose']}, {'id': 'close_only_mode', 'title': 'Close-Only Mode', 'type': 'select_wide', 'default': 'Off', 'options': ['Off', 'On']}, {'id': 'inversion_lookback', 'title': 'Inversion Lookback', 'type': 'number', 'default': 8}, {'id': 'inversion_min__hist_', 'title': 'Inversion Min |Hist|', 'type': 'number', 'default': 0.4}, {'id': 'inversion_min_turn__abs_', 'title': 'Inversion Min Turn (abs)', 'type': 'number', 'default': 0.08}, {'id': 'inversion_peak_tolerance__', 'title': 'Inversion Peak Tolerance %', 'type': 'number', 'default': 0.15}, {'id': 'inversion_max_age__bars_', 'title': 'Inversion Max Age (bars)', 'type': 'number', 'default': 3}, {'id': 'inversion_smooth_ema', 'title': 'Inversion Smooth EMA', 'type': 'number', 'default': 3}, {'id': 'fib_23_6_', 'title': 'Fib 23.6%', 'type': 'number', 'default': 0.236}, {'id': 'fib_38_2_', 'title': 'Fib 38.2%', 'type': 'number', 'default': 0.382}, {'id': 'fib_50_0_', 'title': 'Fib 50.0%', 'type': 'number', 'default': 0.5}, {'id': 'fib_61_8_', 'title': 'Fib 61.8%', 'type': 'number', 'default': 0.618}, {'id': 'fib_78_6_', 'title': 'Fib 78.6%', 'type': 'number', 'default': 0.786}, {'id': 'squeeze_threshold__fixed_', 'title': 'Squeeze Threshold (fixed)', 'type': 'number', 'default': 0.3}, {'id': 'slope_line_thickness', 'title': 'Slope Line Thickness', 'type': 'number', 'default': 3}, {'id': 'slope_vol_lookback', 'title': 'Slope Vol Lookback', 'type': 'number', 'default': 20}, {'id': 'slope_band_mult', 'title': 'Slope Band Mult', 'type': 'number', 'default': 2}, {'id': 'band_type', 'title': 'Band Type', 'type': 'select_wide', 'default': 'StdDev', 'options': ['StdDev', 'MAD']}, {'id': 'mad_len', 'title': 'MAD Len', 'type': 'number', 'default': 20}, {'id': 'threshold_mode', 'title': 'Threshold Mode', 'type': 'select_wide', 'default': 'Adaptive (z-score)', 'options': ['Fixed', 'Adaptive (z-score)', 'Adaptive (percentile)']}, {'id': 'adaptive_lookback__z_', 'title': 'Adaptive Lookback (z)', 'type': 'number', 'default': 100}, {'id': 'adaptive_cut__z_', 'title': 'Adaptive Cut (z)', 'type': 'number', 'default': -0.5}, {'id': 'percentile_lookback', 'title': 'Percentile Lookback', 'type': 'number', 'default': 100}, {'id': 'percentile_cut__0__1_', 'title': 'Percentile Cut (0..1)', 'type': 'number', 'default': 0.2}, {'id': 'min_hist_impulse', 'title': 'Min Hist Impulse', 'type': 'number', 'default': 0.15}, {'id': 'hist_scale', 'title': 'Hist Scale', 'type': 'number', 'default': 0.2}, {'id': 'hist_cap__abs_', 'title': 'Hist Cap (abs)', 'type': 'number', 'default': 3}, {'id': 'hist_deadzone', 'title': 'Hist Deadzone', 'type': 'number', 'default': 0.05}, {'id': 'hist_smooth_ema', 'title': 'Hist Smooth EMA', 'type': 'number', 'default': 3}, {'id': 'min_sign_streak', 'title': 'Min Sign Streak', 'type': 'number', 'default': 2}, {'id': 'paint_smoothed_histogram', 'title': 'Paint Smoothed Histogram', 'type': 'select_wide', 'default': 'On', 'options': ['On', 'Off']}, {'id': 'use_smoothed_hist_for_signals', 'title': 'Use Smoothed Hist For Signals', 'type': 'select_wide', 'default': 'On', 'options': ['On', 'Off']}, {'id': 'sign_vote_window', 'title': 'Sign Vote Window', 'type': 'number', 'default': 3}, {'id': 'sign_vote_majority__', 'title': 'Sign Vote Majority %', 'type': 'number', 'default': 0.6}, {'id': 'reversal_block_bars', 'title': 'Reversal Block Bars', 'type': 'number', 'default': 0}, {'id': 'inversion_shade_bars', 'title': 'Inversion Shade Bars', 'type': 'number', 'default': 2}, {'id': 'inversion_shade_height', 'title': 'Inversion Shade Height', 'type': 'number', 'default': 0}],
    outputs=['slope', 'slope_upper_band', 'slope_lower_band', 'squeeze_histogram', 'fib_23_6_', 'fib_38_2_', 'fib_50_0_', 'fib_61_8_', 'fib_78_6_', 'line_11', 'line_12', 'line_14', 'line_15', 'squeeze_on', 'squeeze_off', 'expansion_up', 'expansion_down', 'expansion_up__strong_', 'expansion_down__strong_', 'inversion_up', 'inversion_down'],
    signals=['squeeze_on', 'squeeze_off', 'expansion_up', 'expansion_down', 'expansion_up__strong_', 'expansion_down__strong_', 'inversion_up', 'inversion_down'],
    requires=[],
    parity='exact',
)
