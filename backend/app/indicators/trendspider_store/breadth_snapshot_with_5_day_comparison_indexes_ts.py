"""
Breadth Snapshot with 5-Day Comparison (Indexes) -- TrendSpider store indicator by TrendSpider.

Registered as "breadth_snapshot_with_5_day_comparison_indexes_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/69e7e7-breadth-snapshot-with-5-day-comparison-indexes/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_Promise = G["Promise"]
    G_describe_indicator = G["describe_indicator"]
    G_input = G["input"]
    G_paint_overlay = G["paint_overlay"]
    G_request = G["request"]
    def extractValues(h=J.undefined, *_args):
        if ((not J.truthy(h)) or J.truthy(J.get(h, "error"))):
            return J.obj(("current", None), ("previous", None))
        if ((not J.truthy(J.get(h, "close"))) or J.seq(J.get(J.get(h, "close"), "length"), 0)):
            return J.obj(("current", None), ("previous", None))
        lastIdx = J.sub(J.get(J.get(h, "close"), "length"), 1)
        prevIdx = J.sub(J.get(J.get(h, "close"), "length"), 6)
        lastVal = J.get(J.get(h, "close"), lastIdx)
        currentPct = (J.mul(lastVal, 100) if J.seq(J.typeof(lastVal), "number") else None)
        previousPct = None
        if J.ge(prevIdx, 0):
            prevVal = J.get(J.get(h, "close"), prevIdx)
            previousPct = (J.mul(prevVal, 100) if J.seq(J.typeof(prevVal), "number") else None)
        return J.obj(("current", currentPct), ("previous", previousPct))
    def colorForPct(v=J.undefined, *_args):
        if (v is None):
            return GRAY
        if J.ge(v, 70):
            return GREEN
        if J.ge(v, 50):
            return LIGHT_GREEN
        if J.ge(v, 30):
            return YELLOW
        return RED
    def fmtPct(v=J.undefined, *_args):
        if (v is None):
            return "—"
        return J.add(J.get(v, "toFixed")(0), "%")
    def dataRow(item=J.undefined, *_args):
        currentPct = J.get(item, "current")
        previousPct = J.get(item, "previous")
        currentCol = colorForPct(currentPct)
        previousCol = colorForPct(previousPct)
        clamped = (0 if (currentPct is None) else J.get(G_Math, "max")(0, J.get(G_Math, "min")(100, currentPct)))
        fillWidth = J.mul(J.div(clamped, 100), BAR_WIDTH)
        barHtml = J.template("<div style=\"width:", BAR_WIDTH, "px;height:8px;background:", BG_TRACK, ";border-radius:4px;overflow:hidden;\"><div style=\"width:", fillWidth, "px;height:8px;background:", currentCol, ";border-radius:4px;\"></div></div>")
        return J.obj(("cells", J.JSArray([J.obj(("text", J.get(item, "label")), ("color", "#d1d5db"), ("fontSize", "11px"), ("width", LABEL_W), ("textAlign", "left"), ("padding", "4px 8px"), ("borderTop", DIVIDER)), J.obj(("text", barHtml), ("width", J.add(BAR_WIDTH, "px")), ("textAlign", "left"), ("padding", "4px 8px"), ("borderTop", DIVIDER)), J.obj(("text", fmtPct(currentPct)), ("color", currentCol), ("fontSize", "12px"), ("fontWeight", "bold"), ("width", VAL_W), ("textAlign", "right"), ("padding", "4px 8px"), ("borderTop", DIVIDER)), J.obj(("text", fmtPct(previousPct)), ("color", previousCol), ("fontSize", "11px"), ("width", VAL_W), ("textAlign", "right"), ("padding", "4px 8px"), ("borderTop", DIVIDER))])))
    def sectionHeader(text=J.undefined, *_args):
        return J.obj(("cells", J.JSArray([J.obj(("text", text), ("color", MUTED), ("fontSize", "10px"), ("fontWeight", "bold"), ("letterSpacing", "1px"), ("colspan", 4), ("textAlign", "left"), ("padding", "10px 8px 4px 8px"))])))
    G_describe_indicator("Breadth Snapshot with 5-Day Comparison (Indexes)", "price")
    metricOptions = J.JSArray(["% Above 20-SMA", "% Above 50-SMA", "% Above 200-SMA", "% 21-Day Highs", "% 63-Day Highs"])
    prefixMap = J.obj(("% Above 20-SMA", "$MA20"), ("% Above 50-SMA", "$MA50"), ("% Above 200-SMA", "$MA200"), ("% 21-Day Highs", "$H21"), ("% 63-Day Highs", "$H63"))
    selectedMetric = J.get(G_input, "select")("Breadth Metric", "% Above 50-SMA", metricOptions)
    prefix = J.get(prefixMap, selectedMetric)
    indexes = J.JSArray([J.obj(("key", "SP500"), ("label", "S&P 500")), J.obj(("key", "N100"), ("label", "Nasdaq 100")), J.obj(("key", "R2000"), ("label", "Russell 2000")), J.obj(("key", "DJ30"), ("label", "Dow 30")), J.obj(("key", "SPM400"), ("label", "S&P MidCap"))])
    historyPromises = J.JSArray([])
    i = 0
    while J.lt(i, J.get(indexes, "length")):
        J.get(historyPromises, "push")(J.get(G_request, "history")(J.add(prefix, J.get(J.get(indexes, i), "key")), "D"))
        i = J.inc(i)
    histories = J.get(G_Promise, "all")(historyPromises)
    indexValues = J.JSArray([])
    i_2 = 0
    while J.lt(i_2, J.get(indexes, "length")):
        vals = extractValues(J.get(histories, i_2))
        J.get(indexValues, "push")(J.obj(("label", J.get(J.get(indexes, i_2), "label")), ("current", J.get(vals, "current")), ("previous", J.get(vals, "previous"))))
        i_2 = J.inc(i_2)
    GREEN = "#22c55e"
    LIGHT_GREEN = "#86efac"
    YELLOW = "#eab308"
    RED = "#ef4444"
    GRAY = "#9ca3af"
    MUTED = "#6b7280"
    BG_TRACK = "rgba(255,255,255,0.08)"
    DIVIDER = "1px solid rgba(255,255,255,0.06)"
    BAR_WIDTH = 110
    LABEL_W = "100px"
    VAL_W = "45px"
    rows = J.JSArray([])
    J.get(rows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", J.add("BREADTH SNAPSHOT — ", J.get(selectedMetric, "toUpperCase")())), ("color", "#f9fafb"), ("fontSize", "12px"), ("fontWeight", "bold"), ("letterSpacing", "1px"), ("colspan", 4), ("textAlign", "left"), ("padding", "4px 8px 8px 8px"))]))))
    J.get(rows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", ""), ("width", LABEL_W), ("padding", "2px 8px"), ("fontSize", "9px")), J.obj(("text", ""), ("width", J.add(BAR_WIDTH, "px")), ("padding", "2px 8px"), ("fontSize", "9px")), J.obj(("text", "LAST CLS"), ("color", MUTED), ("fontSize", "9px"), ("fontWeight", "bold"), ("width", VAL_W), ("textAlign", "right"), ("padding", "2px 8px")), J.obj(("text", "5D AGO"), ("color", MUTED), ("fontSize", "9px"), ("fontWeight", "bold"), ("width", VAL_W), ("textAlign", "right"), ("padding", "2px 8px"))]))))
    J.get(rows, "push")(sectionHeader("INDEXES"))
    i_3 = 0
    while J.lt(i_3, J.get(indexValues, "length")):
        J.get(rows, "push")(dataRow(J.get(indexValues, i_3)))
        i_3 = J.inc(i_3)
    G_paint_overlay("BreadthSnapshot", J.obj(("position", "top_right"), ("offset_x", (-40)), ("offset_y", 40), ("order", "above_all")), J.obj(("background", "rgba(13, 13, 13, 0.94)"), ("padding", "12px"), ("borderRadius", "8px"), ("rows", rows)))


register_store_indicator(
    script,
    name='breadth_snapshot_with_5_day_comparison_indexes_TS',
    title='Breadth Snapshot with 5-Day Comparison (Indexes)',
    developer='TrendSpider',
    url='https://trendspider.com/trading-tools-store/indicators/69e7e7-breadth-snapshot-with-5-day-comparison-indexes/',
    position='price',
    inputs=[{'id': 'breadth_metric', 'title': 'Breadth Metric', 'type': 'select_wide', 'default': '% Above 50-SMA', 'options': ['% Above 20-SMA', '% Above 50-SMA', '% Above 200-SMA', '% 21-Day Highs', '% 63-Day Highs']}],
    outputs=[],
    signals=[],
    requires=['history'],
    parity='exact',
)
