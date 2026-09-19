"""
ORB Trading Strategy Indicator -- TrendSpider store indicator by TrendSpider.

Registered as "orb_trading_strategy_indicator_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6977b1-orb-trading-strategy-indicator/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
aapl_d: both-error, syn_5m: OK.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Array = G["Array"]
    G_Math = G["Math"]
    G_assert = G["assert"]
    G_close = G["close"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_input = G["input"]
    G_isNaN = G["isNaN"]
    G_library = G["library"]
    G_low = G["low"]
    G_paint = G["paint"]
    G_paint_label_at_line = G["paint_label_at_line"]
    G_paint_projection = G["paint_projection"]
    G_parseInt = G["parseInt"]
    G_register_signal = G["register_signal"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    def seriesOrNull(enabled=J.undefined, s=J.undefined, *_args):
        return (s if J.truthy(enabled) else G_series_of(None))
    def getETMinutes(ts=J.undefined, *_args):
        m = J.get(moment, "tz")(J.mul(ts, 1000), SESSION_TZ)
        return J.add(J.mul(J.get(m, "hour")(), 60), J.get(m, "minute")())
    def isWithinSession(ts=J.undefined, *_args):
        timeVal = getETMinutes(ts)
        if J.truthy(sessionCrossesMidnight):
            return (_t1 if J.truthy(_t1 := J.ge(timeVal, sessionStartMinutes)) else J.lt(timeVal, sessionEndMinutes))
        return (J.lt(timeVal, sessionEndMinutes) if J.truthy(_t2 := J.ge(timeVal, sessionStartMinutes)) else _t2)
    def getSessionDayKey(ts=J.undefined, *_args):
        m = J.get(moment, "tz")(J.mul(ts, 1000), SESSION_TZ)
        timeVal = J.add(J.mul(J.get(m, "hour")(), 60), J.get(m, "minute")())
        if (J.truthy(sessionCrossesMidnight) and J.lt(timeVal, sessionEndMinutes)):
            return J.get(J.get(J.get(m, "clone")(), "subtract")(1, "day"), "format")("YYYY-MM-DD")
        return J.get(m, "format")("YYYY-MM-DD")
    def getORWindowStart(dayKey=J.undefined, *_args):
        m = J.get(moment, "tz")(dayKey, "YYYY-MM-DD", SESSION_TZ)
        J.get(m, "hour")(sessionStartHour)
        J.get(m, "minute")(sessionStartMin)
        J.get(m, "second")(0)
        return J.get(m, "unix")()
    def lastDefinedIndex(s=J.undefined, *_args):
        i = J.sub(J.get(s, "length"), 1)
        while J.ge(i, 0):
            if ((J.get(s, i) is not None) and (J.get(s, i) is not J.undefined)):
                return i
            i = J.dec(i)
        return (-1)
    def labelEndOfLineSafe(enabled=J.undefined, paintedLine=J.undefined, series=J.undefined, text=J.undefined, color=J.undefined, labelStyle=J.undefined, *_args):
        if (not J.truthy(showEndLabels)):
            return J.undefined
        idx = lastDefinedIndex((series if J.truthy(enabled) else G_series_of(None)))
        if J.lt(idx, 0):
            return J.undefined
        G_paint_label_at_line(paintedLine, idx, text, J.obj(*J.obj_spread(labelStyle), ("color", color)))
    G_describe_indicator("ORB Trading Strategy Indicator", "overlay")
    moment = G_library("moment-timezone")
    chartTimeframe = G_parseInt(J.get(G_current, "resolution"), 10)
    isIntraday = (not J.truthy(G_isNaN(chartTimeframe)))
    G_assert(isIntraday, "This indicator requires an intraday chart (minute-based timeframe).")
    sessionChoice = J.get(G_input, "select")("Session", "New York (9:30 AM ET)", J.JSArray(["New York (9:30 AM ET)", "London (3:00 AM ET)", "Asian (7:00 PM ET)", "Globex (6:00 PM ET)"]))
    displayOverride = J.get(G_input, "select")("OR Window", "Auto", J.JSArray(["Auto", "1", "5", "10", "15", "30", "60"]))
    orWindowMinutes = (chartTimeframe if J.seq(displayOverride, "Auto") else G_parseInt(displayOverride, 10))
    supportedTFs = J.JSArray([1, 5, 10, 15, 30, 60])
    if J.seq(displayOverride, "Auto"):
        G_assert(J.get(supportedTFs, "includes")(chartTimeframe), J.template("Chart timeframe (", chartTimeframe, "m) not supported for Auto mode. Use 1m, 5m, 10m, 15m, 30m, or 60m — or set an OR Window override."))
    showMidpoint = J.get(G_input, "boolean")("Show OR Midpoint", False)
    showHistorical = J.get(G_input, "boolean")("Show Historical Sessions", True)
    showEndLabels = J.get(G_input, "boolean")("Show End-of-Line Labels", True)
    showEntryLabels = J.get(G_input, "boolean")("Show Entry Labels", True)
    showR05 = J.get(G_input, "boolean")("Show 0.5R Targets", False)
    showR1 = J.get(G_input, "boolean")("Show 1R Targets", True)
    showR2 = J.get(G_input, "boolean")("Show 2R Targets", False)
    showR3 = J.get(G_input, "boolean")("Show 3R Targets", False)
    colorORH = J.get(G_input, "color")("ORH Color", "#22C55E")
    colorORL = J.get(G_input, "color")("ORL Color", "#EF4444")
    colorMid = J.get(G_input, "color")("OR Midpoint Color", "#94A3B8")
    colorLongTargets = J.get(G_input, "color")("Long Targets Color", "#22C55E")
    colorShortTargets = J.get(G_input, "color")("Short Targets Color", "#EF4444")
    SESSION_TZ = "America/New_York"
    sessionStartHour = J.undefined
    sessionStartMin = J.undefined
    sessionEndHour = J.undefined
    sessionEndMin = J.undefined
    sessionLabel = J.undefined
    if J.seq(sessionChoice, "New York (9:30 AM ET)"):
        sessionStartHour = 9
        sessionStartMin = 30
        sessionEndHour = 16
        sessionEndMin = 0
        sessionLabel = "NY"
    elif J.seq(sessionChoice, "London (3:00 AM ET)"):
        sessionStartHour = 3
        sessionStartMin = 0
        sessionEndHour = 12
        sessionEndMin = 0
        sessionLabel = "LDN"
    elif J.seq(sessionChoice, "Asian (7:00 PM ET)"):
        sessionStartHour = 19
        sessionStartMin = 0
        sessionEndHour = 4
        sessionEndMin = 0
        sessionLabel = "ASIA"
    elif J.seq(sessionChoice, "Globex (6:00 PM ET)"):
        sessionStartHour = 18
        sessionStartMin = 0
        sessionEndHour = 17
        sessionEndMin = 0
        sessionLabel = "GBX"
    sessionStartMinutes = J.add(J.mul(sessionStartHour, 60), sessionStartMin)
    sessionEndMinutes = J.add(J.mul(sessionEndHour, 60), sessionEndMin)
    sessionCrossesMidnight = J.le(sessionEndMinutes, sessionStartMinutes)
    LABEL_STYLE_OR = J.obj(("border_width", 1), ("border_radius", 3), ("border_color", "#374151"), ("background_color", "#111827"))
    LABEL_STYLE_TARGET = J.obj(("border_width", 1), ("border_radius", 3), ("border_color", "#374151"), ("background_color", "#111827"))
    stateORBuilding = G_series_of(False)
    stateORLockedToday = G_series_of(False)
    stateRTHActive = G_series_of(False)
    orhLevel = G_series_of(None)
    orlLevel = G_series_of(None)
    orMidLevel = G_series_of(None)
    upR05Level = G_series_of(None)
    upR1Level = G_series_of(None)
    upR2Level = G_series_of(None)
    upR3Level = G_series_of(None)
    dnR05Level = G_series_of(None)
    dnR1Level = G_series_of(None)
    dnR2Level = G_series_of(None)
    dnR3Level = G_series_of(None)
    longStopLevel = G_series_of(None)
    shortStopLevel = G_series_of(None)
    orhVisual = G_series_of(None)
    orlVisual = G_series_of(None)
    orMidVisual = G_series_of(None)
    upR05Visual = G_series_of(None)
    upR1Visual = G_series_of(None)
    upR2Visual = G_series_of(None)
    upR3Visual = G_series_of(None)
    dnR05Visual = G_series_of(None)
    dnR1Visual = G_series_of(None)
    dnR2Visual = G_series_of(None)
    dnR3Visual = G_series_of(None)
    dayKeySeries = G_series_of(None)
    isCurrentDaySeries = G_series_of(False)
    currentDayKey = None
    orWindowStartTs = None
    orWindowEndTs = None
    sessionORHigh = None
    sessionORLow = None
    sessionORLocked = False
    carryORH = None
    carryORL = None
    carryMid = None
    carryUpR05 = None
    carryUpR1 = None
    carryUpR2 = None
    carryUpR3 = None
    carryDnR05 = None
    carryDnR1 = None
    carryDnR2 = None
    carryDnR3 = None
    lastDayKey = getSessionDayKey(J.get(G_time, J.sub(J.get(G_time, "length"), 1)))
    i = 0
    while J.lt(i, J.get(G_time, "length")):
        ts = J.get(G_time, i)
        dayKey = getSessionDayKey(ts)
        J.set(dayKeySeries, i, dayKey)
        J.set(isCurrentDaySeries, i, J.seq(dayKey, lastDayKey))
        if J.sne(dayKey, currentDayKey):
            currentDayKey = dayKey
            orWindowStartTs = getORWindowStart(dayKey)
            orWindowEndTs = J.add(orWindowStartTs, J.mul(orWindowMinutes, 60))
            sessionORHigh = None
            sessionORLow = None
            sessionORLocked = False
        inRTH = isWithinSession(ts)
        J.set(stateRTHActive, i, inRTH)
        withinORWindow = (J.lt(ts, orWindowEndTs) if J.truthy(_t1 := J.ge(ts, orWindowStartTs)) else _t1)
        pastORWindow = J.ge(ts, orWindowEndTs)
        if (J.truthy(withinORWindow) and J.truthy(inRTH)):
            J.set(stateORBuilding, i, True)
            J.set(stateORLockedToday, i, False)
            sessionORHigh = (J.get(G_high, i) if (sessionORHigh is None) else J.get(G_Math, "max")(sessionORHigh, J.get(G_high, i)))
            sessionORLow = (J.get(G_low, i) if (sessionORLow is None) else J.get(G_Math, "min")(sessionORLow, J.get(G_low, i)))
        elif ((((J.truthy(pastORWindow) and J.truthy(inRTH)) and (not J.truthy(sessionORLocked))) and (sessionORHigh is not None)) and (sessionORLow is not None)):
            sessionORLocked = True
            J.set(stateORBuilding, i, False)
            J.set(stateORLockedToday, i, True)
            range = J.sub(sessionORHigh, sessionORLow)
            carryORH = sessionORHigh
            carryORL = sessionORLow
            carryMid = J.div(J.add(carryORH, carryORL), 2)
            if J.gt(range, 0):
                carryUpR05 = J.add(carryORH, J.mul(range, 0.5))
                carryUpR1 = J.add(carryORH, J.mul(range, 1))
                carryUpR2 = J.add(carryORH, J.mul(range, 2))
                carryUpR3 = J.add(carryORH, J.mul(range, 3))
                carryDnR05 = J.sub(carryORL, J.mul(range, 0.5))
                carryDnR1 = J.sub(carryORL, J.mul(range, 1))
                carryDnR2 = J.sub(carryORL, J.mul(range, 2))
                carryDnR3 = J.sub(carryORL, J.mul(range, 3))
            else:
                carryUpR05 = (carryUpR1 := (carryUpR2 := (carryUpR3 := None)))
                carryDnR05 = (carryDnR1 := (carryDnR2 := (carryDnR3 := None)))
        elif J.truthy(sessionORLocked):
            J.set(stateORBuilding, i, False)
            J.set(stateORLockedToday, i, inRTH)
        J.set(orhLevel, i, carryORH)
        J.set(orlLevel, i, carryORL)
        J.set(orMidLevel, i, carryMid)
        J.set(upR05Level, i, carryUpR05)
        J.set(upR1Level, i, carryUpR1)
        J.set(upR2Level, i, carryUpR2)
        J.set(upR3Level, i, carryUpR3)
        J.set(dnR05Level, i, carryDnR05)
        J.set(dnR1Level, i, carryDnR1)
        J.set(dnR2Level, i, carryDnR2)
        J.set(dnR3Level, i, carryDnR3)
        J.set(longStopLevel, i, carryORL)
        J.set(shortStopLevel, i, carryORH)
        show = (((_t3 if J.truthy(_t3 := J.get(stateORBuilding, i)) else sessionORLocked) if J.truthy(_t2 := inRTH) else _t2) if J.truthy(showHistorical) else ((_t6 if J.truthy(_t6 := J.get(stateORBuilding, i)) else sessionORLocked) if J.truthy(_t4 := (inRTH if J.truthy(_t5 := J.get(isCurrentDaySeries, i)) else _t5)) else _t4))
        if J.truthy(show):
            if ((J.truthy(J.get(stateORBuilding, i)) and (sessionORHigh is not None)) and (sessionORLow is not None)):
                J.set(orhVisual, i, sessionORHigh)
                J.set(orlVisual, i, sessionORLow)
                J.set(orMidVisual, i, J.div(J.add(sessionORHigh, sessionORLow), 2))
            elif J.truthy(sessionORLocked):
                J.set(orhVisual, i, carryORH)
                J.set(orlVisual, i, carryORL)
                J.set(orMidVisual, i, carryMid)
                J.set(upR05Visual, i, carryUpR05)
                J.set(upR1Visual, i, carryUpR1)
                J.set(upR2Visual, i, carryUpR2)
                J.set(upR3Visual, i, carryUpR3)
                J.set(dnR05Visual, i, carryDnR05)
                J.set(dnR1Visual, i, carryDnR1)
                J.set(dnR2Visual, i, carryDnR2)
                J.set(dnR3Visual, i, carryDnR3)
        i = J.inc(i)
    orbLongEntry = G_series_of(False)
    orbShortEntry = G_series_of(False)
    sessionHadEntry = False
    currentSessionKey = None
    i_2 = 1
    while J.lt(i_2, J.get(G_time, "length")):
        dayKey_2 = J.get(dayKeySeries, i_2)
        if J.sne(dayKey_2, currentSessionKey):
            currentSessionKey = dayKey_2
            sessionHadEntry = False
        prevClose = J.get(G_close, J.sub(i_2, 1))
        currClose = J.get(G_close, i_2)
        orh = J.get(orhLevel, i_2)
        orl = J.get(orlLevel, i_2)
        locked = J.get(stateORLockedToday, i_2)
        if (((((not J.truthy(sessionHadEntry)) and (orh is not None)) and (orl is not None)) and (prevClose is not None)) and J.truthy(locked)):
            if (J.le(prevClose, orh) and J.gt(currClose, orh)):
                J.set(orbLongEntry, i_2, True)
                sessionHadEntry = True
            elif (J.ge(prevClose, orl) and J.lt(currClose, orl)):
                J.set(orbShortEntry, i_2, True)
                sessionHadEntry = True
        i_2 = J.inc(i_2)
    scannerLongEntry = G_series_of(False)
    scannerShortEntry = G_series_of(False)
    scanSessionHadEntry = False
    scanCurrentSessionKey = None
    i_3 = 0
    while J.lt(i_3, J.get(G_time, "length")):
        dayKey_3 = J.get(dayKeySeries, i_3)
        if J.sne(dayKey_3, scanCurrentSessionKey):
            scanCurrentSessionKey = dayKey_3
            scanSessionHadEntry = False
        orh_2 = J.get(orhLevel, i_3)
        orl_2 = J.get(orlLevel, i_3)
        locked_2 = J.get(stateORLockedToday, i_3)
        if (((((not J.truthy(scanSessionHadEntry)) and J.truthy(J.get(isCurrentDaySeries, i_3))) and (orh_2 is not None)) and (orl_2 is not None)) and J.truthy(locked_2)):
            if J.gt(J.get(G_high, i_3), orh_2):
                J.set(scannerLongEntry, i_3, True)
                scanSessionHadEntry = True
            elif J.lt(J.get(G_low, i_3), orl_2):
                J.set(scannerShortEntry, i_3, True)
                scanSessionHadEntry = True
        i_3 = J.inc(i_3)
    longStopHit = G_series_of(False)
    shortStopHit = G_series_of(False)
    i_4 = 1
    while J.lt(i_4, J.get(G_time, "length")):
        orl_3 = J.get(orlLevel, i_4)
        orh_3 = J.get(orhLevel, i_4)
        if ((((orl_3 is not None) and (J.get(G_low, J.sub(i_4, 1)) is not None)) and J.ge(J.get(G_low, J.sub(i_4, 1)), orl_3)) and J.lt(J.get(G_low, i_4), orl_3)):
            J.set(longStopHit, i_4, True)
        if ((((orh_3 is not None) and (J.get(G_high, J.sub(i_4, 1)) is not None)) and J.le(J.get(G_high, J.sub(i_4, 1)), orh_3)) and J.gt(J.get(G_high, i_4), orh_3)):
            J.set(shortStopHit, i_4, True)
        i_4 = J.inc(i_4)
    longTarget05Hit = G_series_of(False)
    longTarget1Hit = G_series_of(False)
    longTarget2Hit = G_series_of(False)
    longTarget3Hit = G_series_of(False)
    shortTarget05Hit = G_series_of(False)
    shortTarget1Hit = G_series_of(False)
    shortTarget2Hit = G_series_of(False)
    shortTarget3Hit = G_series_of(False)
    i_5 = 1
    while J.lt(i_5, J.get(G_time, "length")):
        pH = J.get(G_high, J.sub(i_5, 1))
        cH = J.get(G_high, i_5)
        pL = J.get(G_low, J.sub(i_5, 1))
        cL = J.get(G_low, i_5)
        l05 = J.get(upR05Level, i_5)
        if ((((l05 is not None) and (pH is not None)) and J.lt(pH, l05)) and J.ge(cH, l05)):
            J.set(longTarget05Hit, i_5, True)
        l1 = J.get(upR1Level, i_5)
        if ((((l1 is not None) and (pH is not None)) and J.lt(pH, l1)) and J.ge(cH, l1)):
            J.set(longTarget1Hit, i_5, True)
        l2 = J.get(upR2Level, i_5)
        if ((((l2 is not None) and (pH is not None)) and J.lt(pH, l2)) and J.ge(cH, l2)):
            J.set(longTarget2Hit, i_5, True)
        l3 = J.get(upR3Level, i_5)
        if ((((l3 is not None) and (pH is not None)) and J.lt(pH, l3)) and J.ge(cH, l3)):
            J.set(longTarget3Hit, i_5, True)
        s05 = J.get(dnR05Level, i_5)
        if ((((s05 is not None) and (pL is not None)) and J.gt(pL, s05)) and J.le(cL, s05)):
            J.set(shortTarget05Hit, i_5, True)
        s1 = J.get(dnR1Level, i_5)
        if ((((s1 is not None) and (pL is not None)) and J.gt(pL, s1)) and J.le(cL, s1)):
            J.set(shortTarget1Hit, i_5, True)
        s2 = J.get(dnR2Level, i_5)
        if ((((s2 is not None) and (pL is not None)) and J.gt(pL, s2)) and J.le(cL, s2)):
            J.set(shortTarget2Hit, i_5, True)
        s3 = J.get(dnR3Level, i_5)
        if ((((s3 is not None) and (pL is not None)) and J.gt(pL, s3)) and J.le(cL, s3)):
            J.set(shortTarget3Hit, i_5, True)
        i_5 = J.inc(i_5)
    sessionExit = G_series_of(False)
    exitTimeMinutes = J.undefined
    if J.truthy(sessionCrossesMidnight):
        exitTimeMinutes = J.sub(sessionEndMinutes, chartTimeframe)
        if J.lt(exitTimeMinutes, 0):
            exitTimeMinutes = J.add(exitTimeMinutes, J.mul(24, 60))
    else:
        exitTimeMinutes = J.sub(sessionEndMinutes, chartTimeframe)
    eodExitFiredThisSession = False
    currentEodSessionKey = None
    i_6 = 0
    while J.lt(i_6, J.get(G_time, "length")):
        dayKey_4 = J.get(dayKeySeries, i_6)
        if J.sne(dayKey_4, currentEodSessionKey):
            currentEodSessionKey = dayKey_4
            eodExitFiredThisSession = False
        candleMinutes = getETMinutes(J.get(G_time, i_6))
        pastExitTime = False
        if J.truthy(sessionCrossesMidnight):
            if J.ge(exitTimeMinutes, sessionStartMinutes):
                pastExitTime = (_t7 if J.truthy(_t7 := J.ge(candleMinutes, exitTimeMinutes)) else J.lt(candleMinutes, sessionEndMinutes))
            else:
                pastExitTime = (J.lt(candleMinutes, sessionEndMinutes) if J.truthy(_t8 := J.ge(candleMinutes, exitTimeMinutes)) else _t8)
        else:
            pastExitTime = J.ge(candleMinutes, exitTimeMinutes)
        if ((J.truthy(J.get(stateRTHActive, i_6)) and (not J.truthy(eodExitFiredThisSession))) and J.truthy(pastExitTime)):
            J.set(sessionExit, i_6, True)
            eodExitFiredThisSession = True
        i_6 = J.inc(i_6)
    i_7 = 1
    while J.lt(i_7, J.get(G_time, "length")):
        if (J.truthy(J.get(stateRTHActive, J.sub(i_7, 1))) and (not J.truthy(J.get(stateRTHActive, i_7)))):
            J.set(sessionExit, i_7, True)
        i_7 = J.inc(i_7)
    safeEntryWindow = G_series_of(False)
    entryCutoffMinutes = J.undefined
    if J.truthy(sessionCrossesMidnight):
        entryCutoffMinutes = J.sub(sessionEndMinutes, J.get(G_Math, "floor")(J.mul(orWindowMinutes, 3.5)))
        if J.lt(entryCutoffMinutes, 0):
            entryCutoffMinutes = J.add(entryCutoffMinutes, J.mul(24, 60))
    else:
        entryCutoffMinutes = J.sub(sessionEndMinutes, J.get(G_Math, "floor")(J.mul(orWindowMinutes, 3.5)))
    i_8 = 0
    while J.lt(i_8, J.get(G_time, "length")):
        candleMinutes_2 = getETMinutes(J.get(G_time, i_8))
        beforeCutoff = False
        if J.truthy(sessionCrossesMidnight):
            if J.ge(entryCutoffMinutes, sessionStartMinutes):
                beforeCutoff = (J.lt(candleMinutes_2, entryCutoffMinutes) if J.truthy(_t9 := J.ge(candleMinutes_2, sessionStartMinutes)) else _t9)
            else:
                beforeCutoff = (_t10 if J.truthy(_t10 := J.ge(candleMinutes_2, sessionStartMinutes)) else J.lt(candleMinutes_2, entryCutoffMinutes))
        else:
            beforeCutoff = J.lt(candleMinutes_2, entryCutoffMinutes)
        if ((J.truthy(J.get(stateORLockedToday, i_8)) and J.truthy(J.get(stateRTHActive, i_8))) and J.truthy(beforeCutoff)):
            J.set(safeEntryWindow, i_8, True)
        i_8 = J.inc(i_8)
    G_register_signal(orbLongEntry, "Entry: Long (Strategy)")
    G_register_signal(orbShortEntry, "Entry: Short (Strategy)")
    G_register_signal(scannerLongEntry, "Entry: Long (Scan)")
    G_register_signal(scannerShortEntry, "Entry: Short (Scan)")
    G_register_signal(safeEntryWindow, "Safe Entry Window")
    G_register_signal(longStopHit, "Stop: Long")
    G_register_signal(shortStopHit, "Stop: Short")
    G_register_signal(longTarget05Hit, "Target: Long 0.5R")
    G_register_signal(longTarget1Hit, "Target: Long 1R")
    G_register_signal(longTarget2Hit, "Target: Long 2R")
    G_register_signal(longTarget3Hit, "Target: Long 3R")
    G_register_signal(shortTarget05Hit, "Target: Short 0.5R")
    G_register_signal(shortTarget1Hit, "Target: Short 1R")
    G_register_signal(shortTarget2Hit, "Target: Short 2R")
    G_register_signal(shortTarget3Hit, "Target: Short 3R")
    G_register_signal(sessionExit, "Session Exit")
    pORH = G_paint(orhVisual, J.obj(("name", "ORH (Long Breakout)"), ("style", "ladder"), ("color", colorORH), ("thickness", 2)))
    pORL = G_paint(orlVisual, J.obj(("name", "ORL (Short Breakdown)"), ("style", "ladder"), ("color", colorORL), ("thickness", 2)))
    pMid = G_paint(seriesOrNull(showMidpoint, orMidVisual), J.obj(("name", "OR Midpoint"), ("style", "ladder"), ("color", colorMid), ("thickness", 1)))
    pLongR05 = G_paint(seriesOrNull(showR05, upR05Visual), J.obj(("name", "Long 0.5R Target"), ("style", "ladder"), ("color", colorLongTargets), ("thickness", 1)))
    pLongR1 = G_paint(seriesOrNull(showR1, upR1Visual), J.obj(("name", "Long 1R Target"), ("style", "ladder"), ("color", colorLongTargets), ("thickness", 1)))
    pLongR2 = G_paint(seriesOrNull(showR2, upR2Visual), J.obj(("name", "Long 2R Target"), ("style", "ladder"), ("color", colorLongTargets), ("thickness", 1)))
    pLongR3 = G_paint(seriesOrNull(showR3, upR3Visual), J.obj(("name", "Long 3R Target"), ("style", "ladder"), ("color", colorLongTargets), ("thickness", 1)))
    pShortR05 = G_paint(seriesOrNull(showR05, dnR05Visual), J.obj(("name", "Short 0.5R Target"), ("style", "ladder"), ("color", colorShortTargets), ("thickness", 1)))
    pShortR1 = G_paint(seriesOrNull(showR1, dnR1Visual), J.obj(("name", "Short 1R Target"), ("style", "ladder"), ("color", colorShortTargets), ("thickness", 1)))
    pShortR2 = G_paint(seriesOrNull(showR2, dnR2Visual), J.obj(("name", "Short 2R Target"), ("style", "ladder"), ("color", colorShortTargets), ("thickness", 1)))
    pShortR3 = G_paint(seriesOrNull(showR3, dnR3Visual), J.obj(("name", "Short 3R Target"), ("style", "ladder"), ("color", colorShortTargets), ("thickness", 1)))
    labelEndOfLineSafe(True, pORH, orhVisual, J.template("ORH [", sessionLabel, "]"), colorORH, LABEL_STYLE_OR)
    labelEndOfLineSafe(True, pORL, orlVisual, J.template("ORL [", sessionLabel, "]"), colorORL, LABEL_STYLE_OR)
    labelEndOfLineSafe(showMidpoint, pMid, orMidVisual, "MID", colorMid, LABEL_STYLE_OR)
    labelEndOfLineSafe(showR05, pLongR05, upR05Visual, "0.5R", colorLongTargets, LABEL_STYLE_TARGET)
    labelEndOfLineSafe(showR1, pLongR1, upR1Visual, "1R", colorLongTargets, LABEL_STYLE_TARGET)
    labelEndOfLineSafe(showR2, pLongR2, upR2Visual, "2R", colorLongTargets, LABEL_STYLE_TARGET)
    labelEndOfLineSafe(showR3, pLongR3, upR3Visual, "3R", colorLongTargets, LABEL_STYLE_TARGET)
    labelEndOfLineSafe(showR05, pShortR05, dnR05Visual, "0.5R", colorShortTargets, LABEL_STYLE_TARGET)
    labelEndOfLineSafe(showR1, pShortR1, dnR1Visual, "1R", colorShortTargets, LABEL_STYLE_TARGET)
    labelEndOfLineSafe(showR2, pShortR2, dnR2Visual, "2R", colorShortTargets, LABEL_STYLE_TARGET)
    labelEndOfLineSafe(showR3, pShortR3, dnR3Visual, "3R", colorShortTargets, LABEL_STYLE_TARGET)
    lastTs = J.get(G_time, J.sub(J.get(G_time, "length"), 1))
    lastCandleMinutes = getETMinutes(lastTs)
    lastCandleInRTH = J.get(stateRTHActive, J.sub(J.get(G_time, "length"), 1))
    minutesRemaining = 0
    if (J.truthy(lastCandleInRTH) and (carryORH is not None)):
        if J.truthy(sessionCrossesMidnight):
            if J.ge(lastCandleMinutes, sessionStartMinutes):
                minutesRemaining = J.add(J.sub(J.mul(24, 60), lastCandleMinutes), sessionEndMinutes)
            else:
                minutesRemaining = J.sub(sessionEndMinutes, lastCandleMinutes)
        else:
            minutesRemaining = J.sub(sessionEndMinutes, lastCandleMinutes)
    if ((J.truthy(lastCandleInRTH) and (carryORH is not None)) and J.gt(minutesRemaining, 0)):
        candlesRemaining = J.get(G_Math, "max")(1, J.get(G_Math, "ceil")(J.div(minutesRemaining, chartTimeframe)))
        G_paint_projection(pORH, J.get(G_Array(candlesRemaining), "fill")(carryORH))
        G_paint_projection(pORL, J.get(G_Array(candlesRemaining), "fill")(carryORL))
        if (J.truthy(showMidpoint) and (carryMid is not None)):
            G_paint_projection(pMid, J.get(G_Array(candlesRemaining), "fill")(carryMid))
        if J.truthy(showR05):
            if (carryUpR05 is not None):
                G_paint_projection(pLongR05, J.get(G_Array(candlesRemaining), "fill")(carryUpR05))
            if (carryDnR05 is not None):
                G_paint_projection(pShortR05, J.get(G_Array(candlesRemaining), "fill")(carryDnR05))
        if J.truthy(showR1):
            if (carryUpR1 is not None):
                G_paint_projection(pLongR1, J.get(G_Array(candlesRemaining), "fill")(carryUpR1))
            if (carryDnR1 is not None):
                G_paint_projection(pShortR1, J.get(G_Array(candlesRemaining), "fill")(carryDnR1))
        if J.truthy(showR2):
            if (carryUpR2 is not None):
                G_paint_projection(pLongR2, J.get(G_Array(candlesRemaining), "fill")(carryUpR2))
            if (carryDnR2 is not None):
                G_paint_projection(pShortR2, J.get(G_Array(candlesRemaining), "fill")(carryDnR2))
        if J.truthy(showR3):
            if (carryUpR3 is not None):
                G_paint_projection(pLongR3, J.get(G_Array(candlesRemaining), "fill")(carryUpR3))
            if (carryDnR3 is not None):
                G_paint_projection(pShortR3, J.get(G_Array(candlesRemaining), "fill")(carryDnR3))
    def _f11(s=J.undefined, *_args):
        return ("LONG" if J.truthy(s) else None)
    longEntryLabels = G_for_every(orbLongEntry, _f11)
    def _f12(s=J.undefined, *_args):
        return ("SHORT" if J.truthy(s) else None)
    shortEntryLabels = G_for_every(orbShortEntry, _f12)
    G_paint(seriesOrNull(showEntryLabels, longEntryLabels), J.obj(("style", "labels_below"), ("name", "Long Entry"), ("color", "#FFFFFF"), ("backgroundColor", "#22C55E"), ("fontSize", 11), ("verticalOffset", 5)))
    G_paint(seriesOrNull(showEntryLabels, shortEntryLabels), J.obj(("style", "labels_above"), ("name", "Short Entry"), ("color", "#FFFFFF"), ("backgroundColor", "#EF4444"), ("fontSize", 11), ("verticalOffset", 5)))


register_store_indicator(
    script,
    name='orb_trading_strategy_indicator_TS',
    title='ORB Trading Strategy Indicator',
    developer='TrendSpider',
    url='https://trendspider.com/trading-tools-store/indicators/6977b1-orb-trading-strategy-indicator/',
    position='price',
    inputs=[],
    outputs=[],
    signals=[],
    requires=[],
    parity='aapl_d: both-error, syn_5m: OK',
)
