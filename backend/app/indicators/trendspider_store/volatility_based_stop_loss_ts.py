"""
Volatility Based Stop Loss -- TrendSpider store indicator by TrendSpider Team.

Registered as "volatility_based_stop_loss_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/volatility-based-stop-loss/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_atr = G["atr"]
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_input = G["input"]
    G_paint = G["paint"]
    G_series_of = G["series_of"]
    G_describe_indicator("Volatility-Based Stop Loss")
    length = J.get(G_input, "number")("ATR Length", 14, J.obj(("min", 1)))
    multiplier = J.get(G_input, "number")("ATR Multiplier", 2, J.obj(("min", 0.1), ("step", 0.1)))
    myAtr = G_atr(length)
    stopLoss = G_series_of(None)
    def _f1(c=J.undefined, a=J.undefined, prev=J.undefined, i=J.undefined, *_args):
        if J.seq(i, 0):
            J.set(stopLoss, i, J.sub(c, J.mul(a, multiplier)))
        else:
            prevStop = J.get(stopLoss, J.sub(i, 1))
            if J.gt(c, prevStop):
                J.set(stopLoss, i, J.get(G_Math, "max")(J.sub(c, J.mul(a, multiplier)), prevStop))
            else:
                J.set(stopLoss, i, J.get(G_Math, "min")(J.add(c, J.mul(a, multiplier)), prevStop))
    G_for_every(G_close, myAtr, _f1)
    def _f2(c=J.undefined, s=J.undefined, *_args):
        return ("green" if J.gt(c, s) else "red")
    stopColor = G_for_every(G_close, stopLoss, _f2)
    G_paint(stopLoss, J.obj(("name", "Volatility Stop"), ("color", stopColor), ("style", "line"), ("linewidth", 2)))


register_store_indicator(
    script,
    name='volatility_based_stop_loss_TS',
    title='Volatility Based Stop Loss',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/volatility-based-stop-loss/',
    position='price',
    inputs=[{'id': 'atr_length', 'title': 'ATR Length', 'type': 'number', 'default': 14}, {'id': 'atr_multiplier', 'title': 'ATR Multiplier', 'type': 'number', 'default': 2}],
    outputs=['volatility_stop'],
    signals=[],
    requires=[],
    parity='exact',
)
