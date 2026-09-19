"""
RSI MTF Stack -- TrendSpider store indicator by Rock Regan.

Registered as "rsi_mtf_stack_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6a8b13-rsi-mtf-stack/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_Number = G["Number"]
    G_String = G["String"]
    G_close = G["close"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_input = G["input"]
    G_library = G["library"]
    G_paint_overlay = G["paint_overlay"]
    G_parseInt = G["parseInt"]
    G_request = G["request"]
    G_rsi = G["rsi"]
    G_time = G["time"]
    def tfLabel(tf=J.undefined, *_args):
        return (_t1 if J.truthy(_t1 := J.get(TF_LABEL, tf)) else G_String(tf))
    def scaleVal(n=J.undefined, *_args):
        return J.get(G_Math, "max")(1, J.get(G_Math, "round")(J.div(J.mul(n, uiScale), 100)))
    def px(n=J.undefined, *_args):
        return J.add(scaleVal(n), "px")
    def pad(v=J.undefined, h=J.undefined, *_args):
        return J.add(J.add(px(v), " "), px(h))
    def toMs(ts=J.undefined, *_args):
        if ((ts is None) or (ts is J.undefined)):
            return None
        return (J.mul(ts, 1000) if J.lt(ts, 1000000000000) else ts)
    def lastFinite(series=J.undefined, *_args):
        if ((not J.truthy(series)) or (not J.truthy(J.get(series, "length")))):
            return None
        i = J.sub(J.get(series, "length"), 1)
        while J.ge(i, 0):
            if J.truthy(J.get(G_Number, "isFinite")(J.get(series, i))):
                return J.get(series, i)
            i = J.dec(i)
        return None
    def readTimeframe(tf=J.undefined, *_args):
        key = G_String(tf)
        if (J.get(seriesCache, key) is not J.undefined):
            return J.get(seriesCache, key)
        result = J.obj(("value", None), ("source", "err"), ("filled", False))
        if J.seq(key, chartRes):
            result = J.obj(("value", lastFinite(G_rsi(G_close, rsiLength))), ("source", "native"), ("filled", False))
        else:
            try:
                data = J.get(G_request, "history")(J.get(G_current, "ticker"), key)
                if ((J.truthy(data) and J.truthy(J.get(data, "close"))) and J.truthy(J.get(J.get(data, "close"), "length"))):
                    closes = J.get(data, "close")
                    filled = False
                    fetchLastMs = (toMs(J.get(J.get(data, "time"), J.sub(J.get(J.get(data, "time"), "length"), 1))) if (J.truthy(J.get(data, "time")) and J.truthy(J.get(J.get(data, "time"), "length"))) else None)
                    chartLeads = (J.gt(chartLastMs, fetchLastMs) if J.truthy(_t1 := ((fetchLastMs is not None) if J.truthy(_t2 := (chartLastMs is not None)) else _t2)) else _t1)
                    if (J.truthy(chartLeads) and J.truthy(J.get(G_Number, "isFinite")(curClose))):
                        closes = J.get(J.get(data, "close"), "concat")(J.JSArray([curClose]))
                        filled = True
                    result = J.obj(("value", lastFinite(G_rsi(closes, rsiLength))), ("source", "fetch"), ("filled", filled))
            except Exception as _e3:
                e = J.catch_value(_e3)
                result = J.obj(("value", None), ("source", "err"), ("filled", False))
        J.set(seriesCache, key, result)
        return result
    def isOk(v=J.undefined, *_args):
        return J.get(G_Number, "isFinite")(v)
    def resolveTier(v=J.undefined, *_args):
        if (not J.truthy(isOk(v))):
            return "na"
        if (J.truthy(useTiers) and J.ge(v, J.get(LV, "ob"))):
            return "ob"
        if (J.truthy(useTiers) and J.le(v, J.get(LV, "os"))):
            return "os"
        if J.ge(v, J.get(LV, "bull")):
            return "bull"
        if J.le(v, J.get(LV, "bear")):
            return "bear"
        return "neutral"
    def statusDot(tier=J.undefined, *_args):
        if (not J.truthy(showStatus)):
            return ""
        return (_t1 if J.truthy(_t1 := J.get(TIER_DOT, tier)) else "⚫ ")
    def valueBg(tier=J.undefined, *_args):
        return (_t1 if J.truthy(_t1 := J.get(TIER_BG, tier)) else J.get(TH, "flatBg"))
    def hexLuminance(hex=J.undefined, *_args):
        if J.sne(J.typeof(hex), "string"):
            return None
        h = J.get(hex, "trim")()
        if J.sne(J.get(h, "charAt")(0), "#"):
            return None
        h = J.get(h, "slice")(1)
        if J.seq(J.get(h, "length"), 3):
            h = J.add(J.add(J.add(J.add(J.add(J.get(h, "charAt")(0), J.get(h, "charAt")(0)), J.get(h, "charAt")(1)), J.get(h, "charAt")(1)), J.get(h, "charAt")(2)), J.get(h, "charAt")(2))
        if J.sne(J.get(h, "length"), 6):
            return None
        chan = J.JSArray([])
        i = 0
        while J.lt(i, 3):
            n = G_parseInt(J.get(h, "substr")(J.mul(i, 2), 2), 16)
            if (not J.truthy(J.get(G_Number, "isFinite")(n))):
                return None
            x = J.div(n, 255)
            J.get(chan, "push")((J.div(x, 12.92) if J.le(x, 0.03928) else J.get(G_Math, "pow")(J.div(J.add(x, 0.055), 1.055), 2.4)))
            i = J.inc(i)
        return J.add(J.add(J.mul(0.2126, J.get(chan, 0)), J.mul(0.7152, J.get(chan, 1))), J.mul(0.0722, J.get(chan, 2)))
    def pickTextColor(bg=J.undefined, *_args):
        L = hexLuminance(bg)
        if (L is None):
            return J.get(TH, "text")
        vsWhite = J.div(1.05, J.add(L, 0.05))
        vsBlack = J.div(J.add(L, 0.05), 0.05)
        return ("#000000" if J.gt(vsBlack, vsWhite) else "#FFFFFF")
    def valueText(v=J.undefined, *_args):
        return (J.get(v, "toFixed")(2) if J.truthy(isOk(v)) else "N/A")
    def buildRow(tf=J.undefined, res=J.undefined, *_args):
        v = (J.get(res, "value") if J.truthy(res) else None)
        tier = resolveTier(v)
        bg = valueBg(tier)
        fg = pickTextColor(bg)
        return J.obj(("cells", J.JSArray([J.obj(("text", tfLabel(tf)), ("color", J.get(TH, "text")), ("background", J.get(TH, "labelBg")), ("padding", pad(4, 8)), ("fontSize", px(J.get(fs, "row"))), ("fontWeight", "bold"), ("textAlign", "left")), J.obj(("text", J.add(statusDot(tier), valueText(v))), ("color", fg), ("background", bg), ("padding", pad(4, 8)), ("fontSize", px(J.get(fs, "row"))), ("fontWeight", "bold"), ("textAlign", "right"))])))
    def buildFooterText(*_args):
        stamp = J.undefined
        if (chartLastMs is None):
            stamp = ("--/--" if J.truthy(isDailyRes) else "--:-- ET")
        elif J.truthy(isDailyRes):
            stamp = J.get(J.get(moment(chartLastMs), "tz")("America/New_York"), "format")("MM/DD")
        else:
            stamp = J.add(J.get(J.get(moment(chartLastMs), "tz")("America/New_York"), "format")("HH:mm"), " ET")
        nativeTfs = J.JSArray([])
        filledTfs = J.JSArray([])
        pairs = J.JSArray([J.JSArray([tf1, r1]), J.JSArray([tf2, r2]), J.JSArray([tf3, r3])])
        i = 0
        while J.lt(i, J.get(pairs, "length")):
            tf = J.get(J.get(pairs, i), 0)
            res = J.get(J.get(pairs, i), 1)
            if (not J.truthy(res)):
                i = J.inc(i)
                continue
            if (J.seq(J.get(res, "source"), "native") and J.lt(J.get(nativeTfs, "indexOf")(tf), 0)):
                J.get(nativeTfs, "push")(tf)
            if (J.truthy(J.get(res, "filled")) and J.lt(J.get(filledTfs, "indexOf")(tf), 0)):
                J.get(filledTfs, "push")(tf)
            i = J.inc(i)
        isLive = (_t1 if J.truthy(_t1 := J.gt(J.get(filledTfs, "length"), 0)) else J.gt(J.get(nativeTfs, "length"), 0))
        txt = J.add(J.add(stamp, " · "), ("live" if J.truthy(isLive) else "closed"))
        if J.truthy(J.get(nativeTfs, "length")):
            txt = J.add(txt, J.add(" · exact: ", J.get(J.get(nativeTfs, "map")(tfLabel), "join")(",")))
        return txt
    G_describe_indicator("RSI MTF Stack", J.obj(("shortName", "\ud83d\udcca RSI MTF")))
    moment = G_library("moment-timezone")
    TF_LIST = J.JSArray(["1", "2", "3", "5", "10", "15", "30", "60", "120", "240", "D", "W", "M"])
    TF_LABEL = J.obj(("1", "1 min"), ("2", "2 min"), ("3", "3 min"), ("5", "5 min"), ("10", "10 min"), ("15", "15 min"), ("30", "30 min"), ("60", "1 hour"), ("120", "2 hour"), ("240", "4 hour"), ("D", "Daily"), ("W", "Weekly"), ("M", "Monthly"))
    tf1 = J.get(G_input, "select")("Timeframe 1", "15", TF_LIST)
    tf2 = J.get(G_input, "select")("Timeframe 2", "60", TF_LIST)
    tf3 = J.get(G_input, "select")("Timeframe 3", "D", TF_LIST)
    rsiLength = J.get(G_input, "number")("RSI Length", 14, J.obj(("min", 1), ("max", 100)))
    obLevel = J.get(G_input, "number")("Overbought Level", 70, J.obj(("min", 51), ("max", 100)))
    bullLevel = J.get(G_input, "number")("Bullish Above", 55, J.obj(("min", 51), ("max", 99)))
    bearLevel = J.get(G_input, "number")("Bearish Below", 45, J.obj(("min", 1), ("max", 49)))
    osLevel = J.get(G_input, "number")("Oversold Level", 30, J.obj(("min", 0), ("max", 49)))
    useTiers = J.get(G_input, "boolean")("Overbought/Oversold Colors", True)
    levelsOk = (J.lt(bullLevel, obLevel) if J.truthy(_t1 := (J.lt(bearLevel, bullLevel) if J.truthy(_t2 := (J.lt(osLevel, bearLevel) if J.truthy(_t3 := (J.get(G_Number, "isFinite")(obLevel) if J.truthy(_t4 := (J.get(G_Number, "isFinite")(bullLevel) if J.truthy(_t5 := (J.get(G_Number, "isFinite")(bearLevel) if J.truthy(_t6 := J.get(G_Number, "isFinite")(osLevel)) else _t6)) else _t5)) else _t4)) else _t3)) else _t2)) else _t1)
    LV = (J.obj(("os", osLevel), ("bear", bearLevel), ("bull", bullLevel), ("ob", obLevel)) if J.truthy(levelsOk) else J.obj(("os", 30), ("bear", 45), ("bull", 55), ("ob", 70)))
    scaleChoice = J.get(G_input, "select")("UI Scale", "100%", J.JSArray(["65%", "80%", "100%", "120%", "150%"]))
    showTable = J.get(G_input, "boolean")("Show Table", True)
    showStatus = J.get(G_input, "boolean")("Show Status Dot", True)
    showFooter = J.get(G_input, "boolean")("Show Status Footer", True)
    uiScale = G_parseInt(scaleChoice, 10)
    fs = J.obj(("hdr", 13), ("row", 12), ("foot", 10))
    TH = J.obj(("panelBg", "rgba(0, 0, 0, 0.7)"), ("titleBg", "#222222"), ("labelBg", "rgba(42, 53, 59, 0.9)"), ("footBg", "rgba(20, 26, 30, 0.95)"), ("bullBg", "rgba(0, 150, 0, 0.8)"), ("bearBg", "rgba(220, 20, 20, 0.8)"), ("obBg", "#79FF3B"), ("osBg", "#F608FD"), ("neutBg", "#8A6D1F"), ("flatBg", "rgba(128, 128, 128, 0.7)"), ("text", "white"), ("footFg", "#9FB6C9"), ("border", "#444444"))
    chartRes = G_String(J.get(G_current, "resolution"))
    chartLastMs = toMs(J.get(G_time, J.sub(J.get(G_time, "length"), 1)))
    curClose = J.get(G_close, J.sub(J.get(G_close, "length"), 1))
    seriesCache = J.obj()
    r1 = readTimeframe(tf1)
    r2 = readTimeframe(tf2)
    r3 = readTimeframe(tf3)
    TIER_BG = J.obj(("ob", J.get(TH, "obBg")), ("bull", J.get(TH, "bullBg")), ("neutral", J.get(TH, "neutBg")), ("bear", J.get(TH, "bearBg")), ("os", J.get(TH, "osBg")), ("na", J.get(TH, "flatBg")))
    TIER_DOT = J.obj(("ob", "\ud83d\udfe2 "), ("bull", "\ud83d\udfe2 "), ("neutral", "⚪ "), ("bear", "\ud83d\udd34 "), ("os", "\ud83d\udd34 "), ("na", "⚫ "))
    isDailyRes = (_t7 if J.truthy(_t7 := (_t8 if J.truthy(_t8 := J.seq(chartRes, "D")) else J.seq(chartRes, "W"))) else J.seq(chartRes, "M"))
    visibleRows = J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", J.add(J.add("MTF RSI (", rsiLength), ")")), ("colspan", 2), ("color", J.get(TH, "text")), ("background", J.get(TH, "titleBg")), ("padding", pad(6, 10)), ("fontSize", px(J.get(fs, "hdr"))), ("fontWeight", "bold"), ("textAlign", "center"))]))), buildRow(tf1, r1), buildRow(tf2, r2), buildRow(tf3, r3)])
    if J.truthy(showFooter):
        J.get(visibleRows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", buildFooterText()), ("colspan", 2), ("color", J.get(TH, "footFg")), ("background", J.get(TH, "footBg")), ("padding", pad(2, 8)), ("fontSize", px(J.get(fs, "foot"))), ("fontWeight", "normal"), ("textAlign", "center"))]))))
    hiddenRows = J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", ""), ("color", "transparent"), ("background", "transparent"), ("padding", "0px"))])))])
    G_paint_overlay("RSI MTF Stack", J.obj(("order", "above_all"), ("offset_x", 0), ("offset_y", 0)), (J.obj(("fontSize", scaleVal(J.get(fs, "row"))), ("background", J.get(TH, "panelBg")), ("border", J.add(J.add(scaleVal(1), "px solid "), J.get(TH, "border"))), ("borderRadius", px(6)), ("rows", visibleRows)) if J.truthy(showTable) else J.obj(("fontSize", 1), ("background", "transparent"), ("border", "none"), ("rows", hiddenRows))))


register_store_indicator(
    script,
    name='rsi_mtf_stack_TS',
    title='RSI MTF Stack',
    developer='Rock Regan',
    url='https://trendspider.com/trading-tools-store/indicators/6a8b13-rsi-mtf-stack/',
    position='price',
    inputs=[{'id': 'timeframe_1', 'title': 'Timeframe 1', 'type': 'select_wide', 'default': '15', 'options': ['1', '2', '3', '5', '10', '15', '30', '60', '120', '240', 'D', 'W', 'M']}, {'id': 'timeframe_2', 'title': 'Timeframe 2', 'type': 'select_wide', 'default': '60', 'options': ['1', '2', '3', '5', '10', '15', '30', '60', '120', '240', 'D', 'W', 'M']}, {'id': 'timeframe_3', 'title': 'Timeframe 3', 'type': 'select_wide', 'default': 'D', 'options': ['1', '2', '3', '5', '10', '15', '30', '60', '120', '240', 'D', 'W', 'M']}, {'id': 'rsi_length', 'title': 'RSI Length', 'type': 'number', 'default': 14}, {'id': 'overbought_level', 'title': 'Overbought Level', 'type': 'number', 'default': 70}, {'id': 'bullish_above', 'title': 'Bullish Above', 'type': 'number', 'default': 55}, {'id': 'bearish_below', 'title': 'Bearish Below', 'type': 'number', 'default': 45}, {'id': 'oversold_level', 'title': 'Oversold Level', 'type': 'number', 'default': 30}, {'id': 'overbought_oversold_colors', 'title': 'Overbought/Oversold Colors', 'type': 'boolean', 'default': True}, {'id': 'ui_scale', 'title': 'UI Scale', 'type': 'select_wide', 'default': '100%', 'options': ['65%', '80%', '100%', '120%', '150%']}, {'id': 'show_table', 'title': 'Show Table', 'type': 'boolean', 'default': True}, {'id': 'show_status_dot', 'title': 'Show Status Dot', 'type': 'boolean', 'default': True}, {'id': 'show_status_footer', 'title': 'Show Status Footer', 'type': 'boolean', 'default': True}],
    outputs=[],
    signals=[],
    requires=['history'],
    parity='exact',
)
