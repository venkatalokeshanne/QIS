"""
SPY SPX ES Price Converter [Pt] -- TrendSpider store indicator by PtGambler.

Registered as "spy_spx_es_price_converter_pt_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6a062b-spy-spx-es-price-converter-pt/)
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
    G_Number = G["Number"]
    G_Promise = G["Promise"]
    G_String = G["String"]
    G_bar_at = G["bar_at"]
    G_close = G["close"]
    G_console = G["console"]
    G_constants = G["constants"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_horizontal_line = G["horizontal_line"]
    G_input = G["input"]
    G_interpolate_sparse_series = G["interpolate_sparse_series"]
    G_isFinite = G["isFinite"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_paint = G["paint"]
    G_paint_label_at_line = G["paint_label_at_line"]
    G_paint_overlay = G["paint_overlay"]
    G_request = G["request"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    G_time_of = G["time_of"]
    def getLineStyle(style=J.undefined, *_args):
        if J.seq(style, "Solid"):
            return "line"
        if J.seq(style, "Dotted"):
            return "dotted"
        if J.seq(style, "Dashed"):
            return "dotted"
        return None
    def anchoredBase(price=J.undefined, multiplier=J.undefined, base=J.undefined, *_args):
        if ((((not J.truthy(isNum(price))) or (not J.truthy(isNum(multiplier)))) or J.le(multiplier, 0)) or (not J.truthy(isNum(base)))):
            return None
        localBase = J.add(J.mul(J.get(G_Math, "floor")(J.div(price, 10)), 10), base)
        kRaw = J.div(J.sub(price, localBase), multiplier)
        k = J.get(G_Math, "round")(kRaw)
        return J.add(localBase, J.mul(k, multiplier))
    def buildConvertedLevels(sourceLabel=J.undefined, enabled=J.undefined, sourcePrice=J.undefined, basePrice=J.undefined, multiplier=J.undefined, chartPrice=J.undefined, *_args):
        side = J.get(G_Math, "min")(MAX_LEVELS_EACH_SIDE, J.get(G_Math, "max")(0, J.get(G_Math, "round")(levelsEachSide)))
        valid = (isNum(chartPrice) if J.truthy(_t1 := (isNum(multiplier) if J.truthy(_t2 := (isNum(basePrice) if J.truthy(_t3 := (J.sne(sourcePrice, 0) if J.truthy(_t4 := (isNum(sourcePrice) if J.truthy(_t5 := enabled) else _t5)) else _t4)) else _t3)) else _t2)) else _t1)
        levels = J.JSArray([])
        slot = 0
        while J.le(slot, J.mul(MAX_LEVELS_EACH_SIDE, 2)):
            step = levelStep(slot)
            active = (J.le(J.get(G_Math, "abs")(step), side) if J.truthy(_t6 := valid) else _t6)
            source = (J.add(basePrice, J.mul(step, multiplier)) if J.truthy(active) else None)
            value = (J.mul(source, J.div(chartPrice, sourcePrice)) if J.truthy(active) else None)
            J.get(levels, "push")(J.obj(("source", source), ("value", value), ("text", (J.template(sourceLabel, " ", formatPrice(source)) if (J.truthy(active) and J.truthy(isNum(value))) else "-"))))
            slot = J.add(slot, 1)
        return levels
    def drawConvertedLevels(id=J.undefined, sourceLabel=J.undefined, enabled=J.undefined, sourcePrice=J.undefined, basePrice=J.undefined, multiplier=J.undefined, chartPrice=J.undefined, offsetBars=J.undefined, color=J.undefined, styleName=J.undefined, *_args):
        style = getLineStyle(styleName)
        levels = buildConvertedLevels(sourceLabel, enabled, sourcePrice, basePrice, multiplier, chartPrice)
        labelIndex = J.get(G_Math, "max")(0, J.sub(activeIndex, J.get(G_Math, "round")(offsetBars)))
        def _f1(level=J.undefined, slot=J.undefined, *_args):
            visible = (isNum(J.get(level, "value")) if J.truthy(_t1 := enabled) else _t1)
            levelSeries = (G_horizontal_line(J.get(level, "value")) if J.truthy(visible) else G_series_of(None))
            ref = G_paint(levelSeries, J.obj(("name", J.template(id, " Level ", J.add(slot, 1))), ("color", (color if J.truthy(style) else "rgba(0,0,0,0)")), ("style", (_t2 if J.truthy(_t2 := style) else "line")), ("thickness", 1), ("ignoreWhenScaling", True), ("editorHidden", True), ("hideInLegend", True), ("hideInScriptEditor", True)))
            G_paint_label_at_line(ref, labelIndex, J.get(level, "text"), labelOptions(color))
        J.get(levels, "forEach")(_f1)
    def levelStep(slot=J.undefined, *_args):
        if J.seq(slot, 0):
            return 0
        if J.le(slot, MAX_LEVELS_EACH_SIDE):
            return slot
        return J.neg(J.sub(slot, MAX_LEVELS_EACH_SIDE))
    def formatPrice(value=J.undefined, *_args):
        if (not J.truthy(isNum(value))):
            return "n/a"
        decimals = (2 if J.ge(J.get(G_Math, "abs")(value), 100) else 4)
        return J.get(G_Number(J.get(value, "toFixed")(decimals)), "toString")()
    def formatPercent(value=J.undefined, *_args):
        if (not J.truthy(isNum(value))):
            return ""
        return J.template(("+" if J.ge(value, 0) else ""), J.get(value, "toFixed")(2), "%")
    def getSymbolData(symbol=J.undefined, *_args):
        if (not J.truthy(symbol)):
            return None
        if J.truthy(sameTicker(symbol, J.get(G_current, "ticker"))):
            return J.obj(("symbol", symbol), ("price", valueAt(G_close, activeIndex)), ("close", G_close))
        data = requestHistory(symbol, J.get(G_current, "resolution"), J.obj(("ext_session", useExtSession)))
        if (not J.truthy(data)):
            return None
        landed = G_interpolate_sparse_series(G_land_points_onto_series(J.get(data, "time"), J.get(data, "close"), G_time, "ge"), "constant")
        return J.obj(("symbol", symbol), ("price", valueAt(landed, activeIndex)), ("close", landed), ("raw", data))
    def requestHistory(symbol=J.undefined, resolution=J.undefined, _p1=J.undefined, *_args):
        _t2 = _p1
        if _t2 is J.undefined:
            _t2 = J.obj()
        options = _t2
        try:
            data = J.get(G_request, "history")(symbol, resolution, options)
            if (((not J.truthy(data)) or J.truthy(J.get(data, "error"))) or (not J.truthy(J.get(G_Array, "isArray")(J.get(data, "close"))))):
                J.get(G_console, "warn")(J.template("No usable data for ", symbol, ": ", (J.get(data, "error") if (J.truthy(data) and J.truthy(J.get(data, "error"))) else "unknown error")))
                return None
            return data
        except Exception as _e3:
            e = J.catch_value(_e3)
            J.get(G_console, "warn")(J.template("Request failed for ", symbol, ": ", e))
            return None
    def getPrevDailyClose(symbol=J.undefined, *_args):
        data = requestHistory(symbol, "D")
        return (J.get(J.get(data, "close"), J.sub(J.get(J.get(data, "close"), "length"), 2)) if (J.truthy(data) and J.gt(J.get(J.get(data, "close"), "length"), 1)) else None)
    def getPriorRegularClose(symbol=J.undefined, *_args):
        data = requestHistory(symbol, "30", J.obj(("ext_session", True)))
        if J.truthy(data):
            byDate = J.obj()
            order = J.JSArray([])
            i = 0
            while J.lt(i, J.get(J.get(data, "time"), "length")):
                if (J.gt(J.get(J.get(data, "time"), i), J.get(G_time, activeIndex)) or (not J.truthy(isRegularSessionTime(J.get(J.get(data, "time"), i))))):
                    i = J.add(i, 1)
                    continue
                key = nyDateKey(J.get(J.get(data, "time"), i))
                if (not J.has(key, byDate)):
                    J.get(order, "push")(key)
                J.set(byDate, key, J.get(J.get(data, "close"), i))
                i = J.add(i, 1)
            if J.gt(J.get(order, "length"), 1):
                return J.get(byDate, J.get(order, J.sub(J.get(order, "length"), 2)))
        return getPrevDailyClose(symbol)
    def latestRegularChartClose(*_args):
        i = activeIndex
        while J.ge(i, 0):
            if (J.truthy(isRegularSessionTime(J.get(G_time, i))) and J.truthy(isNum(J.get(G_close, i)))):
                return J.get(G_close, i)
            i = J.sub(i, 1)
        return chartClose
    def isRegularSessionTime(ts=J.undefined, *_args):
        p = G_time_of(ts)
        hours = (_t1 if J.truthy(_t1 := (_t2 if J.truthy(_t2 := J.get(p, "hours")) else J.get(p, "hour"))) else 0)
        minutes = (_t3 if J.truthy(_t3 := (_t4 if J.truthy(_t4 := J.get(p, "minutes")) else J.get(p, "minute"))) else 0)
        weekday = (_t5 if J.truthy(_t5 := (_t6 if J.truthy(_t6 := (_t7 if J.truthy(_t7 := J.get(p, "weekday")) else J.get(p, "dayOfWeek"))) else J.get(p, "day_of_week"))) else "")
        isWeekend = (_t8 if J.truthy(_t8 := (_t9 if J.truthy(_t9 := (_t10 if J.truthy(_t10 := (_t11 if J.truthy(_t11 := J.seq(weekday, "Sat")) else J.seq(weekday, "Sun"))) else J.seq(weekday, 0))) else J.seq(weekday, 6))) else J.seq(weekday, 7))
        mins = J.add(J.mul(hours, 60), minutes)
        return (J.lt(mins, 960) if J.truthy(_t12 := (J.ge(mins, 570) if J.truthy(_t13 := (not J.truthy(isWeekend))) else _t13)) else _t12)
    def nyDateKey(ts=J.undefined, *_args):
        dayBar = G_bar_at(ts, "D")
        return (G_String(J.get(dayBar, "session")) if (J.truthy(dayBar) and J.truthy(J.get(dayBar, "session"))) else G_String(ts))
    def tableHeader(*_args):
        cells = J.JSArray([tableCell("Symbol", THEME_ACCENT, True), tableCell("Price", THEME_ACCENT, True), tableCell(("Change" if J.truthy(showChange) else ""), THEME_ACCENT, True)])
        return J.obj(("cells", cells))
    def tableRow(symbol=J.undefined, price=J.undefined, pct=J.undefined, *_args):
        changeColor = (THEME_TEXT if (not J.truthy(isNum(pct))) else (POSITIVE_COLOR if J.ge(pct, 0) else NEGATIVE_COLOR))
        return J.obj(("cells", J.JSArray([tableCell(symbol, THEME_TEXT, False), tableCell(formatPrice(price), THEME_TEXT, True), tableCell((formatPercent(pct) if J.truthy(showChange) else ""), changeColor, True)])))
    def tableCell(text=J.undefined, color=J.undefined, bold=J.undefined, *_args):
        return J.obj(("text", text), ("color", color), ("padding", 4), ("fontWeight", ("bold" if J.truthy(bold) else "normal")), ("background", "transparent"))
    def fontSize(label=J.undefined, *_args):
        return (_t1 if J.truthy(_t1 := J.get(J.obj(("Tiny", "10px"), ("Small", "11px"), ("Normal", "12px"), ("Large", "14px")), label)) else "12px")
    def labelOptions(color=J.undefined, *_args):
        return J.obj(("color", color), ("background_color", "rgba(128,128,128,0)"), ("border_color", color), ("border_width", 1), ("border_radius", 3))
    def pctChange(now=J.undefined, prev=J.undefined, *_args):
        return (J.mul(J.div(J.sub(now, prev), prev), 100) if ((J.truthy(isNum(now)) and J.truthy(isNum(prev))) and J.sne(prev, 0)) else None)
    def valueAt(series=J.undefined, index=J.undefined, *_args):
        if (not J.truthy(J.get(G_Array, "isArray")(series))):
            return None
        i = J.get(G_Math, "min")(index, J.sub(J.get(series, "length"), 1))
        while J.ge(i, 0):
            if J.truthy(isNum(J.get(series, i))):
                return J.get(series, i)
            i = J.sub(i, 1)
        return None
    def labelSymbol(symbol=J.undefined, *_args):
        s = J.get(G_String((_t1 if J.truthy(_t1 := symbol) else "")), "trim")()
        return (J.get(J.get(s, "split")(":"), "pop")() if J.truthy(J.get(s, "includes")(":")) else s)
    def normTicker(symbol=J.undefined, *_args):
        return J.get(J.get(labelSymbol(symbol), "replace")(J.regex("^$", ""), ""), "toUpperCase")()
    def sameTicker(a=J.undefined, b=J.undefined, *_args):
        return J.seq(normTicker(a), normTicker(b))
    def isNum(value=J.undefined, *_args):
        return (G_isFinite(value) if J.truthy(_t1 := J.seq(J.typeof(value), "number")) else _t1)
    G_describe_indicator("SPY SPX ES Price Converter [Pt]", "price", J.obj(("shortName", "SPY/SPX/ES Conv [Pt]")))
    enableSpy = J.get(G_input, "boolean")("SPY on", True)
    spyMult = J.get(G_input, "number")("SPY increment", 1, J.obj(("min", 0.1), ("step", 0.5)))
    spyBase = J.get(G_input, "number")("SPY base", 1, J.obj(("min", 1), ("max", 10), ("step", 1)))
    spyColor = J.get(G_input, "color")("SPY color", "#ff00ff")
    spyOffset = J.get(G_input, "number")("SPY left", 50, J.obj(("min", 0), ("step", 10)))
    spyStyle = J.get(G_input, "select")("SPY style", "Dashed", J.JSArray(["Solid", "Dashed", "Dotted", "None"]))
    enableSpx = J.get(G_input, "boolean")("SPX on", False)
    spxMult = J.get(G_input, "number")("SPX increment", 10, J.obj(("min", 0.1), ("step", 5)))
    spxBase = J.get(G_input, "number")("SPX base", 10, J.obj(("min", 1), ("max", 10), ("step", 1)))
    spxColor = J.get(G_input, "color")("SPX color", "#ffff00")
    spxOffset = J.get(G_input, "number")("SPX left", 100, J.obj(("min", 0), ("step", 10)))
    spxStyle = J.get(G_input, "select")("SPX style", "Dashed", J.JSArray(["Solid", "Dashed", "Dotted", "None"]))
    enableEs = J.get(G_input, "boolean")("ES on", False)
    esMult = J.get(G_input, "number")("ES increment", 10, J.obj(("min", 0.25), ("step", 5)))
    esBase = J.get(G_input, "number")("ES base", 10, J.obj(("min", 1), ("max", 10), ("step", 1)))
    esColor = J.get(G_input, "color")("ES color", "#ff9900")
    esOffset = J.get(G_input, "number")("ES left", 150, J.obj(("min", 0), ("step", 10)))
    esStyle = J.get(G_input, "select")("ES style", "Dashed", J.JSArray(["Solid", "Dashed", "Dotted", "None"]))
    levelsEachSide = J.get(G_input, "number")("# levels +/-", 10, J.obj(("min", 0), ("max", 10), ("step", 1)))
    updateFreq = J.get(G_input, "select")("Update", "Every tick", J.JSArray(["Every tick", "Per Candle Close"]))
    showTable = J.get(G_input, "boolean")("Table", True)
    tableFontSize = J.get(G_input, "select")("Table size", "Normal", J.JSArray(["Auto", "Tiny", "Small", "Normal", "Large"]))
    showChange = J.get(G_input, "boolean")("Show chg", True)
    SPX_SYMBOL = "$SPX"
    ES_SYMBOL = "ES1!"
    THEME_BG = "var(--background-color)"
    THEME_TEXT = "var(--text-color)"
    THEME_ACCENT = "var(--text-accent-color)"
    THEME_BORDER = "var(--border-color)"
    POSITIVE_COLOR = "#15803d"
    NEGATIVE_COLOR = "#b91c1c"
    MAX_LEVELS_EACH_SIDE = 10
    barCount = J.get(G_close, "length")
    activeIndex = J.get(G_Math, "max")(0, (J.sub(barCount, 2) if (J.seq(updateFreq, "Per Candle Close") and J.gt(barCount, 1)) else J.sub(barCount, 1)))
    useExtSession = (_t1 if J.truthy(_t1 := J.seq(J.get(G_current, "is_ext_hours"), True)) else (J.seq(J.get(J.get(G_constants, "session"), "lengthMinutes"), J.get(J.get(G_constants, "ext_session"), "lengthMinutes")) if J.truthy(_t2 := (J.get(G_constants, "ext_session") if J.truthy(_t3 := J.get(G_constants, "session")) else _t3)) else _t2))
    needSpy = (_t4 if J.truthy(_t4 := enableSpy) else showTable)
    needSpx = (_t5 if J.truthy(_t5 := enableSpx) else showTable)
    needEs = (_t6 if J.truthy(_t6 := enableEs) else showTable)
    _t7 = J.iter_of(J.get(G_Promise, "all")(J.JSArray([(getSymbolData("SPY") if J.truthy(needSpy) else None), (getSymbolData(SPX_SYMBOL) if J.truthy(needSpx) else None), (getSymbolData(ES_SYMBOL) if J.truthy(needEs) else None)])))
    spyData = (_t7[0] if 0 < len(_t7) else J.undefined)
    spxData = (_t7[1] if 1 < len(_t7) else J.undefined)
    esData = (_t7[2] if 2 < len(_t7) else J.undefined)
    chartClose = valueAt(G_close, activeIndex)
    regularChartClose = latestRegularChartClose()
    drawConvertedLevels("SPY", "SPY", enableSpy, (J.get(spyData, "price") if J.truthy(_t8 := spyData) else _t8), anchoredBase((J.get(spyData, "price") if J.truthy(_t9 := spyData) else _t9), spyMult, spyBase), spyMult, regularChartClose, spyOffset, spyColor, spyStyle)
    drawConvertedLevels("SPX", "SPX", enableSpx, (J.get(spxData, "price") if J.truthy(_t10 := spxData) else _t10), anchoredBase((J.get(spxData, "price") if J.truthy(_t11 := spxData) else _t11), spxMult, spxBase), spxMult, regularChartClose, spxOffset, spxColor, spxStyle)
    drawConvertedLevels("ES", "ES1!", enableEs, (J.get(esData, "price") if J.truthy(_t12 := esData) else _t12), anchoredBase((J.get(esData, "price") if J.truthy(_t13 := esData) else _t13), esMult, esBase), esMult, chartClose, esOffset, esColor, esStyle)
    esPrevClose = (getPriorRegularClose(ES_SYMBOL) if (J.truthy(showTable) and J.truthy(showChange)) else None)
    esPct = (pctChange((J.get(esData, "price") if J.truthy(_t14 := esData) else _t14), esPrevClose) if J.truthy(showChange) else None)
    tableRows = (J.JSArray([tableHeader(), tableRow("SPY", (J.get(spyData, "price") if J.truthy(_t15 := spyData) else _t15), None), tableRow("SPX", (J.get(spxData, "price") if J.truthy(_t16 := spxData) else _t16), None), tableRow("ES1!", (J.get(esData, "price") if J.truthy(_t17 := esData) else _t17), esPct)]) if J.truthy(showTable) else J.JSArray([]))
    G_paint_overlay("SPY SPX ES Prices", J.obj(("position", "top_right"), ("order", "above_all")), J.obj(("background", THEME_BG), ("border", J.template("solid ", THEME_BORDER, " 1px")), ("color", THEME_TEXT), ("padding", 6), ("fontSize", fontSize(tableFontSize)), ("rows", tableRows)))


register_store_indicator(
    script,
    name='spy_spx_es_price_converter_pt_TS',
    title='SPY SPX ES Price Converter [Pt]',
    developer='PtGambler',
    url='https://trendspider.com/trading-tools-store/indicators/6a062b-spy-spx-es-price-converter-pt/',
    position='price',
    inputs=[{'id': 'spy_on', 'title': 'SPY on', 'type': 'boolean', 'default': True}, {'id': 'spy_increment', 'title': 'SPY increment', 'type': 'number', 'default': 1}, {'id': 'spy_base', 'title': 'SPY base', 'type': 'number', 'default': 1}, {'id': 'spy_color', 'title': 'SPY color', 'type': 'color', 'default': '#ff00ff'}, {'id': 'spy_left', 'title': 'SPY left', 'type': 'number', 'default': 50}, {'id': 'spy_style', 'title': 'SPY style', 'type': 'select_wide', 'default': 'Dashed', 'options': ['Solid', 'Dashed', 'Dotted', 'None']}, {'id': 'spx_on', 'title': 'SPX on', 'type': 'boolean', 'default': False}, {'id': 'spx_increment', 'title': 'SPX increment', 'type': 'number', 'default': 10}, {'id': 'spx_base', 'title': 'SPX base', 'type': 'number', 'default': 10}, {'id': 'spx_color', 'title': 'SPX color', 'type': 'color', 'default': '#ffff00'}, {'id': 'spx_left', 'title': 'SPX left', 'type': 'number', 'default': 100}, {'id': 'spx_style', 'title': 'SPX style', 'type': 'select_wide', 'default': 'Dashed', 'options': ['Solid', 'Dashed', 'Dotted', 'None']}, {'id': 'es_on', 'title': 'ES on', 'type': 'boolean', 'default': False}, {'id': 'es_increment', 'title': 'ES increment', 'type': 'number', 'default': 10}, {'id': 'es_base', 'title': 'ES base', 'type': 'number', 'default': 10}, {'id': 'es_color', 'title': 'ES color', 'type': 'color', 'default': '#ff9900'}, {'id': 'es_left', 'title': 'ES left', 'type': 'number', 'default': 150}, {'id': 'es_style', 'title': 'ES style', 'type': 'select_wide', 'default': 'Dashed', 'options': ['Solid', 'Dashed', 'Dotted', 'None']}, {'id': '__levels____', 'title': '# levels +/-', 'type': 'number', 'default': 10}, {'id': 'update', 'title': 'Update', 'type': 'select_wide', 'default': 'Every tick', 'options': ['Every tick', 'Per Candle Close']}, {'id': 'table', 'title': 'Table', 'type': 'boolean', 'default': True}, {'id': 'table_size', 'title': 'Table size', 'type': 'select_wide', 'default': 'Normal', 'options': ['Auto', 'Tiny', 'Small', 'Normal', 'Large']}, {'id': 'show_chg', 'title': 'Show chg', 'type': 'boolean', 'default': True}],
    outputs=['spy_level_1', 'spy_level_2', 'spy_level_3', 'spy_level_4', 'spy_level_5', 'spy_level_6', 'spy_level_7', 'spy_level_8', 'spy_level_9', 'spy_level_10', 'spy_level_11', 'spy_level_12', 'spy_level_13', 'spy_level_14', 'spy_level_15', 'spy_level_16', 'spy_level_17', 'spy_level_18', 'spy_level_19', 'spy_level_20', 'spy_level_21', 'spx_level_1', 'spx_level_2', 'spx_level_3', 'spx_level_4', 'spx_level_5', 'spx_level_6', 'spx_level_7', 'spx_level_8', 'spx_level_9', 'spx_level_10', 'spx_level_11', 'spx_level_12', 'spx_level_13', 'spx_level_14', 'spx_level_15', 'spx_level_16', 'spx_level_17', 'spx_level_18', 'spx_level_19', 'spx_level_20', 'spx_level_21', 'es_level_1', 'es_level_2', 'es_level_3', 'es_level_4', 'es_level_5', 'es_level_6', 'es_level_7', 'es_level_8', 'es_level_9', 'es_level_10', 'es_level_11', 'es_level_12', 'es_level_13', 'es_level_14', 'es_level_15', 'es_level_16', 'es_level_17', 'es_level_18', 'es_level_19', 'es_level_20', 'es_level_21'],
    signals=[],
    requires=['history'],
    parity='exact',
)
