"""
VECTR -- TrendSpider store indicator by Gustivus.

Registered as "vectr_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6aa0f7-vectr/)
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
    G_Number = G["Number"]
    G_Object = G["Object"]
    G_String = G["String"]
    G_assert = G["assert"]
    G_atr = G["atr"]
    G_close = G["close"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_ema = G["ema"]
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_horizontal_line = G["horizontal_line"]
    G_input = G["input"]
    G_low = G["low"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_request = G["request"]
    G_rsi = G["rsi"]
    G_series_of = G["series_of"]
    G_sma = G["sma"]
    G_stdev = G["stdev"]
    G_time = G["time"]
    G_volume = G["volume"]
    G_wildma = G["wildma"]
    G_wma = G["wma"]
    def monthIndex(days=J.undefined, *_args):
        z = J.add(days, 719468)
        era = J.get(G_Math, "floor")(J.div(z, 146097))
        doe = J.sub(z, J.mul(era, 146097))
        yoe = J.get(G_Math, "floor")(J.div(J.sub(J.add(J.sub(doe, J.get(G_Math, "floor")(J.div(doe, 1460))), J.get(G_Math, "floor")(J.div(doe, 36524))), J.get(G_Math, "floor")(J.div(doe, 146096))), 365))
        doy = J.sub(doe, J.sub(J.add(J.mul(365, yoe), J.get(G_Math, "floor")(J.div(yoe, 4))), J.get(G_Math, "floor")(J.div(yoe, 100))))
        mp = J.get(G_Math, "floor")(J.div(J.add(J.mul(5, doy), 2), 153))
        m = (J.add(mp, 3) if J.lt(mp, 10) else J.sub(mp, 9))
        y = J.add(J.add(yoe, J.mul(era, 400)), (1 if J.le(m, 2) else 0))
        return J.add(J.mul(y, 12), J.sub(m, 1))
    G_describe_indicator("VECTR", "lower")
    L = J.get(G_input, "number")("Kinematic Window (L)", 10, J.obj(("min", 4), ("max", 60)))
    N = J.get(G_input, "number")("Normalization Window (N)", 100, J.obj(("min", 30), ("max", 500)))
    enhance = J.get(G_input, "number")("Enhancement Strength", 1, J.obj(("min", 0), ("max", 1)))
    fadeThresh = J.get(G_input, "number")("Fade Threshold (|accel|)", 1, J.obj(("min", 0.1), ("max", 5)))
    velDirWeight = J.get(G_input, "number")("Velocity Direction Weight", 0, J.obj(("min", 0), ("max", 100)))
    mapping = G_input("Strength Mapping", "percentile", J.JSArray(["percentile", "z-linear"]))
    benchSel = J.get(G_input, "select")("Benchmark", "auto", J.JSArray(["auto", "SPY", "QQQ", "RSP", "SMH", "SOXX", "XSD", "IGV", "WCLD", "XLK", "XLC", "XLF", "KBE", "KRE", "KIE", "XLV", "XBI", "IHI", "XLE", "XOP", "XLI", "ITA", "XLY", "XRT", "XLP", "XLU", "XLRE", "XLB"]))
    relSmooth = J.get(G_input, "number")("Relative Extension Smoothing", 1, J.obj(("min", 1), ("max", 20)))
    INDUSTRY_ETF = J.JSArray([J.JSArray(["reit", "XLRE"]), J.JSArray(["realestate", "XLRE"]), J.JSArray(["semiconductorequipment", "SMH"]), J.JSArray(["semiconductor", "SMH"]), J.JSArray(["softwareinfrastructure", "IGV"]), J.JSArray(["softwareapplication", "IGV"]), J.JSArray(["software", "IGV"]), J.JSArray(["informationtechnologyservices", "XLK"]), J.JSArray(["computerhardware", "XLK"]), J.JSArray(["communicationequipment", "XLK"]), J.JSArray(["electroniccomponents", "XLK"]), J.JSArray(["consumerelectronics", "XLK"]), J.JSArray(["internetcontent", "XLC"]), J.JSArray(["interactivemedia", "XLC"]), J.JSArray(["entertainment", "XLC"]), J.JSArray(["telecom", "XLC"]), J.JSArray(["advertising", "XLC"]), J.JSArray(["internetretail", "XLY"]), J.JSArray(["banksregional", "KRE"]), J.JSArray(["regionalbank", "KRE"]), J.JSArray(["bank", "KBE"]), J.JSArray(["creditservices", "XLF"]), J.JSArray(["capitalmarkets", "XLF"]), J.JSArray(["assetmanagement", "XLF"]), J.JSArray(["financialdata", "XLF"]), J.JSArray(["insurance", "KIE"]), J.JSArray(["biotechnology", "XBI"]), J.JSArray(["medicaldevices", "IHI"]), J.JSArray(["medicalinstruments", "IHI"]), J.JSArray(["drugmanufacturers", "XLV"]), J.JSArray(["healthcare", "XLV"]), J.JSArray(["medical", "XLV"]), J.JSArray(["diagnostics", "XLV"]), J.JSArray(["oilgas", "XOP"]), J.JSArray(["oil", "XLE"]), J.JSArray(["energy", "XLE"]), J.JSArray(["uranium", "XLE"]), J.JSArray(["solar", "XLE"]), J.JSArray(["aerospace", "ITA"]), J.JSArray(["defense", "ITA"]), J.JSArray(["industrial", "XLI"]), J.JSArray(["machinery", "XLI"]), J.JSArray(["railroads", "XLI"]), J.JSArray(["trucking", "XLI"]), J.JSArray(["airlines", "XLI"]), J.JSArray(["engineering", "XLI"]), J.JSArray(["building", "XLI"]), J.JSArray(["electricalequipment", "XLI"]), J.JSArray(["staffing", "XLI"]), J.JSArray(["waste", "XLI"]), J.JSArray(["retail", "XRT"]), J.JSArray(["apparel", "XRT"]), J.JSArray(["footwear", "XRT"]), J.JSArray(["department", "XRT"]), J.JSArray(["luxury", "XRT"]), J.JSArray(["restaurant", "XLY"]), J.JSArray(["auto", "XLY"]), J.JSArray(["homebuild", "XLY"]), J.JSArray(["leisure", "XLY"]), J.JSArray(["lodging", "XLY"]), J.JSArray(["gambling", "XLY"]), J.JSArray(["travel", "XLY"]), J.JSArray(["furnishings", "XLY"]), J.JSArray(["beverages", "XLP"]), J.JSArray(["grocery", "XLP"]), J.JSArray(["packagedfoods", "XLP"]), J.JSArray(["household", "XLP"]), J.JSArray(["tobacco", "XLP"]), J.JSArray(["discountstores", "XLP"]), J.JSArray(["confectioners", "XLP"]), J.JSArray(["utilities", "XLU"]), J.JSArray(["utility", "XLU"]), J.JSArray(["electric", "XLU"]), J.JSArray(["chemical", "XLB"]), J.JSArray(["steel", "XLB"]), J.JSArray(["copper", "XLB"]), J.JSArray(["gold", "XLB"]), J.JSArray(["silver", "XLB"]), J.JSArray(["aluminum", "XLB"]), J.JSArray(["lumber", "XLB"]), J.JSArray(["paper", "XLB"]), J.JSArray(["packaging", "XLB"]), J.JSArray(["agricultural", "XLB"]), J.JSArray(["metal", "XLB"]), J.JSArray(["mining", "XLB"])])
    SECTOR_ETF = J.obj(("technology", "XLK"), ("healthcare", "XLV"), ("finance", "XLF"), ("financial", "XLF"), ("utilities", "XLU"), ("energy", "XLE"), ("industrials", "XLI"), ("consumerdefensive", "XLP"), ("consumercyclical", "XLY"), ("consumer", "XLY"), ("communication", "XLC"), ("realestate", "XLRE"), ("materials", "XLB"), ("basicmaterials", "XLB"))
    def norm(v=J.undefined, *_args):
        return J.get(J.get(G_String(("" if J.nullish(_t1 := v) else _t1)), "toLowerCase")(), "replace")(J.regex("[^a-z]", "g"), "")
    industryId = norm((J.get(G_current, "industry") if J.truthy(_t1 := G_current) else _t1))
    sectorId = norm((J.get(G_current, "sector") if J.truthy(_t2 := G_current) else _t2))
    benchTicker = "SPY"
    benchHow = "default"
    if J.sne(benchSel, "auto"):
        benchTicker = benchSel
        benchHow = "manual"
    else:
        def _f3(pair=J.undefined, *_args):
            return J.ge(J.get(industryId, "indexOf")(J.get(pair, 0)), 0)
        hit = (J.get(INDUSTRY_ETF, "find")(_f3) if J.truthy(industryId) else None)
        def _f4(k=J.undefined, *_args):
            return (_t1 if J.truthy(_t1 := (_t2 if J.truthy(_t2 := J.seq(sectorId, k)) else J.ge(J.get(sectorId, "indexOf")(k), 0))) else J.ge(J.get(k, "indexOf")(sectorId), 0))
        sec = (J.get(J.get(G_Object, "keys")(SECTOR_ETF), "find")(_f4) if J.truthy(sectorId) else None)
        if J.truthy(hit):
            benchTicker = J.get(hit, 1)
            benchHow = "industry"
        elif J.truthy(sec):
            benchTicker = J.get(SECTOR_ETF, sec)
            benchHow = "sector"
    RSI_LEN = 14
    ADX_LEN = 14
    DI_SMOOTH = 9
    ATR_LEN = 14
    VOL_WMA = 8
    VOL_EMA = 5
    W_RSI = 0.4
    W_DI = 0.6
    W_ADX = 0.45
    W_ATR = 0.3
    W_VOL = 0.25
    ADX_FULL = 25
    FADE_W = 0.6
    STRUCT_W = 0.5
    WEEKLY_W = 0.6
    FADE_EXIT_RATIO = 0.25
    FADE_SMOOTH = 2
    DENS_LOOKBACK = J.mul(3, L)
    DENS_TOL_ATR = 0.3
    DENS_THIN = 0.25
    DENS_THICK = 0.4
    HTF_L = J.get(G_Math, "max")(4, J.get(G_Math, "round")(J.mul(0.6, L)))
    HTF_FULL = 0.5
    CONFIRM_VEL = 0
    CONFIRM_EXTRA = 0.15
    PENDING_MAX = L
    FAIL_BUFFER_ATR = 0.25
    EXT_LOOKBACK = 250
    EXT_P_HIGH = 0.95
    EXT_P_MID = 0.8
    REL_Z_LEVEL = 2
    REL_SCALE = 33
    fadeWeight = J.mul(FADE_W, enhance)
    structWeight = J.mul(STRUCT_W, enhance)
    htfWeight = J.mul(WEEKLY_W, enhance)
    fadeExit = J.mul(fadeThresh, FADE_EXIT_RATIO)
    confirmExtra = J.mul(CONFIRM_EXTRA, enhance)
    def isNum(v=J.undefined, *_args):
        return ((not J.truthy(J.get(G_Number, "isNaN")(v))) if J.truthy(_t1 := ((v is not J.undefined) if J.truthy(_t2 := (v is not None)) else _t2)) else _t1)
    def clamp(v=J.undefined, lo=J.undefined, hi=J.undefined, *_args):
        return J.get(G_Math, "max")(lo, J.get(G_Math, "min")(hi, v))
    def windowed(src=J.undefined, len=J.undefined, fn=J.undefined, *_args):
        def _f1(_v=J.undefined, _p=J.undefined, i=J.undefined, *_args):
            if J.lt(i, J.sub(len, 1)):
                return None
            w = J.get(src, "slice")(J.add(J.sub(i, len), 1), J.add(i, 1))
            j = 0
            while J.lt(j, J.get(w, "length")):
                if (not J.truthy(isNum(J.get(w, j)))):
                    return None
                j = J.inc(j)
            return fn(w)
        return G_for_every(src, _f1)
    def zscore(src=J.undefined, len=J.undefined, *_args):
        mean = G_sma(src, len)
        sd = G_stdev(src, len)
        def _f1(v=J.undefined, m=J.undefined, s=J.undefined, *_args):
            return (None if ((((not J.truthy(isNum(v))) or (not J.truthy(isNum(m)))) or (not J.truthy(isNum(s)))) or J.seq(s, 0)) else clamp(J.div(J.sub(v, m), s), (-3), 3))
        return G_for_every(src, mean, sd, _f1)
    def prank(src=J.undefined, len=J.undefined, *_args):
        def _f1(v=J.undefined, _p=J.undefined, i=J.undefined, *_args):
            if ((not J.truthy(isNum(v))) or J.lt(i, J.sub(len, 1))):
                return None
            below = 0
            ties = 0
            n = 0
            j = J.add(J.sub(i, len), 1)
            while J.le(j, i):
                x = J.get(src, j)
                if (not J.truthy(isNum(x))):
                    j = J.inc(j)
                    continue
                n = J.inc(n)
                if J.lt(x, v):
                    below = J.inc(below)
                elif J.seq(x, v):
                    ties = J.inc(ties)
                j = J.inc(j)
            return (J.div(J.add(below, J.mul(0.5, J.sub(ties, 1))), J.sub(n, 1)) if J.gt(n, 1) else 0.5)
        return G_for_every(src, _f1)
    def zStrength(z=J.undefined, *_args):
        def _f1(v=J.undefined, *_args):
            return (J.div(J.add(v, 3), 6) if J.truthy(isNum(v)) else None)
        return G_for_every(z, _f1)
    def ptile(src=J.undefined, len=J.undefined, p=J.undefined, minN=J.undefined, *_args):
        def _f1(_v=J.undefined, _p=J.undefined, i=J.undefined, *_args):
            vals = J.JSArray([])
            j = J.get(G_Math, "max")(0, J.add(J.sub(i, len), 1))
            while J.le(j, i):
                if J.truthy(isNum(J.get(src, j))):
                    J.get(vals, "push")(J.get(src, j))
                j = J.inc(j)
            if J.lt(J.get(vals, "length"), minN):
                return None
            def _f1(a=J.undefined, b=J.undefined, *_args):
                return J.sub(a, b)
            J.get(vals, "sort")(_f1)
            return J.get(vals, J.get(G_Math, "min")(J.sub(J.get(vals, "length"), 1), J.get(G_Math, "floor")(J.mul(p, J.sub(J.get(vals, "length"), 1)))))
        return G_for_every(src, _f1)
    rsiZ = zscore(G_rsi(G_close, RSI_LEN), N)
    tr = G_series_of(0)
    pdm = G_series_of(0)
    mdm = G_series_of(0)
    i = 1
    while J.lt(i, J.get(G_close, "length")):
        up = J.sub(J.get(G_high, i), J.get(G_high, J.sub(i, 1)))
        dn = J.sub(J.get(G_low, J.sub(i, 1)), J.get(G_low, i))
        J.set(tr, i, J.get(G_Math, "max")(J.sub(J.get(G_high, i), J.get(G_low, i)), J.get(G_Math, "abs")(J.sub(J.get(G_high, i), J.get(G_close, J.sub(i, 1)))), J.get(G_Math, "abs")(J.sub(J.get(G_low, i), J.get(G_close, J.sub(i, 1))))))
        if (J.gt(up, dn) and J.gt(up, 0)):
            J.set(pdm, i, up)
        if (J.gt(dn, up) and J.gt(dn, 0)):
            J.set(mdm, i, dn)
        i = J.inc(i)
    sTR = G_wildma(tr, ADX_LEN)
    def _f5(d=J.undefined, t=J.undefined, *_args):
        return (0 if ((not J.truthy(isNum(t))) or J.seq(t, 0)) else J.div(J.mul(100, d), t))
    plusDI = G_for_every(G_wildma(pdm, ADX_LEN), sTR, _f5)
    def _f6(d=J.undefined, t=J.undefined, *_args):
        return (0 if ((not J.truthy(isNum(t))) or J.seq(t, 0)) else J.div(J.mul(100, d), t))
    minusDI = G_for_every(G_wildma(mdm, ADX_LEN), sTR, _f6)
    def _f7(p=J.undefined, m=J.undefined, *_args):
        return (0 if J.seq(J.add(p, m), 0) else J.div(J.mul(100, J.get(G_Math, "abs")(J.sub(p, m))), J.add(p, m)))
    dx = G_for_every(plusDI, minusDI, _f7)
    adxRaw = G_wildma(dx, ADX_LEN)
    adxRank = prank(adxRaw, N)
    atrRaw = G_atr(ATR_LEN)
    volSm = G_ema(G_wma(G_volume, VOL_WMA), VOL_EMA)
    adxStrength = (adxRank if J.seq(mapping, "percentile") else zStrength(zscore(adxRaw, N)))
    def _f8(v=J.undefined, *_args):
        return (J.get(G_Math, "log")(v) if (J.truthy(isNum(v)) and J.gt(v, 0)) else None)
    atrStrength = (prank(atrRaw, N) if J.seq(mapping, "percentile") else zStrength(zscore(G_for_every(atrRaw, _f8), N)))
    def _f9(v=J.undefined, m=J.undefined, s=J.undefined, *_args):
        return (0 if ((not J.truthy(isNum(s))) or J.seq(s, 0)) else J.div(J.sub(v, m), s))
    volStrength = (prank(volSm, N) if J.seq(mapping, "percentile") else zStrength(zscore(G_ema(G_wma(G_for_every(G_volume, G_sma(G_volume, N), G_stdev(G_volume, N), _f9), VOL_WMA), VOL_EMA), N)))
    def _f10(p=J.undefined, m=J.undefined, *_args):
        return J.sub(p, m)
    diDelta = G_ema(G_for_every(plusDI, minusDI, _f10), DI_SMOOTH)
    def _f11(a=J.undefined, *_args):
        return (J.get(G_Math, "min")(J.div(a, ADX_FULL), 1) if J.truthy(isNum(a)) else None)
    diWeight = (adxRank if J.seq(mapping, "percentile") else G_for_every(adxRaw, _f11))
    def _f12(d=J.undefined, w=J.undefined, *_args):
        return (J.mul(d, w) if (J.truthy(isNum(d)) and J.truthy(isNum(w))) else None)
    diZ = zscore(G_for_every(diDelta, diWeight, _f12), N)
    def _f13(r=J.undefined, d=J.undefined, *_args):
        return (J.add(J.mul(r, W_RSI), J.mul(d, W_DI)) if (J.truthy(isNum(r)) and J.truthy(isNum(d))) else None)
    direction = G_for_every(rsiZ, diZ, _f13)
    def _f14(a=J.undefined, t=J.undefined, v=J.undefined, *_args):
        return (J.add(J.add(J.mul(a, W_ADX), J.mul(t, W_ATR)), J.mul(v, W_VOL)) if ((J.truthy(isNum(a)) and J.truthy(isNum(t))) and J.truthy(isNum(v))) else None)
    conviction = G_for_every(adxStrength, atrStrength, volStrength, _f14)
    def _f15(d=J.undefined, c=J.undefined, *_args):
        return (clamp(J.mul(J.mul(d, c), J.div(100, 3)), (-100), 100) if (J.truthy(isNum(d)) and J.truthy(isNum(c))) else None)
    compositeBase = G_for_every(direction, conviction, _f15)
    u = J.JSArray([])
    i_2 = 0
    while J.lt(i_2, L):
        J.get(u, "push")(J.div(J.sub(i_2, J.sub(L, 1)), J.sub(L, 1)))
        i_2 = J.inc(i_2)
    def _f16(a=J.undefined, v=J.undefined, *_args):
        return J.add(a, v)
    uMean = J.div(J.get(u, "reduce")(_f16, 0), L)
    def _f17(a=J.undefined, v=J.undefined, *_args):
        return J.add(a, J.pow_(J.sub(v, uMean), 2))
    Suu = J.get(u, "reduce")(_f17, 0)
    def _f18(v=J.undefined, *_args):
        return J.div(J.sub(v, uMean), Suu)
    wLin = J.get(u, "map")(_f18)
    S = J.obj(("u", 0), ("u2", 0), ("u3", 0), ("u4", 0))
    def _f19(v=J.undefined, *_args):
        J.set(S, "u", J.add(J.get(S, "u"), v))
        J.set(S, "u2", J.add(J.get(S, "u2"), J.mul(v, v)))
        J.set(S, "u3", J.add(J.get(S, "u3"), J.pow_(v, 3)))
        J.set(S, "u4", J.add(J.get(S, "u4"), J.pow_(v, 4)))
    J.get(u, "forEach")(_f19)
    M = J.JSArray([J.JSArray([L, J.get(S, "u"), J.get(S, "u2")]), J.JSArray([J.get(S, "u"), J.get(S, "u2"), J.get(S, "u3")]), J.JSArray([J.get(S, "u2"), J.get(S, "u3"), J.get(S, "u4")])])
    detM = J.add(J.sub(J.mul(J.get(J.get(M, 0), 0), J.sub(J.mul(J.get(J.get(M, 1), 1), J.get(J.get(M, 2), 2)), J.mul(J.get(J.get(M, 1), 2), J.get(J.get(M, 2), 1)))), J.mul(J.get(J.get(M, 0), 1), J.sub(J.mul(J.get(J.get(M, 1), 0), J.get(J.get(M, 2), 2)), J.mul(J.get(J.get(M, 1), 2), J.get(J.get(M, 2), 0))))), J.mul(J.get(J.get(M, 0), 2), J.sub(J.mul(J.get(J.get(M, 1), 0), J.get(J.get(M, 2), 1)), J.mul(J.get(J.get(M, 1), 1), J.get(J.get(M, 2), 0)))))
    G_assert(J.gt(J.get(G_Math, "abs")(detM), 1.0e-12), "Quadratic design matrix is singular; increase L")
    inv2 = J.JSArray([J.div(J.sub(J.mul(J.get(J.get(M, 1), 0), J.get(J.get(M, 2), 1)), J.mul(J.get(J.get(M, 1), 1), J.get(J.get(M, 2), 0))), detM), J.div(J.neg(J.sub(J.mul(J.get(J.get(M, 0), 0), J.get(J.get(M, 2), 1)), J.mul(J.get(J.get(M, 0), 1), J.get(J.get(M, 2), 0)))), detM), J.div(J.sub(J.mul(J.get(J.get(M, 0), 0), J.get(J.get(M, 1), 1)), J.mul(J.get(J.get(M, 0), 1), J.get(J.get(M, 1), 0))), detM)])
    def _f20(v=J.undefined, *_args):
        return J.add(J.add(J.get(inv2, 0), J.mul(J.get(inv2, 1), v)), J.mul(J.mul(J.get(inv2, 2), v), v))
    wAcc = J.get(u, "map")(_f20)
    def _f21(w=J.undefined, *_args):
        return J.get(G_Math, "max")(*J.spread(w))
    def _f22(w=J.undefined, *_args):
        return J.get(G_Math, "min")(*J.spread(w))
    def _f23(h=J.undefined, l=J.undefined, *_args):
        return (J.sub(h, l) if ((J.truthy(isNum(h)) and J.truthy(isNum(l))) and J.gt(J.sub(h, l), 0)) else None)
    rangeL = G_for_every(windowed(G_high, L, _f21), windowed(G_low, L, _f22), _f23)
    def _f24(w=J.undefined, *_args):
        def _f1(s=J.undefined, p=J.undefined, i_3=J.undefined, *_args):
            return J.add(s, J.mul(J.get(wAcc, i_3), p))
        return J.mul(2, J.get(w, "reduce")(_f1, 0))
    def _f25(q=J.undefined, rg=J.undefined, *_args):
        return (J.div(q, rg) if (J.truthy(isNum(q)) and J.truthy(isNum(rg))) else None)
    accel = G_for_every(windowed(G_close, L, _f24), rangeL, _f25)
    def _f26(w=J.undefined, *_args):
        def _f1(s=J.undefined, p=J.undefined, i_3=J.undefined, *_args):
            return J.add(s, J.mul(J.get(wLin, i_3), p))
        return J.get(w, "reduce")(_f1, 0)
    def _f27(d=J.undefined, rg=J.undefined, *_args):
        return (clamp(J.div(d, rg), (-1), 1) if (J.truthy(isNum(d)) and J.truthy(isNum(rg))) else None)
    velocity = G_for_every(windowed(G_close, L, _f26), rangeL, _f27)
    def _f28(d=J.undefined, y=J.undefined, *_args):
        if (not J.truthy(isNum(d))):
            return None
        if (J.seq(velDirWeight, 0) or (not J.truthy(isNum(y)))):
            return d
        wv = J.div(velDirWeight, 100)
        return J.add(J.mul(J.sub(1, wv), d), J.mul(wv, J.mul(3, y)))
    directionEnh = G_for_every(direction, velocity, _f28)
    resStr = J.get(G_String((_t29 if J.truthy(_t29 := (J.get(G_current, "resolution") if J.truthy(_t30 := G_current) else _t30)) else "D")), "toUpperCase")()
    htfKind = ("month" if J.ge(J.get(resStr, "indexOf")("W"), 0) else ("week" if J.ge(J.get(resStr, "indexOf")("D"), 0) else "day"))
    def toSec(ts=J.undefined, *_args):
        return (J.div(ts, 1000) if J.gt(ts, 100000000000) else ts)
    def bucketId(ts=J.undefined, *_args):
        sec_2 = toSec(ts)
        if J.seq(htfKind, "day"):
            return J.get(G_Math, "floor")(J.div(J.sub(sec_2, J.mul(5, 3600)), 86400))
        if J.seq(htfKind, "week"):
            return J.get(G_Math, "floor")(J.div(J.add(J.div(sec_2, 86400), 3), 7))
        return monthIndex(J.get(G_Math, "floor")(J.div(sec_2, 86400)))
    uh = J.JSArray([])
    i_3 = 0
    while J.lt(i_3, HTF_L):
        J.get(uh, "push")(J.div(J.sub(i_3, J.sub(HTF_L, 1)), J.sub(HTF_L, 1)))
        i_3 = J.inc(i_3)
    def _f31(a=J.undefined, v=J.undefined, *_args):
        return J.add(a, v)
    uhMean = J.div(J.get(uh, "reduce")(_f31, 0), HTF_L)
    def _f32(v=J.undefined, *_args):
        def _f1(a=J.undefined, x=J.undefined, *_args):
            return J.add(a, J.pow_(J.sub(x, uhMean), 2))
        return J.div(J.sub(v, uhMean), J.get(uh, "reduce")(_f1, 0))
    wLinH = J.get(uh, "map")(_f32)
    bC = J.JSArray([])
    bH = J.JSArray([])
    bLo = J.JSArray([])
    htfVelocity = G_series_of(0)
    curB = None
    curH = J.neg(G_Infinity)
    curL = G_Infinity
    curC = None
    lastHtfVel = 0
    i_4 = 0
    while J.lt(i_4, J.get(G_close, "length")):
        b = bucketId(J.get(G_time, i_4))
        if ((curB is not None) and J.sne(b, curB)):
            J.get(bC, "push")(curC)
            J.get(bH, "push")(curH)
            J.get(bLo, "push")(curL)
            n = J.get(bC, "length")
            if J.ge(n, HTF_L):
                disp = 0
                hi = J.neg(G_Infinity)
                lo = G_Infinity
                j = 0
                while J.lt(j, HTF_L):
                    k = J.add(J.sub(n, HTF_L), j)
                    disp = J.add(disp, J.mul(J.get(wLinH, j), J.get(bC, k)))
                    hi = J.get(G_Math, "max")(hi, J.get(bH, k))
                    lo = J.get(G_Math, "min")(lo, J.get(bLo, k))
                    j = J.inc(j)
                lastHtfVel = (clamp(J.div(disp, J.sub(hi, lo)), (-1), 1) if J.gt(J.sub(hi, lo), 0) else 0)
            curH = J.neg(G_Infinity)
            curL = G_Infinity
        curB = b
        curH = J.get(G_Math, "max")(curH, J.get(G_high, i_4))
        curL = J.get(G_Math, "min")(curL, J.get(G_low, i_4))
        curC = J.get(G_close, i_4)
        J.set(htfVelocity, i_4, lastHtfVel)
        i_4 = J.inc(i_4)
    htfOk = J.ge(J.get(bC, "length"), HTF_L)
    def _f33(c=J.undefined, _p=J.undefined, i_5=J.undefined, *_args):
        if (J.lt(i_5, DENS_LOOKBACK) or (not J.truthy(isNum(J.get(atrRaw, i_5))))):
            return None
        tol = J.mul(J.get(atrRaw, i_5), DENS_TOL_ATR)
        n_2 = 0
        j_2 = 1
        while J.le(j_2, DENS_LOOKBACK):
            if J.le(J.get(G_Math, "abs")(J.sub(J.get(G_close, J.sub(i_5, j_2)), c)), tol):
                n_2 = J.inc(n_2)
            if (J.ge(J.get(G_high, J.sub(i_5, j_2)), c) and J.le(J.get(G_low, J.sub(i_5, j_2)), c)):
                n_2 = J.inc(n_2)
            j_2 = J.inc(j_2)
        return J.div(n_2, DENS_LOOKBACK)
    density = G_for_every(G_close, _f33)
    def _f34(d=J.undefined, *_args):
        return (clamp(J.div(J.sub(d, DENS_THIN), J.sub(DENS_THICK, DENS_THIN)), 0, 1) if J.truthy(isNum(d)) else None)
    structure = G_for_every(density, _f34)
    def _f35(d=J.undefined, *_args):
        return (1 if (J.truthy(isNum(d)) and J.gt(d, DENS_THICK)) else 0)
    thick = G_for_every(density, _f35)
    def _f36(a=J.undefined, d=J.undefined, *_args):
        if ((not J.truthy(isNum(a))) or (not J.truthy(isNum(d)))):
            return None
        opposing = (J.neg(a) if J.gt(d, 0) else (a if J.lt(d, 0) else 0))
        return clamp(J.div(J.sub(opposing, fadeExit), J.get(G_Math, "max")(J.sub(fadeThresh, fadeExit), 1.0e-9)), 0, 1)
    deterioration = G_ema(G_for_every(accel, directionEnh, _f36), FADE_SMOOTH)
    htfAgainst = G_series_of(0)
    i_5 = 0
    while J.lt(i_5, J.get(G_close, "length")):
        d = J.get(directionEnh, i_5)
        hv = J.get(htfVelocity, i_5)
        if (((not J.truthy(isNum(d))) or (not J.truthy(isNum(hv)))) or J.seq(d, 0)):
            i_5 = J.inc(i_5)
            continue
        J.set(htfAgainst, i_5, clamp(J.div((J.neg(hv) if J.lt(d, 0) else hv), HTF_FULL), 0, 1))
        i_5 = J.inc(i_5)
    convictionEnh = G_series_of(None)
    i_6 = 0
    while J.lt(i_6, J.get(G_close, "length")):
        c = J.get(conviction, i_6)
        if (not J.truthy(isNum(c))):
            i_6 = J.inc(i_6)
            continue
        det = (J.get(deterioration, i_6) if J.truthy(isNum(J.get(deterioration, i_6))) else 0)
        st = (J.get(structure, i_6) if J.truthy(isNum(J.get(structure, i_6))) else 0)
        fw = J.mul(fadeWeight, J.sub(1, J.mul(htfWeight, J.get(htfAgainst, i_6))))
        J.set(convictionEnh, i_6, J.mul(J.mul(c, J.sub(1, J.mul(fw, det))), J.sub(1, J.mul(structWeight, st))))
        i_6 = J.inc(i_6)
    def _f37(d_2=J.undefined, c_2=J.undefined, *_args):
        return (clamp(J.mul(J.mul(d_2, c_2), J.div(100, 3)), (-100), 100) if (J.truthy(isNum(d_2)) and J.truthy(isNum(c_2))) else None)
    composite = G_for_every(directionEnh, convictionEnh, _f37)
    def _f38(v=J.undefined, *_args):
        return (J.get(G_Math, "abs")(v) if J.truthy(isNum(v)) else None)
    absScore = G_for_every(composite, _f38)
    extHigh = ptile(absScore, EXT_LOOKBACK, EXT_P_HIGH, J.get(G_Math, "min")(EXT_LOOKBACK, N))
    extMid = ptile(absScore, EXT_LOOKBACK, EXT_P_MID, J.get(G_Math, "min")(EXT_LOOKBACK, N))
    def _f39(v=J.undefined, e=J.undefined, *_args):
        return (1 if ((J.truthy(isNum(v)) and J.truthy(isNum(e))) and J.ge(J.get(G_Math, "abs")(v), e)) else 0)
    extended = G_for_every(composite, extHigh, _f39)
    benchClose = G_series_of(None)
    benchOk = False
    try:
        b_2 = J.get(G_request, "history")(benchTicker, J.get(G_current, "resolution"))
        if (((J.truthy(b_2) and (not J.truthy(J.get(b_2, "error")))) and J.truthy(J.get(b_2, "close"))) and J.truthy(J.get(b_2, "time"))):
            idx = J.JSArray([])
            i_7 = 0
            while J.lt(i_7, J.get(J.get(b_2, "time"), "length")):
                J.get(idx, "push")(i_7)
                i_7 = J.inc(i_7)
            def _f40(p=J.undefined, q=J.undefined, *_args):
                return J.sub(J.get(J.get(b_2, "time"), p), J.get(J.get(b_2, "time"), q))
            J.get(idx, "sort")(_f40)
            k_2 = 0
            hits = 0
            lastV = None
            i_8 = 0
            while J.lt(i_8, J.get(G_time, "length")):
                while (J.lt(k_2, J.get(idx, "length")) and J.le(J.get(J.get(b_2, "time"), J.get(idx, k_2)), J.get(G_time, i_8))):
                    v = J.get(J.get(b_2, "close"), J.get(idx, k_2))
                    if J.truthy(isNum(v)):
                        lastV = v
                    k_2 = J.inc(k_2)
                if (lastV is not None):
                    J.set(benchClose, i_8, lastV)
                    hits = J.inc(hits)
                i_8 = J.inc(i_8)
            benchOk = J.gt(hits, N)
    except Exception as _e41:
        e = J.catch_value(_e41)
        benchOk = False
    relRatio = G_series_of(None)
    i_9 = 0
    while J.lt(i_9, J.get(G_close, "length")):
        bc = J.get(benchClose, i_9)
        if ((J.truthy(isNum(bc)) and J.gt(bc, 0)) and J.gt(J.get(G_close, i_9), 0)):
            J.set(relRatio, i_9, J.get(G_Math, "log")(J.div(J.get(G_close, i_9), bc)))
        i_9 = J.inc(i_9)
    relExtRaw = G_series_of(None)
    i_10 = J.sub(N, 1)
    while J.lt(i_10, J.get(G_close, "length")):
        if (not J.truthy(isNum(J.get(relRatio, i_10)))):
            i_10 = J.inc(i_10)
            continue
        sm = 0
        s2 = 0
        n_2 = 0
        j_2 = J.add(J.sub(i_10, N), 1)
        while J.le(j_2, i_10):
            v_2 = J.get(relRatio, j_2)
            if J.truthy(isNum(v_2)):
                sm = J.add(sm, v_2)
                s2 = J.add(s2, J.mul(v_2, v_2))
                n_2 = J.inc(n_2)
            j_2 = J.inc(j_2)
        if J.lt(n_2, J.mul(N, 0.8)):
            i_10 = J.inc(i_10)
            continue
        mean = J.div(sm, n_2)
        sd = J.get(G_Math, "sqrt")(J.get(G_Math, "max")(J.sub(J.div(s2, n_2), J.mul(mean, mean)), 0))
        J.set(relExtRaw, i_10, (clamp(J.div(J.sub(J.get(relRatio, i_10), mean), sd), (-4), 4) if J.gt(sd, 1.0e-12) else 0))
        i_10 = J.inc(i_10)
    relExt = G_series_of(None)
    k_3 = J.div(2, J.add(relSmooth, 1))
    e_2 = None
    i_11 = 0
    while J.lt(i_11, J.get(G_close, "length")):
        v_3 = J.get(relExtRaw, i_11)
        if (not J.truthy(isNum(v_3))):
            i_11 = J.inc(i_11)
            continue
        e_2 = (v_3 if ((e_2 is None) or J.le(relSmooth, 1)) else J.add(J.mul(v_3, k_3), J.mul(e_2, J.sub(1, k_3))))
        J.set(relExt, i_11, e_2)
        i_11 = J.inc(i_11)
    relVel = G_series_of(None)
    i_12 = J.sub(L, 1)
    while J.lt(i_12, J.get(G_close, "length")):
        disp_2 = 0
        ok = True
        j_3 = 0
        while J.lt(j_3, L):
            v_4 = J.get(relRatio, J.add(J.add(J.sub(i_12, L), 1), j_3))
            if (not J.truthy(isNum(v_4))):
                ok = False
                break
            disp_2 = J.add(disp_2, J.mul(J.get(wLin, j_3), v_4))
            j_3 = J.inc(j_3)
        if J.truthy(ok):
            J.set(relVel, i_12, disp_2)
        i_12 = J.inc(i_12)
    def _f42(e_3=J.undefined, *_args):
        return (1 if (J.truthy(isNum(e_3)) and J.ge(e_3, REL_Z_LEVEL)) else 0)
    relHigh = G_for_every(relExt, _f42)
    def _f43(e_3=J.undefined, *_args):
        return (1 if (J.truthy(isNum(e_3)) and J.le(e_3, J.neg(REL_Z_LEVEL))) else 0)
    relLow = G_for_every(relExt, _f43)
    def _f44(e_3=J.undefined, v_5=J.undefined, *_args):
        return (1 if (((J.truthy(isNum(e_3)) and J.truthy(isNum(v_5))) and J.ge(e_3, REL_Z_LEVEL)) and J.lt(v_5, 0)) else 0)
    relOverExt = G_for_every(relExt, relVel, _f44)
    def _f45(e_3=J.undefined, v_5=J.undefined, *_args):
        return (1 if (((J.truthy(isNum(e_3)) and J.truthy(isNum(v_5))) and J.le(e_3, J.neg(REL_Z_LEVEL))) and J.gt(v_5, 0)) else 0)
    relCatchUp = G_for_every(relExt, relVel, _f45)
    gateOn = J.gt(enhance, 0)
    def _f46(v_5=J.undefined, t=J.undefined, *_args):
        return (1 if (((J.truthy(isNum(v_5)) and J.ge(v_5, 0.5)) and J.gt(fadeWeight, 0)) and (not (J.truthy(gateOn) and J.seq(t, 1)))) else 0)
    discountOn = G_for_every(deterioration, thick, _f46)
    def onset(flag=J.undefined, *_args):
        def _f1(v_5=J.undefined, _p=J.undefined, i_13=J.undefined, *_args):
            return (1 if ((J.seq(v_5, 1) and J.gt(i_13, 0)) and J.sne(J.get(flag, J.sub(i_13, 1)), 1)) else 0)
        return G_for_every(flag, _f1)
    def _f47(o=J.undefined, sc=J.undefined, *_args):
        return (1 if ((J.seq(o, 1) and J.truthy(isNum(sc))) and J.ge(sc, 0)) else 0)
    bullExhaustOn = G_for_every(onset(discountOn), composite, _f47)
    def _f48(o=J.undefined, sc=J.undefined, *_args):
        return (1 if ((J.seq(o, 1) and J.truthy(isNum(sc))) and J.lt(sc, 0)) else 0)
    bearExhaustOn = G_for_every(onset(discountOn), composite, _f48)
    revUp = G_series_of(0)
    bearFail = G_series_of(0)
    revDn = G_series_of(0)
    bullFail = G_series_of(0)
    pendingBottom = G_series_of(0)
    pendingTop = G_series_of(0)
    botOpen = False
    botLow = 0
    botSince = 0
    botAg = 0
    topOpen = False
    topHigh = 0
    topSince = 0
    topAg = 0
    i_13 = 0
    while J.lt(i_13, J.get(G_close, "length")):
        v_5 = J.get(velocity, i_13)
        buf = J.mul(FAIL_BUFFER_ATR, (_t49 if J.truthy(_t49 := J.get(atrRaw, i_13)) else 0))
        if J.seq(J.get(bearExhaustOn, i_13), 1):
            botOpen = True
            botLow = J.get(G_low, i_13)
            botSince = i_13
            botAg = J.get(htfAgainst, i_13)
        elif J.truthy(botOpen):
            if J.lt(J.get(G_low, i_13), J.sub(botLow, buf)):
                J.set(bearFail, i_13, 1)
                botOpen = False
            elif (J.truthy(isNum(v_5)) and J.gt(v_5, J.add(CONFIRM_VEL, J.mul(confirmExtra, botAg)))):
                J.set(revUp, i_13, 1)
                botOpen = False
            elif J.gt(J.sub(i_13, botSince), PENDING_MAX):
                botOpen = False
        if J.seq(J.get(bullExhaustOn, i_13), 1):
            topOpen = True
            topHigh = J.get(G_high, i_13)
            topSince = i_13
            topAg = J.get(htfAgainst, i_13)
        elif J.truthy(topOpen):
            if J.gt(J.get(G_high, i_13), J.add(topHigh, buf)):
                J.set(bullFail, i_13, 1)
                topOpen = False
            elif (J.truthy(isNum(v_5)) and J.lt(v_5, J.neg(J.add(CONFIRM_VEL, J.mul(confirmExtra, topAg))))):
                J.set(revDn, i_13, 1)
                topOpen = False
            elif J.gt(J.sub(i_13, topSince), PENDING_MAX):
                topOpen = False
        J.set(pendingBottom, i_13, (1 if J.truthy(botOpen) else 0))
        J.set(pendingTop, i_13, (1 if J.truthy(topOpen) else 0))
        i_13 = J.inc(i_13)
    def bandColor(s=J.undefined, *_args):
        if (not J.truthy(isNum(s))):
            return "#555555"
        if J.ge(s, 66):
            return "#00e676"
        if J.ge(s, 33):
            return "#90ee90"
        if J.gt(s, 10):
            return "rgba(129,199,132,0.7)"
        if J.ge(s, (-10)):
            return "#777777"
        if J.gt(s, (-33)):
            return "rgba(239,154,154,0.7)"
        if J.gt(s, (-66)):
            return "#ff7777"
        return "#f44336"
    def _f50(s=J.undefined, on=J.undefined, t=J.undefined, *_args):
        return ("rgba(160,160,160,0.55)" if (J.truthy(gateOn) and J.seq(t, 1)) else (("#FFB020" if J.ge(s, 0) else "#00E5FF") if J.seq(on, 1) else bandColor(s)))
    colors = G_for_every(composite, discountOn, thick, _f50)
    G_paint(composite, J.obj(("name", "Composite Trend Score"), ("style", "column"), ("color", colors)))
    def mark(flag=J.undefined, offset=J.undefined, symbol=J.undefined, fill=J.undefined, hollowWhenAgainst=J.undefined, *_args):
        def _f1(v_6=J.undefined, _p=J.undefined, i_14=J.undefined, *_args):
            if (J.sne(v_6, 1) or (not J.truthy(isNum(J.get(composite, i_14))))):
                return None
            ag = (J.ge(J.get(htfAgainst, i_14), 0.5) if J.truthy(_t1 := hollowWhenAgainst) else _t1)
            return J.obj(("y", J.add(J.get(composite, i_14), offset)), ("marker", J.obj(("enabled", True), ("radius", 5), ("symbol", symbol), ("fillColor", ("rgba(0,0,0,0)" if J.truthy(ag) else fill)), ("lineColor", (fill if J.truthy(ag) else "#111111")), ("lineWidth", (2 if J.truthy(ag) else 1)))))
        return G_for_every(flag, _f1)
    G_paint(mark(bullExhaustOn, 8, "triangle-down", "#FFB020", True), J.obj(("name", "Bull Exhaustion Marker"), ("color", "transparent")))
    G_paint(mark(bearExhaustOn, (-8), "triangle", "#00E5FF", True), J.obj(("name", "Bear Exhaustion Marker"), ("color", "transparent")))
    G_paint(mark(revUp, (-16), "circle", "#00E676", False), J.obj(("name", "Reversal Up Marker"), ("color", "transparent")))
    G_paint(mark(revDn, 16, "circle", "#FF3D71", False), J.obj(("name", "Reversal Down Marker"), ("color", "transparent")))
    G_paint(mark(bearFail, (-16), "diamond", "#9E9E9E", False), J.obj(("name", "Bear Exhaust Fail Marker"), ("color", "transparent")))
    G_paint(mark(bullFail, 16, "diamond", "#9E9E9E", False), J.obj(("name", "Bull Exhaust Fail Marker"), ("color", "transparent")))
    def _f51(e_3=J.undefined, *_args):
        return ("#888888" if (not J.truthy(isNum(e_3))) else ("#FFB020" if J.ge(e_3, REL_Z_LEVEL) else ("#00E5FF" if J.le(e_3, J.neg(REL_Z_LEVEL)) else "rgba(255,255,255,0.75)")))
    relColor = G_for_every(relExt, _f51)
    def _f52(e_3=J.undefined, *_args):
        return (J.mul(e_3, REL_SCALE) if J.truthy(isNum(e_3)) else None)
    G_paint(G_for_every(relExt, _f52), J.obj(("name", "Relative Extension"), ("color", relColor), ("thickness", 1), ("ignoreWhenScaling", True)))
    def x100(s=J.undefined, *_args):
        def _f1(v_6=J.undefined, *_args):
            return (J.mul(v_6, 100) if J.truthy(isNum(v_6)) else None)
        return G_for_every(s, _f1)
    G_paint(compositeBase, J.obj(("name", "Composite (Base)"), ("color", "#B0BEC5"), ("thickness", 1), ("invisibleByDefault", True)))
    G_paint(x100(deterioration), J.obj(("name", "Deterioration x100"), ("color", "#FFB020"), ("thickness", 1), ("invisibleByDefault", True), ("ignoreWhenScaling", True)))
    def _f53(v_6=J.undefined, *_args):
        return (J.mul(v_6, 25) if J.truthy(isNum(v_6)) else None)
    G_paint(G_for_every(accel, _f53), J.obj(("name", "Price Accel x25"), ("color", "#C77DFF"), ("thickness", 1), ("invisibleByDefault", True), ("ignoreWhenScaling", True)))
    G_paint(x100(velocity), J.obj(("name", "Price Velocity x100"), ("color", "#4FC3F7"), ("thickness", 1), ("invisibleByDefault", True), ("ignoreWhenScaling", True)))
    G_paint(x100(htfVelocity), J.obj(("name", "HTF Velocity x100"), ("color", "#FFD54F"), ("thickness", 1), ("invisibleByDefault", True), ("ignoreWhenScaling", True)))
    G_paint(x100(density), J.obj(("name", "Structure Density x100"), ("color", "#9E9E9E"), ("thickness", 1), ("invisibleByDefault", True), ("ignoreWhenScaling", True)))
    G_paint(x100(conviction), J.obj(("name", "Conviction x100"), ("color", "#80CBC4"), ("thickness", 1), ("invisibleByDefault", True), ("ignoreWhenScaling", True)))
    G_paint(extHigh, J.obj(("name", "Extended Upper p95"), ("color", "#FFB020"), ("thickness", 1), ("style", "dotted")))
    def _f54(v_6=J.undefined, *_args):
        return (J.neg(v_6) if J.truthy(isNum(v_6)) else None)
    G_paint(G_for_every(extHigh, _f54), J.obj(("name", "Extended Lower p95"), ("color", "#FFB020"), ("thickness", 1), ("style", "dotted")))
    G_paint(extMid, J.obj(("name", "Elevated Upper p80"), ("color", "#8D6E63"), ("thickness", 1), ("style", "dotted")))
    def _f55(v_6=J.undefined, *_args):
        return (J.neg(v_6) if J.truthy(isNum(v_6)) else None)
    G_paint(G_for_every(extMid, _f55), J.obj(("name", "Elevated Lower p80"), ("color", "#8D6E63"), ("thickness", 1), ("style", "dotted")))
    G_paint(G_horizontal_line(66), J.obj(("name", "Strong Bullish"), ("color", "#3A3A3A"), ("style", "dotted")))
    G_paint(G_horizontal_line(33), J.obj(("name", "Bullish Trend"), ("color", "#3A3A3A"), ("style", "dotted")))
    G_paint(G_horizontal_line(0), J.obj(("name", "Neutral"), ("color", "#888888"), ("style", "dotted")))
    G_paint(G_horizontal_line((-33)), J.obj(("name", "Bearish Trend"), ("color", "#3A3A3A"), ("style", "dotted")))
    G_paint(G_horizontal_line((-66)), J.obj(("name", "Strong Bearish"), ("color", "#3A3A3A"), ("style", "dotted")))
    G_register_signal(discountOn, "Fade Discount Active")
    G_register_signal(thick, "Structure Thick")
    def _f56(d_2=J.undefined, *_args):
        return (1 if (J.truthy(isNum(d_2)) and J.lt(d_2, DENS_THIN)) else 0)
    G_register_signal(G_for_every(density, _f56), "Structure Thin")
    G_register_signal(bullExhaustOn, "Bull Exhaustion Onset")
    G_register_signal(bearExhaustOn, "Bear Exhaustion Onset")
    G_register_signal(pendingBottom, "Bottom Pending")
    G_register_signal(pendingTop, "Top Pending")
    G_register_signal(revUp, "Reversal Up Confirmed")
    G_register_signal(revDn, "Reversal Down Confirmed")
    G_register_signal(bearFail, "Bear Exhaustion Failed (continuation)")
    G_register_signal(bullFail, "Bull Exhaustion Failed (continuation)")
    def _f57(v_6=J.undefined, *_args):
        return (1 if J.ge(v_6, 0.5) else 0)
    G_register_signal(G_for_every(htfAgainst, _f57), "HTF Against Reversal")
    G_register_signal(extended, "Extended Either Side p95")
    def _f58(v_6=J.undefined, e_3=J.undefined, *_args):
        return (1 if ((J.seq(e_3, 1) and J.truthy(isNum(v_6))) and J.gt(v_6, 0)) else 0)
    G_register_signal(G_for_every(composite, extended, _f58), "Extended Bullish")
    def _f59(v_6=J.undefined, e_3=J.undefined, *_args):
        return (1 if ((J.seq(e_3, 1) and J.truthy(isNum(v_6))) and J.lt(v_6, 0)) else 0)
    G_register_signal(G_for_every(composite, extended, _f59), "Extended Bearish")
    G_register_signal(relHigh, "Rel Extension High (+2σ vs benchmark)")
    G_register_signal(relLow, "Rel Extension Low (-2σ vs benchmark)")
    G_register_signal(relOverExt, "Overextended vs Benchmark (gap closing)")
    G_register_signal(relCatchUp, "Laggard Catch-up vs Benchmark")
    def _f60(v_6=J.undefined, *_args):
        return (1 if (J.truthy(isNum(v_6)) and J.ge(v_6, 33)) else 0)
    G_register_signal(G_for_every(composite, _f60), "Composite Bullish (>=33)")
    def _f61(v_6=J.undefined, *_args):
        return (1 if (J.truthy(isNum(v_6)) and J.le(v_6, (-33))) else 0)
    G_register_signal(G_for_every(composite, _f61), "Composite Bearish (<=-33)")


register_store_indicator(
    script,
    name='vectr_TS',
    title='VECTR',
    developer='Gustivus',
    url='https://trendspider.com/trading-tools-store/indicators/6aa0f7-vectr/',
    position='lower',
    inputs=[{'id': 'kinematic_window__l_', 'title': 'Kinematic Window (L)', 'type': 'number', 'default': 10}, {'id': 'normalization_window__n_', 'title': 'Normalization Window (N)', 'type': 'number', 'default': 100}, {'id': 'enhancement_strength', 'title': 'Enhancement Strength', 'type': 'number', 'default': 1}, {'id': 'fade_threshold___accel__', 'title': 'Fade Threshold (|accel|)', 'type': 'number', 'default': 1}, {'id': 'velocity_direction_weight', 'title': 'Velocity Direction Weight', 'type': 'number', 'default': 0}, {'id': 'strength_mapping', 'title': 'Strength Mapping', 'type': 'select_wide', 'default': 'percentile', 'options': ['percentile', 'z-linear']}, {'id': 'benchmark', 'title': 'Benchmark', 'type': 'select_wide', 'default': 'auto', 'options': ['auto', 'SPY', 'QQQ', 'RSP', 'SMH', 'SOXX', 'XSD', 'IGV', 'WCLD', 'XLK', 'XLC', 'XLF', 'KBE', 'KRE', 'KIE', 'XLV', 'XBI', 'IHI', 'XLE', 'XOP', 'XLI', 'ITA', 'XLY', 'XRT', 'XLP', 'XLU', 'XLRE', 'XLB']}, {'id': 'relative_extension_smoothing', 'title': 'Relative Extension Smoothing', 'type': 'number', 'default': 1}],
    outputs=['composite_trend_score', 'bull_exhaustion_marker', 'bear_exhaustion_marker', 'reversal_up_marker', 'reversal_down_marker', 'bear_exhaust_fail_marker', 'bull_exhaust_fail_marker', 'relative_extension', 'composite__base_', 'deterioration_x100', 'price_accel_x25', 'price_velocity_x100', 'htf_velocity_x100', 'structure_density_x100', 'conviction_x100', 'extended_upper_p95', 'extended_lower_p95', 'elevated_upper_p80', 'elevated_lower_p80', 'strong_bullish', 'bullish_trend', 'neutral', 'bearish_trend', 'strong_bearish', 'fade_discount_active', 'structure_thick', 'structure_thin', 'bull_exhaustion_onset', 'bear_exhaustion_onset', 'bottom_pending', 'top_pending', 'reversal_up_confirmed', 'reversal_down_confirmed', 'bear_exhaustion_failed__continuation_', 'bull_exhaustion_failed__continuation_', 'htf_against_reversal', 'extended_either_side_p95', 'extended_bullish', 'extended_bearish', 'rel_extension_high___2__vs_benchmark_', 'rel_extension_low___2__vs_benchmark_', 'overextended_vs_benchmark__gap_closing_', 'laggard_catch_up_vs_benchmark', 'composite_bullish____33_', 'composite_bearish_____33_'],
    signals=['fade_discount_active', 'structure_thick', 'structure_thin', 'bull_exhaustion_onset', 'bear_exhaustion_onset', 'bottom_pending', 'top_pending', 'reversal_up_confirmed', 'reversal_down_confirmed', 'bear_exhaustion_failed__continuation_', 'bull_exhaustion_failed__continuation_', 'htf_against_reversal', 'extended_either_side_p95', 'extended_bullish', 'extended_bearish', 'rel_extension_high___2__vs_benchmark_', 'rel_extension_low___2__vs_benchmark_', 'overextended_vs_benchmark__gap_closing_', 'laggard_catch_up_vs_benchmark', 'composite_bullish____33_', 'composite_bearish_____33_'],
    requires=['history'],
    parity='exact',
)
