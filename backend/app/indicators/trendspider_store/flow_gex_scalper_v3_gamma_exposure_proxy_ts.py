"""
Flow GEX Scalper v3 - Gamma exposure proxy -- TrendSpider store indicator by Rock Regan.

Registered as "flow_gex_scalper_v3_gamma_exposure_proxy_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68ab37-flow-gex-scalper-v1-options-gamma-flow-analyzer/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Array = G["Array"]
    G_Date = G["Date"]
    G_Math = G["Math"]
    G_String = G["String"]
    G_absCall = G["absCall"]
    G_absPut = G["absPut"]
    G_absTot = G["absTot"]
    G_actualPagesLoaded = G["actualPagesLoaded"]
    G_allowZero = G["allowZero"]
    G_avgDataAge = G["avgDataAge"]
    G_baseFont = G["baseFont"]
    G_callF = G["callF"]
    G_callG = G["callG"]
    G_callShare = G["callShare"]
    G_chartColors = G["chartColors"]
    G_chartLabels = G["chartLabels"]
    G_chartValues = G["chartValues"]
    G_close = G["close"]
    G_criticalIssues = G["criticalIssues"]
    G_current = G["current"]
    G_d = G["d"]
    G_describe_indicator = G["describe_indicator"]
    G_dte = G["dte"]
    G_dte2 = G["dte2"]
    G_dteLowerPass = G["dteLowerPass"]
    G_dteM = G["dteM"]
    G_dteUpperPass = G["dteUpperPass"]
    G_dteZ = G["dteZ"]
    G_effSz = G["effSz"]
    G_gamma = G["gamma"]
    G_gd = G["gd"]
    G_gexData = G["gexData"]
    G_gexImbalance = G["gexImbalance"]
    G_healthColor = G["healthColor"]
    G_healthWarnings = G["healthWarnings"]
    G_input = G["input"]
    G_isFinite = G["isFinite"]
    G_k = G["k"]
    G_key = G["key"]
    G_loadRes = G["loadRes"]
    G_maxAbsGEX = G["maxAbsGEX"]
    G_maxAgeMs = G["maxAgeMs"]
    G_maxGEXStrike = G["maxGEXStrike"]
    G_maxStrikeText = G["maxStrikeText"]
    G_modeBadge = G["modeBadge"]
    G_nearShare = G["nearShare"]
    G_nearWindow = G["nearWindow"]
    G_netG = G["netG"]
    G_o = G["o"]
    G_op = G["op"]
    G_oz = G["oz"]
    G_paint_overlay = G["paint_overlay"]
    G_parseFloat = G["parseFloat"]
    G_pinShare = G["pinShare"]
    G_prem = G["prem"]
    G_premiumRatio = G["premiumRatio"]
    G_putCallRatio = G["putCallRatio"]
    G_putF = G["putF"]
    G_putG = G["putG"]
    G_ratiosText = G["ratiosText"]
    G_rawOptionsData = G["rawOptionsData"]
    G_rejectedErrorCount = G["rejectedErrorCount"]
    G_rejectedNullCount = G["rejectedNullCount"]
    G_rejectedStaleCount = G["rejectedStaleCount"]
    G_request = G["request"]
    G_rows = G["rows"]
    G_s = G["s"]
    G_sZ = G["sZ"]
    G_sd = G["sd"]
    G_signalPrefix = G["signalPrefix"]
    G_size0 = G["size0"]
    G_spot = G["spot"]
    G_strike = G["strike"]
    G_strikeDTE = G["strikeDTE"]
    G_strikeData = G["strikeData"]
    G_symbol = G["symbol"]
    G_sz = G["sz"]
    G_tExp = G["tExp"]
    G_titleLeft = G["titleLeft"]
    G_tmp = G["tmp"]
    G_totalProcessed = G["totalProcessed"]
    G_totalStrikes = G["totalStrikes"]
    G_type = G["type"]
    G_type2 = G["type2"]
    G_vol = G["vol"]
    G_weightedDTE = G["weightedDTE"]
    noDataReason = J.undefined
    vi = J.undefined
    m = J.undefined
    validOptions = J.undefined
    z = J.undefined
    zeroCnt = J.undefined
    zeroSz = J.undefined
    totSz = J.undefined
    gi = J.undefined
    sumSizeForDTE = J.undefined
    sumSizeTimesDTE = J.undefined
    allStrikes = J.undefined
    dataSufficiency = J.undefined
    sufficiencyColor = J.undefined
    sufficiencyText = J.undefined
    si = J.undefined
    bothStrikes = J.undefined
    callStrikes = J.undefined
    putStrikes = J.undefined
    callPutBalance = J.undefined
    ai = J.undefined
    totalCallGEX = J.undefined
    totalPutGEX = J.undefined
    totalFlowGEX = J.undefined
    totalCallVolume = J.undefined
    totalPutVolume = J.undefined
    totalCallPremium = J.undefined
    totalPutPremium = J.undefined
    mi = J.undefined
    maxIdx = J.undefined
    nearPct = J.undefined
    ni = J.undefined
    nearAbs = J.undefined
    ci = J.undefined
    healthText = J.undefined
    hw = J.undefined
    tradeSignal = J.undefined
    signalColor = J.undefined
    def toNum(v=J.undefined, *_args):
        s = J.undefined
        n = J.undefined
        s = J.get(G_String(("0" if (J.nullish(v)) else v)), "replace")(J.regex(",", "g"), "")
        n = G_parseFloat(s)
        return (n if J.truthy(G_isFinite(n)) else 0)
    def calculateGamma(strike=J.undefined, spot=J.undefined, timeToExp=J.undefined, vol=J.undefined, *_args):
        lnSK = J.undefined
        sqrtT = J.undefined
        r = J.undefined
        d1 = J.undefined
        phi = J.undefined
        if (((J.le(timeToExp, 0) or J.le(vol, 0)) or J.le(spot, 0)) or J.le(strike, 0)):
            return 0
        lnSK = J.get(G_Math, "log")(J.div(spot, strike))
        sqrtT = J.get(G_Math, "sqrt")(timeToExp)
        r = 0.0412
        d1 = J.div(J.add(lnSK, J.mul(J.add(r, J.mul(J.mul(0.5, vol), vol)), timeToExp)), J.mul(vol, sqrtT))
        phi = J.div(J.get(G_Math, "exp")(J.mul(J.mul((-0.5), d1), d1)), J.get(G_Math, "sqrt")(J.mul(2, J.get(G_Math, "PI"))))
        return J.div(phi, J.mul(J.mul(spot, vol), sqrtT))
    def volGuess(strike=J.undefined, spotPx=J.undefined, *_args):
        m_2 = J.undefined
        bump = J.undefined
        vol = J.undefined
        m_2 = J.div(strike, spotPx)
        if J.lt(m_2, 0.01):
            m_2 = 0.01
        if J.gt(m_2, 10):
            m_2 = 10
        bump = J.mul(0.25, J.get(G_Math, "pow")(J.get(G_Math, "log")(m_2), 2))
        vol = J.add(0.25, J.get(G_Math, "min")(0.35, bump))
        if J.lt(vol, 0.05):
            vol = 0.05
        if J.gt(vol, 3):
            vol = 3
        return vol
    def fmt(v=J.undefined, *_args):
        a = J.undefined
        a = J.get(G_Math, "abs")(v)
        if J.ge(a, 1000000000):
            return J.add(J.get(J.div(v, 1000000000), "toFixed")(2), "B")
        if J.ge(a, 1000000):
            return J.add(J.get(J.div(v, 1000000), "toFixed")(1), "M")
        if J.ge(a, 1000):
            return J.add(J.get(J.div(v, 1000), "toFixed")(1), "K")
        return J.get(v, "toFixed")(0)
    def scaleVal(n=J.undefined, *_args):
        return J.get(G_Math, "max")(1, J.get(G_Math, "round")(J.div(J.mul(n, uiScale), 100)))
    def px(n=J.undefined, *_args):
        return J.add(scaleVal(n), "px")
    def loadFreshOptions(ticker=J.undefined, maxPages=J.undefined, maxAgeMs=J.undefined, *_args):
        allOptions = J.undefined
        lastTimestamp = J.undefined
        pagesLoaded = J.undefined
        rejectedStale = J.undefined
        rejectedNull = J.undefined
        rejectedError = J.undefined
        avgAge = J.undefined
        ageSum = J.undefined
        ageCount = J.undefined
        nowMs = J.undefined
        cutoffTime = J.undefined
        i = J.undefined
        pageData = J.undefined
        k = J.undefined
        record = J.undefined
        recordTimeMs = J.undefined
        rawTS = J.undefined
        hoursSince = J.undefined
        last = J.undefined
        allOptions = J.JSArray([])
        lastTimestamp = None
        pagesLoaded = 0
        rejectedStale = 0
        rejectedNull = 0
        rejectedError = 0
        avgAge = 0
        ageSum = 0
        ageCount = 0
        nowMs = J.get(G_Date, "now")()
        cutoffTime = J.sub(nowMs, maxAgeMs)
        i = 0
        while J.lt(i, maxPages):
            pageData = J.undefined
            if J.seq(i, 0):
                pageData = J.get(G_request, "unusual_options")(ticker)
            else:
                pageData = J.get(G_request, "unusual_options")(ticker, J.obj(("filters", J.JSArray([J.obj(("field", "timestamp"), ("filter", "less"), ("value", lastTimestamp))]))))
            if (((not J.truthy(pageData)) or (not J.truthy(J.get(G_Array, "isArray")(pageData)))) or J.seq(J.get(pageData, "length"), 0)):
                break
            k = 0
            while J.lt(k, J.get(pageData, "length")):
                record = J.get(pageData, k)
                if (not J.nullish(J.get(record, "timestamp"))):
                    try:
                        recordTimeMs = J.undefined
                        rawTS = J.get(record, "timestamp")
                        if J.seq(J.typeof(rawTS), "string"):
                            recordTimeMs = J.get(G_Date, "parse")(rawTS)
                        else:
                            if J.lt(rawTS, 1000000000000):
                                recordTimeMs = J.mul(rawTS, 1000)
                            else:
                                recordTimeMs = rawTS
                        if (J.truthy(G_isFinite(recordTimeMs)) and J.gt(recordTimeMs, cutoffTime)):
                            J.get(allOptions, "push")(record)
                            hoursSince = J.div(J.sub(nowMs, recordTimeMs), J.mul(J.mul(1000, 60), 60))
                            ageSum = J.add(ageSum, hoursSince)
                            ageCount = J.inc(ageCount)
                        else:
                            rejectedStale = J.inc(rejectedStale)
                    except Exception as _e1:
                        e = J.catch_value(_e1)
                        rejectedError = J.inc(rejectedError)
                else:
                    rejectedNull = J.inc(rejectedNull)
                k = J.inc(k)
            last = J.get(pageData, J.sub(J.get(pageData, "length"), 1))
            if (J.truthy(last) and (not J.nullish(J.get(last, "timestamp")))):
                lastTimestamp = J.get(last, "timestamp")
            pagesLoaded = J.inc(pagesLoaded)
            i = J.inc(i)
        avgAge = (J.div(ageSum, ageCount) if J.gt(ageCount, 0) else 0)
        return J.obj(("data", allOptions), ("pagesLoaded", pagesLoaded), ("rejectedStale", rejectedStale), ("rejectedNull", rejectedNull), ("rejectedError", rejectedError), ("totalProcessed", J.add(J.add(J.add(J.get(allOptions, "length"), rejectedStale), rejectedNull), rejectedError)), ("avgAge", avgAge))
    G_describe_indicator("Flow GEX Scalper v3 - Gamma exposure proxy", J.obj(("shortName", "Flow GEX v3")))
    topN = J.get(G_input, "number")("Top N Strikes", 15, J.obj(("min", 5), ("max", 30)))
    pagesToLoad = J.get(G_input, "number")("Pages to Load", 2, J.obj(("min", 1), ("max", 10)))
    maxDTE = J.get(G_input, "number")("Max DTE (days)", 7, J.obj(("min", 0), ("max", 60)))
    useTightNear = J.get(G_input, "boolean")("Tight Near-Spot Window (±5%)", True)
    include0DTE = J.get(G_input, "boolean")("Include 0DTE (blend)", True)
    zeroDTEWeight = J.get(G_input, "number")("0DTE Weight (0–1)", 0.6, J.obj(("min", 0), ("max", 1), ("step", 0.05)))
    mode0DTE = J.get(G_input, "boolean")("0DTE-Only Mode", False)
    maxDataAgeHours = J.get(G_input, "number")("Max Data Age (hours)", 48, J.obj(("min", 1), ("max", 168)))
    showDataHealth = J.get(G_input, "boolean")("Show Data Health Info", True)
    compactHUD = J.get(G_input, "boolean")("Compact HUD", True)
    uiScale = J.get(G_input, "number")("UI Scale (%)", 100, J.obj(("min", 50), ("max", 150), ("step", 5)))
    G_baseFont = J.obj(("header", px(12)), ("totals", px(12)), ("ratios", px(11)), ("small", px(10)))
    G_symbol = (J.get(G_current, "symbol") if (J.truthy(G_current) and J.truthy(J.get(G_current, "symbol"))) else (J.get(G_current, "ticker") if (J.truthy(G_current) and J.truthy(J.get(G_current, "ticker"))) else ""))
    G_spot = J.get(G_close, J.sub(J.get(G_close, "length"), 1))
    G_maxAgeMs = J.mul(J.mul(J.mul(maxDataAgeHours, 60), 60), 1000)
    G_loadRes = loadFreshOptions(G_symbol, pagesToLoad, G_maxAgeMs)
    G_rawOptionsData = J.get(G_loadRes, "data")
    G_actualPagesLoaded = J.get(G_loadRes, "pagesLoaded")
    G_rejectedStaleCount = J.get(G_loadRes, "rejectedStale")
    G_rejectedNullCount = J.get(G_loadRes, "rejectedNull")
    G_rejectedErrorCount = J.get(G_loadRes, "rejectedError")
    G_totalProcessed = J.get(G_loadRes, "totalProcessed")
    G_avgDataAge = J.get(G_loadRes, "avgAge")
    G_dataHealthy = True
    G_healthWarnings = J.JSArray([])
    G_criticalIssues = J.JSArray([])
    if J.gt(G_rejectedStaleCount, J.mul(J.get(G_rawOptionsData, "length"), 2)):
        J.get(G_healthWarnings, "push")("High stale data ratio - consider increasing age limit")
    if J.gt(G_rejectedErrorCount, J.mul(G_totalProcessed, 0.1)):
        J.get(G_criticalIssues, "push")(J.add(J.add("High timestamp conversion error rate: ", J.get(J.mul(J.div(G_rejectedErrorCount, G_totalProcessed), 100), "toFixed")(1)), "%"))
    if J.lt(J.get(G_rawOptionsData, "length"), 50):
        J.get(G_healthWarnings, "push")("Limited fresh data available")
    if J.gt(G_avgDataAge, 24):
        J.get(G_healthWarnings, "push")("Average data age over 24 hours")
    if ((not J.truthy(G_rawOptionsData)) or J.seq(J.get(G_rawOptionsData, "length"), 0)):
        noDataReason = J.add(J.add("All ", G_totalProcessed), " records rejected: ")
        noDataReason = J.add(noDataReason, J.add(G_rejectedStaleCount, " stale, "))
        noDataReason = J.add(noDataReason, J.add(G_rejectedNullCount, " null, "))
        noDataReason = J.add(noDataReason, J.add(G_rejectedErrorCount, " errors"))
        G_paint_overlay("GEXChart", J.obj(("position", "bottom_right"), ("offset_x", (-50)), ("offset_y", (-50)), ("order", "above_all")), J.obj(("background", "rgba(20,20,20,0.95)"), ("border", "1px solid red"), ("borderRadius", scaleVal(4)), ("rows", J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", "NO FRESH OPTIONS DATA"), ("color", "#ffffff"), ("textAlign", "center"), ("fontWeight", "bold"), ("fontSize", J.get(G_baseFont, "totals")))]))), J.obj(("cells", J.JSArray([J.obj(("text", J.add(J.add(G_symbol, " - "), noDataReason)), ("color", "#ffffff"), ("textAlign", "center"), ("fontSize", J.get(G_baseFont, "small")))])))]))))
        return J.undefined
    validOptions = J.JSArray([])
    vi = 0
    while J.lt(vi, J.get(G_rawOptionsData, "length")):
        G_op = (_t1 if J.truthy(_t1 := J.get(G_rawOptionsData, vi)) else J.obj())
        G_type = J.get(G_String(("" if (J.nullish(J.get(G_op, "type"))) else J.get(G_op, "type"))), "toUpperCase")()
        G_strike = toNum(J.get(G_op, "strike"))
        G_size0 = toNum((J.get(G_op, "size") if (not J.nullish(J.get(G_op, "size"))) else (J.get(G_op, "quantity") if (not J.nullish(J.get(G_op, "quantity"))) else J.get(G_op, "contracts"))))
        G_dte = toNum((J.get(G_op, "daysToExp") if (not J.nullish(J.get(G_op, "daysToExp"))) else (J.get(G_op, "dte") if (not J.nullish(J.get(G_op, "dte"))) else J.get(G_op, "days_to_expiry"))))
        G_allowZero = (_t2 if J.truthy(_t2 := include0DTE) else mode0DTE)
        G_dteLowerPass = (J.ge(G_dte, 0) if J.truthy(G_allowZero) else J.ge(G_dte, 1))
        G_dteUpperPass = (True if J.le(maxDTE, 0) else J.le(G_dte, maxDTE))
        if ((((J.gt(G_strike, 0) and J.gt(G_size0, 0)) and (J.seq(G_type, "CALL") or J.seq(G_type, "PUT"))) and J.truthy(G_dteLowerPass)) and J.truthy(G_dteUpperPass)):
            J.get(validOptions, "push")(G_op)
        vi = J.inc(vi)
    if J.truthy(mode0DTE):
        G_tmp = J.JSArray([])
        m = 0
        while J.lt(m, J.get(validOptions, "length")):
            G_dteM = toNum((J.get(J.get(validOptions, m), "daysToExp") if (not J.nullish(J.get(J.get(validOptions, m), "daysToExp"))) else (J.get(J.get(validOptions, m), "dte") if (not J.nullish(J.get(J.get(validOptions, m), "dte"))) else J.get(J.get(validOptions, m), "days_to_expiry"))))
            if J.seq(G_dteM, 0):
                J.get(G_tmp, "push")(J.get(validOptions, m))
            m = J.inc(m)
        validOptions = G_tmp
    if J.seq(J.get(validOptions, "length"), 0):
        G_paint_overlay("GEXChart", J.obj(("position", "bottom_right"), ("offset_x", (-50)), ("offset_y", (-50)), ("order", "above_all")), J.obj(("background", "rgba(20,20,20,0.95)"), ("border", "1px solid orange"), ("borderRadius", scaleVal(4)), ("rows", J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", "NO VALID FRESH OPTIONS"), ("color", "#ffffff"), ("textAlign", "center"), ("fontWeight", "bold"), ("fontSize", J.get(G_baseFont, "totals")))]))), J.obj(("cells", J.JSArray([J.obj(("text", J.add(J.add(J.add(G_symbol, " - "), J.get(G_rawOptionsData, "length")), " fresh, 0 valid after filters")), ("color", "#ffffff"), ("textAlign", "center"), ("fontSize", J.get(G_baseFont, "small")))])))]))))
        return J.undefined
    zeroCnt = 0
    zeroSz = 0
    totSz = 0
    z = 0
    while J.lt(z, J.get(validOptions, "length")):
        G_oz = J.get(validOptions, z)
        G_dteZ = toNum((J.get(G_oz, "daysToExp") if (not J.nullish(J.get(G_oz, "daysToExp"))) else (J.get(G_oz, "dte") if (not J.nullish(J.get(G_oz, "dte"))) else J.get(G_oz, "days_to_expiry"))))
        G_sZ = toNum((J.get(G_oz, "size") if (not J.nullish(J.get(G_oz, "size"))) else (J.get(G_oz, "quantity") if (not J.nullish(J.get(G_oz, "quantity"))) else J.get(G_oz, "contracts"))))
        if J.seq(G_dteZ, 0):
            zeroCnt = J.inc(zeroCnt)
            zeroSz = J.add(zeroSz, G_sZ)
        totSz = J.add(totSz, G_sZ)
        z = J.inc(z)
    G_zeroShare = (J.div(zeroSz, totSz) if J.gt(totSz, 0) else 0)
    G_strikeData = J.obj()
    sumSizeForDTE = 0
    sumSizeTimesDTE = 0
    gi = 0
    while J.lt(gi, J.get(validOptions, "length")):
        G_o = (_t3 if J.truthy(_t3 := J.get(validOptions, gi)) else J.obj())
        G_s = toNum(J.get(G_o, "strike"))
        G_sz = toNum((J.get(G_o, "size") if (not J.nullish(J.get(G_o, "size"))) else (J.get(G_o, "quantity") if (not J.nullish(J.get(G_o, "quantity"))) else J.get(G_o, "contracts"))))
        G_dte2 = toNum((J.get(G_o, "daysToExp") if (not J.nullish(J.get(G_o, "daysToExp"))) else (J.get(G_o, "dte") if (not J.nullish(J.get(G_o, "dte"))) else J.get(G_o, "days_to_expiry"))))
        G_type2 = J.get(G_String(("" if (J.nullish(J.get(G_o, "type"))) else J.get(G_o, "type"))), "toUpperCase")()
        G_prem = toNum((_t4 if J.truthy(_t4 := (_t5 if J.truthy(_t5 := (_t6 if J.truthy(_t6 := (J.get(G_o, "costBasis") if (not J.nullish(J.get(G_o, "costBasis"))) else None)) else (J.get(G_o, "premium") if (not J.nullish(J.get(G_o, "premium"))) else None))) else (J.get(G_o, "notional") if (not J.nullish(J.get(G_o, "notional"))) else None))) else (J.get(G_o, "price") if (not J.nullish(J.get(G_o, "price"))) else None)))
        G_effSz = (J.mul(G_sz, zeroDTEWeight) if (J.seq(G_dte2, 0) and (not J.truthy(mode0DTE))) else G_sz)
        if (not J.truthy(J.get(G_strikeData, G_s))):
            J.set(G_strikeData, G_s, J.obj(("strike", G_s), ("callFlow", 0), ("putFlow", 0), ("callVolume", 0), ("putVolume", 0), ("callPremium", 0), ("putPremium", 0), ("sizeForDTE", 0), ("sizeTimesDTE", 0), ("records", 0)))
        G_d = J.get(G_strikeData, G_s)
        J.set(G_d, "records", J.add(J.get(G_d, "records"), 1))
        J.set(G_d, "sizeForDTE", J.add(J.get(G_d, "sizeForDTE"), G_effSz))
        J.set(G_d, "sizeTimesDTE", J.add(J.get(G_d, "sizeTimesDTE"), J.mul(G_effSz, G_dte2)))
        if J.seq(G_type2, "CALL"):
            J.set(G_d, "callFlow", J.add(J.get(G_d, "callFlow"), G_effSz))
            J.set(G_d, "callVolume", J.add(J.get(G_d, "callVolume"), G_effSz))
            J.set(G_d, "callPremium", J.add(J.get(G_d, "callPremium"), J.mul(G_prem, G_effSz)))
        else:
            J.set(G_d, "putFlow", J.add(J.get(G_d, "putFlow"), G_effSz))
            J.set(G_d, "putVolume", J.add(J.get(G_d, "putVolume"), G_effSz))
            J.set(G_d, "putPremium", J.add(J.get(G_d, "putPremium"), J.mul(G_prem, G_effSz)))
        sumSizeForDTE = J.add(sumSizeForDTE, G_effSz)
        sumSizeTimesDTE = J.add(sumSizeTimesDTE, J.mul(G_effSz, G_dte2))
        gi = J.inc(gi)
    allStrikes = J.JSArray([])
    for G_key in J.iter_in(G_strikeData):
        if J.truthy(J.get(G_strikeData, "hasOwnProperty")(G_key)):
            J.get(allStrikes, "push")(J.get(G_strikeData, G_key))
    def _f7(d=J.undefined, *_args):
        return J.gt(J.add(J.get(d, "callFlow"), J.get(d, "putFlow")), 0)
    allStrikes = J.get(allStrikes, "filter")(_f7)
    def _f8(a=J.undefined, b=J.undefined, *_args):
        return J.sub(J.add(J.get(b, "callFlow"), J.get(b, "putFlow")), J.add(J.get(a, "callFlow"), J.get(a, "putFlow")))
    J.get(allStrikes, "sort")(_f8)
    G_totalStrikes = J.get(allStrikes, "length")
    allStrikes = J.get(allStrikes, "slice")(0, topN)
    def _f9(a=J.undefined, b=J.undefined, *_args):
        return J.sub(J.get(a, "strike"), J.get(b, "strike"))
    J.get(allStrikes, "sort")(_f9)
    G_weightedDTE = (J.div(sumSizeTimesDTE, sumSizeForDTE) if J.gt(sumSizeForDTE, 0) else 1)
    dataSufficiency = "GOOD"
    sufficiencyColor = "rgba(0,150,0,0.8)"
    sufficiencyText = "Data: GOOD"
    if J.gt(J.get(G_criticalIssues, "length"), 0):
        dataSufficiency = "CRITICAL"
        sufficiencyColor = "rgba(200,0,0,0.9)"
        sufficiencyText = J.add("Data: CRITICAL - ", J.get(G_criticalIssues, 0))
    else:
        callPutBalance = 0
        callStrikes = 0
        putStrikes = 0
        bothStrikes = 0
        si = 0
        while J.lt(si, J.get(allStrikes, "length")):
            G_sd = J.get(allStrikes, si)
            if (J.gt(J.get(G_sd, "callFlow"), 0) and J.gt(J.get(G_sd, "putFlow"), 0)):
                bothStrikes = J.inc(bothStrikes)
            elif J.gt(J.get(G_sd, "callFlow"), 0):
                callStrikes = J.inc(callStrikes)
            elif J.gt(J.get(G_sd, "putFlow"), 0):
                putStrikes = J.inc(putStrikes)
            si = J.inc(si)
        callPutBalance = (J.div(bothStrikes, J.add(J.add(callStrikes, putStrikes), bothStrikes)) if J.gt(J.add(callStrikes, putStrikes), 0) else 0)
        if ((J.lt(J.get(validOptions, "length"), 50) or J.lt(G_totalStrikes, 8)) or J.lt(callPutBalance, 0.2)):
            dataSufficiency = "WEAK"
            sufficiencyColor = "rgba(200,0,0,0.8)"
            sufficiencyText = "Data: WEAK - Limited Flow"
        elif ((J.lt(J.get(validOptions, "length"), 100) or J.lt(G_totalStrikes, 12)) or J.lt(callPutBalance, 0.3)):
            dataSufficiency = "FAIR"
            sufficiencyColor = "rgba(200,120,0,0.8)"
            sufficiencyText = "Data: FAIR"
    totalFlowGEX = 0
    totalCallGEX = 0
    totalPutGEX = 0
    totalCallVolume = 0
    totalPutVolume = 0
    totalCallPremium = 0
    totalPutPremium = 0
    G_gexData = J.JSArray([])
    ai = 0
    while J.lt(ai, J.get(allStrikes, "length")):
        G_sd = J.get(allStrikes, ai)
        G_k = J.get(G_sd, "strike")
        G_callF = J.get(G_sd, "callFlow")
        G_putF = J.get(G_sd, "putFlow")
        G_strikeDTE = (J.div(J.get(G_sd, "sizeTimesDTE"), J.get(G_sd, "sizeForDTE")) if J.gt(J.get(G_sd, "sizeForDTE"), 0) else G_weightedDTE)
        G_tExp = J.get(G_Math, "max")(0.01, J.div(G_strikeDTE, 365))
        G_vol = volGuess(G_k, G_spot)
        G_gamma = calculateGamma(G_k, G_spot, G_tExp, G_vol)
        G_callG = J.mul(J.mul(J.mul(J.mul(G_gamma, G_callF), 100), G_spot), G_spot)
        G_putG = J.mul(J.mul(J.mul(J.mul(J.neg(G_gamma), G_putF), 100), G_spot), G_spot)
        G_netG = J.add(G_callG, G_putG)
        totalCallGEX = J.add(totalCallGEX, G_callG)
        totalPutGEX = J.add(totalPutGEX, G_putG)
        totalFlowGEX = J.add(totalFlowGEX, G_netG)
        totalCallVolume = J.add(totalCallVolume, J.get(G_sd, "callVolume"))
        totalPutVolume = J.add(totalPutVolume, J.get(G_sd, "putVolume"))
        totalCallPremium = J.add(totalCallPremium, J.get(G_sd, "callPremium"))
        totalPutPremium = J.add(totalPutPremium, J.get(G_sd, "putPremium"))
        J.get(G_gexData, "push")(J.obj(("strike", G_k), ("netGEX", G_netG), ("callGEX", G_callG), ("putGEX", G_putG)))
        ai = J.inc(ai)
    G_putCallRatio = (J.div(totalPutVolume, totalCallVolume) if J.gt(totalCallVolume, 0) else 0)
    G_premiumRatio = (J.div(totalPutPremium, totalCallPremium) if J.gt(totalCallPremium, 0) else 0)
    maxIdx = 0
    mi = 1
    while J.lt(mi, J.get(G_gexData, "length")):
        if J.gt(J.get(G_Math, "abs")(J.get(J.get(G_gexData, mi), "netGEX")), J.get(G_Math, "abs")(J.get(J.get(G_gexData, maxIdx), "netGEX"))):
            maxIdx = mi
        mi = J.inc(mi)
    G_maxGEXStrike = (J.get(G_gexData, maxIdx) if J.truthy(J.get(G_gexData, "length")) else None)
    nearPct = (0.05 if J.truthy(useTightNear) else 0.08)
    if (J.truthy(mode0DTE) and J.truthy(useTightNear)):
        nearPct = 0.04
    G_nearWindow = J.mul(nearPct, G_spot)
    nearAbs = 0
    ni = 0
    while J.lt(ni, J.get(G_gexData, "length")):
        G_gd = J.get(G_gexData, ni)
        if J.le(J.get(G_Math, "abs")(J.sub(J.get(G_gd, "strike"), G_spot)), G_nearWindow):
            nearAbs = J.add(nearAbs, J.get(G_Math, "abs")(J.get(G_gd, "netGEX")))
        ni = J.inc(ni)
    G_absCall = J.get(G_Math, "abs")(totalCallGEX)
    G_absPut = J.get(G_Math, "abs")(totalPutGEX)
    G_absTot = J.add(G_absCall, G_absPut)
    G_gexImbalance = (J.div(totalFlowGEX, G_absTot) if J.gt(G_absTot, 0) else 0)
    G_callShare = (J.div(G_absCall, G_absTot) if J.gt(G_absTot, 0) else 0)
    G_nearShare = (J.div(nearAbs, G_absTot) if J.gt(G_absTot, 0) else 0)
    G_maxAbsGEX = (J.get(G_Math, "abs")(J.get(G_maxGEXStrike, "netGEX")) if J.truthy(G_maxGEXStrike) else 0)
    G_pinShare = (J.div(G_maxAbsGEX, G_absTot) if J.gt(G_absTot, 0) else 0)
    G_chartLabels = J.JSArray([])
    G_chartValues = J.JSArray([])
    G_chartColors = J.JSArray([])
    ci = 0
    while J.lt(ci, J.get(G_gexData, "length")):
        J.get(G_chartLabels, "push")(J.get(J.get(J.get(G_gexData, ci), "strike"), "toFixed")(1))
        J.get(G_chartValues, "push")(J.div(J.get(J.get(G_gexData, ci), "netGEX"), 1000000))
        J.get(G_chartColors, "push")(("#00FF00" if J.gt(J.get(J.get(G_gexData, ci), "netGEX"), 0) else "#FF0000"))
        ci = J.inc(ci)
    G_titleLeft = J.add(J.add(G_symbol, " – Spot: "), J.get(G_spot, "toFixed")(2))
    G_maxStrikeText = (J.get(G_maxGEXStrike, "strike") if (J.truthy(G_maxGEXStrike) and (not J.nullish(J.get(G_maxGEXStrike, "strike")))) else "—")
    G_modeBadge = ("0DTE MODE" if J.truthy(mode0DTE) else (J.add(J.add("0DTE@", J.get(G_Math, "round")(J.mul(zeroDTEWeight, 100))), "%") if J.truthy(include0DTE) else "No 0DTE"))
    G_rows = J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", J.add(J.add(J.add(J.add(J.add(J.add(G_titleLeft, " | Max |Flow GEX| at: "), G_maxStrikeText), "  ["), G_modeBadge), "] | "), sufficiencyText)), ("color", "yellow"), ("textAlign", "center"), ("fontWeight", "bold"), ("background", "#54008A"), ("fontSize", J.get(G_baseFont, "header")))])))])
    if J.truthy(showDataHealth):
        healthText = J.add(J.add(J.add(J.get(G_rawOptionsData, "length"), " fresh records ("), J.get(G_avgDataAge, "toFixed")(1)), "h avg age)")
        if ((J.gt(G_rejectedStaleCount, 0) or J.gt(G_rejectedNullCount, 0)) or J.gt(G_rejectedErrorCount, 0)):
            healthText = J.add(healthText, J.add(J.add(" | Rejected: ", G_rejectedStaleCount), " stale"))
            if J.gt(G_rejectedNullCount, 0):
                healthText = J.add(healthText, J.add(J.add(", ", G_rejectedNullCount), " null"))
            if J.gt(G_rejectedErrorCount, 0):
                healthText = J.add(healthText, J.add(J.add(", ", G_rejectedErrorCount), " errors"))
        G_healthColor = ("rgba(0,150,0,0.8)" if J.lt(G_avgDataAge, 12) else ("rgba(200,120,0,0.8)" if J.lt(G_avgDataAge, 48) else "rgba(200,0,0,0.8)"))
        J.get(G_rows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", healthText), ("color", "#ffffff"), ("textAlign", "center"), ("fontSize", J.get(G_baseFont, "small")), ("background", G_healthColor))]))))
        ci = 0
        while J.lt(ci, J.get(G_criticalIssues, "length")):
            J.get(G_rows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", J.add("CRITICAL: ", J.get(G_criticalIssues, ci))), ("color", "#ffffff"), ("textAlign", "center"), ("fontWeight", "bold"), ("background", "rgba(200,0,0,0.9)"), ("fontSize", J.get(G_baseFont, "totals")))]))))
            ci = J.inc(ci)
        hw = 0
        while J.lt(hw, J.get(G_healthWarnings, "length")):
            J.get(G_rows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", J.add("HEALTH: ", J.get(G_healthWarnings, hw))), ("color", "#ffffff"), ("textAlign", "center"), ("fontWeight", "bold"), ("background", "rgba(200,100,0,0.9)"), ("fontSize", J.get(G_baseFont, "small")))]))))
            hw = J.inc(hw)
    if J.truthy(mode0DTE):
        J.get(G_rows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", "0DTE-Only: intraday pin & whipsaw sensitivity is HIGH"), ("color", "#ffffff"), ("textAlign", "center"), ("fontWeight", "bold"), ("background", "#b00020"), ("fontSize", J.get(G_baseFont, "totals")))]))))
    J.get(G_rows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", J.add(J.add(J.add(J.add(J.add("Flow GEX (proxy): ", fmt(totalFlowGEX)), " | Call: "), fmt(totalCallGEX)), " | Put: "), fmt(totalPutGEX))), ("color", "#ffffff"), ("textAlign", "center"), ("fontWeight", "bold"), ("fontSize", J.get(G_baseFont, "totals")), ("background", ("rgba(0,150,0,0.8)" if J.gt(totalFlowGEX, 0) else "rgba(200,0,0,0.8)")))]))))
    J.get(G_rows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", J.add(J.add(J.add(J.add(J.add(J.add("P/C Vol: ", J.get(G_putCallRatio, "toFixed")(2)), " | P/C Prem: "), J.get(G_premiumRatio, "toFixed")(2)), " | Near Window: ±"), J.get(J.mul(nearPct, 100), "toFixed")(0)), "%")), ("color", "#ffffff"), ("textAlign", "center"), ("fontWeight", "bold"), ("fontSize", J.get(G_baseFont, "totals")), ("background", ("rgba(200,0,0,0.8)" if J.gt(G_putCallRatio, 1.5) else ("rgba(0,200,0,0.8)" if J.lt(G_putCallRatio, 0.7) else "rgba(0,120,200,0.8)"))))]))))
    if (not J.truthy(compactHUD)):
        J.get(G_rows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", J.add(J.add(J.add(J.add(J.add(J.add(J.add(J.add(J.add(J.add("Data: ", J.get(validOptions, "length")), " prints ("), G_actualPagesLoaded), "/"), pagesToLoad), " pages) | "), G_totalStrikes), " strikes | DTE: "), J.get(G_weightedDTE, "toFixed")(1)), "d avg")), ("color", "#ffffff"), ("textAlign", "center"), ("fontSize", J.get(G_baseFont, "small")), ("background", sufficiencyColor))]))))
    tradeSignal = "NEUTRAL: Mixed/weak gamma configuration"
    signalColor = "rgba(150,120,0,0.8)"
    G_signalPrefix = ("DATA CRITICAL - " if J.seq(dataSufficiency, "CRITICAL") else ("LOW CONFIDENCE - " if J.seq(dataSufficiency, "WEAK") else ("MODERATE - " if J.seq(dataSufficiency, "FAIR") else "")))
    if (not J.truthy(mode0DTE)):
        if ((J.le(G_gexImbalance, (-0.25)) and J.lt(G_premiumRatio, 1)) and J.le(G_putCallRatio, 1.1)):
            tradeSignal = J.add(G_signalPrefix, "BULLISH TILT: Net short gamma + call-leaning capital")
            signalColor = "rgba(50,200,50,0.8)"
        elif (J.le(G_gexImbalance, (-0.25)) and J.ge(G_putCallRatio, 1.3)):
            tradeSignal = J.add(G_signalPrefix, "VOLATILE: Net short gamma + put-heavy volume (whipsaw risk)")
            signalColor = "rgba(220,100,0,0.8)"
        elif (J.ge(G_gexImbalance, 0.3) and J.ge(G_nearShare, 0.55)):
            tradeSignal = J.add(G_signalPrefix, "RANGE BIAS: Net long gamma + concentrated near spot")
            signalColor = "rgba(0,180,180,0.8)"
        elif (J.ge(G_pinShare, 0.35) and J.ge(G_nearShare, 0.45)):
            tradeSignal = J.add(J.add(G_signalPrefix, "PIN RISK: Strong magnet near "), G_maxStrikeText)
            signalColor = "rgba(200,0,200,0.9)"
    else:
        if (J.ge(G_pinShare, 0.4) and J.ge(G_nearShare, 0.5)):
            tradeSignal = J.add(J.add(J.add(G_signalPrefix, "TODAY PIN MAGNET: Watch "), G_maxStrikeText), " for intraday gravitation")
            signalColor = "rgba(200,0,200,0.95)"
        elif (J.le(G_gexImbalance, (-0.2)) and J.le(G_putCallRatio, 1)):
            tradeSignal = J.add(G_signalPrefix, "SQUEEZE RISK: 0DTE short gamma leaning calls")
            signalColor = "rgba(50,200,50,0.9)"
        elif (J.le(G_gexImbalance, (-0.2)) and J.gt(G_putCallRatio, 1.2)):
            tradeSignal = J.add(G_signalPrefix, "DUMP/WHIP RISK: 0DTE short gamma leaning puts")
            signalColor = "rgba(220,100,0,0.95)"
        elif (J.ge(G_gexImbalance, 0.25) and J.ge(G_nearShare, 0.55)):
            tradeSignal = J.add(G_signalPrefix, "0DTE RANGE BIAS: Liquidity dampens moves near spot")
            signalColor = "rgba(0,180,180,0.9)"
    G_ratiosText = (J.add(J.add(J.add(J.add(J.add(J.add(J.add(J.add("Imbalance: ", J.get(J.mul(G_gexImbalance, 100), "toFixed")(0)), "% | Near: "), J.get(J.mul(G_nearShare, 100), "toFixed")(0)), "% | Pin: "), J.get(J.mul(G_pinShare, 100), "toFixed")(0)), "% | Call: "), J.get(J.mul(G_callShare, 100), "toFixed")(0)), "%") if J.truthy(compactHUD) else J.add(J.add(J.add(J.add(J.add(J.add(J.add(J.add("Ratios → Imbalance: ", J.get(J.mul(G_gexImbalance, 100), "toFixed")(0)), "% | NearShare: "), J.get(J.mul(G_nearShare, 100), "toFixed")(0)), "% | PinShare: "), J.get(J.mul(G_pinShare, 100), "toFixed")(0)), "% | CallShare: "), J.get(J.mul(G_callShare, 100), "toFixed")(0)), "%"))
    J.get(G_rows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", G_ratiosText), ("color", "yellow"), ("textAlign", "center"), ("fontSize", J.get(G_baseFont, "ratios")), ("background", "rgba(0,0,0)"))]))))
    J.get(G_rows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", tradeSignal), ("color", "#FFFFFF"), ("textAlign", "center"), ("fontWeight", "bold"), ("background", signalColor), ("fontSize", J.get(G_baseFont, "totals")))]))))
    J.get(G_rows, "push")(J.obj(("cells", J.JSArray([J.obj(("chart", J.obj(("width", px(600)), ("height", px(220)), ("type", "bar"), ("options", J.obj(("plugins", J.obj(("legend", J.obj(("display", False))), ("title", J.obj(("display", True), ("text", J.add(J.add(J.add(J.add(J.add("Flow GEX v3 (proxy) by Strike (", G_actualPagesLoaded), " page"), ("" if J.seq(G_actualPagesLoaded, 1) else "s")), (", 0DTE-Only" if J.truthy(mode0DTE) else "")), ")")), ("color", "#ffffff"))))), ("scales", J.obj(("x", J.obj(("title", J.obj(("display", True), ("text", "Strike"), ("color", "#ffffff"))), ("ticks", J.obj(("color", "#ffffff"))), ("grid", J.obj(("color", "#616161"))))), ("y", J.obj(("title", J.obj(("display", True), ("text", "Flow GEX (M)"), ("color", "#ffffff"))), ("ticks", J.obj(("color", "#ffffff"))), ("grid", J.obj(("color", "#616161"))))))))), ("data", J.obj(("labels", G_chartLabels), ("datasets", J.JSArray([J.obj(("label", "Net (proxy)"), ("data", G_chartValues), ("backgroundColor", G_chartColors), ("borderWidth", 1), ("borderColor", "#666666"))])))))))]))))
    G_paint_overlay("GEXChart", J.obj(("position", "bottom_right"), ("offset_x", 0), ("offset_y", 0), ("order", "above_all")), J.obj(("background", "#3a4950"), ("border", "1px solid lime"), ("borderRadius", scaleVal(6)), ("rows", G_rows)))


register_store_indicator(
    script,
    name='flow_gex_scalper_v3_gamma_exposure_proxy_TS',
    title='Flow GEX Scalper v3 - Gamma exposure proxy',
    developer='Rock Regan',
    url='https://trendspider.com/trading-tools-store/indicators/68ab37-flow-gex-scalper-v1-options-gamma-flow-analyzer/',
    position='price',
    inputs=[{'id': 'top_n_strikes', 'title': 'Top N Strikes', 'type': 'number', 'default': 15}, {'id': 'pages_to_load', 'title': 'Pages to Load', 'type': 'number', 'default': 2}, {'id': 'max_dte__days_', 'title': 'Max DTE (days)', 'type': 'number', 'default': 7}, {'id': 'tight_near_spot_window___5__', 'title': 'Tight Near-Spot Window (±5%)', 'type': 'boolean', 'default': True}, {'id': 'include_0dte__blend_', 'title': 'Include 0DTE (blend)', 'type': 'boolean', 'default': True}, {'id': '0dte_weight__0_1_', 'title': '0DTE Weight (0–1)', 'type': 'number', 'default': 0.6}, {'id': '0dte_only_mode', 'title': '0DTE-Only Mode', 'type': 'boolean', 'default': False}, {'id': 'max_data_age__hours_', 'title': 'Max Data Age (hours)', 'type': 'number', 'default': 48}, {'id': 'show_data_health_info', 'title': 'Show Data Health Info', 'type': 'boolean', 'default': True}, {'id': 'compact_hud', 'title': 'Compact HUD', 'type': 'boolean', 'default': True}, {'id': 'ui_scale____', 'title': 'UI Scale (%)', 'type': 'number', 'default': 100}],
    outputs=[],
    signals=[],
    requires=['unusual_options'],
    parity='exact',
)
