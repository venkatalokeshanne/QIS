"""
LRI Pivot -- TrendSpider store indicator by Grant Pratt.

Registered as "lri_pivot_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68a735-lri-pivot/)
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
    G_color_candles = G["color_candles"]
    G_describe_indicator = G["describe_indicator"]
    G_ema = G["ema"]
    G_input = G["input"]
    G_linreg = G["linreg"]
    G_paint = G["paint"]
    G_series_of = G["series_of"]
    G_shift = G["shift"]
    G_describe_indicator("LRI Pivot")
    myLength = J.get(G_input, "number")("LR Length", 17, J.obj(("min", 1)))
    myDelay = J.get(G_input, "number")("Delay", 16, J.obj(("min", 0)))
    myEmaLength = J.get(G_input, "number")("EMA Length", 13, J.obj(("min", 1)))
    myLriSmoothLength = J.get(G_input, "number")("LRI Smooth Length", 5, J.obj(("min", 1)))
    myLri = G_linreg(G_close, myLength)
    mySmoothLri = G_ema(myLri, myLriSmoothLength)
    myShiftedLri = G_shift(mySmoothLri, myDelay)
    myEma = G_ema(G_close, myEmaLength)
    myColors = G_series_of(None)
    i = J.get(G_Math, "max")(myDelay, myEmaLength, myLriSmoothLength, 1)
    while J.lt(i, J.get(G_close, "length")):
        if ((J.gt(J.get(G_close, i), J.get(myShiftedLri, i)) and J.le(J.get(G_close, J.sub(i, 1)), J.get(myShiftedLri, J.sub(i, 1)))) or (J.lt(J.get(G_close, i), J.get(myShiftedLri, i)) and J.ge(J.get(G_close, J.sub(i, 1)), J.get(myShiftedLri, J.sub(i, 1))))):
            J.set(myColors, i, "orange")
        elif (J.gt(J.get(G_close, i), J.get(myShiftedLri, i)) and J.gt(J.get(G_close, i), J.get(myEma, i))):
            J.set(myColors, i, "darkgreen")
        elif (J.gt(J.get(G_close, i), J.get(myShiftedLri, i)) and J.le(J.get(G_close, i), J.get(myEma, i))):
            J.set(myColors, i, "lightgreen")
        elif (J.le(J.get(G_close, i), J.get(myShiftedLri, i)) and J.gt(J.get(G_close, i), J.get(myEma, i))):
            J.set(myColors, i, "pink")
        else:
            J.set(myColors, i, "darkred")
        i = J.inc(i)
    G_paint(myShiftedLri, J.obj(("color", "purple"), ("name", "Shifted Smoothed LRI")))
    G_paint(myEma, J.obj(("color", "white"), ("name", "13 EMA")))
    G_color_candles(myColors)


register_store_indicator(
    script,
    name='lri_pivot_TS',
    title='LRI Pivot',
    developer='Grant Pratt',
    url='https://trendspider.com/trading-tools-store/indicators/68a735-lri-pivot/',
    position='price',
    inputs=[{'id': 'lr_length', 'title': 'LR Length', 'type': 'number', 'default': 17}, {'id': 'delay', 'title': 'Delay', 'type': 'number', 'default': 16}, {'id': 'ema_length', 'title': 'EMA Length', 'type': 'number', 'default': 13}, {'id': 'lri_smooth_length', 'title': 'LRI Smooth Length', 'type': 'number', 'default': 5}],
    outputs=['shifted_smoothed_lri', '13_ema', 'cdl'],
    signals=[],
    requires=[],
    parity='exact',
)
