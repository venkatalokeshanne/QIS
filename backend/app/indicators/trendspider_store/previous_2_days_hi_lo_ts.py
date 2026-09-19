"""
Previous 2 Days Hi Lo -- TrendSpider store indicator by Ripster G.

Registered as "previous_2_days_hi_lo_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6923cb-previous-2-days-hi-lo/)
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
    G_horizontal_line = G["horizontal_line"]
    G_paint = G["paint"]
    G_request = G["request"]
    G_describe_indicator("Previous 2 Days Hi Lo")
    dailyData = J.get(G_request, "history")(J.get(G_current, "ticker"), "D")
    G_assert((not J.truthy(J.get(dailyData, "error"))), J.template("Error fetching daily data: ", J.get(dailyData, "error")))
    weeklyData = J.get(G_request, "history")(J.get(G_current, "ticker"), "W")
    G_assert((not J.truthy(J.get(weeklyData, "error"))), J.template("Error fetching weekly data: ", J.get(weeklyData, "error")))
    altaAnteontem = (J.get(J.get(dailyData, "high"), J.sub(J.get(J.get(dailyData, "high"), "length"), 3)) if J.ge(J.get(J.get(dailyData, "high"), "length"), 3) else None)
    baixaAnteontem = (J.get(J.get(dailyData, "low"), J.sub(J.get(J.get(dailyData, "low"), "length"), 3)) if J.ge(J.get(J.get(dailyData, "low"), "length"), 3) else None)
    altaOntem = (J.get(J.get(dailyData, "high"), J.sub(J.get(J.get(dailyData, "high"), "length"), 2)) if J.ge(J.get(J.get(dailyData, "high"), "length"), 2) else None)
    baixaOntem = (J.get(J.get(dailyData, "low"), J.sub(J.get(J.get(dailyData, "low"), "length"), 2)) if J.ge(J.get(J.get(dailyData, "low"), "length"), 2) else None)
    baixaSemanaAnterior = (J.get(J.get(weeklyData, "low"), J.sub(J.get(J.get(weeklyData, "low"), "length"), 2)) if J.ge(J.get(J.get(weeklyData, "low"), "length"), 2) else None)
    altaSemanaAnterior = (J.get(J.get(weeklyData, "high"), J.sub(J.get(J.get(weeklyData, "high"), "length"), 2)) if J.ge(J.get(J.get(weeklyData, "high"), "length"), 2) else None)
    G_paint(G_horizontal_line(altaAnteontem), J.obj(("name", "High 2 Days Ago"), ("color", "red"), ("style", "dotted")))
    G_paint(G_horizontal_line(baixaAnteontem), J.obj(("name", "Low 2 Days Ago"), ("color", "red"), ("style", "dotted")))
    G_paint(G_horizontal_line(altaOntem), J.obj(("name", "High Yesterday"), ("color", "yellow"), ("style", "dotted")))
    G_paint(G_horizontal_line(baixaOntem), J.obj(("name", "Low Yesterday"), ("color", "yellow"), ("style", "dotted")))
    G_paint(G_horizontal_line(baixaSemanaAnterior), J.obj(("name", "Low Previous Week"), ("color", "purple"), ("style", "line")))
    G_paint(G_horizontal_line(altaSemanaAnterior), J.obj(("name", "High Previous Week"), ("color", "purple"), ("style", "line")))


register_store_indicator(
    script,
    name='previous_2_days_hi_lo_TS',
    title='Previous 2 Days Hi Lo',
    developer='Ripster G',
    url='https://trendspider.com/trading-tools-store/indicators/6923cb-previous-2-days-hi-lo/',
    position='price',
    inputs=[],
    outputs=['high_2_days_ago', 'low_2_days_ago', 'high_yesterday', 'low_yesterday', 'low_previous_week', 'high_previous_week'],
    signals=[],
    requires=['history'],
    parity='exact',
)
