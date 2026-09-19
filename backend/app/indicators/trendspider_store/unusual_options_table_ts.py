"""
Unusual Options Table -- TrendSpider store indicator by Rock Regan.

Registered as "unusual_options_table_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68a3e6-unusual-options-table/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Array = G["Array"]
    G_Infinity = G["Infinity"]
    G_Intl = G["Intl"]
    G_Math = G["Math"]
    G_String = G["String"]
    G_console = G["console"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_input = G["input"]
    G_isNaN = G["isNaN"]
    G_library = G["library"]
    G_paint_overlay = G["paint_overlay"]
    G_parseFloat = G["parseFloat"]
    G_parseInt = G["parseInt"]
    G_request = G["request"]
    G_time = G["time"]
    def px(base=J.undefined, *_args):
        return J.add(J.get(G_Math, "round")(J.mul(base, scale)), "px")
    def fs(base=J.undefined, *_args):
        return J.get(G_Math, "round")(J.mul(base, scale))
    def formatNumber(value=J.undefined, *_args):
        if J.truthy(G_isNaN(value)):
            return "-"
        return J.get(J.get(G_Intl, "NumberFormat")("en-US", J.obj(("notation", "compact"), ("maximumFractionDigits", 1))), "format")(value)
    def formatCurrency(value=J.undefined, *_args):
        if J.truthy(G_isNaN(value)):
            return "-"
        return J.add("$", formatNumber(value))
    def formatTime(timestamp=J.undefined, *_args):
        tsNum = G_parseInt(timestamp)
        ms = (J.mul(tsNum, 1000) if J.le(J.get(G_String(tsNum), "length"), 10) else tsNum)
        moment = G_library("moment-timezone")
        return J.get(J.get(moment(ms), "tz")("America/New_York"), "format")("MM/DD HH:mm")
    def getDaysAgoTimestamp(days=J.undefined, *_args):
        secsInDay = J.mul(J.mul(24, 60), 60)
        nowTs = J.get(G_time, J.sub(J.get(G_time, "length"), 1))
        return J.sub(nowTs, J.mul(days, secsInDay))
    def getOiPctColor(pct=J.undefined, *_args):
        if (((pct is J.undefined) or (pct is None)) or J.truthy(G_isNaN(pct))):
            return "#888888"
        if J.ge(pct, 1000):
            return "#ff00ff"
        if J.ge(pct, 100):
            return "#ff66ff"
        if J.ge(pct, 50):
            return "#00ffff"
        if J.ge(pct, 25):
            return "#FFDC61"
        if J.ge(pct, 10):
            return "#ffffff"
        return "#aaaaaa"
    def getRowBackground(tags=J.undefined, *_args):
        if ((not J.truthy(tags)) or J.seq(J.get(tags, "length"), 0)):
            return "transparent"
        def _f1(t=J.undefined, *_args):
            return J.get(G_String(t), "toLowerCase")()
        tagsLower = J.get(tags, "map")(_f1)
        isAboveAsk = J.sne(J.get(tagsLower, "indexOf")("above_ask"), (-1))
        isBelowBid = J.sne(J.get(tagsLower, "indexOf")("below_bid"), (-1))
        isBullish = J.sne(J.get(tagsLower, "indexOf")("bullish"), (-1))
        isBearish = J.sne(J.get(tagsLower, "indexOf")("bearish"), (-1))
        if J.truthy(isAboveAsk):
            return "rgba(0,255,0,0.28)"
        if J.truthy(isBelowBid):
            return "rgba(255,0,0,0.28)"
        if J.truthy(isBullish):
            return "rgba(0,255,0,0.13)"
        if J.truthy(isBearish):
            return "rgba(255,0,0,0.13)"
        return "transparent"
    def getTypeColor(t=J.undefined, *_args):
        if (not J.truthy(t)):
            return "#f0f0f0"
        u = J.get(G_String(t), "toUpperCase")()
        if (J.seq(u, "CALL") or J.seq(u, "C")):
            return "#00ff88"
        if (J.seq(u, "PUT") or J.seq(u, "P")):
            return "#ff5555"
        return "#f0f0f0"
    def execTagsForFilter(filter=J.undefined, *_args):
        _t1 = filter
        if J.seq(_t1, "ask-side"):
            _t2 = 0
        elif J.seq(_t1, "at ask"):
            _t2 = 1
        elif J.seq(_t1, "above ask"):
            _t2 = 2
        elif J.seq(_t1, "bid-side"):
            _t2 = 3
        elif J.seq(_t1, "at bid"):
            _t2 = 4
        elif J.seq(_t1, "below bid"):
            _t2 = 5
        elif J.seq(_t1, "midpoint"):
            _t2 = 6
        elif J.seq(_t1, "aggressive (any side)"):
            _t2 = 7
        else:
            _t2 = 8
        _c3 = False
        for _once in (0,):
            if _t2 <= 0:
                return J.JSArray(["at_ask", "above_ask"])
            if _t2 <= 1:
                return J.JSArray(["at_ask"])
            if _t2 <= 2:
                return J.JSArray(["above_ask"])
            if _t2 <= 3:
                return J.JSArray(["at_bid", "below_bid"])
            if _t2 <= 4:
                return J.JSArray(["at_bid"])
            if _t2 <= 5:
                return J.JSArray(["below_bid"])
            if _t2 <= 6:
                return J.JSArray(["at_midpoint"])
            if _t2 <= 7:
                return J.JSArray(["above_ask", "below_bid"])
            if _t2 <= 8:
                return J.JSArray([])
            pass
    def passesFilters(opt=J.undefined, *_args):
        if ((not J.truthy(J.get(opt, "timestamp"))) or J.lt(J.get(opt, "timestamp"), getDaysAgoTimestamp(myLookbackDays))):
            return False
        if ((not J.truthy(J.get(opt, "costBasis"))) or J.lt(J.get(opt, "costBasis"), myMinPremium)):
            return False
        if ((J.gt(myMinOiPct, 0) and (J.get(opt, "oiPercent") is not J.undefined)) and (J.get(opt, "oiPercent") is not None)):
            if J.lt(J.get(opt, "oiPercent"), myMinOiPct):
                return False
        if ((J.get(opt, "daysToExp") is not J.undefined) and J.gt(J.get(opt, "daysToExp"), myMaxDTE)):
            return False
        def _f2(t=J.undefined, *_args):
            return J.get(G_String(t), "toLowerCase")()
        tags = J.get((_t1 if J.truthy(_t1 := J.get(opt, "tags")) else J.JSArray([])), "map")(_f2)
        if (J.sne(myDirFilter, "all") and J.seq(J.get(tags, "indexOf")(myDirFilter), (-1))):
            return False
        if J.sne(myTypeFilter, "all"):
            wantType = ("call" if J.seq(myTypeFilter, "calls") else "put")
            optTypeStr = J.get((_t3 if J.truthy(_t3 := J.get(opt, "type")) else ""), "toLowerCase")()
            if (J.sne(optTypeStr, wantType) and J.seq(J.get(tags, "indexOf")(wantType), (-1))):
                return False
        if (J.sne(myMoneyFilter, "all") and J.seq(J.get(tags, "indexOf")(myMoneyFilter), (-1))):
            return False
        if J.sne(myExecFilter, "all"):
            wantTags = execTagsForFilter(myExecFilter)
            def _f4(t=J.undefined, *_args):
                return J.sne(J.get(tags, "indexOf")(t), (-1))
            matched = J.get(wantTags, "some")(_f4)
            if (not J.truthy(matched)):
                return False
        if (J.seq(mySweepFilter, "sweep only") and J.seq(J.get(tags, "indexOf")("sweep"), (-1))):
            return False
        return True
    def sortRows(arr=J.undefined, field=J.undefined, *_args):
        _t1 = field
        if J.seq(_t1, "premium"):
            _t2 = 0
        elif J.seq(_t1, "oi%"):
            _t2 = 1
        elif J.seq(_t1, "size"):
            _t2 = 2
        elif J.seq(_t1, "dte"):
            _t2 = 3
        elif J.seq(_t1, "time"):
            _t2 = 4
        else:
            _t2 = 5
        _c3 = False
        for _once in (0,):
            if _t2 <= 0:
                def _f4(a=J.undefined, b=J.undefined, *_args):
                    return J.sub((_t1 if J.truthy(_t1 := J.get(b, "costBasis")) else 0), (_t2 if J.truthy(_t2 := J.get(a, "costBasis")) else 0))
                return J.get(J.get(arr, "slice")(), "sort")(_f4)
            if _t2 <= 1:
                def _f5(a=J.undefined, b=J.undefined, *_args):
                    return J.sub((_t1 if J.truthy(_t1 := J.get(b, "oiPercent")) else 0), (_t2 if J.truthy(_t2 := J.get(a, "oiPercent")) else 0))
                return J.get(J.get(arr, "slice")(), "sort")(_f5)
            if _t2 <= 2:
                def _f6(a=J.undefined, b=J.undefined, *_args):
                    return J.sub((_t1 if J.truthy(_t1 := J.get(b, "size")) else 0), (_t2 if J.truthy(_t2 := J.get(a, "size")) else 0))
                return J.get(J.get(arr, "slice")(), "sort")(_f6)
            if _t2 <= 3:
                def _f7(a=J.undefined, b=J.undefined, *_args):
                    aDte = (J.get(a, "daysToExp") if ((J.get(a, "daysToExp") is not J.undefined) and (J.get(a, "daysToExp") is not None)) else G_Infinity)
                    bDte = (J.get(b, "daysToExp") if ((J.get(b, "daysToExp") is not J.undefined) and (J.get(b, "daysToExp") is not None)) else G_Infinity)
                    return J.sub(aDte, bDte)
                return J.get(J.get(arr, "slice")(), "sort")(_f7)
            if _t2 <= 5:
                def _f8(a=J.undefined, b=J.undefined, *_args):
                    return J.sub(J.get(b, "timestamp"), J.get(a, "timestamp"))
                return J.get(J.get(arr, "slice")(), "sort")(_f8)
            pass
    def fetchAndFilter(*_args):
        try:
            data = J.get(G_request, "unusual_options")(J.get(G_current, "ticker"))
            if ((((not J.truthy(data)) or J.truthy(J.get(data, "error"))) or (not J.truthy(J.get(G_Array, "isArray")(data)))) or J.seq(J.get(data, "length"), 0)):
                return J.JSArray([])
            filtered = J.get(data, "filter")(passesFilters)
            sorted = sortRows(filtered, mySortBy)
            return J.get(sorted, "slice")(0, myMaxRows)
        except Exception as _e1:
            e = J.catch_value(_e1)
            J.get(G_console, "error")("Unusual Options Table v2.4 error:", e)
            return J.JSArray([])
    def computeFooter(opts=J.undefined, *_args):
        totalPrem = 0
        callPrem = 0
        putPrem = 0
        def _f1(o=J.undefined, *_args):
            nonlocal totalPrem, callPrem, putPrem
            prem = (_t1 if J.truthy(_t1 := J.get(o, "costBasis")) else 0)
            totalPrem = J.add(totalPrem, prem)
            typeStr = J.get((_t2 if J.truthy(_t2 := J.get(o, "type")) else ""), "toLowerCase")()
            if J.seq(typeStr, "call"):
                callPrem = J.add(callPrem, prem)
            elif J.seq(typeStr, "put"):
                putPrem = J.add(putPrem, prem)
        J.get(opts, "forEach")(_f1)
        cpRatio = "-"
        if J.gt(putPrem, 0):
            cpRatio = J.get(J.div(callPrem, putPrem), "toFixed")(2)
        elif J.gt(callPrem, 0):
            cpRatio = "calls only"
        return J.obj(("totalPrem", totalPrem), ("cpRatio", cpRatio), ("callPrem", callPrem), ("putPrem", putPrem))
    G_describe_indicator("Unusual Options Table", J.obj(("shortName", "Un Options Table v2")))
    myScale = J.get(G_input, "number")("UI Scale %", 100, J.obj(("min", 50), ("max", 300)))
    myMaxRows = J.get(G_input, "number")("Max Rows", 10, J.obj(("min", 1), ("max", 30)))
    myLookbackDays = J.get(G_input, "number")("Lookback (Days)", 2, J.obj(("min", 1)))
    myMinPremium = J.get(G_input, "number")("Min Prem $", 50000, J.obj(("min", 0), ("max", 100000000)))
    myMinOiPct = J.get(G_input, "number")("Min OI %", 0, J.obj(("min", 0), ("max", 10000)))
    myMaxDTE = J.get(G_input, "number")("Max DTE", 365, J.obj(("min", 0), ("max", 3650)))
    myDirFilter = J.get(G_input, "select")("Direction", "all", J.JSArray(["all", "bullish", "bearish", "neutral"]))
    myTypeFilter = J.get(G_input, "select")("Type", "all", J.JSArray(["all", "calls", "puts"]))
    myMoneyFilter = J.get(G_input, "select")("Moneyness", "all", J.JSArray(["all", "itm", "atm", "otm"]))
    myExecFilter = J.get(G_input, "select")("Execution", "all", J.JSArray(["all", "ask-side", "at ask", "above ask", "bid-side", "at bid", "below bid", "midpoint", "aggressive (any side)"]))
    mySweepFilter = J.get(G_input, "select")("Sweep", "all", J.JSArray(["all", "sweep only"]))
    mySortBy = J.get(G_input, "select")("Sort By", "time", J.JSArray(["time", "premium", "oi%", "size", "dte"]))
    scale = J.div(myScale, 100)
    BODY_FS = fs(11)
    HEADER_FS = fs(12)
    displayOptions = fetchAndFilter()
    footer = computeFooter(displayOptions)
    filterParts = J.JSArray([])
    if J.sne(myDirFilter, "all"):
        J.get(filterParts, "push")(myDirFilter)
    if J.sne(myTypeFilter, "all"):
        J.get(filterParts, "push")(myTypeFilter)
    if J.sne(myMoneyFilter, "all"):
        J.get(filterParts, "push")(J.get(myMoneyFilter, "toUpperCase")())
    if J.sne(myExecFilter, "all"):
        J.get(filterParts, "push")(myExecFilter)
    if J.seq(mySweepFilter, "sweep only"):
        J.get(filterParts, "push")("sweep")
    if J.gt(myMinOiPct, 0):
        J.get(filterParts, "push")(J.add(J.add("OI≥", myMinOiPct), "%"))
    if J.lt(myMaxDTE, 365):
        J.get(filterParts, "push")(J.add("DTE≤", myMaxDTE))
    if J.sne(mySortBy, "time"):
        J.get(filterParts, "push")(J.add("sort:", mySortBy))
    filterChip = J.get(filterParts, "join")(", ")
    MAX_CHIP_LEN = 70
    if J.gt(J.get(filterChip, "length"), MAX_CHIP_LEN):
        filterChip = J.add(J.get(filterChip, "substring")(0, J.sub(MAX_CHIP_LEN, 3)), "...")
    titleText = J.add(J.add(J.get(G_current, "ticker"), ": Unusual Options"), (J.add(J.add("  [", filterChip), "]") if J.truthy(filterChip) else ""))
    rows = J.JSArray([])
    padTitle = J.add(J.add(px(5), " "), px(7))
    padHeader = J.add(J.add(px(3), " "), px(7))
    padCell = J.add(J.add(px(3), " "), px(7))
    padPrem = J.add(J.add(px(3), " "), px(10))
    padFoot = J.add(J.add(px(4), " "), px(7))
    padFootR = J.add(J.add(px(4), " "), px(10))
    padEmpty = J.add(J.add(px(8), " "), px(7))
    J.get(rows, "push")(J.obj(("cells", J.JSArray([J.obj(("colspan", 8), ("text", titleText), ("color", "#FFF600"), ("padding", padTitle), ("textAlign", "center"), ("borderBottom", "1px solid orange"), ("fontWeight", "bold"), ("fontSize", HEADER_FS), ("background", "#000000"))]))))
    J.get(rows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", "Time"), ("color", "yellow"), ("padding", padHeader), ("fontWeight", "bold")), J.obj(("text", "Exp"), ("color", "yellow"), ("padding", padHeader), ("fontWeight", "bold")), J.obj(("text", "Strike"), ("color", "yellow"), ("padding", padHeader), ("fontWeight", "bold"), ("textAlign", "right")), J.obj(("text", "Type"), ("color", "yellow"), ("padding", padHeader), ("fontWeight", "bold")), J.obj(("text", "Size"), ("color", "yellow"), ("padding", padHeader), ("fontWeight", "bold"), ("textAlign", "right")), J.obj(("text", "OI%"), ("color", "yellow"), ("padding", padHeader), ("fontWeight", "bold"), ("textAlign", "right")), J.obj(("text", "Premium"), ("color", "yellow"), ("padding", padPrem), ("fontWeight", "bold"), ("textAlign", "right")), J.obj(("text", "Tags"), ("color", "yellow"), ("padding", padHeader), ("fontWeight", "bold"))]))))
    J.get(rows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", ""), ("colspan", 8), ("borderBottom", "1px solid orange"))]))))
    if J.seq(J.get(displayOptions, "length"), 0):
        J.get(rows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", J.add(J.add("No matches for ", J.get(G_current, "ticker")), " with current filters")), ("colspan", 8), ("color", "#aaaaaa"), ("padding", padEmpty), ("textAlign", "center"))]))))
    else:
        def _f1(opt=J.undefined, *_args):
            def _f2(t=J.undefined, *_args):
                return J.get(G_String(t), "toLowerCase")()
            tagsLower = J.get((_t1 if J.truthy(_t1 := J.get(opt, "tags")) else J.JSArray([])), "map")(_f2)
            isSweep = J.sne(J.get(tagsLower, "indexOf")("sweep"), (-1))
            rowBg = getRowBackground(J.get(opt, "tags"))
            timeStr = formatTime(J.get(opt, "timestamp"))
            expStr = "?"
            dte = J.get(opt, "daysToExp")
            expDateShort = (_t3 if J.truthy(_t3 := J.get(opt, "expDateFormatted")) else "")
            if (((dte is not J.undefined) and (dte is not None)) and J.truthy(expDateShort)):
                expStr = J.add(J.add(J.add(dte, " ("), expDateShort), ")")
            elif ((dte is not J.undefined) and (dte is not None)):
                expStr = G_String(dte)
            elif J.truthy(expDateShort):
                expStr = expDateShort
            strikeText = (J.add("$", J.get(G_parseFloat(J.get(opt, "strike")), "toFixed")((1 if J.lt(G_parseFloat(J.get(opt, "strike")), 100) else 0))) if J.truthy(J.get(opt, "strike")) else "N/A")
            typeChar = (J.get(J.get(G_String(J.get(opt, "type")), "charAt")(0), "toUpperCase")() if J.truthy(J.get(opt, "type")) else "?")
            typeStr = (J.add("⚡", typeChar) if J.truthy(isSweep) else typeChar)
            typeColor = getTypeColor(J.get(opt, "type"))
            sizeStr = (formatNumber(J.get(opt, "size")) if J.truthy(J.get(opt, "size")) else "N/A")
            oiPct = J.get(opt, "oiPercent")
            oiPctStr = (J.add(J.get(oiPct, "toFixed")(1), "%") if ((oiPct is not J.undefined) and (oiPct is not None)) else "-")
            oiPctColor = getOiPctColor(oiPct)
            premiumStr = formatCurrency(J.get(opt, "costBasis"))
            tagsStr = (J.get(J.get(opt, "tags"), "join")(", ") if (J.truthy(J.get(opt, "tags")) and J.gt(J.get(J.get(opt, "tags"), "length"), 0)) else "-")
            J.get(rows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", timeStr), ("color", "#f0f0f0"), ("padding", padCell), ("background", rowBg)), J.obj(("text", expStr), ("color", "#f0f0f0"), ("padding", padCell), ("background", rowBg)), J.obj(("text", strikeText), ("color", "#f0f0f0"), ("padding", padCell), ("background", rowBg), ("textAlign", "right")), J.obj(("text", typeStr), ("color", typeColor), ("padding", padCell), ("background", rowBg), ("fontWeight", "bold")), J.obj(("text", sizeStr), ("color", "#f0f0f0"), ("padding", padCell), ("background", rowBg), ("textAlign", "right")), J.obj(("text", oiPctStr), ("color", oiPctColor), ("padding", padCell), ("background", rowBg), ("textAlign", "right"), ("fontWeight", "bold")), J.obj(("text", premiumStr), ("color", "#f0f0f0"), ("padding", padPrem), ("background", rowBg), ("textAlign", "right")), J.obj(("text", tagsStr), ("color", "#cccccc"), ("padding", padCell), ("background", rowBg))]))))
        J.get(displayOptions, "forEach")(_f1)
        J.get(rows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", ""), ("colspan", 8), ("borderTop", "1px solid orange"))]))))
        J.get(rows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", J.add("Total: ", formatCurrency(J.get(footer, "totalPrem")))), ("colspan", 4), ("color", "#FFDC61"), ("padding", padFoot), ("fontWeight", "bold"), ("background", "#1a2025")), J.obj(("text", J.add("C/P Prem: ", J.get(footer, "cpRatio"))), ("colspan", 4), ("color", "#FFDC61"), ("padding", padFootR), ("textAlign", "right"), ("fontWeight", "bold"), ("background", "#1a2025"))]))))
    G_paint_overlay("Unusual Options Table v2.4", J.obj(("position", "bottom_left"), ("order", "above_all")), J.obj(("fontSize", BODY_FS), ("border", "1px solid orange"), ("background", "#2a353b"), ("rows", rows)))


register_store_indicator(
    script,
    name='unusual_options_table_TS',
    title='Unusual Options Table',
    developer='Rock Regan',
    url='https://trendspider.com/trading-tools-store/indicators/68a3e6-unusual-options-table/',
    position='price',
    inputs=[{'id': 'ui_scale__', 'title': 'UI Scale %', 'type': 'number', 'default': 100}, {'id': 'max_rows', 'title': 'Max Rows', 'type': 'number', 'default': 10}, {'id': 'lookback__days_', 'title': 'Lookback (Days)', 'type': 'number', 'default': 2}, {'id': 'min_prem__', 'title': 'Min Prem $', 'type': 'number', 'default': 50000}, {'id': 'min_oi__', 'title': 'Min OI %', 'type': 'number', 'default': 0}, {'id': 'max_dte', 'title': 'Max DTE', 'type': 'number', 'default': 365}, {'id': 'direction', 'title': 'Direction', 'type': 'select_wide', 'default': 'all', 'options': ['all', 'bullish', 'bearish', 'neutral']}, {'id': 'type', 'title': 'Type', 'type': 'select_wide', 'default': 'all', 'options': ['all', 'calls', 'puts']}, {'id': 'moneyness', 'title': 'Moneyness', 'type': 'select_wide', 'default': 'all', 'options': ['all', 'itm', 'atm', 'otm']}, {'id': 'execution', 'title': 'Execution', 'type': 'select_wide', 'default': 'all', 'options': ['all', 'ask-side', 'at ask', 'above ask', 'bid-side', 'at bid', 'below bid', 'midpoint', 'aggressive (any side)']}, {'id': 'sweep', 'title': 'Sweep', 'type': 'select_wide', 'default': 'all', 'options': ['all', 'sweep only']}, {'id': 'sort_by', 'title': 'Sort By', 'type': 'select_wide', 'default': 'time', 'options': ['time', 'premium', 'oi%', 'size', 'dte']}],
    outputs=[],
    signals=[],
    requires=['unusual_options'],
    parity='exact',
)
