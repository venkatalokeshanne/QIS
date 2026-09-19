"""
EMA Stacked -- TrendSpider store indicator by Yoseif Haddad.

Registered as "ema_stacked_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/691f4d-ema-stacked/)
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
    G_input = G["input"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_series_of = G["series_of"]
    G_describe_indicator("EMA Stacked", "lower")
    lookback = J.get(G_input, "number")("Lookback for EMA trend", 20, J.obj(("min", 1), ("max", 50)))
    ema1Length = J.get(G_input, "number")("EMA 1 Length", 8, J.obj(("min", 1), ("max", 500)))
    ema2Length = J.get(G_input, "number")("EMA 2 Length", 21, J.obj(("min", 1), ("max", 500)))
    ema3Length = J.get(G_input, "number")("EMA 3 Length", 34, J.obj(("min", 1), ("max", 500)))
    ema4Length = J.get(G_input, "number")("EMA 4 Length", 55, J.obj(("min", 1), ("max", 500)))
    ema5Length = J.get(G_input, "number")("EMA 5 Length", 89, J.obj(("min", 1), ("max", 500)))
    e8 = G_ema(G_close, ema1Length)
    e21 = G_ema(G_close, ema2Length)
    e34 = G_ema(G_close, ema3Length)
    e55 = G_ema(G_close, ema4Length)
    e89 = G_ema(G_close, ema5Length)
    dotValues = G_series_of(0)
    dotColors = G_series_of(None)
    signalStrongBullish = G_series_of(False)
    signalBullish = G_series_of(False)
    signalStrongBearish = G_series_of(False)
    signalBearish = G_series_of(False)
    signalNeutral = G_series_of(False)
    i = lookback
    while J.lt(i, J.get(G_close, "length")):
        positivelyStacked = (J.gt(J.get(e55, i), J.get(e89, i)) if J.truthy(_t1 := (J.gt(J.get(e34, i), J.get(e55, i)) if J.truthy(_t2 := (J.gt(J.get(e21, i), J.get(e34, i)) if J.truthy(_t3 := J.gt(J.get(e8, i), J.get(e21, i))) else _t3)) else _t2)) else _t1)
        negativelyStacked = (J.lt(J.get(e55, i), J.get(e89, i)) if J.truthy(_t4 := (J.lt(J.get(e34, i), J.get(e55, i)) if J.truthy(_t5 := (J.lt(J.get(e21, i), J.get(e34, i)) if J.truthy(_t6 := J.lt(J.get(e8, i), J.get(e21, i))) else _t6)) else _t5)) else _t4)
        e8Rising = J.gt(J.get(e8, i), J.get(e8, J.sub(i, lookback)))
        e21Rising = J.gt(J.get(e21, i), J.get(e21, J.sub(i, lookback)))
        e34Rising = J.gt(J.get(e34, i), J.get(e34, J.sub(i, lookback)))
        e55Rising = J.gt(J.get(e55, i), J.get(e55, J.sub(i, lookback)))
        e89Rising = J.gt(J.get(e89, i), J.get(e89, J.sub(i, lookback)))
        e8Falling = J.lt(J.get(e8, i), J.get(e8, J.sub(i, lookback)))
        e21Falling = J.lt(J.get(e21, i), J.get(e21, J.sub(i, lookback)))
        e34Falling = J.lt(J.get(e34, i), J.get(e34, J.sub(i, lookback)))
        e55Falling = J.lt(J.get(e55, i), J.get(e55, J.sub(i, lookback)))
        e89Falling = J.lt(J.get(e89, i), J.get(e89, J.sub(i, lookback)))
        allRising = (e89Rising if J.truthy(_t7 := (e55Rising if J.truthy(_t8 := (e34Rising if J.truthy(_t9 := (e21Rising if J.truthy(_t10 := e8Rising) else _t10)) else _t9)) else _t8)) else _t7)
        allFalling = (e89Falling if J.truthy(_t11 := (e55Falling if J.truthy(_t12 := (e34Falling if J.truthy(_t13 := (e21Falling if J.truthy(_t14 := e8Falling) else _t14)) else _t13)) else _t12)) else _t11)
        if J.truthy(positivelyStacked):
            if J.truthy(allRising):
                J.set(dotColors, i, "#16a34a")
                J.set(signalStrongBullish, i, True)
            else:
                J.set(dotColors, i, "#86efac")
                J.set(signalBullish, i, True)
        elif J.truthy(negativelyStacked):
            if J.truthy(allFalling):
                J.set(dotColors, i, "#dc2626")
                J.set(signalStrongBearish, i, True)
            else:
                J.set(dotColors, i, "#fca5a5")
                J.set(signalBearish, i, True)
        else:
            J.set(dotColors, i, "#6b7280")
            J.set(signalNeutral, i, True)
        i = J.inc(i)
    G_paint(dotValues, J.obj(("name", "EMA Signal"), ("color", dotColors), ("style", "dotted"), ("thickness", 4)))
    G_register_signal(signalStrongBullish, "Strong Bullish (All EMAs Rising)")
    G_register_signal(signalBullish, "Bullish (Stacked Positive)")
    G_register_signal(signalStrongBearish, "Strong Bearish (All EMAs Falling)")
    G_register_signal(signalBearish, "Bearish (Stacked Negative)")
    G_register_signal(signalNeutral, "Neutral (Not Stacked)")


register_store_indicator(
    script,
    name='ema_stacked_TS',
    title='EMA Stacked',
    developer='Yoseif Haddad',
    url='https://trendspider.com/trading-tools-store/indicators/691f4d-ema-stacked/',
    position='lower',
    inputs=[{'id': 'lookback_for_ema_trend', 'title': 'Lookback for EMA trend', 'type': 'number', 'default': 20}, {'id': 'ema_1_length', 'title': 'EMA 1 Length', 'type': 'number', 'default': 8}, {'id': 'ema_2_length', 'title': 'EMA 2 Length', 'type': 'number', 'default': 21}, {'id': 'ema_3_length', 'title': 'EMA 3 Length', 'type': 'number', 'default': 34}, {'id': 'ema_4_length', 'title': 'EMA 4 Length', 'type': 'number', 'default': 55}, {'id': 'ema_5_length', 'title': 'EMA 5 Length', 'type': 'number', 'default': 89}],
    outputs=['ema_signal', 'strong_bullish__all_emas_rising_', 'bullish__stacked_positive_', 'strong_bearish__all_emas_falling_', 'bearish__stacked_negative_', 'neutral__not_stacked_'],
    signals=['strong_bullish__all_emas_rising_', 'bullish__stacked_positive_', 'strong_bearish__all_emas_falling_', 'bearish__stacked_negative_', 'neutral__not_stacked_'],
    requires=[],
    parity='exact',
)
