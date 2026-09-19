"""
ATR Multiple From MA -- TrendSpider store indicator by TrendSpider Team.

Registered as "atr_multiple_from_ma_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/atr-multiple-from-ma/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_add = G["add"]
    G_atr = G["atr"]
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_div = G["div"]
    G_high = G["high"]
    G_indicators = G["indicators"]
    G_input = G["input"]
    G_low = G["low"]
    G_mult = G["mult"]
    G_paint = G["paint"]
    G_paint_overlay = G["paint_overlay"]
    G_register_signal = G["register_signal"]
    G_series_of = G["series_of"]
    G_sub = G["sub"]
    G_describe_indicator("ATR multiple from MA", "price", J.obj(("warmup", 300)))
    atrLength = J.get(G_input, "number")("ATR Length", 15, J.obj(("min", 0), ("max", 150)))
    maLength = J.get(G_input, "number")("MA Length", 50, J.obj(("min", 0), ("max", 150)))
    maType = G_input("MA Type", "sma", J.JSArray(["sma", "ema", "wildma", "vwma", "wma", "hullma"]))
    threshold = G_input("Threshold", 7, J.obj(("min", 0), ("max", 100)))
    showMA = J.get(G_input, "boolean")("Paint MA", True)
    maValues = J.get(G_indicators, maType)(G_close, maLength)
    atrPercentage = G_mult(G_div(G_atr(atrLength), G_close), 100)
    gainFromMa = G_mult(G_div(G_sub(G_close, maValues), maValues), 100)
    atrMultiple = G_div(gainFromMa, atrPercentage)
    dotsDistance = G_mult(G_atr(15), 1)
    def _f1(value=J.undefined, index=J.undefined, *_args):
        return (J.get(G_high, index) if J.ge(value, threshold) else None)
    sellSignals = G_add(J.get(atrMultiple, "map")(_f1), dotsDistance)
    def _f2(value=J.undefined, index=J.undefined, *_args):
        return (J.get(G_low, index) if J.le(value, J.neg(threshold)) else None)
    buySignals = G_sub(J.get(atrMultiple, "map")(_f2), dotsDistance)
    G_register_signal(sellSignals, "Sell")
    G_register_signal(buySignals, "Buy")
    VALUE_COLUMN_STYLE = J.obj(("fontWeight", "bold"), ("paddingLeft", 10))
    currentGain = J.get(J.get(gainFromMa, J.sub(J.get(gainFromMa, "length"), 1)), "toFixed")(2)
    G_paint_overlay("Table", J.obj(("position", "bottom_left"), ("order", "above_all")), J.obj(("paddingBottom", 15), ("background", "var(--background-color)"), ("rows", J.JSArray([J.obj(("cells", J.JSArray([J.obj(("colspan", 2), ("text", J.template("xATR(", atrLength, ") from ", maType, "(", maLength, ")")), ("padding", 2), ("background", "orange"), ("color", "black")), J.obj()]))), J.obj(("cells", J.JSArray([J.obj(("text", "ATR% Multiple distance"), ("padding", 2)), J.obj(("text", J.get(J.get(atrMultiple, J.sub(J.get(atrMultiple, "length"), 1)), "toFixed")(2)), *J.obj_spread(VALUE_COLUMN_STYLE), ("color", ("green" if J.gt(currentGain, 0) else "red")))]))), J.obj(("cells", J.JSArray([J.obj(("text", J.template("% Gain from ", maType)), ("padding", 2)), J.obj(("text", J.template(currentGain, "%")), *J.obj_spread(VALUE_COLUMN_STYLE), ("color", ("green" if J.gt(currentGain, 0) else "red")))]))), J.obj(("cells", J.JSArray([J.obj(("text", "ATR%"), ("padding", 2)), J.obj(("text", J.template(J.get(J.get(atrPercentage, J.sub(J.get(atrPercentage, "length"), 1)), "toFixed")(2), "%")), *J.obj_spread(VALUE_COLUMN_STYLE))])))]))))
    G_paint(sellSignals, J.obj(("name", "Sell Signals"), ("color", "red"), ("style", "dotted"), ("thickness", 3), ("hideInScriptEditor", True), ("hideInLegend", True)))
    G_paint(buySignals, J.obj(("name", "Buy Signals"), ("color", "green"), ("style", "dotted"), ("thickness", 3), ("hideInScriptEditor", True), ("hideInLegend", True)))
    G_paint((maValues if J.truthy(showMA) else G_series_of(None)), J.obj(("name", "MA"), ("color", "orange")))


register_store_indicator(
    script,
    name='atr_multiple_from_ma_TS',
    title='ATR Multiple From MA',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/atr-multiple-from-ma/',
    position='price',
    inputs=[{'id': 'warmup', 'title': 'Warmup', 'type': 'number', 'default': 300}, {'id': 'atr_length', 'title': 'ATR Length', 'type': 'number', 'default': 15}, {'id': 'ma_length', 'title': 'MA Length', 'type': 'number', 'default': 50}, {'id': 'ma_type', 'title': 'MA Type', 'type': 'select_wide', 'default': 'sma', 'options': ['sma', 'ema', 'wildma', 'vwma', 'wma', 'hullma']}, {'id': 'threshold', 'title': 'Threshold', 'type': 'number', 'default': 7}, {'id': 'paint_ma', 'title': 'Paint MA', 'type': 'boolean', 'default': True}],
    outputs=['sell', 'buy', 'sell_signals', 'buy_signals', 'ma'],
    signals=['sell', 'buy'],
    requires=[],
    parity='exact',
)
