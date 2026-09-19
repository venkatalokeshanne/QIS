"""
Options Contract Chart Overlay -- TrendSpider store indicator by Rock Regan.

Registered as "options_contract_chart_overlay_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/69d59d-options-contract-chart-overlay/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Array = G["Array"]
    G_Math = G["Math"]
    G_NaN = G["NaN"]
    G_Number = G["Number"]
    G_String = G["String"]
    G_barsAgo = G["barsAgo"]
    G_chartLabels = G["chartLabels"]
    G_chartStart = G["chartStart"]
    G_close = G["close"]
    G_constants = G["constants"]
    G_current = G["current"]
    G_datasets = G["datasets"]
    G_describe_indicator = G["describe_indicator"]
    G_diff = G["diff"]
    G_dist = G["dist"]
    G_drawPosLine = G["drawPosLine"]
    G_eDD = G["eDD"]
    G_eMM = G["eMM"]
    G_eYY = G["eYY"]
    G_effectiveColor = G["effectiveColor"]
    G_effectiveIsCall = G["effectiveIsCall"]
    G_exp = G["exp"]
    G_expStr = G["expStr"]
    G_finalBorder = G["finalBorder"]
    G_fmtG = G["fmtG"]
    G_fmtP = G["fmtP"]
    G_h = G["h"]
    G_h2 = G["h2"]
    G_hLen = G["hLen"]
    G_headerBg = G["headerBg"]
    G_hudRows = G["hudRows"]
    G_input = G["input"]
    G_intrinsic = G["intrinsic"]
    G_isDaily = G["isDaily"]
    G_isManualMode = G["isManualMode"]
    G_isNaN = G["isNaN"]
    G_lastVal = G["lastVal"]
    G_lastVal2 = G["lastVal2"]
    G_library = G["library"]
    G_lineColor = G["lineColor"]
    G_lineData = G["lineData"]
    G_manExp = G["manExp"]
    G_manStrRaw = G["manStrRaw"]
    G_manStrVal = G["manStrVal"]
    G_manTicker = G["manTicker"]
    G_manType = G["manType"]
    G_moneyness = G["moneyness"]
    G_occLen = G["occLen"]
    G_occLen2 = G["occLen2"]
    G_offsetLabel = G["offsetLabel"]
    G_opraData = G["opraData"]
    G_paint = G["paint"]
    G_paint_overlay = G["paint_overlay"]
    G_parseFloat = G["parseFloat"]
    G_parseInt = G["parseInt"]
    G_pointColors = G["pointColors"]
    G_posLine = G["posLine"]
    G_prevVal = G["prevVal"]
    G_request = G["request"]
    G_resStr = G["resStr"]
    G_scaledChartH = G["scaledChartH"]
    G_scaledChartW = G["scaledChartW"]
    G_schedType = G["schedType"]
    G_sd = G["sd"]
    G_srcTag = G["srcTag"]
    G_strikeInt = G["strikeInt"]
    G_strikePad = G["strikePad"]
    G_val = G["val"]
    manualLabel = J.undefined
    expCode = J.undefined
    selectedStrike = J.undefined
    schedule = J.undefined
    schedErr = J.undefined
    ei = J.undefined
    bestDiff = J.undefined
    bestIdx = J.undefined
    selectedExp = J.undefined
    strikeList = J.undefined
    si = J.undefined
    minDist = J.undefined
    atmIdx = J.undefined
    atmStrike = J.undefined
    targetIdx = J.undefined
    resolveErr = J.undefined
    occSymbol = J.undefined
    contractLabel = J.undefined
    hasContract = J.undefined
    effectiveTypeKey = J.undefined
    effectiveTicker = J.undefined
    contract = J.undefined
    curLast = J.undefined
    curBid = J.undefined
    curAsk = J.undefined
    curIV = J.undefined
    curOI = J.undefined
    curDelta = J.undefined
    curGamma = J.undefined
    curTheta = J.undefined
    curVega = J.undefined
    curVol = J.undefined
    spread = J.undefined
    hasOPRA = J.undefined
    histClose = J.undefined
    histTime = J.undefined
    hasChart = J.undefined
    i = J.undefined
    expInfo = J.undefined
    actualDTE = J.undefined
    atmInfo = J.undefined
    def scaleVal(n=J.undefined, *_args):
        return J.get(G_Math, "max")(1, J.get(G_Math, "round")(J.div(J.mul(n, uiScale), 100)))
    def px(n=J.undefined, *_args):
        return J.add(scaleVal(n), "px")
    def fmtTime(ts=J.undefined, *_args):
        ms = J.undefined
        ms = (J.mul(ts, 1000) if J.lt(ts, 1000000000000) else ts)
        if J.truthy(G_isDaily):
            return J.get(moment(ms), "format")("MM/DD")
        return J.get(moment(ms), "format")("h:mm")
    G_describe_indicator("Options Contract Chart Overlay", J.obj(("shortName", "OCC Overlay v1.1")))
    moment = G_library("moment-timezone")
    dteChoice = G_input("Expiry", "0DTE", J.JSArray(["0DTE", "1DTE", "2DTE", "3DTE", "5DTE", "7DTE", "14DTE", "30DTE", "60DTE", "90DTE"]))
    typeChoice = G_input("Type", "Call", J.JSArray(["Call", "Put"]))
    offsetChoice = G_input("ATM Offset", "ATM", J.JSArray(["-10", "-5", "-4", "-3", "-2", "-1", "ATM", "+1", "+2", "+3", "+4", "+5", "+10"]))
    useManual = J.get(G_input, "boolean")("Manual Override", False)
    manualOCC = J.get(G_input, "symbol")("Manual OCC", "", J.obj(("hide_in_legend", True)))
    barsToShow = J.get(G_input, "number")("Bars to Display", 30, J.obj(("min", 5), ("max", 100), ("step", 1)))
    chartHeight = J.get(G_input, "number")("Chart Height (px)", 200, J.obj(("min", 100), ("max", 400), ("step", 25)))
    chartWidth = J.get(G_input, "number")("Chart Width (px)", 520, J.obj(("min", 400), ("max", 800), ("step", 50)))
    scaleChoice = G_input("UI Scale", "100%", J.JSArray(["75%", "100%", "125%", "150%"]))
    showOverlay = J.get(G_input, "boolean")("Show Overlay", True)
    showGreeks = J.get(G_input, "boolean")("Show Greeks Row", False)
    showPosLine = J.get(G_input, "boolean")("Show Position Line", False)
    posPrice = J.get(G_input, "number")("Position Entry $", 0, J.obj(("min", 0), ("max", 99999), ("step", 0.01)))
    posColor = J.get(G_input, "color")("Position Line Color", "#FFD700")
    targetDTE = G_parseInt(dteChoice, 10)
    isCall = J.seq(typeChoice, "Call")
    atmOffset = (0 if J.seq(offsetChoice, "ATM") else G_parseInt(offsetChoice, 10))
    uiScale = G_parseInt(scaleChoice, 10)
    G_scaledChartH = scaleVal(chartHeight)
    G_scaledChartW = scaleVal(chartWidth)
    G_resStr = G_String(J.get(G_constants, "resolution"))
    G_isDaily = (_t1 if J.truthy(_t1 := (_t2 if J.truthy(_t2 := J.seq(G_resStr, "D")) else J.seq(G_resStr, "W"))) else J.seq(G_resStr, "M"))
    callColor = "#00C864"
    putColor = "#DC3232"
    typeColor = (callColor if J.truthy(isCall) else putColor)
    optTypeKey = ("C" if J.truthy(isCall) else "P")
    optTypeLabel = ("Call" if J.truthy(isCall) else "Put")
    def _f3(*_args):
        return G_NaN
    G_paint(J.get(G_close, "map")(_f3), J.obj(("name", "OptChartRef"), ("style", "line"), ("color", "#7BF1A8")))
    ticker = (_t4 if J.truthy(_t4 := (_t5 if J.truthy(_t5 := J.get(G_current, "ticker")) else J.get(G_current, "symbol"))) else "SPY")
    dataLength = J.get(G_close, "length")
    lastIdx = J.sub(dataLength, 1)
    currentPrice = J.get(G_close, lastIdx)
    def padTwo(n=J.undefined, *_args):
        return J.add(("0" if J.lt(n, 10) else ""), J.get(G_Math, "floor")(n))
    def G_fmtP(v=J.undefined, *_args):
        return (J.add("$", J.get(G_Number(v), "toFixed")(2)) if (not J.nullish(v)) else "n/a")
    def G_fmtG(v=J.undefined, *_args):
        return (J.get(G_Number(v), "toFixed")(4) if (not J.nullish(v)) else "n/a")
    selectedExp = None
    expCode = None
    selectedStrike = None
    atmStrike = None
    strikeList = None
    resolveErr = ""
    G_isManualMode = (J.gt(J.get(manualOCC, "length"), 15) if J.truthy(_t6 := (manualOCC if J.truthy(_t7 := useManual) else _t7)) else _t6)
    manualLabel = ""
    if J.truthy(G_isManualMode):
        G_occLen = J.get(manualOCC, "length")
        G_manTicker = J.get(manualOCC, "substring")(0, J.sub(G_occLen, 15))
        G_manExp = J.get(manualOCC, "substring")(J.sub(G_occLen, 15), J.sub(G_occLen, 9))
        G_manType = J.get(manualOCC, "substring")(J.sub(G_occLen, 9), J.sub(G_occLen, 8))
        G_manStrRaw = J.get(manualOCC, "substring")(J.sub(G_occLen, 8))
        G_manStrVal = J.div(G_parseInt(G_manStrRaw, 10), 1000)
        manualLabel = J.add(J.add(J.add(J.add(J.add(J.add(G_manTicker, " $"), G_manStrVal), " "), ("Call" if J.seq(G_manType, "C") else "Put")), " "), G_manExp)
        expCode = G_parseInt(G_manExp, 10)
        selectedStrike = G_manStrVal
    else:
        schedule = None
        schedErr = ""
        try:
            schedule = J.get(G_request, "options_schedule")(ticker)
        except Exception as _e8:
            e = J.catch_value(_e8)
            schedErr = J.get(G_String(e), "substring")(0, 60)
        if ((J.truthy(schedule) and J.truthy(J.get(G_Array, "isArray")(schedule))) and J.gt(J.get(schedule, "length"), 0)):
            bestIdx = 0
            bestDiff = 99999
            ei = 0
            while J.lt(ei, J.get(schedule, "length")):
                if ((J.truthy(J.get(schedule, ei)) and J.truthy(J.get(J.get(schedule, ei), "expiration"))) and (not J.nullish(J.get(J.get(J.get(schedule, ei), "expiration"), "dte")))):
                    G_diff = J.get(G_Math, "abs")(J.sub(J.get(J.get(J.get(schedule, ei), "expiration"), "dte"), targetDTE))
                    if J.lt(G_diff, bestDiff):
                        bestDiff = G_diff
                        bestIdx = ei
                ei = J.inc(ei)
            selectedExp = J.get(schedule, bestIdx)
            if ((J.truthy(selectedExp) and J.truthy(J.get(selectedExp, "expiration"))) and J.truthy(J.get(J.get(selectedExp, "expiration"), "code"))):
                expCode = J.get(J.get(selectedExp, "expiration"), "code")
            if ((J.truthy(selectedExp) and J.truthy(J.get(selectedExp, "strikes"))) and J.gt(J.get(J.get(selectedExp, "strikes"), "length"), 0)):
                strikeList = J.get(selectedExp, "strikes")
                def _f9(a=J.undefined, b=J.undefined, *_args):
                    return J.sub(a, b)
                J.get(strikeList, "sort")(_f9)
                atmIdx = 0
                minDist = J.get(G_Math, "abs")(J.sub(J.get(strikeList, 0), currentPrice))
                si = 1
                while J.lt(si, J.get(strikeList, "length")):
                    G_dist = J.get(G_Math, "abs")(J.sub(J.get(strikeList, si), currentPrice))
                    if J.lt(G_dist, minDist):
                        minDist = G_dist
                        atmIdx = si
                    si = J.inc(si)
                atmStrike = J.get(strikeList, atmIdx)
                targetIdx = J.add(atmIdx, atmOffset)
                targetIdx = J.get(G_Math, "max")(0, J.get(G_Math, "min")(targetIdx, J.sub(J.get(strikeList, "length"), 1)))
                selectedStrike = J.get(strikeList, targetIdx)
            else:
                resolveErr = "No strikes in schedule entry"
        else:
            resolveErr = (_t10 if J.truthy(_t10 := schedErr) else "options_schedule returned empty")
    occSymbol = ""
    contractLabel = ""
    hasContract = False
    effectiveTypeKey = optTypeKey
    effectiveTicker = ticker
    if J.truthy(G_isManualMode):
        occSymbol = manualOCC
        contractLabel = manualLabel
        hasContract = True
        G_occLen2 = J.get(manualOCC, "length")
        effectiveTypeKey = J.get(manualOCC, "substring")(J.sub(G_occLen2, 9), J.sub(G_occLen2, 8))
        effectiveTicker = J.get(manualOCC, "substring")(0, J.sub(G_occLen2, 15))
    elif ((expCode is not None) and (selectedStrike is not None)):
        G_expStr = G_String(expCode)
        G_eYY = J.get(G_expStr, "substring")(0, 2)
        G_eMM = J.get(G_expStr, "substring")(2, 4)
        G_eDD = J.get(G_expStr, "substring")(4, 6)
        G_strikeInt = J.get(G_Math, "round")(J.mul(selectedStrike, 1000))
        G_strikePad = J.get(G_String(G_strikeInt), "padStart")(8, "0")
        occSymbol = J.add(J.add(J.add(J.add(J.add(ticker, G_eYY), G_eMM), G_eDD), optTypeKey), G_strikePad)
        contractLabel = J.add(J.add(J.add(J.add(J.add(J.add(ticker, " $"), selectedStrike), " "), optTypeLabel), " "), expCode)
        hasContract = True
    contract = None
    curLast = None
    curBid = None
    curAsk = None
    curIV = None
    curOI = None
    curDelta = None
    curGamma = None
    curTheta = None
    curVega = None
    curVol = None
    spread = None
    hasOPRA = False
    if (J.truthy(hasContract) and J.truthy(expCode)):
        try:
            G_opraData = J.get(G_request, "options_data_for_expiration")(effectiveTicker, expCode, J.JSArray(["l", "b", "a", "iv", "oi", "gd", "gg", "gt", "gv", "dvol"]))
            if (J.truthy(G_opraData) and J.truthy(J.get(G_opraData, "resultByStrike"))):
                G_sd = (_t11 if J.truthy(_t11 := J.get(J.get(G_opraData, "resultByStrike"), selectedStrike)) else J.get(J.get(G_opraData, "resultByStrike"), G_String(selectedStrike)))
                if (J.truthy(G_sd) and J.truthy(J.get(G_sd, effectiveTypeKey))):
                    contract = J.get(G_sd, effectiveTypeKey)
        except Exception as _e12:
            e_2 = J.catch_value(_e12)
            pass
        if J.truthy(contract):
            curLast = (J.get(contract, "l") if (not J.nullish(J.get(contract, "l"))) else None)
            curBid = (J.get(contract, "b") if (not J.nullish(J.get(contract, "b"))) else None)
            curAsk = (J.get(contract, "a") if (not J.nullish(J.get(contract, "a"))) else None)
            curIV = (J.get(contract, "iv") if (not J.nullish(J.get(contract, "iv"))) else None)
            curOI = (J.get(contract, "oi") if (not J.nullish(J.get(contract, "oi"))) else None)
            curDelta = (J.get(contract, "gd") if (not J.nullish(J.get(contract, "gd"))) else None)
            curGamma = (J.get(contract, "gg") if (not J.nullish(J.get(contract, "gg"))) else None)
            curTheta = (J.get(contract, "gt") if (not J.nullish(J.get(contract, "gt"))) else None)
            curVega = (J.get(contract, "gv") if (not J.nullish(J.get(contract, "gv"))) else None)
            curVol = (J.get(contract, "dvol") if (not J.nullish(J.get(contract, "dvol"))) else None)
            spread = (J.sub(curAsk, curBid) if ((not J.nullish(curBid)) and (not J.nullish(curAsk))) else None)
            hasOPRA = (not J.nullish(curLast))
    histClose = None
    histTime = None
    hasChart = False
    if J.truthy(hasContract):
        try:
            G_h = J.get(G_request, "history")(occSymbol, J.get(G_constants, "resolution"))
            if ((J.truthy(G_h) and J.truthy(J.get(G_h, "close"))) and J.gt(J.get(J.get(G_h, "close"), "length"), 0)):
                histClose = J.get(G_h, "close")
                histTime = (_t13 if J.truthy(_t13 := J.get(G_h, "time")) else None)
                hasChart = True
        except Exception as _e14:
            e_3 = J.catch_value(_e14)
            pass
        if (not J.truthy(hasChart)):
            try:
                G_h2 = J.get(G_request, "history")(J.add("O:", occSymbol), J.get(G_constants, "resolution"))
                if ((J.truthy(G_h2) and J.truthy(J.get(G_h2, "close"))) and J.gt(J.get(J.get(G_h2, "close"), "length"), 0)):
                    histClose = J.get(G_h2, "close")
                    histTime = (_t15 if J.truthy(_t15 := J.get(G_h2, "time")) else None)
                    hasChart = True
            except Exception as _e16:
                e_4 = J.catch_value(_e16)
                pass
    G_chartLabels = J.JSArray([])
    G_lineData = J.JSArray([])
    G_pointColors = J.JSArray([])
    G_posLine = J.JSArray([])
    G_drawPosLine = (hasChart if J.truthy(_t17 := (J.gt(posPrice, 0) if J.truthy(_t18 := showPosLine) else _t18)) else _t17)
    if J.truthy(hasChart):
        G_hLen = J.get(histClose, "length")
        G_chartStart = J.get(G_Math, "max")(0, J.sub(G_hLen, barsToShow))
        i = G_chartStart
        while J.lt(i, G_hLen):
            if (J.truthy(histTime) and (not J.nullish(J.get(histTime, i)))):
                J.get(G_chartLabels, "push")(fmtTime(J.get(histTime, i)))
            else:
                G_barsAgo = J.sub(J.sub(G_hLen, i), 1)
                J.get(G_chartLabels, "push")(("Now" if J.seq(G_barsAgo, 0) else J.add("-", G_barsAgo)))
            G_val = (J.get(histClose, i) if ((not J.nullish(J.get(histClose, i))) and (not J.truthy(G_isNaN(J.get(histClose, i))))) else 0)
            J.get(G_lineData, "push")(G_parseFloat(J.get(G_Number(G_val), "toFixed")(4)))
            if J.truthy(G_drawPosLine):
                J.get(G_posLine, "push")(posPrice)
            if (J.gt(i, G_chartStart) and (not J.nullish(J.get(histClose, J.sub(i, 1))))):
                if J.gt(G_val, J.get(histClose, J.sub(i, 1))):
                    J.get(G_pointColors, "push")("#00C864")
                elif J.lt(G_val, J.get(histClose, J.sub(i, 1))):
                    J.get(G_pointColors, "push")("#DC3232")
                else:
                    J.get(G_pointColors, "push")("#888888")
            else:
                J.get(G_pointColors, "push")("#888888")
            i = J.inc(i)
    G_lastVal = (J.get(G_lineData, J.sub(J.get(G_lineData, "length"), 1)) if J.gt(J.get(G_lineData, "length"), 0) else 0)
    G_prevVal = (J.get(G_lineData, J.sub(J.get(G_lineData, "length"), 2)) if J.gt(J.get(G_lineData, "length"), 1) else G_lastVal)
    G_lineColor = ("#00C864" if J.gt(G_lastVal, G_prevVal) else ("#DC3232" if J.lt(G_lastVal, G_prevVal) else "#aaaaaa"))
    G_hudRows = J.JSArray([])
    if (not J.truthy(hasContract)):
        J.get(G_hudRows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", J.add(J.add("\ud83d\udcca OptChart — ", ticker), " — \ud83d\udd34 No Contract")), ("color", "#ffffff"), ("textAlign", "center"), ("fontWeight", "bold"), ("background", "#CC0000"), ("fontSize", px(13)), ("padding", px(5)))]))))
        J.get(G_hudRows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", (_t19 if J.truthy(_t19 := resolveErr) else "Could not resolve expiration/strike")), ("color", "#FF6600"), ("textAlign", "center"), ("fontWeight", "normal"), ("background", "#1a1a2e"), ("fontSize", px(11)), ("padding", px(6)))]))))
    else:
        G_srcTag = ("\ud83d\udfe2 LIVE" if J.truthy(hasChart) else ("\ud83d\udfe1 Snapshot" if J.truthy(hasOPRA) else "\ud83d\udd34 No Data"))
        G_headerBg = ("#5D0EC0" if J.truthy(hasChart) else ("#806600" if J.truthy(hasOPRA) else "#CC0000"))
        expInfo = ""
        actualDTE = ""
        if (J.truthy(selectedExp) and J.truthy(J.get(selectedExp, "expiration"))):
            G_exp = J.get(selectedExp, "expiration")
            G_schedType = ("Wkly" if J.seq(J.get(G_exp, "schedule"), "W") else ("Mthly" if J.seq(J.get(G_exp, "schedule"), "M") else (_t20 if J.truthy(_t20 := J.get(G_exp, "schedule")) else "")))
            expInfo = J.add(J.add(J.add(J.add(G_schedType, " "), (_t21 if J.truthy(_t21 := J.get(G_exp, "month")) else "")), " "), (_t22 if J.truthy(_t22 := J.get(G_exp, "day")) else ""))
            actualDTE = (J.get(G_exp, "dte") if (not J.nullish(J.get(G_exp, "dte"))) else "?")
        J.get(G_hudRows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", J.add(J.add(J.add("[Option Contract]  ", contractLabel), " — "), G_srcTag)), ("color", "#FFE700"), ("textAlign", "center"), ("fontWeight", "bold"), ("background", G_headerBg), ("fontSize", px(14)), ("padding", px(5)))]))))
        atmInfo = ""
        if J.truthy(G_isManualMode):
            atmInfo = J.add("MANUAL | ", manualOCC)
        else:
            G_offsetLabel = ("(ATM)" if J.seq(atmOffset, 0) else J.add(J.add(J.add("(", ("+" if J.gt(atmOffset, 0) else "")), atmOffset), ")"))
            atmInfo = J.add(J.add(J.add(J.add(J.add(J.add(J.add(J.add(J.add("ATM: $", (atmStrike if (not J.nullish(atmStrike)) else "n/a")), " | Selected: $"), selectedStrike), " "), G_offsetLabel), " | DTE: "), actualDTE), " | "), expInfo)
        J.get(G_hudRows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", atmInfo), ("color", ("#FFA500" if J.truthy(G_isManualMode) else "#46ECD5")), ("textAlign", "center"), ("fontWeight", "normal"), ("background", "#0a1a2e"), ("fontSize", px(12)), ("padding", px(3)))]))))
        if J.truthy(hasOPRA):
            J.get(G_hudRows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", J.add(J.add(J.add(J.add(J.add(J.add(J.add("Last: ", G_fmtP(curLast)), " | Bid: "), G_fmtP(curBid)), " | Ask: "), G_fmtP(curAsk)), " | Spread: "), (J.add("$", J.get(spread, "toFixed")(2)) if (not J.nullish(spread)) else "n/a"))), ("color", "#ffffff"), ("textAlign", "center"), ("fontWeight", "normal"), ("background", "#1a1a2e"), ("fontSize", px(12)), ("padding", px(4)))]))))
        elif J.truthy(hasChart):
            G_lastVal2 = (J.get(G_lineData, J.sub(J.get(G_lineData, "length"), 1)) if J.gt(J.get(G_lineData, "length"), 0) else 0)
            J.get(G_hudRows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", J.add("Last: ", G_fmtP(G_lastVal2))), ("color", "#ffffff"), ("textAlign", "center"), ("fontWeight", "normal"), ("background", "#1a1a2e"), ("fontSize", px(11)), ("padding", px(4)))]))))
        if (J.truthy(showGreeks) and J.truthy(hasOPRA)):
            J.get(G_hudRows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", J.add(J.add(J.add(J.add(J.add(J.add(J.add(J.add(J.add("Δ ", G_fmtG(curDelta)), " | Γ "), G_fmtG(curGamma)), " | Θ "), G_fmtG(curTheta)), " | V "), G_fmtG(curVega)), " | IV "), (J.add(J.get(G_Number(curIV), "toFixed")(1), "%") if (not J.nullish(curIV)) else "n/a"))), ("color", "#FFD700"), ("textAlign", "center"), ("fontWeight", "bold"), ("background", "#101010"), ("fontSize", px(11)), ("padding", px(4)))]))))
        if J.truthy(hasChart):
            G_datasets = J.JSArray([J.obj(("label", "Last"), ("data", G_lineData), ("borderColor", G_lineColor), ("backgroundColor", "rgba(0,0,0,0)"), ("pointBackgroundColor", G_pointColors), ("pointBorderColor", G_pointColors), ("borderWidth", scaleVal(1)))])
            if (J.truthy(G_drawPosLine) and J.gt(J.get(G_posLine, "length"), 0)):
                J.get(G_datasets, "push")(J.obj(("label", J.add("Entry $", J.get(posPrice, "toFixed")(2))), ("data", G_posLine), ("borderColor", posColor), ("backgroundColor", "rgba(0,0,0,0)"), ("borderWidth", 1), ("borderDash", J.JSArray([6, 3])), ("pointRadius", 0), ("pointHoverRadius", 0)))
            J.get(G_hudRows, "push")(J.obj(("cells", J.JSArray([J.obj(("chart", J.obj(("width", J.add(G_scaledChartW, "px")), ("height", J.add(G_scaledChartH, "px")), ("type", "line"), ("options", J.obj(("indexAxis", "x"), ("responsive", True), ("maintainAspectRatio", False), ("plugins", J.obj(("legend", J.obj(("display", G_drawPosLine), ("position", "top"), ("labels", J.obj(("color", "#aaa"), ("font", J.obj(("size", scaleVal(8)))), ("boxWidth", scaleVal(12)))))), ("title", J.obj(("display", False))))), ("scales", J.obj(("x", J.obj(("title", J.obj(("display", False))), ("ticks", J.obj(("color", "#ffffff"), ("font", J.obj(("size", scaleVal(8)))), ("maxRotation", 45), ("autoSkip", True), ("maxTicksLimit", 10))), ("grid", J.obj(("color", "#4A4A4A"))))), ("y", J.obj(("title", J.obj(("display", True), ("text", "Last ($)"), ("color", "#aaa"), ("font", J.obj(("size", scaleVal(10)))))), ("ticks", J.obj(("color", "#ffffff"), ("font", J.obj(("size", scaleVal(9)))))), ("grid", J.obj(("color", "#4A4A4A"))))))), ("elements", J.obj(("point", J.obj(("radius", scaleVal(2)), ("hoverRadius", scaleVal(4)))), ("line", J.obj(("tension", 0.3))))))), ("data", J.obj(("labels", G_chartLabels), ("datasets", G_datasets))))))]))))
        elif (not J.truthy(hasOPRA)):
            J.get(G_hudRows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", J.add("No chart data for ", occSymbol)), ("color", "#FF6600"), ("textAlign", "center"), ("fontWeight", "normal"), ("background", "#1a1a2e"), ("fontSize", px(11)), ("padding", px(6)))]))))
        G_effectiveIsCall = J.seq(effectiveTypeKey, "C")
        G_moneyness = ("ITM" if J.gt(currentPrice, selectedStrike) else ("OTM" if J.lt(currentPrice, selectedStrike) else "ATM"))
        G_intrinsic = (J.get(G_Math, "max")(J.sub(currentPrice, selectedStrike), 0) if J.truthy(G_effectiveIsCall) else J.get(G_Math, "max")(J.sub(selectedStrike, currentPrice), 0))
        J.get(G_hudRows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", J.add(J.add(J.add(J.add(J.add(J.add(J.add(J.add(J.add(J.add(G_moneyness, " | Intrinsic: $"), J.get(G_intrinsic, "toFixed")(2)), " | OI: "), (J.get(G_Math, "round")(curOI) if (not J.nullish(curOI)) else "n/a")), " | Vol: "), (J.get(G_Math, "round")(curVol) if (not J.nullish(curVol)) else "n/a")), " | "), effectiveTicker), ": $"), J.get(currentPrice, "toFixed")(2))), ("color", "#73FF00"), ("textAlign", "center"), ("fontWeight", "bold"), ("background", "#1F1F1F"), ("fontSize", px(12)), ("padding", px(4)))]))))
    G_effectiveColor = (callColor if J.seq(effectiveTypeKey, "C") else putColor)
    G_finalBorder = ((G_effectiveColor if J.truthy(hasChart) else ("#FFD700" if J.truthy(hasOPRA) else "#CC0000")) if J.truthy(hasContract) else "#CC0000")
    G_paint_overlay("OptContractChart", J.obj(("position", "bottom_left"), ("order", "above_all"), ("offset_x", 50), ("offset_y", 0)), (J.obj(("background", "#0d0d0d"), ("border", J.add(J.add(scaleVal(2), "px solid "), G_finalBorder)), ("borderRadius", px(6)), ("padding", "0px"), ("rows", G_hudRows)) if J.truthy(showOverlay) else J.obj(("fontSize", 1), ("border", "none"), ("background", "transparent"), ("rows", J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", ""), ("padding", "0px"), ("background", "transparent"))])))])))))


register_store_indicator(
    script,
    name='options_contract_chart_overlay_TS',
    title='Options Contract Chart Overlay',
    developer='Rock Regan',
    url='https://trendspider.com/trading-tools-store/indicators/69d59d-options-contract-chart-overlay/',
    position='price',
    inputs=[{'id': 'expiry', 'title': 'Expiry', 'type': 'select_wide', 'default': '0DTE', 'options': ['0DTE', '1DTE', '2DTE', '3DTE', '5DTE', '7DTE', '14DTE', '30DTE', '60DTE', '90DTE']}, {'id': 'type', 'title': 'Type', 'type': 'select_wide', 'default': 'Call', 'options': ['Call', 'Put']}, {'id': 'atm_offset', 'title': 'ATM Offset', 'type': 'select_wide', 'default': 'ATM', 'options': ['-10', '-5', '-4', '-3', '-2', '-1', 'ATM', '+1', '+2', '+3', '+4', '+5', '+10']}, {'id': 'manual_override', 'title': 'Manual Override', 'type': 'boolean', 'default': False}, {'id': 'sym-manual_occ', 'title': 'Manual OCC', 'type': 'symbol-search', 'default': ''}, {'id': 'bars_to_display', 'title': 'Bars to Display', 'type': 'number', 'default': 30}, {'id': 'chart_height__px_', 'title': 'Chart Height (px)', 'type': 'number', 'default': 200}, {'id': 'chart_width__px_', 'title': 'Chart Width (px)', 'type': 'number', 'default': 520}, {'id': 'ui_scale', 'title': 'UI Scale', 'type': 'select_wide', 'default': '100%', 'options': ['75%', '100%', '125%', '150%']}, {'id': 'show_overlay', 'title': 'Show Overlay', 'type': 'boolean', 'default': True}, {'id': 'show_greeks_row', 'title': 'Show Greeks Row', 'type': 'boolean', 'default': False}, {'id': 'show_position_line', 'title': 'Show Position Line', 'type': 'boolean', 'default': False}, {'id': 'position_entry__', 'title': 'Position Entry $', 'type': 'number', 'default': 0}, {'id': 'position_line_color', 'title': 'Position Line Color', 'type': 'color', 'default': '#FFD700'}],
    outputs=['optchartref'],
    signals=[],
    requires=['history', 'options_data_for_expiration', 'options_schedule'],
    parity='exact',
)
