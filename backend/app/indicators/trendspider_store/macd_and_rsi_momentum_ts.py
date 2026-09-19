"""
MACD and RSI Momentum -- TrendSpider store indicator by James Chambers.

Registered as "macd_and_rsi_momentum_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/macd-and-rsi-momentum/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_close = G["close"]
    G_color_candles = G["color_candles"]
    G_describe_indicator = G["describe_indicator"]
    G_ema = G["ema"]
    G_for_every = G["for_every"]
    G_input = G["input"]
    G_register_signal = G["register_signal"]
    G_rsi = G["rsi"]
    G_sma = G["sma"]
    G_sub = G["sub"]
    G_describe_indicator("MACD & RSI Based Momentum", "price", J.obj(("shortName", "MACD RSI Momentum"), ("warmup", 250)))
    fastLength = G_input("MACD Fast Length", 12, J.obj(("min", 1), ("max", 100)))
    slowLength = G_input("MACD Slow Length", 26, J.obj(("min", 1), ("max", 100)))
    signalSmoothing = G_input("MACD Signal Length", 9, J.obj(("min", 1), ("max", 100)))
    rsiLength = G_input("RSI Length", 14, J.obj(("min", 1), ("max", 100)))
    fastMA = G_ema(G_close, fastLength)
    slowMA = G_ema(G_close, slowLength)
    macdLine = G_sub(fastMA, slowMA)
    signalLine = G_sma(macdLine, signalSmoothing)
    histogram = G_sub(macdLine, signalLine)
    rsiValues = G_rsi(G_close, rsiLength)
    def _f1(hist=J.undefined, rsi=J.undefined, *_args):
        if (J.gt(hist, 0) and J.gt(rsi, 50)):
            return "blue"
        elif (J.gt(hist, 0) and J.le(rsi, 50)):
            return "lightblue"
        elif (J.lt(hist, 0) and J.lt(rsi, 50)):
            return "red"
        else:
            return "pink"
    candleColors = G_for_every(histogram, rsiValues, _f1)
    G_color_candles(candleColors)
    def _f2(hist=J.undefined, rsi=J.undefined, *_args):
        return (J.gt(rsi, 50) if J.truthy(_t1 := J.gt(hist, 0)) else _t1)
    strongUptrendSignal = G_for_every(histogram, rsiValues, _f2)
    def _f3(hist=J.undefined, rsi=J.undefined, *_args):
        return (J.le(rsi, 50) if J.truthy(_t1 := J.gt(hist, 0)) else _t1)
    weakUptrendSignal = G_for_every(histogram, rsiValues, _f3)
    def _f4(hist=J.undefined, rsi=J.undefined, *_args):
        return (J.lt(rsi, 50) if J.truthy(_t1 := J.lt(hist, 0)) else _t1)
    strongDowntrendSignal = G_for_every(histogram, rsiValues, _f4)
    def _f5(hist=J.undefined, rsi=J.undefined, *_args):
        return (J.ge(rsi, 50) if J.truthy(_t1 := J.lt(hist, 0)) else _t1)
    weakDowntrendSignal = G_for_every(histogram, rsiValues, _f5)
    G_register_signal(strongUptrendSignal, "Strong Uptrend")
    G_register_signal(weakUptrendSignal, "Weak Uptrend")
    G_register_signal(strongDowntrendSignal, "Strong Downtrend")
    G_register_signal(weakDowntrendSignal, "Weak Downtrend")


register_store_indicator(
    script,
    name='macd_and_rsi_momentum_TS',
    title='MACD and RSI Momentum',
    developer='James Chambers',
    url='https://trendspider.com/trading-tools-store/indicators/macd-and-rsi-momentum/',
    position='price',
    inputs=[{'id': 'warmup', 'title': 'Warmup', 'type': 'number', 'default': 250}, {'id': 'macd_fast_length', 'title': 'MACD Fast Length', 'type': 'number', 'default': 12}, {'id': 'macd_slow_length', 'title': 'MACD Slow Length', 'type': 'number', 'default': 26}, {'id': 'macd_signal_length', 'title': 'MACD Signal Length', 'type': 'number', 'default': 9}, {'id': 'rsi_length', 'title': 'RSI Length', 'type': 'number', 'default': 14}],
    outputs=['cdl', 'strong_uptrend', 'weak_uptrend', 'strong_downtrend', 'weak_downtrend'],
    signals=['strong_uptrend', 'weak_uptrend', 'strong_downtrend', 'weak_downtrend'],
    requires=[],
    parity='exact',
)
