"""
Seasonality Overlay -- TrendSpider store indicator by TrendSpider Team.

Registered as "seasonality_overlay_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/seasonality-overlay/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
aapl_d: both-error, syn_5m: both-error.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Date = G["Date"]
    G_assert = G["assert"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_library = G["library"]
    G_paint_overlay = G["paint_overlay"]
    G_request = G["request"]
    G_describe_indicator("Seasonality Overlay")
    moment = G_library("moment-timezone")
    tinycolor = G_library("tinycolor2")
    jstat = G_library("jstat")
    data = J.get(G_request, "seasonality")(J.get(G_current, "ticker"), "monthly", "change")
    G_assert((not J.truthy(J.get(data, "error"))), J.get(data, "error"))
    COLOR_SUCCESS = "#12d962"
    LEVEL_SUCCESS = 60
    COLOR_FAILURE = "red"
    LEVEL_FAILURE = 40
    COLORS_BY_WINP = J.JSArray([J.obj(("from", LEVEL_SUCCESS), ("color", COLOR_SUCCESS)), J.obj(("from", LEVEL_FAILURE), ("color", "gray")), J.obj(("from", 0), ("color", COLOR_FAILURE))])
    def percentageOfWinningPeriods(periodId=J.undefined, *_args):
        def _f1(record=J.undefined, *_args):
            return J.gt(J.get(record, "value"), 0)
        return J.div(J.mul(100, J.get(J.get(J.get(J.get(data, "dataByCategory"), periodId), "filter")(_f1), "length")), J.get(J.get(J.get(data, "dataByCategory"), periodId), "length"))
    winPData = J.get(J.get(data, "categories"), "map")(percentageOfWinningPeriods)
    def _f1(winPercent=J.undefined, *_args):
        def _f1(record=J.undefined, *_args):
            return J.gt(winPercent, J.get(record, "from"))
        return J.get(J.get(COLORS_BY_WINP, "find")(_f1), "color")
    columnColors = J.get(winPData, "map")(_f1)
    currentCategory = J.get(moment(J.get(G_Date, "now")()), "format")("MMM")
    def _f2(color=J.undefined, *_args):
        return J.get(J.get(tinycolor(color), "setAlpha")(0.3), "toRgbString")()
    G_paint_overlay("Table", J.obj(("position", "bottom_right")), J.obj(("rows", J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", J.template("Seasonality (", J.get(moment(J.get(G_Date, "now")()), "diff")(moment(J.mul(J.get(data, "sinceDate"), 1000)), "years"), " years since ", J.get(moment(J.mul(J.get(data, "sinceDate"), 1000)), "format")("MMM YYYY"), ")")), ("color", "var(--text-color)"))]))), J.obj(("cells", J.JSArray([J.obj(("chart", J.obj(("width", "350px"), ("height", "170px"), ("type", "bar"), ("options", J.obj(("devicePixelRatio", 2), ("scales", J.obj(("y", J.obj(("position", "right"), ("alignToPixels", True))))), ("plugins", J.obj(("legend", J.obj(("display", False))), ("annotation", J.obj(("annotations", J.obj(("line1", J.obj(("type", "line"), ("yMin", LEVEL_SUCCESS), ("yMax", LEVEL_SUCCESS), ("borderColor", COLOR_SUCCESS), ("borderWidth", 1), ("borderDash", J.JSArray([3])))), ("line2", J.obj(("type", "line"), ("yMin", LEVEL_FAILURE), ("yMax", LEVEL_FAILURE), ("borderColor", COLOR_FAILURE), ("borderWidth", 1), ("borderDash", J.JSArray([3])))), ("line3", J.obj(("type", "line"), ("yMin", 0), ("yMax", 100), ("xMin", currentCategory), ("xMax", currentCategory), ("borderColor", "blue"), ("borderWidth", 1), ("borderDash", J.JSArray([3])))))))))))), ("data", J.obj(("labels", J.get(data, "categories")), ("datasets", J.JSArray([J.obj(("label", "Winning periods"), ("data", winPData), ("backgroundColor", J.get(columnColors, "map")(_f2)), ("borderColor", columnColors), ("borderWidth", 1), ("borderRadius", J.obj(("topLeft", 3), ("topRight", 3))))])))))))])))]))))


register_store_indicator(
    script,
    name='seasonality_overlay_TS',
    title='Seasonality Overlay',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/seasonality-overlay/',
    position='price',
    inputs=[],
    outputs=[],
    signals=[],
    requires=['seasonality'],
    parity='aapl_d: both-error, syn_5m: both-error',
)
