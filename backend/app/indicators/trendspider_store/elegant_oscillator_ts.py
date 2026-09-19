"""
Elegant Oscillator -- TrendSpider store indicator by James Chambers.

Registered as "elegant_oscillator_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/elegant-oscillator/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_div = G["div"]
    G_ema = G["ema"]
    G_horizontal_line = G["horizontal_line"]
    G_input = G["input"]
    G_mult = G["mult"]
    G_paint = G["paint"]
    G_shift = G["shift"]
    G_sma = G["sma"]
    G_sub = G["sub"]
    G_describe_indicator("Elegant Oscillator", "lower", J.obj(("shortName", "EO")))
    rmsLength = J.get(G_input, "number")("RMS Length", 50, J.obj(("min", 1)))
    cutoffLength = J.get(G_input, "number")("Cutoff Length", 20, J.obj(("min", 1)))
    threshold = J.get(G_input, "number")("Threshold", 0.5, J.obj(("min", 0), ("max", 1)))
    derivative = G_sub(G_close, G_shift(G_close, 2))
    rms = J.get(G_sma(G_mult(derivative, derivative), rmsLength), "map")(J.get(G_Math, "sqrt"))
    normDerivative = G_div(derivative, rms)
    def _f1(value=J.undefined, *_args):
        return J.div(J.sub(J.get(G_Math, "exp")(J.mul(2, value)), 1), J.add(J.get(G_Math, "exp")(J.mul(2, value)), 1))
    ift = J.get(normDerivative, "map")(_f1)
    elegantOsc = G_ema(ift, cutoffLength)
    def _f2(value=J.undefined, *_args):
        return ("#00FF00" if J.ge(value, 0) else "#FF0000")
    oscColors = J.get(elegantOsc, "map")(_f2)
    G_paint(elegantOsc, J.obj(("name", "Elegant Oscillator"), ("style", "histogram"), ("color", oscColors)))
    G_paint(G_horizontal_line(threshold), "Upper Level", "#FFA500")
    G_paint(G_horizontal_line(0), "Zero Line", "#000000", "dotted")
    G_paint(G_horizontal_line(J.neg(threshold)), "Lower Level", "#FFA500")


register_store_indicator(
    script,
    name='elegant_oscillator_TS',
    title='Elegant Oscillator',
    developer='James Chambers',
    url='https://trendspider.com/trading-tools-store/indicators/elegant-oscillator/',
    position='lower',
    inputs=[{'id': 'rms_length', 'title': 'RMS Length', 'type': 'number', 'default': 50}, {'id': 'cutoff_length', 'title': 'Cutoff Length', 'type': 'number', 'default': 20}, {'id': 'threshold', 'title': 'Threshold', 'type': 'number', 'default': 0.5}],
    outputs=['elegant_oscillator', 'upper_level', 'zero_line', 'lower_level'],
    signals=[],
    requires=[],
    parity='exact',
)
