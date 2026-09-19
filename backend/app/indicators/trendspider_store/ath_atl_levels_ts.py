"""
ATH/ATL Levels -- TrendSpider store indicator by Boo Fighter.

Registered as "ath_atl_levels_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/69efc4-ath-atl-lines-with-projection/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Date = G["Date"]
    G_assert = G["assert"]
    G_close = G["close"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_horizontal_line = G["horizontal_line"]
    G_library = G["library"]
    G_paint = G["paint"]
    G_paint_label_at_line = G["paint_label_at_line"]
    G_paint_projection = G["paint_projection"]
    G_request = G["request"]
    G_describe_indicator("ATH/ATL Levels")
    moment = G_library("moment-timezone")
    monthlyData = J.get(G_request, "history")(J.get(G_current, "ticker"), "M")
    G_assert((not J.truthy(J.get(monthlyData, "error"))), J.template("Error fetching history: \"", J.get(monthlyData, "error"), "\""))
    athValue = None
    athIndex = None
    atlValue = None
    atlIndex = None
    candleIndex = 0
    while J.lt(candleIndex, J.get(J.get(monthlyData, "high"), "length")):
        if ((athValue is None) or J.gt(J.get(J.get(monthlyData, "high"), candleIndex), athValue)):
            athValue = J.get(J.get(monthlyData, "high"), candleIndex)
            athIndex = candleIndex
        if ((atlValue is None) or J.lt(J.get(J.get(monthlyData, "low"), candleIndex), atlValue)):
            atlValue = J.get(J.get(monthlyData, "low"), candleIndex)
            atlIndex = candleIndex
        candleIndex = J.add(candleIndex, 1)
    def formatTimeDifference(timestampSeconds=J.undefined, *_args):
        now = moment(J.get(G_Date, "now")())
        past = moment(J.mul(timestampSeconds, 1000))
        months = J.get(now, "diff")(past, "months")
        if J.lt(months, 1):
            return "less than a month ago"
        return J.template(months, " months ago")
    athTimestamp = J.get(J.get(monthlyData, "time"), athIndex)
    atlTimestamp = J.get(J.get(monthlyData, "time"), atlIndex)
    athTimeAgo = formatTimeDifference(athTimestamp)
    atlTimeAgo = formatTimeDifference(atlTimestamp)
    athLine = G_paint(G_horizontal_line(athValue), J.obj(("name", "ATH"), ("style", "dotted"), ("color", "green"), ("thickness", 1), ("ignoreWhenScaling", 1)))
    atlLine = G_paint(G_horizontal_line(atlValue), J.obj(("name", "ATL"), ("style", "dotted"), ("color", "red"), ("thickness", 1), ("ignoreWhenScaling", 1)))
    PROJECTION_LENGTH = 50
    athProjectionValues = J.JSArray([])
    atlProjectionValues = J.JSArray([])
    currentCloseProjection = J.JSArray([])
    currentClose = J.get(G_close, J.sub(J.get(G_close, "length"), 1))
    i = 0
    while J.lt(i, PROJECTION_LENGTH):
        J.get(athProjectionValues, "push")(athValue)
        J.get(atlProjectionValues, "push")(atlValue)
        J.get(currentCloseProjection, "push")(currentClose)
        i = J.add(i, 1)
    athProjection = G_paint_projection(athProjectionValues, J.obj(("name", "ATH Projection"), ("style", "dotted"), ("color", "green"), ("thickness", 1), ("ignoreWhenScaling", 1)))
    atlProjection = G_paint_projection(atlProjectionValues, J.obj(("name", "ATL Projection"), ("style", "dotted"), ("color", "red"), ("thickness", 1), ("ignoreWhenScaling", 1)))
    currentCloseProjectionLine = G_paint_projection(currentCloseProjection, J.obj(("name", "Last"), ("style", "dotted"), ("color", "blue"), ("thickness", 1)))
    G_paint_label_at_line(athProjection, J.sub(PROJECTION_LENGTH, 1), J.template("ATH $", J.get(athValue, "toFixed")(2), " (", athTimeAgo, ")"), J.obj(("color", "white"), ("background_color", "green"), ("border_radius", 3)))
    G_paint_label_at_line(atlProjection, J.sub(PROJECTION_LENGTH, 1), J.template("ATL $", J.get(atlValue, "toFixed")(2), " (", atlTimeAgo, ")"), J.obj(("color", "white"), ("background_color", "red"), ("border_radius", 3)))
    percentFromATH = J.get(J.mul(J.div(J.sub(currentClose, athValue), athValue), 100), "toFixed")(1)
    percentFromATL = J.get(J.mul(J.div(J.sub(currentClose, atlValue), atlValue), 100), "toFixed")(1)
    athLabel = (J.template("+", percentFromATH, "%") if J.ge(percentFromATH, 0) else J.template(percentFromATH, "%"))
    atlLabel = (J.template("+", percentFromATL, "%") if J.ge(percentFromATL, 0) else J.template(percentFromATL, "%"))
    G_paint_label_at_line(currentCloseProjectionLine, J.sub(PROJECTION_LENGTH, 1), J.template(athLabel, " ATH, ", atlLabel, " ATL"), J.obj(("color", "white"), ("background_color", "blue"), ("border_radius", 3)))


register_store_indicator(
    script,
    name='ath_atl_levels_TS',
    title='ATH/ATL Levels',
    developer='Boo Fighter',
    url='https://trendspider.com/trading-tools-store/indicators/69efc4-ath-atl-lines-with-projection/',
    position='price',
    inputs=[],
    outputs=['ath', 'atl'],
    signals=[],
    requires=['history'],
    parity='exact',
)
