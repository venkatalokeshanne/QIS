"""
Trend Strength Oscillator (TSO) -- TrendSpider store indicator by TrendSpider Team.

Registered as "trend_strength_oscillator_tso_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/trend-strength-oscillator-tso/)
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
    G_horizontal_line = G["horizontal_line"]
    G_indicators = G["indicators"]
    G_input = G["input"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_rsi = G["rsi"]
    G_sma = G["sma"]
    G_describe_indicator("Trend Strength Oscillator (TSO)", "lower")
    adxPeriod = J.get(G_input, "number")("ADX Period", 14, J.obj(("min", 1)))
    rsiPeriod = J.get(G_input, "number")("RSI Period", 14, J.obj(("min", 1)))
    smoothingPeriod = J.get(G_input, "number")("TSO Smoothing Period", 5, J.obj(("min", 1)))
    myAdx = J.get(G_indicators, "adx")(adxPeriod)
    myRsi = G_rsi(G_close, rsiPeriod)
    def _f1(a=J.undefined, r=J.undefined, *_args):
        adxComponent = J.mul(J.div(J.sub(a, 25), 75), 100)
        rsiComponent = J.sub(r, 50)
        return J.add(adxComponent, rsiComponent)
    rawTso = G_for_every(J.get(myAdx, "adx"), myRsi, _f1)
    smoothedTso = G_sma(rawTso, smoothingPeriod)
    def _f2(t=J.undefined, *_args):
        if J.gt(t, 50):
            return "green"
        if J.lt(t, (-50)):
            return "red"
        return "gray"
    tsoColor = G_for_every(smoothedTso, _f2)
    G_paint(smoothedTso, J.obj(("style", "line"), ("color", tsoColor), ("name", "TSO")))
    G_paint(G_horizontal_line(50), J.obj(("style", "dotted"), ("color", "green"), ("name", "Overbought")))
    G_paint(G_horizontal_line((-50)), J.obj(("style", "dotted"), ("color", "red"), ("name", "Oversold")))
    G_paint(G_horizontal_line(0), J.obj(("style", "dotted"), ("color", "gray"), ("name", "Zero Line")))
    def _f3(t=J.undefined, *_args):
        return J.gt(t, 50)
    G_register_signal(G_for_every(smoothedTso, _f3), "Bullish Trend Overextension")
    def _f4(t=J.undefined, *_args):
        return J.lt(t, (-50))
    G_register_signal(G_for_every(smoothedTso, _f4), "Bearish Trend Overextension")


register_store_indicator(
    script,
    name='trend_strength_oscillator_tso_TS',
    title='Trend Strength Oscillator (TSO)',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/trend-strength-oscillator-tso/',
    position='lower',
    inputs=[{'id': 'adx_period', 'title': 'ADX Period', 'type': 'number', 'default': 14}, {'id': 'rsi_period', 'title': 'RSI Period', 'type': 'number', 'default': 14}, {'id': 'tso_smoothing_period', 'title': 'TSO Smoothing Period', 'type': 'number', 'default': 5}],
    outputs=['tso', 'overbought', 'oversold', 'zero_line', 'bullish_trend_overextension', 'bearish_trend_overextension'],
    signals=['bullish_trend_overextension', 'bearish_trend_overextension'],
    requires=[],
    parity='exact',
)
