"""
CCI and ATR strategy -- TrendSpider store indicator by TrendSpider Team.

Registered as "cci_and_atr_strategy_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/cci-and-atr-strategy/)
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
    G_cci = G["cci"]
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_input = G["input"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_series_of = G["series_of"]
    G_describe_indicator("CCI & ATR Strategy", "price", J.obj(("shortName", "CCI_ATR_Strategy")))
    cciLength = G_input("CCI Length", 14, J.obj(("min", 1), ("max", 50)))
    atrLength = G_input("ATR Length", 14, J.obj(("min", 1), ("max", 50)))
    atrMultiplier = G_input("ATR Multiplier", 2, J.obj(("min", 0.1), ("max", 10)))
    cciValues = G_cci(G_close, cciLength)
    atrValues = G_atr(atrLength)
    def _f1(val=J.undefined, *_args):
        return J.lt(val, (-200))
    buySignal = J.get(cciValues, "map")(_f1)
    inPosition = False
    entryPrice = 0
    buySellSignals = G_series_of(None)
    i = 1
    while J.lt(i, J.get(G_close, "length")):
        if (J.truthy(J.get(buySignal, i)) and (not J.truthy(inPosition))):
            J.set(buySellSignals, i, "BUY")
            entryPrice = J.get(G_close, i)
            inPosition = True
        elif J.truthy(inPosition):
            priceChange = J.get(G_Math, "abs")(J.sub(J.get(G_close, i), entryPrice))
            if J.gt(priceChange, J.mul(J.get(atrValues, i), atrMultiplier)):
                J.set(buySellSignals, i, "SELL")
                inPosition = False
        i = J.inc(i)
    def _f2(signal=J.undefined, *_args):
        return ("BUY" if J.seq(signal, "BUY") else None)
    buyLabels = J.get(buySellSignals, "map")(_f2)
    def _f3(signal=J.undefined, *_args):
        return ("SELL" if J.seq(signal, "SELL") else None)
    sellLabels = J.get(buySellSignals, "map")(_f3)
    G_paint(buyLabels, J.obj(("style", "labels_below"), ("color", "black"), ("backgroundColor", "#0ADD08"), ("fontSize", 7), ("backgroundBorderRadius", 3), ("verticalOffset", 3)))
    G_paint(sellLabels, J.obj(("style", "labels_above"), ("color", "black"), ("backgroundColor", "#EE4B2B"), ("fontSize", 7), ("backgroundBorderRadius", 3), ("verticalOffset", 3)))
    def _f4(signal=J.undefined, *_args):
        return J.seq(signal, "BUY")
    buySignalSeries = J.get(buySellSignals, "map")(_f4)
    def _f5(signal=J.undefined, *_args):
        return J.seq(signal, "SELL")
    sellSignalSeries = J.get(buySellSignals, "map")(_f5)
    G_register_signal(buySignalSeries, "Buy Signal")
    G_register_signal(sellSignalSeries, "Sell Signal")


register_store_indicator(
    script,
    name='cci_and_atr_strategy_TS',
    title='CCI and ATR strategy',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/cci-and-atr-strategy/',
    position='price',
    inputs=[{'id': 'cci_length', 'title': 'CCI Length', 'type': 'number', 'default': 14}, {'id': 'atr_length', 'title': 'ATR Length', 'type': 'number', 'default': 14}, {'id': 'atr_multiplier', 'title': 'ATR Multiplier', 'type': 'number', 'default': 2}],
    outputs=['line_1', 'line_2', 'buy_signal', 'sell_signal'],
    signals=['buy_signal', 'sell_signal'],
    requires=[],
    parity='exact',
)
