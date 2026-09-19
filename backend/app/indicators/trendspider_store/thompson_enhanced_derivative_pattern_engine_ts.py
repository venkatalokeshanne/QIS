"""
Thompson-Enhanced Derivative Pattern Engine -- TrendSpider store indicator by DskyzInvestments.

Registered as "thompson_enhanced_derivative_pattern_engine_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6a4ab0-thompson-enhanced-derivative-pattern-engine/)
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
    G_TH = G["TH"]
    G_aLoss = G["aLoss"]
    G_aWin = G["aWin"]
    G_actualMatches = G["actualMatches"]
    G_actualMatchesArr = G["actualMatchesArr"]
    G_am = G["am"]
    G_atrAtJ = G["atrAtJ"]
    G_atrVals = G["atrVals"]
    G_avgLossArr = G["avgLossArr"]
    G_avgLossAtrArr = G["avgLossAtrArr"]
    G_avgWinArr = G["avgWinArr"]
    G_avgWinAtrArr = G["avgWinAtrArr"]
    G_barColArr = G["barColArr"]
    G_barsNeeded = G["barsNeeded"]
    G_barsOk = G["barsOk"]
    G_baseInd = G["baseInd"]
    G_bearZoneBot = G["bearZoneBot"]
    G_bearZoneTop = G["bearZoneTop"]
    G_bullZoneBot = G["bullZoneBot"]
    G_bullZoneTop = G["bullZoneTop"]
    G_buyStateArr = G["buyStateArr"]
    G_close = G["close"]
    G_color_candles = G["color_candles"]
    G_color_cloud = G["color_cloud"]
    G_consensusArr = G["consensusArr"]
    G_d1 = G["d1"]
    G_d2 = G["d2"]
    G_d3 = G["d3"]
    G_d4 = G["d4"]
    G_describe_indicator = G["describe_indicator"]
    G_dist = G["dist"]
    G_e_d1 = G["e_d1"]
    G_e_d2 = G["e_d2"]
    G_e_d3 = G["e_d3"]
    G_e_d4 = G["e_d4"]
    G_energyColor = G["energyColor"]
    G_energyRows = G["energyRows"]
    G_ev = G["ev"]
    G_expectedValueArr = G["expectedValueArr"]
    G_finalBuyArr = G["finalBuyArr"]
    G_finalSellArr = G["finalSellArr"]
    G_fwdIdx = G["fwdIdx"]
    G_glowBuyInner = G["glowBuyInner"]
    G_glowBuyOuter = G["glowBuyOuter"]
    G_glowSellInner = G["glowSellInner"]
    G_glowSellOuter = G["glowSellOuter"]
    G_high = G["high"]
    G_highBound = G["highBound"]
    G_i_atrLen = G["i_atrLen"]
    G_i_atrMult = G["i_atrMult"]
    G_i_banditMode = G["i_banditMode"]
    G_i_baseLen = G["i_baseLen"]
    G_i_baseType = G["i_baseType"]
    G_i_decay = G["i_decay"]
    G_i_evThresh = G["i_evThresh"]
    G_i_filterPer = G["i_filterPer"]
    G_i_glow = G["i_glow"]
    G_i_matchCount = G["i_matchCount"]
    G_i_matchThr = G["i_matchThr"]
    G_i_minMatches = G["i_minMatches"]
    G_i_normLen = G["i_normLen"]
    G_i_projFwd = G["i_projFwd"]
    G_i_searchWin = G["i_searchWin"]
    G_i_showBars = G["i_showBars"]
    G_i_showSignals = G["i_showSignals"]
    G_i_showZones = G["i_showZones"]
    G_i_signalMode = G["i_signalMode"]
    G_i_theme = G["i_theme"]
    G_i_useBandit = G["i_useBandit"]
    G_i_useFilter = G["i_useFilter"]
    G_input = G["input"]
    G_isNaN = G["isNaN"]
    G_l_avgLoss = G["l_avgLoss"]
    G_l_avgWin = G["l_avgWin"]
    G_l_ev = G["l_ev"]
    G_l_matches = G["l_matches"]
    G_l_nD1 = G["l_nD1"]
    G_l_nD2 = G["l_nD2"]
    G_l_nD3 = G["l_nD3"]
    G_l_nD4 = G["l_nD4"]
    G_l_rr = G["l_rr"]
    G_l_w1 = G["l_w1"]
    G_l_w2 = G["l_w2"]
    G_l_w3 = G["l_w3"]
    G_l_w4 = G["l_w4"]
    G_l_winRate = G["l_winRate"]
    G_l_wp = G["l_wp"]
    G_last = G["last"]
    G_lastIdx = G["lastIdx"]
    G_lb = G["lb"]
    G_library = G["library"]
    G_low = G["low"]
    G_lowBound = G["lowBound"]
    G_mLen = G["mLen"]
    G_markerBuy = G["markerBuy"]
    G_markerSell = G["markerSell"]
    G_n = G["n"]
    G_nD1 = G["nD1"]
    G_nD2 = G["nD2"]
    G_nD3 = G["nD3"]
    G_nD4 = G["nD4"]
    G_normW1 = G["normW1"]
    G_normW2 = G["normW2"]
    G_normW3 = G["normW3"]
    G_normW4 = G["normW4"]
    G_paint = G["paint"]
    G_paint_label_at_line = G["paint_label_at_line"]
    G_paint_overlay = G["paint_overlay"]
    G_pctEnergy = G["pctEnergy"]
    G_priceChange = G["priceChange"]
    G_priceDir = G["priceDir"]
    G_rSlLabel = G["rSlLabel"]
    G_rTpLabel = G["rTpLabel"]
    G_register_signal = G["register_signal"]
    G_ret2 = G["ret2"]
    G_ret2Atr = G["ret2Atr"]
    G_retArr = G["retArr"]
    G_retArrAtr = G["retArrAtr"]
    G_rngNext = G["rngNext"]
    G_searchStart = G["searchStart"]
    G_sellStateArr = G["sellStateArr"]
    G_sim = G["sim"]
    G_sim2 = G["sim2"]
    G_simArr = G["simArr"]
    G_slLabelPts = G["slLabelPts"]
    G_slLabelText = G["slLabelText"]
    G_slLabelY = G["slLabelY"]
    G_slLineArr = G["slLineArr"]
    G_statsRows = G["statsRows"]
    G_statusColor = G["statusColor"]
    G_tiny = G["tiny"]
    G_totalEnergy = G["totalEnergy"]
    G_totalW = G["totalW"]
    G_tpLabelPts = G["tpLabelPts"]
    G_tpLabelText = G["tpLabelText"]
    G_tpLabelY = G["tpLabelY"]
    G_tpLineArr = G["tpLineArr"]
    G_tr = G["tr"]
    G_tra = G["tra"]
    G_ts = G["ts"]
    G_volume = G["volume"]
    G_wWinProb = G["wWinProb"]
    G_weightedWinProbArr = G["weightedWinProbArr"]
    G_winRateArr = G["winRateArr"]
    G_wp = G["wp"]
    rawBase = J.undefined
    i = J.undefined
    bd1A = J.undefined
    bd1B = J.undefined
    bd2A = J.undefined
    bd2B = J.undefined
    bd3A = J.undefined
    bd3B = J.undefined
    bd4A = J.undefined
    bd4B = J.undefined
    bw1 = J.undefined
    bw2 = J.undefined
    bw3 = J.undefined
    bw4 = J.undefined
    j = J.undefined
    sq = J.undefined
    a1 = J.undefined
    a2 = J.undefined
    bestIdx = J.undefined
    kk = J.undefined
    sumW = J.undefined
    sumWRet = J.undefined
    winCnt = J.undefined
    sumWWin = J.undefined
    sumWUpRet = J.undefined
    sumWUpW = J.undefined
    sumWUpRetAtr = J.undefined
    sumWDownRet = J.undefined
    sumWDownW = J.undefined
    sumWDownRetAtr = J.undefined
    barsInTrade = J.undefined
    tradeStatus = J.undefined
    tradeDir = J.undefined
    activeTp = J.undefined
    activeSl = J.undefined
    def fillNull(len=J.undefined, *_args):
        arr = J.undefined
        i_2 = J.undefined
        arr = J.JSArray([])
        i_2 = 0
        while J.lt(i_2, len):
            J.get(arr, "push")(None)
            i_2 = J.inc(i_2)
        return arr
    def nz(v=J.undefined, fallback=J.undefined, *_args):
        fb = J.undefined
        fb = (0 if (fallback is J.undefined) else fallback)
        if ((v is None) or (v is J.undefined)):
            return fb
        if (J.seq(J.typeof(v), "number") and J.truthy(G_isNaN(v))):
            return fb
        return v
    def fmtNum(v=J.undefined, dec=J.undefined, *_args):
        if (((v is None) or (v is J.undefined)) or J.truthy(G_isNaN(v))):
            return "---"
        return J.get(v, "toFixed")(dec)
    def smaArr(arr=J.undefined, len=J.undefined, *_args):
        m = J.undefined
        out = J.undefined
        runSum = J.undefined
        cnt = J.undefined
        i_2 = J.undefined
        v = J.undefined
        old = J.undefined
        m = J.get(arr, "length")
        out = fillNull(m)
        runSum = 0
        cnt = 0
        i_2 = 0
        while J.lt(i_2, m):
            v = J.get(arr, i_2)
            if ((v is not None) and (v is not J.undefined)):
                runSum = J.add(runSum, v)
                cnt = J.inc(cnt)
            if J.ge(i_2, len):
                old = J.get(arr, J.sub(i_2, len))
                if ((old is not None) and (old is not J.undefined)):
                    runSum = J.sub(runSum, old)
                    cnt = J.dec(cnt)
            if (J.ge(i_2, J.sub(len, 1)) and J.gt(cnt, 0)):
                J.set(out, i_2, J.div(runSum, len))
            i_2 = J.inc(i_2)
        return out
    def rmaArr(arr=J.undefined, len=J.undefined, *_args):
        m = J.undefined
        out = J.undefined
        smoothK = J.undefined
        prev = J.undefined
        i_2 = J.undefined
        m = J.get(arr, "length")
        out = fillNull(m)
        smoothK = J.div(1, len)
        prev = None
        i_2 = 0
        while J.lt(i_2, m):
            if ((J.get(arr, i_2) is None) or (J.get(arr, i_2) is J.undefined)):
                i_2 = J.inc(i_2)
                continue
            prev = (J.get(arr, i_2) if (prev is None) else J.add(J.mul(smoothK, J.get(arr, i_2)), J.mul(J.sub(1, smoothK), prev)))
            J.set(out, i_2, prev)
            i_2 = J.inc(i_2)
        return out
    def diffArr(src=J.undefined, *_args):
        m = J.undefined
        out = J.undefined
        i_2 = J.undefined
        m = J.get(src, "length")
        out = fillNull(m)
        i_2 = 1
        while J.lt(i_2, m):
            if ((J.get(src, i_2) is None) or (J.get(src, J.sub(i_2, 1)) is None)):
                i_2 = J.inc(i_2)
                continue
            J.set(out, i_2, J.sub(J.get(src, i_2), J.get(src, J.sub(i_2, 1))))
            i_2 = J.inc(i_2)
        return out
    def zScoreArr(src=J.undefined, len=J.undefined, *_args):
        m = J.undefined
        out = J.undefined
        meanArr = J.undefined
        i_2 = J.undefined
        sumSq = J.undefined
        cnt = J.undefined
        k = J.undefined
        v = J.undefined
        sd = J.undefined
        m = J.get(src, "length")
        out = fillNull(m)
        meanArr = smaArr(src, len)
        i_2 = J.sub(len, 1)
        while J.lt(i_2, m):
            if ((J.get(src, i_2) is None) or (J.get(meanArr, i_2) is None)):
                i_2 = J.inc(i_2)
                continue
            sumSq = 0
            cnt = 0
            k = 0
            while J.lt(k, len):
                v = J.get(src, J.sub(i_2, k))
                if ((v is None) or (v is J.undefined)):
                    k = J.inc(k)
                    continue
                sumSq = J.add(sumSq, J.get(G_Math, "pow")(J.sub(v, J.get(meanArr, i_2)), 2))
                cnt = J.inc(cnt)
                k = J.inc(k)
            sd = (J.get(G_Math, "sqrt")(J.div(sumSq, cnt)) if J.gt(cnt, 0) else 0)
            J.set(out, i_2, (0 if J.seq(sd, 0) else J.div(J.sub(J.get(src, i_2), J.get(meanArr, i_2)), sd)))
            i_2 = J.inc(i_2)
        return out
    def barString(val=J.undefined, slots=J.undefined, *_args):
        s = J.undefined
        filled = J.undefined
        str = J.undefined
        i_2 = J.undefined
        s = (_t1 if J.truthy(_t1 := slots) else 10)
        filled = J.get(G_Math, "max")(0, J.get(G_Math, "min")(s, J.get(G_Math, "round")(val)))
        str = ""
        i_2 = 1
        while J.le(i_2, s):
            str = J.add(str, ("█" if J.le(i_2, filled) else "░"))
            i_2 = J.inc(i_2)
        return str
    def rsiCalc(src=J.undefined, len=J.undefined, *_args):
        m = J.undefined
        gains = J.undefined
        losses = J.undefined
        i_2 = J.undefined
        chg = J.undefined
        avgG = J.undefined
        avgL = J.undefined
        out = J.undefined
        m = J.get(src, "length")
        gains = fillNull(m)
        losses = fillNull(m)
        J.set(gains, 0, 0)
        J.set(losses, 0, 0)
        i_2 = 1
        while J.lt(i_2, m):
            chg = J.sub(J.get(src, i_2), J.get(src, J.sub(i_2, 1)))
            J.set(gains, i_2, (chg if J.gt(chg, 0) else 0))
            J.set(losses, i_2, (J.neg(chg) if J.lt(chg, 0) else 0))
            i_2 = J.inc(i_2)
        avgG = rmaArr(gains, len)
        avgL = rmaArr(losses, len)
        out = fillNull(m)
        i_2 = 0
        while J.lt(i_2, m):
            if ((J.get(avgG, i_2) is None) or (J.get(avgL, i_2) is None)):
                i_2 = J.inc(i_2)
                continue
            J.set(out, i_2, (100 if J.seq(J.get(avgL, i_2), 0) else J.sub(100, J.div(100, J.add(1, J.div(J.get(avgG, i_2), J.get(avgL, i_2)))))))
            i_2 = J.inc(i_2)
        return out
    def trCalc(*_args):
        out = J.undefined
        i_2 = J.undefined
        a = J.undefined
        b = J.undefined
        c = J.undefined
        out = fillNull(G_n)
        i_2 = 0
        while J.lt(i_2, G_n):
            if J.seq(i_2, 0):
                J.set(out, i_2, J.sub(J.get(G_high, i_2), J.get(G_low, i_2)))
                i_2 = J.inc(i_2)
                continue
            a = J.sub(J.get(G_high, i_2), J.get(G_low, i_2))
            b = J.get(G_Math, "abs")(J.sub(J.get(G_high, i_2), J.get(G_close, J.sub(i_2, 1))))
            c = J.get(G_Math, "abs")(J.sub(J.get(G_low, i_2), J.get(G_close, J.sub(i_2, 1))))
            J.set(out, i_2, J.get(G_Math, "max")(a, J.get(G_Math, "max")(b, c)))
            i_2 = J.inc(i_2)
        return out
    def atrCalc(len=J.undefined, *_args):
        return rmaArr(trCalc(), len)
    def mfiCalc(len=J.undefined, *_args):
        tp = J.undefined
        mf = J.undefined
        posMF = J.undefined
        negMF = J.undefined
        i_2 = J.undefined
        posSum = J.undefined
        negSum = J.undefined
        out = J.undefined
        pS = J.undefined
        nS = J.undefined
        tp = fillNull(G_n)
        mf = fillNull(G_n)
        posMF = fillNull(G_n)
        negMF = fillNull(G_n)
        i_2 = 0
        while J.lt(i_2, G_n):
            J.set(tp, i_2, J.div(J.add(J.add(J.get(G_high, i_2), J.get(G_low, i_2)), J.get(G_close, i_2)), 3))
            J.set(mf, i_2, J.mul(J.get(tp, i_2), J.get(G_volume, i_2)))
            if J.seq(i_2, 0):
                J.set(posMF, i_2, 0)
                J.set(negMF, i_2, 0)
                i_2 = J.inc(i_2)
                continue
            if J.gt(J.get(tp, i_2), J.get(tp, J.sub(i_2, 1))):
                J.set(posMF, i_2, J.get(mf, i_2))
                J.set(negMF, i_2, 0)
            elif J.lt(J.get(tp, i_2), J.get(tp, J.sub(i_2, 1))):
                J.set(posMF, i_2, 0)
                J.set(negMF, i_2, J.get(mf, i_2))
            else:
                J.set(posMF, i_2, 0)
                J.set(negMF, i_2, 0)
            i_2 = J.inc(i_2)
        posSum = smaArr(posMF, len)
        negSum = smaArr(negMF, len)
        out = fillNull(G_n)
        i_2 = 0
        while J.lt(i_2, G_n):
            if ((J.get(posSum, i_2) is None) or (J.get(negSum, i_2) is None)):
                i_2 = J.inc(i_2)
                continue
            pS = J.mul(J.get(posSum, i_2), len)
            nS = J.mul(J.get(negSum, i_2), len)
            J.set(out, i_2, (100 if J.seq(nS, 0) else J.sub(100, J.div(100, J.add(1, J.div(pS, nS))))))
            i_2 = J.inc(i_2)
        return out
    def cciCalc(len=J.undefined, *_args):
        tp = J.undefined
        i_2 = J.undefined
        tpSma = J.undefined
        out = J.undefined
        devSum = J.undefined
        k = J.undefined
        devMean = J.undefined
        tp = fillNull(G_n)
        i_2 = 0
        while J.lt(i_2, G_n):
            J.set(tp, i_2, J.div(J.add(J.add(J.get(G_high, i_2), J.get(G_low, i_2)), J.get(G_close, i_2)), 3))
            i_2 = J.inc(i_2)
        tpSma = smaArr(tp, len)
        out = fillNull(G_n)
        i_2 = J.sub(len, 1)
        while J.lt(i_2, G_n):
            if (J.get(tpSma, i_2) is None):
                i_2 = J.inc(i_2)
                continue
            devSum = 0
            k = 0
            while J.lt(k, len):
                devSum = J.add(devSum, J.get(G_Math, "abs")(J.sub(J.get(tp, J.sub(i_2, k)), J.get(tpSma, i_2))))
                k = J.inc(k)
            devMean = J.div(devSum, len)
            J.set(out, i_2, (0 if J.seq(devMean, 0) else J.div(J.sub(J.get(tp, i_2), J.get(tpSma, i_2)), J.mul(0.015, devMean))))
            i_2 = J.inc(i_2)
        return out
    def obvCalc(*_args):
        out = J.undefined
        run = J.undefined
        i_2 = J.undefined
        out = fillNull(G_n)
        run = 0
        i_2 = 0
        while J.lt(i_2, G_n):
            if J.seq(i_2, 0):
                run = J.get(G_volume, i_2)
            elif J.gt(J.get(G_close, i_2), J.get(G_close, J.sub(i_2, 1))):
                run = J.add(run, J.get(G_volume, i_2))
            elif J.lt(J.get(G_close, i_2), J.get(G_close, J.sub(i_2, 1))):
                run = J.sub(run, J.get(G_volume, i_2))
            J.set(out, i_2, run)
            i_2 = J.inc(i_2)
        return out
    def cmfCalc(len=J.undefined, *_args):
        mfv = J.undefined
        i_2 = J.undefined
        hl = J.undefined
        mfvSma = J.undefined
        volSma = J.undefined
        out = J.undefined
        mfv = fillNull(G_n)
        i_2 = 0
        while J.lt(i_2, G_n):
            hl = J.sub(J.get(G_high, i_2), J.get(G_low, i_2))
            J.set(mfv, i_2, (0 if J.seq(hl, 0) else J.mul(J.div(J.sub(J.sub(J.get(G_close, i_2), J.get(G_low, i_2)), J.sub(J.get(G_high, i_2), J.get(G_close, i_2))), hl), J.get(G_volume, i_2))))
            i_2 = J.inc(i_2)
        mfvSma = smaArr(mfv, len)
        volSma = smaArr(G_volume, len)
        out = fillNull(G_n)
        i_2 = 0
        while J.lt(i_2, G_n):
            if (((J.get(mfvSma, i_2) is None) or (J.get(volSma, i_2) is None)) or J.seq(J.get(volSma, i_2), 0)):
                i_2 = J.inc(i_2)
                continue
            J.set(out, i_2, J.div(J.get(mfvSma, i_2), J.get(volSma, i_2)))
            i_2 = J.inc(i_2)
        return out
    def rocCalc(len=J.undefined, *_args):
        out = J.undefined
        i_2 = J.undefined
        out = fillNull(G_n)
        i_2 = len
        while J.lt(i_2, G_n):
            J.set(out, i_2, (0 if J.seq(J.get(G_close, J.sub(i_2, len)), 0) else J.mul(J.div(J.sub(J.get(G_close, i_2), J.get(G_close, J.sub(i_2, len))), J.get(G_close, J.sub(i_2, len))), 100)))
            i_2 = J.inc(i_2)
        return out
    def lowPassFilter(src=J.undefined, length=J.undefined, *_args):
        clampLen = J.undefined
        weights = J.undefined
        k = J.undefined
        out = J.undefined
        i_2 = J.undefined
        valSum = J.undefined
        wUsed = J.undefined
        idx = J.undefined
        clampLen = J.get(G_Math, "max")(length, 3)
        weights = J.JSArray([])
        k = 0
        while J.lt(k, clampLen):
            J.get(weights, "push")(J.get(G_Math, "exp")(J.div(J.neg(J.get(G_Math, "pow")(J.sub(k, J.div(J.sub(clampLen, 1), 2)), 2)), J.mul(2, J.get(G_Math, "pow")(J.div(clampLen, 4), 2)))))
            k = J.inc(k)
        out = fillNull(G_n)
        i_2 = 0
        while J.lt(i_2, G_n):
            if (J.get(src, i_2) is None):
                i_2 = J.inc(i_2)
                continue
            valSum = 0
            wUsed = 0
            k = 0
            while J.lt(k, clampLen):
                idx = J.sub(i_2, k)
                if ((J.lt(idx, 0) or (J.get(src, idx) is None)) or (J.get(src, idx) is J.undefined)):
                    k = J.inc(k)
                    continue
                valSum = J.add(valSum, J.mul(J.get(src, idx), J.get(weights, k)))
                wUsed = J.add(wUsed, J.get(weights, k))
                k = J.inc(k)
            J.set(out, i_2, (J.get(src, i_2) if J.seq(wUsed, 0) else J.div(valSum, wUsed)))
            i_2 = J.inc(i_2)
        return out
    def mulberry32(seed=J.undefined, *_args):
        s = J.undefined
        s = J.ushr(seed, 0)
        def _f1(*_args):
            nonlocal s
            t = J.undefined
            s = J.bit_or(J.add(s, 1831565813), 0)
            t = s
            t = J.get(G_Math, "imul")(J.bit_xor(t, J.ushr(t, 15)), J.bit_or(t, 1))
            t = J.bit_xor(J.add(t, J.get(G_Math, "imul")(J.bit_xor(t, J.ushr(t, 7)), J.bit_or(t, 61))), t)
            return J.div(J.ushr(J.bit_xor(t, J.ushr(t, 14)), 0), 4294967296)
        return _f1
    def betaNormalSample(a=J.undefined, b=J.undefined, rngNext=J.undefined, *_args):
        mu = J.undefined
        sig2 = J.undefined
        sig = J.undefined
        u1 = J.undefined
        u2 = J.undefined
        zz = J.undefined
        mu = J.div(a, J.add(a, b))
        sig2 = J.div(J.mul(a, b), J.mul(J.get(G_Math, "pow")(J.add(a, b), 2), J.add(J.add(a, b), 1)))
        sig = J.get(G_Math, "sqrt")(J.get(G_Math, "max")(sig2, 0))
        u1 = J.get(G_Math, "max")(J.get(G_Math, "min")(rngNext(), 0.999999), 0.000001)
        u2 = J.get(G_Math, "max")(J.get(G_Math, "min")(rngNext(), 0.999999), 0.000001)
        zz = J.mul(J.get(G_Math, "sqrt")(J.mul((-2), J.get(G_Math, "log")(u1))), J.get(G_Math, "cos")(J.mul(J.mul(2, J.get(G_Math, "PI")), u2)))
        return J.get(G_Math, "max")(J.get(G_Math, "min")(J.add(mu, J.mul(zz, sig)), 1), 0)
    def rgba(h=J.undefined, a=J.undefined, *_args):
        return J.get(J.get(G_tiny(h), "setAlpha")(a), "toRgbString")()
    def dirArrow(v=J.undefined, *_args):
        return ("▲ UP" if J.gt(nz(v, 0), 0) else "▼ DN")
    def dirColor(v=J.undefined, *_args):
        return (J.get(G_TH, "bull") if J.gt(nz(v, 0), 0) else J.get(G_TH, "bear"))
    def mkCell(t=J.undefined, c=J.undefined, a=J.undefined, b=J.undefined, cs=J.undefined, bg=J.undefined, *_args):
        return J.obj(("text", G_String(t)), ("color", (_t1 if J.truthy(_t1 := c) else J.get(G_TH, "txt"))), ("textAlign", (_t2 if J.truthy(_t2 := a) else "left")), ("fontSize", 10), ("fontWeight", ("bold" if J.truthy(b) else "normal")), ("colspan", (_t3 if J.truthy(_t3 := cs) else 1)), ("background", (_t4 if J.truthy(_t4 := bg) else J.get(G_TH, "panel"))))
    def mkSub(t=J.undefined, c=J.undefined, bg=J.undefined, *_args):
        return J.obj(("text", G_String(t)), ("color", (_t1 if J.truthy(_t1 := c) else J.get(G_TH, "a1"))), ("background", (_t2 if J.truthy(_t2 := bg) else rgba(J.get(G_TH, "a1"), 0.08))), ("textAlign", "center"), ("fontSize", 9), ("fontWeight", "bold"), ("colspan", 2))
    G_describe_indicator("Thompson-Enhanced Derivative Pattern Engine", "price", J.obj(("shortName", "⟡ TED-PE"), ("mainColorInheritFrom", "legend_anchor")))
    G_i_baseType = J.get(G_input, "select")("Base Indicator", "CCI", J.JSArray(["RSI", "MFI", "CCI", "OBV", "CMF", "ROC"]))
    G_i_baseLen = J.get(G_input, "number")("Indicator Length", 14, J.obj(("min", 2)))
    G_i_banditMode = J.get(G_input, "select")("Bandit Mode", "Stochastic", J.JSArray(["Stochastic", "Deterministic"]))
    G_i_filterPer = J.get(G_input, "number")("Filter Period", 9, J.obj(("min", 3), ("max", 30)))
    G_i_normLen = J.get(G_input, "number")("Normalization Lookback", 50, J.obj(("min", 5)))
    G_i_decay = J.get(G_input, "number")("Bandit Decay Factor", 0.999, J.obj(("min", 0.9), ("max", 1), ("step", 0.001)))
    G_i_useFilter = J.get(G_input, "boolean")("Apply Low-Pass Filter", True)
    G_i_useBandit = J.get(G_input, "boolean")("Dynamic Bayesian Weighting", True)
    G_i_searchWin = J.get(G_input, "number")("Search History Depth (Bars)", 500, J.obj(("min", 100), ("max", 1000)))
    G_i_matchCount = J.get(G_input, "number")("Analog Matches to Find", 5, J.obj(("min", 2), ("max", 10)))
    G_i_matchThr = J.get(G_input, "number")("Similarity Threshold", 0.75, J.obj(("min", 0.1), ("max", 1), ("step", 0.05)))
    G_i_projFwd = J.get(G_input, "number")("Projection Horizon (Bars)", 10, J.obj(("min", 3), ("max", 50)))
    G_i_evThresh = J.get(G_input, "number")("Minimum EV Threshold %", 0.1, J.obj(("min", 0), ("max", 5), ("step", 0.05)))
    G_i_minMatches = J.get(G_input, "number")("Minimum Analog Count", 2, J.obj(("min", 1), ("max", 10)))
    G_i_signalMode = J.get(G_input, "select")("Signal Timing", "Real-Time", J.JSArray(["Real-Time", "Confirmed (Bar Close)"]))
    G_i_atrLen = J.get(G_input, "number")("ATR Length", 14, J.obj(("min", 1)))
    G_i_atrMult = J.get(G_input, "number")("ATR Stop Multiplier", 2, J.obj(("min", 0.1), ("step", 0.1)))
    G_i_showSignals = J.get(G_input, "boolean")("Show Signal Markers", True)
    G_i_showBars = J.get(G_input, "boolean")("Color Candles by EV", True)
    G_i_showZones = J.get(G_input, "boolean")("Show TP/SL Zone", True)
    G_i_glow = J.get(G_input, "boolean")("Glow-Halo Signal Markers", True)
    G_i_theme = J.get(G_input, "select")("Dashboard", "Full", J.JSArray(["Full", "Compact", "Off"]))
    G_n = J.get(G_close, "length")
    rawBase = fillNull(G_n)
    if J.seq(G_i_baseType, "RSI"):
        rawBase = rsiCalc(G_close, G_i_baseLen)
    elif J.seq(G_i_baseType, "MFI"):
        rawBase = mfiCalc(G_i_baseLen)
    elif J.seq(G_i_baseType, "CCI"):
        rawBase = cciCalc(G_i_baseLen)
    elif J.seq(G_i_baseType, "OBV"):
        rawBase = obvCalc()
    elif J.seq(G_i_baseType, "CMF"):
        rawBase = cmfCalc(G_i_baseLen)
    else:
        rawBase = rocCalc(G_i_baseLen)
    G_baseInd = (lowPassFilter(rawBase, G_i_filterPer) if J.truthy(G_i_useFilter) else rawBase)
    G_d1 = diffArr(G_baseInd)
    G_d2 = diffArr(G_d1)
    G_d3 = diffArr(G_d2)
    G_d4 = diffArr(G_d3)
    G_nD1 = zScoreArr(G_d1, G_i_normLen)
    G_nD2 = zScoreArr(G_d2, G_i_normLen)
    G_nD3 = zScoreArr(G_d3, G_i_normLen)
    G_nD4 = zScoreArr(G_d4, G_i_normLen)
    G_normW1 = fillNull(G_n)
    G_normW2 = fillNull(G_n)
    G_normW3 = fillNull(G_n)
    G_normW4 = fillNull(G_n)
    bd1A = 1
    bd1B = 1
    bd2A = 1
    bd2B = 1
    bd3A = 1
    bd3B = 1
    bd4A = 1
    bd4B = 1
    bw1 = 1
    bw2 = 1
    bw3 = 1
    bw4 = 1
    i = 0
    while J.lt(i, G_n):
        if J.truthy(G_i_useBandit):
            if J.gt(i, G_i_projFwd):
                G_lb = J.sub(i, G_i_projFwd)
                if ((J.get(G_close, G_lb) is not None) and J.sne(J.get(G_close, G_lb), 0)):
                    G_priceChange = J.sub(J.get(G_close, i), J.get(G_close, G_lb))
                    G_priceDir = (1 if J.gt(G_priceChange, 0) else ((-1) if J.lt(G_priceChange, 0) else 0))
                    if ((((J.sne(G_priceDir, 0) and (J.get(G_nD1, G_lb) is not None)) and (J.get(G_nD2, G_lb) is not None)) and (J.get(G_nD3, G_lb) is not None)) and (J.get(G_nD4, G_lb) is not None)):
                        bd1A = J.mul(bd1A, G_i_decay)
                        bd1B = J.mul(bd1B, G_i_decay)
                        bd2A = J.mul(bd2A, G_i_decay)
                        bd2B = J.mul(bd2B, G_i_decay)
                        bd3A = J.mul(bd3A, G_i_decay)
                        bd3B = J.mul(bd3B, G_i_decay)
                        bd4A = J.mul(bd4A, G_i_decay)
                        bd4B = J.mul(bd4B, G_i_decay)
                        if ((J.gt(J.get(G_nD1, G_lb), 0) and J.seq(G_priceDir, 1)) or (J.lt(J.get(G_nD1, G_lb), 0) and J.seq(G_priceDir, (-1)))):
                            bd1A = J.add(bd1A, 1)
                        if ((J.gt(J.get(G_nD1, G_lb), 0) and J.seq(G_priceDir, (-1))) or (J.lt(J.get(G_nD1, G_lb), 0) and J.seq(G_priceDir, 1))):
                            bd1B = J.add(bd1B, 1)
                        if ((J.gt(J.get(G_nD2, G_lb), 0) and J.seq(G_priceDir, 1)) or (J.lt(J.get(G_nD2, G_lb), 0) and J.seq(G_priceDir, (-1)))):
                            bd2A = J.add(bd2A, 1)
                        if ((J.gt(J.get(G_nD2, G_lb), 0) and J.seq(G_priceDir, (-1))) or (J.lt(J.get(G_nD2, G_lb), 0) and J.seq(G_priceDir, 1))):
                            bd2B = J.add(bd2B, 1)
                        if ((J.gt(J.get(G_nD3, G_lb), 0) and J.seq(G_priceDir, 1)) or (J.lt(J.get(G_nD3, G_lb), 0) and J.seq(G_priceDir, (-1)))):
                            bd3A = J.add(bd3A, 1)
                        if ((J.gt(J.get(G_nD3, G_lb), 0) and J.seq(G_priceDir, (-1))) or (J.lt(J.get(G_nD3, G_lb), 0) and J.seq(G_priceDir, 1))):
                            bd3B = J.add(bd3B, 1)
                        if ((J.gt(J.get(G_nD4, G_lb), 0) and J.seq(G_priceDir, 1)) or (J.lt(J.get(G_nD4, G_lb), 0) and J.seq(G_priceDir, (-1)))):
                            bd4A = J.add(bd4A, 1)
                        if ((J.gt(J.get(G_nD4, G_lb), 0) and J.seq(G_priceDir, (-1))) or (J.lt(J.get(G_nD4, G_lb), 0) and J.seq(G_priceDir, 1))):
                            bd4B = J.add(bd4B, 1)
            if J.seq(G_i_banditMode, "Stochastic"):
                G_rngNext = mulberry32(J.add(i, 1))
                bw1 = betaNormalSample(bd1A, bd1B, G_rngNext)
                bw2 = betaNormalSample(bd2A, bd2B, G_rngNext)
                bw3 = betaNormalSample(bd3A, bd3B, G_rngNext)
                bw4 = betaNormalSample(bd4A, bd4B, G_rngNext)
            else:
                bw1 = J.div(bd1A, J.add(bd1A, bd1B))
                bw2 = J.div(bd2A, J.add(bd2A, bd2B))
                bw3 = J.div(bd3A, J.add(bd3A, bd3B))
                bw4 = J.div(bd4A, J.add(bd4A, bd4B))
        else:
            bw1 = 1
            bw2 = 1
            bw3 = 1
            bw4 = 1
        G_totalW = J.add(J.add(J.add(bw1, bw2), bw3), bw4)
        J.set(G_normW1, i, J.mul(J.div(bw1, G_totalW), 4))
        J.set(G_normW2, i, J.mul(J.div(bw2, G_totalW), 4))
        J.set(G_normW3, i, J.mul(J.div(bw3, G_totalW), 4))
        J.set(G_normW4, i, J.mul(J.div(bw4, G_totalW), 4))
        i = J.inc(i)
    G_atrVals = atrCalc(G_i_atrLen)
    G_actualMatchesArr = fillNull(G_n)
    G_weightedWinProbArr = fillNull(G_n)
    G_avgWinArr = fillNull(G_n)
    G_avgLossArr = fillNull(G_n)
    G_expectedValueArr = fillNull(G_n)
    G_consensusArr = fillNull(G_n)
    G_winRateArr = fillNull(G_n)
    G_avgWinAtrArr = fillNull(G_n)
    G_avgLossAtrArr = fillNull(G_n)
    G_searchStart = J.add(J.add(J.add(G_i_searchWin, G_i_projFwd), G_i_normLen), 5)
    i = G_searchStart
    while J.lt(i, G_n):
        if ((((J.get(G_nD1, i) is None) or (J.get(G_nD2, i) is None)) or (J.get(G_nD3, i) is None)) or (J.get(G_nD4, i) is None)):
            i = J.inc(i)
            continue
        G_simArr = J.JSArray([])
        G_retArr = J.JSArray([])
        G_retArrAtr = J.JSArray([])
        G_lowBound = J.get(G_Math, "max")(0, J.sub(i, G_i_searchWin))
        G_highBound = J.sub(i, G_i_projFwd)
        j = G_lowBound
        while J.le(j, G_highBound):
            if ((((J.get(G_nD1, j) is None) or (J.get(G_nD2, j) is None)) or (J.get(G_nD3, j) is None)) or (J.get(G_nD4, j) is None)):
                j = J.inc(j)
                continue
            sq = 0
            sq = J.add(sq, J.mul(J.get(G_normW1, i), J.get(G_Math, "pow")(J.sub(J.get(G_nD1, i), J.get(G_nD1, j)), 2)))
            sq = J.add(sq, J.mul(J.get(G_normW2, i), J.get(G_Math, "pow")(J.sub(J.get(G_nD2, i), J.get(G_nD2, j)), 2)))
            sq = J.add(sq, J.mul(J.get(G_normW3, i), J.get(G_Math, "pow")(J.sub(J.get(G_nD3, i), J.get(G_nD3, j)), 2)))
            sq = J.add(sq, J.mul(J.get(G_normW4, i), J.get(G_Math, "pow")(J.sub(J.get(G_nD4, i), J.get(G_nD4, j)), 2)))
            G_dist = J.get(G_Math, "sqrt")(sq)
            G_sim = J.div(1, J.add(1, G_dist))
            if J.ge(G_sim, G_i_matchThr):
                G_fwdIdx = J.add(j, G_i_projFwd)
                G_atrAtJ = nz(J.get(G_atrVals, j), 0)
                if ((J.lt(G_fwdIdx, G_n) and J.sne(J.get(G_close, j), 0)) and J.gt(G_atrAtJ, 0)):
                    J.get(G_simArr, "push")(G_sim)
                    J.get(G_retArr, "push")(J.div(J.sub(J.get(G_close, G_fwdIdx), J.get(G_close, j)), J.get(G_close, j)))
                    J.get(G_retArrAtr, "push")(J.div(J.sub(J.get(G_close, G_fwdIdx), J.get(G_close, j)), G_atrAtJ))
            j = J.inc(j)
        G_mLen = J.get(G_simArr, "length")
        a1 = 0
        while J.lt(a1, J.sub(G_mLen, 1)):
            bestIdx = a1
            a2 = J.add(a1, 1)
            while J.lt(a2, G_mLen):
                if J.gt(J.get(G_simArr, a2), J.get(G_simArr, bestIdx)):
                    bestIdx = a2
                a2 = J.inc(a2)
            if J.sne(bestIdx, a1):
                G_ts = J.get(G_simArr, a1)
                J.set(G_simArr, a1, J.get(G_simArr, bestIdx))
                J.set(G_simArr, bestIdx, G_ts)
                G_tr = J.get(G_retArr, a1)
                J.set(G_retArr, a1, J.get(G_retArr, bestIdx))
                J.set(G_retArr, bestIdx, G_tr)
                G_tra = J.get(G_retArrAtr, a1)
                J.set(G_retArrAtr, a1, J.get(G_retArrAtr, bestIdx))
                J.set(G_retArrAtr, bestIdx, G_tra)
            a1 = J.inc(a1)
        G_actualMatches = J.get(G_Math, "min")(G_mLen, G_i_matchCount)
        J.set(G_actualMatchesArr, i, G_actualMatches)
        if J.gt(G_actualMatches, 0):
            sumW = 0
            sumWRet = 0
            sumWWin = 0
            sumWUpRet = 0
            sumWUpW = 0
            sumWDownRet = 0
            sumWDownW = 0
            winCnt = 0
            sumWUpRetAtr = 0
            sumWDownRetAtr = 0
            kk = 0
            while J.lt(kk, G_actualMatches):
                G_sim2 = J.get(G_simArr, kk)
                G_ret2 = J.get(G_retArr, kk)
                G_ret2Atr = J.get(G_retArrAtr, kk)
                sumW = J.add(sumW, G_sim2)
                sumWRet = J.add(sumWRet, J.mul(G_sim2, G_ret2))
                if J.gt(G_ret2, 0):
                    winCnt = J.add(winCnt, 1)
                    sumWWin = J.add(sumWWin, G_sim2)
                    sumWUpRet = J.add(sumWUpRet, J.mul(G_sim2, G_ret2))
                    sumWUpW = J.add(sumWUpW, G_sim2)
                    sumWUpRetAtr = J.add(sumWUpRetAtr, J.mul(G_sim2, G_ret2Atr))
                else:
                    sumWDownRet = J.add(sumWDownRet, J.mul(G_sim2, J.get(G_Math, "abs")(G_ret2)))
                    sumWDownW = J.add(sumWDownW, G_sim2)
                    sumWDownRetAtr = J.add(sumWDownRetAtr, J.mul(G_sim2, J.get(G_Math, "abs")(G_ret2Atr)))
                kk = J.inc(kk)
            G_wWinProb = (J.div(sumWWin, sumW) if J.gt(sumW, 0) else 0)
            G_aWin = (J.mul(J.div(sumWUpRet, sumWUpW), 100) if J.gt(sumWUpW, 0) else 0)
            G_aLoss = (J.mul(J.div(sumWDownRet, sumWDownW), 100) if J.gt(sumWDownW, 0) else 0)
            G_ev = J.sub(J.mul(G_wWinProb, G_aWin), J.mul(J.sub(1, G_wWinProb), G_aLoss))
            J.set(G_weightedWinProbArr, i, G_wWinProb)
            J.set(G_avgWinArr, i, G_aWin)
            J.set(G_avgLossArr, i, G_aLoss)
            J.set(G_expectedValueArr, i, G_ev)
            J.set(G_consensusArr, i, J.get(G_Math, "max")(J.get(G_Math, "min")(J.mul(G_ev, 20), 100), (-100)))
            J.set(G_winRateArr, i, J.mul(J.div(winCnt, G_actualMatches), 100))
            J.set(G_avgWinAtrArr, i, (J.div(sumWUpRetAtr, sumWUpW) if J.gt(sumWUpW, 0) else 0))
            J.set(G_avgLossAtrArr, i, (J.div(sumWDownRetAtr, sumWDownW) if J.gt(sumWDownW, 0) else 0))
        else:
            J.set(G_weightedWinProbArr, i, 0)
            J.set(G_avgWinArr, i, 0)
            J.set(G_avgLossArr, i, 0)
            J.set(G_expectedValueArr, i, 0)
            J.set(G_consensusArr, i, 0)
            J.set(G_winRateArr, i, 0)
            J.set(G_avgWinAtrArr, i, 0)
            J.set(G_avgLossAtrArr, i, 0)
        i = J.inc(i)
    G_buyStateArr = fillNull(G_n)
    G_sellStateArr = fillNull(G_n)
    i = 0
    while J.lt(i, G_n):
        G_am = nz(J.get(G_actualMatchesArr, i), 0)
        G_ev = nz(J.get(G_expectedValueArr, i), 0)
        G_wp = nz(J.get(G_weightedWinProbArr, i), 0)
        J.set(G_buyStateArr, i, (1 if ((J.ge(G_am, G_i_minMatches) and J.ge(G_ev, G_i_evThresh)) and J.gt(G_wp, 0.5)) else 0))
        J.set(G_sellStateArr, i, (1 if ((J.ge(G_am, G_i_minMatches) and J.le(G_ev, J.neg(G_i_evThresh))) and J.lt(G_wp, 0.5)) else 0))
        i = J.inc(i)
    G_finalBuyArr = fillNull(G_n)
    G_finalSellArr = fillNull(G_n)
    i = 1
    while J.lt(i, G_n):
        J.set(G_finalBuyArr, i, (J.seq(J.get(G_buyStateArr, J.sub(i, 1)), 0) if J.truthy(_t1 := (J.seq(J.get(G_buyStateArr, i), 1) if J.truthy(_t2 := G_i_showSignals) else _t2)) else _t1))
        J.set(G_finalSellArr, i, (J.seq(J.get(G_sellStateArr, J.sub(i, 1)), 0) if J.truthy(_t3 := (J.seq(J.get(G_sellStateArr, i), 1) if J.truthy(_t4 := G_i_showSignals) else _t4)) else _t3))
        i = J.inc(i)
    if (J.seq(G_i_signalMode, "Confirmed (Bar Close)") and J.gt(G_n, 0)):
        J.set(G_finalBuyArr, J.sub(G_n, 1), False)
        J.set(G_finalSellArr, J.sub(G_n, 1), False)
    G_tpLineArr = fillNull(G_n)
    G_slLineArr = fillNull(G_n)
    tradeDir = 0
    activeTp = None
    activeSl = None
    barsInTrade = 0
    tradeStatus = "Flat"
    i = 0
    while J.lt(i, G_n):
        if J.sne(tradeDir, 0):
            barsInTrade = J.add(barsInTrade, 1)
            if (J.seq(tradeDir, 1) and J.ge(J.get(G_high, i), activeTp)):
                tradeStatus = "TP Hit (Long)"
                tradeDir = 0
            elif (J.seq(tradeDir, 1) and J.le(J.get(G_low, i), activeSl)):
                tradeStatus = "SL Hit (Long)"
                tradeDir = 0
            elif (J.seq(tradeDir, (-1)) and J.le(J.get(G_low, i), activeTp)):
                tradeStatus = "TP Hit (Short)"
                tradeDir = 0
            elif (J.seq(tradeDir, (-1)) and J.ge(J.get(G_high, i), activeSl)):
                tradeStatus = "SL Hit (Short)"
                tradeDir = 0
            elif J.ge(barsInTrade, G_i_projFwd):
                tradeStatus = "Time Exit"
                tradeDir = 0
        if J.seq(tradeDir, 0):
            activeTp = None
            activeSl = None
        if J.truthy(J.get(G_finalBuyArr, i)):
            activeTp = J.add(J.get(G_close, i), J.mul(nz(J.get(G_avgWinAtrArr, i), 0), nz(J.get(G_atrVals, i), 0)))
            activeSl = J.sub(J.get(G_close, i), J.mul(nz(J.get(G_atrVals, i), 0), G_i_atrMult))
            tradeDir = 1
            barsInTrade = 0
            tradeStatus = "Long Active"
        elif J.truthy(J.get(G_finalSellArr, i)):
            activeTp = J.sub(J.get(G_close, i), J.mul(nz(J.get(G_avgLossAtrArr, i), 0), nz(J.get(G_atrVals, i), 0)))
            activeSl = J.add(J.get(G_close, i), J.mul(nz(J.get(G_atrVals, i), 0), G_i_atrMult))
            tradeDir = (-1)
            barsInTrade = 0
            tradeStatus = "Short Active"
        J.set(G_tpLineArr, i, (activeTp if J.truthy(G_i_showZones) else None))
        J.set(G_slLineArr, i, (activeSl if J.truthy(G_i_showZones) else None))
        i = J.inc(i)
    G_TH = J.obj(("bull", "#00FF88"), ("bear", "#FF3C00"), ("bullDim", "rgba(0,255,136,0.35)"), ("bearDim", "rgba(255,60,0,0.35)"), ("glowBull", "rgba(0,255,136,0.16)"), ("glowBear", "rgba(255,60,0,0.16)"), ("zoneBull", "rgba(0,255,136,0.08)"), ("zoneBear", "rgba(255,60,0,0.08)"), ("gold", "#FFD700"), ("cyan", "#00F5E9"), ("d1", "#00FF88"), ("d2", "#00D9FF"), ("d3", "#FFA500"), ("d4", "#FF3C60"), ("panel", "#0A0A14"), ("border", "#333344"), ("a1", "#00F5E9"), ("a2", "#9D4EDD"), ("txt", "#E2F1FF"), ("dim", "#8888AA"))
    G_tiny = G_library("tinycolor2")
    G_glowBuyOuter = fillNull(G_n)
    G_glowBuyInner = fillNull(G_n)
    G_markerBuy = fillNull(G_n)
    G_glowSellOuter = fillNull(G_n)
    G_glowSellInner = fillNull(G_n)
    G_markerSell = fillNull(G_n)
    i = 0
    while J.lt(i, G_n):
        if J.truthy(J.get(G_finalBuyArr, i)):
            if J.truthy(G_i_glow):
                J.set(G_glowBuyOuter, i, "●")
                J.set(G_glowBuyInner, i, "●")
            J.set(G_markerBuy, i, "▲")
        if J.truthy(J.get(G_finalSellArr, i)):
            if J.truthy(G_i_glow):
                J.set(G_glowSellOuter, i, "●")
                J.set(G_glowSellInner, i, "●")
            J.set(G_markerSell, i, "▼")
        i = J.inc(i)
    G_paint(G_glowBuyOuter, J.obj(("name", "Buy Glow Outer"), ("style", "labels_below"), ("color", J.get(G_TH, "glowBull")), ("size", "large")))
    G_paint(G_glowBuyInner, J.obj(("name", "Buy Glow Inner"), ("style", "labels_below"), ("color", J.get(G_TH, "bullDim")), ("size", "normal")))
    G_paint(G_markerBuy, J.obj(("name", "Buy Signal"), ("style", "labels_below"), ("color", J.get(G_TH, "bull")), ("size", "normal")))
    G_paint(G_glowSellOuter, J.obj(("name", "Sell Glow Outer"), ("style", "labels_above"), ("color", J.get(G_TH, "glowBear")), ("size", "large")))
    G_paint(G_glowSellInner, J.obj(("name", "Sell Glow Inner"), ("style", "labels_above"), ("color", J.get(G_TH, "bearDim")), ("size", "normal")))
    G_paint(G_markerSell, J.obj(("name", "Sell Signal"), ("style", "labels_above"), ("color", J.get(G_TH, "bear")), ("size", "normal")))
    G_barColArr = fillNull(G_n)
    i = 0
    while J.lt(i, G_n):
        if (not J.truthy(G_i_showBars)):
            i = J.inc(i)
            continue
        G_ev = J.get(G_expectedValueArr, i)
        if (G_ev is None):
            i = J.inc(i)
            continue
        if J.ge(G_ev, G_i_evThresh):
            J.set(G_barColArr, i, J.get(G_TH, "bull"))
        elif J.le(G_ev, J.neg(G_i_evThresh)):
            J.set(G_barColArr, i, J.get(G_TH, "bear"))
        i = J.inc(i)
    G_color_candles(G_barColArr, J.obj(("name", "EV Candle Color")))
    G_paint(G_tpLineArr, J.obj(("name", "Take Profit"), ("color", J.get(G_TH, "bull")), ("style", "dotted"), ("thickness", 2)))
    G_paint(G_slLineArr, J.obj(("name", "Stop Loss"), ("color", J.get(G_TH, "bear")), ("style", "dotted"), ("thickness", 2)))
    G_bullZoneTop = fillNull(G_n)
    G_bullZoneBot = fillNull(G_n)
    G_bearZoneTop = fillNull(G_n)
    G_bearZoneBot = fillNull(G_n)
    i = 0
    while J.lt(i, G_n):
        if ((J.get(G_tpLineArr, i) is None) or (J.get(G_slLineArr, i) is None)):
            i = J.inc(i)
            continue
        if J.gt(J.get(G_tpLineArr, i), J.get(G_slLineArr, i)):
            J.set(G_bullZoneTop, i, J.get(G_tpLineArr, i))
            J.set(G_bullZoneBot, i, J.get(G_slLineArr, i))
        else:
            J.set(G_bearZoneTop, i, J.get(G_slLineArr, i))
            J.set(G_bearZoneBot, i, J.get(G_tpLineArr, i))
        i = J.inc(i)
    G_color_cloud(G_bullZoneTop, G_bullZoneBot, J.get(G_TH, "zoneBull"), J.get(G_TH, "zoneBull"), "Bull Zone Top", "Bull Zone Bottom")
    G_color_cloud(G_bearZoneTop, G_bearZoneBot, J.get(G_TH, "zoneBear"), J.get(G_TH, "zoneBear"), "Bear Zone Top", "Bear Zone Bottom")
    G_lastIdx = J.get(G_Math, "max")(J.sub(G_n, 1), 0)
    G_tpLabelY = (J.get(G_tpLineArr, J.sub(G_n, 1)) if (J.gt(G_n, 0) and (J.get(G_tpLineArr, J.sub(G_n, 1)) is not None)) else nz(J.get(G_close, G_lastIdx), 0))
    G_slLabelY = (J.get(G_slLineArr, J.sub(G_n, 1)) if (J.gt(G_n, 0) and (J.get(G_slLineArr, J.sub(G_n, 1)) is not None)) else nz(J.get(G_close, G_lastIdx), 0))
    G_tpLabelText = (J.add("TP ", fmtNum(J.get(G_tpLineArr, J.sub(G_n, 1)), 5)) if (J.gt(G_n, 0) and (J.get(G_tpLineArr, J.sub(G_n, 1)) is not None)) else "TP —")
    G_slLabelText = (J.add("SL ", fmtNum(J.get(G_slLineArr, J.sub(G_n, 1)), 5)) if (J.gt(G_n, 0) and (J.get(G_slLineArr, J.sub(G_n, 1)) is not None)) else "SL —")
    G_tpLabelPts = fillNull(G_n)
    J.set(G_tpLabelPts, G_lastIdx, G_tpLabelY)
    G_slLabelPts = fillNull(G_n)
    J.set(G_slLabelPts, G_lastIdx, G_slLabelY)
    G_rTpLabel = G_paint(G_tpLabelPts, J.obj(("name", "TP Label Anchor"), ("color", "transparent"), ("affects_scale", False), ("show_in_legend", False)))
    G_rSlLabel = G_paint(G_slLabelPts, J.obj(("name", "SL Label Anchor"), ("color", "transparent"), ("affects_scale", False), ("show_in_legend", False)))
    G_paint_label_at_line(G_rTpLabel, G_lastIdx, G_tpLabelText, J.obj(("color", J.get(G_TH, "bull")), ("background_color", "transparent"), ("border_width", 0), ("vertical_align", "middle")))
    G_paint_label_at_line(G_rSlLabel, G_lastIdx, G_slLabelText, J.obj(("color", J.get(G_TH, "bear")), ("background_color", "transparent"), ("border_width", 0), ("vertical_align", "middle")))
    G_register_signal(G_finalBuyArr, "TED-PE Buy")
    G_register_signal(G_finalSellArr, "TED-PE Sell")
    G_last = J.sub(G_n, 1)
    G_l_nD1 = (J.get(G_nD1, G_last) if J.ge(G_last, 0) else None)
    G_l_nD2 = (J.get(G_nD2, G_last) if J.ge(G_last, 0) else None)
    G_l_nD3 = (J.get(G_nD3, G_last) if J.ge(G_last, 0) else None)
    G_l_nD4 = (J.get(G_nD4, G_last) if J.ge(G_last, 0) else None)
    G_l_w1 = (J.get(G_normW1, G_last) if J.ge(G_last, 0) else None)
    G_l_w2 = (J.get(G_normW2, G_last) if J.ge(G_last, 0) else None)
    G_l_w3 = (J.get(G_normW3, G_last) if J.ge(G_last, 0) else None)
    G_l_w4 = (J.get(G_normW4, G_last) if J.ge(G_last, 0) else None)
    G_l_matches = (nz(J.get(G_actualMatchesArr, G_last), 0) if J.ge(G_last, 0) else 0)
    G_l_winRate = (nz(J.get(G_winRateArr, G_last), 0) if J.ge(G_last, 0) else 0)
    G_l_wp = (nz(J.get(G_weightedWinProbArr, G_last), 0) if J.ge(G_last, 0) else 0)
    G_l_avgWin = (nz(J.get(G_avgWinArr, G_last), 0) if J.ge(G_last, 0) else 0)
    G_l_avgLoss = (nz(J.get(G_avgLossArr, G_last), 0) if J.ge(G_last, 0) else 0)
    G_l_ev = (nz(J.get(G_expectedValueArr, G_last), 0) if J.ge(G_last, 0) else 0)
    G_l_rr = (J.div(G_l_avgWin, G_l_avgLoss) if J.gt(G_l_avgLoss, 0) else None)
    G_e_d1 = J.get(G_Math, "min")(J.mul(J.get(G_Math, "abs")(nz(G_l_nD1, 0)), 2.5), 10)
    G_e_d2 = J.get(G_Math, "min")(J.mul(J.get(G_Math, "abs")(nz(G_l_nD2, 0)), 2.5), 10)
    G_e_d3 = J.get(G_Math, "min")(J.mul(J.get(G_Math, "abs")(nz(G_l_nD3, 0)), 2.5), 10)
    G_e_d4 = J.get(G_Math, "min")(J.mul(J.get(G_Math, "abs")(nz(G_l_nD4, 0)), 2.5), 10)
    G_totalEnergy = J.add(J.add(J.add(J.get(G_Math, "abs")(nz(G_l_nD1, 0)), J.get(G_Math, "abs")(nz(G_l_nD2, 0))), J.get(G_Math, "abs")(nz(G_l_nD3, 0))), J.get(G_Math, "abs")(nz(G_l_nD4, 0)))
    G_pctEnergy = J.get(G_Math, "min")(J.mul(J.div(G_totalEnergy, 16), 100), 100)
    G_energyColor = ("#FF3C00" if J.gt(G_totalEnergy, 6) else ("#FFA500" if J.gt(G_totalEnergy, 4) else ("#9D4EDD" if J.gt(G_totalEnergy, 2) else "#666677")))
    G_statsRows = J.JSArray([])
    if J.sne(G_i_theme, "Off"):
        G_statusColor = (J.get(G_TH, "bull") if J.seq(tradeDir, 1) else (J.get(G_TH, "bear") if J.seq(tradeDir, (-1)) else J.get(G_TH, "dim")))
        J.get(G_statsRows, "push")(J.obj(("cells", J.JSArray([mkCell("⟡ TED-PE STATS", J.get(G_TH, "a1"), "center", True, 2, J.get(G_TH, "panel"))]))))
        G_barsNeeded = J.add(J.add(J.add(G_i_searchWin, G_i_projFwd), G_i_normLen), 5)
        G_barsOk = J.ge(G_n, G_barsNeeded)
        J.get(G_statsRows, "push")(J.obj(("cells", J.JSArray([mkCell("Bars Loaded / Needed", J.get(G_TH, "dim"), "left", False, 1), mkCell(J.add(J.add(G_n, " / "), G_barsNeeded), (J.get(G_TH, "bull") if J.truthy(G_barsOk) else J.get(G_TH, "bear")), "right", True, 1)]))))
        if (not J.truthy(G_barsOk)):
            J.get(G_statsRows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", "⚠ Not enough history — lower Search Depth"), ("color", "#ffffff"), ("background", rgba(J.get(G_TH, "bear"), 0.35)), ("colspan", 2), ("textAlign", "center"), ("fontSize", 8.5), ("fontWeight", "bold"))]))))
        J.get(G_statsRows, "push")(J.obj(("cells", J.JSArray([mkCell("d1 Velocity", J.get(G_TH, "dim"), "left", False, 1), mkCell(J.add(fmtNum(G_l_w1, 2), "x"), J.get(G_TH, "d1"), "right", True, 1)]))))
        J.get(G_statsRows, "push")(J.obj(("cells", J.JSArray([mkCell("d2 Accel", J.get(G_TH, "dim"), "left", False, 1), mkCell(J.add(fmtNum(G_l_w2, 2), "x"), J.get(G_TH, "d2"), "right", True, 1)]))))
        if J.seq(G_i_theme, "Full"):
            J.get(G_statsRows, "push")(J.obj(("cells", J.JSArray([mkCell("d3 Jerk", J.get(G_TH, "dim"), "left", False, 1), mkCell(J.add(fmtNum(G_l_w3, 2), "x"), J.get(G_TH, "d3"), "right", True, 1)]))))
            J.get(G_statsRows, "push")(J.obj(("cells", J.JSArray([mkCell("d4 Snap", J.get(G_TH, "dim"), "left", False, 1), mkCell(J.add(fmtNum(G_l_w4, 2), "x"), J.get(G_TH, "d4"), "right", True, 1)]))))
        J.get(G_statsRows, "push")(J.obj(("cells", J.JSArray([mkSub("» ANALOG SEARCH")]))))
        J.get(G_statsRows, "push")(J.obj(("cells", J.JSArray([mkCell("Analogs / Win%", J.get(G_TH, "dim"), "left", False, 1), mkCell(J.add(J.add(J.add(G_l_matches, " / "), fmtNum(G_l_winRate, 1)), "%"), J.get(G_TH, "txt"), "right", True, 1)]))))
        J.get(G_statsRows, "push")(J.obj(("cells", J.JSArray([mkCell("Weighted WinProb", J.get(G_TH, "dim"), "left", False, 1), mkCell(J.add(fmtNum(J.mul(G_l_wp, 100), 1), "%"), (J.get(G_TH, "bull") if J.gt(G_l_wp, 0.5) else J.get(G_TH, "bear")), "right", True, 1)]))))
        if J.seq(G_i_theme, "Full"):
            J.get(G_statsRows, "push")(J.obj(("cells", J.JSArray([mkCell("Avg Win / Loss", J.get(G_TH, "dim"), "left", False, 1), mkCell(J.add(J.add(J.add(fmtNum(G_l_avgWin, 2), "% / "), fmtNum(G_l_avgLoss, 2)), "%"), J.get(G_TH, "txt"), "right", True, 1)]))))
            J.get(G_statsRows, "push")(J.obj(("cells", J.JSArray([mkCell("Reward:Risk", J.get(G_TH, "dim"), "left", False, 1), mkCell(("n/a" if (G_l_rr is None) else fmtNum(G_l_rr, 2)), J.get(G_TH, "txt"), "right", True, 1)]))))
        J.get(G_statsRows, "push")(J.obj(("cells", J.JSArray([mkCell("Expected Value", J.get(G_TH, "dim"), "left", False, 1), mkCell(J.add(fmtNum(G_l_ev, 3), "%"), (J.get(G_TH, "bull") if J.ge(G_l_ev, 0) else J.get(G_TH, "bear")), "right", True, 1)]))))
        J.get(G_statsRows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", tradeStatus), ("color", "#ffffff"), ("background", G_statusColor), ("colspan", 2), ("textAlign", "center"), ("fontSize", 9), ("fontWeight", "bold"))]))))
    G_paint_overlay("TED-PE Stats Dashboard", J.obj(("position", "top_right"), ("order", "above_all")), J.obj(("background", rgba(J.get(G_TH, "panel"), 0.95)), ("border", J.add("1px solid ", J.get(G_TH, "border"))), ("borderRadius", 4), ("width", 200), ("rows", G_statsRows)))
    G_energyRows = J.JSArray([])
    if J.seq(G_i_theme, "Full"):
        J.get(G_energyRows, "push")(J.obj(("cells", J.JSArray([mkCell("⚡ DERIVATIVE ENERGY", J.get(G_TH, "a2"), "center", True, 2, J.get(G_TH, "panel"))]))))
        J.get(G_energyRows, "push")(J.obj(("cells", J.JSArray([mkCell(J.add("d1 ", dirArrow(G_l_nD1)), dirColor(G_l_nD1), "left", False, 1), mkCell(barString(G_e_d1), dirColor(G_l_nD1), "right", False, 1)]))))
        J.get(G_energyRows, "push")(J.obj(("cells", J.JSArray([mkCell(J.add("d2 ", dirArrow(G_l_nD2)), dirColor(G_l_nD2), "left", False, 1), mkCell(barString(G_e_d2), dirColor(G_l_nD2), "right", False, 1)]))))
        J.get(G_energyRows, "push")(J.obj(("cells", J.JSArray([mkCell(J.add("d3 ", dirArrow(G_l_nD3)), dirColor(G_l_nD3), "left", False, 1), mkCell(barString(G_e_d3), dirColor(G_l_nD3), "right", False, 1)]))))
        J.get(G_energyRows, "push")(J.obj(("cells", J.JSArray([mkCell(J.add("d4 ", dirArrow(G_l_nD4)), dirColor(G_l_nD4), "left", False, 1), mkCell(barString(G_e_d4), dirColor(G_l_nD4), "right", False, 1)]))))
        J.get(G_energyRows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", "Total Energy"), ("color", "#ffffff"), ("background", G_energyColor), ("textAlign", "left"), ("fontSize", 9), ("fontWeight", "bold")), J.obj(("text", J.add(J.add(J.add(fmtNum(G_totalEnergy, 2), " ("), fmtNum(G_pctEnergy, 1)), "%)")), ("color", "#ffffff"), ("background", G_energyColor), ("textAlign", "right"), ("fontSize", 9), ("fontWeight", "bold"))]))))
    G_paint_overlay("TED-PE Energy Dashboard", J.obj(("position", "bottom_right"), ("order", "above_all")), J.obj(("background", rgba(J.get(G_TH, "panel"), 0.95)), ("border", J.add("1px solid ", J.get(G_TH, "border"))), ("borderRadius", 4), ("width", 220), ("rows", G_energyRows)))


register_store_indicator(
    script,
    name='thompson_enhanced_derivative_pattern_engine_TS',
    title='Thompson-Enhanced Derivative Pattern Engine',
    developer='DskyzInvestments',
    url='https://trendspider.com/trading-tools-store/indicators/6a4ab0-thompson-enhanced-derivative-pattern-engine/',
    position='price',
    inputs=[{'id': 'base_indicator', 'title': 'Base Indicator', 'type': 'select_wide', 'default': 'CCI', 'options': ['RSI', 'MFI', 'CCI', 'OBV', 'CMF', 'ROC']}, {'id': 'indicator_length', 'title': 'Indicator Length', 'type': 'number', 'default': 14}, {'id': 'bandit_mode', 'title': 'Bandit Mode', 'type': 'select_wide', 'default': 'Stochastic', 'options': ['Stochastic', 'Deterministic']}, {'id': 'filter_period', 'title': 'Filter Period', 'type': 'number', 'default': 9}, {'id': 'normalization_lookback', 'title': 'Normalization Lookback', 'type': 'number', 'default': 50}, {'id': 'bandit_decay_factor', 'title': 'Bandit Decay Factor', 'type': 'number', 'default': 0.999}, {'id': 'apply_low_pass_filter', 'title': 'Apply Low-Pass Filter', 'type': 'boolean', 'default': True}, {'id': 'dynamic_bayesian_weighting', 'title': 'Dynamic Bayesian Weighting', 'type': 'boolean', 'default': True}, {'id': 'search_history_depth__bars_', 'title': 'Search History Depth (Bars)', 'type': 'number', 'default': 500}, {'id': 'analog_matches_to_find', 'title': 'Analog Matches to Find', 'type': 'number', 'default': 5}, {'id': 'similarity_threshold', 'title': 'Similarity Threshold', 'type': 'number', 'default': 0.75}, {'id': 'projection_horizon__bars_', 'title': 'Projection Horizon (Bars)', 'type': 'number', 'default': 10}, {'id': 'minimum_ev_threshold__', 'title': 'Minimum EV Threshold %', 'type': 'number', 'default': 0.1}, {'id': 'minimum_analog_count', 'title': 'Minimum Analog Count', 'type': 'number', 'default': 2}, {'id': 'signal_timing', 'title': 'Signal Timing', 'type': 'select_wide', 'default': 'Real-Time', 'options': ['Real-Time', 'Confirmed (Bar Close)']}, {'id': 'atr_length', 'title': 'ATR Length', 'type': 'number', 'default': 14}, {'id': 'atr_stop_multiplier', 'title': 'ATR Stop Multiplier', 'type': 'number', 'default': 2}, {'id': 'show_signal_markers', 'title': 'Show Signal Markers', 'type': 'boolean', 'default': True}, {'id': 'color_candles_by_ev', 'title': 'Color Candles by EV', 'type': 'boolean', 'default': True}, {'id': 'show_tp_sl_zone', 'title': 'Show TP/SL Zone', 'type': 'boolean', 'default': True}, {'id': 'glow_halo_signal_markers', 'title': 'Glow-Halo Signal Markers', 'type': 'boolean', 'default': True}, {'id': 'dashboard', 'title': 'Dashboard', 'type': 'select_wide', 'default': 'Full', 'options': ['Full', 'Compact', 'Off']}],
    outputs=['buy_glow_outer', 'buy_glow_inner', 'buy_signal', 'sell_glow_outer', 'sell_glow_inner', 'sell_signal', 'cdl', 'take_profit', 'stop_loss', 'line_10', 'line_11', 'line_13', 'line_14', 'line_16', 'line_17', 'line_19', 'line_20', 'tp_label_anchor', 'sl_label_anchor', 'ted_pe_buy', 'ted_pe_sell'],
    signals=['ted_pe_buy', 'ted_pe_sell'],
    requires=[],
    parity='exact',
)
