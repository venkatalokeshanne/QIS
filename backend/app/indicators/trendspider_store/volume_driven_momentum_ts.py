"""
Volume-Driven Momentum -- TrendSpider store indicator by TrendSpider Team.

Registered as "volume_driven_momentum_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/volume-driven-momentum/)
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
    G_div = G["div"]
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_input = G["input"]
    G_low = G["low"]
    G_open = G["open"]
    G_register_signal = G["register_signal"]
    G_sma = G["sma"]
    G_volume = G["volume"]
    G_describe_indicator("Volume-Driven Momentum")
    rvolThreshold = J.get(G_input, "number")("RVOL Threshold", 2, J.obj(("min", 1)))
    rvolPeriod = J.get(G_input, "number")("RVOL Lookback Period", 20, J.obj(("min", 1)))
    bullishColor = J.get(G_input, "color")("Bullish Candle Color", "cyan")
    bearishColor = J.get(G_input, "color")("Bearish Candle Color", "#FF69B4")
    myVolumeSMA = G_sma(G_volume, rvolPeriod)
    myRVOL = G_div(G_volume, myVolumeSMA)
    def hasLargeBody(o=J.undefined, h=J.undefined, l=J.undefined, c=J.undefined, *_args):
        bodySize = J.get(G_Math, "abs")(J.sub(c, o))
        totalWickSize = J.sub(J.sub(h, l), bodySize)
        return J.ge(bodySize, J.mul(2, totalWickSize))
    def _f1(_o=J.undefined, _h=J.undefined, _l=J.undefined, _c=J.undefined, _rvol=J.undefined, *_args):
        if (J.ge(_rvol, rvolThreshold) and J.truthy(hasLargeBody(_o, _h, _l, _c))):
            return (bullishColor if J.gt(_c, _o) else bearishColor)
        return None
    candleColors = G_for_every(G_open, G_high, G_low, G_close, myRVOL, _f1)
    G_color_candles(candleColors)
    def _f2(_o=J.undefined, _h=J.undefined, _l=J.undefined, _c=J.undefined, _rvol=J.undefined, *_args):
        return (hasLargeBody(_o, _h, _l, _c) if J.truthy(_t1 := (J.ge(_rvol, rvolThreshold) if J.truthy(_t2 := J.gt(_c, _o)) else _t2)) else _t1)
    bullishSignal = G_for_every(G_open, G_high, G_low, G_close, myRVOL, _f2)
    G_register_signal(bullishSignal, "Bullish Volume-Driven Momentum")
    def _f3(_o=J.undefined, _h=J.undefined, _l=J.undefined, _c=J.undefined, _rvol=J.undefined, *_args):
        return (hasLargeBody(_o, _h, _l, _c) if J.truthy(_t1 := (J.ge(_rvol, rvolThreshold) if J.truthy(_t2 := J.gt(_o, _c)) else _t2)) else _t1)
    bearishSignal = G_for_every(G_open, G_high, G_low, G_close, myRVOL, _f3)
    G_register_signal(bearishSignal, "Bearish Volume-Driven Momentum")


register_store_indicator(
    script,
    name='volume_driven_momentum_TS',
    title='Volume-Driven Momentum',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/volume-driven-momentum/',
    position='price',
    inputs=[{'id': 'rvol_threshold', 'title': 'RVOL Threshold', 'type': 'number', 'default': 2}, {'id': 'rvol_lookback_period', 'title': 'RVOL Lookback Period', 'type': 'number', 'default': 20}, {'id': 'bullish_candle_color', 'title': 'Bullish Candle Color', 'type': 'color', 'default': 'cyan'}, {'id': 'bearish_candle_color', 'title': 'Bearish Candle Color', 'type': 'color', 'default': '#FF69B4'}],
    outputs=['cdl', 'bullish_volume_driven_momentum', 'bearish_volume_driven_momentum'],
    signals=['bullish_volume_driven_momentum', 'bearish_volume_driven_momentum'],
    requires=[],
    parity='exact',
)
