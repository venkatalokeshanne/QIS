"""
Underlying Chart Overlay -- TrendSpider store indicator by Rock Regan.

Registered as "underlying_chart_overlay_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/69e024-underlying-chart-overlay/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_NaN = G["NaN"]
    G_Number = G["Number"]
    G_String = G["String"]
    G_barsAgo = G["barsAgo"]
    G_borderColor = G["borderColor"]
    G_cData = G["cData"]
    G_callColor = G["callColor"]
    G_chartH = G["chartH"]
    G_chartLabels = G["chartLabels"]
    G_chartStart = G["chartStart"]
    G_chartSymbol = G["chartSymbol"]
    G_chartW = G["chartW"]
    G_close = G["close"]
    G_constants = G["constants"]
    G_contractPrice = G["contractPrice"]
    G_current = G["current"]
    G_dataLength = G["dataLength"]
    G_datasets = G["datasets"]
    G_describe_indicator = G["describe_indicator"]
    G_expInt = G["expInt"]
    G_extrinsic = G["extrinsic"]
    G_fmtG = G["fmtG"]
    G_fmtP = G["fmtP"]
    G_fmtTime = G["fmtTime"]
    G_fs = G["fs"]
    G_hChart = G["hChart"]
    G_hComp = G["hComp"]
    G_hLen = G["hLen"]
    G_hLen2 = G["hLen2"]
    G_hUnd = G["hUnd"]
    G_headerBg = G["headerBg"]
    G_headerLabel = G["headerLabel"]
    G_hudRows = G["hudRows"]
    G_input = G["input"]
    G_isCompareMode = G["isCompareMode"]
    G_isDaily = G["isDaily"]
    G_isNaN = G["isNaN"]
    G_lastIdx = G["lastIdx"]
    G_lastVal = G["lastVal"]
    G_library = G["library"]
    G_lineColor = G["lineColor"]
    G_lineData = G["lineData"]
    G_moneyColor = G["moneyColor"]
    G_opraData = G["opraData"]
    G_paint = G["paint"]
    G_paint_overlay = G["paint_overlay"]
    G_parseFloat = G["parseFloat"]
    G_parseInt = G["parseInt"]
    G_pointColors = G["pointColors"]
    G_prevVal = G["prevVal"]
    G_putColor = G["putColor"]
    G_rawSymbol = G["rawSymbol"]
    G_request = G["request"]
    G_resStr = G["resStr"]
    G_scanStart = G["scanStart"]
    G_sd = G["sd"]
    G_showStrikeOnChart = G["showStrikeOnChart"]
    G_srcTag = G["srcTag"]
    G_strikeLine = G["strikeLine"]
    G_strikeRaw = G["strikeRaw"]
    G_suffixStart = G["suffixStart"]
    G_val = G["val"]
    underlying = J.undefined
    parsedExpiry = J.undefined
    parsedType = J.undefined
    parsedStrike = J.undefined
    parsedTypeLabel = J.undefined
    parseSuccess = J.undefined
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
    undCurrent = J.undefined
    hasUnderlying = J.undefined
    histClose = J.undefined
    histHigh = J.undefined
    histLow = J.undefined
    histTime = J.undefined
    hasChart = J.undefined
    chartCurrent = J.undefined
    i = J.undefined
    distToStrike = J.undefined
    distPct = J.undefined
    moneyness = J.undefined
    intrinsic = J.undefined
    priceText = J.undefined
    chartHi = J.undefined
    chartLo = J.undefined
    j = J.undefined
    def scaleVal(n=J.undefined, *_args):
        return J.get(G_Math, "max")(1, J.get(G_Math, "round")(J.div(J.mul(n, uiScale), 100)))
    def px(n=J.undefined, *_args):
        return J.add(scaleVal(n), "px")
    G_describe_indicator("Underlying Chart Overlay", J.obj(("shortName", "\ud83d\udcc8 UndChart v1.0")))
    moment = G_library("moment-timezone")
    barsToShow = J.get(G_input, "number")("Bars to Display", 30, J.obj(("min", 5), ("max", 100), ("step", 1)))
    uiScale = J.get(G_input, "number")("UI Scale (%)", 100, J.obj(("min", 50), ("max", 150), ("step", 5)))
    showOverlay = J.get(G_input, "boolean")("Show Overlay", True)
    showGreeks = J.get(G_input, "boolean")("Show Greeks Row", False)
    showStrikeLine = J.get(G_input, "boolean")("Show Strike Line on Chart", True)
    useCompare = J.get(G_input, "boolean")("Use Compare Symbol", False)
    compareSymbol = J.get(G_input, "symbol")("Compare Symbol", "SPY")
    G_chartW = scaleVal(520)
    G_chartH = scaleVal(200)
    G_fs = J.obj(("hdr", px(14)), ("row", px(12)), ("sm", px(11)), ("xs", px(10)), ("chart", scaleVal(9)))
    def _f1(*_args):
        return G_NaN
    G_paint(J.get(G_close, "map")(_f1), J.obj(("name", "UndChartRef"), ("style", "line"), ("color", "white")))
    G_dataLength = J.get(G_close, "length")
    G_lastIdx = J.sub(G_dataLength, 1)
    G_contractPrice = J.get(G_close, G_lastIdx)
    def G_padTwo(n=J.undefined, *_args):
        return J.add(("0" if J.lt(n, 10) else ""), J.get(G_Math, "floor")(n))
    G_resStr = G_String(J.get(G_constants, "resolution"))
    G_isDaily = (_t2 if J.truthy(_t2 := (_t3 if J.truthy(_t3 := J.seq(G_resStr, "D")) else J.seq(G_resStr, "W"))) else J.seq(G_resStr, "M"))
    def G_fmtTime(ts=J.undefined, *_args):
        ms = J.undefined
        if (J.nullish(ts)):
            return ""
        ms = (J.mul(ts, 1000) if J.lt(ts, 1000000000000) else ts)
        if J.truthy(G_isDaily):
            return J.get(moment(ms), "format")("MM/DD")
        return J.get(moment(ms), "format")("HH:mm")
    G_rawSymbol = (_t4 if J.truthy(_t4 := (_t5 if J.truthy(_t5 := J.get(G_current, "ticker")) else J.get(G_current, "symbol"))) else "")
    underlying = ""
    parsedStrike = 0
    parsedType = ""
    parsedTypeLabel = ""
    parsedExpiry = ""
    parseSuccess = False
    if J.gt(J.get(G_rawSymbol, "length"), 15):
        G_suffixStart = J.sub(J.get(G_rawSymbol, "length"), 15)
        underlying = J.get(G_rawSymbol, "substring")(0, G_suffixStart)
        parsedExpiry = J.get(G_rawSymbol, "substring")(G_suffixStart, J.add(G_suffixStart, 6))
        parsedType = J.get(G_rawSymbol, "substring")(J.add(G_suffixStart, 6), J.add(G_suffixStart, 7))
        G_strikeRaw = J.get(G_rawSymbol, "substring")(J.add(G_suffixStart, 7), J.add(G_suffixStart, 15))
        parsedStrike = J.div(G_parseInt(G_strikeRaw, 10), 1000)
        parsedTypeLabel = ("Call" if J.seq(parsedType, "C") else "Put")
        if (((J.gt(J.get(underlying, "length"), 0) and J.le(J.get(underlying, "length"), 6)) and (J.seq(parsedType, "C") or J.seq(parsedType, "P"))) and J.gt(parsedStrike, 0)):
            parseSuccess = True
    if (not J.truthy(parseSuccess)):
        underlying = G_rawSymbol
    G_chartSymbol = (compareSymbol if (J.truthy(useCompare) and J.truthy(compareSymbol)) else underlying)
    G_isCompareMode = (J.sne(G_chartSymbol, underlying) if J.truthy(_t6 := (compareSymbol if J.truthy(_t7 := useCompare) else _t7)) else _t6)
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
    if J.truthy(parseSuccess):
        try:
            G_expInt = G_parseInt(parsedExpiry, 10)
            G_opraData = J.get(G_request, "options_data_for_expiration")(underlying, G_expInt, J.JSArray(["l", "b", "a", "iv", "oi", "gd", "gg", "gt", "gv", "dvol"]))
            if (J.truthy(G_opraData) and J.truthy(J.get(G_opraData, "resultByStrike"))):
                G_sd = (_t8 if J.truthy(_t8 := J.get(J.get(G_opraData, "resultByStrike"), parsedStrike)) else J.get(J.get(G_opraData, "resultByStrike"), G_String(parsedStrike)))
                if (J.truthy(G_sd) and J.truthy(J.get(G_sd, parsedType))):
                    G_cData = J.get(G_sd, parsedType)
                    curLast = J.get(G_cData, "l")
                    curBid = J.get(G_cData, "b")
                    curAsk = J.get(G_cData, "a")
                    curIV = J.get(G_cData, "iv")
                    curOI = J.get(G_cData, "oi")
                    curDelta = J.get(G_cData, "gd")
                    curGamma = J.get(G_cData, "gg")
                    curTheta = J.get(G_cData, "gt")
                    curVega = J.get(G_cData, "gv")
                    curVol = J.get(G_cData, "dvol")
                    spread = (J.sub(curAsk, curBid) if ((not J.nullish(curBid)) and (not J.nullish(curAsk))) else None)
                    hasOPRA = (not J.nullish(curLast))
        except Exception as _e9:
            e = J.catch_value(_e9)
            pass
    undCurrent = None
    hasUnderlying = False
    if J.gt(J.get(underlying, "length"), 0):
        try:
            G_hUnd = J.get(G_request, "history")(underlying, J.get(G_constants, "resolution"))
            if ((J.truthy(G_hUnd) and J.truthy(J.get(G_hUnd, "close"))) and J.gt(J.get(J.get(G_hUnd, "close"), "length"), 0)):
                undCurrent = J.get(J.get(G_hUnd, "close"), J.sub(J.get(J.get(G_hUnd, "close"), "length"), 1))
                hasUnderlying = True
        except Exception as _e10:
            e_2 = J.catch_value(_e10)
            pass
    histClose = None
    histHigh = None
    histLow = None
    histTime = None
    hasChart = False
    chartCurrent = None
    if ((not J.truthy(G_isCompareMode)) and J.truthy(hasUnderlying)):
        try:
            G_hChart = J.get(G_request, "history")(underlying, J.get(G_constants, "resolution"))
            if ((J.truthy(G_hChart) and J.truthy(J.get(G_hChart, "close"))) and J.gt(J.get(J.get(G_hChart, "close"), "length"), 0)):
                histClose = J.get(G_hChart, "close")
                histHigh = (_t11 if J.truthy(_t11 := J.get(G_hChart, "high")) else None)
                histLow = (_t12 if J.truthy(_t12 := J.get(G_hChart, "low")) else None)
                histTime = (_t13 if J.truthy(_t13 := J.get(G_hChart, "time")) else None)
                hasChart = True
                chartCurrent = J.get(histClose, J.sub(J.get(histClose, "length"), 1))
        except Exception as _e14:
            e_3 = J.catch_value(_e14)
            pass
    elif J.truthy(G_isCompareMode):
        try:
            G_hComp = J.get(G_request, "history")(compareSymbol, J.get(G_constants, "resolution"))
            if ((J.truthy(G_hComp) and J.truthy(J.get(G_hComp, "close"))) and J.gt(J.get(J.get(G_hComp, "close"), "length"), 0)):
                histClose = J.get(G_hComp, "close")
                histHigh = (_t15 if J.truthy(_t15 := J.get(G_hComp, "high")) else None)
                histLow = (_t16 if J.truthy(_t16 := J.get(G_hComp, "low")) else None)
                histTime = (_t17 if J.truthy(_t17 := J.get(G_hComp, "time")) else None)
                hasChart = True
                chartCurrent = J.get(histClose, J.sub(J.get(histClose, "length"), 1))
        except Exception as _e18:
            e_4 = J.catch_value(_e18)
            pass
    G_chartLabels = J.JSArray([])
    G_lineData = J.JSArray([])
    G_pointColors = J.JSArray([])
    G_strikeLine = J.JSArray([])
    G_showStrikeOnChart = ((not J.truthy(G_isCompareMode)) if J.truthy(_t19 := (parseSuccess if J.truthy(_t20 := showStrikeLine) else _t20)) else _t19)
    if J.truthy(hasChart):
        G_hLen = J.get(histClose, "length")
        G_chartStart = J.get(G_Math, "max")(0, J.sub(G_hLen, barsToShow))
        i = G_chartStart
        while J.lt(i, G_hLen):
            if (J.truthy(histTime) and (not J.nullish(J.get(histTime, i)))):
                J.get(G_chartLabels, "push")(G_fmtTime(J.get(histTime, i)))
            else:
                G_barsAgo = J.sub(J.sub(G_hLen, i), 1)
                J.get(G_chartLabels, "push")(("Now" if J.seq(G_barsAgo, 0) else J.add("-", G_barsAgo)))
            G_val = (J.get(histClose, i) if ((not J.nullish(J.get(histClose, i))) and (not J.truthy(G_isNaN(J.get(histClose, i))))) else 0)
            J.get(G_lineData, "push")(G_parseFloat(J.get(G_Number(G_val), "toFixed")(2)))
            if J.truthy(G_showStrikeOnChart):
                J.get(G_strikeLine, "push")(parsedStrike)
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
    moneyness = "n/a"
    intrinsic = 0
    distToStrike = 0
    distPct = 0
    if ((not J.nullish(undCurrent)) and J.truthy(parseSuccess)):
        distToStrike = J.sub(undCurrent, parsedStrike)
        distPct = J.mul(J.div(distToStrike, parsedStrike), 100)
        if J.seq(parsedType, "C"):
            moneyness = ("ITM" if J.gt(undCurrent, parsedStrike) else ("OTM" if J.lt(undCurrent, parsedStrike) else "ATM"))
            intrinsic = J.get(G_Math, "max")(J.sub(undCurrent, parsedStrike), 0)
        else:
            moneyness = ("ITM" if J.lt(undCurrent, parsedStrike) else ("OTM" if J.gt(undCurrent, parsedStrike) else "ATM"))
            intrinsic = J.get(G_Math, "max")(J.sub(parsedStrike, undCurrent), 0)
    G_extrinsic = (J.get(G_Math, "max")(J.sub(G_contractPrice, intrinsic), 0) if ((not J.nullish(G_contractPrice)) and (not J.nullish(intrinsic))) else 0)
    def G_fmtP(v=J.undefined, *_args):
        return (J.add("$", J.get(G_Number(v), "toFixed")(2)) if (not J.nullish(v)) else "n/a")
    def G_fmtG(v=J.undefined, *_args):
        return (J.get(G_Number(v), "toFixed")(4) if (not J.nullish(v)) else "n/a")
    G_hudRows = J.JSArray([])
    G_srcTag = ("\ud83d\udfe2 LIVE" if J.truthy(hasChart) else "\ud83d\udd34 No Data")
    G_callColor = "#006633"
    G_putColor = "#660000"
    G_headerBg = ("MediumBlue" if J.truthy(G_isCompareMode) else ((G_callColor if J.seq(parsedType, "C") else G_putColor) if J.truthy(hasChart) else "#CC0000"))
    G_borderColor = ("MediumBlue" if J.truthy(G_isCompareMode) else ("#A6ACAF" if J.truthy(hasChart) else "#CC0000"))
    G_headerLabel = (J.add(J.add(J.add("[Compare MODE] ", G_chartSymbol), "   "), G_srcTag) if J.truthy(G_isCompareMode) else J.add(J.add(J.add("[Underlying Ticker] ", underlying), "   "), G_srcTag))
    J.get(G_hudRows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", G_headerLabel), ("color", "#FFDF20"), ("textAlign", "center"), ("fontWeight", "bold"), ("background", G_headerBg), ("fontSize", J.get(G_fs, "hdr")), ("padding", px(5)))]))))
    if J.truthy(parseSuccess):
        J.get(G_hudRows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", J.add(J.add(J.add(J.add(J.add(J.add(parsedTypeLabel, " $"), parsedStrike), " | Exp: "), parsedExpiry), " | Contract: "), G_fmtP(G_contractPrice))), ("color", "#cccccc"), ("textAlign", "center"), ("fontWeight", "normal"), ("background", ("#178236" if J.seq(parsedType, "C") else "#660000")), ("fontSize", J.get(G_fs, "row")), ("padding", px(4)))]))))
    if (not J.nullish(undCurrent)):
        priceText = J.add(J.add(underlying, ": "), G_fmtP(undCurrent))
        if (J.truthy(G_isCompareMode) and (not J.nullish(chartCurrent))):
            priceText = J.add(J.add(J.add(J.add(priceText, " | "), G_chartSymbol), ": "), G_fmtP(chartCurrent))
        chartHi = None
        chartLo = None
        if (J.truthy(histHigh) and J.gt(J.get(histHigh, "length"), 0)):
            G_hLen2 = J.get(histHigh, "length")
            G_scanStart = J.get(G_Math, "max")(0, J.sub(G_hLen2, barsToShow))
            chartHi = J.get(histHigh, G_scanStart)
            chartLo = (J.get(histLow, G_scanStart) if J.truthy(histLow) else None)
            j = G_scanStart
            while J.lt(j, G_hLen2):
                if ((not J.nullish(J.get(histHigh, j))) and J.gt(J.get(histHigh, j), chartHi)):
                    chartHi = J.get(histHigh, j)
                if ((J.truthy(histLow) and (not J.nullish(J.get(histLow, j)))) and ((J.nullish(chartLo)) or J.lt(J.get(histLow, j), chartLo))):
                    chartLo = J.get(histLow, j)
                j = J.inc(j)
        if ((not J.truthy(G_isCompareMode)) and (not J.nullish(chartHi))):
            priceText = J.add(J.add(J.add(J.add(priceText, " | Hi: "), G_fmtP(chartHi)), " Lo: "), G_fmtP(chartLo))
        J.get(G_hudRows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", priceText), ("color", "#ffffff"), ("textAlign", "center"), ("fontWeight", "bold"), ("background", "#1a1a2e"), ("fontSize", J.get(G_fs, "row")), ("padding", px(4)))]))))
        if (J.truthy(G_isCompareMode) and (not J.nullish(chartHi))):
            J.get(G_hudRows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", J.add(J.add(J.add(J.add(G_chartSymbol, " Hi: "), G_fmtP(chartHi)), " | Lo: "), G_fmtP(chartLo))), ("color", "#aaaaaa"), ("textAlign", "center"), ("fontWeight", "normal"), ("background", "#1a1a2e"), ("fontSize", J.get(G_fs, "xs")), ("padding", px(3)))]))))
    if J.truthy(hasOPRA):
        J.get(G_hudRows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", J.add(J.add(J.add(J.add(J.add(J.add(J.add("OPRA → Last: ", G_fmtP(curLast)), " | Bid: "), G_fmtP(curBid)), " | Ask: "), G_fmtP(curAsk)), " | Spread: "), (J.add("$", J.get(spread, "toFixed")(2)) if (not J.nullish(spread)) else "n/a"))), ("color", "#aaaaaa"), ("textAlign", "center"), ("fontWeight", "normal"), ("background", "#101010"), ("fontSize", J.get(G_fs, "xs")), ("padding", px(3)))]))))
    if (J.truthy(showGreeks) and J.truthy(hasOPRA)):
        J.get(G_hudRows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", J.add(J.add(J.add(J.add(J.add(J.add(J.add(J.add(J.add("Δ ", G_fmtG(curDelta)), " | Γ "), G_fmtG(curGamma)), " | Θ "), G_fmtG(curTheta)), " | V "), G_fmtG(curVega)), " | IV "), (J.add(J.get(G_Number(curIV), "toFixed")(1), "%") if (not J.nullish(curIV)) else "n/a"))), ("color", "#FFD700"), ("textAlign", "center"), ("fontWeight", "bold"), ("background", "#101010"), ("fontSize", J.get(G_fs, "sm")), ("padding", px(4)))]))))
    if J.truthy(hasChart):
        G_datasets = J.JSArray([J.obj(("label", G_chartSymbol), ("data", G_lineData), ("borderColor", G_lineColor), ("backgroundColor", "rgba(0,0,0,0)"), ("pointBackgroundColor", G_pointColors), ("pointBorderColor", G_pointColors), ("borderWidth", 2))])
        if (J.truthy(G_showStrikeOnChart) and J.gt(J.get(G_strikeLine, "length"), 0)):
            J.get(G_datasets, "push")(J.obj(("label", J.add("Strike $", parsedStrike)), ("data", G_strikeLine), ("borderColor", "#FFD700"), ("backgroundColor", "rgba(0,0,0,0)"), ("borderWidth", 1), ("borderDash", J.JSArray([6, 3])), ("pointRadius", 0), ("pointHoverRadius", 0)))
        J.get(G_hudRows, "push")(J.obj(("cells", J.JSArray([J.obj(("chart", J.obj(("width", J.add(G_chartW, "px")), ("height", J.add(G_chartH, "px")), ("type", "line"), ("options", J.obj(("indexAxis", "x"), ("responsive", True), ("maintainAspectRatio", False), ("plugins", J.obj(("legend", J.obj(("display", G_showStrikeOnChart), ("position", "top"), ("labels", J.obj(("color", "#aaa"), ("font", J.obj(("size", J.get(G_fs, "chart")))), ("boxWidth", scaleVal(12)))))), ("title", J.obj(("display", False))))), ("scales", J.obj(("x", J.obj(("title", J.obj(("display", True), ("text", "Time"), ("color", "#aaa"), ("font", J.obj(("size", J.get(G_fs, "chart")))))), ("ticks", J.obj(("color", "#ffffff"), ("font", J.obj(("size", J.get(G_fs, "chart")))), ("maxRotation", 45), ("minRotation", 0), ("autoSkip", True), ("maxTicksLimit", 10))), ("grid", J.obj(("color", "#4A4A4A"))))), ("y", J.obj(("title", J.obj(("display", True), ("text", J.add(G_chartSymbol, " ($)")), ("color", "#aaa"), ("font", J.obj(("size", J.get(G_fs, "chart")))))), ("ticks", J.obj(("color", "#ffffff"), ("font", J.obj(("size", J.get(G_fs, "chart")))))), ("grid", J.obj(("color", "#4A4A4A"))))))), ("elements", J.obj(("point", J.obj(("radius", scaleVal(2)), ("hoverRadius", scaleVal(4)))), ("line", J.obj(("tension", 0.3))))))), ("data", J.obj(("labels", G_chartLabels), ("datasets", G_datasets))))))]))))
    else:
        J.get(G_hudRows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", (J.add(J.add("Could not load ", G_chartSymbol), " history") if J.gt(J.get(G_chartSymbol, "length"), 0) else J.add("Could not parse underlying from: ", G_rawSymbol))), ("color", "#FF6600"), ("textAlign", "center"), ("fontWeight", "normal"), ("background", "#1a1a2e"), ("fontSize", J.get(G_fs, "sm")), ("padding", px(6)))]))))
    G_moneyColor = ("#00C864" if J.seq(moneyness, "ITM") else ("#DC3232" if J.seq(moneyness, "OTM") else "#FFD700"))
    J.get(G_hudRows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", J.add(J.add(J.add(J.add(J.add(J.add(J.add(J.add(J.add(J.add(J.add(J.add(J.add(J.add(moneyness, " | Dist: "), ("+" if J.ge(distToStrike, 0) else "")), J.get(distToStrike, "toFixed")(2)), " ("), ("+" if J.ge(distPct, 0) else "")), J.get(distPct, "toFixed")(2)), "%) | Intr: $"), J.get(intrinsic, "toFixed")(2)), " | Extr: $"), J.get(G_extrinsic, "toFixed")(2)), " | OI: "), (J.get(G_Math, "round")(curOI) if (not J.nullish(curOI)) else "n/a")), " | Vol: "), (J.get(G_Math, "round")(curVol) if (not J.nullish(curVol)) else "n/a"))), ("color", G_moneyColor), ("textAlign", "center"), ("fontWeight", "bold"), ("background", "#1F1F1F"), ("fontSize", J.get(G_fs, "row")), ("padding", px(4)))]))))
    G_paint_overlay("UndChartOverlay", J.obj(("position", "bottom_left"), ("order", "above_all"), ("offset_x", scaleVal(50)), ("offset_y", 0)), (J.obj(("background", "#0d0d0d"), ("border", J.add("1px solid ", G_borderColor)), ("borderRadius", px(6)), ("padding", "0px"), ("rows", G_hudRows)) if J.truthy(showOverlay) else J.obj(("fontSize", 1), ("border", "none"), ("background", "transparent"), ("rows", J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", ""), ("padding", "0px"), ("background", "transparent"))])))])))))


register_store_indicator(
    script,
    name='underlying_chart_overlay_TS',
    title='Underlying Chart Overlay',
    developer='Rock Regan',
    url='https://trendspider.com/trading-tools-store/indicators/69e024-underlying-chart-overlay/',
    position='price',
    inputs=[{'id': 'bars_to_display', 'title': 'Bars to Display', 'type': 'number', 'default': 30}, {'id': 'ui_scale____', 'title': 'UI Scale (%)', 'type': 'number', 'default': 100}, {'id': 'show_overlay', 'title': 'Show Overlay', 'type': 'boolean', 'default': True}, {'id': 'show_greeks_row', 'title': 'Show Greeks Row', 'type': 'boolean', 'default': False}, {'id': 'show_strike_line_on_chart', 'title': 'Show Strike Line on Chart', 'type': 'boolean', 'default': True}, {'id': 'use_compare_symbol', 'title': 'Use Compare Symbol', 'type': 'boolean', 'default': False}, {'id': 'sym-compare_symbol', 'title': 'Compare Symbol', 'type': 'symbol-search', 'default': 'SPY'}],
    outputs=['undchartref'],
    signals=[],
    requires=['history', 'options_data_for_expiration'],
    parity='exact',
)
