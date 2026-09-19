"""
Stochastic + RSI Volume -- TrendSpider store indicator by TrendSpider Team.

Registered as "stochastic_rsi_volume_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/stochastic-rsi-volume/)
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
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_input = G["input"]
    G_low = G["low"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_rsi = G["rsi"]
    G_sma = G["sma"]
    G_stochastic = G["stochastic"]
    G_volume = G["volume"]
    G_describe_indicator("Stochastic + RSI Volume", "lower")
    rsiLength = J.get(G_input, "number")("RSI Length", 14, J.obj(("min", 1)))
    rsiOverbought = J.get(G_input, "number")("RSI Overbought", 70, J.obj(("min", 50), ("max", 100)))
    rsiOversold = J.get(G_input, "number")("RSI Oversold", 30, J.obj(("min", 0), ("max", 50)))
    stochLength = J.get(G_input, "number")("Stochastic Length", 14, J.obj(("min", 1)))
    stochSmooth = J.get(G_input, "number")("Stochastic Smooth", 3, J.obj(("min", 1)))
    stochOverbought = J.get(G_input, "number")("Stochastic Overbought", 80, J.obj(("min", 50), ("max", 100)))
    stochOversold = J.get(G_input, "number")("Stochastic Oversold", 20, J.obj(("min", 0), ("max", 50)))
    myRsi = G_rsi(G_close, rsiLength)
    myStoch = G_stochastic(G_close, G_high, G_low, stochLength)
    myStochK = G_sma(myStoch, stochSmooth)
    myStochD = G_sma(myStochK, stochSmooth)
    colorOversold = "green"
    colorNeutral = "grey"
    colorOverbought = "red"
    def _f1(r=J.undefined, k=J.undefined, d=J.undefined, *_args):
        if ((J.le(r, rsiOversold) and J.le(k, stochOversold)) and J.le(d, stochOversold)):
            return colorOversold
        if ((J.ge(r, rsiOverbought) and J.ge(k, stochOverbought)) and J.ge(d, stochOverbought)):
            return colorOverbought
        return colorNeutral
    volumeColor = G_for_every(myRsi, myStochK, myStochD, _f1)
    G_paint(G_volume, J.obj(("name", "Volume"), ("color", volumeColor), ("style", "column")))
    G_paint(myStochK, J.obj(("name", "Stoch %K"), ("color", "blue")))
    G_paint(myStochD, J.obj(("name", "Stoch %D"), ("color", "red")))
    def _f2(r=J.undefined, k=J.undefined, d=J.undefined, *_args):
        return (1 if ((J.le(r, rsiOversold) and J.le(k, stochOversold)) and J.le(d, stochOversold)) else 0)
    oversoldSignal = G_for_every(myRsi, myStochK, myStochD, _f2)
    def _f3(r=J.undefined, k=J.undefined, d=J.undefined, *_args):
        return (1 if ((J.ge(r, rsiOverbought) and J.ge(k, stochOverbought)) and J.ge(d, stochOverbought)) else 0)
    overboughtSignal = G_for_every(myRsi, myStochK, myStochD, _f3)
    G_register_signal(oversoldSignal, "Oversold Volume")
    G_register_signal(overboughtSignal, "Overbought Volume")


register_store_indicator(
    script,
    name='stochastic_rsi_volume_TS',
    title='Stochastic + RSI Volume',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/stochastic-rsi-volume/',
    position='lower',
    inputs=[{'id': 'rsi_length', 'title': 'RSI Length', 'type': 'number', 'default': 14}, {'id': 'rsi_overbought', 'title': 'RSI Overbought', 'type': 'number', 'default': 70}, {'id': 'rsi_oversold', 'title': 'RSI Oversold', 'type': 'number', 'default': 30}, {'id': 'stochastic_length', 'title': 'Stochastic Length', 'type': 'number', 'default': 14}, {'id': 'stochastic_smooth', 'title': 'Stochastic Smooth', 'type': 'number', 'default': 3}, {'id': 'stochastic_overbought', 'title': 'Stochastic Overbought', 'type': 'number', 'default': 80}, {'id': 'stochastic_oversold', 'title': 'Stochastic Oversold', 'type': 'number', 'default': 20}],
    outputs=['volume', 'stoch__k', 'stoch__d', 'oversold_volume', 'overbought_volume'],
    signals=['oversold_volume', 'overbought_volume'],
    requires=[],
    parity='exact',
)
