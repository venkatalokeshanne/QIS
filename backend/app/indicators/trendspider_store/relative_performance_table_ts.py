"""
Relative Performance Table -- TrendSpider store indicator by TrendSpider Team.

Registered as "relative_performance_table_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/relative-performance-table/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_assert = G["assert"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_library = G["library"]
    G_paint_overlay = G["paint_overlay"]
    G_request = G["request"]
    G_describe_indicator("Relative Performance Table")
    moment = G_library("moment-timezone")
    tinycolor = G_library("tinycolor2")
    universes = J.JSArray(["spx500", "russell2000", "same_sector", "same_mktcap", "same_sector_mktcap"])
    performanceType = "techrank"
    performanceData = J.obj()
    for universe in J.iter_of(universes):
        data = J.get(G_request, "relative_performance")(J.get(G_current, "ticker"), performanceType, universe)
        G_assert((not J.truthy(J.get(data, "error"))), J.template("Error fetching data for ", universe, ": ", J.get(data, "error")))
        J.set(performanceData, universe, J.get(J.get(data, J.sub(J.get(data, "length"), 1)), 1))
    def getColor(value=J.undefined, *_args):
        if J.gt(value, 70):
            return "#12d962"
        if J.lt(value, 20):
            return "red"
        return "gray"
    def _f1(universe_2=J.undefined, index=J.undefined, *_args):
        return J.JSArray([J.obj(("text", J.template(universe_2, ":")), ("color", "var(--text-color)"), ("background", ("rgba(255,255,255,0.05)" if J.seq(J.mod(index, 2), 0) else "transparent")), ("padding", "10px 10px"), ("border", J.obj(("width", 1), ("color", "white")))), J.obj(("text", J.get(J.get(performanceData, universe_2), "toFixed")(2)), ("color", getColor(J.get(performanceData, universe_2))), ("background", ("rgba(255,255,255,0.05)" if J.seq(J.mod(index, 2), 0) else "transparent")), ("padding", "10px 10px"), ("border", J.obj(("width", 1), ("color", "white"))))])
    cells = J.get(universes, "flatMap")(_f1)
    G_paint_overlay("RelativePerformanceTable", J.obj(("position", "bottom_right"), ("offset_x", (-40)), ("offset_y", (-20)), ("order", "above_all")), J.obj(("rows", J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", J.template("Relative Performance: ")), ("color", "var(--text-color)"), ("padding", "10px 10px"), ("border", J.obj(("width", 1), ("color", "white")))), *J.spread(cells)])))])), ("border", J.obj(("width", 2), ("color", "white"), ("radius", 5))), ("background", "rgba(0,0,0,0.7)"), ("cellSpacing", 2)))


register_store_indicator(
    script,
    name='relative_performance_table_TS',
    title='Relative Performance Table',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/relative-performance-table/',
    position='price',
    inputs=[],
    outputs=[],
    signals=[],
    requires=['relative_performance'],
    parity='exact',
)
