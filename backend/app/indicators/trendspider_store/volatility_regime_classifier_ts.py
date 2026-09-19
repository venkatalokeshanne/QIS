"""
Volatility Regime Classifier -- TrendSpider store indicator by Gustivus.

Registered as "volatility_regime_classifier_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6918c7-volatility-regime-classifier/)
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
    G_high = G["high"]
    G_horizontal_line = G["horizontal_line"]
    G_input = G["input"]
    G_low = G["low"]
    G_open = G["open"]
    G_paint = G["paint"]
    G_paint_overlay = G["paint_overlay"]
    G_register_signal = G["register_signal"]
    G_series_of = G["series_of"]
    def calcSMA(data=J.undefined, period=J.undefined, idx=J.undefined, *_args):
        if J.lt(idx, J.sub(period, 1)):
            return J.get(data, idx)
        total = 0
        i = 0
        while J.lt(i, period):
            total = J.add(total, J.get(data, J.sub(idx, i)))
            i = J.inc(i)
        return J.div(total, period)
    def calcEMA(data=J.undefined, period=J.undefined, idx=J.undefined, prevEMA_2=J.undefined, *_args):
        if J.seq(idx, 0):
            return J.get(data, 0)
        alpha = J.div(2, J.add(period, 1))
        return J.add(J.mul(alpha, J.get(data, idx)), J.mul(J.sub(1, alpha), (_t1 if J.truthy(_t1 := prevEMA_2) else J.get(data, idx))))
    def calcStdDev(data=J.undefined, period=J.undefined, idx=J.undefined, *_args):
        if J.lt(idx, J.sub(period, 1)):
            return 0
        mean = calcSMA(data, period, idx)
        sumSquaredDiff = 0
        i = 0
        while J.lt(i, period):
            diff = J.sub(J.get(data, J.sub(idx, i)), mean)
            sumSquaredDiff = J.add(sumSquaredDiff, J.mul(diff, diff))
            i = J.inc(i)
        return J.get(G_Math, "sqrt")(J.div(sumSquaredDiff, period))
    def calcPercentile(data=J.undefined, period=J.undefined, idx=J.undefined, percentile=J.undefined, *_args):
        if J.lt(idx, J.sub(period, 1)):
            return J.get(data, idx)
        window = J.JSArray([])
        i = 0
        while J.lt(i, period):
            J.get(window, "push")(J.get(data, J.sub(idx, i)))
            i = J.inc(i)
        def _f1(a=J.undefined, b=J.undefined, *_args):
            return J.sub(a, b)
        J.get(window, "sort")(_f1)
        index = J.get(G_Math, "floor")(J.mul(J.get(window, "length"), percentile))
        return J.get(window, index)
    def calcParkinsonVolatility(high=J.undefined, low=J.undefined, period=J.undefined, idx=J.undefined, *_args):
        if J.lt(idx, J.sub(period, 1)):
            return 0
        sumLogRatioSquared = 0
        i = 0
        while J.lt(i, period):
            h = J.get(high, J.sub(idx, i))
            l = J.get(low, J.sub(idx, i))
            if (J.gt(l, 0) and J.gt(h, 0)):
                logRatio = J.get(G_Math, "log")(J.div(h, l))
                sumLogRatioSquared = J.add(sumLogRatioSquared, J.mul(logRatio, logRatio))
            i = J.inc(i)
        parkinsonConstant = J.div(1, J.mul(4, J.get(G_Math, "log")(2)))
        varianceVal = J.mul(parkinsonConstant, J.div(sumLogRatioSquared, period))
        return J.mul(J.get(G_Math, "sqrt")(J.mul(varianceVal, 252)), 100)
    def calcGarmanKlassVolatility(open=J.undefined, high=J.undefined, low=J.undefined, close=J.undefined, period=J.undefined, idx=J.undefined, *_args):
        if J.lt(idx, J.sub(period, 1)):
            return 0
        sumVariance = 0
        i = 0
        while J.lt(i, period):
            o = J.get(open, J.sub(idx, i))
            h = J.get(high, J.sub(idx, i))
            l = J.get(low, J.sub(idx, i))
            c = J.get(close, J.sub(idx, i))
            if (((J.gt(l, 0) and J.gt(h, 0)) and J.gt(o, 0)) and J.gt(c, 0)):
                hlTerm = J.mul(0.5, J.get(G_Math, "pow")(J.get(G_Math, "log")(J.div(h, l)), 2))
                ocTerm = J.mul(J.sub(J.mul(2, J.get(G_Math, "log")(2)), 1), J.get(G_Math, "pow")(J.get(G_Math, "log")(J.div(c, o)), 2))
                sumVariance = J.add(sumVariance, J.sub(hlTerm, ocTerm))
            i = J.inc(i)
        varianceVal = J.div(sumVariance, period)
        return J.mul(J.get(G_Math, "sqrt")(J.mul(varianceVal, 252)), 100)
    def calcYangZhangVolatility(open=J.undefined, high=J.undefined, low=J.undefined, close=J.undefined, period=J.undefined, idx=J.undefined, *_args):
        if J.lt(idx, J.sub(period, 1)):
            return 0
        sumOpenJump = 0
        sumOpenJumpSq = 0
        i = 1
        while J.lt(i, period):
            prevClose = J.get(close, J.sub(idx, i))
            currOpen = J.get(open, J.add(J.sub(idx, i), 1))
            if (J.gt(prevClose, 0) and J.gt(currOpen, 0)):
                jump = J.get(G_Math, "log")(J.div(currOpen, prevClose))
                sumOpenJump = J.add(sumOpenJump, jump)
                sumOpenJumpSq = J.add(sumOpenJumpSq, J.mul(jump, jump))
            i = J.inc(i)
        meanOpenJump = J.div(sumOpenJump, J.sub(period, 1))
        openVariance = J.sub(J.div(sumOpenJumpSq, J.sub(period, 1)), J.mul(meanOpenJump, meanOpenJump))
        sumClose = 0
        sumCloseSq = 0
        i_2 = 1
        while J.lt(i_2, period):
            prevClose_2 = J.get(close, J.sub(idx, i_2))
            currClose = J.get(close, J.add(J.sub(idx, i_2), 1))
            if (J.gt(prevClose_2, 0) and J.gt(currClose, 0)):
                ret = J.get(G_Math, "log")(J.div(currClose, prevClose_2))
                sumClose = J.add(sumClose, ret)
                sumCloseSq = J.add(sumCloseSq, J.mul(ret, ret))
            i_2 = J.inc(i_2)
        meanClose = J.div(sumClose, J.sub(period, 1))
        closeVariance = J.sub(J.div(sumCloseSq, J.sub(period, 1)), J.mul(meanClose, meanClose))
        sumRS = 0
        i_3 = 0
        while J.lt(i_3, period):
            o = J.get(open, J.sub(idx, i_3))
            h = J.get(high, J.sub(idx, i_3))
            l = J.get(low, J.sub(idx, i_3))
            c = J.get(close, J.sub(idx, i_3))
            if (((J.gt(o, 0) and J.gt(h, 0)) and J.gt(l, 0)) and J.gt(c, 0)):
                rs = J.add(J.mul(J.get(G_Math, "log")(J.div(h, c)), J.get(G_Math, "log")(J.div(h, o))), J.mul(J.get(G_Math, "log")(J.div(l, c)), J.get(G_Math, "log")(J.div(l, o))))
                sumRS = J.add(sumRS, rs)
            i_3 = J.inc(i_3)
        rsVariance = J.div(sumRS, period)
        k = J.div(0.34, J.add(1.34, J.div(J.add(period, 1), J.sub(period, 1))))
        yzVariance = J.add(J.add(openVariance, J.mul(k, closeVariance)), J.mul(J.sub(1, k), rsVariance))
        return J.mul(J.get(G_Math, "sqrt")(J.mul(J.get(G_Math, "max")(0, yzVariance), 252)), 100)
    def calcCompositeVolatility(parkinson=J.undefined, garmanKlass=J.undefined, yangZhang=J.undefined, *_args):
        return J.add(J.add(J.mul(yangZhang, 0.5), J.mul(garmanKlass, 0.3)), J.mul(parkinson, 0.2))
    def calcVarianceRatio(prices=J.undefined, shortPeriod=J.undefined, longPeriod=J.undefined, idx=J.undefined, *_args):
        if J.lt(idx, longPeriod):
            return 1
        shortVar = 0
        i = 1
        while J.lt(i, shortPeriod):
            ret = J.div(J.sub(J.get(prices, J.add(J.sub(idx, i), 1)), J.get(prices, J.sub(idx, i))), J.get(prices, J.sub(idx, i)))
            shortVar = J.add(shortVar, J.mul(ret, ret))
            i = J.inc(i)
        shortVar = J.div(shortVar, J.sub(shortPeriod, 1))
        longVar = 0
        ratio = J.get(G_Math, "floor")(J.div(longPeriod, shortPeriod))
        i_2 = 1
        while J.lt(i_2, ratio):
            start = J.sub(idx, J.mul(i_2, shortPeriod))
            end = J.sub(idx, J.mul(J.sub(i_2, 1), shortPeriod))
            if (J.ge(start, 0) and J.lt(end, J.get(prices, "length"))):
                ret_2 = J.div(J.sub(J.get(prices, end), J.get(prices, start)), J.get(prices, start))
                longVar = J.add(longVar, J.mul(ret_2, ret_2))
            i_2 = J.inc(i_2)
        longVar = J.div(longVar, J.sub(ratio, 1))
        if J.seq(shortVar, 0):
            return 1
        return J.div(longVar, J.mul(shortVar, ratio))
    def classifyRegime(varianceRatio_2=J.undefined, vol=J.undefined, volMA_2=J.undefined, volStdDev_2=J.undefined, trendThresh=J.undefined, meanRevThresh=J.undefined, *_args):
        volZScore = (J.div(J.sub(vol, volMA_2), volStdDev_2) if J.gt(volStdDev_2, 0) else 0)
        regime = "transitional"
        confidence = 50
        if J.gt(varianceRatio_2, trendThresh):
            regime = "trending"
            confidence = J.get(G_Math, "min")(90, J.add(50, J.mul(J.sub(varianceRatio_2, trendThresh), 20)))
            if J.gt(volZScore, 0.5):
                confidence = J.add(confidence, 10)
        elif J.lt(varianceRatio_2, meanRevThresh):
            regime = "mean_reverting"
            confidence = J.get(G_Math, "min")(90, J.add(50, J.mul(J.sub(meanRevThresh, varianceRatio_2), 30)))
            if J.lt(volZScore, (-0.5)):
                confidence = J.add(confidence, 10)
        else:
            confidence = J.add(50, J.mul(J.get(G_Math, "abs")(volZScore), 10))
            if J.gt(volZScore, 1.5):
                regime = "choppy"
                confidence = J.get(G_Math, "min")(85, J.add(confidence, 15))
        return J.obj(("regime", regime), ("confidence", J.get(G_Math, "min")(95, confidence)), ("varianceRatio", varianceRatio_2), ("volZScore", volZScore))
    def assessRisk(zScore=J.undefined, elevatedThresh=J.undefined, highThresh=J.undefined, extremeThresh=J.undefined, elevatedSize=J.undefined, highSize=J.undefined, extremeSize=J.undefined, *_args):
        absZ = J.get(G_Math, "abs")(zScore)
        riskLevel_2 = "NORMAL"
        positionSize = 100
        riskColor_2 = J.get(COLORS, "RISK_NORMAL")
        riskEmoji_2 = "✅"
        if J.ge(absZ, extremeThresh):
            riskLevel_2 = "EXTREME"
            positionSize = extremeSize
            riskColor_2 = J.get(COLORS, "RISK_EXTREME")
            riskEmoji_2 = "\ud83d\udd25"
        elif J.ge(absZ, highThresh):
            riskLevel_2 = "HIGH"
            positionSize = highSize
            riskColor_2 = J.get(COLORS, "RISK_HIGH")
            riskEmoji_2 = "⚠️"
        elif J.ge(absZ, elevatedThresh):
            riskLevel_2 = "ELEVATED"
            positionSize = elevatedSize
            riskColor_2 = J.get(COLORS, "RISK_ELEVATED")
            riskEmoji_2 = "⚡"
        if J.lt(zScore, J.neg(extremeThresh)):
            riskLevel_2 = "LOW VOL"
            positionSize = 100
            riskColor_2 = J.get(COLORS, "RISK_NORMAL")
            riskEmoji_2 = "\ud83d\udca4"
        return J.obj(("level", riskLevel_2), ("positionSize", positionSize), ("color", riskColor_2), ("emoji", riskEmoji_2), ("zScore", zScore))
    def detectVCP(volatility=J.undefined, period=J.undefined, idx=J.undefined, minPeriods=J.undefined, maxPeriods=J.undefined, contractionThreshold_2=J.undefined, *_args):
        if J.lt(idx, maxPeriods):
            return J.obj(("isVCP", False), ("contractionPercent", 0), ("periodLength", 0), ("quality", 0))
        maxVol = 0
        i = minPeriods
        while J.le(i, maxPeriods):
            if J.gt(J.get(volatility, J.sub(idx, i)), maxVol):
                maxVol = J.get(volatility, J.sub(idx, i))
            i = J.inc(i)
        currentVol_2 = J.get(volatility, idx)
        contractionPercent = (J.mul(J.div(J.sub(maxVol, currentVol_2), maxVol), 100) if J.gt(maxVol, 0) else 0)
        contractionLength = 0
        i_2 = 0
        while J.lt(i_2, maxPeriods):
            if J.lt(J.get(volatility, J.sub(idx, i_2)), J.get(volatility, J.sub(J.sub(idx, i_2), 1))):
                contractionLength = J.inc(contractionLength)
            else:
                break
            i_2 = J.inc(i_2)
        isVCP = (J.ge(contractionLength, minPeriods) if J.truthy(_t1 := J.ge(contractionPercent, contractionThreshold_2)) else _t1)
        quality = 0
        if J.truthy(isVCP):
            quality = J.get(G_Math, "min")(100, J.add(contractionPercent, J.mul(contractionLength, 2)))
        return J.obj(("isVCP", isVCP), ("contractionPercent", contractionPercent), ("periodLength", contractionLength), ("quality", quality))
    G_describe_indicator("Volatility Regime Classifier", "lower", J.obj(("shortName", "VRC"), ("version", "3.0"), ("description", "Advanced volatility structure with regime classification, VCP detection, and risk-based position sizing")))
    volPeriod = J.get(G_input, "number")("Volatility Period", 20, J.obj(("min", 10), ("max", 50)))
    volLookback = J.get(G_input, "number")("Regime Lookback", 50, J.obj(("min", 20), ("max", 100)))
    smoothing = J.get(G_input, "number")("Smoothing Period", 5, J.obj(("min", 1), ("max", 10)))
    trendThreshold = J.get(G_input, "number")("Trend Threshold", 1.5, J.obj(("min", 1), ("max", 3), ("step", 0.1)))
    meanRevThreshold = J.get(G_input, "number")("Mean Reversion Threshold", 0.7, J.obj(("min", 0.3), ("max", 1), ("step", 0.05)))
    regimeConfidence = J.get(G_input, "number")("Min Regime Confidence", 65, J.obj(("min", 50), ("max", 90)))
    vcpContractionThreshold = J.get(G_input, "number")("VCP Contraction %", 60, J.obj(("min", 40), ("max", 80)))
    vcpMinPeriods = J.get(G_input, "number")("VCP Min Periods", 10, J.obj(("min", 5), ("max", 20)))
    vcpMaxPeriods = J.get(G_input, "number")("VCP Max Periods", 40, J.obj(("min", 20), ("max", 60)))
    expansionThreshold = J.get(G_input, "number")("Expansion Threshold", 1.3, J.obj(("min", 1.1), ("max", 2), ("step", 0.1)))
    contractionThreshold = J.get(G_input, "number")("Contraction Threshold", 0.7, J.obj(("min", 0.3), ("max", 0.9), ("step", 0.05)))
    elevatedRiskZScore = J.get(G_input, "number")("Elevated Risk Z-Score", 1.5, J.obj(("min", 1), ("max", 2), ("step", 0.1)))
    highRiskZScore = J.get(G_input, "number")("High Risk Z-Score", 2, J.obj(("min", 1.5), ("max", 2.5), ("step", 0.1)))
    extremeRiskZScore = J.get(G_input, "number")("Extreme Risk Z-Score", 2.5, J.obj(("min", 2), ("max", 3.5), ("step", 0.1)))
    zScoreHysteresis = J.get(G_input, "number")("Z-Score Exit Hysteresis", 0.3, J.obj(("min", 0.2), ("max", 1), ("step", 0.1)))
    elevatedRiskSize = J.get(G_input, "number")("Elevated Risk Size %", 50, J.obj(("min", 25), ("max", 75), ("step", 5)))
    highRiskSize = J.get(G_input, "number")("High Risk Size %", 25, J.obj(("min", 10), ("max", 50), ("step", 5)))
    extremeRiskSize = J.get(G_input, "number")("Extreme Risk Size %", 10, J.obj(("min", 5), ("max", 25), ("step", 5)))
    showParkinson = J.get(G_input, "boolean")("Show Parkinson Vol", True)
    showGarmanKlass = J.get(G_input, "boolean")("Show Garman-Klass Vol", True)
    showYangZhang = J.get(G_input, "boolean")("Show Yang-Zhang Vol", True)
    showComposite = J.get(G_input, "boolean")("Show Composite Vol", True)
    showRegimeBands = J.get(G_input, "boolean")("Show Regime Bands", True)
    showVolatilityBands = J.get(G_input, "boolean")("Show Volatility Bands", False)
    showVolZScore = J.get(G_input, "boolean")("Show Vol Z-Score", False)
    showZScoreRefs = J.get(G_input, "boolean")("Show Z-Score References", False)
    showRiskZones = J.get(G_input, "boolean")("Show Risk Zones", True)
    COLORS = J.obj(("LOW_VOL", "#00FF00"), ("NORMAL_VOL", "#FFD700"), ("HIGH_VOL", "#FF6347"), ("EXTREME_VOL", "#FF0000"), ("TRENDING", "#00FFFF"), ("MEAN_REVERTING", "#FF00FF"), ("TRANSITIONAL", "#FFFF00"), ("CHOPPY", "#FF6347"), ("EXPANDING", "#FF1493"), ("CONTRACTING", "#00CED1"), ("STABLE", "#9370DB"), ("VCP_ACTIVE", "#00FF00"), ("VCP_BREAKOUT", "#00FFFF"), ("RISK_NORMAL", "#00FF00"), ("RISK_ELEVATED", "#FFD700"), ("RISK_HIGH", "#FFA500"), ("RISK_EXTREME", "#FF0000"), ("RISK_CAPITULATION", "#FF00FF"), ("PANEL_BG", "#1A1A2EDD"), ("TEXT", "#FFFFFF"), ("PARKINSON", "#00CED1"), ("GARMAN_KLASS", "#9370DB"), ("YANG_ZHANG", "#FF69B4"), ("COMPOSITE", "#00FF00"))
    parkinsonVol = G_series_of(0)
    garmanKlassVol = G_series_of(0)
    yangZhangVol = G_series_of(0)
    compositeVol = G_series_of(0)
    smoothedVol = G_series_of(0)
    volMA = G_series_of(0)
    volStdDev = G_series_of(0)
    upperBand = G_series_of(0)
    lowerBand = G_series_of(0)
    varianceRatio = G_series_of(1)
    regimeType = J.JSArray([])
    regimeConfidenceScore = G_series_of(50)
    regimeZScore = G_series_of(0)
    riskLevel = J.JSArray([])
    positionSizePercent = G_series_of(100)
    riskColor = J.JSArray([])
    vcpActive = G_series_of(False)
    vcpQuality = G_series_of(0)
    vcpContraction = G_series_of(0)
    volState = J.JSArray([])
    volPercentile = G_series_of(50)
    i = 0
    while J.lt(i, J.get(G_close, "length")):
        if J.ge(i, J.sub(volPeriod, 1)):
            J.set(parkinsonVol, i, calcParkinsonVolatility(G_high, G_low, volPeriod, i))
            J.set(garmanKlassVol, i, calcGarmanKlassVolatility(G_open, G_high, G_low, G_close, volPeriod, i))
            J.set(yangZhangVol, i, calcYangZhangVolatility(G_open, G_high, G_low, G_close, volPeriod, i))
            J.set(compositeVol, i, calcCompositeVolatility(J.get(parkinsonVol, i), J.get(garmanKlassVol, i), J.get(yangZhangVol, i)))
        else:
            J.set(parkinsonVol, i, 0)
            J.set(garmanKlassVol, i, 0)
            J.set(yangZhangVol, i, 0)
            J.set(compositeVol, i, 0)
        i = J.inc(i)
    prevEMA = J.get(compositeVol, 0)
    i_2 = 0
    while J.lt(i_2, J.get(G_close, "length")):
        J.set(smoothedVol, i_2, calcEMA(compositeVol, smoothing, i_2, prevEMA))
        prevEMA = J.get(smoothedVol, i_2)
        i_2 = J.inc(i_2)
    i_3 = 0
    while J.lt(i_3, J.get(G_close, "length")):
        if J.ge(i_3, volLookback):
            J.set(volMA, i_3, calcSMA(smoothedVol, volLookback, i_3))
            J.set(volStdDev, i_3, calcStdDev(smoothedVol, volLookback, i_3))
            J.set(upperBand, i_3, J.add(J.get(volMA, i_3), J.mul(J.get(volStdDev, i_3), 2)))
            J.set(lowerBand, i_3, J.get(G_Math, "max")(0, J.sub(J.get(volMA, i_3), J.mul(J.get(volStdDev, i_3), 2))))
            J.set(volPercentile, i_3, calcPercentile(smoothedVol, volLookback, i_3, 0.5))
        else:
            J.set(volMA, i_3, J.get(smoothedVol, i_3))
            J.set(volStdDev, i_3, 0)
            J.set(upperBand, i_3, J.get(smoothedVol, i_3))
            J.set(lowerBand, i_3, J.get(smoothedVol, i_3))
            J.set(volPercentile, i_3, J.get(smoothedVol, i_3))
        i_3 = J.inc(i_3)
    i_4 = 0
    while J.lt(i_4, J.get(G_close, "length")):
        if J.ge(i_4, volLookback):
            J.set(varianceRatio, i_4, calcVarianceRatio(G_close, volPeriod, volLookback, i_4))
            classification = classifyRegime(J.get(varianceRatio, i_4), J.get(smoothedVol, i_4), J.get(volMA, i_4), J.get(volStdDev, i_4), trendThreshold, meanRevThreshold)
            J.set(regimeType, i_4, J.get(classification, "regime"))
            J.set(regimeConfidenceScore, i_4, J.get(classification, "confidence"))
            J.set(regimeZScore, i_4, J.get(classification, "volZScore"))
            risk = assessRisk(J.get(classification, "volZScore"), elevatedRiskZScore, highRiskZScore, extremeRiskZScore, elevatedRiskSize, highRiskSize, extremeRiskSize)
            J.set(riskLevel, i_4, J.get(risk, "level"))
            J.set(positionSizePercent, i_4, J.get(risk, "positionSize"))
            J.set(riskColor, i_4, J.get(risk, "color"))
        else:
            J.set(varianceRatio, i_4, 1)
            J.set(regimeType, i_4, "transitional")
            J.set(regimeConfidenceScore, i_4, 50)
            J.set(regimeZScore, i_4, 0)
            J.set(riskLevel, i_4, "NORMAL")
            J.set(positionSizePercent, i_4, 100)
            J.set(riskColor, i_4, J.get(COLORS, "RISK_NORMAL"))
        i_4 = J.inc(i_4)
    i_5 = 1
    while J.lt(i_5, J.get(G_close, "length")):
        volChange = J.div(J.get(smoothedVol, i_5), J.get(smoothedVol, J.sub(i_5, 1)))
        if J.gt(volChange, expansionThreshold):
            J.set(volState, i_5, "expanding")
        elif J.lt(volChange, contractionThreshold):
            J.set(volState, i_5, "contracting")
        else:
            J.set(volState, i_5, "stable")
        i_5 = J.inc(i_5)
    J.set(volState, 0, "stable")
    i_6 = 0
    while J.lt(i_6, J.get(G_close, "length")):
        if J.ge(i_6, vcpMaxPeriods):
            vcp = detectVCP(smoothedVol, volPeriod, i_6, vcpMinPeriods, vcpMaxPeriods, vcpContractionThreshold)
            J.set(vcpActive, i_6, J.get(vcp, "isVCP"))
            J.set(vcpQuality, i_6, J.get(vcp, "quality"))
            J.set(vcpContraction, i_6, J.get(vcp, "contractionPercent"))
        i_6 = J.inc(i_6)
    if J.truthy(showParkinson):
        G_paint(parkinsonVol, J.obj(("name", "Parkinson Vol"), ("color", J.get(COLORS, "PARKINSON")), ("style", "line"), ("thickness", 1), ("opacity", 0.6)))
    if J.truthy(showGarmanKlass):
        G_paint(garmanKlassVol, J.obj(("name", "Garman-Klass Vol"), ("color", J.get(COLORS, "GARMAN_KLASS")), ("style", "line"), ("thickness", 1), ("opacity", 0.6)))
    if J.truthy(showYangZhang):
        G_paint(yangZhangVol, J.obj(("name", "Yang-Zhang Vol"), ("color", J.get(COLORS, "YANG_ZHANG")), ("style", "line"), ("thickness", 1), ("opacity", 0.6)))
    if J.truthy(showComposite):
        compositeColors = J.JSArray([])
        i_7 = 0
        while J.lt(i_7, J.get(smoothedVol, "length")):
            regime = J.get(regimeType, i_7)
            state = J.get(volState, i_7)
            risk_2 = J.get(riskLevel, i_7)
            if (J.seq(risk_2, "EXTREME") or J.seq(risk_2, "HIGH")):
                J.set(compositeColors, i_7, J.get(riskColor, i_7))
            elif J.truthy(J.get(vcpActive, i_7)):
                J.set(compositeColors, i_7, J.get(COLORS, "VCP_ACTIVE"))
            elif J.seq(regime, "trending"):
                J.set(compositeColors, i_7, J.get(COLORS, "TRENDING"))
            elif J.seq(regime, "mean_reverting"):
                J.set(compositeColors, i_7, J.get(COLORS, "MEAN_REVERTING"))
            elif J.seq(regime, "choppy"):
                J.set(compositeColors, i_7, J.get(COLORS, "CHOPPY"))
            elif J.seq(state, "expanding"):
                J.set(compositeColors, i_7, J.get(COLORS, "EXPANDING"))
            elif J.seq(state, "contracting"):
                J.set(compositeColors, i_7, J.get(COLORS, "CONTRACTING"))
            else:
                J.set(compositeColors, i_7, J.get(COLORS, "STABLE"))
            i_7 = J.inc(i_7)
        G_paint(smoothedVol, J.obj(("name", "Composite Vol"), ("colors", compositeColors), ("thickness", 3), ("opacity", 1)))
    if J.truthy(showVolatilityBands):
        G_paint(upperBand, J.obj(("name", "Upper Band"), ("color", J.get(COLORS, "HIGH_VOL")), ("style", "line"), ("thickness", 1), ("opacity", 0.4)))
        G_paint(lowerBand, J.obj(("name", "Lower Band"), ("color", J.get(COLORS, "LOW_VOL")), ("style", "line"), ("thickness", 1), ("opacity", 0.4)))
    if J.truthy(showVolZScore):
        zScoreColors = J.JSArray([])
        i_8 = 0
        while J.lt(i_8, J.get(regimeZScore, "length")):
            J.set(zScoreColors, i_8, J.get(riskColor, i_8))
            i_8 = J.inc(i_8)
        G_paint(regimeZScore, J.obj(("name", "Vol Z-Score"), ("colors", zScoreColors), ("style", "line"), ("thickness", 2), ("opacity", 0.8)))
    if (J.truthy(showZScoreRefs) and J.truthy(showVolZScore)):
        extremeRiskLine = G_series_of(extremeRiskZScore)
        extremeLowLine = G_series_of(J.neg(extremeRiskZScore))
        highRiskLine = G_series_of(highRiskZScore)
        highRiskLowLine = G_series_of(J.neg(highRiskZScore))
        elevatedRiskLine = G_series_of(elevatedRiskZScore)
        elevatedRiskLowLine = G_series_of(J.neg(elevatedRiskZScore))
        zeroLine = G_series_of(0)
        G_paint(extremeRiskLine, J.obj(("name", J.template("Extreme Risk (+", extremeRiskZScore, "σ)")), ("color", J.get(COLORS, "RISK_EXTREME")), ("style", "line"), ("thickness", 2), ("opacity", 0.7)))
        G_paint(extremeLowLine, J.obj(("name", J.template("Extreme Low Vol (-", extremeRiskZScore, "σ)")), ("color", J.get(COLORS, "RISK_NORMAL")), ("style", "line"), ("thickness", 2), ("opacity", 0.7)))
        G_paint(highRiskLine, J.obj(("name", J.template("High Risk (+", highRiskZScore, "σ)")), ("color", J.get(COLORS, "RISK_HIGH")), ("style", "dotted"), ("thickness", 1), ("opacity", 0.6)))
        G_paint(elevatedRiskLine, J.obj(("name", J.template("Elevated Risk (+", elevatedRiskZScore, "σ)")), ("color", J.get(COLORS, "RISK_ELEVATED")), ("style", "dotted"), ("thickness", 1), ("opacity", 0.5)))
        G_paint(zeroLine, J.obj(("name", "Z-Score Zero"), ("color", J.get(COLORS, "TEXT")), ("style", "line"), ("thickness", 1), ("opacity", 0.3)))
    if J.truthy(showRegimeBands):
        avgVol = 0
        count = 0
        i_9 = J.get(G_Math, "max")(0, J.sub(J.get(G_close, "length"), volLookback))
        while J.lt(i_9, J.get(G_close, "length")):
            avgVol = J.add(avgVol, J.get(smoothedVol, i_9))
            count = J.inc(count)
            i_9 = J.inc(i_9)
        avgVol = (J.div(avgVol, count) if J.gt(count, 0) else 20)
        G_horizontal_line(J.mul(avgVol, 1.5), J.obj(("name", "High Vol"), ("color", J.get(COLORS, "HIGH_VOL")), ("style", "dotted"), ("thickness", 1), ("opacity", 0.5)))
        G_horizontal_line(avgVol, J.obj(("name", "Normal Vol"), ("color", J.get(COLORS, "NORMAL_VOL")), ("style", "line"), ("thickness", 1), ("opacity", 0.3)))
        G_horizontal_line(J.mul(avgVol, 0.5), J.obj(("name", "Low Vol"), ("color", J.get(COLORS, "LOW_VOL")), ("style", "dotted"), ("thickness", 1), ("opacity", 0.5)))
    volExpansion = G_series_of(False)
    volContraction = G_series_of(False)
    extremeVolatility = G_series_of(False)
    lowVolatility = G_series_of(False)
    regimeTrending = G_series_of(False)
    regimeMeanReverting = G_series_of(False)
    regimeChoppy = G_series_of(False)
    vcpDetected = G_series_of(False)
    vcpBreakout = G_series_of(False)
    highConfidenceRegime = G_series_of(False)
    elevatedRiskEntered = G_series_of(False)
    highRiskEntered = G_series_of(False)
    extremeRiskEntered = G_series_of(False)
    riskNormalized = G_series_of(False)
    possibleCapitulation = G_series_of(False)
    premiumCompressionZone = G_series_of(False)
    volAwakening = G_series_of(False)
    i_10 = J.add(volLookback, 1)
    while J.lt(i_10, J.get(G_close, "length")):
        if (J.seq(J.get(volState, i_10), "expanding") and J.sne(J.get(volState, J.sub(i_10, 1)), "expanding")):
            J.set(volExpansion, i_10, True)
        if (J.seq(J.get(volState, i_10), "contracting") and J.sne(J.get(volState, J.sub(i_10, 1)), "contracting")):
            J.set(volContraction, i_10, True)
        if (J.gt(J.get(smoothedVol, i_10), J.get(upperBand, i_10)) and J.le(J.get(smoothedVol, J.sub(i_10, 1)), J.get(upperBand, J.sub(i_10, 1)))):
            J.set(extremeVolatility, i_10, True)
        if (J.lt(J.get(smoothedVol, i_10), J.get(lowerBand, i_10)) and J.ge(J.get(smoothedVol, J.sub(i_10, 1)), J.get(lowerBand, J.sub(i_10, 1)))):
            J.set(lowVolatility, i_10, True)
        if ((J.seq(J.get(regimeType, i_10), "trending") and J.sne(J.get(regimeType, J.sub(i_10, 1)), "trending")) and J.gt(J.get(regimeConfidenceScore, i_10), regimeConfidence)):
            J.set(regimeTrending, i_10, True)
        if ((J.seq(J.get(regimeType, i_10), "mean_reverting") and J.sne(J.get(regimeType, J.sub(i_10, 1)), "mean_reverting")) and J.gt(J.get(regimeConfidenceScore, i_10), regimeConfidence)):
            J.set(regimeMeanReverting, i_10, True)
        if (J.seq(J.get(regimeType, i_10), "choppy") and J.sne(J.get(regimeType, J.sub(i_10, 1)), "choppy")):
            J.set(regimeChoppy, i_10, True)
        if (J.gt(J.get(regimeConfidenceScore, i_10), 75) and J.le(J.get(regimeConfidenceScore, J.sub(i_10, 1)), 75)):
            J.set(highConfidenceRegime, i_10, True)
        if ((J.truthy(J.get(vcpActive, i_10)) and (not J.truthy(J.get(vcpActive, J.sub(i_10, 1))))) and J.gt(J.get(vcpQuality, i_10), 60)):
            J.set(vcpDetected, i_10, True)
        if ((J.truthy(J.get(vcpActive, J.sub(i_10, 1))) and (not J.truthy(J.get(vcpActive, i_10)))) and J.seq(J.get(volState, i_10), "expanding")):
            J.set(vcpBreakout, i_10, True)
        currentRisk = J.get(riskLevel, i_10)
        prevRisk = J.get(riskLevel, J.sub(i_10, 1))
        currentZ = J.get(regimeZScore, i_10)
        prevZ = J.get(regimeZScore, J.sub(i_10, 1))
        if (J.seq(currentRisk, "ELEVATED") and J.seq(prevRisk, "NORMAL")):
            J.set(elevatedRiskEntered, i_10, True)
        if (J.seq(currentRisk, "HIGH") and (J.seq(prevRisk, "NORMAL") or J.seq(prevRisk, "ELEVATED"))):
            J.set(highRiskEntered, i_10, True)
        if (J.seq(currentRisk, "EXTREME") and J.sne(prevRisk, "EXTREME")):
            J.set(extremeRiskEntered, i_10, True)
            if (J.seq(J.get(regimeType, i_10), "mean_reverting") and J.gt(J.get(regimeConfidenceScore, i_10), 60)):
                J.set(possibleCapitulation, i_10, True)
        exitThreshold = J.sub(elevatedRiskZScore, zScoreHysteresis)
        if (J.lt(J.get(G_Math, "abs")(currentZ), exitThreshold) and J.ge(J.get(G_Math, "abs")(prevZ), exitThreshold)):
            wasElevated = False
            j = 1
            while J.le(j, 5):
                if (J.ge(J.sub(i_10, j), 0) and J.ge(J.get(G_Math, "abs")(J.get(regimeZScore, J.sub(i_10, j))), elevatedRiskZScore)):
                    wasElevated = True
                    break
                j = J.inc(j)
            if J.truthy(wasElevated):
                J.set(riskNormalized, i_10, True)
        if (J.lt(currentZ, J.neg(extremeRiskZScore)) and J.ge(prevZ, J.neg(extremeRiskZScore))):
            J.set(premiumCompressionZone, i_10, True)
        if (J.gt(currentZ, J.neg(J.sub(extremeRiskZScore, zScoreHysteresis))) and J.le(prevZ, J.neg(J.sub(extremeRiskZScore, zScoreHysteresis)))):
            wasExtremeLow = False
            j_2 = 1
            while J.le(j_2, 5):
                if (J.ge(J.sub(i_10, j_2), 0) and J.lt(J.get(regimeZScore, J.sub(i_10, j_2)), J.neg(extremeRiskZScore))):
                    wasExtremeLow = True
                    break
                j_2 = J.inc(j_2)
            if J.truthy(wasExtremeLow):
                J.set(volAwakening, i_10, True)
        i_10 = J.inc(i_10)
    G_register_signal(volExpansion, "\ud83d\udcc8 Volatility EXPANDING")
    G_register_signal(volContraction, "\ud83d\udcc9 Volatility CONTRACTING")
    G_register_signal(extremeVolatility, "⚠️ EXTREME Volatility")
    G_register_signal(lowVolatility, "\ud83d\ude34 LOW Volatility Zone")
    G_register_signal(regimeTrending, "\ud83c\udfaf TRENDING Regime Detected")
    G_register_signal(regimeMeanReverting, "\ud83d\udd04 MEAN REVERTING Regime")
    G_register_signal(regimeChoppy, "⚠️ CHOPPY Market Warning")
    G_register_signal(highConfidenceRegime, "✅ High Confidence Regime")
    G_register_signal(vcpDetected, "\ud83c\udfaa VCP Pattern Detected")
    G_register_signal(vcpBreakout, "\ud83d\ude80 VCP BREAKOUT")
    G_register_signal(elevatedRiskEntered, J.template("⚡ ELEVATED RISK - Size Down to ", elevatedRiskSize, "%"))
    G_register_signal(highRiskEntered, J.template("⚠️ HIGH RISK - Size Down to ", highRiskSize, "%"))
    G_register_signal(extremeRiskEntered, J.template("\ud83d\udd25 EXTREME RISK - Size Down to ", extremeRiskSize, "%"))
    G_register_signal(possibleCapitulation, "\ud83d\udca5 POSSIBLE CAPITULATION - High Risk/High Reward Setup")
    G_register_signal(riskNormalized, "✅ Risk NORMALIZING - Resume Standard Sizing")
    G_register_signal(premiumCompressionZone, "\ud83d\udca4 PREMIUM COMPRESSION - Optimal Selling Environment")
    G_register_signal(volAwakening, "⚡ Vol AWAKENING - Directional Move Likely")
    lastIdx = J.sub(J.get(G_close, "length"), 1)
    currentVol = J.get(smoothedVol, lastIdx)
    currentMA = J.get(volMA, lastIdx)
    currentRegime = J.get(regimeType, lastIdx)
    currentConfidence = J.get(regimeConfidenceScore, lastIdx)
    currentState = J.get(volState, lastIdx)
    currentVR = J.get(varianceRatio, lastIdx)
    currentVCP = J.get(vcpActive, lastIdx)
    currentVCPQuality = J.get(vcpQuality, lastIdx)
    currentZScore = J.get(regimeZScore, lastIdx)
    currentRiskLevel = J.get(riskLevel, lastIdx)
    currentPositionSize = J.get(positionSizePercent, lastIdx)
    currentRiskColor = J.get(riskColor, lastIdx)
    volLevel = "NORMAL"
    volColor = J.get(COLORS, "NORMAL_VOL")
    volRatio = (J.div(currentVol, currentMA) if J.gt(currentMA, 0) else 1)
    if J.gt(currentVol, J.get(upperBand, lastIdx)):
        volLevel = "EXTREME"
        volColor = J.get(COLORS, "EXTREME_VOL")
    elif J.gt(volRatio, 1.3):
        volLevel = "HIGH"
        volColor = J.get(COLORS, "HIGH_VOL")
    elif J.lt(currentVol, J.get(lowerBand, lastIdx)):
        volLevel = "LOW"
        volColor = J.get(COLORS, "LOW_VOL")
    regimeColor = J.get(COLORS, "TRANSITIONAL")
    if J.seq(currentRegime, "trending"):
        regimeColor = J.get(COLORS, "TRENDING")
    elif J.seq(currentRegime, "mean_reverting"):
        regimeColor = J.get(COLORS, "MEAN_REVERTING")
    elif J.seq(currentRegime, "choppy"):
        regimeColor = J.get(COLORS, "CHOPPY")
    stateEmoji = "◆"
    if J.seq(currentState, "expanding"):
        stateEmoji = "\ud83d\udcc8"
    elif J.seq(currentState, "contracting"):
        stateEmoji = "\ud83d\udcc9"
    riskEmoji = "✅"
    if J.seq(currentRiskLevel, "EXTREME"):
        riskEmoji = "\ud83d\udd25"
    elif J.seq(currentRiskLevel, "HIGH"):
        riskEmoji = "⚠️"
    elif J.seq(currentRiskLevel, "ELEVATED"):
        riskEmoji = "⚡"
    elif J.seq(currentRiskLevel, "LOW VOL"):
        riskEmoji = "\ud83d\udca4"
    recommendation = "NEUTRAL"
    recColor = J.get(COLORS, "TEXT")
    if J.seq(currentRegime, "choppy"):
        recommendation = "AVOID"
        recColor = J.get(COLORS, "CHOPPY")
    elif J.truthy(currentVCP):
        recommendation = "VCP - STANDBY"
        recColor = J.get(COLORS, "VCP_ACTIVE")
    elif (J.seq(currentRegime, "trending") and J.gt(currentConfidence, 70)):
        if (J.seq(currentRiskLevel, "EXTREME") or J.seq(currentRiskLevel, "HIGH")):
            recommendation = J.template("DIRECTIONAL - ", currentPositionSize, "% SIZE")
            recColor = J.get(COLORS, "TRENDING")
        else:
            recommendation = "DIRECTIONAL"
            recColor = J.get(COLORS, "TRENDING")
    elif (J.seq(currentRegime, "mean_reverting") and J.gt(currentConfidence, 70)):
        if J.seq(currentRiskLevel, "EXTREME"):
            recommendation = J.template("MEAN REV - ", currentPositionSize, "% SIZE")
            recColor = J.get(COLORS, "RISK_CAPITULATION")
        elif J.seq(currentRiskLevel, "HIGH"):
            recommendation = J.template("MEAN REV - ", currentPositionSize, "% SIZE")
            recColor = J.get(COLORS, "MEAN_REVERTING")
        elif J.seq(currentRiskLevel, "ELEVATED"):
            recommendation = J.template("MEAN REV - ", currentPositionSize, "% SIZE")
            recColor = J.get(COLORS, "MEAN_REVERTING")
        elif (J.seq(volLevel, "LOW") or J.seq(currentRiskLevel, "LOW VOL")):
            recommendation = "SELL PREMIUM"
            recColor = J.get(COLORS, "LOW_VOL")
        else:
            recommendation = "MEAN REV"
            recColor = J.get(COLORS, "MEAN_REVERTING")
    dashboardRows = J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", "\ud83d\udcca VOLATILITY REGIME"), ("color", J.get(COLORS, "COMPOSITE")), ("textAlign", "center"), ("fontWeight", "bold"), ("fontSize", 12))]))), J.obj(("cells", J.JSArray([J.obj(("text", J.template("Vol: ", J.get(currentVol, "toFixed")(1), "% (", volLevel, ")")), ("color", volColor), ("textAlign", "center"), ("fontSize", 10))]))), J.obj(("cells", J.JSArray([J.obj(("text", J.template(stateEmoji, " ", J.get(currentState, "toUpperCase")())), ("color", J.get(COLORS, "TEXT")), ("textAlign", "center"), ("fontSize", 10))]))), J.obj(("cells", J.JSArray([J.obj(("text", J.template(riskEmoji, " Risk: ", currentRiskLevel)), ("color", currentRiskColor), ("textAlign", "center"), ("fontSize", 10), ("fontWeight", "bold"))]))), J.obj(("cells", J.JSArray([J.obj(("text", J.template("Z: ", J.get(currentZScore, "toFixed")(2), "σ")), ("color", currentRiskColor), ("textAlign", "center"), ("fontSize", 9))]))), J.obj(("cells", J.JSArray([J.obj(("text", J.template("Position Size: ", currentPositionSize, "%")), ("color", (J.get(COLORS, "RISK_EXTREME") if J.lt(currentPositionSize, 50) else J.get(COLORS, "RISK_NORMAL"))), ("textAlign", "center"), ("fontSize", 10), ("fontWeight", ("bold" if J.lt(currentPositionSize, 50) else "normal")))]))), J.obj(("cells", J.JSArray([J.obj(("text", J.template("Regime: ", J.get(currentRegime, "toUpperCase")())), ("color", regimeColor), ("textAlign", "center"), ("fontSize", 9))]))), J.obj(("cells", J.JSArray([J.obj(("text", J.template("Confidence: ", J.get(currentConfidence, "toFixed")(0), "%")), ("color", (J.get(COLORS, "LOW_VOL") if J.gt(currentConfidence, 70) else J.get(COLORS, "TEXT"))), ("textAlign", "center"), ("fontSize", 9))]))), J.obj(("cells", J.JSArray([J.obj(("text", J.template("VR: ", J.get(currentVR, "toFixed")(2))), ("color", J.get(COLORS, "TEXT")), ("textAlign", "center"), ("fontSize", 9))])))])
    if J.truthy(currentVCP):
        J.get(dashboardRows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", J.template("\ud83c\udfaa VCP: ", J.get(currentVCPQuality, "toFixed")(0), "% Quality")), ("color", J.get(COLORS, "VCP_ACTIVE")), ("textAlign", "center"), ("fontSize", 9), ("fontWeight", "bold"))]))))
    if ((J.seq(currentRiskLevel, "EXTREME") and J.seq(currentRegime, "mean_reverting")) and J.gt(currentConfidence, 60)):
        J.get(dashboardRows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", "\ud83d\udca5 CAPITULATION?"), ("color", J.get(COLORS, "RISK_CAPITULATION")), ("textAlign", "center"), ("fontSize", 9), ("fontWeight", "bold"))]))))
    J.get(dashboardRows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", J.template("→ ", recommendation)), ("color", recColor), ("textAlign", "center"), ("fontSize", 10), ("fontWeight", "bold"))]))))
    G_paint_overlay("VRC_Panel", J.obj(("position", "center_right")), J.obj(("background", J.get(COLORS, "PANEL_BG")), ("border", J.template("2px solid ", currentRiskColor)), ("borderRadius", 4), ("rows", dashboardRows)))


register_store_indicator(
    script,
    name='volatility_regime_classifier_TS',
    title='Volatility Regime Classifier',
    developer='Gustivus',
    url='https://trendspider.com/trading-tools-store/indicators/6918c7-volatility-regime-classifier/',
    position='lower',
    inputs=[{'id': 'volatility_period', 'title': 'Volatility Period', 'type': 'number', 'default': 20}, {'id': 'regime_lookback', 'title': 'Regime Lookback', 'type': 'number', 'default': 50}, {'id': 'smoothing_period', 'title': 'Smoothing Period', 'type': 'number', 'default': 5}, {'id': 'trend_threshold', 'title': 'Trend Threshold', 'type': 'number', 'default': 1.5}, {'id': 'mean_reversion_threshold', 'title': 'Mean Reversion Threshold', 'type': 'number', 'default': 0.7}, {'id': 'min_regime_confidence', 'title': 'Min Regime Confidence', 'type': 'number', 'default': 65}, {'id': 'vcp_contraction__', 'title': 'VCP Contraction %', 'type': 'number', 'default': 60}, {'id': 'vcp_min_periods', 'title': 'VCP Min Periods', 'type': 'number', 'default': 10}, {'id': 'vcp_max_periods', 'title': 'VCP Max Periods', 'type': 'number', 'default': 40}, {'id': 'expansion_threshold', 'title': 'Expansion Threshold', 'type': 'number', 'default': 1.3}, {'id': 'contraction_threshold', 'title': 'Contraction Threshold', 'type': 'number', 'default': 0.7}, {'id': 'elevated_risk_z_score', 'title': 'Elevated Risk Z-Score', 'type': 'number', 'default': 1.5}, {'id': 'high_risk_z_score', 'title': 'High Risk Z-Score', 'type': 'number', 'default': 2}, {'id': 'extreme_risk_z_score', 'title': 'Extreme Risk Z-Score', 'type': 'number', 'default': 2.5}, {'id': 'z_score_exit_hysteresis', 'title': 'Z-Score Exit Hysteresis', 'type': 'number', 'default': 0.3}, {'id': 'elevated_risk_size__', 'title': 'Elevated Risk Size %', 'type': 'number', 'default': 50}, {'id': 'high_risk_size__', 'title': 'High Risk Size %', 'type': 'number', 'default': 25}, {'id': 'extreme_risk_size__', 'title': 'Extreme Risk Size %', 'type': 'number', 'default': 10}, {'id': 'show_parkinson_vol', 'title': 'Show Parkinson Vol', 'type': 'boolean', 'default': True}, {'id': 'show_garman_klass_vol', 'title': 'Show Garman-Klass Vol', 'type': 'boolean', 'default': True}, {'id': 'show_yang_zhang_vol', 'title': 'Show Yang-Zhang Vol', 'type': 'boolean', 'default': True}, {'id': 'show_composite_vol', 'title': 'Show Composite Vol', 'type': 'boolean', 'default': True}, {'id': 'show_regime_bands', 'title': 'Show Regime Bands', 'type': 'boolean', 'default': True}, {'id': 'show_volatility_bands', 'title': 'Show Volatility Bands', 'type': 'boolean', 'default': False}, {'id': 'show_vol_z_score', 'title': 'Show Vol Z-Score', 'type': 'boolean', 'default': False}, {'id': 'show_z_score_references', 'title': 'Show Z-Score References', 'type': 'boolean', 'default': False}, {'id': 'show_risk_zones', 'title': 'Show Risk Zones', 'type': 'boolean', 'default': True}],
    outputs=['parkinson_vol', 'garman_klass_vol', 'yang_zhang_vol', 'composite_vol', '___volatility_expanding', '___volatility_contracting', '___extreme_volatility', '___low_volatility_zone', '___trending_regime_detected', '___mean_reverting_regime', '___choppy_market_warning', '__high_confidence_regime', '___vcp_pattern_detected', '___vcp_breakout', '__elevated_risk___size_down_to_50_', '___high_risk___size_down_to_25_', '___extreme_risk___size_down_to_10_', '___possible_capitulation___high_risk_high_reward_setup', '__risk_normalizing___resume_standard_sizing', '___premium_compression___optimal_selling_environment', '__vol_awakening___directional_move_likely'],
    signals=['___volatility_expanding', '___volatility_contracting', '___extreme_volatility', '___low_volatility_zone', '___trending_regime_detected', '___mean_reverting_regime', '___choppy_market_warning', '__high_confidence_regime', '___vcp_pattern_detected', '___vcp_breakout', '__elevated_risk___size_down_to_50_', '___high_risk___size_down_to_25_', '___extreme_risk___size_down_to_10_', '___possible_capitulation___high_risk_high_reward_setup', '__risk_normalizing___resume_standard_sizing', '___premium_compression___optimal_selling_environment', '__vol_awakening___directional_move_likely'],
    requires=[],
    parity='exact',
)
