"""
Pattern Analysis Overlay -- TrendSpider store indicator by Grant Pratt.

Registered as "pattern_analysis_overlay_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68aba5-pattern-analysis-overlay/)
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
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_high = G["high"]
    G_input = G["input"]
    G_low = G["low"]
    G_paint = G["paint"]
    G_paint_overlay = G["paint_overlay"]
    G_series_of = G["series_of"]
    G_describe_indicator("Pattern Analysis Overlay")
    myFontSize = J.get(G_input, "number")("Font Size", 12, J.obj(("min", 8), ("max", 30)))
    showTrendlines = J.get(G_input, "boolean")("Show Trendlines", True)
    showTargets = J.get(G_input, "boolean")("Show Price Targets", True)
    showLevels = J.get(G_input, "boolean")("Show Pattern Levels", True)
    patternSensitivity = J.get(G_input, "number")("Pattern Sensitivity", 0.6, J.obj(("min", 0.1), ("max", 1)))
    PATTERN_STATS = J.obj(("Ascending Triangle", J.obj(("avg", 8.2), ("success", 72), ("duration", 21), ("direction", "↗"), ("color", "#4CAF50"))), ("Descending Triangle", J.obj(("avg", (-6.8)), ("success", 68), ("duration", 18), ("direction", "↘"), ("color", "#F44336"))), ("Symmetrical Triangle", J.obj(("avg", 5.4), ("success", 64), ("duration", 25), ("direction", "↕"), ("color", "#FF9800"))), ("Head & Shoulders", J.obj(("avg", (-9.2)), ("success", 78), ("duration", 35), ("direction", "↘"), ("color", "#9C27B0"))), ("Inverse H&S", J.obj(("avg", 11.4), ("success", 74), ("duration", 32), ("direction", "↗"), ("color", "#2196F3"))), ("Double Top", J.obj(("avg", (-7.6)), ("success", 71), ("duration", 28), ("direction", "↘"), ("color", "#E91E63"))), ("Double Bottom", J.obj(("avg", 9.8), ("success", 69), ("duration", 26), ("direction", "↗"), ("color", "#00BCD4"))), ("Rising Channel", J.obj(("avg", 6.3), ("success", 58), ("duration", 42), ("direction", "↗"), ("color", "#4CAF50"))), ("Falling Channel", J.obj(("avg", (-4.9)), ("success", 56), ("duration", 38), ("direction", "↘"), ("color", "#F44336"))), ("Horizontal Channel", J.obj(("avg", 1.8), ("success", 52), ("duration", 35), ("direction", "→"), ("color", "#9E9E9E"))), ("Rising Wedge", J.obj(("avg", (-5.2)), ("success", 63), ("duration", 22), ("direction", "↘"), ("color", "#FF5722"))), ("Falling Wedge", J.obj(("avg", 7.8), ("success", 67), ("duration", 24), ("direction", "↗"), ("color", "#00BCD4"))), ("Broadening Ascending", J.obj(("avg", 4.1), ("success", 55), ("duration", 40), ("direction", "↗"), ("color", "#FF9800"))), ("Broadening Descending", J.obj(("avg", (-3.8)), ("success", 53), ("duration", 38), ("direction", "↘"), ("color", "#FF5722"))), ("Broadening Symmetrical", J.obj(("avg", 2.3), ("success", 48), ("duration", 45), ("direction", "↕"), ("color", "#9C27B0"))), ("Uptrend", J.obj(("avg", 12.5), ("success", 65), ("duration", 60), ("direction", "↗"), ("color", "#4CAF50"))), ("Downtrend", J.obj(("avg", (-8.7)), ("success", 62), ("duration", 45), ("direction", "↘"), ("color", "#F44336"))), ("Sideways", J.obj(("avg", 2.1), ("success", 45), ("duration", 30), ("direction", "→"), ("color", "#9E9E9E"))))
    STAGE_DESCRIPTIONS = J.obj(("Ascending Triangle", J.JSArray(["Formation", "Testing Resistance", "Breakout Prep", "Initial Breakout", "Breakout Retest", "Confirmed Breakout"])), ("Descending Triangle", J.JSArray(["Formation", "Testing Support", "Breakdown Prep", "Initial Breakdown", "Breakdown Retest", "Confirmed Breakdown"])), ("Symmetrical Triangle", J.JSArray(["Formation", "Convergence", "Apex Approach", "Initial Breakout", "Breakout Retest", "Confirmed Breakout"])), ("Head & Shoulders", J.JSArray(["Left Shoulder", "Head Formation", "Right Shoulder", "Initial Breakdown", "Breakdown Retest", "Confirmed Breakdown"])), ("Inverse H&S", J.JSArray(["Left Shoulder", "Head Formation", "Right Shoulder", "Initial Breakout", "Breakout Retest", "Confirmed Breakout"])), ("Double Top", J.JSArray(["First Peak", "Retest Peak", "Neckline Test", "Initial Breakdown", "Breakdown Retest", "Confirmed Breakdown"])), ("Double Bottom", J.JSArray(["First Trough", "Retest Trough", "Neckline Test", "Initial Breakout", "Breakout Retest", "Confirmed Breakout"])), ("Rising Channel", J.JSArray(["Formation", "Trend Development", "Maturity", "Initial Breakout", "Breakout Retest", "Confirmed Breakout"])), ("Falling Channel", J.JSArray(["Formation", "Trend Development", "Maturity", "Initial Breakdown", "Breakdown Retest", "Confirmed Breakdown"])), ("Horizontal Channel", J.JSArray(["Formation", "Range Development", "Consolidation", "Initial Breakout", "Breakout Retest", "Confirmed Breakout"])), ("Rising Wedge", J.JSArray(["Formation", "Convergence", "Apex Approach", "Initial Breakdown", "Breakdown Retest", "Confirmed Breakdown"])), ("Falling Wedge", J.JSArray(["Formation", "Convergence", "Apex Approach", "Initial Breakout", "Breakout Retest", "Confirmed Breakout"])), ("Broadening Ascending", J.JSArray(["Formation", "Expansion", "Volatility Peak", "Initial Resolution", "Resolution Retest", "Confirmed Resolution"])), ("Broadening Descending", J.JSArray(["Formation", "Expansion", "Volatility Peak", "Initial Resolution", "Resolution Retest", "Confirmed Resolution"])), ("Broadening Symmetrical", J.JSArray(["Formation", "Expansion", "Volatility Peak", "Initial Resolution", "Resolution Retest", "Confirmed Resolution"])), ("Uptrend", J.JSArray(["Early Stage", "Building Momentum", "Acceleration", "Strong Trend", "Powerful Trend", "Confirmed Breakout"])), ("Downtrend", J.JSArray(["Early Stage", "Building Momentum", "Acceleration", "Strong Decline", "Powerful Decline", "Confirmed Breakdown"])), ("Sideways", J.JSArray(["Range Formation", "Consolidation", "Coiling", "Breakout Prep", "Testing Boundaries", "Range Bound"])))
    BG = "#1e1e1e"
    STRIPE1 = "#2a2a2a"
    STRIPE2 = "#333333"
    HEADER_BG = "#0d47a1"
    swingLength = 10
    lookbackBars = 50
    swingHighs = G_series_of(None)
    swingLows = G_series_of(None)
    i = swingLength
    while J.lt(i, J.sub(J.get(G_close, "length"), swingLength)):
        isSwingHigh = True
        isSwingLow = True
        j = J.sub(i, swingLength)
        while J.le(j, J.add(i, swingLength)):
            if J.seq(j, i):
                j = J.inc(j)
                continue
            if J.ge(J.get(G_high, j), J.get(G_high, i)):
                isSwingHigh = False
            if J.le(J.get(G_low, j), J.get(G_low, i)):
                isSwingLow = False
            j = J.inc(j)
        if J.truthy(isSwingHigh):
            J.set(swingHighs, i, J.get(G_high, i))
        if J.truthy(isSwingLow):
            J.set(swingLows, i, J.get(G_low, i))
        i = J.inc(i)
    high1Index = (-1)
    high1Price = 0
    high2Index = (-1)
    high2Price = 0
    high3Index = (-1)
    high3Price = 0
    low1Index = (-1)
    low1Price = 0
    low2Index = (-1)
    low2Price = 0
    low3Index = (-1)
    low3Price = 0
    highCount = 0
    lowCount = 0
    i_2 = J.get(G_Math, "max")(0, J.sub(J.get(G_close, "length"), lookbackBars))
    while J.lt(i_2, J.get(G_close, "length")):
        if (J.get(swingHighs, i_2) is not None):
            high3Index = high2Index
            high3Price = high2Price
            high2Index = high1Index
            high2Price = high1Price
            high1Index = i_2
            high1Price = J.get(swingHighs, i_2)
            highCount = J.inc(highCount)
        if (J.get(swingLows, i_2) is not None):
            low3Index = low2Index
            low3Price = low2Price
            low2Index = low1Index
            low2Price = low1Price
            low1Index = i_2
            low1Price = J.get(swingLows, i_2)
            lowCount = J.inc(lowCount)
        i_2 = J.inc(i_2)
    detectedPattern = ""
    patternStrength = 0
    currentStage = 1
    completionPrice = 0
    targetPrice = 0
    stopLoss = 0
    failureTarget = 0
    breakoutPrice = 0
    breakdownPrice = 0
    daysInPattern = 0
    holdAboveLevel = 0
    nextTarget = 0
    if J.lt(J.get(G_close, "length"), 20):
        detectedPattern = "Insufficient Data"
        patternStrength = 0
    elif (J.ge(highCount, 2) and J.ge(lowCount, 2)):
        highSlope = (J.div(J.sub(high1Price, high2Price), J.sub(high1Index, high2Index)) if J.gt(high1Index, high2Index) else 0)
        lowSlope = (J.div(J.sub(low1Price, low2Price), J.sub(low1Index, low2Index)) if J.gt(low1Index, low2Index) else 0)
        currentPrice_2 = J.get(G_close, J.sub(J.get(G_close, "length"), 1))
        patternStartIndex = J.get(G_Math, "min")(high2Index, low2Index)
        daysInPattern = J.sub(J.sub(J.get(G_close, "length"), 1), patternStartIndex)
        if ((J.seq(detectedPattern, "") and J.ge(highCount, 2)) and J.ge(lowCount, 2)):
            slopeSum = J.add(highSlope, lowSlope)
            convergenceStrength = J.add(J.get(G_Math, "abs")(highSlope), J.get(G_Math, "abs")(lowSlope))
            if (((J.lt(highSlope, (-0.0003)) and J.gt(lowSlope, 0.0003)) and J.lt(J.get(G_Math, "abs")(slopeSum), J.mul(convergenceStrength, 0.6))) and J.gt(convergenceStrength, 0.001)):
                detectedPattern = "Symmetrical Triangle"
                patternStrength = J.get(G_Math, "min")(J.mul(convergenceStrength, 600), 1)
                upperBound = J.add(high2Price, J.mul(highSlope, J.sub(J.sub(J.get(G_close, "length"), 1), high2Index)))
                lowerBound = J.add(low2Price, J.mul(lowSlope, J.sub(J.sub(J.get(G_close, "length"), 1), low2Index)))
                if J.gt(currentPrice_2, J.mul(upperBound, 1.05)):
                    currentStage = 6
                    holdAboveLevel = upperBound
                    nextTarget = J.mul(currentPrice_2, 1.15)
                elif J.gt(currentPrice_2, J.mul(upperBound, 1.02)):
                    currentStage = 5
                    holdAboveLevel = upperBound
                elif J.gt(currentPrice_2, upperBound):
                    currentStage = 4
                    holdAboveLevel = upperBound
                elif J.lt(currentPrice_2, J.mul(lowerBound, 0.95)):
                    currentStage = 6
                elif J.lt(currentPrice_2, J.mul(lowerBound, 0.98)):
                    currentStage = 5
                elif J.lt(currentPrice_2, lowerBound):
                    currentStage = 4
                else:
                    convergencePoint = J.div(J.sub(high2Price, low2Price), J.add(J.get(G_Math, "abs")(highSlope), J.get(G_Math, "abs")(lowSlope)))
                    timeToConvergence = J.sub(convergencePoint, J.sub(J.sub(J.get(G_close, "length"), 1), J.get(G_Math, "max")(high2Index, low2Index)))
                    if J.gt(timeToConvergence, 10):
                        currentStage = 1
                    elif J.gt(timeToConvergence, 5):
                        currentStage = 2
                    else:
                        currentStage = 3
            elif (J.lt(highSlope, (-0.0003)) and J.lt(J.get(G_Math, "abs")(lowSlope), 0.0003)):
                detectedPattern = "Descending Triangle"
                patternStrength = J.mul(J.get(G_Math, "abs")(highSlope), 1000)
                currentStage = (2 if J.gt(J.get(G_Math, "abs")(highSlope), 0.01) else 3)
            elif (J.lt(J.get(G_Math, "abs")(highSlope), 0.0003) and J.gt(lowSlope, 0.0003)):
                detectedPattern = "Ascending Triangle"
                patternStrength = J.mul(J.get(G_Math, "abs")(lowSlope), 1000)
                currentStage = (2 if J.gt(J.get(G_Math, "abs")(lowSlope), 0.01) else 3)
        if ((J.seq(detectedPattern, "") and J.lt(J.get(G_Math, "abs")(J.sub(highSlope, lowSlope)), 0.0005)) and J.gt(J.get(G_Math, "abs")(highSlope), 0.001)):
            if (J.gt(highSlope, 0.001) and J.gt(lowSlope, 0.001)):
                detectedPattern = "Rising Channel"
                patternStrength = J.mul(J.add(highSlope, lowSlope), 500)
            elif (J.lt(highSlope, (-0.001)) and J.lt(lowSlope, (-0.001))):
                detectedPattern = "Falling Channel"
                patternStrength = J.mul(J.get(G_Math, "abs")(J.add(highSlope, lowSlope)), 500)
        if ((((J.seq(detectedPattern, "") and J.lt(J.get(G_Math, "abs")(highSlope), 0.0005)) and J.lt(J.get(G_Math, "abs")(lowSlope), 0.0005)) and J.ge(highCount, 2)) and J.ge(lowCount, 2)):
            range = J.get(G_Math, "abs")(J.sub(high1Price, low1Price))
            if J.gt(J.div(range, currentPrice_2), 0.02):
                detectedPattern = "Horizontal Channel"
                patternStrength = 0.7
                currentStage = 2
        if ((J.seq(detectedPattern, "") and J.gt(J.get(G_Math, "abs")(highSlope), 0.001)) and J.gt(J.get(G_Math, "abs")(lowSlope), 0.001)):
            convergenceRate = J.get(G_Math, "abs")(J.add(highSlope, lowSlope))
            if J.gt(convergenceRate, 0.002):
                if ((J.gt(highSlope, 0.001) and J.gt(lowSlope, 0.001)) and J.gt(highSlope, lowSlope)):
                    detectedPattern = "Rising Wedge"
                    patternStrength = J.mul(convergenceRate, 400)
                    currentStage = (2 if J.gt(highSlope, 0.01) else 3)
                elif ((J.lt(highSlope, (-0.001)) and J.lt(lowSlope, (-0.001))) and J.gt(J.get(G_Math, "abs")(lowSlope), J.get(G_Math, "abs")(highSlope))):
                    detectedPattern = "Falling Wedge"
                    patternStrength = J.mul(convergenceRate, 400)
                    currentStage = (2 if J.gt(J.get(G_Math, "abs")(lowSlope), 0.01) else 3)
        if ((J.seq(detectedPattern, "") and J.gt(J.get(G_Math, "abs")(highSlope), 0.001)) and J.gt(J.get(G_Math, "abs")(lowSlope), 0.001)):
            divergenceRate = J.get(G_Math, "abs")(J.sub(highSlope, lowSlope))
            if J.gt(divergenceRate, 0.003):
                if (J.gt(highSlope, 0.001) and J.lt(lowSlope, (-0.001))):
                    detectedPattern = "Broadening Ascending"
                    patternStrength = J.mul(divergenceRate, 300)
                    currentStage = 2
                elif (J.lt(highSlope, (-0.001)) and J.gt(lowSlope, 0.001)):
                    if J.gt(divergenceRate, 0.01):
                        detectedPattern = "Broadening Descending"
                        patternStrength = J.mul(divergenceRate, 300)
                        currentStage = 2
                elif ((J.gt(highSlope, 0.001) and J.gt(lowSlope, 0.001)) or (J.lt(highSlope, (-0.001)) and J.lt(lowSlope, (-0.001)))):
                    if J.gt(divergenceRate, J.get(G_Math, "abs")(J.div(J.add(highSlope, lowSlope), 2))):
                        detectedPattern = "Broadening Symmetrical"
                        patternStrength = J.mul(divergenceRate, 300)
                        currentStage = 2
        if (((J.seq(detectedPattern, "") and J.ge(highCount, 2)) and J.ge(high2Index, 0)) and J.ge(high1Index, 0)):
            priceDiff = J.get(G_Math, "abs")(J.sub(high1Price, high2Price))
            avgPrice = J.div(J.add(high1Price, high2Price), 2)
            timeDiff = J.sub(high1Index, high2Index)
            if (J.lt(J.div(priceDiff, avgPrice), 0.05) and J.gt(timeDiff, 5)):
                detectedPattern = "Double Top"
                patternStrength = 0.8
                valleyLow = J.get(G_Math, "min")(low1Price, low2Price)
                if J.lt(currentPrice_2, valleyLow):
                    currentStage = 4
                elif J.lt(currentPrice_2, J.mul(avgPrice, 0.97)):
                    currentStage = 3
                else:
                    currentStage = 2
        if (((J.seq(detectedPattern, "") and J.ge(lowCount, 2)) and J.ge(low2Index, 0)) and J.ge(low1Index, 0)):
            priceDiff_2 = J.get(G_Math, "abs")(J.sub(low1Price, low2Price))
            avgPrice_2 = J.div(J.add(low1Price, low2Price), 2)
            timeDiff_2 = J.sub(low1Index, low2Index)
            if (J.lt(J.div(priceDiff_2, avgPrice_2), 0.05) and J.gt(timeDiff_2, 5)):
                detectedPattern = "Double Bottom"
                patternStrength = 0.8
                peakHigh = J.get(G_Math, "max")(high1Price, high2Price)
                if J.gt(currentPrice_2, J.mul(peakHigh, 1.02)):
                    currentStage = 6
                elif J.gt(currentPrice_2, peakHigh):
                    currentStage = 4
                elif J.gt(currentPrice_2, J.mul(avgPrice_2, 1.03)):
                    currentStage = 3
                else:
                    currentStage = 2
        if (((J.ge(highCount, 3) and J.ge(high3Index, 0)) and J.ge(high2Index, 0)) and J.ge(high1Index, 0)):
            leftShoulder = high3Price
            head = high2Price
            rightShoulder = high1Price
            if (J.gt(head, leftShoulder) and J.gt(head, rightShoulder)):
                shoulderDiff = J.get(G_Math, "abs")(J.sub(leftShoulder, rightShoulder))
                shoulderAvg = J.div(J.add(leftShoulder, rightShoulder), 2)
                headHeight = J.sub(head, shoulderAvg)
                if (J.lt(J.div(shoulderDiff, shoulderAvg), 0.1) and J.gt(J.div(headHeight, shoulderAvg), 0.05)):
                    detectedPattern = "Head & Shoulders"
                    patternStrength = J.div(headHeight, head)
                    currentStage = 3
        if (((J.ge(lowCount, 3) and J.ge(low3Index, 0)) and J.ge(low2Index, 0)) and J.ge(low1Index, 0)):
            leftShoulder_2 = low3Price
            head_2 = low2Price
            rightShoulder_2 = low1Price
            if (J.lt(head_2, leftShoulder_2) and J.lt(head_2, rightShoulder_2)):
                shoulderDiff_2 = J.get(G_Math, "abs")(J.sub(leftShoulder_2, rightShoulder_2))
                shoulderAvg_2 = J.div(J.add(leftShoulder_2, rightShoulder_2), 2)
                headDepth = J.sub(shoulderAvg_2, head_2)
                if (J.lt(J.div(shoulderDiff_2, shoulderAvg_2), 0.1) and J.gt(J.div(headDepth, shoulderAvg_2), 0.05)):
                    detectedPattern = "Inverse H&S"
                    patternStrength = J.div(headDepth, shoulderAvg_2)
                    currentStage = 3
    if (J.seq(detectedPattern, "") and J.ge(J.get(G_close, "length"), 20)):
        currentClose = J.get(G_close, J.sub(J.get(G_close, "length"), 1))
        past20 = J.get(G_close, J.sub(J.get(G_close, "length"), 20))
        past10 = J.get(G_close, J.sub(J.get(G_close, "length"), 10))
        change20 = J.div(J.sub(currentClose, past20), past20)
        change10 = J.div(J.sub(currentClose, past10), past10)
        if J.gt(change20, 0.05):
            detectedPattern = "Uptrend"
            patternStrength = J.get(G_Math, "min")(J.mul(change20, 5), 1)
            if J.gt(change20, 0.2):
                currentStage = 6
            elif J.gt(change20, 0.15):
                currentStage = 5
            elif J.gt(change20, 0.1):
                currentStage = 4
            elif J.gt(change20, 0.08):
                currentStage = 3
            elif J.gt(change20, 0.06):
                currentStage = 2
            else:
                currentStage = 1
        elif J.lt(change20, (-0.05)):
            detectedPattern = "Downtrend"
            patternStrength = J.get(G_Math, "min")(J.mul(J.get(G_Math, "abs")(change20), 5), 1)
            if J.gt(J.get(G_Math, "abs")(change20), 0.2):
                currentStage = 6
            elif J.gt(J.get(G_Math, "abs")(change20), 0.15):
                currentStage = 5
            elif J.gt(J.get(G_Math, "abs")(change20), 0.1):
                currentStage = 4
            elif J.gt(J.get(G_Math, "abs")(change20), 0.08):
                currentStage = 3
            elif J.gt(J.get(G_Math, "abs")(change20), 0.06):
                currentStage = 2
            else:
                currentStage = 1
        else:
            detectedPattern = "Sideways"
            patternStrength = 0.6
            currentStage = 2
            recentHigh = 0
            recentLow = 999999
            i_3 = J.get(G_Math, "max")(0, J.sub(J.get(G_close, "length"), 20))
            while J.lt(i_3, J.get(G_close, "length")):
                if J.gt(J.get(G_close, i_3), recentHigh):
                    recentHigh = J.get(G_close, i_3)
                if J.lt(J.get(G_close, i_3), recentLow):
                    recentLow = J.get(G_close, i_3)
                i_3 = J.inc(i_3)
            breakoutPrice = recentHigh
            breakdownPrice = recentLow
            completionPrice = recentHigh
            stopLoss = recentLow
            failureTarget = J.div(J.add(recentHigh, recentLow), 2)
            daysInPattern = 20
    currentPrice = (J.get(G_close, J.sub(J.get(G_close, "length"), 1)) if J.gt(J.get(G_close, "length"), 0) else 0)
    if ((J.gt(currentPrice, 0) and J.sne(detectedPattern, "")) and J.truthy(J.get(PATTERN_STATS, detectedPattern))):
        stats = J.get(PATTERN_STATS, detectedPattern)
        targetPrice = J.mul(currentPrice, J.add(1, J.div(J.get(stats, "avg"), 100)))
        if J.seq(detectedPattern, "Ascending Triangle"):
            resistanceLevel = (J.get(G_Math, "max")(high1Price, high2Price) if J.ge(highCount, 2) else high1Price)
            supportLevel = (low1Price if J.ge(lowCount, 1) else J.mul(currentPrice, 0.95))
            breakoutPrice = resistanceLevel
            breakdownPrice = supportLevel
            completionPrice = resistanceLevel
            stopLoss = supportLevel
            failureTarget = J.mul(supportLevel, 0.95)
            if J.gt(currentPrice, J.mul(resistanceLevel, 1.1)):
                currentStage = 6
            elif J.gt(currentPrice, J.mul(resistanceLevel, 1.02)):
                currentStage = 5
            elif J.gt(currentPrice, resistanceLevel):
                currentStage = 4
            elif J.lt(currentPrice, supportLevel):
                currentStage = 4
                completionPrice = breakdownPrice
        elif J.seq(detectedPattern, "Descending Triangle"):
            completionPrice = (J.get(G_Math, "min")(low1Price, low2Price) if J.ge(lowCount, 2) else low1Price)
            stopLoss = (high1Price if J.ge(highCount, 1) else J.mul(currentPrice, 1.05))
            if J.lt(currentPrice, J.mul(completionPrice, 0.9)):
                currentStage = 6
            elif J.lt(currentPrice, J.mul(completionPrice, 0.98)):
                currentStage = 5
            elif J.lt(currentPrice, completionPrice):
                currentStage = 4
        elif J.seq(detectedPattern, "Symmetrical Triangle"):
            resistanceLevel_2 = (J.get(G_Math, "max")(high1Price, high2Price) if J.ge(highCount, 2) else high1Price)
            supportLevel_2 = (J.get(G_Math, "min")(low1Price, low2Price) if J.ge(lowCount, 2) else low1Price)
            breakoutPrice = resistanceLevel_2
            breakdownPrice = supportLevel_2
            completionPrice = (resistanceLevel_2 if J.gt(currentPrice, J.div(J.add(resistanceLevel_2, supportLevel_2), 2)) else supportLevel_2)
            stopLoss = (supportLevel_2 if J.gt(currentPrice, J.div(J.add(resistanceLevel_2, supportLevel_2), 2)) else resistanceLevel_2)
            if J.gt(currentPrice, J.div(J.add(resistanceLevel_2, supportLevel_2), 2)):
                failureTarget = J.mul(supportLevel_2, 0.95)
            else:
                failureTarget = J.mul(resistanceLevel_2, 1.05)
            if (J.gt(currentPrice, J.mul(resistanceLevel_2, 1.1)) or J.lt(currentPrice, J.mul(supportLevel_2, 0.9))):
                currentStage = 6
            elif (J.gt(currentPrice, J.mul(resistanceLevel_2, 1.02)) or J.lt(currentPrice, J.mul(supportLevel_2, 0.98))):
                currentStage = 5
            elif (J.gt(currentPrice, resistanceLevel_2) or J.lt(currentPrice, supportLevel_2)):
                currentStage = 4
        elif J.seq(detectedPattern, "Double Top"):
            leftPeakIndex = high2Index
            rightPeakIndex = high1Index
            valleyLow_2 = currentPrice
            i_4 = J.add(leftPeakIndex, 1)
            while J.lt(i_4, rightPeakIndex):
                if J.lt(J.get(G_low, i_4), valleyLow_2):
                    valleyLow_2 = J.get(G_low, i_4)
                i_4 = J.inc(i_4)
            neckline = valleyLow_2
            completionPrice = neckline
            targetPrice = J.mul(neckline, J.add(1, J.div(J.get(J.get(PATTERN_STATS, detectedPattern), "avg"), 100)))
            nextTarget = J.mul(targetPrice, 0.85)
            stopLoss = J.get(G_Math, "max")(high1Price, high2Price)
            failureTarget = J.mul(J.get(G_Math, "max")(high1Price, high2Price), 1.02)
            if J.lt(currentPrice, J.mul(neckline, 0.9)):
                currentStage = 6
            elif J.lt(currentPrice, J.mul(neckline, 0.98)):
                currentStage = 5
            elif J.lt(currentPrice, neckline):
                currentStage = 4
        elif J.seq(detectedPattern, "Double Bottom"):
            neckline_2 = (J.get(G_Math, "max")(high1Price, high2Price) if J.ge(highCount, 2) else J.mul(currentPrice, 1.05))
            completionPrice = neckline_2
            stopLoss = J.get(G_Math, "min")(low1Price, low2Price)
            if J.gt(currentPrice, J.mul(neckline_2, 2)):
                currentStage = 6
            elif J.gt(currentPrice, J.mul(neckline_2, 1.5)):
                currentStage = 5
            elif J.gt(currentPrice, J.mul(neckline_2, 1.1)):
                currentStage = 4
        elif J.seq(detectedPattern, "Head & Shoulders"):
            neckline_3 = (J.get(G_Math, "min")(low1Price, low3Price) if J.ge(lowCount, 2) else J.mul(currentPrice, 0.95))
            completionPrice = neckline_3
            stopLoss = high2Price
            if J.lt(currentPrice, J.mul(neckline_3, 0.9)):
                currentStage = 6
            elif J.lt(currentPrice, J.mul(neckline_3, 0.95)):
                currentStage = 5
            elif J.lt(currentPrice, neckline_3):
                currentStage = 4
        elif J.seq(detectedPattern, "Inverse H&S"):
            neckline_4 = (J.get(G_Math, "max")(high1Price, high3Price) if J.ge(highCount, 2) else J.mul(currentPrice, 1.05))
            completionPrice = neckline_4
            stopLoss = low2Price
            if J.gt(currentPrice, J.mul(neckline_4, 1.15)):
                currentStage = 6
            elif J.gt(currentPrice, J.mul(neckline_4, 1.05)):
                currentStage = 5
            elif J.gt(currentPrice, neckline_4):
                currentStage = 4
        elif J.seq(detectedPattern, "Uptrend"):
            completionPrice = J.mul(currentPrice, 1.05)
            stopLoss = (low1Price if J.ge(lowCount, 1) else J.mul(currentPrice, 0.95))
        elif J.seq(detectedPattern, "Downtrend"):
            completionPrice = J.mul(currentPrice, 0.95)
            stopLoss = (high1Price if J.ge(highCount, 1) else J.mul(currentPrice, 1.05))
        elif J.seq(detectedPattern, "Rising Channel"):
            completionPrice = J.mul(currentPrice, 1.03)
            stopLoss = low1Price
        elif J.seq(detectedPattern, "Falling Channel"):
            completionPrice = J.mul(currentPrice, 0.97)
            stopLoss = high1Price
        elif J.seq(detectedPattern, "Horizontal Channel"):
            midPoint = J.div(J.add(high1Price, low1Price), 2)
            completionPrice = (J.mul(high1Price, 1.01) if J.gt(currentPrice, midPoint) else J.mul(low1Price, 0.99))
            stopLoss = (low1Price if J.gt(currentPrice, midPoint) else high1Price)
        elif J.seq(detectedPattern, "Rising Wedge"):
            completionPrice = low1Price
            stopLoss = J.get(G_Math, "max")(high1Price, high2Price)
        elif J.seq(detectedPattern, "Falling Wedge"):
            completionPrice = high1Price
            stopLoss = J.get(G_Math, "min")(low1Price, low2Price)
        elif J.seq(detectedPattern, "Broadening Ascending"):
            completionPrice = J.mul(high1Price, 1.02)
            stopLoss = low1Price
        elif J.seq(detectedPattern, "Broadening Descending"):
            completionPrice = J.mul(low1Price, 0.98)
            stopLoss = high1Price
        elif J.seq(detectedPattern, "Broadening Symmetrical"):
            range_2 = J.get(G_Math, "abs")(J.sub(high1Price, low1Price))
            completionPrice = J.add(currentPrice, J.mul(range_2, 0.5))
            stopLoss = J.sub(currentPrice, J.mul(range_2, 0.3))
    rows = J.JSArray([])
    J.get(rows, "push")(J.obj(("cells", J.JSArray([J.obj(("colspan", 2), ("text", J.add(J.add("\ud83d\udcca ", J.get(G_constants, "ticker")), " Pattern Analysis")), ("fontWeight", "bold"), ("color", "#FFD700"), ("textAlign", "center"), ("padding", "10px 15px"), ("fontSize", J.add(myFontSize, 2)), ("background", BG), ("border", "1px solid #FFD700"))]))))
    if (J.sne(detectedPattern, "") and (((J.ge(patternStrength, patternSensitivity) or J.seq(detectedPattern, "Uptrend")) or J.seq(detectedPattern, "Downtrend")) or J.seq(detectedPattern, "Sideways"))):
        stats_2 = J.get(PATTERN_STATS, detectedPattern)
        confidence = J.get(G_Math, "round")(J.mul(patternStrength, 100))
        stages = (_t1 if J.truthy(_t1 := J.get(STAGE_DESCRIPTIONS, detectedPattern)) else J.JSArray(["Stage 1", "Stage 2", "Stage 3", "Stage 4"]))
        stageDesc = J.get(stages, J.get(G_Math, "min")(J.sub(currentStage, 1), J.sub(J.get(stages, "length"), 1)))
        J.get(rows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", "Pattern:"), ("fontWeight", "bold"), ("padding", "6px 12px"), ("color", "lightgray"), ("background", HEADER_BG)), J.obj(("text", J.add(J.add(J.add(J.add(J.add(J.get(stats_2, "direction"), " "), detectedPattern), " ("), confidence), "%)")), ("padding", "6px 12px"), ("color", J.get(stats_2, "color")), ("fontWeight", "bold"), ("background", STRIPE1))]))))
        J.get(rows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", "Stage:"), ("fontWeight", "bold"), ("padding", "6px 12px"), ("color", "lightgray"), ("background", HEADER_BG)), J.obj(("text", J.add(J.add(currentStage, "/6 - "), stageDesc)), ("padding", "6px 12px"), ("color", "#E0E0E0"), ("background", STRIPE2))]))))
        J.get(rows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", "Avg Return:"), ("fontWeight", "bold"), ("padding", "6px 12px"), ("color", "lightgray"), ("background", HEADER_BG)), J.obj(("text", J.add(J.add(("+" if J.gt(J.get(stats_2, "avg"), 0) else ""), J.get(stats_2, "avg")), "%")), ("padding", "6px 12px"), ("color", ("#4CAF50" if J.gt(J.get(stats_2, "avg"), 0) else "#F44336")), ("fontWeight", "bold"), ("background", STRIPE1))]))))
        J.get(rows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", "Success Rate:"), ("fontWeight", "bold"), ("padding", "6px 12px"), ("color", "lightgray"), ("background", HEADER_BG)), J.obj(("text", J.add(J.get(stats_2, "success"), "%")), ("padding", "6px 12px"), ("color", ("#4CAF50" if J.gt(J.get(stats_2, "success"), 65) else ("#FF9800" if J.gt(J.get(stats_2, "success"), 50) else "#F44336"))), ("background", STRIPE2))]))))
        if (J.truthy(showTargets) and J.gt(targetPrice, 0)):
            targetReturn = J.mul(J.div(J.sub(targetPrice, currentPrice), currentPrice), 100)
            J.get(rows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", "Price Target:"), ("fontWeight", "bold"), ("padding", "6px 12px"), ("color", "lightgray"), ("background", HEADER_BG)), J.obj(("text", J.add(J.add(J.add(J.add(J.add("$", J.get(targetPrice, "toFixed")(2)), " ("), ("+" if J.gt(targetReturn, 0) else "")), J.get(targetReturn, "toFixed")(1)), "%)")), ("padding", "6px 12px"), ("color", ("#4CAF50" if J.gt(targetReturn, 0) else "#F44336")), ("fontWeight", "bold"), ("background", STRIPE1))]))))
        if (J.ge(currentStage, 4) and J.gt(holdAboveLevel, 0)):
            J.get(rows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", "Hold Above:"), ("fontWeight", "bold"), ("padding", "6px 12px"), ("color", "lightgray"), ("background", HEADER_BG)), J.obj(("text", J.add(J.add("$", J.get(holdAboveLevel, "toFixed")(2)), " (Support)")), ("padding", "6px 12px"), ("color", "#4CAF50"), ("background", STRIPE2))]))))
        elif J.gt(completionPrice, 0):
            direction = ("above" if J.gt(completionPrice, currentPrice) else "below")
            J.get(rows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", "Completion:"), ("fontWeight", "bold"), ("padding", "6px 12px"), ("color", "lightgray"), ("background", HEADER_BG)), J.obj(("text", J.add(J.add(J.add("Break ", direction), " $"), J.get(completionPrice, "toFixed")(2))), ("padding", "6px 12px"), ("color", "#00BCD4"), ("background", STRIPE2))]))))
        if (J.gt(nextTarget, 0) and J.lt(J.div(J.get(G_Math, "abs")(J.sub(currentPrice, targetPrice)), targetPrice), 0.02)):
            nextReturn = J.mul(J.div(J.sub(nextTarget, currentPrice), currentPrice), 100)
            J.get(rows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", "Next Target:"), ("fontWeight", "bold"), ("padding", "6px 12px"), ("color", "lightgray"), ("background", HEADER_BG)), J.obj(("text", J.add(J.add(J.add(J.add(J.add("$", J.get(nextTarget, "toFixed")(2)), " ("), ("+" if J.gt(nextReturn, 0) else "")), J.get(nextReturn, "toFixed")(1)), "%)")), ("padding", "6px 12px"), ("color", "#9C27B0"), ("background", STRIPE1))]))))
        if J.gt(stopLoss, 0):
            riskPercent = J.get(G_Math, "abs")(J.mul(J.div(J.sub(stopLoss, currentPrice), currentPrice), 100))
            J.get(rows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", "Risk Level:"), ("fontWeight", "bold"), ("padding", "6px 12px"), ("color", "lightgray"), ("background", HEADER_BG)), J.obj(("text", J.add(J.add(J.add(J.add("$", J.get(stopLoss, "toFixed")(2)), " (-"), J.get(riskPercent, "toFixed")(1)), "%)")), ("padding", "6px 12px"), ("color", "#FF5722"), ("background", STRIPE1))]))))
        if J.gt(daysInPattern, 0):
            J.get(rows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", "Days in Pattern:"), ("fontWeight", "bold"), ("padding", "6px 12px"), ("color", "lightgray"), ("background", HEADER_BG)), J.obj(("text", J.add(daysInPattern, " days")), ("padding", "6px 12px"), ("color", "#9E9E9E"), ("background", STRIPE2))]))))
        if ((((J.seq(detectedPattern, "Symmetrical Triangle") or J.seq(detectedPattern, "Sideways")) or J.seq(detectedPattern, "Horizontal Channel")) and J.gt(breakoutPrice, 0)) and J.gt(breakdownPrice, 0)):
            upPercent = J.mul(J.div(J.sub(breakoutPrice, currentPrice), currentPrice), 100)
            downPercent = J.mul(J.div(J.sub(breakdownPrice, currentPrice), currentPrice), 100)
            J.get(rows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", "Breakout Target:"), ("fontWeight", "bold"), ("padding", "6px 12px"), ("color", "lightgray"), ("background", HEADER_BG)), J.obj(("text", J.add(J.add(J.add(J.add(J.add("$", J.get(breakoutPrice, "toFixed")(2)), " ("), ("+" if J.gt(upPercent, 0) else "")), J.get(upPercent, "toFixed")(1)), "%)")), ("padding", "6px 12px"), ("color", "#4CAF50"), ("background", STRIPE1))]))))
            J.get(rows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", "Breakdown Target:"), ("fontWeight", "bold"), ("padding", "6px 12px"), ("color", "lightgray"), ("background", HEADER_BG)), J.obj(("text", J.add(J.add(J.add(J.add("$", J.get(breakdownPrice, "toFixed")(2)), " ("), J.get(downPercent, "toFixed")(1)), "%)")), ("padding", "6px 12px"), ("color", "#F44336"), ("background", STRIPE2))]))))
        if (J.gt(failureTarget, 0) and J.sne(failureTarget, currentPrice)):
            failPercent = J.mul(J.div(J.sub(failureTarget, currentPrice), currentPrice), 100)
            J.get(rows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", "Pattern Failure:"), ("fontWeight", "bold"), ("padding", "6px 12px"), ("color", "lightgray"), ("background", HEADER_BG)), J.obj(("text", J.add(J.add(J.add(J.add(J.add("$", J.get(failureTarget, "toFixed")(2)), " ("), ("+" if J.gt(failPercent, 0) else "")), J.get(failPercent, "toFixed")(1)), "%)")), ("padding", "6px 12px"), ("color", "#FF9800"), ("background", STRIPE1))]))))
    else:
        J.get(rows, "push")(J.obj(("cells", J.JSArray([J.obj(("colspan", 2), ("text", "\ud83d\udd0d No clear pattern detected - Increase sensitivity or wait for pattern development"), ("color", "#9E9E9E"), ("textAlign", "center"), ("padding", "10px 15px"), ("background", STRIPE2))]))))
    G_paint_overlay("Pattern Analysis", J.obj(("position", "top_right"), ("order", "above_all")), J.obj(("fontSize", myFontSize), ("background", BG), ("border", "2px solid #FFD700"), ("borderRadius", "8px"), ("rows", rows)))
    if J.truthy(showTrendlines):
        trendlineTop = G_series_of(None)
        trendlineBottom = G_series_of(None)
        if ((J.ge(highCount, 2) and J.ge(high2Index, 0)) and J.ge(high1Index, 0)):
            slope = J.div(J.sub(high1Price, high2Price), J.sub(high1Index, high2Index))
            i_5 = high2Index
            while J.lt(i_5, J.get(G_close, "length")):
                J.set(trendlineTop, i_5, J.add(high2Price, J.mul(slope, J.sub(i_5, high2Index))))
                i_5 = J.inc(i_5)
        if ((J.ge(lowCount, 2) and J.ge(low2Index, 0)) and J.ge(low1Index, 0)):
            slope_2 = J.div(J.sub(low1Price, low2Price), J.sub(low1Index, low2Index))
            i_6 = low2Index
            while J.lt(i_6, J.get(G_close, "length")):
                J.set(trendlineBottom, i_6, J.add(low2Price, J.mul(slope_2, J.sub(i_6, low2Index))))
                i_6 = J.inc(i_6)
        G_paint(trendlineTop, "Resistance Line", "#F44336")
        G_paint(trendlineBottom, "Support Line", "#4CAF50")
        G_paint(swingHighs, "Swing Highs", "#FF5722")
        G_paint(swingLows, "Swing Lows", "#00BCD4")
    completionLine = G_series_of(None)
    holdAboveLine = G_series_of(None)
    targetLine = G_series_of(None)
    nextTargetLine = G_series_of(None)
    failureLine = G_series_of(None)
    breakoutLine = G_series_of(None)
    breakdownLine = G_series_of(None)
    riskLine = G_series_of(None)
    if ((J.truthy(showLevels) and J.sne(detectedPattern, "")) and (((J.ge(patternStrength, patternSensitivity) or J.seq(detectedPattern, "Uptrend")) or J.seq(detectedPattern, "Downtrend")) or J.seq(detectedPattern, "Sideways"))):
        currentIndex = J.sub(J.get(G_close, "length"), 1)
        if (J.gt(completionPrice, 0) and J.lt(currentStage, 4)):
            i_7 = J.get(G_Math, "max")(0, J.sub(currentIndex, 5))
            while J.lt(i_7, J.get(G_close, "length")):
                J.set(completionLine, i_7, completionPrice)
                i_7 = J.inc(i_7)
        if (J.gt(holdAboveLevel, 0) and J.ge(currentStage, 4)):
            i_8 = J.get(G_Math, "max")(0, J.sub(currentIndex, 5))
            while J.lt(i_8, J.get(G_close, "length")):
                J.set(holdAboveLine, i_8, holdAboveLevel)
                i_8 = J.inc(i_8)
        if (J.truthy(showTargets) and J.gt(targetPrice, 0)):
            i_9 = J.get(G_Math, "max")(0, J.sub(currentIndex, 5))
            while J.lt(i_9, J.get(G_close, "length")):
                J.set(targetLine, i_9, targetPrice)
                i_9 = J.inc(i_9)
        if (J.truthy(showTargets) and J.gt(nextTarget, 0)):
            i_10 = J.get(G_Math, "max")(0, J.sub(currentIndex, 5))
            while J.lt(i_10, J.get(G_close, "length")):
                J.set(nextTargetLine, i_10, nextTarget)
                i_10 = J.inc(i_10)
        if J.gt(failureTarget, 0):
            i_11 = J.get(G_Math, "max")(0, J.sub(currentIndex, 5))
            while J.lt(i_11, J.get(G_close, "length")):
                J.set(failureLine, i_11, failureTarget)
                i_11 = J.inc(i_11)
        if J.gt(stopLoss, 0):
            i_12 = J.get(G_Math, "max")(0, J.sub(currentIndex, 5))
            while J.lt(i_12, J.get(G_close, "length")):
                J.set(riskLine, i_12, stopLoss)
                i_12 = J.inc(i_12)
        if (((J.truthy(showTargets) and ((J.seq(detectedPattern, "Symmetrical Triangle") or J.seq(detectedPattern, "Sideways")) or J.seq(detectedPattern, "Horizontal Channel"))) and J.gt(breakoutPrice, 0)) and J.gt(breakdownPrice, 0)):
            i_13 = J.get(G_Math, "max")(0, J.sub(currentIndex, 5))
            while J.lt(i_13, J.get(G_close, "length")):
                J.set(breakoutLine, i_13, breakoutPrice)
                J.set(breakdownLine, i_13, breakdownPrice)
                i_13 = J.inc(i_13)
    G_paint(completionLine, "Completion Level", "#00BCD4")
    G_paint(holdAboveLine, "Hold Above (Support)", "#4CAF50")
    G_paint(targetLine, "Price Target", "#FF9800")
    G_paint(nextTargetLine, "Next Target", "#9C27B0")
    G_paint(failureLine, "Pattern Failure", "#FF5722")
    G_paint(riskLine, "Risk Level (Stop)", "#E91E63")
    G_paint(breakoutLine, "Breakout Target", "#66BB6A")
    G_paint(breakdownLine, "Breakdown Target", "#EF5350")


register_store_indicator(
    script,
    name='pattern_analysis_overlay_TS',
    title='Pattern Analysis Overlay',
    developer='Grant Pratt',
    url='https://trendspider.com/trading-tools-store/indicators/68aba5-pattern-analysis-overlay/',
    position='price',
    inputs=[{'id': 'font_size', 'title': 'Font Size', 'type': 'number', 'default': 12}, {'id': 'show_trendlines', 'title': 'Show Trendlines', 'type': 'boolean', 'default': True}, {'id': 'show_price_targets', 'title': 'Show Price Targets', 'type': 'boolean', 'default': True}, {'id': 'show_pattern_levels', 'title': 'Show Pattern Levels', 'type': 'boolean', 'default': True}, {'id': 'pattern_sensitivity', 'title': 'Pattern Sensitivity', 'type': 'number', 'default': 0.6}],
    outputs=['resistance_line', 'support_line', 'swing_highs', 'swing_lows', 'completion_level', 'hold_above__support_', 'price_target', 'next_target', 'pattern_failure', 'risk_level__stop_', 'breakout_target', 'breakdown_target'],
    signals=[],
    requires=[],
    parity='exact',
)
