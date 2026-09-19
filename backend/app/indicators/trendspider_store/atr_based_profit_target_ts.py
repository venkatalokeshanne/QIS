"""
ATR-based Profit Target -- TrendSpider store indicator by khaled elsokkary.

Registered as "atr_based_profit_target_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68aa1b-atr-based-profit-target/)
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
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_input = G["input"]
    G_low = G["low"]
    G_paint = G["paint"]
    G_describe_indicator("ATR-based Profit Target")
    atrPeriod = J.get(G_input, "number")("ATR Period", 14, J.obj(("min", 1)))
    atrMultiplier = J.get(G_input, "number")("ATR Multiplier", 1, J.obj(("min", 0.1), ("step", 0.1)))
    myAtr = G_atr(G_high, G_low, G_close, atrPeriod)
    def _f1(_close=J.undefined, _atr=J.undefined, *_args):
        return J.add(_close, J.mul(_atr, atrMultiplier))
    profitTarget = G_for_every(G_close, myAtr, _f1)
    G_paint(profitTarget, J.obj(("name", "ATR Profit Target"), ("color", "green"), ("style", "line"), ("lineWidth", 2)))


register_store_indicator(
    script,
    name='atr_based_profit_target_TS',
    title='ATR-based Profit Target',
    developer='khaled elsokkary',
    url='https://trendspider.com/trading-tools-store/indicators/68aa1b-atr-based-profit-target/',
    position='price',
    inputs=[{'id': 'atr_period', 'title': 'ATR Period', 'type': 'number', 'default': 14}, {'id': 'atr_multiplier', 'title': 'ATR Multiplier', 'type': 'number', 'default': 1}],
    outputs=['atr_profit_target'],
    signals=[],
    requires=[],
    parity='exact',
)
