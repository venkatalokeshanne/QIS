"""
Expected Options Move (Daily, Weekly, Monthly) -- TrendSpider store indicator by Jared Crean.

Registered as "expected_options_move_daily_weekly_monthly_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/69e439-expected-options-move-daily-weekly-monthly/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Infinity = G["Infinity"]
    G_Math = G["Math"]
    G_Number = G["Number"]
    G_Object = G["Object"]
    G_Promise = G["Promise"]
    G_assert = G["assert"]
    G_close = G["close"]
    G_constants = G["constants"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_fill = G["fill"]
    G_horizontal_line = G["horizontal_line"]
    G_input = G["input"]
    G_paint = G["paint"]
    G_paint_overlay = G["paint_overlay"]
    G_request = G["request"]
    G_series_of = G["series_of"]
    G_describe_indicator("Expected Options Move (Daily, Weekly, Monthly)")
    showDailyBand = J.get(G_input, "boolean")("Show Daily Band", True)
    showWeeklyBand = J.get(G_input, "boolean")("Show Weekly Band", True)
    showMonthlyBand = J.get(G_input, "boolean")("Show Monthly Band", True)
    dailyBandColor = J.get(G_input, "color")("Daily Band Color", "#FFD700")
    weeklyBandColor = J.get(G_input, "color")("Weekly Band Color", "#00CED1")
    monthlyBandColor = J.get(G_input, "color")("Monthly Band Color", "#FF8C00")
    dailyLineStyle = J.get(G_input, "select")("Daily Line Style", "dotted", J.JSArray(["line", "dotted"]))
    weeklyLineStyle = J.get(G_input, "select")("Weekly Line Style", "dotted", J.JSArray(["line", "dotted"]))
    monthlyLineStyle = J.get(G_input, "select")("Monthly Line Style", "line", J.JSArray(["line", "dotted"]))
    lineThickness = G_input("Line Thickness", 2)
    fillOpacity = G_input("Fill Opacity", 0.08)
    dailyMaxDte = G_input("Daily Max DTE", 2)
    weeklyMinDte = G_input("Weekly Min DTE", 4)
    weeklyMaxDte = G_input("Weekly Max DTE", 10)
    monthlyMinDte = G_input("Monthly Min DTE", 20)
    monthlyMaxDte = G_input("Monthly Max DTE", 50)
    useAsymmetric = J.get(G_input, "boolean")("Asymmetric Bands (16-delta)", False)
    straddleMult = G_input("EM Multiplier", 0.85)
    wideSpreadCutoff = G_input("IV Fallback Spread", 0.2)
    schedule = J.get(G_request, "options_schedule")(J.get(G_current, "ticker"))
    G_assert(((not J.truthy(J.get(schedule, "error"))) if J.truthy(_t1 := schedule) else _t1), J.template("Error fetching options schedule: ", (_t2 if J.truthy(_t2 := J.chain_end(J.oget(schedule, "error"))) else "Unknown error")))
    def _f3(a=J.undefined, b=J.undefined, *_args):
        return J.sub(J.get(J.get(a, "expiration"), "dte"), J.get(J.get(b, "expiration"), "dte"))
    sortedSchedule = J.get(J.JSArray([*J.spread(schedule)]), "sort")(_f3)
    def findExpiration(minDte=J.undefined, maxDte=J.undefined, *_args):
        for exp in J.iter_of(sortedSchedule):
            dte = J.get(J.get(exp, "expiration"), "dte")
            if (J.ge(dte, minDte) and J.le(dte, maxDte)):
                return exp
        return None
    def mid(q=J.undefined, *_args):
        if (not J.truthy(q)):
            return None
        if (J.truthy(J.get(q, "l")) and J.gt(J.get(q, "l"), 0)):
            return J.get(q, "l")
        if (J.gt(J.get(q, "b"), 0) and J.gt(J.get(q, "a"), 0)):
            return J.div(J.add(J.get(q, "b"), J.get(q, "a")), 2)
        if J.gt(J.get(q, "b"), 0):
            return J.get(q, "b")
        if J.gt(J.get(q, "a"), 0):
            return J.get(q, "a")
        return None
    def relSpread(q=J.undefined, *_args):
        if (((not J.truthy(q)) or (not J.gt(J.get(q, "b"), 0))) or (not J.gt(J.get(q, "a"), 0))):
            return 1
        m = J.div(J.add(J.get(q, "a"), J.get(q, "b")), 2)
        return (J.div(J.sub(J.get(q, "a"), J.get(q, "b")), m) if J.gt(m, 0) else 1)
    def computeExpectedMove(expiration=J.undefined, *_args):
        if (not J.truthy(expiration)):
            return None
        optionsData = J.get(G_request, "options_data_for_expiration")(J.get(G_current, "ticker"), J.get(J.get(expiration, "expiration"), "code"), J.JSArray(["l", "b", "a", "iv", "gd"]))
        if (not J.truthy(J.chain_end(J.oget(optionsData, "resultByStrike")))):
            return None
        currentPrice = J.get(J.get(optionsData, "underlyingSymbolQuote"), "lastPrice")
        def _f1(x=J.undefined, y=J.undefined, *_args):
            return J.sub(x, y)
        strikes = J.get(J.get(J.get(G_Object, "keys")(J.get(optionsData, "resultByStrike")), "map")(G_Number), "sort")(_f1)
        if J.seq(J.get(strikes, "length"), 0):
            return None
        lowerIdx = 0
        i = 0
        while J.lt(i, J.get(strikes, "length")):
            if J.le(J.get(strikes, i), currentPrice):
                lowerIdx = i
            else:
                break
            i = J.inc(i)
        upperIdx = J.get(G_Math, "min")(J.add(lowerIdx, 1), J.sub(J.get(strikes, "length"), 1))
        lowStrike = J.get(strikes, lowerIdx)
        highStrike = J.get(strikes, upperIdx)
        def quoteAt(strike=J.undefined, *_args):
            d = J.get(J.get(optionsData, "resultByStrike"), strike)
            c = mid(J.chain_end(J.oget(d, "C")))
            p = mid(J.chain_end(J.oget(d, "P")))
            if ((((not J.truthy(c)) or (not J.truthy(p))) or J.le(c, 0)) or J.le(p, 0)):
                return None
            return J.obj(("call", c), ("put", p), ("iv", (None if J.nullish(_t1 := (J.chain_end(J.oget(J.oget(d, "P"), "iv")) if J.nullish(_t2 := J.chain_end(J.oget(J.oget(d, "C"), "iv"))) else _t2)) else _t1)), ("callSpread", relSpread(J.chain_end(J.oget(d, "C")))), ("putSpread", relSpread(J.chain_end(J.oget(d, "P")))))
        lowQ = quoteAt(lowStrike)
        highQ = quoteAt(highStrike)
        if ((not J.truthy(lowQ)) and (not J.truthy(highQ))):
            return None
        callPrice = J.undefined
        putPrice = J.undefined
        iv = J.undefined
        worstSpread = J.undefined
        if ((J.truthy(lowQ) and J.truthy(highQ)) and J.sne(lowStrike, highStrike)):
            t = J.div(J.sub(currentPrice, lowStrike), J.sub(highStrike, lowStrike))
            callPrice = J.add(J.get(lowQ, "call"), J.mul(t, J.sub(J.get(highQ, "call"), J.get(lowQ, "call"))))
            putPrice = J.add(J.get(lowQ, "put"), J.mul(t, J.sub(J.get(highQ, "put"), J.get(lowQ, "put"))))
            iv = (J.add(J.get(lowQ, "iv"), J.mul(t, J.sub(J.get(highQ, "iv"), J.get(lowQ, "iv")))) if ((not J.nullish(J.get(lowQ, "iv"))) and (not J.nullish(J.get(highQ, "iv")))) else (J.get(highQ, "iv") if J.nullish(_t2 := J.get(lowQ, "iv")) else _t2))
            worstSpread = J.get(G_Math, "max")(J.get(lowQ, "callSpread"), J.get(lowQ, "putSpread"), J.get(highQ, "callSpread"), J.get(highQ, "putSpread"))
        else:
            d = (_t3 if J.truthy(_t3 := lowQ) else highQ)
            callPrice = J.get(d, "call")
            putPrice = J.get(d, "put")
            iv = J.get(d, "iv")
            worstSpread = J.get(G_Math, "max")(J.get(d, "callSpread"), J.get(d, "putSpread"))
        straddle = J.add(callPrice, putPrice)
        emStraddle = J.mul(straddle, straddleMult)
        dte = J.get(J.get(expiration, "expiration"), "dte")
        emIv = (J.mul(J.mul(currentPrice, iv), J.get(G_Math, "sqrt")(J.div(dte, 365))) if ((J.truthy(iv) and J.gt(iv, 0)) and J.gt(dte, 0)) else None)
        useIv = (emIv if J.truthy(_t4 := J.gt(worstSpread, wideSpreadCutoff)) else _t4)
        expectedMove = (emIv if J.truthy(useIv) else emStraddle)
        source = ("IV" if J.truthy(useIv) else "straddle")
        upperStrike = None
        lowerStrike = None
        bestCallDiff = G_Infinity
        bestPutDiff = G_Infinity
        for strike in J.iter_of(strikes):
            d_2 = J.get(J.get(optionsData, "resultByStrike"), strike)
            if (not J.nullish(J.chain_end(J.oget(J.oget(d_2, "C"), "gd")))):
                raw = J.get(J.get(d_2, "C"), "gd")
                norm = (J.div(raw, 100) if J.gt(J.get(G_Math, "abs")(raw), 1) else raw)
                diff = J.get(G_Math, "abs")(J.sub(norm, 0.16))
                if J.lt(diff, bestCallDiff):
                    bestCallDiff = diff
                    upperStrike = strike
            if (not J.nullish(J.chain_end(J.oget(J.oget(d_2, "P"), "gd")))):
                raw_2 = J.get(J.get(d_2, "P"), "gd")
                norm_2 = (J.div(raw_2, 100) if J.gt(J.get(G_Math, "abs")(raw_2), 1) else raw_2)
                diff_2 = J.get(G_Math, "abs")(J.add(norm_2, 0.16))
                if J.lt(diff_2, bestPutDiff):
                    bestPutDiff = diff_2
                    lowerStrike = strike
        return J.obj(("expectedMove", expectedMove), ("currentPrice", currentPrice), ("dte", dte), ("source", source), ("emStraddle", emStraddle), ("emIv", emIv), ("upperStrike", upperStrike), ("lowerStrike", lowerStrike))
    dailyExp = findExpiration(0, dailyMaxDte)
    weeklyExp = findExpiration(weeklyMinDte, weeklyMaxDte)
    monthlyExp = findExpiration(monthlyMinDte, monthlyMaxDte)
    _t4 = J.iter_of(J.get(G_Promise, "all")(J.JSArray([computeExpectedMove(dailyExp), computeExpectedMove(weeklyExp), computeExpectedMove(monthlyExp)])))
    dailyMove = (_t4[0] if 0 < len(_t4) else J.undefined)
    weeklyMove = (_t4[1] if 1 < len(_t4) else J.undefined)
    monthlyMove = (_t4[2] if 2 < len(_t4) else J.undefined)
    anchor = (J.get(G_close, J.sub(J.get(G_close, "length"), 1)) if J.nullish(_t5 := (J.chain_end(J.oget(dailyMove, "currentPrice")) if J.nullish(_t6 := (J.chain_end(J.oget(weeklyMove, "currentPrice")) if J.nullish(_t7 := J.chain_end(J.oget(monthlyMove, "currentPrice"))) else _t7)) else _t6)) else _t5)
    def paintBand(move=J.undefined, label=J.undefined, color=J.undefined, style=J.undefined, show=J.undefined, *_args):
        noData = (not J.truthy(move))
        upperPrice = J.undefined
        lowerPrice = J.undefined
        if (not J.truthy(noData)):
            if ((J.truthy(useAsymmetric) and (not J.nullish(J.get(move, "upperStrike")))) and (not J.nullish(J.get(move, "lowerStrike")))):
                upperPrice = J.get(move, "upperStrike")
                lowerPrice = J.get(move, "lowerStrike")
            else:
                upperPrice = J.add(anchor, J.get(move, "expectedMove"))
                lowerPrice = J.sub(anchor, J.get(move, "expectedMove"))
        upperSeries = (J.get(G_constants, "empty_series") if J.truthy(noData) else G_horizontal_line(upperPrice))
        lowerSeries = (J.get(G_constants, "empty_series") if J.truthy(noData) else G_horizontal_line(lowerPrice))
        isHidden = (_t1 if J.truthy(_t1 := noData) else (not J.truthy(show)))
        u = G_paint(upperSeries, J.obj(("name", J.template(label, " Upper")), ("color", G_series_of(color)), ("style", style), ("thickness", lineThickness), ("hidden", isHidden), ("ignoreWhenScaling", True)))
        l = G_paint(lowerSeries, J.obj(("name", J.template(label, " Lower")), ("color", G_series_of(color)), ("style", style), ("thickness", lineThickness), ("hidden", isHidden), ("ignoreWhenScaling", True)))
        if (not J.truthy(isHidden)):
            G_fill(u, l, color, fillOpacity)
    paintBand(dailyMove, "Daily", dailyBandColor, dailyLineStyle, showDailyBand)
    paintBand(weeklyMove, "Weekly", weeklyBandColor, weeklyLineStyle, showWeeklyBand)
    paintBand(monthlyMove, "Monthly", monthlyBandColor, monthlyLineStyle, showMonthlyBand)
    def fmtRow(label=J.undefined, move=J.undefined, color=J.undefined, *_args):
        if (not J.truthy(move)):
            return J.obj(("cells", J.JSArray([J.obj(("text", J.template(label, " N/A")), ("color", "#666666"))])))
        text = J.undefined
        if ((J.truthy(useAsymmetric) and (not J.nullish(J.get(move, "upperStrike")))) and (not J.nullish(J.get(move, "lowerStrike")))):
            upMove = J.sub(J.get(move, "upperStrike"), J.get(move, "currentPrice"))
            dnMove = J.sub(J.get(move, "currentPrice"), J.get(move, "lowerStrike"))
            upPct = J.mul(J.div(upMove, J.get(move, "currentPrice")), 100)
            dnPct = J.mul(J.div(dnMove, J.get(move, "currentPrice")), 100)
            tag = (" *" if J.seq(J.get(move, "source"), "IV") else "")
            text = J.template(label, " +$", J.get(upMove, "toFixed")(2), " / -$", J.get(dnMove, "toFixed")(2), " (+", J.get(upPct, "toFixed")(1), "% / -", J.get(dnPct, "toFixed")(1), "%)", tag)
        else:
            pct = J.mul(J.div(J.get(move, "expectedMove"), J.get(move, "currentPrice")), 100)
            tag_2 = (" *" if J.seq(J.get(move, "source"), "IV") else "")
            text = J.template(label, " ±$", J.get(J.get(move, "expectedMove"), "toFixed")(2), " (±", J.get(pct, "toFixed")(2), "%)", tag_2)
        return J.obj(("cells", J.JSArray([J.obj(("text", text), ("color", color))])))
    legendRows = J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", ("1σ Expected Move (asymmetric)" if J.truthy(useAsymmetric) else "1σ Expected Move")), ("color", "white"))]))), fmtRow("Daily:  ", dailyMove, dailyBandColor), fmtRow("Weekly: ", weeklyMove, weeklyBandColor), fmtRow("Monthly:", monthlyMove, monthlyBandColor)])
    def _f8(m=J.undefined, *_args):
        return J.seq(J.chain_end(J.oget(m, "source")), "IV")
    if J.truthy(J.get(J.JSArray([dailyMove, weeklyMove, monthlyMove]), "some")(_f8)):
        J.get(legendRows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", "* IV-based (wide spread)"), ("color", "#888888"))]))))
    def _f9(m=J.undefined, *_args):
        return ((_t2 if J.truthy(_t2 := (J.nullish(J.get(m, "upperStrike")))) else (J.nullish(J.get(m, "lowerStrike")))) if J.truthy(_t1 := m) else _t1)
    if (J.truthy(useAsymmetric) and J.truthy(J.get(J.JSArray([dailyMove, weeklyMove, monthlyMove]), "some")(_f9))):
        J.get(legendRows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", "† delta unavailable, using symmetric EM"), ("color", "#888888"))]))))
    G_paint_overlay("ExpectedMoveLegend", J.obj(("position", "top_right"), ("offset_x", 60), ("offset_y", 20)), J.obj(("rows", legendRows)))


register_store_indicator(
    script,
    name='expected_options_move_daily_weekly_monthly_TS',
    title='Expected Options Move (Daily, Weekly, Monthly)',
    developer='Jared Crean',
    url='https://trendspider.com/trading-tools-store/indicators/69e439-expected-options-move-daily-weekly-monthly/',
    position='price',
    inputs=[{'id': 'show_daily_band', 'title': 'Show Daily Band', 'type': 'boolean', 'default': True}, {'id': 'show_weekly_band', 'title': 'Show Weekly Band', 'type': 'boolean', 'default': True}, {'id': 'show_monthly_band', 'title': 'Show Monthly Band', 'type': 'boolean', 'default': True}, {'id': 'daily_band_color', 'title': 'Daily Band Color', 'type': 'color', 'default': '#FFD700'}, {'id': 'weekly_band_color', 'title': 'Weekly Band Color', 'type': 'color', 'default': '#00CED1'}, {'id': 'monthly_band_color', 'title': 'Monthly Band Color', 'type': 'color', 'default': '#FF8C00'}, {'id': 'daily_line_style', 'title': 'Daily Line Style', 'type': 'select_wide', 'default': 'dotted', 'options': ['line', 'dotted']}, {'id': 'weekly_line_style', 'title': 'Weekly Line Style', 'type': 'select_wide', 'default': 'dotted', 'options': ['line', 'dotted']}, {'id': 'monthly_line_style', 'title': 'Monthly Line Style', 'type': 'select_wide', 'default': 'line', 'options': ['line', 'dotted']}, {'id': 'line_thickness', 'title': 'Line Thickness', 'type': 'number', 'default': 2}, {'id': 'fill_opacity', 'title': 'Fill Opacity', 'type': 'number', 'default': 0.08}, {'id': 'daily_max_dte', 'title': 'Daily Max DTE', 'type': 'number', 'default': 2}, {'id': 'weekly_min_dte', 'title': 'Weekly Min DTE', 'type': 'number', 'default': 4}, {'id': 'weekly_max_dte', 'title': 'Weekly Max DTE', 'type': 'number', 'default': 10}, {'id': 'monthly_min_dte', 'title': 'Monthly Min DTE', 'type': 'number', 'default': 20}, {'id': 'monthly_max_dte', 'title': 'Monthly Max DTE', 'type': 'number', 'default': 50}, {'id': 'asymmetric_bands__16_delta_', 'title': 'Asymmetric Bands (16-delta)', 'type': 'boolean', 'default': False}, {'id': 'em_multiplier', 'title': 'EM Multiplier', 'type': 'number', 'default': 0.85}, {'id': 'iv_fallback_spread', 'title': 'IV Fallback Spread', 'type': 'number', 'default': 0.2}],
    outputs=['daily_upper', 'daily_lower', 'weekly_upper', 'weekly_lower', 'monthly_upper', 'monthly_lower'],
    signals=[],
    requires=['options_data_for_expiration', 'options_schedule'],
    parity='exact',
)
