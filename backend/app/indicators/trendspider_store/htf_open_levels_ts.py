"""
HTF Open Levels -- TrendSpider store indicator by TrendSpider Team.

Registered as "htf_open_levels_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/htf-open-levels/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_assert = G["assert"]
    G_close = G["close"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_horizontal_line = G["horizontal_line"]
    G_input = G["input"]
    G_library = G["library"]
    G_paint = G["paint"]
    G_paint_label_at_line = G["paint_label_at_line"]
    G_request = G["request"]
    G_describe_indicator("HTF Open Levels")
    showDaily = J.get(G_input, "boolean")("Show Daily Open", True)
    showWeekly = J.get(G_input, "boolean")("Show Weekly Open", True)
    showMonthly = J.get(G_input, "boolean")("Show Monthly Open", True)
    showYearly = J.get(G_input, "boolean")("Show Yearly Open", True)
    dailyColor = J.get(G_input, "color")("Daily Color", "blue")
    weeklyColor = J.get(G_input, "color")("Weekly Color", "green")
    monthlyColor = J.get(G_input, "color")("Monthly Color", "red")
    yearlyColor = J.get(G_input, "color")("Yearly Color", "purple")
    lineStyle = J.get(G_input, "select")("Line Style", "line", J.JSArray(["line", "dotted", "ladder"]))
    lineWidth = J.get(G_input, "number")("Line Width", 1, J.obj(("min", 1), ("max", 5)))
    showLabels = J.get(G_input, "boolean")("Show Labels", True)
    labelOpacity = J.get(G_input, "number")("Label Opacity", 0.5, J.obj(("min", 0), ("max", 1), ("step", 0.1)))
    def getOpenPrice(resolution=J.undefined, *_args):
        myData = J.get(G_request, "history")(J.get(G_current, "ticker"), resolution)
        G_assert((not J.truthy(J.get(myData, "error"))), J.template("Error fetching ", resolution, " data: ", J.get(myData, "error")))
        return J.get(J.get(myData, "open"), J.sub(J.get(J.get(myData, "open"), "length"), 1))
    dailyOpen = getOpenPrice("D")
    weeklyOpen = getOpenPrice("W")
    monthlyOpen = getOpenPrice("M")
    yearlyOpen = getOpenPrice("Y")
    def createLine(price=J.undefined, color=J.undefined, label=J.undefined, *_args):
        myLine = G_horizontal_line(price)
        paintedLine = G_paint(myLine, J.obj(("color", color), ("width", lineWidth), ("style", lineStyle), ("name", J.template(label, " Open"))))
        if J.truthy(showLabels):
            tinycolor = G_library("tinycolor2")
            backgroundColor = J.get(J.get(tinycolor(color), "setAlpha")(labelOpacity), "toRgbString")()
            G_paint_label_at_line(paintedLine, J.sub(J.get(G_close, "length"), 1), label, J.obj(("color", "white"), ("background_color", backgroundColor), ("border_radius", 4), ("border_width", 1), ("border_color", color)))
    if J.truthy(showDaily):
        createLine(dailyOpen, dailyColor, "D")
    if J.truthy(showWeekly):
        createLine(weeklyOpen, weeklyColor, "W")
    if J.truthy(showMonthly):
        createLine(monthlyOpen, monthlyColor, "M")
    if J.truthy(showYearly):
        createLine(yearlyOpen, yearlyColor, "Y")


register_store_indicator(
    script,
    name='htf_open_levels_TS',
    title='HTF Open Levels',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/htf-open-levels/',
    position='price',
    inputs=[{'id': 'show_daily_open', 'title': 'Show Daily Open', 'type': 'boolean', 'default': True}, {'id': 'show_weekly_open', 'title': 'Show Weekly Open', 'type': 'boolean', 'default': True}, {'id': 'show_monthly_open', 'title': 'Show Monthly Open', 'type': 'boolean', 'default': True}, {'id': 'show_yearly_open', 'title': 'Show Yearly Open', 'type': 'boolean', 'default': True}, {'id': 'daily_color', 'title': 'Daily Color', 'type': 'color', 'default': 'blue'}, {'id': 'weekly_color', 'title': 'Weekly Color', 'type': 'color', 'default': 'green'}, {'id': 'monthly_color', 'title': 'Monthly Color', 'type': 'color', 'default': 'red'}, {'id': 'yearly_color', 'title': 'Yearly Color', 'type': 'color', 'default': 'purple'}, {'id': 'line_style', 'title': 'Line Style', 'type': 'select_wide', 'default': 'line', 'options': ['line', 'dotted', 'ladder']}, {'id': 'line_width', 'title': 'Line Width', 'type': 'number', 'default': 1}, {'id': 'show_labels', 'title': 'Show Labels', 'type': 'boolean', 'default': True}, {'id': 'label_opacity', 'title': 'Label Opacity', 'type': 'number', 'default': 0.5}],
    outputs=['d_open', 'w_open', 'm_open', 'y_open'],
    signals=[],
    requires=['history'],
    parity='exact',
)
