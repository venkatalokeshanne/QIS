"""
Inversion Fair Value Gaps (IFVG) -- TrendSpider store indicator by John Wolff.

Registered as "inversion_fair_value_gaps_ifvg_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/689d40-inversion-fair-value-gaps-ifvg/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_atr = G["atr"]
    G_close = G["close"]
    G_console = G["console"]
    G_describe_indicator = G["describe_indicator"]
    G_fill = G["fill"]
    G_high = G["high"]
    G_input = G["input"]
    G_low = G["low"]
    G_open = G["open"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_series_of = G["series_of"]
    def validateFVG(fvg=J.undefined, *_args):
        return (J.lt(J.get(G_Math, "abs")(J.sub(J.get(fvg, "mid0"), J.div(J.add(J.get(fvg, "top0"), J.get(fvg, "bot0")), 2))), 0.0001) if J.truthy(_t1 := (J.gt(J.get(fvg, "top0"), J.get(fvg, "bot0")) if J.truthy(_t2 := (J.seq(J.typeof(J.get(fvg, "bot0")), "number") if J.truthy(_t3 := (J.seq(J.typeof(J.get(fvg, "top0")), "number") if J.truthy(_t4 := (J.ge(J.get(fvg, "left"), 0) if J.truthy(_t5 := (J.seq(J.typeof(J.get(fvg, "left")), "number") if J.truthy(_t6 := fvg) else _t6)) else _t5)) else _t4)) else _t3)) else _t2)) else _t1)
    def isSessionGap(currentBar=J.undefined, prevBar=J.undefined, *_args):
        if (not J.truthy(filterSessionGaps)):
            return False
        gapThreshold = J.div(sessionGapThreshold, 100)
        prevClose = J.get(G_close, prevBar)
        currentOpen = J.get(G_open, currentBar)
        if ((J.nullish(prevClose)) or (J.nullish(currentOpen))):
            return False
        gapSize = J.div(J.get(G_Math, "abs")(J.sub(currentOpen, prevClose)), prevClose)
        return J.gt(gapSize, gapThreshold)
    G_describe_indicator("Inversion Fair Value Gaps (IFVG)", "price", J.obj(("shortName", "IFVG")))
    disp_num = J.get(G_input, "number")("Show Last", 5, J.obj(("min", 1), ("max", 100)))
    useWickRetest = J.get(G_input, "boolean")("Use Wick for Signals", False)
    atr_multi = J.get(G_input, "number")("ATR Multiplier", 0.25, J.obj(("min", 0), ("max", 10), ("step", 0.25)))
    proj_len = J.get(G_input, "number")("Projection Bars", 50, J.obj(("min", 0), ("max", 200)))
    showSeeds = J.get(G_input, "boolean")("Show Pre-Inversion Seeds?", False)
    showInversionDots = J.get(G_input, "boolean")("Show Inversion Points?", True)
    extendZones = J.get(G_input, "boolean")("Extend Active Zones?", True)
    showMidlines = J.get(G_input, "boolean")("Show Zone Midlines?", True)
    colorByLocation = J.get(G_input, "boolean")("Color Zones by Location (Above Price = Red, Below = Green)?", False)
    filterSessionGaps = J.get(G_input, "boolean")("Filter Session Gaps?", True)
    sessionGapThreshold = J.get(G_input, "number")("Session Gap Threshold %", 0.1, J.obj(("min", 0), ("max", 5), ("step", 0.1)))
    green = "#08998150"
    red = "#f2364550"
    midCol = "#787b86"
    if (((((not J.truthy(G_high)) or (not J.truthy(G_low))) or (not J.truthy(G_open))) or (not J.truthy(G_close))) or J.lt(J.get(G_close, "length"), 3)):
        J.get(G_console, "error")("Insufficient price data - need at least 3 bars")
    def _f1(__=J.undefined, i=J.undefined, *_args):
        if ((J.nullish(J.get(G_open, i))) or (J.nullish(J.get(G_close, i)))):
            return None
        return J.get(G_Math, "max")(J.get(G_open, i), J.get(G_close, i))
    c_top = J.get(G_high, "map")(_f1)
    def _f2(__=J.undefined, i=J.undefined, *_args):
        if ((J.nullish(J.get(G_open, i))) or (J.nullish(J.get(G_close, i)))):
            return None
        return J.get(G_Math, "min")(J.get(G_open, i), J.get(G_close, i))
    c_bot = J.get(G_low, "map")(_f2)
    atr200 = G_atr(200)
    minWidth = G_series_of(None)
    cumulativeRange = 0
    i = 0
    while J.lt(i, J.get(G_close, "length")):
        if (((not J.nullish(J.get(G_high, i))) and (not J.nullish(J.get(G_low, i)))) and J.ge(J.get(G_high, i), J.get(G_low, i))):
            cumulativeRange = J.add(cumulativeRange, J.sub(J.get(G_high, i), J.get(G_low, i)))
        atrValue = (J.get(atr200, i) if (((J.get(atr200, i) is not None) and (J.get(atr200, i) is not J.undefined)) and J.gt(J.get(atr200, i), 0)) else J.div(cumulativeRange, J.add(i, 1)))
        J.set(minWidth, i, J.get(G_Math, "max")(0, J.mul(atrValue, atr_multi)))
        i = J.inc(i)
    BUFFER = 100
    bulls = J.JSArray([])
    bears = J.JSArray([])
    bullInv = J.JSArray([])
    bearInv = J.JSArray([])
    bullRet = G_series_of(False)
    bearRet = G_series_of(False)
    inversionDots = G_series_of(None)
    seedTop = G_series_of(None)
    seedBot = G_series_of(None)
    maxZones = J.get(G_Math, "min")(J.mul(disp_num, 2), 15)
    preTopSeries = J.JSArray([])
    preBotSeries = J.JSArray([])
    postTopSeries = J.JSArray([])
    postBotSeries = J.JSArray([])
    midSeries = J.JSArray([])
    k = 0
    while J.lt(k, maxZones):
        J.set(preTopSeries, k, G_series_of(None))
        J.set(preBotSeries, k, G_series_of(None))
        J.set(postTopSeries, k, G_series_of(None))
        J.set(postBotSeries, k, G_series_of(None))
        J.set(midSeries, k, G_series_of(None))
        k = J.inc(k)
    debugCounters = J.obj(("bullFVGsDetected", 0), ("bearFVGsDetected", 0), ("bullInversions", 0), ("bearInversions", 0), ("bullSignals", 0), ("bearSignals", 0), ("zonesInvalidated", 0), ("sessionGapsFiltered", 0))
    dataLength = J.get(G_close, "length")
    i_2 = 2
    while J.lt(i_2, dataLength):
        if (((((((((((((J.nullish(J.get(G_high, i_2))) or (J.nullish(J.get(G_low, i_2)))) or (J.nullish(J.get(G_close, i_2)))) or (J.nullish(J.get(G_open, i_2)))) or (J.nullish(J.get(G_high, J.sub(i_2, 1))))) or (J.nullish(J.get(G_low, J.sub(i_2, 1))))) or (J.nullish(J.get(G_close, J.sub(i_2, 1))))) or (J.nullish(J.get(G_high, J.sub(i_2, 2))))) or (J.nullish(J.get(G_low, J.sub(i_2, 2))))) or (J.nullish(J.get(G_close, J.sub(i_2, 2))))) or J.lt(J.get(G_high, i_2), J.get(G_low, i_2))) or J.lt(J.get(G_high, J.sub(i_2, 1)), J.get(G_low, J.sub(i_2, 1)))) or J.lt(J.get(G_high, J.sub(i_2, 2)), J.get(G_low, J.sub(i_2, 2)))):
            i_2 = J.inc(i_2)
            continue
        try:
            if (J.truthy(isSessionGap(i_2, J.sub(i_2, 1))) or J.truthy(isSessionGap(J.sub(i_2, 1), J.sub(i_2, 2)))):
                J.update_member(debugCounters, "sessionGapsFiltered", J.inc, True)
                i_2 = J.inc(i_2)
                continue
            bullFVG = (J.gt(J.get(G_close, J.sub(i_2, 1)), J.get(G_high, J.sub(i_2, 2))) if J.truthy(_t3 := J.gt(J.get(G_low, i_2), J.get(G_high, J.sub(i_2, 2)))) else _t3)
            bearFVG = (J.lt(J.get(G_close, J.sub(i_2, 1)), J.get(G_low, J.sub(i_2, 2))) if J.truthy(_t4 := J.lt(J.get(G_high, i_2), J.get(G_low, J.sub(i_2, 2)))) else _t4)
            bullGapWidth = (J.get(G_Math, "abs")(J.sub(J.get(G_low, i_2), J.get(G_high, J.sub(i_2, 2)))) if J.truthy(bullFVG) else 0)
            bearGapWidth = (J.get(G_Math, "abs")(J.sub(J.get(G_low, J.sub(i_2, 2)), J.get(G_high, i_2))) if J.truthy(bearFVG) else 0)
            currentMinWidth = (_t5 if J.truthy(_t5 := J.get(minWidth, i_2)) else 0)
            validBullFVG = (J.gt(bullGapWidth, currentMinWidth) if J.truthy(_t6 := bullFVG) else _t6)
            validBearFVG = (J.gt(bearGapWidth, currentMinWidth) if J.truthy(_t7 := bearFVG) else _t7)
            if J.truthy(showSeeds):
                if J.truthy(validBullFVG):
                    J.set(seedTop, i_2, J.get(G_low, i_2))
                    J.set(seedBot, i_2, J.get(G_high, J.sub(i_2, 2)))
                if J.truthy(validBearFVG):
                    J.set(seedTop, i_2, J.get(G_low, J.sub(i_2, 2)))
                    J.set(seedBot, i_2, J.get(G_high, i_2))
            if J.truthy(validBullFVG):
                newFVG = J.obj(("left", J.sub(i_2, 1)), ("top0", J.get(G_low, i_2)), ("bot0", J.get(G_high, J.sub(i_2, 2))), ("mid0", J.div(J.add(J.get(G_low, i_2), J.get(G_high, J.sub(i_2, 2))), 2)), ("dir", 1), ("state", 0), ("signaled", False), ("alive", False), ("endIndex", None), ("xIndex", None))
                if J.truthy(validateFVG(newFVG)):
                    J.get(bulls, "push")(newFVG)
                    J.update_member(debugCounters, "bullFVGsDetected", J.inc, True)
            if J.truthy(validBearFVG):
                newFVG_2 = J.obj(("left", J.sub(i_2, 1)), ("top0", J.get(G_low, J.sub(i_2, 2))), ("bot0", J.get(G_high, i_2)), ("mid0", J.div(J.add(J.get(G_low, J.sub(i_2, 2)), J.get(G_high, i_2)), 2)), ("dir", (-1)), ("state", 0), ("signaled", False), ("alive", False), ("endIndex", None), ("xIndex", None))
                if J.truthy(validateFVG(newFVG_2)):
                    J.get(bears, "push")(newFVG_2)
                    J.update_member(debugCounters, "bearFVGsDetected", J.inc, True)
            currentCBot = J.get(c_bot, i_2)
            currentCTop = J.get(c_top, i_2)
            j = J.sub(J.get(bulls, "length"), 1)
            while J.ge(j, 0):
                fvg = J.get(bulls, j)
                if (J.seq(J.get(fvg, "dir"), 1) and J.lt(currentCBot, J.get(fvg, "bot0"))):
                    J.set(fvg, "xIndex", i_2)
                    J.get(bullInv, "push")(J.get(J.get(bulls, "splice")(j, 1), 0))
                    J.update_member(debugCounters, "bullInversions", J.inc, True)
                    J.set(inversionDots, i_2, J.get(fvg, "mid0"))
                j = J.dec(j)
            j_2 = J.sub(J.get(bears, "length"), 1)
            while J.ge(j_2, 0):
                fvg_2 = J.get(bears, j_2)
                if (J.seq(J.get(fvg_2, "dir"), (-1)) and J.gt(currentCTop, J.get(fvg_2, "top0"))):
                    J.set(fvg_2, "xIndex", i_2)
                    J.get(bearInv, "push")(J.get(J.get(bears, "splice")(j_2, 1), 0))
                    J.update_member(debugCounters, "bearInversions", J.inc, True)
                    J.set(inversionDots, i_2, J.get(fvg_2, "mid0"))
                j_2 = J.dec(j_2)
            for fvg_3 in J.iter_of(bullInv):
                if J.seq(J.get(fvg_3, "state"), 0):
                    J.set(fvg_3, "state", 1)
                    J.set(fvg_3, "dir", (-1))
                    J.set(fvg_3, "alive", True)
                    J.set(fvg_3, "endIndex", None)
                if J.ge(J.get(fvg_3, "state"), 1):
                    pass
            for fvg_4 in J.iter_of(bearInv):
                if J.seq(J.get(fvg_4, "state"), 0):
                    J.set(fvg_4, "state", 1)
                    J.set(fvg_4, "dir", 1)
                    J.set(fvg_4, "alive", True)
                    J.set(fvg_4, "endIndex", None)
                if J.ge(J.get(fvg_4, "state"), 1):
                    pass
            if J.gt(i_2, 0):
                for fvg_5 in J.iter_of(bullInv):
                    if ((J.seq(J.get(fvg_5, "dir"), (-1)) and J.seq(J.get(fvg_5, "state"), 1)) and (not J.truthy(J.get(fvg_5, "signaled")))):
                        currentClose = J.get(G_close, i_2)
                        prevPrice = (J.get(G_high, J.sub(i_2, 1)) if J.truthy(useWickRetest) else J.get(G_close, J.sub(i_2, 1)))
                        if ((J.lt(currentClose, J.get(fvg_5, "bot0")) and J.ge(prevPrice, J.get(fvg_5, "bot0"))) and J.lt(prevPrice, J.get(fvg_5, "top0"))):
                            J.set(bearRet, i_2, True)
                            J.set(fvg_5, "signaled", True)
                            J.update_member(debugCounters, "bearSignals", J.inc, True)
                for fvg_6 in J.iter_of(bearInv):
                    if ((J.seq(J.get(fvg_6, "dir"), 1) and J.seq(J.get(fvg_6, "state"), 1)) and (not J.truthy(J.get(fvg_6, "signaled")))):
                        currentClose_2 = J.get(G_close, i_2)
                        prevPrice_2 = (J.get(G_low, J.sub(i_2, 1)) if J.truthy(useWickRetest) else J.get(G_close, J.sub(i_2, 1)))
                        if ((J.gt(currentClose_2, J.get(fvg_6, "top0")) and J.le(prevPrice_2, J.get(fvg_6, "top0"))) and J.gt(prevPrice_2, J.get(fvg_6, "bot0"))):
                            J.set(bullRet, i_2, True)
                            J.set(fvg_6, "signaled", True)
                            J.update_member(debugCounters, "bullSignals", J.inc, True)
            j_3 = J.sub(J.get(bullInv, "length"), 1)
            while J.ge(j_3, 0):
                fvg_7 = J.get(bullInv, j_3)
                if (J.ge(J.get(fvg_7, "state"), 1) and J.sne(J.get(fvg_7, "alive"), False)):
                    shouldInvalidate = (_t8 if J.truthy(_t8 := (J.gt(currentCTop, J.get(fvg_7, "top0")) if J.truthy(_t9 := J.seq(J.get(fvg_7, "dir"), (-1))) else _t9)) else (J.lt(currentCBot, J.get(fvg_7, "bot0")) if J.truthy(_t10 := J.seq(J.get(fvg_7, "dir"), 1)) else _t10))
                    if J.truthy(shouldInvalidate):
                        J.set(fvg_7, "alive", False)
                        J.set(fvg_7, "endIndex", i_2)
                        J.update_member(debugCounters, "zonesInvalidated", J.inc, True)
                j_3 = J.dec(j_3)
            j_4 = J.sub(J.get(bearInv, "length"), 1)
            while J.ge(j_4, 0):
                fvg_8 = J.get(bearInv, j_4)
                if (J.ge(J.get(fvg_8, "state"), 1) and J.sne(J.get(fvg_8, "alive"), False)):
                    shouldInvalidate_2 = (_t11 if J.truthy(_t11 := (J.gt(currentCTop, J.get(fvg_8, "top0")) if J.truthy(_t12 := J.seq(J.get(fvg_8, "dir"), (-1))) else _t12)) else (J.lt(currentCBot, J.get(fvg_8, "bot0")) if J.truthy(_t13 := J.seq(J.get(fvg_8, "dir"), 1)) else _t13))
                    if J.truthy(shouldInvalidate_2):
                        J.set(fvg_8, "alive", False)
                        J.set(fvg_8, "endIndex", i_2)
                        J.update_member(debugCounters, "zonesInvalidated", J.inc, True)
                j_4 = J.dec(j_4)
            if J.ge(J.get(bulls, "length"), BUFFER):
                J.get(bulls, "splice")(0, J.add(J.sub(J.get(bulls, "length"), BUFFER), 10))
            if J.ge(J.get(bears, "length"), BUFFER):
                J.get(bears, "splice")(0, J.add(J.sub(J.get(bears, "length"), BUFFER), 10))
            if J.ge(J.get(bullInv, "length"), BUFFER):
                J.get(bullInv, "splice")(0, J.add(J.sub(J.get(bullInv, "length"), BUFFER), 10))
            if J.ge(J.get(bearInv, "length"), BUFFER):
                J.get(bearInv, "splice")(0, J.add(J.sub(J.get(bearInv, "length"), BUFFER), 10))
        except Exception as _e14:
            error = J.catch_value(_e14)
            J.get(G_console, "warn")(J.add(J.add("IFVG processing error at bar ", i_2), ":"), error)
            i_2 = J.inc(i_2)
            continue
        i_2 = J.inc(i_2)
    def _f15(z=J.undefined, *_args):
        return ((J.get(z, "xIndex") is not None) if J.truthy(_t1 := (J.get(z, "xIndex") is not J.undefined)) else _t1)
    recentBulls = J.get(J.get(bulls, "filter")(_f15), "slice")(J.neg(disp_num))
    def _f16(z=J.undefined, *_args):
        return ((J.get(z, "xIndex") is not None) if J.truthy(_t1 := (J.get(z, "xIndex") is not J.undefined)) else _t1)
    recentBears = J.get(J.get(bears, "filter")(_f16), "slice")(J.neg(disp_num))
    def _f17(z=J.undefined, *_args):
        return ((J.get(z, "xIndex") is not None) if J.truthy(_t1 := (J.get(z, "xIndex") is not J.undefined)) else _t1)
    recentBullInv = J.get(J.get(bullInv, "filter")(_f17), "slice")(J.neg(disp_num))
    def _f18(z=J.undefined, *_args):
        return ((J.get(z, "xIndex") is not None) if J.truthy(_t1 := (J.get(z, "xIndex") is not J.undefined)) else _t1)
    recentBearInv = J.get(J.get(bearInv, "filter")(_f18), "slice")(J.neg(disp_num))
    def _f19(a=J.undefined, b=J.undefined, *_args):
        return J.sub(J.get(a, "xIndex"), J.get(b, "xIndex"))
    allZones = J.get(J.get(recentBulls, "concat")(recentBears, recentBullInv, recentBearInv), "sort")(_f19)
    i_3 = 0
    while J.lt(i_3, J.get(G_close, "length")):
        k_2 = 0
        while J.lt(k_2, J.get(G_Math, "min")(J.get(allZones, "length"), maxZones)):
            zone = J.get(allZones, k_2)
            if (J.ge(i_3, J.get(zone, "left")) and J.le(i_3, J.get(zone, "xIndex"))):
                J.set(J.get(preTopSeries, k_2), i_3, J.get(zone, "top0"))
                J.set(J.get(preBotSeries, k_2), i_3, J.get(zone, "bot0"))
            maxRight = J.undefined
            if ((J.get(zone, "endIndex") is not None) and (J.get(zone, "endIndex") is not J.undefined)):
                maxRight = J.get(zone, "endIndex")
            elif (J.truthy(extendZones) and J.sne(J.get(zone, "alive"), False)):
                maxRight = J.get(G_Math, "min")(J.add(i_3, proj_len), J.sub(J.get(G_close, "length"), 1))
            else:
                maxRight = J.get(zone, "xIndex")
            if (J.ge(i_3, J.get(zone, "xIndex")) and J.le(i_3, maxRight)):
                J.set(J.get(postTopSeries, k_2), i_3, J.get(zone, "top0"))
                J.set(J.get(postBotSeries, k_2), i_3, J.get(zone, "bot0"))
            if J.truthy(showMidlines):
                totalRight = J.get(G_Math, "max")(J.get(zone, "xIndex"), maxRight)
                if (J.ge(i_3, J.get(zone, "left")) and J.le(i_3, totalRight)):
                    J.set(J.get(midSeries, k_2), i_3, J.get(zone, "mid0"))
            k_2 = J.inc(k_2)
        i_3 = J.inc(i_3)
    if J.truthy(showSeeds):
        seedTopRef = G_paint(seedTop, J.obj(("hidden", True), ("color", "#88888822")))
        seedBotRef = G_paint(seedBot, J.obj(("hidden", True), ("color", "#88888822")))
        G_fill(seedTopRef, seedBotRef, "#88888811")
    k_3 = 0
    while J.lt(k_3, J.get(G_Math, "min")(J.get(allZones, "length"), maxZones)):
        zone_2 = J.get(allZones, k_3)
        if (not J.truthy(zone_2)):
            k_3 = J.inc(k_3)
            continue
        preColor = J.undefined
        postColor = J.undefined
        if J.truthy(colorByLocation):
            currentPrice = J.get(G_close, J.sub(J.get(G_close, "length"), 1))
            zoneAbovePrice = J.gt(J.get(zone_2, "bot0"), currentPrice)
            preColor = (red if J.truthy(zoneAbovePrice) else green)
            postColor = (red if J.truthy(zoneAbovePrice) else green)
        else:
            if J.seq(J.get(zone_2, "dir"), (-1)):
                preColor = green
                postColor = red
            else:
                preColor = red
                postColor = green
        if J.truthy(showMidlines):
            G_paint(J.get(midSeries, k_3), J.obj(("color", midCol), ("style", "dotted"), ("thickness", 1)))
        preTopRef = G_paint(J.get(preTopSeries, k_3), J.obj(("hidden", True), ("color", preColor)))
        preBotRef = G_paint(J.get(preBotSeries, k_3), J.obj(("hidden", True), ("color", preColor)))
        postTopRef = G_paint(J.get(postTopSeries, k_3), J.obj(("hidden", True), ("color", postColor)))
        postBotRef = G_paint(J.get(postBotSeries, k_3), J.obj(("hidden", True), ("color", postColor)))
        G_fill(preTopRef, preBotRef, preColor)
        G_fill(postTopRef, postBotRef, postColor)
        k_3 = J.inc(k_3)
    if J.truthy(showInversionDots):
        G_paint(inversionDots, J.obj(("name", "Inversion Points"), ("color", midCol), ("style", "dotted"), ("thickness", 1)))
    G_register_signal(bearRet, "Bearish IFVG Signal")
    G_register_signal(bullRet, "Bullish IFVG Signal")


register_store_indicator(
    script,
    name='inversion_fair_value_gaps_ifvg_TS',
    title='Inversion Fair Value Gaps (IFVG)',
    developer='John Wolff',
    url='https://trendspider.com/trading-tools-store/indicators/689d40-inversion-fair-value-gaps-ifvg/',
    position='price',
    inputs=[{'id': 'show_last', 'title': 'Show Last', 'type': 'number', 'default': 5}, {'id': 'use_wick_for_signals', 'title': 'Use Wick for Signals', 'type': 'boolean', 'default': False}, {'id': 'atr_multiplier', 'title': 'ATR Multiplier', 'type': 'number', 'default': 0.25}, {'id': 'projection_bars', 'title': 'Projection Bars', 'type': 'number', 'default': 50}, {'id': 'show_pre_inversion_seeds_', 'title': 'Show Pre-Inversion Seeds?', 'type': 'boolean', 'default': False}, {'id': 'show_inversion_points_', 'title': 'Show Inversion Points?', 'type': 'boolean', 'default': True}, {'id': 'extend_active_zones_', 'title': 'Extend Active Zones?', 'type': 'boolean', 'default': True}, {'id': 'show_zone_midlines_', 'title': 'Show Zone Midlines?', 'type': 'boolean', 'default': True}, {'id': 'color_zones_by_location__above_price___red__below___green__', 'title': 'Color Zones by Location (Above Price = Red, Below = Green)?', 'type': 'boolean', 'default': False}, {'id': 'filter_session_gaps_', 'title': 'Filter Session Gaps?', 'type': 'boolean', 'default': True}, {'id': 'session_gap_threshold__', 'title': 'Session Gap Threshold %', 'type': 'number', 'default': 0.1}],
    outputs=['line_1', 'line_2', 'line_3', 'line_4', 'line_5', 'line_8', 'line_9', 'line_10', 'line_11', 'line_12', 'inversion_points', 'bearish_ifvg_signal', 'bullish_ifvg_signal'],
    signals=['bearish_ifvg_signal', 'bullish_ifvg_signal'],
    requires=[],
    parity='exact',
)
