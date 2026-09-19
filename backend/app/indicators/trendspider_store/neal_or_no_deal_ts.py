"""
Neal or No Deal -- TrendSpider store indicator by Baba Neal.

Registered as "neal_or_no_deal_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6a98f8-neal-or-no-deal-%f0%9f%90%82%f0%9f%90%bb/)
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
    G_atr = G["atr"]
    G_close = G["close"]
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_ema = G["ema"]
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_highest = G["highest"]
    G_input = G["input"]
    G_low = G["low"]
    G_lowest = G["lowest"]
    G_open = G["open"]
    G_paint = G["paint"]
    G_paint_label_at_line = G["paint_label_at_line"]
    G_paint_overlay = G["paint_overlay"]
    G_paint_projection = G["paint_projection"]
    G_register_signal = G["register_signal"]
    G_request = G["request"]
    G_rsi = G["rsi"]
    G_series_of = G["series_of"]
    G_shift = G["shift"]
    G_sma = G["sma"]
    G_volume = G["volume"]
    def compactMoney(value=J.undefined, *_args):
        absoluteValue = J.get(G_Math, "abs")(value)
        if J.ge(absoluteValue, 1000000000):
            return J.template("$", J.get(J.div(value, 1000000000), "toFixed")(2), "B")
        if J.ge(absoluteValue, 1000000):
            return J.template("$", J.get(J.div(value, 1000000), "toFixed")(2), "M")
        if J.ge(absoluteValue, 1000):
            return J.template("$", J.get(J.div(value, 1000), "toFixed")(1), "K")
        return J.template("$", J.get(G_Math, "round")(value))
    def priceText(value=J.undefined, *_args):
        if (((value is None) or (value is J.undefined)) or (not J.truthy(J.get(G_Number, "isFinite")(value)))):
            return "N/A"
        return J.template("$", J.get(G_Number(value), "toFixed")(2))
    def signedNumber(value=J.undefined, *_args):
        roundedValue = J.get(G_Math, "round")(value)
        return (J.template("+", roundedValue) if J.gt(roundedValue, 0) else J.template(roundedValue))
    def biasName(value=J.undefined, *_args):
        if J.ge(value, 60):
            return "STRONG BULL"
        if J.ge(value, 20):
            return "BULLISH"
        if J.le(value, (-60)):
            return "STRONG BEAR"
        if J.le(value, (-20)):
            return "BEARISH"
        return "NEUTRAL"
    def biasColor(value=J.undefined, *_args):
        if J.ge(value, 60):
            return "#00E676"
        if J.ge(value, 20):
            return "#69F0AE"
        if J.le(value, (-60)):
            return "#FF1744"
        if J.le(value, (-20)):
            return "#FF5252"
        return "#CFD8DC"
    def labelCell(text=J.undefined, *_args):
        return J.obj(("text", text), ("color", "#90A4AE"), ("background", "#0D171E"), ("border", "solid #263C47 1px"), ("padding", "5px 8px"), ("fontSize", "10px"), ("fontWeight", "bold"), ("textAlign", "left"), ("whiteSpace", "nowrap"))
    def valueCell(text=J.undefined, color=J.undefined, *_args):
        return J.obj(("text", text), ("color", (_t1 if J.truthy(_t1 := color) else "#FFFFFF")), ("background", "#16242D"), ("border", "solid #263C47 1px"), ("padding", "5px 8px"), ("fontSize", "10px"), ("fontWeight", "bold"), ("textAlign", "right"), ("whiteSpace", "nowrap"))
    def normalPdf(value=J.undefined, *_args):
        return J.div(J.get(G_Math, "exp")(J.mul(J.mul((-0.5), value), value)), J.get(G_Math, "sqrt")(J.mul(2, J.get(G_Math, "PI"))))
    def gammaValue(spotPrice=J.undefined, strikePrice=J.undefined, yearsToExpiration=J.undefined, volatility=J.undefined, *_args):
        safeTime = J.get(G_Math, "max")(yearsToExpiration, 0.0005)
        safeVolatility = J.get(G_Math, "max")(volatility, 0.01)
        squareRootTime = J.get(G_Math, "sqrt")(safeTime)
        distributionValue = J.div(J.add(J.get(G_Math, "log")(J.div(spotPrice, strikePrice)), J.mul(J.add(J.sub(RISK_FREE_RATE, DIVIDEND_YIELD), J.div(J.mul(safeVolatility, safeVolatility), 2)), safeTime)), J.mul(safeVolatility, squareRootTime))
        return J.div(J.mul(J.get(G_Math, "exp")(J.mul(J.neg(DIVIDEND_YIELD), safeTime)), normalPdf(distributionValue)), J.mul(J.mul(spotPrice, safeVolatility), squareRootTime))
    def chainOpenInterest(chain=J.undefined, *_args):
        totalOpenInterest = 0
        if ((not J.truthy(chain)) or (not J.truthy(J.get(chain, "resultByStrike")))):
            return 0
        def _f1(strikeKey=J.undefined, *_args):
            nonlocal totalOpenInterest
            strikeRow = J.get(J.get(chain, "resultByStrike"), strikeKey)
            totalOpenInterest = J.add(totalOpenInterest, (_t1 if J.truthy(_t1 := G_Number((J.get(J.get(strikeRow, "C"), "oi") if J.truthy(_t2 := J.get(strikeRow, "C")) else _t2))) else 0))
            totalOpenInterest = J.add(totalOpenInterest, (_t3 if J.truthy(_t3 := G_Number((J.get(J.get(strikeRow, "P"), "oi") if J.truthy(_t4 := J.get(strikeRow, "P")) else _t4))) else 0))
        J.get(J.get(G_Object, "keys")(J.get(chain, "resultByStrike")), "forEach")(_f1)
        return totalOpenInterest
    def projectedLevel(value=J.undefined, *_args):
        projection = J.JSArray([])
        projectionIndex = 0
        while J.lt(projectionIndex, PROJECTION_BARS):
            J.get(projection, "push")(value)
            projectionIndex = J.inc(projectionIndex)
        return projection
    def uniqueSortedLevels(levels=J.undefined, ascending=J.undefined, *_args):
        seenLevels = J.obj()
        def _f1(level=J.undefined, *_args):
            if (((J.get(level, "value") is None) or (J.get(level, "value") is J.undefined)) or (not J.truthy(J.get(G_Number, "isFinite")(J.get(level, "value"))))):
                return False
            levelKey = J.get(G_Number(J.get(level, "value")), "toFixed")(4)
            if J.truthy(J.get(seenLevels, levelKey)):
                return False
            J.set(seenLevels, levelKey, True)
            return True
        def _f2(firstLevel=J.undefined, secondLevel=J.undefined, *_args):
            return (J.sub(J.get(firstLevel, "value"), J.get(secondLevel, "value")) if J.truthy(ascending) else J.sub(J.get(secondLevel, "value"), J.get(firstLevel, "value")))
        return J.get(J.get(levels, "filter")(_f1), "sort")(_f2)
    def nearestOptionStrike(targetValue=J.undefined, *_args):
        if (J.seq(J.get(availableOptionStrikes, "length"), 0) or (not J.truthy(J.get(G_Number, "isFinite")(targetValue)))):
            return None
        def _f1(nearestStrike=J.undefined, candidateStrike=J.undefined, *_args):
            return (candidateStrike if J.lt(J.get(G_Math, "abs")(J.sub(candidateStrike, targetValue)), J.get(G_Math, "abs")(J.sub(nearestStrike, targetValue))) else nearestStrike)
        return J.get(availableOptionStrikes, "reduce")(_f1, J.get(availableOptionStrikes, 0))
    def paintGammaLevel(value=J.undefined, enabled=J.undefined, lineName=J.undefined, projectionName=J.undefined, labelText=J.undefined, lineColor=J.undefined, labelOffset=J.undefined, lineThickness=J.undefined, *_args):
        validLevel = (J.get(G_Number, "isFinite")(value) if J.truthy(_t1 := ((value is not J.undefined) if J.truthy(_t2 := ((value is not None) if J.truthy(_t3 := enabled) else _t3)) else _t2)) else _t1)
        levelSeries = G_series_of(None)
        if J.truthy(validLevel):
            candleIndex_3 = 0
            while J.lt(candleIndex_3, J.get(G_close, "length")):
                J.set(levelSeries, candleIndex_3, value)
                candleIndex_3 = J.inc(candleIndex_3)
        gammaLine = G_paint(levelSeries, J.obj(("name", lineName), ("color", lineColor), ("style", "line"), ("thickness", lineThickness), ("ignoreWhenScaling", True), ("hideInLegend", True)))
        G_paint_projection(projectedLevel((value if J.truthy(validLevel) else None)), J.obj(("name", projectionName), ("color", lineColor), ("style", "line"), ("thickness", lineThickness), ("ignoreWhenScaling", True), ("hideInLegend", True)))
        G_paint_label_at_line(gammaLine, J.get(G_Math, "max")(0, J.sub(lastIndex, labelOffset)), (labelText if J.truthy(validLevel) else " "), J.obj(("color", "#FFFFFF"), ("background_color", "#101820"), ("border_color", lineColor), ("border_width", 1), ("border_radius", 3)))
    G_describe_indicator("Neal or No Deal ")
    dashPosition = J.get(G_input, "select")("Dash Position", "top_right", J.JSArray(["top_left", "top_right", "center_left", "center_right", "bottom_left", "bottom_right"]))
    showGammaLines = J.get(G_input, "boolean")("Show Gamma Lines", True)
    callLineColor = J.get(G_input, "color")("Call Line", "#00E676")
    putLineColor = J.get(G_input, "color")("Put Line", "#FF1744")
    FAST_LENGTH = 9
    MID_LENGTH = 21
    SLOW_LENGTH = 50
    RSI_LENGTH = 14
    ATR_LENGTH = 14
    VOLUME_LENGTH = 20
    STRUCTURE_LENGTH = 10
    EXECUTION_THRESHOLD = 55
    MINIMUM_TECHNICAL = 55
    MINIMUM_OPTIONS = 15
    MINIMUM_RR = 1
    MINIMUM_PREMIUM = 25000
    MAXIMUM_DTE = 90
    GAMMA_MINIMUM_OI = 100
    PROJECTION_BARS = 40
    RISK_FREE_RATE = 0.045
    DIVIDEND_YIELD = 0.012
    fastEMA = G_ema(G_close, FAST_LENGTH)
    midEMA = G_ema(G_close, MID_LENGTH)
    slowEMA = G_ema(G_close, SLOW_LENGTH)
    previousFastEMA = G_shift(fastEMA, 1)
    previousMidEMA = G_shift(midEMA, 1)
    rsiValue = G_rsi(G_close, RSI_LENGTH)
    atrValue = G_atr(ATR_LENGTH)
    averageVolume = G_sma(G_volume, VOLUME_LENGTH)
    structureHigh = G_shift(G_highest(G_high, STRUCTURE_LENGTH), 1)
    structureLow = G_shift(G_lowest(G_low, STRUCTURE_LENGTH), 1)
    def _f1(currentVolume=J.undefined, averageValue=J.undefined, *_args):
        if ((averageValue is None) or J.le(averageValue, 0)):
            return 0
        return J.div(currentVolume, averageValue)
    relativeVolume = G_for_every(G_volume, averageVolume, _f1)
    bullishTechnicalScore = J.JSArray([])
    bearishTechnicalScore = J.JSArray([])
    candleIndex = 0
    while J.lt(candleIndex, J.get(G_close, "length")):
        bullishPoints = 0
        bearishPoints = 0
        if J.gt(J.get(fastEMA, candleIndex), J.get(midEMA, candleIndex)):
            bullishPoints = J.add(bullishPoints, 20)
        elif J.lt(J.get(fastEMA, candleIndex), J.get(midEMA, candleIndex)):
            bearishPoints = J.add(bearishPoints, 20)
        if J.gt(J.get(G_close, candleIndex), J.get(midEMA, candleIndex)):
            bullishPoints = J.add(bullishPoints, 15)
        elif J.lt(J.get(G_close, candleIndex), J.get(midEMA, candleIndex)):
            bearishPoints = J.add(bearishPoints, 15)
        if J.gt(J.get(G_close, candleIndex), J.get(slowEMA, candleIndex)):
            bullishPoints = J.add(bullishPoints, 15)
        elif J.lt(J.get(G_close, candleIndex), J.get(slowEMA, candleIndex)):
            bearishPoints = J.add(bearishPoints, 15)
        if (J.gt(J.get(fastEMA, candleIndex), J.get(previousFastEMA, candleIndex)) and J.gt(J.get(midEMA, candleIndex), J.get(previousMidEMA, candleIndex))):
            bullishPoints = J.add(bullishPoints, 15)
        if (J.lt(J.get(fastEMA, candleIndex), J.get(previousFastEMA, candleIndex)) and J.lt(J.get(midEMA, candleIndex), J.get(previousMidEMA, candleIndex))):
            bearishPoints = J.add(bearishPoints, 15)
        if (J.ge(J.get(rsiValue, candleIndex), 52) and J.le(J.get(rsiValue, candleIndex), 78)):
            bullishPoints = J.add(bullishPoints, 15)
        if (J.le(J.get(rsiValue, candleIndex), 48) and J.ge(J.get(rsiValue, candleIndex), 22)):
            bearishPoints = J.add(bearishPoints, 15)
        if J.ge(J.get(relativeVolume, candleIndex), 0.8):
            if J.ge(J.get(G_close, candleIndex), J.get(G_open, candleIndex)):
                bullishPoints = J.add(bullishPoints, 10)
            else:
                bearishPoints = J.add(bearishPoints, 10)
        if ((J.get(structureHigh, candleIndex) is not None) and J.gt(J.get(G_close, candleIndex), J.get(structureHigh, candleIndex))):
            bullishPoints = J.add(bullishPoints, 10)
        if ((J.get(structureLow, candleIndex) is not None) and J.lt(J.get(G_close, candleIndex), J.get(structureLow, candleIndex))):
            bearishPoints = J.add(bearishPoints, 10)
        J.get(bullishTechnicalScore, "push")(J.get(G_Math, "min")(100, bullishPoints))
        J.get(bearishTechnicalScore, "push")(J.get(G_Math, "min")(100, bearishPoints))
        candleIndex = J.inc(candleIndex)
    technicalDirectionalScore = J.JSArray([])
    candleIndex_2 = 0
    while J.lt(candleIndex_2, J.get(G_close, "length")):
        J.get(technicalDirectionalScore, "push")(J.sub(J.get(bullishTechnicalScore, candleIndex_2), J.get(bearishTechnicalScore, candleIndex_2)))
        candleIndex_2 = J.inc(candleIndex_2)
    lastIndex = J.sub(J.get(G_close, "length"), 1)
    currentPrice = J.get(G_close, lastIndex)
    currentATR = (J.get(atrValue, lastIndex) if (J.truthy(J.get(G_Number, "isFinite")(J.get(atrValue, lastIndex))) and J.gt(J.get(atrValue, lastIndex), 0)) else J.mul(currentPrice, 0.01))
    unusualOptionsData = J.get(G_request, "unusual_options")(J.get(G_constants, "ticker"))
    callPressure = 0
    putPressure = 0
    callPremium = 0
    putPremium = 0
    acceptedTrades = 0
    sweepCount = 0
    optionsByStrike = J.obj()
    if (J.truthy(unusualOptionsData) and J.gt(J.get(unusualOptionsData, "length"), 0)):
        def _f2(trade=J.undefined, *_args):
            nonlocal acceptedTrades, sweepCount, callPressure, callPremium, putPressure, putPremium
            premium = J.get(G_Math, "abs")((_t1 if J.truthy(_t1 := G_Number(J.get(trade, "costBasis"))) else 0))
            contractSize = J.get(G_Math, "abs")((_t2 if J.truthy(_t2 := G_Number(J.get(trade, "size"))) else 0))
            openInterest = J.get(G_Math, "abs")((_t3 if J.truthy(_t3 := G_Number(J.get(trade, "oi"))) else 0))
            oiPercentage = J.get(G_Math, "abs")((_t4 if J.truthy(_t4 := G_Number(J.get(trade, "oiPercent"))) else 0))
            daysToExpiration = G_Number(J.get(trade, "daysToExp"))
            strikePrice = G_Number(J.get(trade, "strike"))
            optionType = J.get(G_String((_t5 if J.truthy(_t5 := J.get(trade, "type")) else "")), "toUpperCase")()
            dealType = J.get(G_String((_t6 if J.truthy(_t6 := J.get(trade, "dealType")) else "")), "toUpperCase")()
            moneyStatus = J.get(G_String((_t7 if J.truthy(_t7 := J.get(trade, "moneyStatus")) else "")), "toUpperCase")()
            if J.lt(premium, MINIMUM_PREMIUM):
                return J.undefined
            if (((not J.truthy(J.get(G_Number, "isFinite")(daysToExpiration))) or J.lt(daysToExpiration, 0)) or J.gt(daysToExpiration, MAXIMUM_DTE)):
                return J.undefined
            if (J.sne(optionType, "CALL") and J.sne(optionType, "PUT")):
                return J.undefined
            if (not J.truthy(J.get(G_Number, "isFinite")(strikePrice))):
                return J.undefined
            acceptedTrades = J.add(acceptedTrades, 1)
            dealMultiplier = 1
            if J.seq(dealType, "SWEEP"):
                dealMultiplier = 1.25
                sweepCount = J.add(sweepCount, 1)
            elif J.seq(dealType, "BLOCK"):
                dealMultiplier = 1.15
            expirationMultiplier = 1
            if J.seq(daysToExpiration, 0):
                expirationMultiplier = 1.2
            elif J.le(daysToExpiration, 7):
                expirationMultiplier = 1.15
            elif J.le(daysToExpiration, 45):
                expirationMultiplier = 1.05
            else:
                expirationMultiplier = 0.9
            moneyMultiplier = 1
            if J.seq(moneyStatus, "ATM"):
                moneyMultiplier = 1.15
            elif J.seq(moneyStatus, "ITM"):
                moneyMultiplier = 1.05
            elif J.seq(moneyStatus, "OTM"):
                moneyMultiplier = 0.95
            participationMultiplier = J.add(1, J.div(J.get(G_Math, "min")(oiPercentage, 25), 100))
            if (J.gt(openInterest, 0) and J.gt(contractSize, openInterest)):
                participationMultiplier = J.add(participationMultiplier, 0.2)
            weightedPressure = J.mul(J.mul(J.mul(J.mul(premium, dealMultiplier), expirationMultiplier), moneyMultiplier), participationMultiplier)
            if (not J.truthy(J.get(optionsByStrike, strikePrice))):
                J.set(optionsByStrike, strikePrice, J.obj(("callPressure", 0), ("putPressure", 0), ("totalPressure", 0)))
            if J.seq(optionType, "CALL"):
                callPressure = J.add(callPressure, weightedPressure)
                callPremium = J.add(callPremium, premium)
                _t8 = J.get(optionsByStrike, strikePrice)
                J.set(_t8, "callPressure", J.add(J.get(_t8, "callPressure"), weightedPressure))
            else:
                putPressure = J.add(putPressure, weightedPressure)
                putPremium = J.add(putPremium, premium)
                _t9 = J.get(optionsByStrike, strikePrice)
                J.set(_t9, "putPressure", J.add(J.get(_t9, "putPressure"), weightedPressure))
            _t10 = J.get(optionsByStrike, strikePrice)
            J.set(_t10, "totalPressure", J.add(J.get(_t10, "totalPressure"), weightedPressure))
        J.get(unusualOptionsData, "forEach")(_f2)
    totalOptionsPressure = J.add(callPressure, putPressure)
    optionsScore = 0
    if J.gt(totalOptionsPressure, 0):
        optionsScore = J.mul(J.div(J.sub(callPressure, putPressure), totalOptionsPressure), 100)
    optionsScore = J.get(G_Math, "max")((-100), J.get(G_Math, "min")(100, optionsScore))
    premiumRatioText = "NO FLOW"
    if (J.gt(callPremium, 0) or J.gt(putPremium, 0)):
        if J.ge(callPremium, putPremium):
            callRatio = (J.div(callPremium, putPremium) if J.gt(putPremium, 0) else 99)
            premiumRatioText = J.template(J.get(callRatio, "toFixed")(2), "x CALL")
        else:
            putRatio = (J.div(putPremium, callPremium) if J.gt(callPremium, 0) else 99)
            premiumRatioText = J.template(J.get(putRatio, "toFixed")(2), "x PUT")
    dominantStrike = None
    dominantStrikePressure = 0
    dominantStrikeType = "NONE"
    def _f3(strikeKey=J.undefined, *_args):
        nonlocal dominantStrikePressure, dominantStrike, dominantStrikeType
        strikePrice = G_Number(strikeKey)
        strikeData = J.get(optionsByStrike, strikeKey)
        closeEnough = J.le(J.div(J.get(G_Math, "abs")(J.sub(strikePrice, currentPrice)), currentPrice), 0.08)
        if (J.truthy(closeEnough) and J.gt(J.get(strikeData, "totalPressure"), dominantStrikePressure)):
            dominantStrikePressure = J.get(strikeData, "totalPressure")
            dominantStrike = strikePrice
            dominantStrikeType = ("CALL" if J.ge(J.get(strikeData, "callPressure"), J.get(strikeData, "putPressure")) else "PUT")
    J.get(J.get(G_Object, "keys")(optionsByStrike), "forEach")(_f3)
    dominantStrikeText = (J.template(dominantStrikeType, " $", dominantStrike) if (dominantStrike is not None) else "NONE NEARBY")
    gammaDataAvailable = False
    gammaExpirationDTE = None
    gammaAtmIV = None
    estimatedNetGEX = 0
    gammaCallWall = None
    gammaPutWall = None
    gammaMagnet = None
    gammaFlip = None
    expectedMove = None
    expectedMoveUpper = None
    expectedMoveLower = None
    gammaByStrike = J.obj()
    try:
        optionsSchedule = J.get(G_request, "options_schedule")(J.get(G_constants, "ticker"))
        if (J.truthy(optionsSchedule) and J.gt(J.get(optionsSchedule, "length"), 0)):
            def _f4(firstExpiration=J.undefined, secondExpiration=J.undefined, *_args):
                return J.sub(J.get(J.get(firstExpiration, "expiration"), "dte"), J.get(J.get(secondExpiration, "expiration"), "dte"))
            sortedSchedule = J.get(J.get(optionsSchedule, "slice")(), "sort")(_f4)
            selectedExpiration = J.get(sortedSchedule, 0)
            selectedChain = J.get(G_request, "options_data_for_expiration")(J.get(G_constants, "ticker"), J.get(J.get(selectedExpiration, "expiration"), "code"), J.JSArray(["oi", "iv"]))
            if J.lt(chainOpenInterest(selectedChain), GAMMA_MINIMUM_OI):
                scheduleIndex = 1
                while J.lt(scheduleIndex, J.get(sortedSchedule, "length")):
                    candidateExpiration = J.get(sortedSchedule, scheduleIndex)
                    candidateChain = J.get(G_request, "options_data_for_expiration")(J.get(G_constants, "ticker"), J.get(J.get(candidateExpiration, "expiration"), "code"), J.JSArray(["oi", "iv"]))
                    if J.ge(chainOpenInterest(candidateChain), GAMMA_MINIMUM_OI):
                        selectedExpiration = candidateExpiration
                        selectedChain = candidateChain
                        break
                    scheduleIndex = J.inc(scheduleIndex)
            resultByStrike = (J.get(selectedChain, "resultByStrike") if J.truthy(_t5 := selectedChain) else _t5)
            if (J.truthy(resultByStrike) and J.ge(chainOpenInterest(selectedChain), GAMMA_MINIMUM_OI)):
                gammaExpirationDTE = J.get(J.get(selectedExpiration, "expiration"), "dte")
                timeToExpiration = J.div(J.get(G_Math, "max")(gammaExpirationDTE, 0.25), 365)
                nearestIVDistance = G_Infinity
                def _f6(strikeKey=J.undefined, *_args):
                    strikePrice = G_Number(strikeKey)
                    strikeRow = J.get(resultByStrike, strikeKey)
                    if (not J.truthy(J.get(G_Number, "isFinite")(strikePrice))):
                        return J.undefined
                    strikeGEX = 0
                    strikeOI = 0
                    def _f1(side=J.undefined, *_args):
                        nonlocal strikeGEX, strikeOI, nearestIVDistance, gammaAtmIV
                        contract = J.get(strikeRow, side)
                        if (not J.truthy(contract)):
                            return J.undefined
                        openInterest = J.get(G_Math, "max")(0, (_t1 if J.truthy(_t1 := G_Number(J.get(contract, "oi"))) else 0))
                        normalizedIV = G_Number(J.get(contract, "iv"))
                        if (not J.truthy(J.get(G_Number, "isFinite")(normalizedIV))):
                            normalizedIV = 0.5
                        if J.gt(normalizedIV, 3):
                            normalizedIV = J.div(normalizedIV, 100)
                        normalizedIV = J.get(G_Math, "max")(0.005, J.get(G_Math, "min")(3, normalizedIV))
                        contractGamma = gammaValue(currentPrice, strikePrice, timeToExpiration, normalizedIV)
                        direction = (1 if J.seq(side, "C") else (-1))
                        contractGEX = J.mul(J.mul(J.mul(J.mul(J.mul(J.mul(contractGamma, openInterest), 100), currentPrice), currentPrice), 0.01), direction)
                        strikeGEX = J.add(strikeGEX, contractGEX)
                        strikeOI = J.add(strikeOI, openInterest)
                        distanceFromPrice = J.get(G_Math, "abs")(J.sub(strikePrice, currentPrice))
                        if J.lt(distanceFromPrice, nearestIVDistance):
                            nearestIVDistance = distanceFromPrice
                            gammaAtmIV = normalizedIV
                    J.get(J.JSArray(["C", "P"]), "forEach")(_f1)
                    J.set(gammaByStrike, strikePrice, J.obj(("gex", strikeGEX), ("oi", strikeOI)))
                J.get(J.get(G_Object, "keys")(resultByStrike), "forEach")(_f6)
                def _f7(firstStrike=J.undefined, secondStrike=J.undefined, *_args):
                    return J.sub(firstStrike, secondStrike)
                allGammaStrikes = J.get(J.get(J.get(G_Object, "keys")(gammaByStrike), "map")(G_Number), "sort")(_f7)
                def _f8(strikePrice=J.undefined, *_args):
                    return J.le(J.div(J.get(G_Math, "abs")(J.sub(strikePrice, currentPrice)), currentPrice), 0.15)
                nearbyGammaStrikes = J.get(allGammaStrikes, "filter")(_f8)
                if J.seq(J.get(nearbyGammaStrikes, "length"), 0):
                    nearbyGammaStrikes = allGammaStrikes
                maximumPositiveGEX = J.neg(G_Infinity)
                minimumNegativeGEX = G_Infinity
                magnetNumerator = 0
                magnetDenominator = 0
                def _f9(strikePrice=J.undefined, *_args):
                    nonlocal estimatedNetGEX, magnetNumerator, magnetDenominator, maximumPositiveGEX, gammaCallWall, minimumNegativeGEX, gammaPutWall
                    strikeGEX = J.get(J.get(gammaByStrike, strikePrice), "gex")
                    estimatedNetGEX = J.add(estimatedNetGEX, strikeGEX)
                    magnetNumerator = J.add(magnetNumerator, J.mul(strikePrice, J.get(G_Math, "abs")(strikeGEX)))
                    magnetDenominator = J.add(magnetDenominator, J.get(G_Math, "abs")(strikeGEX))
                    if J.gt(strikeGEX, maximumPositiveGEX):
                        maximumPositiveGEX = strikeGEX
                        gammaCallWall = strikePrice
                    if J.lt(strikeGEX, minimumNegativeGEX):
                        minimumNegativeGEX = strikeGEX
                        gammaPutWall = strikePrice
                J.get(nearbyGammaStrikes, "forEach")(_f9)
                gammaMagnet = (J.div(magnetNumerator, magnetDenominator) if J.gt(magnetDenominator, 0) else currentPrice)
                cumulativeGEX = 0
                def _f10(strikePrice=J.undefined, *_args):
                    nonlocal cumulativeGEX, gammaFlip
                    previousCumulative = cumulativeGEX
                    cumulativeGEX = J.add(cumulativeGEX, J.get(J.get(gammaByStrike, strikePrice), "gex"))
                    crossedZero = (_t1 if J.truthy(_t1 := (J.ge(cumulativeGEX, 0) if J.truthy(_t2 := J.lt(previousCumulative, 0)) else _t2)) else (J.le(cumulativeGEX, 0) if J.truthy(_t3 := J.gt(previousCumulative, 0)) else _t3))
                    if (J.truthy(crossedZero) and ((gammaFlip is None) or J.lt(J.get(G_Math, "abs")(J.sub(strikePrice, currentPrice)), J.get(G_Math, "abs")(J.sub(gammaFlip, currentPrice))))):
                        gammaFlip = strikePrice
                J.get(nearbyGammaStrikes, "forEach")(_f10)
                if ((gammaAtmIV is not None) and J.lt(gammaAtmIV, 2)):
                    expectedMove = J.mul(J.mul(currentPrice, gammaAtmIV), J.get(G_Math, "sqrt")(timeToExpiration))
                    expectedMoveUpper = J.add(currentPrice, expectedMove)
                    expectedMoveLower = J.sub(currentPrice, expectedMove)
                gammaDataAvailable = (J.gt(magnetDenominator, 0) if J.truthy(_t11 := J.gt(J.get(nearbyGammaStrikes, "length"), 0)) else _t11)
    except Exception as _e12:
        gammaRequestError = J.catch_value(_e12)
        gammaDataAvailable = False
    gammaRegime = "UNAVAILABLE"
    gammaRegimeColor = "#90A4AE"
    if J.truthy(gammaDataAvailable):
        if ((J.lt(estimatedNetGEX, 0) and (gammaFlip is not None)) and J.lt(currentPrice, gammaFlip)):
            gammaRegime = "AMPLIFICATION"
            gammaRegimeColor = "#FF1744"
        elif J.lt(estimatedNetGEX, 0):
            gammaRegime = "NEGATIVE GAMMA"
            gammaRegimeColor = "#FF5252"
        elif ((gammaMagnet is not None) and J.lt(J.div(J.get(G_Math, "abs")(J.sub(currentPrice, gammaMagnet)), currentPrice), 0.003)):
            gammaRegime = "PIN RISK"
            gammaRegimeColor = "#FFD600"
        else:
            gammaRegime = "POSITIVE GAMMA"
            gammaRegimeColor = "#69F0AE"
    gammaDirectionalScore = 0
    if J.truthy(gammaDataAvailable):
        if (gammaMagnet is not None):
            gammaDirectionalScore = J.add(gammaDirectionalScore, (35 if J.ge(currentPrice, gammaMagnet) else (-35)))
        if (gammaFlip is not None):
            gammaDirectionalScore = J.add(gammaDirectionalScore, (35 if J.ge(currentPrice, gammaFlip) else (-35)))
        if ((gammaCallWall is not None) and J.gt(currentPrice, gammaCallWall)):
            gammaDirectionalScore = J.add(gammaDirectionalScore, 30)
        if ((gammaPutWall is not None) and J.lt(currentPrice, gammaPutWall)):
            gammaDirectionalScore = J.sub(gammaDirectionalScore, 30)
    gammaDirectionalScore = J.get(G_Math, "max")((-100), J.get(G_Math, "min")(100, gammaDirectionalScore))
    currentTechnicalScore = J.get(technicalDirectionalScore, lastIndex)
    combinedScore = J.add(J.add(J.mul(currentTechnicalScore, 0.55), J.mul(optionsScore, 0.25)), J.mul(gammaDirectionalScore, 0.2))
    signalStrength = J.get(G_Math, "min")(100, J.get(G_Math, "round")(J.get(G_Math, "abs")(combinedScore)))
    technicalLongConfirmed = (J.gt(J.get(G_close, lastIndex), J.get(midEMA, lastIndex)) if J.truthy(_t13 := (J.gt(J.get(fastEMA, lastIndex), J.get(midEMA, lastIndex)) if J.truthy(_t14 := J.ge(J.get(bullishTechnicalScore, lastIndex), MINIMUM_TECHNICAL)) else _t14)) else _t13)
    technicalShortConfirmed = (J.lt(J.get(G_close, lastIndex), J.get(midEMA, lastIndex)) if J.truthy(_t15 := (J.lt(J.get(fastEMA, lastIndex), J.get(midEMA, lastIndex)) if J.truthy(_t16 := J.ge(J.get(bearishTechnicalScore, lastIndex), MINIMUM_TECHNICAL)) else _t16)) else _t15)
    optionsLongConfirmed = J.ge(optionsScore, MINIMUM_OPTIONS)
    optionsShortConfirmed = J.le(optionsScore, J.neg(MINIMUM_OPTIONS))
    gammaLongAllowed = (_t17 if J.truthy(_t17 := (not J.truthy(gammaDataAvailable))) else J.gt(gammaDirectionalScore, (-35)))
    gammaShortAllowed = (_t18 if J.truthy(_t18 := (not J.truthy(gammaDataAvailable))) else J.lt(gammaDirectionalScore, 35))
    baseBuyCondition = (gammaLongAllowed if J.truthy(_t19 := (optionsLongConfirmed if J.truthy(_t20 := (technicalLongConfirmed if J.truthy(_t21 := J.ge(combinedScore, EXECUTION_THRESHOLD)) else _t21)) else _t20)) else _t19)
    baseSellCondition = (gammaShortAllowed if J.truthy(_t22 := (optionsShortConfirmed if J.truthy(_t23 := (technicalShortConfirmed if J.truthy(_t24 := J.le(combinedScore, J.neg(EXECUTION_THRESHOLD))) else _t24)) else _t23)) else _t22)
    gammaLevelCandidates = J.JSArray([J.obj(("value", gammaMagnet), ("name", "MAGNET")), J.obj(("value", gammaFlip), ("name", "GAMMA FLIP")), J.obj(("value", gammaCallWall), ("name", "CALL WALL")), J.obj(("value", gammaPutWall), ("name", "PUT WALL")), J.obj(("value", expectedMoveUpper), ("name", "EM HIGH")), J.obj(("value", expectedMoveLower), ("name", "EM LOW"))])
    tradeEntry = currentPrice
    tradeDirection = "NONE"
    tradeStop = None
    tradeTargetOne = None
    tradeTargetTwo = None
    tradeTargetOneName = ""
    tradeTargetTwoName = ""
    tradeTargetOneRR = None
    if J.truthy(baseBuyCondition):
        tradeDirection = "LONG"
        def _f25(level=J.undefined, *_args):
            return (J.ge(J.get(level, "value"), J.add(tradeEntry, J.mul(currentATR, 0.25))) if J.truthy(_t1 := J.get(G_Number, "isFinite")(J.get(level, "value"))) else _t1)
        longTargets = uniqueSortedLevels(J.get(gammaLevelCandidates, "filter")(_f25), True)
        def _f26(level=J.undefined, *_args):
            return (J.le(J.get(level, "value"), J.sub(tradeEntry, J.mul(currentATR, 0.8))) if J.truthy(_t1 := J.get(G_Number, "isFinite")(J.get(level, "value"))) else _t1)
        longStops = uniqueSortedLevels(J.get(gammaLevelCandidates, "filter")(_f26), False)
        tradeStop = (J.get(J.get(longStops, 0), "value") if J.gt(J.get(longStops, "length"), 0) else J.sub(tradeEntry, J.mul(currentATR, 1.25)))
        if J.gt(J.get(longTargets, "length"), 0):
            tradeTargetOne = J.get(J.get(longTargets, 0), "value")
            tradeTargetOneName = J.get(J.get(longTargets, 0), "name")
        if J.gt(J.get(longTargets, "length"), 1):
            tradeTargetTwo = J.get(J.get(longTargets, 1), "value")
            tradeTargetTwoName = J.get(J.get(longTargets, 1), "name")
    if J.truthy(baseSellCondition):
        tradeDirection = "SHORT"
        def _f27(level=J.undefined, *_args):
            return (J.le(J.get(level, "value"), J.sub(tradeEntry, J.mul(currentATR, 0.25))) if J.truthy(_t1 := J.get(G_Number, "isFinite")(J.get(level, "value"))) else _t1)
        shortTargets = uniqueSortedLevels(J.get(gammaLevelCandidates, "filter")(_f27), False)
        def _f28(level=J.undefined, *_args):
            return (J.ge(J.get(level, "value"), J.add(tradeEntry, J.mul(currentATR, 0.8))) if J.truthy(_t1 := J.get(G_Number, "isFinite")(J.get(level, "value"))) else _t1)
        shortStops = uniqueSortedLevels(J.get(gammaLevelCandidates, "filter")(_f28), True)
        tradeStop = (J.get(J.get(shortStops, 0), "value") if J.gt(J.get(shortStops, "length"), 0) else J.add(tradeEntry, J.mul(currentATR, 1.25)))
        if J.gt(J.get(shortTargets, "length"), 0):
            tradeTargetOne = J.get(J.get(shortTargets, 0), "value")
            tradeTargetOneName = J.get(J.get(shortTargets, 0), "name")
        if J.gt(J.get(shortTargets, "length"), 1):
            tradeTargetTwo = J.get(J.get(shortTargets, 1), "value")
            tradeTargetTwoName = J.get(J.get(shortTargets, 1), "name")
    if ((tradeStop is not None) and (tradeTargetOne is not None)):
        tradeRisk = J.get(G_Math, "abs")(J.sub(tradeEntry, tradeStop))
        if J.gt(tradeRisk, 0):
            tradeTargetOneRR = J.div(J.get(G_Math, "abs")(J.sub(tradeTargetOne, tradeEntry)), tradeRisk)
    forceDebitSpread = (J.lt(tradeTargetOneRR, 1.5) if J.truthy(_t29 := (J.ge(tradeTargetOneRR, 1) if J.truthy(_t30 := (tradeTargetOneRR is not None)) else _t30)) else _t29)
    validTradeMap = (J.ge(tradeTargetOneRR, MINIMUM_RR) if J.truthy(_t31 := (tradeTargetOneRR is not None)) else _t31)
    executeBuy = (validTradeMap if J.truthy(_t32 := baseBuyCondition) else _t32)
    executeSell = (validTradeMap if J.truthy(_t33 := baseSellCondition) else _t33)
    recommendation = "NO TRADE"
    action = "WAIT"
    status = "MIXED CONDITIONS"
    decisionColor = "#455A64"
    decisionIcon = "●"
    dataConflict = (_t34 if J.truthy(_t34 := (J.le(optionsScore, (-20)) if J.truthy(_t35 := J.ge(currentTechnicalScore, 20)) else _t35)) else (J.ge(optionsScore, 20) if J.truthy(_t36 := J.le(currentTechnicalScore, (-20))) else _t36))
    gammaConflict = ((_t38 if J.truthy(_t38 := (J.le(gammaDirectionalScore, (-35)) if J.truthy(_t39 := J.ge(currentTechnicalScore, 20)) else _t39)) else (J.ge(gammaDirectionalScore, 35) if J.truthy(_t40 := J.le(currentTechnicalScore, (-20))) else _t40)) if J.truthy(_t37 := gammaDataAvailable) else _t37)
    if J.truthy(executeBuy):
        recommendation = "BUY"
        action = "LONG CONFIRMED"
        status = "TECH + FLOW + GAMMA AGREE"
        decisionColor = "#008F5A"
        decisionIcon = "\ud83d\udc02"
    elif J.truthy(executeSell):
        recommendation = "SELL"
        action = "SHORT CONFIRMED"
        status = "TECH + FLOW + GAMMA AGREE"
        decisionColor = "#C40000"
        decisionIcon = "\ud83d\udc3b"
    elif J.ge(combinedScore, 25):
        recommendation = "BULLISH WATCH"
        action = "WAIT FOR BUY"
        status = "BELOW EXECUTION"
        decisionColor = "#2E7D32"
        decisionIcon = "\ud83d\udc40"
    elif J.le(combinedScore, (-25)):
        recommendation = "BEARISH WATCH"
        action = "WAIT FOR SELL"
        status = "BELOW EXECUTION"
        decisionColor = "#B71C1C"
        decisionIcon = "\ud83d\udc40"
    if J.seq(acceptedTrades, 0):
        status = "OPTIONS DATA UNAVAILABLE"
    elif J.truthy(dataConflict):
        status = "TECH + OPTIONS CONFLICT"
    elif J.truthy(gammaConflict):
        status = "GAMMA POSITIONING CONFLICT"
    elif ((J.truthy(baseBuyCondition) or J.truthy(baseSellCondition)) and (not J.truthy(validTradeMap))):
        status = "TARGET TOO CLOSE - POOR R:R"
    elif (J.ge(J.get(G_Math, "abs")(currentTechnicalScore), 20) and J.lt(J.get(G_Math, "abs")(optionsScore), MINIMUM_OPTIONS)):
        status = "WAITING FOR OPTIONS CONFIRMATION"
    elif (J.ge(J.get(G_Math, "abs")(optionsScore), MINIMUM_OPTIONS) and J.lt(J.get(G_Math, "abs")(currentTechnicalScore), 20)):
        status = "WAITING FOR TECHNICAL CONFIRMATION"
    def _f41(strikeValue=J.undefined, *_args):
        return J.get(G_Number, "isFinite")(strikeValue)
    def _f42(firstStrike=J.undefined, secondStrike=J.undefined, *_args):
        return J.sub(firstStrike, secondStrike)
    availableOptionStrikes = J.get(J.get(J.get(J.get(G_Object, "keys")(gammaByStrike), "map")(G_Number), "filter")(_f41), "sort")(_f42)
    recommendedBuyStrike = nearestOptionStrike(currentPrice)
    recommendedTargetStrike = nearestOptionStrike((tradeTargetOne if (tradeTargetOne is not None) else currentPrice))
    emaCompression = J.div(J.get(G_Math, "abs")(J.sub(J.get(fastEMA, lastIndex), J.get(slowEMA, lastIndex))), currentATR)
    elevatedIV = (J.ge(gammaAtmIV, 0.55) if J.truthy(_t43 := (gammaAtmIV is not None)) else _t43)
    positiveGammaEnvironment = (_t44 if J.truthy(_t44 := J.seq(gammaRegime, "POSITIVE GAMMA")) else J.seq(gammaRegime, "PIN RISK"))
    moderateConviction = J.lt(signalStrength, 70)
    compressedTrend = J.lt(emaCompression, 0.75)
    nearbyDirectionalWall = (J.le(J.get(G_Math, "abs")(J.sub(gammaCallWall, currentPrice)), J.mul(currentATR, 1.5)) if (J.truthy(executeBuy) and (gammaCallWall is not None)) else (J.le(J.get(G_Math, "abs")(J.sub(currentPrice, gammaPutWall)), J.mul(currentATR, 1.5)) if (J.truthy(executeSell) and (gammaPutWall is not None)) else False))
    preferDebitSpread = (_t45 if J.truthy(_t45 := (_t46 if J.truthy(_t46 := (_t47 if J.truthy(_t47 := (_t48 if J.truthy(_t48 := (_t49 if J.truthy(_t49 := forceDebitSpread) else positiveGammaEnvironment)) else elevatedIV)) else moderateConviction)) else compressedTrend)) else nearbyDirectionalWall)
    optionPlay = "\ud83d\uded1 NO OPTION PLAY"
    optionContract = "WAIT FOR SIGNAL"
    optionExpiration = "N/A"
    optionTrigger = "WAIT"
    optionTargetText = "N/A"
    optionStopText = "N/A"
    optionEnvironment = "MIXED / NO EDGE"
    optionReason = status
    optionStatus = "⏳ WAIT"
    optionColor = "#90A4AE"
    if (J.truthy(executeBuy) or J.truthy(executeSell)):
        bullishOptionPlay = executeBuy
        optionSide = ("CALL" if J.truthy(bullishOptionPlay) else "PUT")
        optionExpiration = (J.template(gammaExpirationDTE, " DTE") if ((gammaExpirationDTE is not None) and J.ge(gammaExpirationDTE, 14)) else "21-45 DTE")
        optionTrigger = J.add(J.template(("ABOVE" if J.truthy(bullishOptionPlay) else "BELOW"), " "), J.template(priceText(tradeEntry)))
        optionTargetText = J.template(priceText(tradeTargetOne), " ", tradeTargetOneName)
        optionStopText = J.add(J.template(("BELOW" if J.truthy(bullishOptionPlay) else "ABOVE"), " "), J.template(priceText(tradeStop)))
        optionColor = ("#00E676" if J.truthy(bullishOptionPlay) else "#FF5252")
        if J.truthy(preferDebitSpread):
            optionPlay = ("\ud83d\udee1️ CALL DEBIT SPREAD" if J.truthy(bullishOptionPlay) else "\ud83d\udee1️ PUT DEBIT SPREAD")
            optionContract = (J.add(J.template("BUY $", recommendedBuyStrike, optionSide, " / "), J.template("SELL $", recommendedTargetStrike, optionSide)) if ((recommendedBuyStrike is not None) and (recommendedTargetStrike is not None)) else J.template(optionSide, " DEBIT SPREAD"))
            if J.truthy(positiveGammaEnvironment):
                optionEnvironment = "\ud83e\uddf2 CHOP / SUPPRESSION"
                optionReason = "POSITIVE GAMMA FAVORS SPREAD"
            elif J.truthy(elevatedIV):
                optionEnvironment = "\ud83d\udee1️ ELEVATED IV"
                optionReason = "SPREAD REDUCES IV COST"
            elif J.truthy(nearbyDirectionalWall):
                optionEnvironment = "\ud83e\uddf1 WALL CAPS MOVE"
                optionReason = "SELL LEG NEAR GAMMA TARGET"
            else:
                optionEnvironment = "〰️ MODERATE MOMENTUM"
                optionReason = "CHOP FILTER PREFERS SPREAD"
            optionStatus = ("✅ BULLISH SPREAD CONFIRMED" if J.truthy(bullishOptionPlay) else "✅ BEARISH SPREAD CONFIRMED")
        else:
            optionPlay = ("⚡ LONG CALL" if J.truthy(bullishOptionPlay) else "⚡ LONG PUT")
            optionContract = (J.template("$", recommendedBuyStrike, " ", optionSide) if (recommendedBuyStrike is not None) else J.template("ATM ", optionSide))
            optionEnvironment = "⚡ NEGATIVE GAMMA EXPANSION"
            optionReason = "STRONG TREND + FLOW + GAMMA"
            optionStatus = ("\ud83d\udc02 LONG CALL CONFIRMED" if J.truthy(bullishOptionPlay) else "\ud83d\udc3b LONG PUT CONFIRMED")
    gammaLinesEnabled = (gammaDataAvailable if J.truthy(_t50 := showGammaLines) else _t50)
    paintGammaLevel(gammaCallWall, gammaLinesEnabled, "BEAST Call Wall", "BEAST Call Wall Extension", J.template("CALL WALL ", priceText(gammaCallWall)), callLineColor, 0, 2)
    paintGammaLevel(gammaPutWall, gammaLinesEnabled, "BEAST Put Wall", "BEAST Put Wall Extension", J.template("PUT WALL ", priceText(gammaPutWall)), putLineColor, 2, 2)
    paintGammaLevel(gammaMagnet, gammaLinesEnabled, "BEAST Magnet", "BEAST Magnet Extension", J.template("\ud83e\uddf2 MAGNET ", priceText(gammaMagnet)), "#AA00FF", 4, 2)
    paintGammaLevel(gammaFlip, gammaLinesEnabled, "BEAST Gamma Flip", "BEAST Gamma Flip Extension", J.template("GAMMA FLIP ", priceText(gammaFlip)), "#FF9100", 6, 2)
    paintGammaLevel(expectedMoveUpper, gammaLinesEnabled, "BEAST EM High", "BEAST EM High Extension", J.template("EM HIGH ", priceText(expectedMoveUpper)), "#00B8D4", 8, 1)
    paintGammaLevel(expectedMoveLower, gammaLinesEnabled, "BEAST EM Low", "BEAST EM Low Extension", J.template("EM LOW ", priceText(expectedMoveLower)), "#00B8D4", 10, 1)
    activeTrade = (_t51 if J.truthy(_t51 := executeBuy) else executeSell)
    paintGammaLevel(tradeEntry, activeTrade, "BEAST Trade Entry", "BEAST Trade Entry Extension", J.template(("\ud83d\udc02 BUY" if J.truthy(executeBuy) else "\ud83d\udc3b SELL"), " ENTRY ", priceText(tradeEntry)), "#FFFFFF", 0, 2)
    paintGammaLevel(tradeStop, activeTrade, "BEAST Trade Stop", "BEAST Trade Stop Extension", J.template("STOP ", priceText(tradeStop)), "#FF1744", 2, 2)
    paintGammaLevel(tradeTargetOne, activeTrade, "BEAST Target One", "BEAST Target One Extension", J.template("T1 ", priceText(tradeTargetOne), " ", tradeTargetOneName), "#FFD600", 4, 2)
    paintGammaLevel(tradeTargetTwo, ((tradeTargetTwo is not None) if J.truthy(_t52 := activeTrade) else _t52), "BEAST Target Two", "BEAST Target Two Extension", J.template("T2 ", priceText(tradeTargetTwo), " ", tradeTargetTwoName), "#CE93D8", 6, 2)
    dashboardRows = J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", "\ud83d\udd25 Neal or No Deal \ud83d\udc02\ud83d\udc3b"), ("colspan", 2), ("color", "#FFFFFF"), ("background", "linear-gradient(90deg,#00796B,#4527A0)"), ("padding", "7px"), ("fontSize", "11px"), ("fontWeight", "bold"), ("textAlign", "center"))]))), J.obj(("cells", J.JSArray([J.obj(("text", J.template(decisionIcon, " ", recommendation)), ("colspan", 2), ("color", "#FFFFFF"), ("background", decisionColor), ("padding", "9px"), ("fontSize", "15px"), ("fontWeight", "bold"), ("textAlign", "center"))]))), J.obj(("cells", J.JSArray([labelCell("ACTION"), valueCell(action, decisionColor)]))), J.obj(("cells", J.JSArray([labelCell("SIGNAL STRENGTH"), valueCell(J.template(signalStrength, "/100"), ("#FFD600" if J.ge(signalStrength, EXECUTION_THRESHOLD) else "#CFD8DC"))]))), J.obj(("cells", J.JSArray([labelCell("TECHNICAL"), valueCell(J.template(biasName(currentTechnicalScore), " ", signedNumber(currentTechnicalScore)), biasColor(currentTechnicalScore))]))), J.obj(("cells", J.JSArray([labelCell("OPTIONS FLOW"), valueCell(J.template(biasName(optionsScore), " ", signedNumber(optionsScore)), biasColor(optionsScore))]))), J.obj(("cells", J.JSArray([labelCell("EST. GAMMA"), valueCell((J.template(biasName(gammaDirectionalScore), " ", signedNumber(gammaDirectionalScore)) if J.truthy(gammaDataAvailable) else "UNAVAILABLE"), (biasColor(gammaDirectionalScore) if J.truthy(gammaDataAvailable) else "#90A4AE"))]))), J.obj(("cells", J.JSArray([labelCell("GAMMA REGIME"), valueCell(gammaRegime, gammaRegimeColor)]))), J.obj(("cells", J.JSArray([labelCell("PREMIUM BIAS"), valueCell(premiumRatioText, ("#69F0AE" if J.ge(callPremium, putPremium) else "#FF5252"))]))), J.obj(("cells", J.JSArray([labelCell("CALL / PUT"), valueCell(J.template(compactMoney(callPremium), " / ", compactMoney(putPremium)))]))), J.obj(("cells", J.JSArray([labelCell("MAIN FLOW"), valueCell(dominantStrikeText, ("#69F0AE" if J.seq(dominantStrikeType, "CALL") else ("#FF5252" if J.seq(dominantStrikeType, "PUT") else "#CFD8DC")))]))), J.obj(("cells", J.JSArray([labelCell("CALL / PUT WALL"), valueCell((J.template(priceText(gammaCallWall), " / ", priceText(gammaPutWall)) if J.truthy(gammaDataAvailable) else "N/A"))]))), J.obj(("cells", J.JSArray([labelCell("\ud83e\uddf2 MAGNET / FLIP"), valueCell((J.template(priceText(gammaMagnet), " / ", priceText(gammaFlip)) if J.truthy(gammaDataAvailable) else "N/A"), "#CE93D8")]))), J.obj(("cells", J.JSArray([labelCell("EXPECTED MOVE"), valueCell((J.add(J.template("±", priceText(expectedMove), " | "), J.template(gammaExpirationDTE, "d")) if (expectedMove is not None) else "N/A"), "#80DEEA")]))), J.obj(("cells", J.JSArray([labelCell("FLOW ACTIVITY"), valueCell(J.add(J.template(acceptedTrades, " trades | "), J.template(sweepCount, " sweeps")))]))), J.obj(("cells", J.JSArray([J.obj(("text", status), ("colspan", 2), ("color", ("#FFD600" if (J.truthy(dataConflict) or J.truthy(gammaConflict)) else "#FFFFFF")), ("background", "#0A1116"), ("border", "solid #37474F 1px"), ("padding", "5px 8px"), ("fontSize", "10px"), ("fontWeight", "bold"), ("textAlign", "center"), ("whiteSpace", "nowrap"))]))), J.obj(("cells", J.JSArray([J.obj(("text", "\ud83c\udfaf BEAST OPTIONS PLAN"), ("colspan", 2), ("color", "#FFFFFF"), ("background", "linear-gradient(90deg,#6A1B9A,#1565C0)"), ("border", "solid #5C6BC0 1px"), ("padding", "7px 8px"), ("fontSize", "12px"), ("fontWeight", "bold"), ("textAlign", "center"))]))), J.obj(("cells", J.JSArray([J.obj(("text", optionPlay), ("colspan", 2), ("color", "#FFFFFF"), ("background", (optionColor if (J.truthy(executeBuy) or J.truthy(executeSell)) else "#263238")), ("border", "solid #455A64 1px"), ("padding", "8px"), ("fontSize", "14px"), ("fontWeight", "bold"), ("textAlign", "center"))]))), J.obj(("cells", J.JSArray([labelCell("CONTRACT"), valueCell(optionContract, optionColor)]))), J.obj(("cells", J.JSArray([labelCell("EXPIRATION"), valueCell(optionExpiration, "#80DEEA")]))), J.obj(("cells", J.JSArray([labelCell("TRIGGER"), valueCell(optionTrigger, "#FFFFFF")]))), J.obj(("cells", J.JSArray([labelCell("\ud83c\udfaf TARGET"), valueCell(optionTargetText, "#FFD600")]))), J.obj(("cells", J.JSArray([labelCell("\ud83d\uded1 INVALIDATION"), valueCell(optionStopText, "#FF8A80")]))), J.obj(("cells", J.JSArray([labelCell("R:R TO TARGET"), valueCell((J.template(J.get(tradeTargetOneRR, "toFixed")(2), "R") if (tradeTargetOneRR is not None) else "N/A"), ("#69F0AE" if ((tradeTargetOneRR is not None) and J.ge(tradeTargetOneRR, 2)) else "#FFD600"))]))), J.obj(("cells", J.JSArray([labelCell("ENVIRONMENT"), valueCell(optionEnvironment, "#CE93D8")]))), J.obj(("cells", J.JSArray([labelCell("WHY THIS PLAY"), valueCell(optionReason, "#CFD8DC")]))), J.obj(("cells", J.JSArray([J.obj(("text", optionStatus), ("colspan", 2), ("color", ("#FFFFFF" if (J.truthy(executeBuy) or J.truthy(executeSell)) else "#FFD600")), ("background", "#0A1116"), ("border", "solid #455A64 1px"), ("padding", "6px 8px"), ("fontSize", "10px"), ("fontWeight", "bold"), ("textAlign", "center"), ("whiteSpace", "nowrap"))])))])
    dashboardDefinition = J.obj(("width", "340px"), ("borderCollapse", "collapse"), ("background", "#101820"), ("border", "solid #455A64 1px"), ("borderRadius", "10px"), ("boxShadow", "0 5px 18px rgba(0,0,0,0.65)"), ("overflow", "hidden"), ("rows", dashboardRows))
    dashboardPosition = dashPosition
    dashboardOffsetX = 15
    dashboardOffsetY = 15
    if ((J.seq(dashPosition, "top_right") or J.seq(dashPosition, "center_right")) or J.seq(dashPosition, "bottom_right")):
        dashboardOffsetX = (-155)
    if (J.seq(dashPosition, "center_left") or J.seq(dashPosition, "center_right")):
        dashboardOffsetY = 0
    if (J.seq(dashPosition, "bottom_left") or J.seq(dashPosition, "bottom_right")):
        dashboardOffsetY = (-15)
    G_paint_overlay("NEAL BEAST V3 DASHBOARD", J.obj(("position", dashboardPosition), ("parent", "chart"), ("order", "above_all"), ("offset_x", dashboardOffsetX), ("offset_y", dashboardOffsetY)), dashboardDefinition)
    buySignal = G_series_of(False)
    sellSignal = G_series_of(False)
    J.set(buySignal, lastIndex, executeBuy)
    J.set(sellSignal, lastIndex, executeSell)
    def _f53(signal=J.undefined, *_args):
        return ("\ud83d\udc02 BEAST BUY" if J.truthy(signal) else None)
    G_paint(J.get(buySignal, "map")(_f53), J.obj(("name", "BEAST V3 LIVE BUY TAG"), ("style", "labels_below"), ("color", "#00E676")))
    def _f54(signal=J.undefined, *_args):
        return ("\ud83d\udc3b BEAST SELL" if J.truthy(signal) else None)
    G_paint(J.get(sellSignal, "map")(_f54), J.obj(("name", "BEAST V3 LIVE SELL TAG"), ("style", "labels_above"), ("color", "#FF1744")))
    G_register_signal(buySignal, "BEAST V3 LIVE BUY")
    G_register_signal(sellSignal, "BEAST V3 LIVE SELL")


register_store_indicator(
    script,
    name='neal_or_no_deal_TS',
    title='Neal or No Deal',
    developer='Baba Neal',
    url='https://trendspider.com/trading-tools-store/indicators/6a98f8-neal-or-no-deal-%f0%9f%90%82%f0%9f%90%bb/',
    position='price',
    inputs=[{'id': 'dash_position', 'title': 'Dash Position', 'type': 'select_wide', 'default': 'top_right', 'options': ['top_left', 'top_right', 'center_left', 'center_right', 'bottom_left', 'bottom_right']}, {'id': 'show_gamma_lines', 'title': 'Show Gamma Lines', 'type': 'boolean', 'default': True}, {'id': 'call_line', 'title': 'Call Line', 'type': 'color', 'default': '#00E676'}, {'id': 'put_line', 'title': 'Put Line', 'type': 'color', 'default': '#FF1744'}],
    outputs=['beast_call_wall', 'beast_put_wall', 'beast_magnet', 'beast_gamma_flip', 'beast_em_high', 'beast_em_low', 'beast_trade_entry', 'beast_trade_stop', 'beast_target_one', 'beast_target_two', 'beast_v3_live_buy_tag', 'beast_v3_live_sell_tag', 'beast_v3_live_buy', 'beast_v3_live_sell'],
    signals=['beast_v3_live_buy', 'beast_v3_live_sell'],
    requires=['options_schedule', 'unusual_options'],
    parity='exact',
)
