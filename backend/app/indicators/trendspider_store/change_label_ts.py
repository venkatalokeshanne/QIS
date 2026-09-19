"""
Change% label -- TrendSpider store indicator by Rock Regan.

Registered as "change_label_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/698351-change/)
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
    G_for_every = G["for_every"]
    G_input = G["input"]
    G_paint = G["paint"]
    G_request = G["request"]
    G_time = G["time"]
    G_time_of = G["time_of"]
    G_describe_indicator("Change% label", "upper")
    if (J.sne(J.get(G_current, "assetType"), "stock") and J.sne(J.get(G_current, "assetType"), "etf")):
        raise J.js_throw("This indicator is only applicable to stocks and ETFs")
    lastCandleTime = G_time_of(J.get(G_time, J.sub(J.get(G_time, "length"), 1)))
    currentHour = J.add(J.get(lastCandleTime, "hours"), J.div(J.get(lastCandleTime, "minutes"), 60))
    isRTH = (J.lt(currentHour, 16) if J.truthy(_t1 := J.ge(currentHour, 9.5)) else _t1)
    isAfterHours = (_t2 if J.truthy(_t2 := J.ge(currentHour, 16)) else J.lt(currentHour, 4))
    fontSize = J.get(G_input, "number")("Label Font Size", 12, J.obj(("min", 8), ("max", 24)))
    def getRefClose(*_args):
        try:
            data = J.get(G_request, "history")(J.get(G_current, "ticker"), "D", J.obj(("ext_session", False)))
            G_assert((not J.truthy(J.get(data, "error"))), J.template("Error fetching data: ", J.get(data, "error")))
            closeIndex = (J.sub(J.get(J.get(data, "close"), "length"), 2) if J.truthy(isRTH) else J.sub(J.get(J.get(data, "close"), "length"), 1))
            return J.get(J.get(data, "close"), closeIndex)
        except Exception as _e1:
            error = J.catch_value(_e1)
            J.get(G_console, "log")("Error fetching closing price:", error)
            return None
    refClose = getRefClose()
    currentPrice = J.get(G_close, J.sub(J.get(G_close, "length"), 1))
    percentChange = None
    if ((refClose is not None) and (currentPrice is not None)):
        percentChange = J.mul(J.div(J.sub(currentPrice, refClose), refClose), 100)
    def _f3(c=J.undefined, __=J.undefined, i=J.undefined, *_args):
        if (J.seq(i, J.sub(J.get(G_close, "length"), 1)) and (percentChange is not None)):
            icon = ("\ud83d\udfe2" if J.ge(percentChange, 0) else "\ud83d\udd34")
            val = J.get(J.get(G_Math, "abs")(percentChange), "toFixed")(2)
            labelText = ("AH Chg" if J.truthy(isAfterHours) else "Chg")
            return J.template(labelText, ": ", icon, val, "%")
        return None
    labels = G_for_every(G_close, _f3)
    G_paint(labels, J.obj(("style", "labels_above"), ("font_weight", "bold"), ("font_size", fontSize), ("color", "#444444"), ("backgroundColor", "white"), ("backgroundOpacity", 0.9), ("verticalOffset", 40), ("borderColor", "black"), ("borderWidth", 1), ("name", "Label")))


register_store_indicator(
    script,
    name='change_label_TS',
    title='Change% label',
    developer='Rock Regan',
    url='https://trendspider.com/trading-tools-store/indicators/698351-change/',
    position='price',
    inputs=[{'id': 'label_font_size', 'title': 'Label Font Size', 'type': 'number', 'default': 12}],
    outputs=['label'],
    signals=[],
    requires=['history'],
    parity='exact',
)
