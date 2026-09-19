"""
Example of a Pure Custom JS strategy -- TrendSpider store indicator by TrendSpider Team.

Registered as "example_of_a_pure_custom_js_strategy_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/683688-example-of-a-pure-custom-js-strategy/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_input = G["input"]
    G_market = G["market"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_series_of = G["series_of"]
    G_sma = G["sma"]
    def shouldEnterAtCandle(candleIndex=J.undefined, *_args):
        return (J.gt(J.get(shortMA, candleIndex), J.get(longMA, candleIndex)) if J.truthy(_t1 := J.lt(J.get(shortMA, J.sub(candleIndex, 1)), J.get(longMA, J.sub(candleIndex, 1)))) else _t1)
    def shouldExitAtCandle(candleIndex=J.undefined, *_args):
        stopLossLevel = J.div(J.mul(J.get(currentPosition, "entryPrice"), J.sub(100, stopLossPercentage)), 100)
        stopLossSignalsExit = J.lt(J.get(G_close, candleIndex), stopLossLevel)
        if J.truthy(stopLossSignalsExit):
            return "SL"
        maCrossSignalsExit = (J.lt(J.get(shortMA, candleIndex), J.get(longMA, candleIndex)) if J.truthy(_t1 := J.gt(J.get(shortMA, J.sub(candleIndex, 1)), J.get(longMA, J.sub(candleIndex, 1)))) else _t1)
        return ("cross" if J.truthy(maCrossSignalsExit) else False)
    G_describe_indicator("Example of a pure custom JS strategy")
    longMA = G_sma(G_close, J.get(G_input, "number")("Long", 40))
    shortMA = G_sma(G_close, J.get(G_input, "number")("Short", 10))
    stopLossPercentage = J.get(G_input, "number")("SL%", 1.5)
    currentPosition = None
    entrySignals = G_series_of(None)
    exitSignals = G_series_of(None)
    entryLabels = G_series_of(None)
    exitLabels = G_series_of(None)
    candleIndex = 0
    while J.lt(candleIndex, J.get(G_close, "length")):
        entryReason = shouldEnterAtCandle(candleIndex)
        if ((not J.truthy(currentPosition)) and J.truthy(entryReason)):
            currentPosition = J.obj(("entryCandleIndex", candleIndex), ("entryPrice", J.get(J.get(G_market, "close"), candleIndex)))
            J.set(entrySignals, candleIndex, True)
            J.set(entryLabels, candleIndex, "Entry")
        if J.truthy(currentPosition):
            exitReason = shouldExitAtCandle(candleIndex)
            if J.truthy(exitReason):
                currentPosition = None
                J.set(exitSignals, candleIndex, True)
                J.set(exitLabels, candleIndex, J.template("Exit ", exitReason))
        candleIndex = J.add(candleIndex, 1)
    G_register_signal(entrySignals, "Entry")
    G_register_signal(exitSignals, "Exit")
    G_paint(exitLabels, J.obj(("color", "#8c29a8"), ("backgroundColor", "#8c29a8"), ("style", "labels_above")))
    G_paint(entryLabels, J.obj(("color", "blue"), ("backgroundColor", "blue"), ("style", "labels_below")))


register_store_indicator(
    script,
    name='example_of_a_pure_custom_js_strategy_TS',
    title='Example of a Pure Custom JS strategy',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/683688-example-of-a-pure-custom-js-strategy/',
    position='price',
    inputs=[{'id': 'long', 'title': 'Long', 'type': 'number', 'default': 40}, {'id': 'short', 'title': 'Short', 'type': 'number', 'default': 10}, {'id': 'sl_', 'title': 'SL%', 'type': 'number', 'default': 1.5}],
    outputs=['entry', 'exit', 'line_3', 'line_4'],
    signals=['entry', 'exit'],
    requires=[],
    parity='exact',
)
