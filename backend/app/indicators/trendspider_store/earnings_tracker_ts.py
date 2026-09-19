"""
Earnings Tracker -- TrendSpider store indicator by TrendSpider.

Registered as "earnings_tracker_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6893cd-earnings-tracker/)
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
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_input = G["input"]
    G_library = G["library"]
    G_paint_overlay = G["paint_overlay"]
    G_parseInt = G["parseInt"]
    G_request = G["request"]
    G_describe_indicator("Earnings Tracker")
    moment = G_library("moment-timezone")
    useRevenue = J.get(G_input, "boolean")("Use Revenue", False)
    chartBackgroundColor = J.get(G_input, "color")("Chart Background Color", "#000000")
    chartBackgroundOpacity = J.get(G_input, "number")("Chart Background Opacity", 0.3, J.obj(("min", 0), ("max", 1), ("step", 0.1)))
    earningsData = J.get(G_request, "earnings")(J.get(G_current, "ticker"), J.obj(("limit", 20)))
    G_assert((not J.truthy(J.get(earningsData, "error"))), J.template("Error fetching earnings data: ", J.get(earningsData, "error")))
    def _f1(a=J.undefined, b=J.undefined, *_args):
        return J.sub(J.get(b, "timestamp"), J.get(a, "timestamp"))
    J.get(earningsData, "sort")(_f1)
    recentEarnings = J.get(earningsData, "slice")(0, 20)
    labels = J.JSArray([])
    actualValues = J.JSArray([])
    estimatedValues = J.JSArray([])
    actualColors = J.JSArray([])
    i = J.sub(J.get(recentEarnings, "length"), 1)
    while J.ge(i, 0):
        earning = J.get(recentEarnings, i)
        currentDate = moment(J.mul(J.get(earning, "timestamp"), 1000))
        J.get(labels, "push")(J.get(currentDate, "format")("YY/MM/DD"))
        actual = ((J.get(earning, "revenue") if (J.get(earning, "revenue") is not J.undefined) else 0) if J.truthy(useRevenue) else (J.get(earning, "eps") if (J.get(earning, "eps") is not J.undefined) else 0))
        estimated = ((J.get(earning, "revenue_est") if (J.get(earning, "revenue_est") is not J.undefined) else 0) if J.truthy(useRevenue) else (J.get(earning, "eps_est") if (J.get(earning, "eps_est") is not J.undefined) else 0))
        J.get(actualValues, "push")(actual)
        J.get(estimatedValues, "push")(estimated)
        if ((actual is not J.undefined) and (estimated is not J.undefined)):
            beatMiss = J.div(J.get(G_Math, "round")(J.mul(J.sub(actual, estimated), 100)), 100)
            J.get(actualColors, "push")(("green" if J.gt(beatMiss, 0) else "red"))
        else:
            J.get(actualColors, "push")("gray")
        i = J.dec(i)
    G_paint_overlay("EPS Chart", J.obj(("position", "bottom_right"), ("offset_x", (-60)), ("offset_y", (-60)), ("order", "above_all")), J.obj(("background", J.template("rgba(", G_parseInt(J.get(chartBackgroundColor, "slice")(1, 3), 16), ", ", G_parseInt(J.get(chartBackgroundColor, "slice")(3, 5), 16), ", ", G_parseInt(J.get(chartBackgroundColor, "slice")(5, 7), 16), ", ", chartBackgroundOpacity, ")")), ("rows", J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", J.template(("Revenue" if J.truthy(useRevenue) else "EPS"), " vs Estimated ", ("Revenue" if J.truthy(useRevenue) else "EPS"), " (Last 20 Quarters)")), ("color", "var(--text-color)"), ("textAlign", "center"), ("colspan", 1))]))), J.obj(("cells", J.JSArray([J.obj(("chart", J.obj(("width", "500px"), ("height", "300px"), ("type", "line"), ("options", J.obj(("devicePixelRatio", 2), ("scales", J.obj(("x", J.obj(("title", J.obj(("display", True), ("text", "Date"))), ("ticks", J.obj(("padding", 5))), ("layout", J.obj(("padding", J.obj(("left", 5), ("right", 5))))))), ("y", J.obj(("position", "left"), ("title", J.obj(("display", True), ("text", J.template(("Revenue" if J.truthy(useRevenue) else "EPS"))))))))), ("plugins", J.obj(("legend", J.obj(("display", True), ("position", "top"), ("align", "center"), ("labels", J.obj(("font", J.obj(("size", 8))))))), ("tooltip", J.obj(("mode", "index"), ("intersect", False))))))), ("data", J.obj(("labels", labels), ("datasets", J.JSArray([J.obj(("label", J.template("Actual ", ("Revenue" if J.truthy(useRevenue) else "EPS"))), ("data", actualValues), ("borderColor", "#808080"), ("borderWidth", 1), ("borderDash", J.JSArray([5, 5])), ("backgroundColor", actualColors), ("pointStyle", "circle"), ("pointRadius", 6), ("pointHoverRadius", 8)), J.obj(("label", J.template("Estimated ", ("Revenue" if J.truthy(useRevenue) else "EPS"))), ("data", estimatedValues), ("borderColor", "white"), ("backgroundColor", "white"), ("pointStyle", "circle"), ("pointRadius", 6), ("pointHoverRadius", 8), ("showLine", False), ("pointBackgroundColor", "transparent"), ("pointBorderColor", "white"), ("pointBorderWidth", 2))])))))))])))]))))


register_store_indicator(
    script,
    name='earnings_tracker_TS',
    title='Earnings Tracker',
    developer='TrendSpider',
    url='https://trendspider.com/trading-tools-store/indicators/6893cd-earnings-tracker/',
    position='price',
    inputs=[{'id': 'use_revenue', 'title': 'Use Revenue', 'type': 'boolean', 'default': False}, {'id': 'chart_background_color', 'title': 'Chart Background Color', 'type': 'color', 'default': '#000000'}, {'id': 'chart_background_opacity', 'title': 'Chart Background Opacity', 'type': 'number', 'default': 0.3}],
    outputs=[],
    signals=[],
    requires=['earnings'],
    parity='exact',
)
