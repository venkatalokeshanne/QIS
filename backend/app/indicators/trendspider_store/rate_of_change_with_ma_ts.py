"""
Rate of Change with MA -- TrendSpider store indicator by TrendSpider Team.

Registered as "rate_of_change_with_ma_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68f930-rate-of-change-with-ma/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_close = G["close"]
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_indicators = G["indicators"]
    G_input = G["input"]
    G_paint = G["paint"]
    G_roc = G["roc"]
    G_series_of = G["series_of"]
    G_describe_indicator("Rate of Change with MA", "lower", J.obj(("shortname", "RoC with MA")))
    rocLength = J.get(G_input, "number")("ROC Length", 14, J.obj(("min", 1)))
    maLength = J.get(G_input, "number")("MA Length", 14, J.obj(("min", 1)))
    def _f1(item=J.undefined, *_args):
        return (not J.truthy(J.get(J.JSArray(["kama", "alma", "twap"]), "includes")(item)))
    priceLengthMAs = J.get(J.get(G_constants, "ma_types"), "filter")(_f1)
    maType = J.get(G_input, "select")("MA Type", "sma", priceLengthMAs)
    myRoc = G_roc(G_close, rocLength)
    computeMA = J.get(G_indicators, maType)
    myRocMA = computeMA(myRoc, maLength)
    G_paint(myRoc, J.obj(("name", "ROC"), ("color", "green")))
    G_paint(myRocMA, J.obj(("name", "ROC MA"), ("color", "red")))
    G_paint(G_series_of(0), J.obj(("name", "Zero Line"), ("color", "gray"), ("style", "dotted")))


register_store_indicator(
    script,
    name='rate_of_change_with_ma_TS',
    title='Rate of Change with MA',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/68f930-rate-of-change-with-ma/',
    position='lower',
    inputs=[{'id': 'roc_length', 'title': 'ROC Length', 'type': 'number', 'default': 14}, {'id': 'ma_length', 'title': 'MA Length', 'type': 'number', 'default': 14}, {'id': 'ma_type', 'title': 'MA Type', 'type': 'select_wide', 'default': 'sma', 'options': ['ema', 'sma', 'wildma', 'vwma', 'wma', 'hullma']}],
    outputs=['roc', 'roc_ma', 'zero_line'],
    signals=[],
    requires=[],
    parity='exact',
)
