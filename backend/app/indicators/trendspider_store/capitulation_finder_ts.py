"""
Capitulation Finder -- TrendSpider store indicator by TrendSpider.

Registered as "capitulation_finder_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6877dd-capitulation-finder/)
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
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_indicators = G["indicators"]
    G_input = G["input"]
    G_register_signal = G["register_signal"]
    G_rsi = G["rsi"]
    G_sma = G["sma"]
    G_volume = G["volume"]
    G_describe_indicator("Capitulation Finder")
    rsiLength = J.get(G_input, "number")("RSI Length", 14, J.obj(("min", 1)))
    rsiOversold = J.get(G_input, "number")("RSI Oversold Level", 30, J.obj(("min", 1), ("max", 100)))
    rsiOverbought = J.get(G_input, "number")("RSI Overbought Level", 70, J.obj(("min", 1), ("max", 100)))
    maType = J.get(G_input, "select")("Moving Average Type", "sma", J.get(G_constants, "ma_types"))
    maLength = J.get(G_input, "number")("Moving Average Length", 50, J.obj(("min", 1)))
    percentageThreshold = J.get(G_input, "number")("Distance from MA (%)", 5, J.obj(("min", 1), ("max", 100)))
    volumeMultiplier = J.get(G_input, "number")("Volume Multiplier", 1.2, J.obj(("min", 1)))
    volumeLength = J.get(G_input, "number")("Volume Average Length", 20, J.obj(("min", 1)))
    myRsi = G_rsi(G_close, rsiLength)
    myMa = J.get(G_indicators, maType)(G_close, maLength)
    myVolumeAvg = G_sma(G_volume, volumeLength)
    def _f1(r=J.undefined, c=J.undefined, m=J.undefined, v=J.undefined, va=J.undefined, *_args):
        return (J.ge(v, J.mul(va, volumeMultiplier)) if J.truthy(_t1 := (J.lt(c, J.mul(m, J.sub(1, J.div(percentageThreshold, 100)))) if J.truthy(_t2 := J.le(r, rsiOversold)) else _t2)) else _t1)
    myOversoldConditions = G_for_every(myRsi, G_close, myMa, G_volume, myVolumeAvg, _f1)
    def _f2(r=J.undefined, c=J.undefined, m=J.undefined, v=J.undefined, va=J.undefined, *_args):
        return (J.ge(v, J.mul(va, volumeMultiplier)) if J.truthy(_t1 := (J.gt(c, J.mul(m, J.add(1, J.div(percentageThreshold, 100)))) if J.truthy(_t2 := J.ge(r, rsiOverbought)) else _t2)) else _t1)
    myOverboughtConditions = G_for_every(myRsi, G_close, myMa, G_volume, myVolumeAvg, _f2)
    def _f3(r=J.undefined, v=J.undefined, va=J.undefined, *_args):
        return (J.ge(v, J.mul(va, volumeMultiplier)) if J.truthy(_t1 := J.le(r, rsiOversold)) else _t1)
    myOversoldConfirmation = G_for_every(myRsi, G_volume, myVolumeAvg, _f3)
    def _f4(r=J.undefined, v=J.undefined, va=J.undefined, *_args):
        return (J.ge(v, J.mul(va, volumeMultiplier)) if J.truthy(_t1 := J.ge(r, rsiOverbought)) else _t1)
    myOverboughtConfirmation = G_for_every(myRsi, G_volume, myVolumeAvg, _f4)
    def _f5(oversold=J.undefined, overbought=J.undefined, *_args):
        return ("#39FF14" if J.truthy(oversold) else ("#FF3131" if J.truthy(overbought) else "#808080"))
    myColors = G_for_every(myOversoldConditions, myOverboughtConditions, _f5)
    G_color_candles(myColors)
    G_register_signal(myOversoldConditions, "Bullish Capitulation")
    G_register_signal(myOverboughtConditions, "Bearish Capitulation")
    def _f6(o=J.undefined, b=J.undefined, *_args):
        return ((not J.truthy(b)) if J.truthy(_t1 := (not J.truthy(o))) else _t1)
    G_register_signal(G_for_every(myOversoldConditions, myOverboughtConditions, _f6), "No Capitulation")
    G_register_signal(myOversoldConfirmation, "Oversold Confirmation")
    G_register_signal(myOverboughtConfirmation, "Overbought Confirmation")


register_store_indicator(
    script,
    name='capitulation_finder_TS',
    title='Capitulation Finder',
    developer='TrendSpider',
    url='https://trendspider.com/trading-tools-store/indicators/6877dd-capitulation-finder/',
    position='price',
    inputs=[{'id': 'rsi_length', 'title': 'RSI Length', 'type': 'number', 'default': 14}, {'id': 'rsi_oversold_level', 'title': 'RSI Oversold Level', 'type': 'number', 'default': 30}, {'id': 'rsi_overbought_level', 'title': 'RSI Overbought Level', 'type': 'number', 'default': 70}, {'id': 'moving_average_type', 'title': 'Moving Average Type', 'type': 'select_wide', 'default': 'sma', 'options': ['ema', 'sma', 'wildma', 'vwma', 'wma', 'hullma', 'kama', 'alma', 'twap']}, {'id': 'moving_average_length', 'title': 'Moving Average Length', 'type': 'number', 'default': 50}, {'id': 'distance_from_ma____', 'title': 'Distance from MA (%)', 'type': 'number', 'default': 5}, {'id': 'volume_multiplier', 'title': 'Volume Multiplier', 'type': 'number', 'default': 1.2}, {'id': 'volume_average_length', 'title': 'Volume Average Length', 'type': 'number', 'default': 20}],
    outputs=['cdl', 'bullish_capitulation', 'bearish_capitulation', 'no_capitulation', 'oversold_confirmation', 'overbought_confirmation'],
    signals=['bullish_capitulation', 'bearish_capitulation', 'no_capitulation', 'oversold_confirmation', 'overbought_confirmation'],
    requires=[],
    parity='exact',
)
