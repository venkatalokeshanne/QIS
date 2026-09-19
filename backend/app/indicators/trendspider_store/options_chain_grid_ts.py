"""
Options Chain Grid -- TrendSpider store indicator by Rock Regan.

Registered as "options_chain_grid_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/69f11e-options-chain-grid/)
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
    G_Object = G["Object"]
    G_String = G["String"]
    G_assert = G["assert"]
    G_close = G["close"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_input = G["input"]
    G_isNaN = G["isNaN"]
    G_paint = G["paint"]
    G_paint_overlay = G["paint_overlay"]
    G_parseFloat = G["parseFloat"]
    G_parseInt = G["parseInt"]
    G_request = G["request"]
    def scaleVal(n=J.undefined, *_args):
        return J.get(G_Math, "max")(1, J.get(G_Math, "round")(J.div(J.mul(n, uiScale), 100)))
    def px(n=J.undefined, *_args):
        return J.add(scaleVal(n), "px")
    def topNSet(values=J.undefined, n=J.undefined, *_args):
        def _f1(v=J.undefined, i_2=J.undefined, *_args):
            return J.obj(("i", i_2), ("v", (_t1 if J.truthy(_t1 := v) else 0)))
        def _f2(x=J.undefined, *_args):
            return J.gt(J.get(x, "v"), 0)
        def _f3(a=J.undefined, b=J.undefined, *_args):
            return J.sub(J.get(b, "v"), J.get(a, "v"))
        def _f4(x=J.undefined, *_args):
            return J.get(x, "i")
        ranked = J.get(J.get(J.get(J.get(J.get(values, "map")(_f1), "filter")(_f2), "sort")(_f3), "slice")(0, n), "map")(_f4)
        s = J.obj()
        k = 0
        while J.lt(k, J.get(ranked, "length")):
            J.set(s, J.get(ranked, k), True)
            k = J.inc(k)
        return s
    def flameSet(oiArr=J.undefined, volArr=J.undefined, sideMaxOI=J.undefined, n=J.undefined, *_args):
        oiFloor = J.get(G_Math, "max")(100, J.mul(sideMaxOI, 0.1))
        def _f1(oi=J.undefined, i_2=J.undefined, *_args):
            v = (_t1 if J.truthy(_t1 := J.get(volArr, i_2)) else 0)
            if (J.lt(oi, oiFloor) or J.le(oi, 0)):
                return J.obj(("i", i_2), ("ratio", 0))
            r = J.div(v, oi)
            return J.obj(("i", i_2), ("ratio", (r if J.ge(r, FLAME_MIN_RATIO) else 0)))
        def _f2(x=J.undefined, *_args):
            return J.gt(J.get(x, "ratio"), 0)
        def _f3(a=J.undefined, b=J.undefined, *_args):
            return J.sub(J.get(b, "ratio"), J.get(a, "ratio"))
        def _f4(x=J.undefined, *_args):
            return J.get(x, "i")
        ranked = J.get(J.get(J.get(J.get(J.get(oiArr, "map")(_f1), "filter")(_f2), "sort")(_f3), "slice")(0, n), "map")(_f4)
        s = J.obj()
        k = 0
        while J.lt(k, J.get(ranked, "length")):
            J.set(s, J.get(ranked, k), True)
            k = J.inc(k)
        return s
    def oiHeatBg(val=J.undefined, max=J.undefined, side=J.undefined, ri=J.undefined, *_args):
        if (((not J.truthy(showOIHeat)) or (not J.truthy(val))) or J.seq(max, 0)):
            return None
        inTop = (J.get(topCallOI, ri) if J.seq(side, "C") else J.get(topPutOI, ri))
        if (not J.truthy(inTop)):
            return None
        i_2 = J.get(G_Math, "sqrt")(J.get(G_Math, "min")(1, J.div(val, max)))
        if J.seq(side, "C"):
            return J.add(J.add(J.add(J.add(J.add(J.add("rgb(", J.get(G_Math, "round")(10)), ","), J.get(G_Math, "round")(J.add(40, J.mul(i_2, 90)))), ","), J.get(G_Math, "round")(J.add(28, J.mul(i_2, 30)))), ")")
        return J.add(J.add(J.add(J.add(J.add(J.add("rgb(", J.get(G_Math, "round")(J.add(40, J.mul(i_2, 90)))), ","), J.get(G_Math, "round")(J.add(15, J.mul(i_2, 10)))), ","), J.get(G_Math, "round")(20)), ")")
    def volHeatBg(val=J.undefined, max=J.undefined, side=J.undefined, ri=J.undefined, *_args):
        if (((not J.truthy(showVolHeat)) or (not J.truthy(val))) or J.seq(max, 0)):
            return None
        inTop = (J.get(topCallVol, ri) if J.seq(side, "C") else J.get(topPutVol, ri))
        if (not J.truthy(inTop)):
            return None
        i_2 = J.get(G_Math, "sqrt")(J.get(G_Math, "min")(1, J.div(val, max)))
        if J.seq(side, "C"):
            return J.add(J.add(J.add(J.add(J.add(J.add("rgb(", J.get(G_Math, "round")(8)), ","), J.get(G_Math, "round")(J.add(35, J.mul(i_2, 75)))), ","), J.get(G_Math, "round")(J.add(50, J.mul(i_2, 90)))), ")")
        return J.add(J.add(J.add(J.add(J.add(J.add("rgb(", J.get(G_Math, "round")(J.add(45, J.mul(i_2, 80)))), ","), J.get(G_Math, "round")(J.add(15, J.mul(i_2, 15)))), ","), J.get(G_Math, "round")(J.add(50, J.mul(i_2, 75)))), ")")
    def mkCell(text=J.undefined, opts=J.undefined, *_args):
        opts = (_t1 if J.truthy(_t1 := opts) else J.obj())
        return J.obj(("text", G_String(text)), ("color", (_t2 if J.truthy(_t2 := J.get(opts, "color")) else J.get(TH, "text"))), ("background", (_t3 if J.truthy(_t3 := J.get(opts, "bg")) else "transparent")), ("fontWeight", ("bold" if J.truthy(J.get(opts, "bold")) else "normal")), ("fontSize", (_t4 if J.truthy(_t4 := J.get(opts, "fontSize")) else px(12))), ("paddingTop", px(4)), ("paddingBottom", px(4)), ("paddingLeft", px(7)), ("paddingRight", px(7)), ("textAlign", (_t5 if J.truthy(_t5 := J.get(opts, "align")) else "right")), ("colspan", (_t6 if J.truthy(_t6 := J.get(opts, "colspan")) else 1)))
    def hdrCell(text=J.undefined, opts=J.undefined, *_args):
        opts = (_t1 if J.truthy(_t1 := opts) else J.obj())
        return mkCell(text, J.obj(("color", (_t2 if J.truthy(_t2 := J.get(opts, "color")) else J.get(TH, "muted"))), ("bg", (_t3 if J.truthy(_t3 := J.get(opts, "bg")) else J.get(TH, "panelBg"))), ("bold", True), ("align", (_t4 if J.truthy(_t4 := J.get(opts, "align")) else "center")), ("colspan", J.get(opts, "colspan"))))
    def spacer(bg=J.undefined, *_args):
        return J.obj(("text", ""), ("background", (_t1 if J.truthy(_t1 := bg) else "transparent")), ("paddingLeft", px(2)), ("paddingRight", px(2)))
    G_describe_indicator("Options Chain Grid", J.obj(("shortName", "⚡ Chain Grid v1.0")))
    dteChoice = G_input("Expiry", "0DTE", J.JSArray(["0DTE", "1DTE", "2DTE", "3DTE", "5DTE", "7DTE", "14DTE", "30DTE", "60DTE", "90DTE"]))
    numStrikes = J.get(G_input, "number")("Strikes Around ATM", 3, J.obj(("min", 2), ("max", 12)))
    displayMode = G_input("Display", "Both", J.JSArray(["Both", "Calls Only", "Puts Only"]))
    scaleChoice = G_input("UI Scale", "100%", J.JSArray(["75%", "90%", "100%", "110%", "125%", "150%"]))
    showIV = J.get(G_input, "boolean")("Show IV Column", True)
    showDelta = J.get(G_input, "boolean")("Show Δ Column", True)
    showGreeksRow = J.get(G_input, "boolean")("Show Greeks Footer", False)
    showOIHeat = J.get(G_input, "boolean")("OI Heatmap", True)
    showVolHeat = J.get(G_input, "boolean")("Vol Heatmap", True)
    heatTopN = J.get(G_input, "number")("Heatmap Top N", 3, J.obj(("min", 1), ("max", 12)))
    flameTopN = J.get(G_input, "number")("Flame Top N", 2, J.obj(("min", 1), ("max", 5)))
    showMoneyness = J.get(G_input, "boolean")("ITM/OTM Tint", False)
    FLAME_MIN_RATIO = 1.5
    targetDTE = G_parseInt(dteChoice, 10)
    uiScale = G_parseInt(scaleChoice, 10)
    showCalls = J.sne(displayMode, "Puts Only")
    showPuts = J.sne(displayMode, "Calls Only")
    TH = J.obj(("bg", "#0d1117"), ("panelBg", "#08244f"), ("rowAlt1", "#0c1824"), ("rowAlt2", "#101e2e"), ("border", "#ABABAB"), ("text", "#d1d5db"), ("muted", "#9ca3af"), ("title", "#FFFFFF"), ("callBg", "#0a2818"), ("callText", "#56f5a2"), ("callMuted", "#3a8a64"), ("callHi", "#00ffaa"), ("putBg", "#2a0f12"), ("putText", "#ff8b8b"), ("putMuted", "#a85a5a"), ("putHi", "#ff5555"), ("atmBg", "#5C5C5C"), ("atmText", "#00FFFF"), ("itmTint", "#00301c"), ("warn", "#FFD700"))
    def fmtC(v=J.undefined, *_args):
        if ((J.nullish(v)) or J.truthy(G_isNaN(v))):
            return "–"
        n = G_Number(v)
        a = J.get(G_Math, "abs")(n)
        if J.ge(a, 1000000):
            return J.add(J.get(J.div(n, 1000000), "toFixed")(1), "M")
        if J.ge(a, 1000):
            return J.add(J.get(J.div(n, 1000), "toFixed")(1), "K")
        return J.get(J.get(G_Math, "round")(n), "toString")()
    def fmtP(v=J.undefined, *_args):
        return (J.get(G_Number(v), "toFixed")(2) if ((not J.nullish(v)) and (not J.truthy(G_isNaN(v)))) else "–")
    def fmtIV(v=J.undefined, *_args):
        return (J.add(J.get(G_Number(v), "toFixed")(0), "%") if ((not J.nullish(v)) and (not J.truthy(G_isNaN(v)))) else "–")
    def fmtG(v=J.undefined, *_args):
        return (J.get(G_Number(v), "toFixed")(2) if ((not J.nullish(v)) and (not J.truthy(G_isNaN(v)))) else "–")
    def fmtSk(v=J.undefined, *_args):
        f = J.get(G_Math, "abs")(J.sub(v, J.get(G_Math, "round")(v)))
        return (J.get(G_Number(v), "toFixed")(0) if J.lt(f, 0.001) else J.get(G_Number(v), "toFixed")(2))
    def _f1(*_args):
        return G_NaN
    G_paint(J.get(G_close, "map")(_f1), J.obj(("name", "ChainV34Ref"), ("style", "line"), ("color", "#FFD700")))
    ticker = (_t2 if J.truthy(_t2 := J.get(G_current, "ticker")) else J.get(G_current, "symbol"))
    currentPrice = J.get(G_close, J.sub(J.get(G_close, "length"), 1))
    schedule = J.get(G_request, "options_schedule")(ticker)
    G_assert((J.gt(J.get(schedule, "length"), 0) if J.truthy(_t3 := schedule) else _t3), J.template("No options schedule for ", ticker))
    bestIdx = 0
    bestDiff = 99999
    i = 0
    while J.lt(i, J.get(schedule, "length")):
        if ((J.truthy(J.get(schedule, i)) and J.truthy(J.get(J.get(schedule, i), "expiration"))) and (not J.nullish(J.get(J.get(J.get(schedule, i), "expiration"), "dte")))):
            diff = J.get(G_Math, "abs")(J.sub(J.get(J.get(J.get(schedule, i), "expiration"), "dte"), targetDTE))
            if J.lt(diff, bestDiff):
                bestDiff = diff
                bestIdx = i
        i = J.inc(i)
    selectedSched = J.get(schedule, bestIdx)
    expiryCode = J.get(J.get(selectedSched, "expiration"), "code")
    daysToExp = J.get(J.get(selectedSched, "expiration"), "dte")
    expiryDisplay = J.add(J.add(J.get(J.get(selectedSched, "expiration"), "month"), " "), J.get(J.get(selectedSched, "expiration"), "day"))
    schedTag = ("Wkly" if J.seq(J.get(J.get(selectedSched, "expiration"), "schedule"), "W") else ("Mthly" if J.seq(J.get(J.get(selectedSched, "expiration"), "schedule"), "M") else ""))
    chainRaw = J.get(G_request, "options_data_for_expiration")(ticker, J.get(expiryCode, "toString")(), J.JSArray(["oi", "dvol", "b", "a", "l", "iv", "gd", "gg", "gt"]))
    G_assert((not J.truthy(J.get(chainRaw, "error"))), J.template("Error fetching chain: ", J.get(chainRaw, "error")))
    chainData = J.get(chainRaw, "resultByStrike")
    G_assert(chainData, "No resultByStrike in chain data")
    def _f4(s=J.undefined, *_args):
        return G_parseFloat(s)
    def _f5(s=J.undefined, *_args):
        return (not J.truthy(G_isNaN(s)))
    def _f6(a=J.undefined, b=J.undefined, *_args):
        return J.sub(a, b)
    allStrikes = J.get(J.get(J.get(J.get(G_Object, "keys")(chainData), "map")(_f4), "filter")(_f5), "sort")(_f6)
    def _f7(c=J.undefined, s=J.undefined, i_2=J.undefined, *_args):
        return (i_2 if J.lt(J.get(G_Math, "abs")(J.sub(s, currentPrice)), J.get(G_Math, "abs")(J.sub(J.get(allStrikes, c), currentPrice))) else c)
    atmIdx = J.get(allStrikes, "reduce")(_f7, 0)
    startIx = J.get(G_Math, "max")(0, J.sub(atmIdx, numStrikes))
    endIx = J.get(G_Math, "min")(J.get(allStrikes, "length"), J.add(J.add(atmIdx, numStrikes), 1))
    strikes = J.get(allStrikes, "slice")(startIx, endIx)
    localATM = J.sub(atmIdx, startIx)
    callOIArr = J.JSArray([])
    callVolArr = J.JSArray([])
    putOIArr = J.JSArray([])
    putVolArr = J.JSArray([])
    totCallOI = 0
    totPutOI = 0
    totCallVol = 0
    totPutVol = 0
    maxCallOI = 1
    maxPutOI = 1
    maxOI = 1
    maxVol = 1
    atmIV = None
    def _f8(strike=J.undefined, ri=J.undefined, *_args):
        nonlocal totCallOI, totPutOI, totCallVol, totPutVol, maxCallOI, maxPutOI, maxOI, maxVol, atmIV
        def _f2(k=J.undefined, *_args):
            return J.seq(G_parseFloat(k), strike)
        sk = (_t1 if J.truthy(_t1 := J.get(J.get(G_Object, "keys")(chainData), "find")(_f2)) else J.get(strike, "toString")())
        sd = (_t3 if J.truthy(_t3 := J.get(chainData, sk)) else J.obj())
        C = (_t4 if J.truthy(_t4 := J.get(sd, "C")) else J.obj())
        P = (_t5 if J.truthy(_t5 := J.get(sd, "P")) else J.obj())
        cOI = (_t6 if J.truthy(_t6 := J.get(C, "oi")) else 0)
        pOI = (_t7 if J.truthy(_t7 := J.get(P, "oi")) else 0)
        cV = (_t8 if J.truthy(_t8 := J.get(C, "dvol")) else 0)
        pV = (_t9 if J.truthy(_t9 := J.get(P, "dvol")) else 0)
        J.get(callOIArr, "push")(cOI)
        J.get(putOIArr, "push")(pOI)
        J.get(callVolArr, "push")(cV)
        J.get(putVolArr, "push")(pV)
        totCallOI = J.add(totCallOI, cOI)
        totPutOI = J.add(totPutOI, pOI)
        totCallVol = J.add(totCallVol, cV)
        totPutVol = J.add(totPutVol, pV)
        maxCallOI = J.get(G_Math, "max")(maxCallOI, cOI)
        maxPutOI = J.get(G_Math, "max")(maxPutOI, pOI)
        if J.truthy(showCalls):
            maxOI = J.get(G_Math, "max")(maxOI, cOI)
            maxVol = J.get(G_Math, "max")(maxVol, cV)
        if J.truthy(showPuts):
            maxOI = J.get(G_Math, "max")(maxOI, pOI)
            maxVol = J.get(G_Math, "max")(maxVol, pV)
        if J.seq(ri, localATM):
            if J.seq(displayMode, "Puts Only"):
                if (not J.nullish(J.get(P, "iv"))):
                    atmIV = J.get(P, "iv")
                elif (not J.nullish(J.get(C, "iv"))):
                    atmIV = J.get(C, "iv")
            else:
                if (not J.nullish(J.get(C, "iv"))):
                    atmIV = J.get(C, "iv")
                elif (not J.nullish(J.get(P, "iv"))):
                    atmIV = J.get(P, "iv")
    J.get(strikes, "forEach")(_f8)
    topCallOI = topNSet(callOIArr, heatTopN)
    topCallVol = topNSet(callVolArr, heatTopN)
    topPutOI = topNSet(putOIArr, heatTopN)
    topPutVol = topNSet(putVolArr, heatTopN)
    flameCallSet = flameSet(callOIArr, callVolArr, maxCallOI, flameTopN)
    flamePutSet = flameSet(putOIArr, putVolArr, maxPutOI, flameTopN)
    def _f9(strike=J.undefined, ri=J.undefined, *_args):
        def _f2(k=J.undefined, *_args):
            return J.seq(G_parseFloat(k), strike)
        sk = (_t1 if J.truthy(_t1 := J.get(J.get(G_Object, "keys")(chainData), "find")(_f2)) else J.get(strike, "toString")())
        sd = (_t3 if J.truthy(_t3 := J.get(chainData, sk)) else J.obj())
        C = (_t4 if J.truthy(_t4 := J.get(sd, "C")) else J.obj())
        P = (_t5 if J.truthy(_t5 := J.get(sd, "P")) else J.obj())
        callOI = (_t6 if J.truthy(_t6 := J.get(C, "oi")) else 0)
        putOI = (_t7 if J.truthy(_t7 := J.get(P, "oi")) else 0)
        callVol = (_t8 if J.truthy(_t8 := J.get(C, "dvol")) else 0)
        putVol = (_t9 if J.truthy(_t9 := J.get(P, "dvol")) else 0)
        isATM = J.seq(ri, localATM)
        isITM_C = J.lt(strike, currentPrice)
        isITM_P = J.gt(strike, currentPrice)
        altBg = (J.get(TH, "rowAlt1") if J.seq(J.mod(ri, 2), 0) else J.get(TH, "rowAlt2"))
        callRowBg = (J.get(TH, "atmBg") if J.truthy(isATM) else (J.get(TH, "itmTint") if (J.truthy(showMoneyness) and J.truthy(isITM_C)) else altBg))
        putRowBg = (J.get(TH, "atmBg") if J.truthy(isATM) else (J.get(TH, "itmTint") if (J.truthy(showMoneyness) and J.truthy(isITM_P)) else altBg))
        callFlow = ("\ud83d\udd25" if J.truthy(J.get(flameCallSet, ri)) else "")
        putFlow = ("\ud83d\udd25" if J.truthy(J.get(flamePutSet, ri)) else "")
        callOIBg = (_t10 if J.truthy(_t10 := oiHeatBg(callOI, maxOI, "C", ri)) else callRowBg)
        putOIBg = (_t11 if J.truthy(_t11 := oiHeatBg(putOI, maxOI, "P", ri)) else putRowBg)
        callVolBg = (_t12 if J.truthy(_t12 := volHeatBg(callVol, maxVol, "C", ri)) else callRowBg)
        putVolBg = (_t13 if J.truthy(_t13 := volHeatBg(putVol, maxVol, "P", ri)) else putRowBg)
        callCells = J.JSArray([])
        if J.truthy(showCalls):
            J.get(callCells, "push")(mkCell(fmtC(callOI), J.obj(("bg", callOIBg), ("color", (J.get(TH, "atmText") if J.truthy(isATM) else J.get(TH, "callText"))), ("bold", isATM))))
            J.get(callCells, "push")(mkCell(J.add(callFlow, fmtC(callVol)), J.obj(("bg", callVolBg), ("color", (J.get(TH, "atmText") if J.truthy(isATM) else J.get(TH, "callMuted"))))))
            if J.truthy(showDelta):
                J.get(callCells, "push")(mkCell(fmtG(J.get(C, "gd")), J.obj(("bg", callRowBg), ("color", J.get(TH, "callMuted")))))
            if J.truthy(showIV):
                J.get(callCells, "push")(mkCell(fmtIV(J.get(C, "iv")), J.obj(("bg", callRowBg), ("color", J.get(TH, "muted")))))
            J.get(callCells, "push")(mkCell(fmtP(J.get(C, "b")), J.obj(("bg", callRowBg), ("color", J.get(TH, "callMuted")))))
            J.get(callCells, "push")(mkCell(fmtP(J.get(C, "a")), J.obj(("bg", callRowBg), ("color", J.get(TH, "callMuted")))))
            J.get(callCells, "push")(mkCell(fmtP(J.get(C, "l")), J.obj(("bg", callRowBg), ("color", (J.get(TH, "atmText") if J.truthy(isATM) else J.get(TH, "callText"))), ("bold", True))))
        strikeCell = mkCell(J.add(("▶ " if J.truthy(isATM) else "  "), fmtSk(strike)), J.obj(("bg", (J.get(TH, "atmBg") if J.truthy(isATM) else J.get(TH, "panelBg"))), ("color", (J.get(TH, "atmText") if J.truthy(isATM) else J.get(TH, "title"))), ("bold", True), ("align", "center")))
        putCells = J.JSArray([])
        if J.truthy(showPuts):
            J.get(putCells, "push")(mkCell(fmtP(J.get(P, "l")), J.obj(("bg", putRowBg), ("color", (J.get(TH, "atmText") if J.truthy(isATM) else J.get(TH, "putText"))), ("bold", True))))
            J.get(putCells, "push")(mkCell(fmtP(J.get(P, "b")), J.obj(("bg", putRowBg), ("color", J.get(TH, "putMuted")))))
            J.get(putCells, "push")(mkCell(fmtP(J.get(P, "a")), J.obj(("bg", putRowBg), ("color", J.get(TH, "putMuted")))))
            if J.truthy(showIV):
                J.get(putCells, "push")(mkCell(fmtIV(J.get(P, "iv")), J.obj(("bg", putRowBg), ("color", J.get(TH, "muted")))))
            if J.truthy(showDelta):
                J.get(putCells, "push")(mkCell(fmtG(J.get(P, "gd")), J.obj(("bg", putRowBg), ("color", J.get(TH, "putMuted")))))
            J.get(putCells, "push")(mkCell(J.add(putFlow, fmtC(putVol)), J.obj(("bg", putVolBg), ("color", (J.get(TH, "atmText") if J.truthy(isATM) else J.get(TH, "putMuted"))))))
            J.get(putCells, "push")(mkCell(fmtC(putOI), J.obj(("bg", putOIBg), ("color", (J.get(TH, "atmText") if J.truthy(isATM) else J.get(TH, "putText"))), ("bold", isATM))))
        rowCells = J.JSArray([])
        if J.truthy(showCalls):
            J.get(rowCells, "push")(*J.spread(callCells))
            J.get(rowCells, "push")(spacer(J.get(TH, "bg")))
        J.get(rowCells, "push")(strikeCell)
        if J.truthy(showPuts):
            J.get(rowCells, "push")(spacer(J.get(TH, "bg")))
            J.get(rowCells, "push")(*J.spread(putCells))
        return J.obj(("cells", rowCells))
    dataRows = J.get(strikes, "map")(_f9)
    callHdrCount = J.add(J.add(5, (1 if J.truthy(showDelta) else 0)), (1 if J.truthy(showIV) else 0))
    putHdrCount = J.add(J.add(5, (1 if J.truthy(showDelta) else 0)), (1 if J.truthy(showIV) else 0))
    totalCols = J.add(J.add(J.add(J.add((callHdrCount if J.truthy(showCalls) else 0), (1 if J.truthy(showCalls) else 0)), 1), (1 if J.truthy(showPuts) else 0)), (putHdrCount if J.truthy(showPuts) else 0))
    pcrVol = (J.get(J.div(totPutVol, totCallVol), "toFixed")(2) if J.gt(totCallVol, 0) else "–")
    pcrColor = (J.get(TH, "putHi") if J.gt(G_parseFloat(pcrVol), 1.2) else (J.get(TH, "callHi") if J.lt(G_parseFloat(pcrVol), 0.8) else J.get(TH, "warn")))
    modeTag = ("  ·  Calls" if J.seq(displayMode, "Calls Only") else ("  ·  Puts" if J.seq(displayMode, "Puts Only") else ""))
    titleText = J.add(J.add(J.add(J.add(J.add(J.add(J.add(J.add(J.add(J.add(J.add(J.add("\ud83d\udcca ", ticker), " Chain"), modeTag), "  ·  "), (J.add(schedTag, " ") if J.truthy(schedTag) else "")), expiryDisplay), " ("), daysToExp), "DTE)  ·  "), "Spot: $"), J.get(currentPrice, "toFixed")(2)), (J.add(J.add("  ·  ATM IV: ", J.get(atmIV, "toFixed")(0)), "%") if (not J.nullish(atmIV)) else ""))
    overlayRows = J.JSArray([])
    J.get(overlayRows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", titleText), ("color", J.get(TH, "title")), ("background", J.get(TH, "panelBg")), ("fontWeight", "bold"), ("fontSize", px(16)), ("textAlign", "center"), ("colspan", totalCols), ("paddingTop", px(7)), ("paddingBottom", px(7)), ("paddingLeft", px(8)), ("paddingRight", px(8)))]))))
    sectionCells = J.JSArray([])
    if J.truthy(showCalls):
        J.get(sectionCells, "push")(hdrCell("— CALLS —", J.obj(("bg", J.get(TH, "callBg")), ("color", J.get(TH, "callHi")), ("colspan", callHdrCount), ("fontSize", px(13)))))
        J.get(sectionCells, "push")(spacer(J.get(TH, "bg")))
    J.get(sectionCells, "push")(hdrCell(" ", J.obj(("bg", J.get(TH, "bg")))))
    if J.truthy(showPuts):
        J.get(sectionCells, "push")(spacer(J.get(TH, "bg")))
        J.get(sectionCells, "push")(hdrCell("— PUTS —", J.obj(("bg", J.get(TH, "putBg")), ("color", J.get(TH, "putHi")), ("colspan", putHdrCount), ("fontSize", px(13)))))
    J.get(overlayRows, "push")(J.obj(("cells", sectionCells)))
    callHdrs = J.JSArray([hdrCell("OI"), hdrCell("Vol")])
    if J.truthy(showDelta):
        J.get(callHdrs, "push")(hdrCell("Δ"))
    if J.truthy(showIV):
        J.get(callHdrs, "push")(hdrCell("IV"))
    J.get(callHdrs, "push")(hdrCell("Bid"), hdrCell("Ask"), hdrCell("Last"))
    putHdrs = J.JSArray([hdrCell("Last"), hdrCell("Bid"), hdrCell("Ask")])
    if J.truthy(showIV):
        J.get(putHdrs, "push")(hdrCell("IV"))
    if J.truthy(showDelta):
        J.get(putHdrs, "push")(hdrCell("Δ"))
    J.get(putHdrs, "push")(hdrCell("Vol"), hdrCell("OI"))
    headerCells = J.JSArray([])
    if J.truthy(showCalls):
        J.get(headerCells, "push")(*J.spread(callHdrs))
        J.get(headerCells, "push")(spacer(J.get(TH, "bg")))
    J.get(headerCells, "push")(hdrCell("Strike", J.obj(("color", J.get(TH, "warn")))))
    if J.truthy(showPuts):
        J.get(headerCells, "push")(spacer(J.get(TH, "bg")))
        J.get(headerCells, "push")(*J.spread(putHdrs))
    J.get(overlayRows, "push")(J.obj(("cells", headerCells)))
    J.get(overlayRows, "push")(*J.spread(dataRows))
    sumCallSpacers = J.JSArray([*J.spread((J.JSArray([mkCell("", J.obj(("bg", J.get(TH, "callBg"))))]) if J.truthy(showDelta) else J.JSArray([]))), *J.spread((J.JSArray([mkCell("", J.obj(("bg", J.get(TH, "callBg"))))]) if J.truthy(showIV) else J.JSArray([]))), mkCell("", J.obj(("bg", J.get(TH, "callBg")))), mkCell("", J.obj(("bg", J.get(TH, "callBg"))))])
    sumPutSpacers = J.JSArray([mkCell("", J.obj(("bg", J.get(TH, "putBg")))), mkCell("", J.obj(("bg", J.get(TH, "putBg")))), *J.spread((J.JSArray([mkCell("", J.obj(("bg", J.get(TH, "putBg"))))]) if J.truthy(showIV) else J.JSArray([]))), *J.spread((J.JSArray([mkCell("", J.obj(("bg", J.get(TH, "putBg"))))]) if J.truthy(showDelta) else J.JSArray([])))])
    footerCells = J.JSArray([])
    if J.truthy(showCalls):
        J.get(footerCells, "push")(mkCell(fmtC(totCallOI), J.obj(("bg", J.get(TH, "callBg")), ("color", J.get(TH, "callHi")), ("bold", True))))
        J.get(footerCells, "push")(mkCell(fmtC(totCallVol), J.obj(("bg", J.get(TH, "callBg")), ("color", J.get(TH, "callHi")), ("bold", True))))
        J.get(footerCells, "push")(*J.spread(sumCallSpacers))
        J.get(footerCells, "push")(mkCell("Σ", J.obj(("bg", J.get(TH, "callBg")), ("color", J.get(TH, "callHi")), ("bold", True), ("align", "center"))))
        J.get(footerCells, "push")(spacer(J.get(TH, "bg")))
    if (J.truthy(showCalls) and J.truthy(showPuts)):
        J.get(footerCells, "push")(mkCell(J.add("P/C  V:", pcrVol), J.obj(("bg", J.get(TH, "panelBg")), ("color", pcrColor), ("bold", True), ("align", "center"))))
    else:
        J.get(footerCells, "push")(mkCell("", J.obj(("bg", J.get(TH, "panelBg")))))
    if J.truthy(showPuts):
        J.get(footerCells, "push")(spacer(J.get(TH, "bg")))
        J.get(footerCells, "push")(mkCell("Σ", J.obj(("bg", J.get(TH, "putBg")), ("color", J.get(TH, "putHi")), ("bold", True), ("align", "center"))))
        J.get(footerCells, "push")(*J.spread(sumPutSpacers))
        J.get(footerCells, "push")(mkCell(fmtC(totPutVol), J.obj(("bg", J.get(TH, "putBg")), ("color", J.get(TH, "putHi")), ("bold", True))))
        J.get(footerCells, "push")(mkCell(fmtC(totPutOI), J.obj(("bg", J.get(TH, "putBg")), ("color", J.get(TH, "putHi")), ("bold", True))))
    J.get(overlayRows, "push")(J.obj(("cells", footerCells)))
    if J.truthy(showGreeksRow):
        def _f11(k=J.undefined, *_args):
            return J.seq(G_parseFloat(k), J.get(strikes, localATM))
        atmSk = (_t10 if J.truthy(_t10 := J.get(J.get(G_Object, "keys")(chainData), "find")(_f11)) else J.get(J.get(strikes, localATM), "toString")())
        atmData = (_t12 if J.truthy(_t12 := J.get(chainData, atmSk)) else J.obj())
        aC = (_t13 if J.truthy(_t13 := J.get(atmData, "C")) else J.obj())
        aP = (_t14 if J.truthy(_t14 := J.get(atmData, "P")) else J.obj())
        greeksText = J.add("ATM ", fmtSk(J.get(strikes, localATM)))
        if J.truthy(showCalls):
            greeksText = J.add(greeksText, J.add(J.add(J.add(J.add(J.add("  ·  Calls: Δ", fmtG(J.get(aC, "gd"))), " Γ"), fmtG(J.get(aC, "gg"))), " Θ"), fmtG(J.get(aC, "gt"))))
        if J.truthy(showPuts):
            greeksText = J.add(greeksText, J.add(J.add(J.add(J.add(J.add(J.add(("  |  " if J.truthy(showCalls) else "  ·  "), "Puts: Δ"), fmtG(J.get(aP, "gd"))), " Γ"), fmtG(J.get(aP, "gg"))), " Θ"), fmtG(J.get(aP, "gt"))))
        J.get(overlayRows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", greeksText), ("color", J.get(TH, "warn")), ("background", J.get(TH, "panelBg")), ("fontWeight", "bold"), ("fontSize", px(13)), ("textAlign", "center"), ("colspan", totalCols), ("paddingTop", px(5)), ("paddingBottom", px(5)))]))))
    G_paint_overlay("OptionsChainV34", J.obj(("position", "bottom_left"), ("offset_y", 0), ("order", "above_all")), J.obj(("background", J.get(TH, "bg")), ("border", J.add("2px solid ", J.get(TH, "border"))), ("borderRadius", px(6)), ("padding", px(3)), ("fontFamily", "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace"), ("rows", overlayRows)))


register_store_indicator(
    script,
    name='options_chain_grid_TS',
    title='Options Chain Grid',
    developer='Rock Regan',
    url='https://trendspider.com/trading-tools-store/indicators/69f11e-options-chain-grid/',
    position='price',
    inputs=[{'id': 'expiry', 'title': 'Expiry', 'type': 'select_wide', 'default': '0DTE', 'options': ['0DTE', '1DTE', '2DTE', '3DTE', '5DTE', '7DTE', '14DTE', '30DTE', '60DTE', '90DTE']}, {'id': 'strikes_around_atm', 'title': 'Strikes Around ATM', 'type': 'number', 'default': 3}, {'id': 'display', 'title': 'Display', 'type': 'select_wide', 'default': 'Both', 'options': ['Both', 'Calls Only', 'Puts Only']}, {'id': 'ui_scale', 'title': 'UI Scale', 'type': 'select_wide', 'default': '100%', 'options': ['75%', '90%', '100%', '110%', '125%', '150%']}, {'id': 'show_iv_column', 'title': 'Show IV Column', 'type': 'boolean', 'default': True}, {'id': 'show___column', 'title': 'Show Δ Column', 'type': 'boolean', 'default': True}, {'id': 'show_greeks_footer', 'title': 'Show Greeks Footer', 'type': 'boolean', 'default': False}, {'id': 'oi_heatmap', 'title': 'OI Heatmap', 'type': 'boolean', 'default': True}, {'id': 'vol_heatmap', 'title': 'Vol Heatmap', 'type': 'boolean', 'default': True}, {'id': 'heatmap_top_n', 'title': 'Heatmap Top N', 'type': 'number', 'default': 3}, {'id': 'flame_top_n', 'title': 'Flame Top N', 'type': 'number', 'default': 2}, {'id': 'itm_otm_tint', 'title': 'ITM/OTM Tint', 'type': 'boolean', 'default': False}],
    outputs=['chainv34ref'],
    signals=[],
    requires=['options_data_for_expiration', 'options_schedule'],
    parity='exact',
)
