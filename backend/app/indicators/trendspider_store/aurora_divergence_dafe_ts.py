"""
Aurora Divergence [DAFE] -- TrendSpider store indicator by DskyzInvestments.

Registered as "aurora_divergence_dafe_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6a272e-aurora-divergence-dafe/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_EPS = G["EPS"]
    G_Math = G["Math"]
    G_Number = G["Number"]
    G_String = G["String"]
    G_TH = G["TH"]
    G_absCol = G["absCol"]
    G_absText = G["absText"]
    G_absVal = G["absVal"]
    G_absorption = G["absorption"]
    G_activationLevel = G["activationLevel"]
    G_aggCol = G["aggCol"]
    G_aggText = G["aggText"]
    G_aggVal = G["aggVal"]
    G_atr = G["atr"]
    G_atr14 = G["atr14"]
    G_atrNow = G["atrNow"]
    G_atrVal = G["atrVal"]
    G_bPress = G["bPress"]
    G_bPressNow = G["bPressNow"]
    G_bearBubsCore = G["bearBubsCore"]
    G_bearBubsGlow = G["bearBubsGlow"]
    G_bearColorSeries = G["bearColorSeries"]
    G_bearGlowColorSeries = G["bearGlowColorSeries"]
    G_bearOffset = G["bearOffset"]
    G_bearPressure = G["bearPressure"]
    G_bullBubsCore = G["bullBubsCore"]
    G_bullBubsGlow = G["bullBubsGlow"]
    G_bullColorSeries = G["bullColorSeries"]
    G_bullGlowColorSeries = G["bullGlowColorSeries"]
    G_bullOffset = G["bullOffset"]
    G_bullPressure = G["bullPressure"]
    G_cdCol = G["cdCol"]
    G_cdText = G["cdText"]
    G_close = G["close"]
    G_confVal = G["confVal"]
    G_confidence = G["confidence"]
    G_constants = G["constants"]
    G_cooldownClear = G["cooldownClear"]
    G_cvdSeries = G["cvdSeries"]
    G_dCVD = G["dCVD"]
    G_dClose = G["dClose"]
    G_dMFI = G["dMFI"]
    G_dOBV = G["dOBV"]
    G_dRSI = G["dRSI"]
    G_dashRows = G["dashRows"]
    G_dashVisible = G["dashVisible"]
    G_describe_indicator = G["describe_indicator"]
    G_dnWick = G["dnWick"]
    G_ema = G["ema"]
    G_expectancy = G["expectancy"]
    G_flowColor = G["flowColor"]
    G_flowText = G["flowText"]
    G_hasBearSig = G["hasBearSig"]
    G_hasBullSig = G["hasBullSig"]
    G_high = G["high"]
    G_i_cooldown = G["i_cooldown"]
    G_i_dash = G["i_dash"]
    G_i_decay = G["i_decay"]
    G_i_normWindow = G["i_normWindow"]
    G_i_pressureTh = G["i_pressureTh"]
    G_i_stopATR = G["i_stopATR"]
    G_i_targetATR = G["i_targetATR"]
    G_i_theme = G["i_theme"]
    G_i_trailATR = G["i_trailATR"]
    G_i_trailActivate = G["i_trailActivate"]
    G_i_wickSmoothing = G["i_wickSmoothing"]
    G_i_wickThresh = G["i_wickThresh"]
    G_input = G["input"]
    G_isCdClear = G["isCdClear"]
    G_isChoppy = G["isChoppy"]
    G_isFinite = G["isFinite"]
    G_lastCd = G["lastCd"]
    G_lastHurst = G["lastHurst"]
    G_lastIdx = G["lastIdx"]
    G_library = G["library"]
    G_low = G["low"]
    G_maxB = G["maxB"]
    G_maxR = G["maxR"]
    G_mfiSeries = G["mfiSeries"]
    G_n = G["n"]
    G_narrCols = G["narrCols"]
    G_narrLines = G["narrLines"]
    G_obvSeries = G["obvSeries"]
    G_open = G["open"]
    G_paint = G["paint"]
    G_paint_overlay = G["paint_overlay"]
    G_period = G["period"]
    G_pnlCol = G["pnlCol"]
    G_posColor = G["posColor"]
    G_posText = G["posText"]
    G_profitFactor = G["profitFactor"]
    G_rPress = G["rPress"]
    G_rPressNow = G["rPressNow"]
    G_rawBearDiv = G["rawBearDiv"]
    G_rawBullDiv = G["rawBullDiv"]
    G_rawWickPressure = G["rawWickPressure"]
    G_register_signal = G["register_signal"]
    G_rng = G["rng"]
    G_rsiSeries = G["rsiSeries"]
    G_series_of = G["series_of"]
    G_sigColor = G["sigColor"]
    G_sigText = G["sigText"]
    G_signalBear = G["signalBear"]
    G_signalBull = G["signalBull"]
    G_sma = G["sma"]
    G_smoothWickPressure = G["smoothWickPressure"]
    G_statusBg = G["statusBg"]
    G_statusCol = G["statusCol"]
    G_statusText = G["statusText"]
    G_swp = G["swp"]
    G_tfVal = G["tfVal"]
    G_tickerText = G["tickerText"]
    G_tiny = G["tiny"]
    G_tradePnl = G["tradePnl"]
    G_trailStop = G["trailStop"]
    G_trendColor = G["trendColor"]
    G_trendText = G["trendText"]
    G_unifiedAgg = G["unifiedAgg"]
    G_upWick = G["upWick"]
    G_v_ma = G["v_ma"]
    G_volMA = G["volMA"]
    G_volQuality = G["volQuality"]
    G_volume = G["volume"]
    G_vqCol = G["vqCol"]
    G_vqText = G["vqText"]
    G_vqVal = G["vqVal"]
    G_wb = G["wb"]
    G_winRate = G["winRate"]
    G_wp = G["wp"]
    G_wpCol = G["wpCol"]
    G_wpLast = G["wpLast"]
    G_wr = G["wr"]
    i = J.undefined
    bullImp = J.undefined
    bearImp = J.undefined
    lastSignalBar = J.undefined
    shouldExit = J.undefined
    exitPrice = J.undefined
    trailBest = J.undefined
    trailActive = J.undefined
    totalTrades = J.undefined
    winTrades = J.undefined
    grossProfit = J.undefined
    grossLoss = J.undefined
    totalPnl = J.undefined
    peakEquity = J.undefined
    maxDD = J.undefined
    pos = J.undefined
    entryPrice = J.undefined
    targetPrice = J.undefined
    stopPrice = J.undefined
    k = J.undefined
    def rgba(h=J.undefined, a=J.undefined, *_args):
        return J.get(J.get(G_tiny(h), "setAlpha")(a), "toRgbString")()
    def nz(v=J.undefined, f=J.undefined, *_args):
        return ((f if (not J.nullish(f)) else 0) if ((J.nullish(v)) or (not J.truthy(G_isFinite(v)))) else v)
    def clamp(v=J.undefined, l=J.undefined, h=J.undefined, *_args):
        return J.get(G_Math, "max")(l, J.get(G_Math, "min")(h, v))
    def make(len=J.undefined, val=J.undefined, *_args):
        a = J.undefined
        i_2 = J.undefined
        a = J.JSArray([])
        i_2 = 0
        while J.lt(i_2, len):
            J.get(a, "push")(val)
            i_2 = J.inc(i_2)
        return a
    def fmt(v=J.undefined, *_args):
        return ("—" if ((J.nullish(v)) or (not J.truthy(G_isFinite(v)))) else J.get(G_Number(v), "toFixed")(2))
    def hLine(v=J.undefined, b=J.undefined, *_args):
        a = J.undefined
        i_2 = J.undefined
        a = make(G_n, None)
        if ((J.nullish(v)) or (not J.truthy(G_isFinite(v)))):
            return a
        i_2 = J.get(G_Math, "max")(0, J.sub(G_lastIdx, (_t1 if J.truthy(_t1 := b) else 120)))
        while J.lt(i_2, G_n):
            J.set(a, i_2, v)
            i_2 = J.inc(i_2)
        return a
    def gauge(v=J.undefined, m=J.undefined, l=J.undefined, *_args):
        p = J.undefined
        f = J.undefined
        s = J.undefined
        i_2 = J.undefined
        p = clamp(J.div(v, m), 0, 1)
        f = J.get(G_Math, "round")(J.mul(p, l))
        s = ""
        i_2 = 0
        while J.lt(i_2, l):
            s = J.add(s, ("■" if J.lt(i_2, f) else "□"))
            i_2 = J.inc(i_2)
        return s
    def mkCell(t=J.undefined, c=J.undefined, a=J.undefined, b=J.undefined, cs=J.undefined, bg=J.undefined, *_args):
        return J.obj(("text", G_String(t)), ("color", (_t1 if J.truthy(_t1 := c) else J.get(G_TH, "dim"))), ("textAlign", (_t2 if J.truthy(_t2 := a) else "left")), ("fontSize", 10), ("fontWeight", ("bold" if J.truthy(b) else "normal")), ("colspan", (_t3 if J.truthy(_t3 := cs) else 1)), ("background", (_t4 if J.truthy(_t4 := bg) else J.get(G_TH, "panel"))))
    def mkSub(t=J.undefined, *_args):
        return J.obj(("text", G_String(t)), ("color", J.get(G_TH, "a2")), ("background", rgba(J.get(G_TH, "a2"), 0.06)), ("textAlign", "center"), ("fontSize", 9), ("fontWeight", "bold"), ("colspan", 4))
    def windowSlice(src=J.undefined, idx=J.undefined, len=J.undefined, *_args):
        out = J.undefined
        start = J.undefined
        i_2 = J.undefined
        out = J.JSArray([])
        start = J.get(G_Math, "max")(0, J.add(J.sub(idx, len), 1))
        i_2 = start
        while J.le(i_2, idx):
            J.get(out, "push")(nz(J.get(src, i_2)))
            i_2 = J.inc(i_2)
        return out
    def proxyDelta(i_2=J.undefined, *_args):
        rng = J.undefined
        upWick = J.undefined
        dnWick = J.undefined
        wickPressure = J.undefined
        body = J.undefined
        rng = J.sub(J.get(G_high, i_2), J.get(G_low, i_2))
        if J.le(rng, G_EPS):
            return 0
        upWick = J.sub(J.get(G_high, i_2), J.get(G_Math, "max")(J.get(G_open, i_2), J.get(G_close, i_2)))
        dnWick = J.sub(J.get(G_Math, "min")(J.get(G_open, i_2), J.get(G_close, i_2)), J.get(G_low, i_2))
        wickPressure = J.div(J.sub(dnWick, upWick), rng)
        body = J.get(G_Math, "abs")(J.sub(J.get(G_close, i_2), J.get(G_open, i_2)))
        return J.mul(J.mul(J.get(G_volume, i_2), J.div(body, rng)), (1 if J.gt(J.get(G_close, i_2), J.get(G_open, i_2)) else ((-1) if J.lt(J.get(G_close, i_2), J.get(G_open, i_2)) else wickPressure)))
    def calculateMFI(len=J.undefined, *_args):
        out = J.undefined
        tp = J.undefined
        i_2 = J.undefined
        posFlow = J.undefined
        negFlow = J.undefined
        k_2 = J.undefined
        idx = J.undefined
        flow = J.undefined
        mRatio = J.undefined
        out = make(G_n, 50)
        tp = make(G_n, 0)
        i_2 = 0
        while J.lt(i_2, G_n):
            J.set(tp, i_2, J.div(J.add(J.add(J.get(G_high, i_2), J.get(G_low, i_2)), J.get(G_close, i_2)), 3))
            i_2 = J.inc(i_2)
        i_2 = len
        while J.lt(i_2, G_n):
            posFlow = 0
            negFlow = 0
            k_2 = 0
            while J.lt(k_2, len):
                idx = J.sub(i_2, k_2)
                flow = J.mul(J.get(tp, idx), J.get(G_volume, idx))
                if J.gt(J.get(tp, idx), J.get(tp, J.sub(idx, 1))):
                    posFlow = J.add(posFlow, flow)
                elif J.lt(J.get(tp, idx), J.get(tp, J.sub(idx, 1))):
                    negFlow = J.add(negFlow, flow)
                k_2 = J.inc(k_2)
            mRatio = (J.div(posFlow, negFlow) if J.gt(negFlow, 0) else 100)
            J.set(out, i_2, J.sub(100, J.div(100, J.add(1, mRatio))))
            i_2 = J.inc(i_2)
        return out
    def calculateRSI(len=J.undefined, *_args):
        out = J.undefined
        up = J.undefined
        dn = J.undefined
        i_2 = J.undefined
        diff = J.undefined
        avgUp = J.undefined
        avgDn = J.undefined
        out = make(G_n, 50)
        up = make(G_n, 0)
        dn = make(G_n, 0)
        i_2 = 1
        while J.lt(i_2, G_n):
            diff = J.sub(J.get(G_close, i_2), J.get(G_close, J.sub(i_2, 1)))
            J.set(up, i_2, (diff if J.gt(diff, 0) else 0))
            J.set(dn, i_2, (J.neg(diff) if J.lt(diff, 0) else 0))
            i_2 = J.inc(i_2)
        avgUp = 0
        avgDn = 0
        i_2 = 1
        while J.le(i_2, len):
            avgUp = J.add(avgUp, J.get(up, i_2))
            avgDn = J.add(avgDn, J.get(dn, i_2))
            i_2 = J.inc(i_2)
        avgUp = J.div(avgUp, len)
        avgDn = J.div(avgDn, len)
        J.set(out, len, (100 if J.seq(avgDn, 0) else J.sub(100, J.div(100, J.add(1, J.div(avgUp, avgDn))))))
        i_2 = J.add(len, 1)
        while J.lt(i_2, G_n):
            avgUp = J.div(J.add(J.mul(avgUp, J.sub(len, 1)), J.get(up, i_2)), len)
            avgDn = J.div(J.add(J.mul(avgDn, J.sub(len, 1)), J.get(dn, i_2)), len)
            J.set(out, i_2, (100 if J.seq(avgDn, 0) else J.sub(100, J.div(100, J.add(1, J.div(avgUp, avgDn))))))
            i_2 = J.inc(i_2)
        return out
    def hurstExp(idx=J.undefined, len=J.undefined, *_args):
        mean = J.undefined
        i_2 = J.undefined
        dev = J.undefined
        mn = J.undefined
        mx = J.undefined
        sd = J.undefined
        if J.lt(idx, len):
            return 0.5
        mean = 0
        i_2 = 0
        while J.lt(i_2, len):
            mean = J.add(mean, J.get(G_close, J.sub(idx, i_2)))
            i_2 = J.inc(i_2)
        mean = J.div(mean, len)
        dev = 0
        mn = 0
        mx = 0
        i_2 = 0
        while J.lt(i_2, len):
            dev = J.add(dev, J.sub(J.get(G_close, J.sub(idx, i_2)), mean))
            if J.lt(dev, mn):
                mn = dev
            if J.gt(dev, mx):
                mx = dev
            i_2 = J.inc(i_2)
        sd = 0
        i_2 = 0
        while J.lt(i_2, len):
            sd = J.add(sd, J.get(G_Math, "pow")(J.sub(J.get(G_close, J.sub(idx, i_2)), mean), 2))
            i_2 = J.inc(i_2)
        sd = J.get(G_Math, "sqrt")(J.div(sd, len))
        if (J.le(sd, 0) or J.le(J.sub(mx, mn), 0)):
            return 0.5
        return J.div(J.get(G_Math, "log")(J.div(J.sub(mx, mn), sd)), J.get(G_Math, "log")(len))
    G_describe_indicator("Aurora Divergence [DAFE]", "overlay", J.obj(("shortName", "⟡ AURORA"), ("mainColorInheritFrom", "legend_anchor")))
    G_i_pressureTh = J.get(G_input, "number")("Divergence Threshold %", 80, J.obj(("min", 50), ("max", 95), ("step", 5)))
    G_i_decay = J.get(G_input, "number")("Accumulator Decay Factor", 0.85, J.obj(("min", 0.5), ("max", 0.98), ("step", 0.01)))
    G_i_normWindow = J.get(G_input, "number")("Normalization Window", 100, J.obj(("min", 50), ("max", 300), ("step", 25)))
    G_i_cooldown = J.get(G_input, "number")("Signal Cooldown (Bars)", 5, J.obj(("min", 1), ("max", 50), ("step", 1)))
    G_i_deltaBlend = J.get(G_input, "number")("Delta Blend Factor", 0.4, J.obj(("min", 0), ("max", 1), ("step", 0.05)))
    G_i_wickSmoothing = J.get(G_input, "number")("Pressure Smoothing", 3, J.obj(("min", 1), ("max", 10), ("step", 1)))
    G_i_wickThresh = J.get(G_input, "number")("Wick Signal Threshold", 0.15, J.obj(("min", 0.05), ("max", 0.5), ("step", 0.05)))
    G_i_targetATR = J.get(G_input, "number")("Target ATR Multiple", 2.5, J.obj(("min", 0.5), ("max", 6), ("step", 0.25)))
    G_i_stopATR = J.get(G_input, "number")("Stop ATR Multiple", 1.5, J.obj(("min", 0.5), ("max", 4), ("step", 0.25)))
    G_i_trailATR = J.get(G_input, "number")("Trailing Stop ATR", 1.2, J.obj(("min", 0.3), ("max", 3), ("step", 0.1)))
    G_i_trailActivate = J.get(G_input, "number")("Trail Activation", 0.5, J.obj(("min", 0.2), ("max", 0.9), ("step", 0.1)))
    G_i_dash = J.get(G_input, "select")("Dashboard Mode", "Full", J.JSArray(["Off", "Compact", "Full"]))
    G_i_theme = J.get(G_input, "select")("Theme Select", "Neon", J.JSArray(["Neon", "Cyber", "Matrix", "Gold", "Ice", "Blood", "DAFE Signature", "Clean"]))
    G_TH = (J.obj(("bull", "#00FFA3"), ("bear", "#FF00FF"), ("neu", "#94A3B8"), ("a1", "#00D9FF"), ("a2", "#FF00FF"), ("bg", "#070B16"), ("panel", "#0F172A"), ("txt", "#F8FAFC"), ("dim", "#64748B"), ("border", "#1E293B")) if J.seq(G_i_theme, "Cyber") else (J.obj(("bull", "#00FF00"), ("bear", "#003300"), ("neu", "#4AF2A1"), ("a1", "#00FF66"), ("a2", "#33CC33"), ("bg", "#020202"), ("panel", "#0A0A0A"), ("txt", "#E0E0E0"), ("dim", "#555555"), ("border", "#111111")) if J.seq(G_i_theme, "Matrix") else (J.obj(("bull", "#FFD700"), ("bear", "#8B6508"), ("neu", "#E5C158"), ("a1", "#FFC125"), ("a2", "#FFD700"), ("bg", "#110F0A"), ("panel", "#1C1912"), ("txt", "#FFF8DC"), ("dim", "#8B864E"), ("border", "#2B271A")) if J.seq(G_i_theme, "Gold") else (J.obj(("bull", "#E0FFFF"), ("bear", "#4682B4"), ("neu", "#B0E0E6"), ("a1", "#87CEFA"), ("a2", "#ADD8E6"), ("bg", "#0B131A"), ("panel", "#121E2A"), ("txt", "#F0F8FF"), ("dim", "#708090"), ("border", "#1F3247")) if J.seq(G_i_theme, "Ice") else (J.obj(("bull", "#FF3333"), ("bear", "#550000"), ("neu", "#CD5C5C"), ("a1", "#FF6666"), ("a2", "#8B0000"), ("bg", "#140505"), ("panel", "#200B0B"), ("txt", "#FAFAFA"), ("dim", "#805F5F"), ("border", "#3B1A1A")) if J.seq(G_i_theme, "Blood") else (J.obj(("bull", "#00E5A0"), ("bear", "#FF2D6A"), ("neu", "#94A3B8"), ("a1", "#00BFFF"), ("a2", "#A855F7"), ("bg", "#0B1020"), ("panel", "#111827"), ("txt", "#E5E7EB"), ("dim", "#6B7280"), ("border", "#243041")) if J.seq(G_i_theme, "DAFE Signature") else (J.obj(("bull", "#4CAF50"), ("bear", "#F44336"), ("neu", "#9E9E9E"), ("a1", "#2196F3"), ("a2", "#9C27B0"), ("bg", "#FFFFFF"), ("panel", "#F5F5F5"), ("txt", "#212121"), ("dim", "#757575"), ("border", "#E0E0E0")) if J.seq(G_i_theme, "Clean") else J.obj(("bull", "#00FFCC"), ("bear", "#FF00AA"), ("neu", "#94A3B8"), ("a1", "#00D9FF"), ("a2", "#FF00FF"), ("bg", "#070B16"), ("panel", "#0F172A"), ("txt", "#F8FAFC"), ("dim", "#64748B"), ("border", "#1E293B")))))))))
    G_tiny = G_library("tinycolor2")
    G_EPS = 1.0e-10
    G_n = J.get(G_close, "length")
    G_lastIdx = J.sub(G_n, 1)
    G_sCut = J.sub(G_n, 1)
    G_atr14 = G_atr(14)
    G_volMA = G_sma(G_volume, 20)
    G_rsiSeries = calculateRSI(14)
    G_mfiSeries = calculateMFI(14)
    G_obvSeries = make(G_n, 0)
    i = 1
    while J.lt(i, G_n):
        J.set(G_obvSeries, i, J.add(J.get(G_obvSeries, J.sub(i, 1)), (J.get(G_volume, i) if J.gt(J.get(G_close, i), J.get(G_close, J.sub(i, 1))) else (J.neg(J.get(G_volume, i)) if J.lt(J.get(G_close, i), J.get(G_close, J.sub(i, 1))) else 0))))
        i = J.inc(i)
    G_cvdSeries = make(G_n, 0)
    i = 1
    while J.lt(i, G_n):
        J.set(G_cvdSeries, i, J.add(J.get(G_cvdSeries, J.sub(i, 1)), proxyDelta(i)))
        i = J.inc(i)
    G_rawWickPressure = make(G_n, 0)
    i = 0
    while J.lt(i, G_n):
        G_rng = J.sub(J.get(G_high, i), J.get(G_low, i))
        if J.gt(G_rng, G_EPS):
            G_upWick = J.sub(J.get(G_high, i), J.get(G_Math, "max")(J.get(G_open, i), J.get(G_close, i)))
            G_dnWick = J.sub(J.get(G_Math, "min")(J.get(G_open, i), J.get(G_close, i)), J.get(G_low, i))
            J.set(G_rawWickPressure, i, J.div(J.sub(G_dnWick, G_upWick), G_rng))
        i = J.inc(i)
    G_smoothWickPressure = G_ema(G_rawWickPressure, G_i_wickSmoothing)
    G_volQuality = make(G_n, 0.5)
    G_absorption = make(G_n, 0)
    G_unifiedAgg = make(G_n, 0.5)
    i = 0
    while J.lt(i, G_n):
        G_v_ma = nz(J.get(G_volMA, i), J.get(G_volume, i))
        J.set(G_volQuality, i, (J.div(clamp(J.div(J.get(G_volume, i), G_v_ma), 0.1, 2), 2) if J.gt(G_v_ma, 0) else 0.5))
        G_rng = J.sub(J.get(G_high, i), J.get(G_low, i))
        G_atrVal = nz(J.get(G_atr14, i), 1)
        J.set(G_absorption, i, (1 if (J.gt(J.get(G_volume, i), J.mul(G_v_ma, 1.5)) and J.lt(G_rng, J.mul(G_atrVal, 0.5))) else 0))
        J.set(G_unifiedAgg, i, (J.div(J.sub(J.get(G_close, i), J.get(G_low, i)), G_rng) if J.gt(G_rng, 0) else 0.5))
        i = J.inc(i)
    G_rawBullDiv = make(G_n, 0)
    G_rawBearDiv = make(G_n, 0)
    i = 1
    while J.lt(i, G_n):
        G_dClose = J.sub(J.get(G_close, i), J.get(G_close, J.sub(i, 1)))
        G_dRSI = J.sub(J.get(G_rsiSeries, i), J.get(G_rsiSeries, J.sub(i, 1)))
        G_dMFI = J.sub(J.get(G_mfiSeries, i), J.get(G_mfiSeries, J.sub(i, 1)))
        G_dOBV = J.sub(J.get(G_obvSeries, i), J.get(G_obvSeries, J.sub(i, 1)))
        G_dCVD = J.sub(J.get(G_cvdSeries, i), J.get(G_cvdSeries, J.sub(i, 1)))
        bullImp = 0
        bearImp = 0
        if J.lt(G_dClose, 0):
            if J.gt(G_dRSI, 0):
                bullImp = J.add(bullImp, 1)
            if J.gt(G_dMFI, 0):
                bullImp = J.add(bullImp, 1)
            if J.gt(G_dOBV, 0):
                bullImp = J.add(bullImp, 1)
            if J.gt(G_dCVD, 0):
                bullImp = J.add(bullImp, 1)
        elif J.gt(G_dClose, 0):
            if J.lt(G_dRSI, 0):
                bearImp = J.add(bearImp, 1)
            if J.lt(G_dMFI, 0):
                bearImp = J.add(bearImp, 1)
            if J.lt(G_dOBV, 0):
                bearImp = J.add(bearImp, 1)
            if J.lt(G_dCVD, 0):
                bearImp = J.add(bearImp, 1)
        G_swp = (_t1 if J.truthy(_t1 := J.get(G_smoothWickPressure, i)) else 0)
        if J.gt(G_swp, G_i_wickThresh):
            bullImp = J.add(bullImp, J.mul(G_swp, 0.5))
        if J.lt(G_swp, J.neg(G_i_wickThresh)):
            bearImp = J.add(bearImp, J.mul(J.get(G_Math, "abs")(G_swp), 0.5))
        J.set(G_rawBullDiv, i, J.add(J.mul(J.get(G_rawBullDiv, J.sub(i, 1)), G_i_decay), bullImp))
        J.set(G_rawBearDiv, i, J.add(J.mul(J.get(G_rawBearDiv, J.sub(i, 1)), G_i_decay), bearImp))
        i = J.inc(i)
    G_bullPressure = make(G_n, 0)
    G_bearPressure = make(G_n, 0)
    i = 0
    while J.lt(i, G_n):
        G_wb = windowSlice(G_rawBullDiv, i, G_i_normWindow)
        G_wr = windowSlice(G_rawBearDiv, i, G_i_normWindow)
        G_maxB = J.get(J.get(G_Math, "max"), "apply")(None, G_wb)
        G_maxR = J.get(J.get(G_Math, "max"), "apply")(None, G_wr)
        J.set(G_bullPressure, i, (J.mul(J.div(J.get(G_rawBullDiv, i), G_maxB), 100) if J.gt(G_maxB, G_EPS) else 0))
        J.set(G_bearPressure, i, (J.mul(J.div(J.get(G_rawBearDiv, i), G_maxR), 100) if J.gt(G_maxR, G_EPS) else 0))
        i = J.inc(i)
    G_signalBull = make(G_n, False)
    G_signalBear = make(G_n, False)
    G_confidence = make(G_n, 0)
    lastSignalBar = (-9999)
    i = 1
    while J.lt(i, G_n):
        G_cooldownClear = J.ge(J.sub(i, lastSignalBar), G_i_cooldown)
        G_bPress = J.get(G_bullPressure, i)
        G_rPress = J.get(G_bearPressure, i)
        if ((J.gt(G_bPress, G_i_pressureTh) and J.gt(G_bPress, G_rPress)) and J.truthy(G_cooldownClear)):
            J.set(G_signalBull, i, True)
            J.set(G_confidence, i, G_bPress)
            lastSignalBar = i
        elif ((J.gt(G_rPress, G_i_pressureTh) and J.gt(G_rPress, G_bPress)) and J.truthy(G_cooldownClear)):
            J.set(G_signalBear, i, True)
            J.set(G_confidence, i, G_rPress)
            lastSignalBar = i
        i = J.inc(i)
    totalTrades = 0
    winTrades = 0
    totalPnl = 0
    grossProfit = 0
    grossLoss = 0
    peakEquity = 0
    maxDD = 0
    pos = 0
    entryPrice = None
    targetPrice = None
    stopPrice = None
    trailBest = None
    trailActive = False
    i = G_i_normWindow
    while J.lt(i, G_n):
        G_atrNow = nz(J.get(G_atr14, i), J.get(G_atr14, G_lastIdx))
        if J.sne(pos, 0):
            shouldExit = False
            exitPrice = J.get(G_close, i)
            if J.seq(pos, 1):
                if J.ge(J.get(G_high, i), targetPrice):
                    shouldExit = True
                    exitPrice = targetPrice
                elif J.le(J.get(G_low, i), stopPrice):
                    shouldExit = True
                    exitPrice = stopPrice
                else:
                    trailBest = J.get(G_Math, "max")(trailBest, J.get(G_high, i))
                    G_activationLevel = J.add(entryPrice, J.mul(J.sub(targetPrice, entryPrice), G_i_trailActivate))
                    if J.ge(trailBest, G_activationLevel):
                        trailActive = True
                    if J.truthy(trailActive):
                        G_trailStop = J.sub(trailBest, J.mul(G_atrNow, G_i_trailATR))
                        if J.le(J.get(G_low, i), G_trailStop):
                            shouldExit = True
                            exitPrice = J.get(G_Math, "max")(J.get(G_low, i), G_trailStop)
                    if J.truthy(J.get(G_signalBear, i)):
                        shouldExit = True
            elif J.seq(pos, (-1)):
                if J.le(J.get(G_low, i), targetPrice):
                    shouldExit = True
                    exitPrice = targetPrice
                elif J.ge(J.get(G_high, i), stopPrice):
                    shouldExit = True
                    exitPrice = stopPrice
                else:
                    trailBest = J.get(G_Math, "min")(trailBest, J.get(G_low, i))
                    G_activationLevel = J.sub(entryPrice, J.mul(J.sub(entryPrice, targetPrice), G_i_trailActivate))
                    if J.le(trailBest, G_activationLevel):
                        trailActive = True
                    if J.truthy(trailActive):
                        G_trailStop = J.add(trailBest, J.mul(G_atrNow, G_i_trailATR))
                        if J.ge(J.get(G_high, i), G_trailStop):
                            shouldExit = True
                            exitPrice = J.get(G_Math, "min")(J.get(G_high, i), G_trailStop)
                    if J.truthy(J.get(G_signalBull, i)):
                        shouldExit = True
            if J.truthy(shouldExit):
                G_tradePnl = (J.mul(J.div(J.sub(exitPrice, entryPrice), entryPrice), 100) if J.seq(pos, 1) else J.mul(J.div(J.sub(entryPrice, exitPrice), entryPrice), 100))
                totalTrades = J.inc(totalTrades)
                if J.gt(G_tradePnl, 0):
                    winTrades = J.inc(winTrades)
                    grossProfit = J.add(grossProfit, G_tradePnl)
                else:
                    grossLoss = J.add(grossLoss, J.get(G_Math, "abs")(G_tradePnl))
                totalPnl = J.add(totalPnl, G_tradePnl)
                peakEquity = J.get(G_Math, "max")(peakEquity, totalPnl)
                maxDD = J.get(G_Math, "max")(maxDD, J.sub(peakEquity, totalPnl))
                pos = 0
                entryPrice = None
                targetPrice = None
                stopPrice = None
                trailBest = None
                trailActive = False
        if J.seq(pos, 0):
            if J.truthy(J.get(G_signalBull, i)):
                pos = 1
                entryPrice = J.get(G_close, i)
                targetPrice = J.add(J.get(G_close, i), J.mul(G_atrNow, G_i_targetATR))
                stopPrice = J.sub(J.get(G_close, i), J.mul(G_atrNow, G_i_stopATR))
                trailBest = J.get(G_high, i)
                trailActive = False
            elif J.truthy(J.get(G_signalBear, i)):
                pos = (-1)
                entryPrice = J.get(G_close, i)
                targetPrice = J.sub(J.get(G_close, i), J.mul(G_atrNow, G_i_targetATR))
                stopPrice = J.add(J.get(G_close, i), J.mul(G_atrNow, G_i_stopATR))
                trailBest = J.get(G_low, i)
                trailActive = False
        i = J.inc(i)
    G_winRate = (J.mul(J.div(winTrades, totalTrades), 100) if J.gt(totalTrades, 0) else 0)
    G_profitFactor = (J.div(grossProfit, grossLoss) if J.gt(grossLoss, 0) else (99.9 if J.gt(grossProfit, 0) else 0))
    G_expectancy = (J.div(totalPnl, totalTrades) if J.gt(totalTrades, 0) else 0)
    G_bullBubsCore = make(G_n, None)
    G_bearBubsCore = make(G_n, None)
    G_bullBubsGlow = make(G_n, None)
    G_bearBubsGlow = make(G_n, None)
    i = 0
    while J.lt(i, G_n):
        G_atrNow = nz(J.get(G_atr14, i), J.get(G_atr14, G_lastIdx))
        if J.truthy(J.get(G_signalBull, i)):
            G_bullOffset = J.sub(J.get(G_low, i), J.mul(G_atrNow, 1.8))
            J.set(G_bullBubsCore, i, J.obj(("y", G_bullOffset), ("z", J.get(G_Math, "round")(J.get(G_confidence, i)))))
            J.set(G_bullBubsGlow, i, J.obj(("y", G_bullOffset), ("z", J.get(G_Math, "round")(J.get(G_confidence, i)))))
        if J.truthy(J.get(G_signalBear, i)):
            G_bearOffset = J.add(J.get(G_high, i), J.mul(G_atrNow, 1.8))
            J.set(G_bearBubsCore, i, J.obj(("y", G_bearOffset), ("z", J.get(G_Math, "round")(J.get(G_confidence, i)))))
            J.set(G_bearBubsGlow, i, J.obj(("y", G_bearOffset), ("z", J.get(G_Math, "round")(J.get(G_confidence, i)))))
        i = J.inc(i)
    G_bullColorSeries = G_series_of(J.get(G_TH, "bull"))
    G_bearColorSeries = G_series_of(J.get(G_TH, "bear"))
    G_bullGlowColorSeries = G_series_of(rgba(J.get(G_TH, "bull"), 0.15))
    G_bearGlowColorSeries = G_series_of(rgba(J.get(G_TH, "bear"), 0.15))
    G_paint(G_bullBubsGlow, J.obj(("style", "bubble"), ("color", G_bullGlowColorSeries), ("min_radius", 20), ("max_radius", 70), ("labels", False), ("name", "Bull Glowing Aura"), ("order", "below_all")))
    G_paint(G_bearBubsGlow, J.obj(("style", "bubble"), ("color", G_bearGlowColorSeries), ("min_radius", 20), ("max_radius", 70), ("labels", False), ("name", "Bear Glowing Aura"), ("order", "below_all")))
    G_paint(G_bullBubsCore, J.obj(("style", "bubble"), ("color", G_bullColorSeries), ("min_radius", 12), ("max_radius", 36), ("labels", True), ("name", "Bull Divergence Orb"), ("order", "below_all")))
    G_paint(G_bearBubsCore, J.obj(("style", "bubble"), ("color", G_bearColorSeries), ("min_radius", 12), ("max_radius", 36), ("labels", True), ("name", "Bear Divergence Orb"), ("order", "below_all")))
    G_isChoppy = J.lt((_t2 if J.truthy(_t2 := hurstExp(G_lastIdx, 30)) else 0.5), 0.45)
    G_narrLines = J.JSArray([])
    G_narrCols = J.JSArray([])
    if J.ge(totalTrades, 3):
        if J.lt(G_winRate, 45):
            J.get(G_narrLines, "push")("WR Low: Tighten Threshold")
            J.get(G_narrCols, "push")(J.get(G_TH, "bear"))
        elif J.gt(G_winRate, 62):
            J.get(G_narrLines, "push")("Strong WR: Expand Target ATR")
            J.get(G_narrCols, "push")(J.get(G_TH, "bull"))
        if J.lt(G_profitFactor, 1):
            J.get(G_narrLines, "push")("PF Negative: Narrow Stop ATR")
            J.get(G_narrCols, "push")(J.get(G_TH, "bear"))
    G_lastHurst = hurstExp(G_lastIdx, 30)
    if J.lt(G_lastHurst, 0.45):
        J.get(G_narrLines, "push")("Chop Detected: Standard Risk")
        J.get(G_narrCols, "push")(J.get(G_TH, "neu"))
    elif J.gt(G_lastHurst, 0.65):
        J.get(G_narrLines, "push")("Sustained Trend: Trail Active")
        J.get(G_narrCols, "push")(J.get(G_TH, "bull"))
    G_wpLast = (_t3 if J.truthy(_t3 := J.get(G_smoothWickPressure, G_lastIdx)) else 0)
    if J.gt(J.get(G_Math, "abs")(G_wpLast), J.mul(G_i_wickThresh, 1.5)):
        J.get(G_narrLines, "push")("Heavy Wick Pressure Active")
        J.get(G_narrCols, "push")(J.get(G_TH, "a1"))
    if J.seq(J.get(G_narrLines, "length"), 0):
        J.get(G_narrLines, "push")("Confluence Aligned & Scanning")
        J.get(G_narrCols, "push")(J.get(G_TH, "neutral"))
    G_dashRows = J.JSArray([])
    if J.sne(G_i_dash, "Off"):
        J.get(G_dashRows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", "\ud83c\udf0c AURORA DIVERGENCE"), ("color", "#FFFFFF"), ("background", rgba(J.get(G_TH, "a2"), 0.25)), ("textAlign", "center"), ("fontSize", 10.5), ("fontWeight", "bold"), ("colspan", 4))]))))
        G_tfVal = (G_period if J.sne("undefined", "undefined") else (J.get(G_constants, "interval") if J.truthy(J.get(G_constants, "interval")) else "Chart"))
        G_tickerText = J.add(J.add(J.add(J.add(" ", (_t4 if J.truthy(_t4 := J.get(G_constants, "ticker")) else "—")), "  •  "), G_tfVal), "  •  ")
        J.get(G_dashRows, "push")(J.obj(("cells", J.JSArray([mkCell(G_tickerText, J.get(G_TH, "txt"), "left", True, 2), J.obj(("text", "● LIVE"), ("color", J.get(G_TH, "bull")), ("background", rgba(J.get(G_TH, "bull"), 0.12)), ("textAlign", "center"), ("fontSize", 9), ("fontWeight", "bold"), ("colspan", 2))]))))
        J.get(G_dashRows, "push")(J.obj(("cells", J.JSArray([mkSub("── DIVERGENCE ENGINE ──")]))))
        G_bPressNow = (_t5 if J.truthy(_t5 := J.get(G_bullPressure, G_lastIdx)) else 0)
        G_rPressNow = (_t6 if J.truthy(_t6 := J.get(G_bearPressure, G_lastIdx)) else 0)
        G_trendText = ("▲ UP" if J.gt(G_bPressNow, G_rPressNow) else ("▼ DN" if J.gt(G_rPressNow, G_bPressNow) else "─ NEU"))
        G_trendColor = (J.get(G_TH, "bull") if J.gt(G_bPressNow, G_rPressNow) else (J.get(G_TH, "bear") if J.gt(G_rPressNow, G_bPressNow) else J.get(G_TH, "neu")))
        G_flowText = ("▲ BUY" if J.gt(G_bPressNow, G_rPressNow) else ("▼ SELL" if J.gt(G_rPressNow, G_bPressNow) else "─ NEU"))
        G_flowColor = (J.get(G_TH, "bull") if J.gt(G_bPressNow, G_rPressNow) else (J.get(G_TH, "bear") if J.gt(G_rPressNow, G_bPressNow) else J.get(G_TH, "neu")))
        J.get(G_dashRows, "push")(J.obj(("cells", J.JSArray([mkCell("Trend", J.get(G_TH, "dim"), "left", False, 1), mkCell(G_trendText, G_trendColor, "left", True, 1), mkCell("Flow", J.get(G_TH, "dim"), "right", False, 1), mkCell(G_flowText, G_flowColor, "right", True, 1)]))))
        G_hasBullSig = J.get(G_signalBull, G_lastIdx)
        G_hasBearSig = J.get(G_signalBear, G_lastIdx)
        G_sigText = ("BULL DIV" if J.truthy(G_hasBullSig) else ("BEAR DIV" if J.truthy(G_hasBearSig) else "Scanning"))
        G_sigColor = (J.get(G_TH, "bull") if J.truthy(G_hasBullSig) else (J.get(G_TH, "bear") if J.truthy(G_hasBearSig) else J.get(G_TH, "neu")))
        G_confVal = (_t7 if J.truthy(_t7 := J.get(G_confidence, G_lastIdx)) else 0)
        J.get(G_dashRows, "push")(J.obj(("cells", J.JSArray([mkCell("Signal", J.get(G_TH, "dim"), "left", False, 1), mkCell(G_sigText, G_sigColor, "left", True, 1), mkCell("Power", J.get(G_TH, "dim"), "right", False, 1), mkCell(J.add(fmt(G_confVal), "%"), G_sigColor, "right", True, 1)]))))
        J.get(G_dashRows, "push")(J.obj(("cells", J.JSArray([mkSub("── MICROSTRUCTURE ──")]))))
        G_wp = (_t8 if J.truthy(_t8 := J.get(G_smoothWickPressure, G_lastIdx)) else 0)
        G_wpCol = (J.get(G_TH, "bull") if J.gt(G_wp, G_i_wickThresh) else (J.get(G_TH, "bear") if J.lt(G_wp, J.neg(G_i_wickThresh)) else J.get(G_TH, "neu")))
        G_vqVal = (_t9 if J.truthy(_t9 := J.get(G_volQuality, G_lastIdx)) else 0.5)
        G_vqText = ("HIGH" if J.gt(G_vqVal, 0.7) else ("MED" if J.gt(G_vqVal, 0.4) else "LOW"))
        G_vqCol = (J.get(G_TH, "bull") if J.gt(G_vqVal, 0.7) else (J.get(G_TH, "a1") if J.gt(G_vqVal, 0.4) else J.get(G_TH, "bear")))
        J.get(G_dashRows, "push")(J.obj(("cells", J.JSArray([mkCell("Wick P.", J.get(G_TH, "dim"), "left", False, 1), mkCell(fmt(G_wp), G_wpCol, "left", True, 1), mkCell("Vol. Q", J.get(G_TH, "dim"), "right", False, 1), mkCell(G_vqText, G_vqCol, "right", True, 1)]))))
        G_absVal = (_t10 if J.truthy(_t10 := J.get(G_absorption, G_lastIdx)) else 0)
        G_absText = ("ABSORB" if J.gt(G_absVal, 0.5) else "NORMAL")
        G_absCol = (J.get(G_TH, "a1") if J.gt(G_absVal, 0.5) else J.get(G_TH, "dim"))
        G_aggVal = (_t11 if J.truthy(_t11 := J.get(G_unifiedAgg, G_lastIdx)) else 0.5)
        G_aggText = ("BUYERS" if J.gt(G_aggVal, 0.6) else ("SELLERS" if J.lt(G_aggVal, 0.4) else "BALANCED"))
        G_aggCol = (J.get(G_TH, "bull") if J.gt(G_aggVal, 0.6) else (J.get(G_TH, "bear") if J.lt(G_aggVal, 0.4) else J.get(G_TH, "neu")))
        J.get(G_dashRows, "push")(J.obj(("cells", J.JSArray([mkCell("Absorb", J.get(G_TH, "dim"), "left", False, 1), mkCell(G_absText, G_absCol, "left", True, 1), mkCell("Aggress.", J.get(G_TH, "dim"), "right", False, 1), mkCell(G_aggText, G_aggCol, "right", True, 1)]))))
        G_lastCd = J.sub(G_lastIdx, lastSignalBar)
        G_isCdClear = J.ge(G_lastCd, G_i_cooldown)
        G_cdText = ("✓ Ready" if J.truthy(G_isCdClear) else J.add(J.sub(G_i_cooldown, G_lastCd), " Bars"))
        G_cdCol = (J.get(G_TH, "bull") if J.truthy(G_isCdClear) else J.get(G_TH, "bear"))
        J.get(G_dashRows, "push")(J.obj(("cells", J.JSArray([mkCell("Cooldown", J.get(G_TH, "dim"), "left", False, 2), mkCell(G_cdText, G_cdCol, "right", True, 2)]))))
        if J.seq(G_i_dash, "Full"):
            J.get(G_dashRows, "push")(J.obj(("cells", J.JSArray([mkSub("── PERFORMANCE STRATEGY ──")]))))
            J.get(G_dashRows, "push")(J.obj(("cells", J.JSArray([mkCell("Trades", J.get(G_TH, "dim"), "left", False, 1), mkCell(G_String(totalTrades), J.get(G_TH, "txt"), "left", True, 1), mkCell("Win %", J.get(G_TH, "dim"), "right", False, 1), mkCell(J.add(fmt(G_winRate), "%"), (J.get(G_TH, "bull") if J.ge(G_winRate, 50) else J.get(G_TH, "bear")), "right", True, 1)]))))
            G_pnlCol = (J.get(G_TH, "bull") if J.ge(totalPnl, 0) else J.get(G_TH, "bear"))
            J.get(G_dashRows, "push")(J.obj(("cells", J.JSArray([mkCell("Net PnL", J.get(G_TH, "dim"), "left", False, 1), mkCell(J.add(fmt(totalPnl), "%"), G_pnlCol, "left", True, 1), mkCell("P. Factor", J.get(G_TH, "dim"), "right", False, 1), mkCell(fmt(G_profitFactor), (J.get(G_TH, "bull") if J.ge(G_profitFactor, 1) else J.get(G_TH, "bear")), "right", True, 1)]))))
            J.get(G_dashRows, "push")(J.obj(("cells", J.JSArray([mkCell("Max DD", J.get(G_TH, "dim"), "left", False, 1), mkCell(J.add(fmt(maxDD), "%"), J.get(G_TH, "bear"), "left", True, 1), mkCell("Expect.", J.get(G_TH, "dim"), "right", False, 1), mkCell(J.add(fmt(G_expectancy), "%"), (J.get(G_TH, "bull") if J.ge(G_expectancy, 0) else J.get(G_TH, "bear")), "right", True, 1)]))))
            G_posText = ("○ Flat" if J.seq(pos, 0) else (J.add("◐ Long", (" [Locked]" if J.truthy(trailActive) else "")) if J.seq(pos, 1) else J.add("◐ Short", (" [Locked]" if J.truthy(trailActive) else ""))))
            G_posColor = (J.get(G_TH, "dim") if J.seq(pos, 0) else (J.get(G_TH, "bull") if J.seq(pos, 1) else J.get(G_TH, "bear")))
            J.get(G_dashRows, "push")(J.obj(("cells", J.JSArray([mkCell("Position", J.get(G_TH, "dim"), "left", False, 2), mkCell(G_posText, G_posColor, "right", True, 2)]))))
            J.get(G_dashRows, "push")(J.obj(("cells", J.JSArray([mkSub("── COGNITIVE ADVISORY ──")]))))
            k = 0
            while J.lt(k, J.get(G_Math, "min")(J.get(G_narrLines, "length"), 3)):
                J.get(G_dashRows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", J.add("• ", J.get(G_narrLines, k))), ("color", J.get(G_narrCols, k)), ("background", J.get(G_TH, "panel")), ("textAlign", "left"), ("fontSize", 9), ("colspan", 4))]))))
                k = J.inc(k)
        G_statusText = ("⚡ ACTIVE: BULLISH TRIGGER" if J.truthy(G_hasBullSig) else ("⚡ ACTIVE: BEARISH TRIGGER" if J.truthy(G_hasBearSig) else ("⚠ WARNING: CHOP DETECTED" if J.truthy(G_isChoppy) else "○ SCANNING DIVERGENCES")))
        G_statusBg = (rgba(J.get(G_TH, "bull"), 0.2) if J.truthy(G_hasBullSig) else (rgba(J.get(G_TH, "bear"), 0.2) if J.truthy(G_hasBearSig) else (rgba(J.get(G_TH, "bear"), 0.1) if J.truthy(G_isChoppy) else rgba(J.get(G_TH, "panel"), 0.5))))
        G_statusCol = (J.get(G_TH, "bull") if J.truthy(G_hasBullSig) else (J.get(G_TH, "bear") if J.truthy(G_hasBearSig) else (J.get(G_TH, "bear") if J.truthy(G_isChoppy) else J.get(G_TH, "dim"))))
        J.get(G_dashRows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", G_statusText), ("background", G_statusBg), ("color", G_statusCol), ("colspan", 4), ("textAlign", "center"), ("fontSize", 9.5), ("fontWeight", "bold"))]))))
        J.get(G_dashRows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", "⟡ DAFE QUANT AURORA SYSTEMS"), ("color", rgba("#FFFFFF", 0.8)), ("background", rgba(J.get(G_TH, "a2"), 0.18)), ("textAlign", "center"), ("fontSize", 9), ("fontWeight", "bold"), ("colspan", 4))]))))
    G_dashVisible = J.sne(G_i_dash, "Off")
    G_paint_overlay("Aurora Divergence", J.obj(("position", "top_right"), ("order", "above_all")), J.obj(("background", (rgba(J.get(G_TH, "bg"), 0.98) if J.truthy(G_dashVisible) else "transparent")), ("border", (J.add("1px solid ", J.get(G_TH, "border")) if J.truthy(G_dashVisible) else "none")), ("borderRadius", (6 if J.truthy(G_dashVisible) else 0)), ("width", (200 if J.truthy(G_dashVisible) else 0)), ("rows", (G_dashRows if J.truthy(G_dashVisible) else J.JSArray([])))))
    G_register_signal(G_signalBull, "Aurora Bull Divergence")
    G_register_signal(G_signalBear, "Aurora Bear Divergence")


register_store_indicator(
    script,
    name='aurora_divergence_dafe_TS',
    title='Aurora Divergence [DAFE]',
    developer='DskyzInvestments',
    url='https://trendspider.com/trading-tools-store/indicators/6a272e-aurora-divergence-dafe/',
    position='price',
    inputs=[{'id': 'divergence_threshold__', 'title': 'Divergence Threshold %', 'type': 'number', 'default': 80}, {'id': 'accumulator_decay_factor', 'title': 'Accumulator Decay Factor', 'type': 'number', 'default': 0.85}, {'id': 'normalization_window', 'title': 'Normalization Window', 'type': 'number', 'default': 100}, {'id': 'signal_cooldown__bars_', 'title': 'Signal Cooldown (Bars)', 'type': 'number', 'default': 5}, {'id': 'delta_blend_factor', 'title': 'Delta Blend Factor', 'type': 'number', 'default': 0.4}, {'id': 'pressure_smoothing', 'title': 'Pressure Smoothing', 'type': 'number', 'default': 3}, {'id': 'wick_signal_threshold', 'title': 'Wick Signal Threshold', 'type': 'number', 'default': 0.15}, {'id': 'target_atr_multiple', 'title': 'Target ATR Multiple', 'type': 'number', 'default': 2.5}, {'id': 'stop_atr_multiple', 'title': 'Stop ATR Multiple', 'type': 'number', 'default': 1.5}, {'id': 'trailing_stop_atr', 'title': 'Trailing Stop ATR', 'type': 'number', 'default': 1.2}, {'id': 'trail_activation', 'title': 'Trail Activation', 'type': 'number', 'default': 0.5}, {'id': 'dashboard_mode', 'title': 'Dashboard Mode', 'type': 'select_wide', 'default': 'Full', 'options': ['Off', 'Compact', 'Full']}, {'id': 'theme_select', 'title': 'Theme Select', 'type': 'select_wide', 'default': 'Neon', 'options': ['Neon', 'Cyber', 'Matrix', 'Gold', 'Ice', 'Blood', 'DAFE Signature', 'Clean']}],
    outputs=['bull_glowing_aura', 'bear_glowing_aura', 'bull_divergence_orb', 'bear_divergence_orb', 'aurora_bull_divergence', 'aurora_bear_divergence'],
    signals=['aurora_bull_divergence', 'aurora_bear_divergence'],
    requires=[],
    parity='exact',
)
