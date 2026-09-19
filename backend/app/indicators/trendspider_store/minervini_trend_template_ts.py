"""
Minervini Trend Template -- TrendSpider store indicator by TrendSpider.

Registered as "minervini_trend_template_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68cda6-minervini-trend-template/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Boolean = G["Boolean"]
    G_Math = G["Math"]
    G_Object = G["Object"]
    G_assert = G["assert"]
    G_close = G["close"]
    G_color_candles = G["color_candles"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_highest = G["highest"]
    G_input = G["input"]
    G_interpolate_sparse_series = G["interpolate_sparse_series"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_lowest = G["lowest"]
    G_paint = G["paint"]
    G_paint_overlay = G["paint_overlay"]
    G_parseInt = G["parseInt"]
    G_register_signal = G["register_signal"]
    G_request = G["request"]
    G_series_of = G["series_of"]
    G_shift = G["shift"]
    G_sma = G["sma"]
    G_time = G["time"]
    def clamp01(t=J.undefined, *_args):
        return J.get(G_Math, "max")(0, J.get(G_Math, "min")(1, t))
    def hex_to_rgb(hex=J.undefined, *_args):
        h = J.get(hex, "replace")("#", "")
        r = G_parseInt(J.get(h, "substring")(0, 2), 16)
        g = G_parseInt(J.get(h, "substring")(2, 4), 16)
        b = G_parseInt(J.get(h, "substring")(4, 6), 16)
        return J.obj(("r", r), ("g", g), ("b", b))
    def rgb_to_hex(r=J.undefined, g=J.undefined, b=J.undefined, *_args):
        def to2(n=J.undefined, *_args):
            s = J.get(J.get(J.get(G_Math, "round")(J.get(G_Math, "max")(0, J.get(G_Math, "min")(255, n))), "toString")(16), "toUpperCase")()
            return (J.add("0", s) if J.seq(J.get(s, "length"), 1) else s)
        return J.add(J.add(J.add("#", to2(r)), to2(g)), to2(b))
    def lerp_color(c1=J.undefined, c2=J.undefined, t=J.undefined, *_args):
        a = hex_to_rgb(c1)
        b = hex_to_rgb(c2)
        r = J.add(J.get(a, "r"), J.mul(J.sub(J.get(b, "r"), J.get(a, "r")), t))
        g = J.add(J.get(a, "g"), J.mul(J.sub(J.get(b, "g"), J.get(a, "g")), t))
        bl = J.add(J.get(a, "b"), J.mul(J.sub(J.get(b, "b"), J.get(a, "b")), t))
        return rgb_to_hex(r, g, bl)
    def color_from_gradient(v=J.undefined, lo=J.undefined, hi=J.undefined, cLo=J.undefined, cHi=J.undefined, *_args):
        if (((J.nullish(v)) or (J.nullish(lo))) or (J.nullish(hi))):
            return None
        t = clamp01(J.div(J.sub(v, lo), J.sub(hi, lo)))
        return lerp_color(cLo, cHi, t)
    G_describe_indicator("Mark Minervini Trend Template Candles")
    showTable = J.get(G_input, "boolean")("Show Criteria Table", True)
    colorPalette = J.JSArray(["#FF1A1A", "#FF4D1A", "#FF751A", "#FF9933", "#FFB84D", "#FFD966", "#99CCFF", "#66B2FF", "#3399FF", "#00F2FE"])
    nativeSMA50 = G_sma(G_close, 50)
    nativeSMA150 = G_sma(G_close, 150)
    nativeSMA200 = G_sma(G_close, 200)
    weeklyDataFor52Week = J.get(G_request, "history")(J.get(G_current, "ticker"), "W")
    G_assert((not J.truthy(J.get(weeklyDataFor52Week, "error"))), J.template("Error fetching weekly data: ", J.get(weeklyDataFor52Week, "error")))
    weekly52WeekHigh = G_highest(J.get(weeklyDataFor52Week, "high"), 52)
    weekly52WeekLow = G_lowest(J.get(weeklyDataFor52Week, "low"), 52)
    native52WeekHigh = G_interpolate_sparse_series(G_land_points_onto_series(J.get(weeklyDataFor52Week, "time"), weekly52WeekHigh, G_time, "le"), "constant")
    native52WeekLow = G_interpolate_sparse_series(G_land_points_onto_series(J.get(weeklyDataFor52Week, "time"), weekly52WeekLow, G_time, "le"), "constant")
    nativeSMA200Shifted = G_shift(nativeSMA200, 30)
    nativeRP = G_series_of(None)
    relativePerformanceData = J.get(G_request, "relative_performance")(J.get(G_current, "ticker"), "yearly", "spx500")
    if ((not J.truthy(J.get(relativePerformanceData, "error"))) and J.gt(J.get(relativePerformanceData, "length"), 0)):
        def _f1(_dataPoint=J.undefined, *_args):
            return J.get(_dataPoint, 1)
        rpValues = J.get(relativePerformanceData, "map")(_f1)
        def _f2(_dataPoint=J.undefined, *_args):
            return J.get(_dataPoint, 0)
        rpTimes = J.get(relativePerformanceData, "map")(_f2)
        nativeRP = G_interpolate_sparse_series(G_land_points_onto_series(rpTimes, rpValues, G_time, "le"), "constant")
    def _f3(currentClose_2=J.undefined, sma50=J.undefined, sma150=J.undefined, sma200=J.undefined, high52=J.undefined, low52=J.undefined, rp=J.undefined, sma200_30_ago=J.undefined, *_args):
        score = 0
        if ((rp is not None) and J.gt(rp, 70)):
            score = J.inc(score)
        if (((currentClose_2 is not None) and (sma50 is not None)) and J.gt(currentClose_2, sma50)):
            score = J.inc(score)
        if (((currentClose_2 is not None) and (sma150 is not None)) and J.gt(currentClose_2, sma150)):
            score = J.inc(score)
        if (((currentClose_2 is not None) and (sma200 is not None)) and J.gt(currentClose_2, sma200)):
            score = J.inc(score)
        if (((sma50 is not None) and (sma150 is not None)) and J.gt(sma50, sma150)):
            score = J.inc(score)
        if (((sma50 is not None) and (sma200 is not None)) and J.gt(sma50, sma200)):
            score = J.inc(score)
        if (((sma150 is not None) and (sma200 is not None)) and J.gt(sma150, sma200)):
            score = J.inc(score)
        if (((currentClose_2 is not None) and (low52 is not None)) and J.ge(currentClose_2, J.mul(low52, 1.3))):
            score = J.inc(score)
        if (((currentClose_2 is not None) and (high52 is not None)) and J.ge(currentClose_2, J.mul(high52, 0.75))):
            score = J.inc(score)
        if (((sma200 is not None) and (sma200_30_ago is not None)) and J.gt(sma200, sma200_30_ago)):
            score = J.inc(score)
        return score
    nativeScores = G_for_every(G_close, nativeSMA50, nativeSMA150, nativeSMA200, native52WeekHigh, native52WeekLow, nativeRP, nativeSMA200Shifted, _f3)
    def _f4(score=J.undefined, prev=J.undefined, i=J.undefined, *_args):
        if (score is None):
            return (J.get(colorPalette, 0) if J.seq(i, 0) else prev)
        if (J.ge(score, 1) and J.le(score, 10)):
            return J.get(colorPalette, J.sub(score, 1))
        return J.get(colorPalette, 0)
    nativeColors = G_for_every(nativeScores, _f4)
    G_color_candles(nativeColors)
    def _f5(score=J.undefined, *_args):
        return (J.seq(score, 10) if J.truthy(_t1 := (score is not None)) else _t1)
    G_register_signal(G_for_every(nativeScores, _f5), "Meets All 10 Trend Template Criteria")
    def _f6(score=J.undefined, *_args):
        return (J.ge(score, 9) if J.truthy(_t1 := (score is not None)) else _t1)
    G_register_signal(G_for_every(nativeScores, _f6), "9+ Criteria Met")
    def _f7(score=J.undefined, *_args):
        return (J.ge(score, 8) if J.truthy(_t1 := (score is not None)) else _t1)
    G_register_signal(G_for_every(nativeScores, _f7), "8+ Criteria Met")
    def _f8(score=J.undefined, *_args):
        return (J.ge(score, 7) if J.truthy(_t1 := (score is not None)) else _t1)
    G_register_signal(G_for_every(nativeScores, _f8), "7+ Criteria Met")
    def _f9(score=J.undefined, *_args):
        return (J.ge(score, 6) if J.truthy(_t1 := (score is not None)) else _t1)
    G_register_signal(G_for_every(nativeScores, _f9), "6+ Criteria Met")
    def _f10(score=J.undefined, *_args):
        return (J.ge(score, 5) if J.truthy(_t1 := (score is not None)) else _t1)
    G_register_signal(G_for_every(nativeScores, _f10), "5+ Criteria Met")
    def _f11(score=J.undefined, *_args):
        return (J.ge(score, 4) if J.truthy(_t1 := (score is not None)) else _t1)
    G_register_signal(G_for_every(nativeScores, _f11), "4+ Criteria Met")
    def _f12(score=J.undefined, *_args):
        return (J.ge(score, 3) if J.truthy(_t1 := (score is not None)) else _t1)
    G_register_signal(G_for_every(nativeScores, _f12), "3+ Criteria Met")
    def _f13(score=J.undefined, *_args):
        return (J.ge(score, 2) if J.truthy(_t1 := (score is not None)) else _t1)
    G_register_signal(G_for_every(nativeScores, _f13), "2+ Criteria Met")
    def _f14(score=J.undefined, *_args):
        return (J.ge(score, 1) if J.truthy(_t1 := (score is not None)) else _t1)
    G_register_signal(G_for_every(nativeScores, _f14), "1+ Criteria Met")
    G_paint(nativeSMA50, J.obj(("name", "SMA 50"), ("color", "yellow")))
    G_paint(nativeSMA150, J.obj(("name", "SMA 150"), ("color", "orange")))
    G_paint(nativeSMA200, J.obj(("name", "SMA 200"), ("color", "red")))
    currentCriteria = J.get(nativeScores, J.sub(J.get(nativeScores, "length"), 1))
    currentClose = J.get(G_close, J.sub(J.get(G_close, "length"), 1))
    currentSMA50 = J.get(nativeSMA50, J.sub(J.get(nativeSMA50, "length"), 1))
    currentSMA150 = J.get(nativeSMA150, J.sub(J.get(nativeSMA150, "length"), 1))
    currentSMA200 = J.get(nativeSMA200, J.sub(J.get(nativeSMA200, "length"), 1))
    currentHigh52 = J.get(native52WeekHigh, J.sub(J.get(native52WeekHigh, "length"), 1))
    currentLow52 = J.get(native52WeekLow, J.sub(J.get(native52WeekLow, "length"), 1))
    currentRP = J.get(nativeRP, J.sub(J.get(nativeRP, "length"), 1))
    currentSMA200Shifted = J.get(nativeSMA200Shifted, J.sub(J.get(nativeSMA200Shifted, "length"), 1))
    def headCell(text=J.undefined, *_args):
        return J.obj(("text", J.template(text)), ("fontWeight", "bold"), ("color", "var(--text-color)"), ("padding", "1px 5px"))
    def valueCell(text=J.undefined, *_args):
        return J.obj(("text", J.template(text)), ("color", "var(--text-color)"), ("padding", "3px 7px"), ("textAlign", "right"))
    def coloredValueCell(text=J.undefined, isPositive=J.undefined, *_args):
        return J.obj(("text", J.template(text)), ("color", ("#2ecc53" if J.truthy(isPositive) else "#e74c3c")), ("padding", "3px 7px"), ("textAlign", "right"), ("fontWeight", "bold"))
    def leftTitleCell(text=J.undefined, *_args):
        return J.obj(("text", J.template(text)), ("fontWeight", "bold"), ("color", "var(--text-color)"), ("padding", "1px 7px"), ("width", "70%"), ("textAlign", "left"))
    def statusCell(text=J.undefined, isMet=J.undefined, *_args):
        return J.obj(("text", J.template(text)), ("color", ("#2ecc53" if J.truthy(isMet) else "#e74c3c")), ("textAlign", "right"), ("padding", "1px 7px"), ("width", "30%"), ("fontWeight", "bold"))
    SEPARATOR = J.obj(("cells", J.JSArray([J.obj(("text", ""), ("colspan", 2), ("borderBottom", "1px solid var(--border-color)"))])))
    criteriaStatus = J.obj(("rp", (J.gt(currentRP, 70) if J.truthy(_t15 := (currentRP is not None)) else _t15)), ("priceAbove50", (J.gt(currentClose, currentSMA50) if J.truthy(_t16 := ((currentSMA50 is not None) if J.truthy(_t17 := (currentClose is not None)) else _t17)) else _t16)), ("priceAbove150", (J.gt(currentClose, currentSMA150) if J.truthy(_t18 := ((currentSMA150 is not None) if J.truthy(_t19 := (currentClose is not None)) else _t19)) else _t18)), ("priceAbove200", (J.gt(currentClose, currentSMA200) if J.truthy(_t20 := ((currentSMA200 is not None) if J.truthy(_t21 := (currentClose is not None)) else _t21)) else _t20)), ("sma50Above150", (J.gt(currentSMA50, currentSMA150) if J.truthy(_t22 := ((currentSMA150 is not None) if J.truthy(_t23 := (currentSMA50 is not None)) else _t23)) else _t22)), ("sma50Above200", (J.gt(currentSMA50, currentSMA200) if J.truthy(_t24 := ((currentSMA200 is not None) if J.truthy(_t25 := (currentSMA50 is not None)) else _t25)) else _t24)), ("sma150Above200", (J.gt(currentSMA150, currentSMA200) if J.truthy(_t26 := ((currentSMA200 is not None) if J.truthy(_t27 := (currentSMA150 is not None)) else _t27)) else _t26)), ("price30AboveLow", (J.ge(currentClose, J.mul(currentLow52, 1.3)) if J.truthy(_t28 := ((currentLow52 is not None) if J.truthy(_t29 := (currentClose is not None)) else _t29)) else _t28)), ("priceWithin25High", (J.ge(currentClose, J.mul(currentHigh52, 0.75)) if J.truthy(_t30 := ((currentHigh52 is not None) if J.truthy(_t31 := (currentClose is not None)) else _t31)) else _t30)), ("sma200Rising", (J.gt(currentSMA200, currentSMA200Shifted) if J.truthy(_t32 := ((currentSMA200Shifted is not None) if J.truthy(_t33 := (currentSMA200 is not None)) else _t33)) else _t32)))
    totalMet = J.get(J.get(J.get(G_Object, "values")(criteriaStatus), "filter")(G_Boolean), "length")
    maxCriteria = 10
    if J.truthy(showTable):
        def _f34(*_args):
            pct = J.mul(J.sub(J.div(currentClose, currentHigh52), 1), 100)
            isPositive = J.ge(pct, 0)
            return coloredValueCell(J.template(("+" if J.ge(pct, 0) else ""), J.get(pct, "toFixed")(1), "%"), isPositive)
        def _f35(*_args):
            pct = J.mul(J.sub(J.div(currentClose, currentLow52), 1), 100)
            isPositive = J.ge(pct, 0)
            return coloredValueCell(J.template(("+" if J.ge(pct, 0) else ""), J.get(pct, "toFixed")(1), "%"), isPositive)
        G_paint_overlay("Minervini Criteria Table", J.obj(("position", "top_right"), ("order", "above_all")), J.obj(("fontSize", 12), ("border", "1px solid var(--border-color)"), ("background", "var(--background-color)"), ("width", "280px"), ("rows", J.JSArray([J.obj(("cells", J.JSArray([J.obj(("colspan", 2), ("text", J.template("Minervini Trend Template (", J.get(G_current, "resolution"), ") - ", totalMet, "/", maxCriteria, (" (RP N/A)" if (currentRP is None) else ""))), ("color", "var(--text-color)"), ("padding", "3px 7px"), ("textAlign", "center"), ("fontWeight", "bold"))]))), J.obj(("cells", J.JSArray([SEPARATOR]))), J.obj(("cells", J.JSArray([leftTitleCell("RP > 70"), (statusCell(("✓" if J.truthy(J.get(criteriaStatus, "rp")) else "✗"), J.get(criteriaStatus, "rp")) if (currentRP is not None) else valueCell("N/A"))]))), J.obj(("cells", J.JSArray([leftTitleCell("Price > SMA 50"), statusCell(("✓" if J.truthy(J.get(criteriaStatus, "priceAbove50")) else "✗"), J.get(criteriaStatus, "priceAbove50"))]))), J.obj(("cells", J.JSArray([leftTitleCell("Price > SMA 150"), statusCell(("✓" if J.truthy(J.get(criteriaStatus, "priceAbove150")) else "✗"), J.get(criteriaStatus, "priceAbove150"))]))), J.obj(("cells", J.JSArray([leftTitleCell("Price > SMA 200"), statusCell(("✓" if J.truthy(J.get(criteriaStatus, "priceAbove200")) else "✗"), J.get(criteriaStatus, "priceAbove200"))]))), J.obj(("cells", J.JSArray([leftTitleCell("SMA 50 > SMA 150"), statusCell(("✓" if J.truthy(J.get(criteriaStatus, "sma50Above150")) else "✗"), J.get(criteriaStatus, "sma50Above150"))]))), J.obj(("cells", J.JSArray([leftTitleCell("SMA 50 > SMA 200"), statusCell(("✓" if J.truthy(J.get(criteriaStatus, "sma50Above200")) else "✗"), J.get(criteriaStatus, "sma50Above200"))]))), J.obj(("cells", J.JSArray([leftTitleCell("SMA 150 > SMA 200"), statusCell(("✓" if J.truthy(J.get(criteriaStatus, "sma150Above200")) else "✗"), J.get(criteriaStatus, "sma150Above200"))]))), J.obj(("cells", J.JSArray([leftTitleCell("Price 30% > 52W Low"), statusCell(("✓" if J.truthy(J.get(criteriaStatus, "price30AboveLow")) else "✗"), J.get(criteriaStatus, "price30AboveLow"))]))), J.obj(("cells", J.JSArray([leftTitleCell("Price w/in 25% of 52W High"), statusCell(("✓" if J.truthy(J.get(criteriaStatus, "priceWithin25High")) else "✗"), J.get(criteriaStatus, "priceWithin25High"))]))), J.obj(("cells", J.JSArray([leftTitleCell("SMA 200 Rising"), statusCell(("✓" if J.truthy(J.get(criteriaStatus, "sma200Rising")) else "✗"), J.get(criteriaStatus, "sma200Rising"))]))), J.obj(("cells", J.JSArray([SEPARATOR]))), J.obj(("cells", J.JSArray([J.obj(("colspan", 2), ("text", J.template("Current Values:")), ("color", "var(--text-color)"), ("padding", "2px 7px"), ("fontWeight", "bold"))]))), J.obj(("cells", J.JSArray([leftTitleCell("RP"), valueCell((J.get(currentRP, "toFixed")(1) if J.truthy(currentRP) else "N/A"))]))), J.obj(("cells", J.JSArray([leftTitleCell("Price vs 52W High"), (_f34() if (J.truthy(currentClose) and J.truthy(currentHigh52)) else valueCell("N/A"))]))), J.obj(("cells", J.JSArray([leftTitleCell("Price vs 52W Low"), (_f35() if (J.truthy(currentClose) and J.truthy(currentLow52)) else valueCell("N/A"))])))]))))


register_store_indicator(
    script,
    name='minervini_trend_template_TS',
    title='Minervini Trend Template',
    developer='TrendSpider',
    url='https://trendspider.com/trading-tools-store/indicators/68cda6-minervini-trend-template/',
    position='price',
    inputs=[{'id': 'show_criteria_table', 'title': 'Show Criteria Table', 'type': 'boolean', 'default': True}],
    outputs=['cdl', 'meets_all_10_trend_template_criteria', '9__criteria_met', '8__criteria_met', '7__criteria_met', '6__criteria_met', '5__criteria_met', '4__criteria_met', '3__criteria_met', '2__criteria_met', '1__criteria_met', 'sma_50', 'sma_150', 'sma_200'],
    signals=['meets_all_10_trend_template_criteria', '9__criteria_met', '8__criteria_met', '7__criteria_met', '6__criteria_met', '5__criteria_met', '4__criteria_met', '3__criteria_met', '2__criteria_met', '1__criteria_met'],
    requires=['history', 'relative_performance'],
    parity='exact',
)
