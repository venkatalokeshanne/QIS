"""
Volume Flow Indicator -- TrendSpider store indicator by TrendSpider Team.

Registered as "volume_flow_indicator_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/volume-flow-indicator/)
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
    G_color_cloud = G["color_cloud"]
    G_describe_indicator = G["describe_indicator"]
    G_div = G["div"]
    G_ema = G["ema"]
    G_for_every = G["for_every"]
    G_hlc3 = G["hlc3"]
    G_horizontal_line = G["horizontal_line"]
    G_input = G["input"]
    G_min_of = G["min_of"]
    G_mult = G["mult"]
    G_paint = G["paint"]
    G_shift = G["shift"]
    G_sma = G["sma"]
    G_stdev = G["stdev"]
    G_sum = G["sum"]
    G_volume = G["volume"]
    G_describe_indicator("Volume Flow Indicator", "lower")
    period = G_input("VFI Period", 130, J.obj(("min", 26), ("max", 300)))
    smooth = G_input("Smooth", 3, J.obj(("min", 1), ("max", 10)))
    maPeriod = G_input("MA Period", 30, J.obj(("min", 20), ("max", 100)))
    coef = G_input("Coef", 0.2)
    volCoef = G_input("Vol Cutoff", 2.5, J.obj(("min", 1), ("max", 5)))
    def _f1(value=J.undefined, previousValue=J.undefined, *_args):
        return J.sub(J.get(G_Math, "log")(value), J.get(G_Math, "log")(previousValue))
    inter = G_for_every(G_hlc3, G_shift(G_hlc3, 1), _f1)
    vinter = G_stdev(inter, 30)
    cutoff = G_mult(vinter, G_close, coef)
    vave = G_shift(G_sma(G_volume, period), (-1))
    vMax = G_mult(vave, volCoef)
    vC = G_min_of(G_volume, vMax)
    def _f2(value=J.undefined, previousValue=J.undefined, *_args):
        return J.sub(value, previousValue)
    mF = G_for_every(G_hlc3, G_shift(G_hlc3, 1), _f2)
    def _f3(mFValue=J.undefined, vCValue=J.undefined, cOValue=J.undefined, *_args):
        if J.gt(mFValue, cOValue):
            return vCValue
        elif J.lt(mFValue, J.neg(cOValue)):
            return J.neg(vCValue)
        else:
            return 0
    vCP = G_for_every(mF, vC, cutoff, _f3)
    vFI1 = G_div(G_sum(vCP, period), vave)
    vFI = G_ema(vFI1, smooth)
    mAVFI = G_sma(vFI, maPeriod)
    G_paint(vFI, "VFI", "black")
    G_paint(mAVFI, "MAVFI", "#00bcd4", "dotted")
    zeroLine = G_horizontal_line(0)
    G_color_cloud(zeroLine, vFI, "red", "green")
    G_paint(zeroLine, "Zero", "gray", "dotted")


register_store_indicator(
    script,
    name='volume_flow_indicator_TS',
    title='Volume Flow Indicator',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/volume-flow-indicator/',
    position='lower',
    inputs=[{'id': 'vfi_period', 'title': 'VFI Period', 'type': 'number', 'default': 130}, {'id': 'smooth', 'title': 'Smooth', 'type': 'number', 'default': 3}, {'id': 'ma_period', 'title': 'MA Period', 'type': 'number', 'default': 30}, {'id': 'coef', 'title': 'Coef', 'type': 'number', 'default': 0.2}, {'id': 'vol_cutoff', 'title': 'Vol Cutoff', 'type': 'number', 'default': 2.5}],
    outputs=['vfi', 'mavfi', 'line_3', 'line_4', 'line_6', 'line_7', 'zero'],
    signals=[],
    requires=[],
    parity='exact',
)
