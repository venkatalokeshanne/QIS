"""
After Hours Chng % -- TrendSpider store indicator by Rock Regan.

Registered as "after_hours_chng_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/69717a-after-hours-chng/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_assert = G["assert"]
    G_close = G["close"]
    G_console = G["console"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_input = G["input"]
    G_interpolate_sparse_series = G["interpolate_sparse_series"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_paint_overlay = G["paint_overlay"]
    G_parseInt = G["parseInt"]
    G_register_signal = G["register_signal"]
    G_request = G["request"]
    G_time = G["time"]
    G_time_of = G["time_of"]
    def scaleVal(n=J.undefined, *_args):
        return J.get(G_Math, "max")(1, J.get(G_Math, "round")(J.div(J.mul(n, uiScale), 100)))
    def px(n=J.undefined, *_args):
        return J.add(scaleVal(n), "px")
    def pickTheme(_name=J.undefined, *_args):
        if J.seq(_name, "Steel + Cyan"):
            return J.obj(("panelBg", "rgba(29, 41, 61, 0.90)"), ("border", "#22D3EE"), ("headerBg", "#1E2A44"), ("headerText", "#F1F5F9"), ("rowBg", "rgba(29, 41, 61, 0.88)"), ("labelText", "#67E8F9"), ("valueText", "#E2E8F0"), ("timeText", "#FFCC33"), ("posBg", "rgba(34, 197, 94, 0.88)"), ("negBg", "rgba(239, 68, 68, 0.88)"), ("neutralBg", "rgba(148, 163, 184, 0.75)"), ("rthDimText", "#94A3B8"), ("rthDimBg", "rgba(15, 23, 42, 0.90)"))
        if J.seq(_name, "Monochrome + Accent"):
            return J.obj(("panelBg", "rgba(0, 0, 0, 0.92)"), ("border", "rgba(255, 176, 0, 0.85)"), ("headerBg", "#0A0A0A"), ("headerText", "#FFB000"), ("rowBg", "rgba(10, 10, 10, 0.92)"), ("labelText", "#FFB000"), ("valueText", "#E5E5E5"), ("timeText", "#FFB000"), ("posBg", "rgba(80, 80, 80, 0.9)"), ("negBg", "rgba(40, 40, 40, 0.95)"), ("neutralBg", "rgba(60, 60, 60, 0.85)"), ("rthDimText", "#737373"), ("rthDimBg", "rgba(0, 0, 0, 0.9)"))
        if J.seq(_name, "Turquoise Classic"):
            return J.obj(("panelBg", "rgba(61,61,61,0.85)"), ("border", "MediumTurquoise"), ("headerBg", "MediumTurquoise"), ("headerText", "#6200ff"), ("rowBg", "rgba(61,61,61,0.85)"), ("labelText", "MediumTurquoise"), ("valueText", "white"), ("timeText", "#FFBA03"), ("posBg", "rgba(0, 128, 0, 0.85)"), ("negBg", "rgba(255, 0, 0, 0.85)"), ("neutralBg", "rgba(128, 128, 128, 0.75)"), ("rthDimText", "gray"), ("rthDimBg", "rgba(61,61,61,0.85)"))
        if J.seq(_name, "Carbon Pro"):
            return J.obj(("panelBg", "rgba(18, 22, 28, 0.95)"), ("border", "#9CA3AF"), ("headerBg", "#1F2A37"), ("headerText", "#E4E7EB"), ("rowBg", "rgba(36, 45, 54, 0.92)"), ("labelText", "#9CA3AF"), ("valueText", "#E6EAEF"), ("timeText", "#D4A017"), ("posBg", "rgba(45, 157, 98, 0.88)"), ("negBg", "rgba(185, 55, 55, 0.88)"), ("neutralBg", "rgba(75, 85, 99, 0.80)"), ("rthDimText", "#6B7280"), ("rthDimBg", "rgba(18, 22, 28, 0.95)"))
        if J.seq(_name, "Forest Tape"):
            return J.obj(("panelBg", "rgba(10, 25, 18, 0.9)"), ("border", "#34D399"), ("headerBg", "#064E3B"), ("headerText", "#A7F3D0"), ("rowBg", "rgba(10, 25, 18, 0.9)"), ("labelText", "#34D399"), ("valueText", "#D1FAE5"), ("timeText", "#FBBF24"), ("posBg", "rgba(16, 185, 129, 0.85)"), ("negBg", "rgba(220, 38, 38, 0.85)"), ("neutralBg", "rgba(75, 85, 99, 0.8)"), ("rthDimText", "#6B7280"), ("rthDimBg", "rgba(10, 25, 18, 0.9)"))
        if J.seq(_name, "Ocean Abyss"):
            return J.obj(("panelBg", "rgba(8, 19, 35, 0.92)"), ("border", "#06B6D4"), ("headerBg", "#0C2A4A"), ("headerText", "#BAE6FD"), ("rowBg", "rgba(8, 19, 35, 0.90)"), ("labelText", "#67E8F9"), ("valueText", "#E0F2FE"), ("timeText", "#FACC15"), ("posBg", "rgba(34, 211, 151, 0.88)"), ("negBg", "rgba(248, 113, 113, 0.88)"), ("neutralBg", "rgba(103, 114, 142, 0.75)"), ("rthDimText", "#64748B"), ("rthDimBg", "rgba(8, 19, 35, 0.92)"))
        if J.seq(_name, "Void Purple"):
            return J.obj(("panelBg", "rgba(13, 9, 26, 0.93)"), ("border", "#C026D3"), ("headerBg", "#2E1065"), ("headerText", "#F3E8FF"), ("rowBg", "rgba(13, 9, 26, 0.90)"), ("labelText", "#D946EF"), ("valueText", "#F5E8FF"), ("timeText", "#FACC15"), ("posBg", "rgba(74, 222, 128, 0.78)"), ("negBg", "rgba(251, 113, 133, 0.78)"), ("neutralBg", "rgba(126, 105, 163, 0.75)"), ("rthDimText", "#7C6D9C"), ("rthDimBg", "rgba(13, 9, 26, 0.93)"))
        if J.seq(_name, "Amber Terminal"):
            return J.obj(("panelBg", "rgba(28, 18, 8, 0.94)"), ("border", "#F59E0B"), ("headerBg", "#451A03"), ("headerText", "#FEF3C7"), ("rowBg", "rgba(28, 18, 8, 0.92)"), ("labelText", "#FBBF24"), ("valueText", "#FEF9C3"), ("timeText", "#67E8F9"), ("posBg", "rgba(163, 230, 77, 0.88)"), ("negBg", "rgba(248, 113, 113, 0.88)"), ("neutralBg", "rgba(161, 98, 7, 0.75)"), ("rthDimText", "#B45309"), ("rthDimBg", "rgba(28, 18, 8, 0.94)"))
        if J.seq(_name, "Matrix Rain"):
            return J.obj(("panelBg", "rgba(2, 12, 8, 0.93)"), ("border", "#22C55E"), ("headerBg", "#052E16"), ("headerText", "#86EFAC"), ("rowBg", "rgba(2, 12, 8, 0.90)"), ("labelText", "#4ADE80"), ("valueText", "#D1FAE5"), ("timeText", "#E0F2FE"), ("posBg", "rgba(74, 222, 128, 0.90)"), ("negBg", "rgba(185, 28, 28, 0.88)"), ("neutralBg", "rgba(52, 211, 153, 0.65)"), ("rthDimText", "#4F7A5F"), ("rthDimBg", "rgba(2, 12, 8, 0.93)"))
        if J.seq(_name, "Platinum Ice"):
            return J.obj(("panelBg", "rgba(15, 23, 42, 0.92)"), ("border", "#E0F2FE"), ("headerBg", "#1E2937"), ("headerText", "#F0F9FF"), ("rowBg", "rgba(15, 23, 42, 0.90)"), ("labelText", "#BAE6FD"), ("valueText", "#F1F5F9"), ("timeText", "#FDE047"), ("posBg", "rgba(52, 211, 153, 0.88)"), ("negBg", "rgba(248, 113, 113, 0.88)"), ("neutralBg", "rgba(148, 163, 184, 0.80)"), ("rthDimText", "#94A3B8"), ("rthDimBg", "rgba(15, 23, 42, 0.92)"))
        return J.obj(("panelBg", "rgba(10, 12, 18, 0.90)"), ("border", "#6200ff"), ("headerBg", "#100099"), ("headerText", "#FFFFFF"), ("rowBg", "rgba(10, 12, 18, 0.90)"), ("labelText", "#A78BFA"), ("valueText", "#E5E7EB"), ("timeText", "#FBBF24"), ("posBg", "rgba(34, 197, 94, 0.88)"), ("negBg", "rgba(239, 68, 68, 0.88)"), ("neutralBg", "rgba(148, 163, 184, 0.75)"), ("rthDimText", "#64748B"), ("rthDimBg", "rgba(10, 12, 18, 0.90)"))
    G_describe_indicator("After Hours Chng %", J.obj(("shortName", "\ud83c\udf19 AH/PM Chg")))
    if (J.sne(J.get(G_current, "assetType"), "stock") and J.sne(J.get(G_current, "assetType"), "etf")):
        raise J.js_throw("This indicator is only applicable to stocks and ETFs")
    themeName = J.get(G_input, "select")("Theme", "Turquoise Classic", J.JSArray(["Midnight Neon", "Steel + Cyan", "Monochrome + Accent", "Turquoise Classic", "Carbon Pro", "Forest Tape", "Ocean Abyss", "Void Purple", "Amber Terminal", "Matrix Rain", "Platinum Ice"]))
    scaleChoice = G_input("UI Scale", "100%", J.JSArray(["70%", "80%", "100%", "110%", "120%", "150%"]))
    signalThreshold = J.get(G_input, "number")("Signal Threshold %", 5, J.obj(("min", 0.5), ("max", 25)))
    uiScale = G_parseInt(scaleChoice, 10)
    FS = J.obj(("header", px(15)), ("body", px(14)), ("small", px(12)))
    PAD = J.obj(("header", J.add(J.add(px(8), " "), px(10))), ("cell", J.add(J.add(px(5), " "), px(10))), ("big", J.add(J.add(px(8), " "), px(15))))
    TH = pickTheme(themeName)
    lastCandleTime = G_time_of(J.get(G_time, J.sub(J.get(G_time, "length"), 1)))
    currentHour = J.add(J.get(lastCandleTime, "hours"), J.div(J.get(lastCandleTime, "minutes"), 60))
    isRTH = (J.lt(currentHour, 16) if J.truthy(_t1 := J.ge(currentHour, 9.5)) else _t1)
    isAfterHours = (_t2 if J.truthy(_t2 := J.ge(currentHour, 16)) else J.lt(currentHour, 4))
    isPremarket = (J.lt(currentHour, 9.5) if J.truthy(_t3 := J.ge(currentHour, 4)) else _t3)
    def getDailyClosingPrices(*_args):
        try:
            data = J.get(G_request, "history")(J.get(G_current, "ticker"), "D", J.obj(("ext_session", False)))
            G_assert((not J.truthy(J.get(data, "error"))), J.template("Error fetching data: ", J.get(data, "error")))
            return G_interpolate_sparse_series(G_land_points_onto_series(J.get(data, "time"), J.get(data, "close"), G_time, "ge"), "constant")
        except Exception as _e1:
            error = J.catch_value(_e1)
            J.get(G_console, "log")("Error fetching closing price:", error)
            return None
    closingPrices = getDailyClosingPrices()
    closingPrice = (J.get(closingPrices, J.sub(J.get(G_close, "length"), 1)) if J.truthy(closingPrices) else None)
    currentPrice = J.get(G_close, J.sub(J.get(G_close, "length"), 1))
    percentChange = None
    if ((closingPrice is not None) and (currentPrice is not None)):
        percentChange = J.mul(J.div(J.sub(currentPrice, closingPrice), closingPrice), 100)
    def _f4(t=J.undefined, index=J.undefined, *_args):
        barTime = G_time_of(t)
        barHour = J.add(J.get(barTime, "hours"), J.div(J.get(barTime, "minutes"), 60))
        barIsRTH = (J.lt(barHour, 16) if J.truthy(_t1 := J.ge(barHour, 9.5)) else _t1)
        if ((J.truthy(barIsRTH) or (not J.truthy(closingPrices))) or (J.get(closingPrices, index) is None)):
            return False
        barPercentChange = J.mul(J.div(J.sub(J.get(G_close, index), J.get(closingPrices, index)), J.get(closingPrices, index)), 100)
        return J.ge(J.get(G_Math, "abs")(barPercentChange), signalThreshold)
    signalArray = J.get(G_time, "map")(_f4)
    G_register_signal(signalArray, "AH Change > Threshold")
    overlayOpts = J.obj(("position", "center_right"), ("offset_x", (-50)), ("offset_y", 0), ("order", "above_all"))
    if J.truthy(isRTH):
        G_paint_overlay("AH Change Table", overlayOpts, J.obj(("border", J.template(scaleVal(2), "px solid ", J.get(TH, "rthDimText"))), ("background", J.get(TH, "rthDimBg")), ("rows", J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", "AH/PM Change"), ("fontWeight", "bold"), ("color", J.get(TH, "rthDimText")), ("background", J.get(TH, "rthDimBg")), ("padding", J.get(PAD, "header")), ("fontSize", J.get(FS, "header")), ("textAlign", "center"))]))), J.obj(("cells", J.JSArray([J.obj(("text", "Off During RTH"), ("color", J.get(TH, "rthDimText")), ("background", J.get(TH, "rthDimBg")), ("padding", J.get(PAD, "big")), ("fontStyle", "italic"), ("fontSize", J.get(FS, "body")), ("textAlign", "center"))])))]))))
        return J.undefined
    sessionLabel = ("PM Change" if J.truthy(isPremarket) else "AH Change")
    pctBg = (J.get(TH, "neutralBg") if (percentChange is None) else (J.get(TH, "posBg") if J.gt(percentChange, 0) else (J.get(TH, "negBg") if J.lt(percentChange, 0) else J.get(TH, "neutralBg"))))
    rows = J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", sessionLabel), ("fontWeight", "bold"), ("color", J.get(TH, "headerText")), ("background", J.get(TH, "headerBg")), ("padding", J.get(PAD, "header")), ("fontSize", J.get(FS, "header")), ("textAlign", "center"), ("colspan", 2))]))), J.obj(("cells", J.JSArray([J.obj(("text", "Session Close"), ("fontWeight", "bold"), ("color", J.get(TH, "labelText")), ("background", J.get(TH, "rowBg")), ("padding", J.get(PAD, "cell")), ("fontSize", J.get(FS, "body"))), J.obj(("text", (J.get(closingPrice, "toFixed")(2) if J.truthy(closingPrice) else "N/A")), ("color", J.get(TH, "labelText")), ("background", J.get(TH, "rowBg")), ("padding", J.get(PAD, "cell")), ("fontSize", J.get(FS, "body")))]))), J.obj(("cells", J.JSArray([J.obj(("text", "Current Candle"), ("color", J.get(TH, "valueText")), ("background", J.get(TH, "rowBg")), ("padding", J.get(PAD, "cell")), ("fontSize", J.get(FS, "body"))), J.obj(("text", (J.get(currentPrice, "toFixed")(2) if J.truthy(currentPrice) else "N/A")), ("color", J.get(TH, "valueText")), ("background", J.get(TH, "rowBg")), ("padding", J.get(PAD, "cell")), ("fontSize", J.get(FS, "body")))]))), J.obj(("cells", J.JSArray([J.obj(("text", "Last Candle Time"), ("color", J.get(TH, "valueText")), ("background", J.get(TH, "rowBg")), ("padding", J.get(PAD, "cell")), ("fontSize", J.get(FS, "small"))), J.obj(("text", J.template(J.get(lastCandleTime, "hours"), ":", J.get(J.get(J.get(lastCandleTime, "minutes"), "toString")(), "padStart")(2, "0"))), ("color", J.get(TH, "timeText")), ("background", J.get(TH, "rowBg")), ("padding", J.get(PAD, "cell")), ("fontSize", J.get(FS, "small")))]))), J.obj(("cells", J.JSArray([J.obj(("text", sessionLabel), ("fontWeight", "bold"), ("color", J.get(TH, "valueText")), ("background", J.get(TH, "rowBg")), ("padding", J.get(PAD, "cell")), ("fontSize", J.get(FS, "body"))), J.obj(("text", (J.add(J.get(percentChange, "toFixed")(2), "%") if (percentChange is not None) else "N/A")), ("color", "white"), ("background", pctBg), ("padding", J.get(PAD, "cell")), ("fontWeight", "bold"), ("fontSize", J.get(FS, "body")))])))])
    G_paint_overlay("AH Change Table", overlayOpts, J.obj(("border", J.template(scaleVal(2), "px solid ", J.get(TH, "border"))), ("background", J.get(TH, "panelBg")), ("rows", rows)))


register_store_indicator(
    script,
    name='after_hours_chng_TS',
    title='After Hours Chng %',
    developer='Rock Regan',
    url='https://trendspider.com/trading-tools-store/indicators/69717a-after-hours-chng/',
    position='price',
    inputs=[{'id': 'theme', 'title': 'Theme', 'type': 'select_wide', 'default': 'Turquoise Classic', 'options': ['Midnight Neon', 'Steel + Cyan', 'Monochrome + Accent', 'Turquoise Classic', 'Carbon Pro', 'Forest Tape', 'Ocean Abyss', 'Void Purple', 'Amber Terminal', 'Matrix Rain', 'Platinum Ice']}, {'id': 'ui_scale', 'title': 'UI Scale', 'type': 'select_wide', 'default': '100%', 'options': ['70%', '80%', '100%', '110%', '120%', '150%']}, {'id': 'signal_threshold__', 'title': 'Signal Threshold %', 'type': 'number', 'default': 5}],
    outputs=['ah_change___threshold'],
    signals=['ah_change___threshold'],
    requires=['history'],
    parity='exact',
)
