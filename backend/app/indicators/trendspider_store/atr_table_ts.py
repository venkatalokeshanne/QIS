"""
ATR Table -- TrendSpider store indicator by Chirag Patnaik.

Registered as "atr_table_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68a719-atr-table/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_atr = G["atr"]
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_high = G["high"]
    G_input = G["input"]
    G_library = G["library"]
    G_low = G["low"]
    G_paint_overlay = G["paint_overlay"]
    G_sma = G["sma"]
    G_describe_indicator("ATR Table")
    atrLength = J.get(G_input, "number")("ATR Length", 14, J.obj(("min", 1)))
    tablePosition = J.get(G_input, "select")("Table Position", "Bottom Left", J.JSArray(["Top Left", "Top Right", "Bottom Left", "Bottom Right"]))
    myAtr = G_atr(G_high, G_low, G_close, atrLength)
    myAtrAverage = G_sma(myAtr, 5)
    positionMap = J.obj(("Top Left", "top_left"), ("Top Right", "top_right"), ("Bottom Left", "bottom_left"), ("Bottom Right", "bottom_right"))
    def formatNumber(num=J.undefined, *_args):
        return J.get(num, "toFixed")(2)
    def formatPercent(num=J.undefined, *_args):
        return J.add(J.get(num, "toFixed")(2), "%")
    tinycolor = G_library("tinycolor2")
    def getColor(color=J.undefined, alpha=J.undefined, *_args):
        return J.get(J.get(tinycolor(color), "setAlpha")(alpha), "toRgbString")()
    G_paint_overlay("ATR Table", J.obj(("position", J.get(positionMap, tablePosition))), J.obj(("rows", J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", "ATR Period"), ("color", "white"), ("background", getColor("blue", 0.1))), J.obj(("text", J.get(atrLength, "toString")()), ("color", "white"), ("background", getColor("blue", 0.1)))]))), J.obj(("cells", J.JSArray([J.obj(("text", "Current ATR (Points)"), ("color", "white"), ("background", getColor("green", 0.1))), J.obj(("text", formatNumber(J.get(myAtr, J.sub(J.get(myAtr, "length"), 1)))), ("color", "white"), ("background", getColor("green", 0.1)))]))), J.obj(("cells", J.JSArray([J.obj(("text", "Current ATR (%)"), ("color", "white"), ("background", getColor("green", 0.1))), J.obj(("text", formatPercent(J.mul(J.div(J.get(myAtr, J.sub(J.get(myAtr, "length"), 1)), J.get(G_close, J.sub(J.get(G_close, "length"), 1))), 100))), ("color", "white"), ("background", getColor("green", 0.1)))]))), J.obj(("cells", J.JSArray([J.obj(("text", "ATR 1 Bar Ago (Points)"), ("color", "white"), ("background", getColor("orange", 0.1))), J.obj(("text", formatNumber(J.get(myAtr, J.sub(J.get(myAtr, "length"), 2)))), ("color", "white"), ("background", getColor("orange", 0.1)))]))), J.obj(("cells", J.JSArray([J.obj(("text", "ATR 1 Bar Ago (%)"), ("color", "white"), ("background", getColor("orange", 0.1))), J.obj(("text", formatPercent(J.mul(J.div(J.get(myAtr, J.sub(J.get(myAtr, "length"), 2)), J.get(G_close, J.sub(J.get(G_close, "length"), 2))), 100))), ("color", "white"), ("background", getColor("orange", 0.1)))]))), J.obj(("cells", J.JSArray([J.obj(("text", "ATR Avg (5 Bars) (Points)"), ("color", "white"), ("background", getColor("purple", 0.1))), J.obj(("text", formatNumber(J.get(myAtrAverage, J.sub(J.get(myAtrAverage, "length"), 1)))), ("color", "white"), ("background", getColor("purple", 0.1)))]))), J.obj(("cells", J.JSArray([J.obj(("text", "ATR Avg (5 Bars) (%)"), ("color", "white"), ("background", getColor("purple", 0.1))), J.obj(("text", formatPercent(J.mul(J.div(J.get(myAtrAverage, J.sub(J.get(myAtrAverage, "length"), 1)), J.get(G_close, J.sub(J.get(G_close, "length"), 1))), 100))), ("color", "white"), ("background", getColor("purple", 0.1)))])))]))))


register_store_indicator(
    script,
    name='atr_table_TS',
    title='ATR Table',
    developer='Chirag Patnaik',
    url='https://trendspider.com/trading-tools-store/indicators/68a719-atr-table/',
    position='price',
    inputs=[{'id': 'atr_length', 'title': 'ATR Length', 'type': 'number', 'default': 14}, {'id': 'table_position', 'title': 'Table Position', 'type': 'select_wide', 'default': 'Bottom Left', 'options': ['Top Left', 'Top Right', 'Bottom Left', 'Bottom Right']}],
    outputs=[],
    signals=[],
    requires=[],
    parity='exact',
)
