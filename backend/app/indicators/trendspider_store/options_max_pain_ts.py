"""
Options Max Pain -- TrendSpider store indicator by TrendSpider.

Registered as "options_max_pain_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/69cbfb-options-max-pain/)
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
    G_String = G["String"]
    G_close = G["close"]
    G_console = G["console"]
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_input = G["input"]
    G_isNaN = G["isNaN"]
    G_library = G["library"]
    G_paint = G["paint"]
    G_paint_label_at_line = G["paint_label_at_line"]
    G_paint_overlay = G["paint_overlay"]
    G_paint_projection = G["paint_projection"]
    G_parseInt = G["parseInt"]
    G_request = G["request"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    def getOffset(dte=J.undefined, *_args):
        if (not J.truthy(isIntraday)):
            return J.get(G_Math, "max")(1, J.get(G_Math, "min")(100, J.add(dte, 1)))
        tradingDays = 0
        i = 1
        while J.le(i, dte):
            dow = J.get(J.get(J.get(lastBarET, "clone")(), "add")(i, "days"), "day")()
            if (J.sne(dow, 0) and J.sne(dow, 6)):
                tradingDays = J.inc(tradingDays)
            i = J.inc(i)
        return J.get(G_Math, "max")(1, J.get(G_Math, "min")(100, J.add(candlesRemainingToday, J.mul(tradingDays, candlesPerFullDay))))
    def computeMaxPain(resultByStrike=J.undefined, *_args):
        def _f1(a=J.undefined, b=J.undefined, *_args):
            return J.sub(a, b)
        strikes = J.get(J.get(J.get(G_Object, "keys")(resultByStrike), "map")(G_Number), "sort")(_f1)
        if J.seq(J.get(strikes, "length"), 0):
            return None
        callOI = J.obj()
        putOI = J.obj()
        totalCallOI = 0
        totalPutOI = 0
        def _f2(K=J.undefined, *_args):
            nonlocal totalCallOI, totalPutOI
            d = J.get(resultByStrike, K)
            J.set(callOI, K, (J.get(J.get(d, "C"), "oi") if ((J.truthy(d) and J.truthy(J.get(d, "C"))) and J.truthy(J.get(J.get(d, "C"), "oi"))) else 0))
            J.set(putOI, K, (J.get(J.get(d, "P"), "oi") if ((J.truthy(d) and J.truthy(J.get(d, "P"))) and J.truthy(J.get(J.get(d, "P"), "oi"))) else 0))
            totalCallOI = J.add(totalCallOI, J.get(callOI, K))
            totalPutOI = J.add(totalPutOI, J.get(putOI, K))
        J.get(strikes, "forEach")(_f2)
        minPain = G_Infinity
        maxPainStrike = J.get(strikes, 0)
        def _f3(S=J.undefined, *_args):
            nonlocal minPain, maxPainStrike
            pain = 0
            def _f1(K=J.undefined, *_args):
                nonlocal pain
                if J.lt(K, S):
                    pain = J.add(pain, J.mul(J.sub(S, K), J.get(callOI, K)))
                if J.gt(K, S):
                    pain = J.add(pain, J.mul(J.sub(K, S), J.get(putOI, K)))
            J.get(strikes, "forEach")(_f1)
            if J.lt(pain, minPain):
                minPain = pain
                maxPainStrike = S
        J.get(strikes, "forEach")(_f3)
        return J.obj(("maxPain", maxPainStrike), ("totalCallOI", totalCallOI), ("totalPutOI", totalPutOI), ("strikeCount", J.get(strikes, "length")))
    G_describe_indicator("Options Max Pain", "overlay")
    numExpirations = J.get(G_input, "number")("Number of Expirations", 4, J.obj(("min", 1), ("max", 8)))
    lineThickness = J.get(G_input, "number")("Line Thickness", 2, J.obj(("min", 1), ("max", 5)))
    showPanel = J.get(G_input, "boolean")("Show Info Panel", True)
    showLineLabel = J.get(G_input, "boolean")("Show Line Label", True)
    BG = "#111111"
    DIVIDER = "1px solid #2a2a2a"
    PALETTE = J.JSArray(["#FF4444", "#FF7722", "#FFAA00", "#FFDD00", "#AACC00", "#44CC77", "#2299CC", "#9966FF"])
    PROJ_NAMES = J.JSArray(["Max Pain Seg 1", "Max Pain Seg 2", "Max Pain Seg 3", "Max Pain Seg 4", "Max Pain Seg 5", "Max Pain Seg 6", "Max Pain Seg 7", "Max Pain Seg 8"])
    moment = G_library("moment-timezone")
    lastBarET = J.get(J.get(moment, "unix")(J.get(G_time, J.sub(J.get(G_time, "length"), 1))), "tz")("America/New_York")
    minuteOfDay = J.add(J.mul(J.get(lastBarET, "hours")(), 60), J.get(lastBarET, "minutes")())
    MARKET_CLOSE = J.mul(16, 60)
    minsPerCandle = G_parseInt(J.get(G_constants, "resolution"), 10)
    isIntraday = (J.gt(minsPerCandle, 0) if J.truthy(_t1 := (not J.truthy(G_isNaN(minsPerCandle)))) else _t1)
    candlesRemainingToday = (J.get(G_Math, "max")(1, J.get(G_Math, "ceil")(J.div(J.sub(MARKET_CLOSE, minuteOfDay), minsPerCandle))) if J.truthy(isIntraday) else 1)
    candlesPerFullDay = (J.get(G_Math, "round")(J.div(390, minsPerCandle)) if J.truthy(isIntraday) else 1)
    currentPrice = J.get(G_close, J.sub(J.get(G_close, "length"), 1))
    results = J.JSArray([])
    errMsg = None
    try:
        schedule = J.get(G_request, "options_schedule")(J.get(G_constants, "ticker"))
        if ((not J.truthy(schedule)) or J.seq(J.get(schedule, "length"), 0)):
            raise J.js_throw(J.template("No options data available for ", J.get(G_constants, "ticker")))
        def _f2(a=J.undefined, b=J.undefined, *_args):
            return J.sub(J.get(J.get(a, "expiration"), "dte"), J.get(J.get(b, "expiration"), "dte"))
        sorted = J.get(J.get(schedule, "slice")(), "sort")(_f2)
        count = J.get(G_Math, "min")(numExpirations, J.get(sorted, "length"), 8)
        targets = J.get(sorted, "slice")(0, count)
        def _f3(t=J.undefined, *_args):
            return J.get(G_request, "options_data_for_expiration")(J.get(G_constants, "ticker"), J.get(J.get(t, "expiration"), "code"), J.JSArray(["oi"]))
        chains = J.get(G_Promise, "all")(J.get(targets, "map")(_f3))
        i = 0
        while J.lt(i, J.get(targets, "length")):
            exp = J.get(J.get(targets, i), "expiration")
            chainData = J.get(chains, i)
            if ((not J.truthy(chainData)) or (not J.truthy(J.get(chainData, "resultByStrike")))):
                i = J.inc(i)
                continue
            computed = computeMaxPain(J.get(chainData, "resultByStrike"))
            if ((not J.truthy(computed)) or (J.get(computed, "maxPain") is None)):
                i = J.inc(i)
                continue
            offset = getOffset(J.get(exp, "dte"))
            J.get(results, "push")(J.obj(("maxPain", J.get(computed, "maxPain")), ("offset", offset), ("exp", exp), ("totalCallOI", J.get(computed, "totalCallOI")), ("totalPutOI", J.get(computed, "totalPutOI")), ("strikeCount", J.get(computed, "strikeCount"))))
            i = J.inc(i)
    except Exception as _e4:
        e = J.catch_value(_e4)
        errMsg = G_String(e)
        J.get(G_console, "log")("[Max Pain]", errMsg)
    nearestMaxPain = (J.get(J.get(results, 0), "maxPain") if J.gt(J.get(results, "length"), 0) else None)
    lineRef = G_paint(G_series_of(nearestMaxPain), J.obj(("name", "Max Pain"), ("color", J.get(PALETTE, 0)), ("style", "line"), ("thickness", lineThickness)))
    i_2 = 0
    while J.lt(i_2, 8):
        hasData = J.lt(i_2, J.get(results, "length"))
        segArr = J.JSArray([])
        if J.truthy(hasData):
            startOff = (0 if J.seq(i_2, 0) else J.get(G_Math, "min")(J.get(J.get(results, J.sub(i_2, 1)), "offset"), 100))
            endOff = J.get(G_Math, "min")(J.get(J.get(results, i_2), "offset"), 100)
            j = 0
            while J.lt(j, startOff):
                J.get(segArr, "push")(None)
                j = J.inc(j)
            j_2 = startOff
            while J.lt(j_2, endOff):
                J.get(segArr, "push")(J.get(J.get(results, i_2), "maxPain"))
                j_2 = J.inc(j_2)
            if J.seq(i_2, J.sub(J.get(results, "length"), 1)):
                while J.lt(J.get(segArr, "length"), 100):
                    J.get(segArr, "push")(J.get(J.get(results, i_2), "maxPain"))
        G_paint_projection((segArr if J.truthy(hasData) else J.JSArray([None])), J.obj(("name", J.get(PROJ_NAMES, i_2)), ("color", J.get(PALETTE, i_2)), ("thickness", lineThickness)))
        i_2 = J.inc(i_2)
    if (J.truthy(showLineLabel) and (nearestMaxPain is not None)):
        labelBar = J.get(G_Math, "max")(0, J.sub(J.get(G_close, "length"), 8))
        G_paint_label_at_line(lineRef, labelBar, J.template("Max Pain  $", J.get(nearestMaxPain, "toFixed")(2)), J.obj(("background_color", "#111111"), ("border_color", J.get(PALETTE, 0)), ("border_width", 1), ("border_radius", 3)))
    def _f5(*_args):
        headerRow = J.obj(("cells", J.JSArray([J.obj(("text", "MAX PAIN"), ("colspan", 3), ("background", BG), ("color", "#ffffff"), ("fontWeight", "800"), ("fontSize", "11px"), ("letterSpacing", "0.1em"), ("padding", "7px 10px 5px"), ("borderBottom", "1px solid #333333"))])))
        if (not J.truthy(showPanel)):
            return J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", ""), ("background", BG), ("padding", "0"))])))])
        if J.truthy(errMsg):
            return J.JSArray([headerRow, J.obj(("cells", J.JSArray([J.obj(("text", errMsg), ("colspan", 3), ("background", BG), ("color", "#FF8A80"), ("fontSize", "10px"), ("padding", "6px 10px"))])))])
        if J.seq(J.get(results, "length"), 0):
            return J.JSArray([headerRow, J.obj(("cells", J.JSArray([J.obj(("text", "No data available"), ("colspan", 3), ("background", BG), ("color", "#888888"), ("fontSize", "10px"), ("padding", "6px 10px"))])))])
        colHeader = J.obj(("cells", J.JSArray([J.obj(("text", "Expiry"), ("background", BG), ("color", "#555555"), ("fontSize", "9px"), ("fontWeight", "700"), ("letterSpacing", "0.06em"), ("padding", "5px 6px 2px 10px")), J.obj(("text", "Strike"), ("background", BG), ("color", "#555555"), ("fontSize", "9px"), ("fontWeight", "700"), ("letterSpacing", "0.06em"), ("padding", "5px 6px 2px 6px"), ("textAlign", "center")), J.obj(("text", "vs Price"), ("background", BG), ("color", "#555555"), ("fontSize", "9px"), ("fontWeight", "700"), ("letterSpacing", "0.06em"), ("padding", "5px 10px 2px 6px"), ("textAlign", "right"))])))
        def _f1(r=J.undefined, i_3=J.undefined, *_args):
            exp_2 = J.get(r, "exp")
            dist = J.mul(J.div(J.sub(J.get(r, "maxPain"), currentPrice), currentPrice), 100)
            distStr = J.template(("+" if J.ge(dist, 0) else ""), J.get(dist, "toFixed")(2), "%")
            distColor = ("#4CAF50" if J.ge(dist, 0) else "#FF5252")
            expLabel = J.template(J.get(exp_2, "month"), " ", J.get(exp_2, "day"), "  ·  ", J.get(exp_2, "dte"), "d")
            return J.obj(("cells", J.JSArray([J.obj(("text", expLabel), ("background", BG), ("color", J.get(PALETTE, i_3)), ("fontSize", "10px"), ("padding", "4px 6px 4px 10px"), ("borderTop", DIVIDER)), J.obj(("text", J.template("$", J.get(J.get(r, "maxPain"), "toFixed")(2))), ("background", BG), ("color", "#f0f0f0"), ("fontSize", "11px"), ("fontWeight", "700"), ("textAlign", "center"), ("padding", "4px 6px"), ("borderTop", DIVIDER)), J.obj(("text", distStr), ("background", BG), ("color", distColor), ("fontSize", "10px"), ("fontWeight", "600"), ("textAlign", "right"), ("padding", "4px 10px 4px 6px"), ("borderTop", DIVIDER))])))
        dataRows = J.get(results, "map")(_f1)
        return J.JSArray([headerRow, colHeader, *J.spread(dataRows)])
    panelRows = _f5()
    G_paint_overlay("Max Pain Panel", J.obj(("position", "top_right"), ("width", 230)), J.obj(("rows", panelRows)))


register_store_indicator(
    script,
    name='options_max_pain_TS',
    title='Options Max Pain',
    developer='TrendSpider',
    url='https://trendspider.com/trading-tools-store/indicators/69cbfb-options-max-pain/',
    position='price',
    inputs=[{'id': 'number_of_expirations', 'title': 'Number of Expirations', 'type': 'number', 'default': 4}, {'id': 'line_thickness', 'title': 'Line Thickness', 'type': 'number', 'default': 2}, {'id': 'show_info_panel', 'title': 'Show Info Panel', 'type': 'boolean', 'default': True}, {'id': 'show_line_label', 'title': 'Show Line Label', 'type': 'boolean', 'default': True}],
    outputs=['max_pain'],
    signals=[],
    requires=['options_data_for_expiration', 'options_schedule'],
    parity='exact',
)
