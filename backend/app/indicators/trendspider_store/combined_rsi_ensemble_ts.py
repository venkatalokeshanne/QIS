"""
Combined RSI Ensemble -- TrendSpider store indicator by TrendSpider Team.

Registered as "combined_rsi_ensemble_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/combined-rsi-ensemble/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_add = G["add"]
    G_close = G["close"]
    G_color_candles = G["color_candles"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_input = G["input"]
    G_register_signal = G["register_signal"]
    G_rsi = G["rsi"]
    G_describe_indicator("Combined RSI Ensemble")
    OVERBOUGHT_LEVEL = J.get(G_input, "number")("Overbought Level", 80, J.obj(("min", 50), ("max", 100)))
    OVERSOLD_LEVEL = J.get(G_input, "number")("Oversold Level", 30, J.obj(("min", 0), ("max", 50)))
    COLOR_SURELY_OVERBOUGHT = J.get(G_input, "color")("Surely Overbought Color", "#ff0000")
    COLOR_PROBABLY_OVERBOUGHT = J.get(G_input, "color")("Probably Overbought Color", "#ffa500")
    COLOR_SLIGHTLY_OVERBOUGHT = J.get(G_input, "color")("Slightly Overbought Color", "#ffff00")
    COLOR_SURELY_OVERSOLD = J.get(G_input, "color")("Surely Oversold Color", "#00ff3c")
    COLOR_PROBABLY_OVERSOLD = J.get(G_input, "color")("Probably Oversold Color", "#2ecc53")
    COLOR_SLIGHTLY_OVERSOLD = J.get(G_input, "color")("Slightly Oversold Color", "#c4e0a3")
    COLOR_NEUTRAL = J.get(G_input, "color")("Neutral Color", "gray")
    rsi14 = G_rsi(G_close, 14)
    rsi9 = G_rsi(G_close, 9)
    rsi5 = G_rsi(G_close, 5)
    def scoreRSI(rsi=J.undefined, threshold=J.undefined, isOverbought=J.undefined, *_args):
        def _f1(r=J.undefined, *_args):
            return ((1 if J.gt(r, threshold) else 0) if J.truthy(isOverbought) else (1 if J.lt(r, threshold) else 0))
        return G_for_every(rsi, _f1)
    overboughtScore = G_add(scoreRSI(rsi14, OVERBOUGHT_LEVEL, True), scoreRSI(rsi9, OVERBOUGHT_LEVEL, True), scoreRSI(rsi5, OVERBOUGHT_LEVEL, True))
    oversoldScore = G_add(scoreRSI(rsi14, OVERSOLD_LEVEL, False), scoreRSI(rsi9, OVERSOLD_LEVEL, False), scoreRSI(rsi5, OVERSOLD_LEVEL, False))
    def _f1(ob=J.undefined, os=J.undefined, *_args):
        if J.gt(os, 0):
            return (COLOR_SURELY_OVERSOLD if J.seq(os, 3) else (COLOR_PROBABLY_OVERSOLD if J.seq(os, 2) else COLOR_SLIGHTLY_OVERSOLD))
        elif J.gt(ob, 0):
            return (COLOR_SURELY_OVERBOUGHT if J.seq(ob, 3) else (COLOR_PROBABLY_OVERBOUGHT if J.seq(ob, 2) else COLOR_SLIGHTLY_OVERBOUGHT))
        return COLOR_NEUTRAL
    candleColors = G_for_every(overboughtScore, oversoldScore, _f1)
    G_color_candles(candleColors)
    def _f2(s=J.undefined, *_args):
        return J.seq(s, 3)
    mySurelyOverbought = G_for_every(overboughtScore, _f2)
    def _f3(s=J.undefined, *_args):
        return J.seq(s, 2)
    myProbablyOverbought = G_for_every(overboughtScore, _f3)
    def _f4(s=J.undefined, *_args):
        return J.seq(s, 1)
    mySlightlyOverbought = G_for_every(overboughtScore, _f4)
    def _f5(s=J.undefined, *_args):
        return J.seq(s, 3)
    mySurelyOversold = G_for_every(oversoldScore, _f5)
    def _f6(s=J.undefined, *_args):
        return J.seq(s, 2)
    myProbablyOversold = G_for_every(oversoldScore, _f6)
    def _f7(s=J.undefined, *_args):
        return J.seq(s, 1)
    mySlightlyOversold = G_for_every(oversoldScore, _f7)
    def _f8(ob=J.undefined, os=J.undefined, *_args):
        return (J.seq(os, 0) if J.truthy(_t1 := J.seq(ob, 0)) else _t1)
    myNeutral = G_for_every(overboughtScore, oversoldScore, _f8)
    G_register_signal(mySurelyOverbought, "Surely Overbought")
    G_register_signal(myProbablyOverbought, "Probably Overbought")
    G_register_signal(mySlightlyOverbought, "Slightly Overbought")
    G_register_signal(mySurelyOversold, "Surely Oversold")
    G_register_signal(myProbablyOversold, "Probably Oversold")
    G_register_signal(mySlightlyOversold, "Slightly Oversold")
    G_register_signal(myNeutral, "Neutral")


register_store_indicator(
    script,
    name='combined_rsi_ensemble_TS',
    title='Combined RSI Ensemble',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/combined-rsi-ensemble/',
    position='price',
    inputs=[{'id': 'overbought_level', 'title': 'Overbought Level', 'type': 'number', 'default': 80}, {'id': 'oversold_level', 'title': 'Oversold Level', 'type': 'number', 'default': 30}, {'id': 'surely_overbought_color', 'title': 'Surely Overbought Color', 'type': 'color', 'default': '#ff0000'}, {'id': 'probably_overbought_color', 'title': 'Probably Overbought Color', 'type': 'color', 'default': '#ffa500'}, {'id': 'slightly_overbought_color', 'title': 'Slightly Overbought Color', 'type': 'color', 'default': '#ffff00'}, {'id': 'surely_oversold_color', 'title': 'Surely Oversold Color', 'type': 'color', 'default': '#00ff3c'}, {'id': 'probably_oversold_color', 'title': 'Probably Oversold Color', 'type': 'color', 'default': '#2ecc53'}, {'id': 'slightly_oversold_color', 'title': 'Slightly Oversold Color', 'type': 'color', 'default': '#c4e0a3'}, {'id': 'neutral_color', 'title': 'Neutral Color', 'type': 'color', 'default': 'gray'}],
    outputs=['cdl', 'surely_overbought', 'probably_overbought', 'slightly_overbought', 'surely_oversold', 'probably_oversold', 'slightly_oversold', 'neutral'],
    signals=['surely_overbought', 'probably_overbought', 'slightly_overbought', 'surely_oversold', 'probably_oversold', 'slightly_oversold', 'neutral'],
    requires=[],
    parity='exact',
)
