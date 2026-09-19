"""
Chart Resolution and Candle Label -- TrendSpider store indicator by Rock Regan.

Registered as "chart_resolution_and_candle_label_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/697183-chart-resolution-and-candle-label/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_input = G["input"]
    G_paint_overlay = G["paint_overlay"]
    G_describe_indicator("Chart Resolution and Candle Label")
    backgroundColor = J.get(G_input, "color")("Background Color", "white")
    textColor = J.get(G_input, "color")("Text Color", "black")
    resolutionColor = J.get(G_input, "color")("title", "#6300d3")
    fontSize = J.get(G_input, "number")("Font Size", 24, J.obj(("min", 8), ("max", 24)))
    intervalMap = J.obj(("1", "1 min"), ("5", "5 min"), ("15", "15 min"), ("30", "30 min"), ("60", "1 hour"), ("240", "4 hour"), ("D", "Daily"), ("W", "Weekly"), ("M", "Monthly"), ("1440", "Session"))
    chartTypeMap = J.obj(("line", "Line"), ("bars", "Bars"), ("candles", "Candles"), ("hollowcandles", "Hollow Candles"), ("rainfall", "Rainfall"), ("heikinashi", "Heikin Ashi"))
    intervalLabel = (_t1 if J.truthy(_t1 := J.get(intervalMap, J.get(G_current, "resolution"))) else J.get(G_current, "resolution"))
    chartTypeLabel = (_t2 if J.truthy(_t2 := J.get(chartTypeMap, J.get(G_current, "chart_type"))) else J.get(G_current, "chart_type"))
    G_paint_overlay("IntervalLabel", J.obj(("position", "top_right"), ("offset_x", (-200)), ("offset_y", (-5))), J.obj(("rows", J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", "Resolution: "), ("color", resolutionColor), ("fontSize", J.template(fontSize, "px")), ("font_weight", "bold"), ("background", backgroundColor), ("padding", "4px")), J.obj(("text", intervalLabel), ("color", textColor), ("fontSize", J.template(fontSize, "px")), ("font_weight", "bold"), ("background", backgroundColor), ("padding", "2px")), J.obj(("text", J.template(" | ", chartTypeLabel)), ("color", textColor), ("fontSize", J.template(fontSize, "px")), ("font_weight", "bold"), ("background", backgroundColor), ("padding", "2px"))])))]))))


register_store_indicator(
    script,
    name='chart_resolution_and_candle_label_TS',
    title='Chart Resolution and Candle Label',
    developer='Rock Regan',
    url='https://trendspider.com/trading-tools-store/indicators/697183-chart-resolution-and-candle-label/',
    position='price',
    inputs=[{'id': 'background_color', 'title': 'Background Color', 'type': 'color', 'default': 'white'}, {'id': 'text_color', 'title': 'Text Color', 'type': 'color', 'default': 'black'}, {'id': 'title', 'title': 'title', 'type': 'color', 'default': '#6300d3'}, {'id': 'font_size', 'title': 'Font Size', 'type': 'number', 'default': 24}],
    outputs=[],
    signals=[],
    requires=[],
    parity='exact',
)
