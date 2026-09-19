"""
RVOL Color-Coded Volume -- TrendSpider store indicator by TrendSpider Team.

Registered as "rvol_color_coded_volume_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/rvol-color-coded-volume/)
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
    G_div = G["div"]
    G_for_every = G["for_every"]
    G_input = G["input"]
    G_open = G["open"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_sma = G["sma"]
    G_volume = G["volume"]
    G_describe_indicator("RVOL Color-Coded Volume", "lower")
    lookbackPeriod = J.get(G_input, "number")("RVOL Lookback Period", 20, J.obj(("min", 5), ("max", 100)))
    moderateThreshold = J.get(G_input, "number")("Moderate RVOL Threshold", 1, J.obj(("min", 0.5), ("max", 2), ("step", 0.1)))
    highThreshold = J.get(G_input, "number")("High RVOL Threshold", 2, J.obj(("min", 1), ("max", 3), ("step", 0.1)))
    extremeThreshold = J.get(G_input, "number")("Extreme RVOL Threshold", 3, J.obj(("min", 2), ("max", 5), ("step", 0.1)))
    lowRvolColor = J.get(G_input, "color")("Low RVOL Color", "#808080")
    moderateBullishColor = J.get(G_input, "color")("Moderate Bullish RVOL Color", "#8fc9f9")
    highBullishColor = J.get(G_input, "color")("High Bullish RVOL Color", "#0da8f4")
    extremeBullishColor = J.get(G_input, "color")("Extreme Bullish RVOL Color", "#00ffff")
    moderateBearishColor = J.get(G_input, "color")("Moderate Bearish RVOL Color", "#FF6666")
    highBearishColor = J.get(G_input, "color")("High Bearish RVOL Color", "#FF0000")
    extremeBearishColor = J.get(G_input, "color")("Extreme Bearish RVOL Color", "#FF1493")
    myVma = G_sma(G_volume, lookbackPeriod)
    myRvol = G_div(G_volume, myVma)
    def getVolumeColor(rvolValue=J.undefined, openPrice=J.undefined, closePrice=J.undefined, *_args):
        if J.lt(rvolValue, moderateThreshold):
            return lowRvolColor
        if J.gt(closePrice, openPrice):
            if J.ge(rvolValue, extremeThreshold):
                return extremeBullishColor
            if J.ge(rvolValue, highThreshold):
                return highBullishColor
            return moderateBullishColor
        elif J.lt(closePrice, openPrice):
            if J.ge(rvolValue, extremeThreshold):
                return extremeBearishColor
            if J.ge(rvolValue, highThreshold):
                return highBearishColor
            return moderateBearishColor
        return lowRvolColor
    def _f1(_rvol=J.undefined, _open=J.undefined, _close=J.undefined, *_args):
        return getVolumeColor(_rvol, _open, _close)
    myVolumeColors = G_for_every(myRvol, G_open, G_close, _f1)
    G_paint(G_volume, J.obj(("style", "column"), ("color", myVolumeColors), ("name", "Colored Volume")))
    def _f2(_r=J.undefined, *_args):
        return J.ge(_r, moderateThreshold)
    G_register_signal(G_for_every(myRvol, _f2), "Moderate RVOL")
    def _f3(_r=J.undefined, *_args):
        return J.ge(_r, highThreshold)
    G_register_signal(G_for_every(myRvol, _f3), "High RVOL")
    def _f4(_r=J.undefined, *_args):
        return J.ge(_r, extremeThreshold)
    G_register_signal(G_for_every(myRvol, _f4), "Extreme RVOL")
    def _f5(_r=J.undefined, _c=J.undefined, _o=J.undefined, *_args):
        return (J.gt(_c, _o) if J.truthy(_t1 := J.ge(_r, extremeThreshold)) else _t1)
    G_register_signal(G_for_every(myRvol, G_close, G_open, _f5), "Extreme Bullish RVOL")
    def _f6(_r=J.undefined, _c=J.undefined, _o=J.undefined, *_args):
        return (J.lt(_c, _o) if J.truthy(_t1 := J.ge(_r, extremeThreshold)) else _t1)
    G_register_signal(G_for_every(myRvol, G_close, G_open, _f6), "Extreme Bearish RVOL")


register_store_indicator(
    script,
    name='rvol_color_coded_volume_TS',
    title='RVOL Color-Coded Volume',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/rvol-color-coded-volume/',
    position='lower',
    inputs=[{'id': 'rvol_lookback_period', 'title': 'RVOL Lookback Period', 'type': 'number', 'default': 20}, {'id': 'moderate_rvol_threshold', 'title': 'Moderate RVOL Threshold', 'type': 'number', 'default': 1}, {'id': 'high_rvol_threshold', 'title': 'High RVOL Threshold', 'type': 'number', 'default': 2}, {'id': 'extreme_rvol_threshold', 'title': 'Extreme RVOL Threshold', 'type': 'number', 'default': 3}, {'id': 'low_rvol_color', 'title': 'Low RVOL Color', 'type': 'color', 'default': '#808080'}, {'id': 'moderate_bullish_rvol_color', 'title': 'Moderate Bullish RVOL Color', 'type': 'color', 'default': '#8fc9f9'}, {'id': 'high_bullish_rvol_color', 'title': 'High Bullish RVOL Color', 'type': 'color', 'default': '#0da8f4'}, {'id': 'extreme_bullish_rvol_color', 'title': 'Extreme Bullish RVOL Color', 'type': 'color', 'default': '#00ffff'}, {'id': 'moderate_bearish_rvol_color', 'title': 'Moderate Bearish RVOL Color', 'type': 'color', 'default': '#FF6666'}, {'id': 'high_bearish_rvol_color', 'title': 'High Bearish RVOL Color', 'type': 'color', 'default': '#FF0000'}, {'id': 'extreme_bearish_rvol_color', 'title': 'Extreme Bearish RVOL Color', 'type': 'color', 'default': '#FF1493'}],
    outputs=['colored_volume', 'moderate_rvol', 'high_rvol', 'extreme_rvol', 'extreme_bullish_rvol', 'extreme_bearish_rvol'],
    signals=['moderate_rvol', 'high_rvol', 'extreme_rvol', 'extreme_bullish_rvol', 'extreme_bearish_rvol'],
    requires=[],
    parity='exact',
)
