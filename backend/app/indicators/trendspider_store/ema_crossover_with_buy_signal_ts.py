"""
EMA Crossover with Buy Signal -- TrendSpider store indicator by TrendSpider Team.

Registered as "ema_crossover_with_buy_signal_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/ema-crossover-with-buy-signal/)
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
    G_ema = G["ema"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_series_of = G["series_of"]
    def EMA_Crossover_Signals(emaShortLength_2=J.undefined, emaLongLength_2=J.undefined, arrowOffset_2=J.undefined, *_args):
        emaShort = G_ema(G_close, emaShortLength_2)
        emaLong = G_ema(G_close, emaLongLength_2)
        buySignalSeries = G_series_of(None)
        sellSignalSeries = G_series_of(None)
        buyConditionSeries = G_series_of(False)
        sellConditionSeries = G_series_of(False)
        i = 1
        while J.lt(i, J.get(G_close, "length")):
            if (J.le(J.get(emaShort, J.sub(i, 1)), J.get(emaLong, J.sub(i, 1))) and J.gt(J.get(emaShort, i), J.get(emaLong, i))):
                J.set(buySignalSeries, i, "Buy")
                J.set(buyConditionSeries, i, True)
            if (J.ge(J.get(emaShort, J.sub(i, 1)), J.get(emaLong, J.sub(i, 1))) and J.lt(J.get(emaShort, i), J.get(emaLong, i))):
                J.set(sellSignalSeries, i, "Sell")
                J.set(sellConditionSeries, i, True)
            i = J.inc(i)
        G_paint(emaShort, J.obj(("name", J.template("EMA ", emaShortLength_2)), ("color", "blue"), ("thickness", 2), ("style", "line")))
        G_paint(emaLong, J.obj(("name", J.template("EMA ", emaLongLength_2)), ("color", "red"), ("thickness", 2), ("style", "line")))
        G_paint(buySignalSeries, J.obj(("style", "labels_below"), ("color", "white"), ("backgroundColor", "green"), ("verticalOffset", arrowOffset_2), ("text", "Buy")))
        G_paint(sellSignalSeries, J.obj(("style", "labels_above"), ("color", "white"), ("backgroundColor", "red"), ("verticalOffset", arrowOffset_2), ("text", "Sell")))
        G_register_signal(buyConditionSeries, "EMA Crossover Buy Signal")
        G_register_signal(sellConditionSeries, "EMA Crossover Sell Signal")
    G_describe_indicator("EMA Crossover Signals", "price", J.obj(("shortName", "EMACross")))
    emaShortLength = 13
    emaLongLength = 50
    arrowOffset = (-10)
    EMA_Crossover_Signals(emaShortLength, emaLongLength, arrowOffset)


register_store_indicator(
    script,
    name='ema_crossover_with_buy_signal_TS',
    title='EMA Crossover with Buy Signal',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/ema-crossover-with-buy-signal/',
    position='price',
    inputs=[],
    outputs=['ema_13', 'ema_50', 'line_3', 'line_4', 'ema_crossover_buy_signal', 'ema_crossover_sell_signal'],
    signals=['ema_crossover_buy_signal', 'ema_crossover_sell_signal'],
    requires=[],
    parity='exact',
)
