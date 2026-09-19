"""
Options Term Structure Hunter v1 -- TrendSpider store indicator by Rock Regan.

Registered as "options_term_structure_hunter_v1_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68ab9f-options-term-structure-hunter-v1/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
aapl_d: both-error, syn_5m: both-error.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_Object = G["Object"]
    G_String = G["String"]
    G_assert = G["assert"]
    G_close = G["close"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_input = G["input"]
    G_isFinite = G["isFinite"]
    G_paint_overlay = G["paint_overlay"]
    G_parseFloat = G["parseFloat"]
    G_parseInt = G["parseInt"]
    G_request = G["request"]
    def scaleVal(n=J.undefined, *_args):
        return J.get(G_Math, "max")(1, J.get(G_Math, "round")(J.div(J.mul(n, uiScale), 100)))
    def px(n=J.undefined, *_args):
        return J.add(scaleVal(n), "px")
    def normCDF(x=J.undefined, *_args):
        a1 = 0.254829592
        a2 = (-0.284496736)
        a3 = 1.421413741
        a4 = (-1.453152027)
        a5 = 1.061405429
        p = 0.3275911
        s = ((-1) if J.lt(x, 0) else 1)
        x = J.div(J.get(G_Math, "abs")(x), J.get(G_Math, "sqrt")(2))
        t = J.div(1, J.add(1, J.mul(p, x)))
        y = J.sub(1, J.mul(J.mul(J.add(J.mul(J.add(J.mul(J.add(J.mul(J.add(J.mul(a5, t), a4), t), a3), t), a2), t), a1), t), J.get(G_Math, "exp")(J.mul(J.neg(x), x))))
        return J.mul(0.5, J.add(1, J.mul(s, y)))
    def normPDF(x=J.undefined, *_args):
        return J.div(J.get(G_Math, "exp")(J.mul(J.mul((-0.5), x), x)), J.get(G_Math, "sqrt")(J.mul(2, J.get(G_Math, "PI"))))
    def blackScholesCall(S_2=J.undefined, K=J.undefined, T=J.undefined, r=J.undefined, s=J.undefined, *_args):
        if J.le(T, 0):
            return J.get(G_Math, "max")(J.sub(S_2, K), 0)
        q = J.get(G_Math, "sqrt")(T)
        d1 = J.div(J.add(J.get(G_Math, "log")(J.div(S_2, K)), J.mul(J.add(r, J.mul(J.mul(0.5, s), s)), T)), J.mul(s, q))
        d2 = J.sub(d1, J.mul(s, q))
        return J.sub(J.mul(S_2, normCDF(d1)), J.mul(J.mul(K, J.get(G_Math, "exp")(J.mul(J.neg(r), T))), normCDF(d2)))
    def blackScholesPut(S_2=J.undefined, K=J.undefined, T=J.undefined, r=J.undefined, s=J.undefined, *_args):
        if J.le(T, 0):
            return J.get(G_Math, "max")(J.sub(K, S_2), 0)
        q = J.get(G_Math, "sqrt")(T)
        d1 = J.div(J.add(J.get(G_Math, "log")(J.div(S_2, K)), J.mul(J.add(r, J.mul(J.mul(0.5, s), s)), T)), J.mul(s, q))
        d2 = J.sub(d1, J.mul(s, q))
        return J.sub(J.mul(J.mul(K, J.get(G_Math, "exp")(J.mul(J.neg(r), T))), normCDF(J.neg(d2))), J.mul(S_2, normCDF(J.neg(d1))))
    def calculateIV(mkt=J.undefined, S_2=J.undefined, K=J.undefined, T=J.undefined, r=J.undefined, isCall=J.undefined, *_args):
        if ((J.le(T, 0) or J.le(mkt, 0)) or (not J.truthy(G_isFinite(mkt)))):
            return None
        s = 0.2
        it = 50
        tol = 0.0001
        q = J.get(G_Math, "sqrt")(T)
        i = 0
        while J.lt(i, it):
            price = (blackScholesCall(S_2, K, T, r, s) if J.truthy(isCall) else blackScholesPut(S_2, K, T, r, s))
            diff = J.sub(price, mkt)
            if J.lt(J.get(G_Math, "abs")(diff), tol):
                return s
            d1 = J.div(J.add(J.get(G_Math, "log")(J.div(S_2, K)), J.mul(J.add(r, J.mul(J.mul(0.5, s), s)), T)), J.mul(s, q))
            vega = J.mul(J.mul(S_2, q), normPDF(d1))
            if (J.lt(vega, 0.000001) or (not J.truthy(G_isFinite(vega)))):
                break
            s = J.sub(s, J.div(diff, vega))
            if J.lt(s, 0.001):
                s = 0.001
            if J.gt(s, 5):
                s = 5
            i = J.inc(i)
        return (s if (J.gt(s, 0.001) and J.lt(s, 5)) else None)
    def calculateTermStructure(expiryData=J.undefined, *_args):
        structure = J.JSArray([])
        i = 0
        while J.lt(i, J.get(expiryData, "length")):
            e = J.get(expiryData, i)
            J.get(structure, "push")(J.obj(("expiry", J.get(e, "expiry")), ("tte", J.get(e, "tte")), ("dte", J.get(e, "dteDisplay")), ("avgCallIV", J.get(e, "avgCallIV")), ("avgPutIV", J.get(e, "avgPutIV")), ("avgIV", J.div(J.add(J.get(e, "avgCallIV"), J.get(e, "avgPutIV")), 2))))
            i = J.inc(i)
        alerts = J.JSArray([])
        i_2 = 1
        while J.lt(i_2, J.get(structure, "length")):
            p = J.get(structure, J.sub(i_2, 1))
            c = J.get(structure, i_2)
            if J.gt(J.get(p, "avgIV"), J.mul(J.get(c, "avgIV"), 1.15)):
                J.get(alerts, "push")(J.add(J.add(J.add(J.add(J.add(J.add(J.add(J.add("⚠️ INVERTED: ", J.get(p, "dte")), "D ("), J.get(J.mul(J.get(p, "avgIV"), 100), "toFixed")(0)), "%) > "), J.get(c, "dte")), "D ("), J.get(J.mul(J.get(c, "avgIV"), 100), "toFixed")(0)), "%)"))
            if J.gt(J.get(c, "avgIV"), J.mul(J.get(p, "avgIV"), 1.25)):
                J.get(alerts, "push")(J.add(J.add(J.add(J.add("\ud83d\udcc8 STEEP: RESEARCH ", J.get(c, "dte")), "D options ("), J.get(J.mul(J.sub(J.get(c, "avgIV"), J.get(p, "avgIV")), 100), "toFixed")(0)), "% premium to front)"))
            i_2 = J.inc(i_2)
        signal = "NEUTRAL"
        confidence = "MEDIUM"
        if J.ge(J.get(structure, "length"), 3):
            f = J.get(J.get(structure, 0), "avgIV")
            m = J.get(J.get(structure, J.bit_or(J.div(J.get(structure, "length"), 2), 0)), "avgIV")
            b = J.get(J.get(structure, J.sub(J.get(structure, "length"), 1)), "avgIV")
            if ((J.gt(f, m) and J.gt(m, b)) and J.gt(f, J.mul(b, 1.2))):
                signal = "RESEARCH_LONGER_TERM"
                confidence = "HIGH"
            elif J.gt(b, J.mul(f, 1.1)):
                signal = "AVOID_LONGER_TERM"
                confidence = "HIGH"
        return J.obj(("structure", structure), ("alerts", alerts), ("signal", signal), ("confidence", confidence))
    def interpolateExpectedIV(t=J.undefined, pts=J.undefined, *_args):
        if ((not J.truthy(pts)) or J.seq(J.get(pts, "length"), 0)):
            return None
        if J.seq(J.get(pts, "length"), 1):
            return J.get(J.get(pts, 0), "iv")
        lo = None
        hi = None
        i = 0
        while J.lt(i, J.get(pts, "length")):
            p = J.get(pts, i)
            if J.le(J.get(p, "tte"), t):
                lo = p
            if (J.ge(J.get(p, "tte"), t) and (hi is None)):
                hi = p
            i = J.inc(i)
        if ((not J.truthy(lo)) and J.truthy(hi)):
            return J.get(hi, "iv")
        if (J.truthy(lo) and (not J.truthy(hi))):
            return J.get(lo, "iv")
        if ((not J.truthy(lo)) and (not J.truthy(hi))):
            return None
        if J.seq(J.get(lo, "tte"), J.get(hi, "tte")):
            return J.get(lo, "iv")
        r = J.div(J.sub(t, J.get(lo, "tte")), J.sub(J.get(hi, "tte"), J.get(lo, "tte")))
        return J.add(J.get(lo, "iv"), J.mul(r, J.sub(J.get(hi, "iv"), J.get(lo, "iv"))))
    def getMoneynessBiasedExpectedIV(strike=J.undefined, expiry=J.undefined, allData=J.undefined, S_2=J.undefined, *_args):
        if J.seq(J.get(allData, "length"), 1):
            expiryData = J.get(allData, 0)
            moneyness = J.div(strike, S_2)
            baseIV = (J.div(J.add(J.get(expiryData, "avgCallIV"), J.get(expiryData, "avgPutIV")), 2) if (J.truthy(J.get(expiryData, "avgCallIV")) and J.truthy(J.get(expiryData, "avgPutIV"))) else ivFallback)
            atmDistance = J.get(G_Math, "abs")(J.sub(moneyness, 1))
            ivAdjustment = J.get(G_Math, "max")(0, J.sub(0.05, J.mul(atmDistance, 0.1)))
            return J.get(G_Math, "min")(J.add(baseIV, ivAdjustment), J.mul(baseIV, 1.2))
        def _f1(d=J.undefined, *_args):
            return J.obj(("tte", J.get(d, "tte")), ("iv", J.div(J.add(J.get(d, "avgCallIV"), J.get(d, "avgPutIV")), 2)))
        curve = J.get(allData, "map")(_f1)
        return interpolateExpectedIV(J.get(expiry, "tte"), curve)
    def findMispricedStrikes(all=J.undefined, ts_2=J.undefined, S_2=J.undefined, *_args):
        out = J.JSArray([])
        def _f1(s=J.undefined, *_args):
            return J.obj(("tte", J.get(s, "tte")), ("iv", J.get(s, "avgIV")))
        curve = J.get(J.get(ts_2, "structure"), "map")(_f1)
        isSingleExpiry = J.seq(J.get(curve, "length"), 1)
        map = J.obj()
        i = 0
        while J.lt(i, J.get(all, "length")):
            e = J.get(all, i)
            j = 0
            while J.lt(j, J.get(J.get(e, "strikes"), "length")):
                st = J.get(J.get(e, "strikes"), j)
                k = J.get(st, "strike")
                J.get((_t2 if J.truthy(_t2 := J.get(map, k)) else J.set(map, k, J.JSArray([]))), "push")(J.obj(("expiry", J.get(e, "expiry")), ("tte", J.get(e, "tte")), ("dteDisplay", J.get(e, "dteDisplay")), ("callIV", J.get(st, "callIV")), ("putIV", J.get(st, "putIV")), ("callPrice", J.get(st, "callPrice")), ("putPrice", J.get(st, "putPrice")), ("callBid", J.get(st, "callBid")), ("callAsk", J.get(st, "callAsk")), ("putBid", J.get(st, "putBid")), ("putAsk", J.get(st, "putAsk")), ("callOI", J.get(st, "callOI")), ("putOI", J.get(st, "putOI"))))
                j = J.inc(j)
            i = J.inc(i)
        keys = J.get(G_Object, "keys")(map)
        i_2 = 0
        while J.lt(i_2, J.get(keys, "length")):
            K = G_parseFloat(J.get(keys, i_2))
            if (not J.truthy(G_isFinite(K))):
                i_2 = J.inc(i_2)
                continue
            m = J.div(K, S_2)
            if (J.lt(m, moneynessMin) or J.gt(m, moneynessMax)):
                i_2 = J.inc(i_2)
                continue
            list = J.get(map, J.get(keys, i_2))
            j_2 = 0
            while J.lt(j_2, J.get(list, "length")):
                o = J.get(list, j_2)
                expected = J.undefined
                if J.truthy(isSingleExpiry):
                    expected = getMoneynessBiasedExpectedIV(K, o, all, S_2)
                else:
                    expected = interpolateExpectedIV(J.get(o, "tte"), curve)
                if (not J.truthy(expected)):
                    j_2 = J.inc(j_2)
                    continue
                dteDisp = (J.get(o, "dteDisplay") if (J.get(o, "dteDisplay") is not J.undefined) else J.get(G_Math, "max")(1, J.get(G_Math, "round")(J.mul(J.get(o, "tte"), 365.25))))
                if ((J.truthy(J.get(o, "callIV")) and J.sne(J.get(o, "callIV"), ivFallback)) and J.ge(J.get(o, "callOI"), oiMin)):
                    mis = J.div(J.sub(expected, J.get(o, "callIV")), expected)
                    ask = (_t5 if J.truthy(_t5 := J.get(o, "callAsk")) else 0)
                    bid = (_t6 if J.truthy(_t6 := J.get(o, "callBid")) else 0)
                    spread = (J.sub(ask, bid) if (J.gt(ask, 0) and J.ge(bid, 0)) else 0)
                    spPct = (J.mul(J.div(spread, ask), 100) if J.gt(ask, 0) else 1000)
                    if ((J.ge(J.mul(J.get(G_Math, "abs")(mis), 100), mispricingThreshold) and J.le(spPct, maxSpreadPct)) and J.gt(bid, 0)):
                        J.get(out, "push")(J.obj(("strike", K), ("expiry", J.get(o, "expiry")), ("tte", J.get(o, "tte")), ("dte", dteDisp), ("type", "CALL"), ("actualIV", J.get(o, "callIV")), ("expectedIV", expected), ("mispricing", mis), ("mispricingPct", J.mul(mis, 100)), ("price", (_t7 if J.truthy(_t7 := J.get(o, "callPrice")) else 0)), ("bid", bid), ("ask", ask), ("oi", J.get(o, "callOI")), ("moneyness", m), ("signal", ("CHEAP" if J.gt(mis, 0) else "EXPENSIVE"))))
                if ((J.truthy(J.get(o, "putIV")) and J.sne(J.get(o, "putIV"), ivFallback)) and J.ge(J.get(o, "putOI"), oiMin)):
                    mis_2 = J.div(J.sub(expected, J.get(o, "putIV")), expected)
                    ask_2 = (_t8 if J.truthy(_t8 := J.get(o, "putAsk")) else 0)
                    bid_2 = (_t9 if J.truthy(_t9 := J.get(o, "putBid")) else 0)
                    spread_2 = (J.sub(ask_2, bid_2) if (J.gt(ask_2, 0) and J.ge(bid_2, 0)) else 0)
                    spPct_2 = (J.mul(J.div(spread_2, ask_2), 100) if J.gt(ask_2, 0) else 1000)
                    if ((J.ge(J.mul(J.get(G_Math, "abs")(mis_2), 100), mispricingThreshold) and J.le(spPct_2, maxSpreadPct)) and J.gt(bid_2, 0)):
                        J.get(out, "push")(J.obj(("strike", K), ("expiry", J.get(o, "expiry")), ("tte", J.get(o, "tte")), ("dte", dteDisp), ("type", "PUT"), ("actualIV", J.get(o, "putIV")), ("expectedIV", expected), ("mispricing", mis_2), ("mispricingPct", J.mul(mis_2, 100)), ("price", (_t10 if J.truthy(_t10 := J.get(o, "putPrice")) else 0)), ("bid", bid_2), ("ask", ask_2), ("oi", J.get(o, "putOI")), ("moneyness", m), ("signal", ("CHEAP" if J.gt(mis_2, 0) else "EXPENSIVE"))))
                j_2 = J.inc(j_2)
            i_2 = J.inc(i_2)
        def _f11(a=J.undefined, b=J.undefined, *_args):
            return J.sub(J.get(G_Math, "abs")(J.get(b, "mispricing")), J.get(G_Math, "abs")(J.get(a, "mispricing")))
        J.get(out, "sort")(_f11)
        return out
    def txtCell(t=J.undefined, bg=J.undefined, align=J.undefined, bold=J.undefined, color=J.undefined, fontSize=J.undefined, *_args):
        cell = J.obj(("text", t), ("color", (_t1 if J.truthy(_t1 := color) else "var(--text-color)")), ("background", (_t2 if J.truthy(_t2 := bg) else "var(--background-color)")), ("textAlign", (_t3 if J.truthy(_t3 := align) else "center")), ("fontWeight", ("bold" if J.truthy(bold) else "normal")), ("paddingTop", scaleVal(2)), ("paddingBottom", scaleVal(2)), ("paddingLeft", scaleVal(3)), ("paddingRight", scaleVal(3)))
        if J.truthy(fontSize):
            J.set(cell, "fontSize", fontSize)
        else:
            J.set(cell, "fontSize", J.get(baseFont, "totals"))
        return cell
    def headerCell(t=J.undefined, *_args):
        return txtCell(t, "#14252f", "center", True, C_FOOTER_TX_DIM, J.get(baseFont, "header"))
    def fullRow(text=J.undefined, bg=J.undefined, bold=J.undefined, color=J.undefined, fontSize=J.undefined, *_args):
        cell = J.obj(("text", text), ("color", (_t1 if J.truthy(_t1 := color) else "var(--text-color)")), ("background", (_t2 if J.truthy(_t2 := bg) else "var(--background-color)")), ("colspan", COLS), ("textAlign", "center"), ("fontWeight", ("bold" if J.truthy(bold) else "normal")), ("paddingTop", scaleVal(2)), ("paddingBottom", scaleVal(2)), ("paddingLeft", scaleVal(3)), ("paddingRight", scaleVal(3)), ("fontSize", (_t3 if J.truthy(_t3 := fontSize) else J.get(baseFont, "totals"))))
        return J.obj(("cells", J.JSArray([cell])))
    G_describe_indicator("Options Term Structure Hunter v1.1", J.obj(("shortName", "Structure Hunter v1.1")))
    shortName = "Structure Hunter v1.1"
    maxExpiries = J.get(G_input, "number")("Max Expiries to Analyze", 6, J.obj(("min", 2), ("max", 10)))
    showDetailsFlag = J.get(G_input, "boolean")("Show Details Table", True)
    topMispricedN = J.get(G_input, "number")("Top Mispriced Strikes", 5, J.obj(("min", 3), ("max", 10)))
    mispricingThreshold = J.get(G_input, "number")("Mispricing Threshold %", 10, J.obj(("min", 5), ("max", 50)))
    termStructureAlert = J.get(G_input, "boolean")("Term Structure Alerts", True)
    riskFreeRate = J.div(J.get(G_input, "number")("Risk Free Rate %", 4.2, J.obj(("min", 0), ("max", 20), ("step", 0.1))), 100)
    ivFallback = J.div(J.get(G_input, "number")("IV Fallback %", 30, J.obj(("min", 15), ("max", 60))), 100)
    showOIColumn = J.get(G_input, "boolean")("Show OI Column", False)
    maxBannerIdeas = J.get(G_input, "number")("Max Banner Ideas", 3, J.obj(("min", 1), ("max", 4)))
    uiScale = J.get(G_input, "number")("UI Scale (%)", 100, J.obj(("min", 50), ("max", 150), ("step", 5)))
    oiMin = J.get(G_input, "number")("Min Open Interest", 25, J.obj(("min", 0), ("max", 500), ("step", 5)))
    maxSpreadPct = J.get(G_input, "number")("Max Spread % of Ask", 40, J.obj(("min", 5), ("max", 80), ("step", 1)))
    moneynessMin = J.get(G_input, "number")("Moneyness Min (K/S)", 0.7, J.obj(("min", 0.3), ("max", 1), ("step", 0.01)))
    moneynessMax = J.get(G_input, "number")("Moneyness Max (K/S)", 1.3, J.obj(("min", 1), ("max", 3), ("step", 0.01)))
    UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    assetType = ("etf" if J.seq(J.get(G_current, "assetType"), "etf") else "stocks")
    SHOW_DETAILS = showDetailsFlag
    SHOW_ALERTS = termStructureAlert
    C_HEADER_BG = "#1E90FF"
    C_HEADER_TX = "#FFFFFF"
    C_BANNER_GOOD = "#00CC00"
    C_BANNER_GOOD_TX = "#FFFFFF"
    C_RESEARCH_BG = "#009900"
    C_RESEARCH_TX = "#FFFFFF"
    C_EMPTY_BG = "#FF8800"
    C_EMPTY_TX = "#FFFFFF"
    C_CONTEXT_BG = "#008B8B"
    C_CONTEXT_TX = "#FFFFFF"
    C_ALERT_BG = "#CCAC02"
    C_ALERT_TX = "#000000"
    C_DISC_STRONG_BG = "#00B300"
    C_DISC_WEAK_BG = "#28A745"
    C_DISC_TX = "#FFFFFF"
    C_SPREAD_WARN = "#FF4500"
    C_SPREAD_MED = "#FF8C00"
    C_SPREAD_TX = "#FFFFFF"
    C_FOOTER_BG1 = "#2a353b"
    C_FOOTER_BG2 = "#333333"
    C_FOOTER_TX_DIM = "#00F7FF"
    baseFont = J.obj(("header", px(12)), ("totals", px(12)), ("ratios", px(11)), ("small", px(10)))
    url = J.template("https://api.nasdaq.com/api/quote/", J.get(G_current, "symbol"), "/option-chain?assetclass=", assetType, "&limit=1000")
    optionsData = J.get(G_request, "http")(url, 300, J.obj(("user-agent", UA), ("accept", "application/json")))
    G_assert((not J.truthy(J.get(optionsData, "error"))), J.template("Error fetching options data: ", J.get(optionsData, "error")))
    myData = J.get(optionsData, "data")
    G_assert(myData, J.template("No data for ", J.get(G_current, "symbol")))
    rowsRaw = J.get(J.get(myData, "table"), "rows")
    G_assert((J.gt(J.get(rowsRaw, "length"), 0) if J.truthy(_t1 := rowsRaw) else _t1), "No option chain data rows found")
    S = J.get(G_close, J.sub(J.get(G_close, "length"), 1))
    seen = J.obj()
    expiries = J.JSArray([])
    i = 0
    while J.lt(i, J.get(rowsRaw, "length")):
        e = J.get(J.get(rowsRaw, i), "expiryDate")
        if (J.truthy(e) and (not J.truthy(J.get(seen, e)))):
            J.set(seen, e, 1)
            J.get(expiries, "push")(e)
        i = J.inc(i)
    selected = J.get(expiries, "slice")(0, maxExpiries)
    G_assert(J.gt(J.get(selected, "length"), 0), "No expiries available.")
    allExpiryData = J.JSArray([])
    i_2 = 0
    while J.lt(i_2, J.get(selected, "length")):
        exp = J.get(selected, i_2)
        expiryRows = J.JSArray([])
        j = 0
        while J.lt(j, J.get(rowsRaw, "length")):
            r = J.get(rowsRaw, j)
            if (J.seq(J.get(r, "expiryDate"), exp) and J.truthy(J.get(r, "strike"))):
                J.get(expiryRows, "push")(r)
            j = J.inc(j)
        if J.lt(J.get(expiryRows, "length"), 5):
            i_2 = J.inc(i_2)
            continue
        dteDisplay = J.add(i_2, 1)
        T = J.get(G_Math, "max")(J.div(1, 365), J.div(dteDisplay, 365.25))
        callIVs = J.JSArray([])
        putIVs = J.JSArray([])
        strikes = J.JSArray([])
        k = 0
        while J.lt(k, J.get(expiryRows, "length")):
            r_2 = J.get(expiryRows, k)
            K = G_parseFloat(J.get(r_2, "strike"))
            if (not J.truthy(G_isFinite(K))):
                k = J.inc(k)
                continue
            cOI = (_t2 if J.truthy(_t2 := G_parseInt(J.get(r_2, "c_Openinterest"))) else 0)
            pOI = (_t3 if J.truthy(_t3 := G_parseInt(J.get(r_2, "p_Openinterest"))) else 0)
            cBid = (_t4 if J.truthy(_t4 := G_parseFloat(J.get(r_2, "c_Bid"))) else 0)
            cAsk = (_t5 if J.truthy(_t5 := G_parseFloat(J.get(r_2, "c_Ask"))) else 0)
            cLast = (_t6 if J.truthy(_t6 := G_parseFloat(J.get(r_2, "c_Last"))) else 0)
            pBid = (_t7 if J.truthy(_t7 := G_parseFloat(J.get(r_2, "p_Bid"))) else 0)
            pAsk = (_t8 if J.truthy(_t8 := G_parseFloat(J.get(r_2, "p_Ask"))) else 0)
            pLast = (_t9 if J.truthy(_t9 := G_parseFloat(J.get(r_2, "p_Last"))) else 0)
            cMid = (J.mul(0.5, J.add(cBid, cAsk)) if (J.gt(cBid, 0) and J.gt(cAsk, 0)) else cLast)
            pMid = (J.mul(0.5, J.add(pBid, pAsk)) if (J.gt(pBid, 0) and J.gt(pAsk, 0)) else pLast)
            cIV = (calculateIV(cMid, S, K, T, riskFreeRate, True) if J.gt(cMid, 0.01) else None)
            pIV = (calculateIV(pMid, S, K, T, riskFreeRate, False) if J.gt(pMid, 0.01) else None)
            storeCallIV = J.undefined
            storePutIV = J.undefined
            if (((J.truthy(cIV) and J.gt(cIV, 0.05)) and J.lt(cIV, 3)) and J.truthy(G_isFinite(cIV))):
                storeCallIV = cIV
                J.get(callIVs, "push")(cIV)
            else:
                storeCallIV = ivFallback
            if (((J.truthy(pIV) and J.gt(pIV, 0.05)) and J.lt(pIV, 3)) and J.truthy(G_isFinite(pIV))):
                storePutIV = pIV
                J.get(putIVs, "push")(pIV)
            else:
                storePutIV = ivFallback
            J.get(strikes, "push")(J.obj(("strike", K), ("callIV", storeCallIV), ("putIV", storePutIV), ("callPrice", cLast), ("putPrice", pLast), ("callBid", cBid), ("callAsk", cAsk), ("putBid", pBid), ("putAsk", pAsk), ("callOI", cOI), ("putOI", pOI)))
            k = J.inc(k)
        def _f10(sum=J.undefined, iv=J.undefined, *_args):
            return J.add(sum, iv)
        avgC = (J.div(J.get(callIVs, "reduce")(_f10, 0), J.get(callIVs, "length")) if J.gt(J.get(callIVs, "length"), 0) else J.mul(ivFallback, J.add(1, J.mul(J.get(G_Math, "random")(), 0.2))))
        def _f11(sum=J.undefined, iv=J.undefined, *_args):
            return J.add(sum, iv)
        avgP = (J.div(J.get(putIVs, "reduce")(_f11, 0), J.get(putIVs, "length")) if J.gt(J.get(putIVs, "length"), 0) else J.mul(ivFallback, J.add(1, J.mul(J.get(G_Math, "random")(), 0.2))))
        J.get(allExpiryData, "push")(J.obj(("expiry", exp), ("tte", T), ("dteDisplay", dteDisplay), ("avgCallIV", avgC), ("avgPutIV", avgP), ("strikes", strikes)))
        i_2 = J.inc(i_2)
    G_assert(J.gt(J.get(allExpiryData, "length"), 0), "No valid expiry data after processing")
    ts = calculateTermStructure(allExpiryData)
    allMis = findMispricedStrikes(allExpiryData, ts, S)
    topMis = J.get(allMis, "slice")(0, topMispricedN)
    COLS = ((12 if J.truthy(showOIColumn) else 11) if J.truthy(SHOW_DETAILS) else 4)
    rows = J.JSArray([])
    analysisMode = ("Single-Expiry Analysis" if J.seq(J.get(allExpiryData, "length"), 1) else J.template(J.get(allExpiryData, "length"), "-Expiry Term Structure"))
    J.get(rows, "push")(fullRow(J.add(J.add(J.add(J.add(shortName, " | "), J.get(G_current, "symbol")), " | "), analysisMode), C_HEADER_BG, True, C_HEADER_TX, J.get(baseFont, "header")))
    def _f12(o=J.undefined, *_args):
        return J.seq(J.get(o, "signal"), "CHEAP")
    cheap = J.get(topMis, "filter")(_f12)
    def _f13(o=J.undefined, *_args):
        return J.seq(J.get(o, "signal"), "EXPENSIVE")
    expensive = J.get(topMis, "filter")(_f13)
    if J.gt(J.get(cheap, "length"), 0):
        J.get(rows, "push")(fullRow(J.template("\ud83c\udfaf ", J.get(cheap, "length"), " MISPRICED OPPORTUNITIES FOUND"), C_BANNER_GOOD, True, C_BANNER_GOOD_TX, J.get(baseFont, "totals")))
        lim = J.get(G_Math, "min")(maxBannerIdeas, J.get(cheap, "length"))
        i_3 = 0
        while J.lt(i_3, lim):
            o = J.get(cheap, i_3)
            conf = ("HIGH" if J.gt(J.get(G_Math, "abs")(J.get(o, "mispricingPct")), 30) else ("MEDIUM" if J.gt(J.get(G_Math, "abs")(J.get(o, "mispricingPct")), 20) else "LOW"))
            mny = ("OTM" if J.gt(J.get(o, "moneyness"), 1.02) else ("ITM" if J.lt(J.get(o, "moneyness"), 0.98) else "ATM"))
            urg = ("⚡" if J.le(J.get(o, "dte"), 14) else ("\ud83d\udcc8" if J.le(J.get(o, "dte"), 28) else "⏰"))
            J.get(rows, "push")(fullRow(J.template(urg, " RESEARCH: ", J.get(o, "strike"), " ", J.get(o, "type"), " ", J.get(o, "dte"), "D (", J.get(J.get(G_Math, "abs")(J.get(o, "mispricingPct")), "toFixed")(0), "% mispricing) ", mny, " - ", conf), C_RESEARCH_BG, True, C_RESEARCH_TX, J.get(baseFont, "totals")))
            i_3 = J.inc(i_3)
    else:
        reasonText = (J.template("⏳ NO MISPRICINGS FOUND - Single expiry analysis complete (Threshold: ", mispricingThreshold, "%)") if J.seq(J.get(allExpiryData, "length"), 1) else J.template("⏳ NO SIGNIFICANT MISPRICINGS FOUND (Threshold: ", mispricingThreshold, "%)"))
        J.get(rows, "push")(fullRow(reasonText, C_EMPTY_BG, True, C_EMPTY_TX, J.get(baseFont, "totals")))
    if J.gt(J.get(cheap, "length"), 0):
        def _f14(x=J.undefined, *_args):
            return J.le(J.get(x, "dte"), 14)
        st = J.get(J.get(cheap, "filter")(_f14), "length")
        def _f15(x=J.undefined, *_args):
            return J.gt(J.get(x, "dte"), 28)
        lt = J.get(J.get(cheap, "filter")(_f15), "length")
        ctx = ("⚡ SHORT-TERM FOCUS: Best opportunities in 0-7 DTE options" if J.gt(st, lt) else ("⏰ LONGER-TERM EDGE: Best opportunities in 30+ DTE options" if J.gt(lt, st) else "\ud83d\udcca MIXED OPPORTUNITIES: Good options across timeframes"))
        J.get(rows, "push")(fullRow(ctx, C_CONTEXT_BG, True, C_CONTEXT_TX, J.get(baseFont, "totals")))
        if (J.truthy(SHOW_ALERTS) and J.truthy(J.get(J.get(ts, "alerts"), "length"))):
            def _f16(z=J.undefined, *_args):
                return (_t1 if J.truthy(_t1 := J.ge(J.get(z, "indexOf")("INVERTED"), 0)) else J.ge(J.get(z, "indexOf")("STEEP"), 0))
            a = J.get(J.get(ts, "alerts"), "find")(_f16)
            if J.truthy(a):
                alertText = (J.add(J.get(a, "replace")("⚠️ INVERTED:", "\ud83c\udfaf OPPORTUNITY:"), " - Research longer-term options!") if J.ge(J.get(a, "indexOf")("INVERTED"), 0) else a)
                J.get(rows, "push")(fullRow(alertText, C_ALERT_BG, True, C_ALERT_TX, J.get(baseFont, "totals")))
    if (J.truthy(SHOW_DETAILS) and J.gt(J.get(cheap, "length"), 0)):
        headers = J.JSArray(["Strike", "Type", "Date", "DTE", "Bid", "Ask", "Last", "Actual IV", "Expected IV", "Mispricing %", "Spread"])
        if J.truthy(showOIColumn):
            J.get(headers, "push")("OI")
        def _f17(h=J.undefined, *_args):
            return headerCell(h)
        J.get(rows, "push")(J.obj(("cells", J.get(headers, "map")(_f17))))
        showN = J.get(G_Math, "max")(6, topMispricedN)
        i_4 = 0
        while J.lt(i_4, J.get(G_Math, "min")(showN, J.get(cheap, "length"))):
            o_2 = J.get(cheap, i_4)
            spread = (J.sub(J.get(o_2, "ask"), J.get(o_2, "bid")) if (J.gt(J.get(o_2, "ask"), 0) and J.ge(J.get(o_2, "bid"), 0)) else 0)
            spreadPct = (J.mul(J.div(spread, J.get(o_2, "ask")), 100) if J.gt(J.get(o_2, "ask"), 0) else 0)
            strongDisc = J.gt(J.get(G_Math, "abs")(J.get(o_2, "mispricingPct")), 30)
            discBg = (C_DISC_STRONG_BG if J.truthy(strongDisc) else C_DISC_WEAK_BG)
            discTx = C_DISC_TX
            spreadBg = (C_SPREAD_WARN if J.gt(spreadPct, 20) else (C_SPREAD_MED if J.gt(spreadPct, 10) else C_FOOTER_BG1))
            spreadTx = (C_SPREAD_TX if J.gt(spreadPct, 10) else "#FFFFFF")
            rowCells = J.JSArray([txtCell(G_String(J.get(o_2, "strike")), C_FOOTER_BG1, "right", False, "#FFFFFF", J.get(baseFont, "totals")), txtCell(J.get(o_2, "type"), C_FOOTER_BG1, "center", True, ("limegreen" if J.seq(J.get(o_2, "type"), "CALL") else "red"), J.get(baseFont, "totals")), txtCell(J.get(o_2, "expiry"), C_FOOTER_BG1, "center", False, "#FFFFFF", J.get(baseFont, "totals")), txtCell(J.add(G_String(J.get(o_2, "dte")), "D"), C_FOOTER_BG1, "center", False, "#FFFFFF", J.get(baseFont, "totals")), txtCell(J.get(J.get(o_2, "bid"), "toFixed")(2), C_FOOTER_BG1, "right", False, "#FFFFFF", J.get(baseFont, "totals")), txtCell(J.get(J.get(o_2, "ask"), "toFixed")(2), C_FOOTER_BG1, "right", False, "#FFFFFF", J.get(baseFont, "totals")), txtCell(J.get(J.get(o_2, "price"), "toFixed")(2), C_FOOTER_BG1, "right", False, "YELLOW", J.get(baseFont, "totals")), txtCell(J.add(J.get(J.mul(J.get(o_2, "actualIV"), 100), "toFixed")(1), "%"), C_FOOTER_BG1, "right", False, "#FFFFFF", J.get(baseFont, "totals")), txtCell(J.add(J.get(J.mul(J.get(o_2, "expectedIV"), 100), "toFixed")(1), "%"), C_FOOTER_BG1, "right", False, "#FFFFFF", J.get(baseFont, "totals")), txtCell(J.add(J.get(J.get(G_Math, "abs")(J.get(o_2, "mispricingPct")), "toFixed")(1), "%"), discBg, "right", True, discTx, J.get(baseFont, "totals")), txtCell(J.get(spread, "toFixed")(2), spreadBg, "right", True, spreadTx, J.get(baseFont, "totals"))])
            if J.truthy(showOIColumn):
                J.get(rowCells, "push")(txtCell(G_String(J.get(o_2, "oi")), C_FOOTER_BG1, "right", False, "#FFFFFF", J.get(baseFont, "totals")))
            J.get(rows, "push")(J.obj(("cells", rowCells)))
            i_4 = J.inc(i_4)
    totalOpps = J.get(cheap, "length")
    def _f18(o_3=J.undefined, *_args):
        return J.gt(J.get(G_Math, "abs")(J.get(o_3, "mispricingPct")), 25)
    highConf = J.get(J.get(cheap, "filter")(_f18), "length")
    J.get(rows, "push")(J.obj(("cells", J.JSArray([txtCell(J.add("Price: ", J.get(S, "toFixed")(2)), C_FOOTER_BG1, "center", True, C_FOOTER_TX_DIM, J.get(baseFont, "totals")), txtCell(J.add("Opportunities: ", totalOpps), (C_BANNER_GOOD if J.gt(totalOpps, 0) else "var(--background-color)"), "center", True, (C_BANNER_GOOD_TX if J.gt(totalOpps, 0) else "var(--text-color)"), J.get(baseFont, "totals")), txtCell(J.add("High Confidence: ", highConf), (C_RESEARCH_BG if J.gt(highConf, 2) else "var(--background-color)"), "center", True, (C_RESEARCH_TX if J.gt(highConf, 2) else "var(--text-color)"), J.get(baseFont, "totals")), txtCell(J.add(J.add("Threshold: ", mispricingThreshold), "%"), "var(--background-color)", "center", True, "var(--text-color)", J.get(baseFont, "totals"))]))))
    J.get(rows, "push")(fullRow("Source: Nasdaq Options Chain • 15min delayed data • Advanced mispricing detection for ETFs and stocks", C_FOOTER_BG1, False, C_FOOTER_TX_DIM, J.get(baseFont, "small")))
    J.get(rows, "push")(fullRow("⚠️ Options Term Structure Hunter identifies potential mispricings for research - Not investment advice ⚠️", C_FOOTER_BG2, False, "#F7EB00", J.get(baseFont, "small")))
    G_paint_overlay("OptionsHunterV4", J.obj(("position", "bottom_right"), ("offset_x", (-40)), ("offset_y", 0), ("order", "above_all")), J.obj(("background", "var(--background-color)"), ("border", "1px solid #1E90FF"), ("borderRadius", scaleVal(4)), ("rows", rows)))


register_store_indicator(
    script,
    name='options_term_structure_hunter_v1_TS',
    title='Options Term Structure Hunter v1',
    developer='Rock Regan',
    url='https://trendspider.com/trading-tools-store/indicators/68ab9f-options-term-structure-hunter-v1/',
    position='price',
    inputs=[{'id': 'max_expiries_to_analyze', 'title': 'Max Expiries to Analyze', 'type': 'number', 'default': 6}, {'id': 'show_details_table', 'title': 'Show Details Table', 'type': 'boolean', 'default': True}, {'id': 'top_mispriced_strikes', 'title': 'Top Mispriced Strikes', 'type': 'number', 'default': 5}, {'id': 'mispricing_threshold__', 'title': 'Mispricing Threshold %', 'type': 'number', 'default': 10}, {'id': 'term_structure_alerts', 'title': 'Term Structure Alerts', 'type': 'boolean', 'default': True}, {'id': 'risk_free_rate__', 'title': 'Risk Free Rate %', 'type': 'number', 'default': 4.2}, {'id': 'iv_fallback__', 'title': 'IV Fallback %', 'type': 'number', 'default': 30}, {'id': 'show_oi_column', 'title': 'Show OI Column', 'type': 'boolean', 'default': False}, {'id': 'max_banner_ideas', 'title': 'Max Banner Ideas', 'type': 'number', 'default': 3}, {'id': 'ui_scale____', 'title': 'UI Scale (%)', 'type': 'number', 'default': 100}, {'id': 'min_open_interest', 'title': 'Min Open Interest', 'type': 'number', 'default': 25}, {'id': 'max_spread___of_ask', 'title': 'Max Spread % of Ask', 'type': 'number', 'default': 40}, {'id': 'moneyness_min__k_s_', 'title': 'Moneyness Min (K/S)', 'type': 'number', 'default': 0.7}, {'id': 'moneyness_max__k_s_', 'title': 'Moneyness Max (K/S)', 'type': 'number', 'default': 1.3}],
    outputs=[],
    signals=[],
    requires=['http'],
    parity='aapl_d: both-error, syn_5m: both-error',
)
