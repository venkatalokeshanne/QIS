"""
Flowbot — Unusual Options (7–14 DTE) -- TrendSpider store indicator by James Chellis.

Registered as "flowbot_unusual_options_7_14_dte_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/689fff-flowbot-unusual-options-7-14-dte/)
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
    G_Math = G["Math"]
    G_NaN = G["NaN"]
    G_Object = G["Object"]
    G_String = G["String"]
    G_close = G["close"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_input = G["input"]
    G_isFinite = G["isFinite"]
    G_paint_overlay = G["paint_overlay"]
    G_parseFloat = G["parseFloat"]
    G_request = G["request"]
    G_time = G["time"]
    def fmtInt(n=J.undefined, *_args):
        if (not J.truthy(G_isFinite(n))):
            return "0"
        if J.ge(J.get(G_Math, "abs")(n), 1000000000):
            return J.add(J.get(J.div(n, 1000000000), "toFixed")(2), "B")
        if J.ge(J.get(G_Math, "abs")(n), 1000000):
            return J.add(J.get(J.div(n, 1000000), "toFixed")(2), "M")
        if J.ge(J.get(G_Math, "abs")(n), 1000):
            return J.add(J.get(J.div(n, 1000), "toFixed")(2), "K")
        return G_String(J.get(G_Math, "round")(n))
    def fmtMoney(n=J.undefined, *_args):
        if (not J.truthy(G_isFinite(n))):
            return "$0"
        if J.ge(J.get(G_Math, "abs")(n), 1000000000):
            return J.add(J.add("$", J.get(J.div(n, 1000000000), "toFixed")(2)), "B")
        if J.ge(J.get(G_Math, "abs")(n), 1000000):
            return J.add(J.add("$", J.get(J.div(n, 1000000), "toFixed")(2)), "M")
        if J.ge(J.get(G_Math, "abs")(n), 1000):
            return J.add(J.add("$", J.get(J.div(n, 1000), "toFixed")(2)), "K")
        return J.add("$", J.get(G_Math, "round")(n))
    def safeNum(v=J.undefined, dflt=J.undefined, *_args):
        return (v if (J.seq(J.typeof(v), "number") and J.truthy(G_isFinite(v))) else dflt)
    def pcRatio(calls=J.undefined, puts=J.undefined, *_args):
        c = safeNum(calls, 0)
        p = safeNum(puts, 0)
        if (J.seq(c, 0) and J.gt(p, 0)):
            return 999
        if (J.seq(c, 0) and J.seq(p, 0)):
            return 1
        return J.div(p, (1 if J.seq(c, 0) else c))
    def dteBucket(d=J.undefined, *_args):
        x = J.get(G_Math, "max")(0, J.get(G_Math, "round")(d))
        if J.seq(x, 0):
            return "0d"
        if J.le(x, 7):
            return "1w"
        if J.le(x, 14):
            return "7–14d"
        if J.le(x, 30):
            return "1m"
        return J.add(x, "d")
    def itmOtmStatus(strike=J.undefined, spot_2=J.undefined, *_args):
        if ((not J.truthy(G_isFinite(strike))) or (not J.truthy(G_isFinite(spot_2)))):
            return ""
        callITM = J.le(strike, spot_2)
        putITM = J.ge(strike, spot_2)
        callTag = ("ITM Call" if J.truthy(callITM) else "OTM Call")
        putTag = ("ITM Put" if J.truthy(putITM) else "OTM Put")
        return J.add(J.add(callTag, " / "), putTag)
    def loadUnusual(maxPages=J.undefined, *_args):
        out = J.JSArray([])
        lastTS = None
        i = 0
        while J.lt(i, maxPages):
            payload = (J.get(G_request, "unusual_options")(J.get(G_current, "ticker")) if J.seq(i, 0) else J.get(G_request, "unusual_options")(J.get(G_current, "ticker"), J.obj(("filters", J.JSArray([J.obj(("field", "timestamp"), ("filter", "less"), ("value", lastTS))])))))
            if (((not J.truthy(payload)) or J.truthy(J.get(payload, "error"))) or J.seq(J.get(payload, "length"), 0)):
                break
            out = J.get(out, "concat")(payload)
            lastTS = J.get(J.get(payload, J.sub(J.get(payload, "length"), 1)), "timestamp")
            i = J.inc(i)
        return out
    def headerCell(t=J.undefined, *_args):
        return J.obj(("text", t), ("backgroundColor", cHeader), ("color", cText), ("fontWeight", "bold"), ("padding", "6px"))
    def cellTxt(t=J.undefined, bg=J.undefined, *_args):
        return J.obj(("text", t), ("color", cText), ("backgroundColor", (bg if J.truthy(bg) else "")), ("padding", "4px"))
    def pcCell(v=J.undefined, *_args):
        val = J.get((v if J.truthy(G_isFinite(v)) else 1), "toFixed")(2)
        bg = cGrey
        if J.gt(v, 1.2):
            bg = cRed
        elif J.lt(v, 0.8):
            bg = cGreen
        return J.obj(("text", val), ("color", cText), ("backgroundColor", bg), ("padding", "4px"))
    G_describe_indicator("Flowbot — Unusual Options (7–14 DTE)", "lower", J.obj(("shortName", "Flowbot")))
    pagesToLoad = J.get(G_input, "number")("Pages to Load", 3, J.obj(("min", 1), ("max", 10)))
    minSize = J.get(G_input, "number")("Min Contract Size", 10, J.obj(("min", 1), ("max", 5000)))
    minDTE = J.get(G_input, "number")("Min DTE", 7, J.obj(("min", 0), ("max", 60)))
    maxDTE = J.get(G_input, "number")("Max DTE", 14, J.obj(("min", 1), ("max", 180)))
    include0DTE = J.get(G_input, "boolean")("Include 0DTE", False)
    rankBy = J.get(G_input, "select")("Rank By", "Premium", J.JSArray(["Premium", "Volume"]))
    includeOTM = J.get(G_input, "boolean")("Include OTM", True)
    includeITM = J.get(G_input, "boolean")("Include ITM", True)
    cHeader = "#1e272e"
    cPanelBG = "rgba(25,25,35,0.92)"
    cBorder = "#565656"
    cText = "#ffffff"
    cGreen = "#00B300"
    cRed = "#B30000"
    cGrey = "#808080"
    cGoldBG = "#ffd700"
    cGoldTxt = "#111111"
    cGoldBdr = "#b8860b"
    cRowBG = "#2f3640"
    spot = J.get(G_close, J.sub(J.get(G_close, "length"), 1))
    nowTs = J.get(G_time, J.sub(J.get(G_time, "length"), 1))
    raw = loadUnusual(pagesToLoad)
    fetchedN = (J.get(raw, "length") if J.truthy(J.get(G_Array, "isArray")(raw)) else 0)
    keep = J.JSArray([])
    i = 0
    while J.lt(i, fetchedN):
        o = J.get(raw, i)
        if (not J.truthy(o)):
            i = J.inc(i)
            continue
        size = safeNum(J.get(o, "size"), 0)
        if J.lt(size, minSize):
            i = J.inc(i)
            continue
        dte = (J.get(o, "daysToExp") if J.seq(J.typeof(J.get(o, "daysToExp")), "number") else (J.get(G_Math, "round")(J.div(J.sub(J.get(o, "expDate"), nowTs), 86400000)) if J.seq(J.typeof(J.get(o, "expDate")), "number") else None))
        if (dte is None):
            i = J.inc(i)
            continue
        if (J.seq(dte, 0) and (not J.truthy(include0DTE))):
            i = J.inc(i)
            continue
        if (J.lt(dte, minDTE) or J.gt(dte, maxDTE)):
            i = J.inc(i)
            continue
        strike = safeNum(J.get(o, "strike"), G_NaN)
        if (not J.truthy(G_isFinite(strike))):
            i = J.inc(i)
            continue
        typ = (J.get(o, "type") if (J.seq(J.get(o, "type"), "PUT") or J.seq(J.get(o, "type"), "CALL")) else None)
        if (not J.truthy(typ)):
            i = J.inc(i)
            continue
        isOTM = (_t1 if J.truthy(_t1 := (J.gt(strike, spot) if J.truthy(_t2 := J.seq(typ, "CALL")) else _t2)) else (J.lt(strike, spot) if J.truthy(_t3 := J.seq(typ, "PUT")) else _t3))
        isITM = (not J.truthy(isOTM))
        if (J.truthy(isOTM) and (not J.truthy(includeOTM))):
            i = J.inc(i)
            continue
        if (J.truthy(isITM) and (not J.truthy(includeITM))):
            i = J.inc(i)
            continue
        prem = J.mul(safeNum(J.get(o, "costBasis"), 0), size)
        J.get(keep, "push")(J.obj(("type", typ), ("size", size), ("strike", strike), ("dte", dte), ("bucket", dteBucket(dte)), ("premium", prem), ("timestamp", safeNum(J.get(o, "timestamp"), nowTs))))
        i = J.inc(i)
    afterFilters = J.get(keep, "length")
    if J.seq(afterFilters, 0):
        G_paint_overlay("Flowbot", J.obj(("position", "bottom_left"), ("width", "86%")), J.obj(("background", cPanelBG), ("border", J.add("1px solid ", cBorder)), ("borderRadius", "6px"), ("rows", J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", "No unusual options within filters"), ("color", cText), ("padding", "8px"), ("fontWeight", "bold"))]))), J.obj(("cells", J.JSArray([J.obj(("text", J.add(J.add(J.add(J.add(J.add(J.add(J.add(J.add(J.add("Fetched: ", fetchedN), " • After filters: 0 • DTE "), minDTE), "–"), maxDTE), (" (0DTE on)" if J.truthy(include0DTE) else " (0DTE off)")), " • MinSize ≥ "), minSize), " • #TSBuild25")), ("color", cText), ("fontSize", "11px"), ("padding", "6px"))])))]))))
        return J.obj(("fetched", fetchedN), ("kept", 0), ("note", "No data after filters"))
    totCallsVol = 0
    totPutsVol = 0
    totCallsPrem = 0
    totPutsPrem = 0
    byExpiry = J.obj()
    byStrike = J.obj()
    i_2 = 0
    while J.lt(i_2, J.get(keep, "length")):
        r = J.get(keep, i_2)
        if J.seq(J.get(r, "type"), "CALL"):
            totCallsVol = J.add(totCallsVol, J.get(r, "size"))
            totCallsPrem = J.add(totCallsPrem, J.get(r, "premium"))
        else:
            totPutsVol = J.add(totPutsVol, J.get(r, "size"))
            totPutsPrem = J.add(totPutsPrem, J.get(r, "premium"))
        if (not J.truthy(J.get(byExpiry, J.get(r, "bucket")))):
            J.set(byExpiry, J.get(r, "bucket"), J.obj(("vol", 0), ("calls", 0), ("puts", 0), ("prem", 0)))
        e = J.get(byExpiry, J.get(r, "bucket"))
        J.set(e, "vol", J.add(J.get(e, "vol"), J.get(r, "size")))
        J.set(e, "prem", J.add(J.get(e, "prem"), J.get(r, "premium")))
        if J.seq(J.get(r, "type"), "CALL"):
            J.set(e, "calls", J.add(J.get(e, "calls"), J.get(r, "size")))
        else:
            J.set(e, "puts", J.add(J.get(e, "puts"), J.get(r, "size")))
        k = G_String(J.get(r, "strike"))
        if (not J.truthy(J.get(byStrike, k))):
            J.set(byStrike, k, J.obj(("vol", 0), ("calls", 0), ("puts", 0), ("prem", 0), ("dteMap", J.obj())))
        s = J.get(byStrike, k)
        J.set(s, "vol", J.add(J.get(s, "vol"), J.get(r, "size")))
        J.set(s, "prem", J.add(J.get(s, "prem"), J.get(r, "premium")))
        if J.seq(J.get(r, "type"), "CALL"):
            J.set(s, "calls", J.add(J.get(s, "calls"), J.get(r, "size")))
        else:
            J.set(s, "puts", J.add(J.get(s, "puts"), J.get(r, "size")))
        b = J.get(r, "bucket")
        if (not J.truthy(J.get(J.get(s, "dteMap"), b))):
            J.set(J.get(s, "dteMap"), b, J.obj(("vol", 0), ("calls", 0), ("puts", 0), ("prem", 0)))
        _t4 = J.get(J.get(s, "dteMap"), b)
        J.set(_t4, "vol", J.add(J.get(_t4, "vol"), J.get(r, "size")))
        _t5 = J.get(J.get(s, "dteMap"), b)
        J.set(_t5, "prem", J.add(J.get(_t5, "prem"), J.get(r, "premium")))
        if J.seq(J.get(r, "type"), "CALL"):
            _t6 = J.get(J.get(s, "dteMap"), b)
            J.set(_t6, "calls", J.add(J.get(_t6, "calls"), J.get(r, "size")))
        else:
            _t7 = J.get(J.get(s, "dteMap"), b)
            J.set(_t7, "puts", J.add(J.get(_t7, "puts"), J.get(r, "size")))
        i_2 = J.inc(i_2)
    pcVol = pcRatio(totCallsVol, totPutsVol)
    pcPrem = pcRatio(totCallsPrem, totPutsPrem)
    sentiment = "Neutral"
    if (J.gt(pcVol, 1.2) and J.gt(pcPrem, 1.2)):
        sentiment = "Bearish"
    elif (J.lt(pcVol, 0.8) and J.lt(pcPrem, 0.8)):
        sentiment = "Bullish"
    expKeys = J.get(G_Object, "keys")(byExpiry)
    def _f8(a=J.undefined, b_2=J.undefined, *_args):
        if J.seq(rankBy, "Premium"):
            return J.sub(J.get(J.get(byExpiry, b_2), "prem"), J.get(J.get(byExpiry, a), "prem"))
        return J.sub(J.get(J.get(byExpiry, b_2), "vol"), J.get(J.get(byExpiry, a), "vol"))
    J.get(expKeys, "sort")(_f8)
    def _f9(bk=J.undefined, *_args):
        return J.obj(("bucket", bk), ("vol", J.get(J.get(byExpiry, bk), "vol")), ("calls", J.get(J.get(byExpiry, bk), "calls")), ("puts", J.get(J.get(byExpiry, bk), "puts")), ("pc", pcRatio(J.get(J.get(byExpiry, bk), "calls"), J.get(J.get(byExpiry, bk), "puts"))), ("prem", J.get(J.get(byExpiry, bk), "prem")))
    topExp = J.get(J.get(expKeys, "slice")(0, 5), "map")(_f9)
    def _f10(x=J.undefined, *_args):
        return G_parseFloat(x)
    def _f11(x=J.undefined, *_args):
        return G_isFinite(x)
    strikeKeys = J.get(J.get(J.get(G_Object, "keys")(byStrike), "map")(_f10), "filter")(_f11)
    def _f12(a=J.undefined, b_2=J.undefined, *_args):
        A = J.get(byStrike, G_String(a))
        B = J.get(byStrike, G_String(b_2))
        if J.seq(rankBy, "Premium"):
            return J.sub(J.get(B, "prem"), J.get(A, "prem"))
        return J.sub(J.get(B, "vol"), J.get(A, "vol"))
    J.get(strikeKeys, "sort")(_f12)
    def _f13(st=J.undefined, *_args):
        rec = J.get(byStrike, G_String(st))
        domBk = None
        domPrem = (-1)
        dKeys = J.get(G_Object, "keys")(J.get(rec, "dteMap"))
        i_3 = 0
        while J.lt(i_3, J.get(dKeys, "length")):
            k_2 = J.get(dKeys, i_3)
            pv = J.get(J.get(J.get(rec, "dteMap"), k_2), "prem")
            if J.gt(pv, domPrem):
                domPrem = pv
                domBk = k_2
            i_3 = J.inc(i_3)
        return J.obj(("strike", st), ("status", itmOtmStatus(st, spot)), ("vol", J.get(rec, "vol")), ("calls", J.get(rec, "calls")), ("puts", J.get(rec, "puts")), ("pc", pcRatio(J.get(rec, "calls"), J.get(rec, "puts"))), ("dom", (_t1 if J.truthy(_t1 := domBk) else "")), ("prem", J.get(rec, "prem")))
    topStrikesList = J.get(J.get(strikeKeys, "slice")(0, 10), "map")(_f13)
    nearestStrike = None
    if (J.gt(J.get(topStrikesList, "length"), 0) and J.truthy(G_isFinite(spot))):
        bestDiff = G_Infinity
        i_3 = 0
        while J.lt(i_3, J.get(topStrikesList, "length")):
            st = J.get(J.get(topStrikesList, i_3), "strike")
            d = J.get(G_Math, "abs")(J.sub(st, spot))
            if J.lt(d, bestDiff):
                bestDiff = d
                nearestStrike = st
            i_3 = J.inc(i_3)
    summaryRow = J.obj(("cells", J.JSArray([J.obj(("text", "Sentiment"), ("backgroundColor", cHeader), ("color", cText), ("fontWeight", "bold"), ("padding", "6px")), J.obj(("text", sentiment), ("backgroundColor", (cGreen if J.seq(sentiment, "Bullish") else (cRed if J.seq(sentiment, "Bearish") else cGrey))), ("color", cText), ("fontWeight", "bold"), ("padding", "6px")), J.obj(("text", J.add("P/C (Vol) ", J.get(pcVol, "toFixed")(2))), ("backgroundColor", (cRed if J.gt(pcVol, 1.2) else (cGreen if J.lt(pcVol, 0.8) else cGrey))), ("color", cText), ("padding", "6px")), J.obj(("text", J.add("P/C (Prem) ", J.get(pcPrem, "toFixed")(2))), ("backgroundColor", (cRed if J.gt(pcPrem, 1.2) else (cGreen if J.lt(pcPrem, 0.8) else cGrey))), ("color", cText), ("padding", "6px")), J.obj(("text", J.add("Calls ", fmtInt(totCallsVol))), ("color", cText), ("backgroundColor", cGreen), ("padding", "6px"), ("fontWeight", "bold")), J.obj(("text", J.add("Puts ", fmtInt(totPutsVol))), ("color", cText), ("backgroundColor", cRed), ("padding", "6px"), ("fontWeight", "bold")), J.obj(("text", J.add("Rank: ", rankBy)), ("color", cText), ("padding", "6px"))])))
    def _f14(r_2=J.undefined, *_args):
        return J.obj(("cells", J.JSArray([cellTxt(J.get(r_2, "bucket")), cellTxt(fmtInt(J.get(r_2, "vol"))), J.obj(("text", fmtInt(J.get(r_2, "calls"))), ("color", cText), ("backgroundColor", "rgba(0,179,0,0.5)"), ("padding", "4px")), J.obj(("text", fmtInt(J.get(r_2, "puts"))), ("color", cText), ("backgroundColor", "rgba(179,0,0,0.5)"), ("padding", "4px")), pcCell(J.get(r_2, "pc")), cellTxt(fmtMoney(J.get(r_2, "prem")))])))
    expRows = J.JSArray([J.obj(("cells", J.JSArray([headerCell("DTE"), headerCell("Vol"), headerCell("Calls"), headerCell("Puts"), headerCell("P/C"), headerCell("Premium")]))), *J.spread(J.get(topExp, "map")(_f14))])
    def _f15(r_2=J.undefined, *_args):
        return J.obj(("cells", J.JSArray([J.obj(("text", G_String(J.get(r_2, "strike"))), ("backgroundColor", (cGoldBG if ((nearestStrike is not None) and J.seq(J.get(r_2, "strike"), nearestStrike)) else cRowBG)), ("color", (cGoldTxt if ((nearestStrike is not None) and J.seq(J.get(r_2, "strike"), nearestStrike)) else cText)), ("border", (J.add("1px solid ", cGoldBdr) if ((nearestStrike is not None) and J.seq(J.get(r_2, "strike"), nearestStrike)) else "")), ("padding", "4px"), ("fontWeight", ("bold" if ((nearestStrike is not None) and J.seq(J.get(r_2, "strike"), nearestStrike)) else "normal"))), cellTxt(J.get(r_2, "status")), cellTxt(fmtInt(J.get(r_2, "vol"))), J.obj(("text", fmtInt(J.get(r_2, "calls"))), ("color", cText), ("backgroundColor", "rgba(0,179,0,0.5)"), ("padding", "4px")), J.obj(("text", fmtInt(J.get(r_2, "puts"))), ("color", cText), ("backgroundColor", "rgba(179,0,0,0.5)"), ("padding", "4px")), pcCell(J.get(r_2, "pc")), cellTxt((_t1 if J.truthy(_t1 := J.get(r_2, "dom")) else "")), cellTxt(fmtMoney(J.get(r_2, "prem")))])))
    strikeRows = J.JSArray([J.obj(("cells", J.JSArray([headerCell("Strike"), headerCell("Status"), headerCell("Vol"), headerCell("Calls"), headerCell("Puts"), headerCell("P/C"), headerCell("Dom Exp (DTE)"), headerCell("Premium")]))), *J.spread(J.get(topStrikesList, "map")(_f15))])
    footer = J.obj(("cells", J.JSArray([J.obj(("text", J.add(J.add(J.add(J.add(J.add(J.add(J.add(J.add(J.add(J.add(J.add(J.add(J.add("Fetched: ", fetchedN), " • After filters: "), afterFilters), " • DTE "), minDTE), "–"), maxDTE), (" (0DTE on)" if J.truthy(include0DTE) else " (0DTE off)")), " • MinSize ≥ "), minSize), " • Rank: "), rankBy), " • #TSBuild25")), ("color", cText), ("fontSize", "11px"), ("padding", "6px"), ("colSpan", 8))])))
    G_paint_overlay("Flowbot — Options Flow", J.obj(("position", "bottom_left"), ("width", "86%")), J.obj(("background", cPanelBG), ("border", J.add("1px solid ", cBorder)), ("borderRadius", "6px"), ("rows", J.JSArray([summaryRow, J.obj(("cells", J.JSArray([J.obj(("text", J.add(J.add("Top Expiries (by ", ("Premium" if J.seq(rankBy, "Premium") else "Volume")), ")")), ("backgroundColor", cHeader), ("color", cText), ("fontWeight", "bold"), ("padding", "6px"), ("colSpan", 7))]))), *J.spread(expRows), J.obj(("cells", J.JSArray([J.obj(("text", J.add(J.add("Top Strikes (by ", ("Premium" if J.seq(rankBy, "Premium") else "Volume")), ")")), ("backgroundColor", cHeader), ("color", cText), ("fontWeight", "bold"), ("padding", "6px"), ("colSpan", 8))]))), *J.spread(strikeRows), footer]))))
    return J.obj(("fetched", fetchedN), ("kept", afterFilters), ("sentiment", sentiment), ("pc_vol", pcVol), ("pc_premium", pcPrem), ("calls", totCallsVol), ("puts", totPutsVol))


register_store_indicator(
    script,
    name='flowbot_unusual_options_7_14_dte_TS',
    title='Flowbot — Unusual Options (7–14 DTE)',
    developer='James Chellis',
    url='https://trendspider.com/trading-tools-store/indicators/689fff-flowbot-unusual-options-7-14-dte/',
    position='lower',
    inputs=[{'id': 'pages_to_load', 'title': 'Pages to Load', 'type': 'number', 'default': 3}, {'id': 'min_contract_size', 'title': 'Min Contract Size', 'type': 'number', 'default': 10}, {'id': 'min_dte', 'title': 'Min DTE', 'type': 'number', 'default': 7}, {'id': 'max_dte', 'title': 'Max DTE', 'type': 'number', 'default': 14}, {'id': 'include_0dte', 'title': 'Include 0DTE', 'type': 'boolean', 'default': False}, {'id': 'rank_by', 'title': 'Rank By', 'type': 'select_wide', 'default': 'Premium', 'options': ['Premium', 'Volume']}, {'id': 'include_otm', 'title': 'Include OTM', 'type': 'boolean', 'default': True}, {'id': 'include_itm', 'title': 'Include ITM', 'type': 'boolean', 'default': True}],
    outputs=[],
    signals=[],
    requires=['unusual_options'],
    parity='exact',
)
