"""
Composite Symbol MACD -- TrendSpider store indicator by TrendSpider Team.

Registered as "composite_symbol_macd_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/composite-symbol-macd/)
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
    G_ema = G["ema"]
    G_input = G["input"]
    G_paint = G["paint"]
    G_request = G["request"]
    G_sma = G["sma"]
    G_sub = G["sub"]
    G_describe_indicator("Composite Symbol MACD", "lower", J.obj(("decimals", 4)))
    comparisonSymbol = J.get(G_input, "symbol")("Comparison Symbol", "XLK")
    compositeHistory = J.get(G_request, "history")(J.template("=", J.get(G_current, "ticker"), "/", comparisonSymbol), J.get(G_current, "resolution"), J.obj(("land_onto_current_candles", True)))
    compositeClose = J.get(compositeHistory, "close")
    shortLength = J.get(G_input, "number")("Short Length", 12)
    longLength = J.get(G_input, "number")("Long Length", 26)
    signalLength = J.get(G_input, "number")("Signal Length", 9)
    short = G_ema(compositeClose, shortLength)
    long = G_ema(compositeClose, longLength)
    macd = G_sub(short, long)
    signal = G_sma(macd, signalLength)
    histogram = G_sub(macd, signal)
    def _f1(value=J.undefined, *_args):
        return ("green" if J.gt(value, 0) else "red")
    G_paint(histogram, J.obj(("title", "MACD Histogram"), ("style", "histogram"), ("color", J.get(histogram, "map")(_f1))))
    G_paint(macd, J.obj(("name", "MACD"), ("color", "blue"), ("thickness", 2)))
    G_paint(signal, J.obj(("name", "Signal"), ("color", "purple"), ("thickness", 2)))


register_store_indicator(
    script,
    name='composite_symbol_macd_TS',
    title='Composite Symbol MACD',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/composite-symbol-macd/',
    position='lower',
    inputs=[{'id': 'sym-comparison_symbol', 'title': 'Comparison Symbol', 'type': 'symbol-search', 'default': 'XLK'}, {'id': 'short_length', 'title': 'Short Length', 'type': 'number', 'default': 12}, {'id': 'long_length', 'title': 'Long Length', 'type': 'number', 'default': 26}, {'id': 'signal_length', 'title': 'Signal Length', 'type': 'number', 'default': 9}],
    outputs=['line_1', 'macd', 'signal'],
    signals=[],
    requires=['history'],
    parity='exact',
)
