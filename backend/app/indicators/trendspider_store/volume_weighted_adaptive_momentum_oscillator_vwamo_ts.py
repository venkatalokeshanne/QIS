"""
Volume-Weighted Adaptive Momentum Oscillator (VWAMO) -- TrendSpider store indicator by Aliu Kehinde.

Registered as "volume_weighted_adaptive_momentum_oscillator_vwamo_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68aa6e-volume-weighted-adaptive-momentum-oscillator-vwamo/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_atr = G["atr"]
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_input = G["input"]
    G_paint = G["paint"]
    G_paint_overlay = G["paint_overlay"]
    G_register_signal = G["register_signal"]
    G_series_of = G["series_of"]
    G_sma = G["sma"]
    G_volume = G["volume"]
    G_describe_indicator("Volume-Weighted Adaptive Momentum Oscillator (VWAMO)", "lower", J.obj(("shortName", "VWAMO")))
    momPeriod = J.get(G_input, "number")("Momentum Period", 14, J.obj(("min", 5), ("max", 30), ("step", 1)))
    volMultiplier = J.get(G_input, "number")("Volume Multiplier", 1.5, J.obj(("min", 0.5), ("max", 3), ("step", 0.1)))
    atrPeriod = J.get(G_input, "number")("ATR Period", 20, J.obj(("min", 10), ("max", 50), ("step", 1)))
    bandTightness = J.get(G_input, "number")("Band Tightness", 2, J.obj(("min", 1), ("max", 3), ("step", 0.1)))
    oscColor = "#5D3FD3"
    volColor = "#787B86"
    upperBandColor = "#F23645"
    lowerBandColor = "#089981"
    buySignalColor = "#089981"
    sellSignalColor = "#F23645"
    def _f1(c=J.undefined, i=J.undefined, *_args):
        if J.lt(i, momPeriod):
            return None
        pastClose = J.get(G_close, J.sub(i, momPeriod))
        if ((pastClose is None) or (c is None)):
            return None
        return J.mul(J.div(J.sub(c, pastClose), pastClose), 100)
    myMomentum = G_for_every(G_close, _f1)
    smoothMomentum = G_sma(myMomentum, 3)
    avgVolume = G_sma(G_volume, 20)
    def _f2(vol=J.undefined, avg=J.undefined, *_args):
        if (((vol is None) or (avg is None)) or J.seq(avg, 0)):
            return 1
        return J.get(G_Math, "min")(2, J.get(G_Math, "max")(0.5, J.mul(J.div(vol, avg), volMultiplier)))
    volumeRatio = G_for_every(G_volume, avgVolume, _f2)
    def _f3(mom=J.undefined, ratio=J.undefined, *_args):
        if ((mom is None) or (ratio is None)):
            return None
        return J.mul(mom, ratio)
    volumeWeightedMomentum = G_for_every(smoothMomentum, volumeRatio, _f3)
    atrValues = G_atr(atrPeriod)
    def _f4(atrVal=J.undefined, c=J.undefined, *_args):
        if (((atrVal is None) or (c is None)) or J.seq(c, 0)):
            return 1
        return J.mul(J.div(atrVal, c), 100)
    atrPercent = G_for_every(atrValues, G_close, _f4)
    avgAtrPercent = G_sma(atrPercent, 20)
    def _f5(val=J.undefined, *_args):
        if (val is None):
            return 20
        return J.add(30, J.mul(val, bandTightness))
    dynamicUpper = G_for_every(avgAtrPercent, _f5)
    def _f6(val=J.undefined, *_args):
        if (val is None):
            return (-20)
        return J.sub((-30), J.mul(val, bandTightness))
    dynamicLower = G_for_every(avgAtrPercent, _f6)
    bullSignal = G_series_of(False)
    bearSignal = G_series_of(False)
    i = 1
    while J.lt(i, J.get(volumeWeightedMomentum, "length")):
        currentMom = J.get(volumeWeightedMomentum, i)
        prevMom = J.get(volumeWeightedMomentum, J.sub(i, 1))
        currentUpper = J.get(dynamicUpper, i)
        currentLower = J.get(dynamicLower, i)
        currentVolRatio = J.get(volumeRatio, i)
        if (((((currentMom is not None) and (prevMom is not None)) and (currentUpper is not None)) and (currentLower is not None)) and (currentVolRatio is not None)):
            if ((J.lt(prevMom, currentLower) and J.ge(currentMom, currentLower)) and J.gt(currentVolRatio, 1)):
                J.set(bullSignal, i, True)
            if ((J.gt(prevMom, currentUpper) and J.le(currentMom, currentUpper)) and J.gt(currentVolRatio, 1)):
                J.set(bearSignal, i, True)
        i = J.inc(i)
    oscLine = G_paint(volumeWeightedMomentum, J.obj(("name", "VWAMO"), ("color", oscColor), ("thickness", 2)))
    G_paint(dynamicUpper, J.obj(("name", "Upper Band"), ("color", upperBandColor), ("style", "dotted")))
    G_paint(dynamicLower, J.obj(("name", "Lower Band"), ("color", lowerBandColor), ("style", "dotted")))
    G_paint(volumeRatio, J.obj(("name", "Volume Ratio"), ("color", volColor), ("style", "column"), ("thickness", 1), ("hidden", True)))
    G_paint(bullSignal, J.obj(("name", "Buy Signal"), ("color", buySignalColor), ("style", "labels_above")))
    G_paint(bearSignal, J.obj(("name", "Sell Signal"), ("color", sellSignalColor), ("style", "labels_below")))
    G_register_signal(bullSignal, "VWAMO Bullish Signal")
    G_register_signal(bearSignal, "VWAMO Bearish Signal")
    lastMom = J.get(volumeWeightedMomentum, J.sub(J.get(volumeWeightedMomentum, "length"), 1))
    lastUpper = J.get(dynamicUpper, J.sub(J.get(dynamicUpper, "length"), 1))
    lastLower = J.get(dynamicLower, J.sub(J.get(dynamicLower, "length"), 1))
    lastVolRatio = J.get(volumeRatio, J.sub(J.get(volumeRatio, "length"), 1))
    signalText = "Neutral"
    signalColor = "var(--text-color)"
    if (((lastMom is not None) and (lastUpper is not None)) and (lastLower is not None)):
        if J.gt(lastMom, lastUpper):
            signalText = "Overbought"
            signalColor = upperBandColor
        elif J.lt(lastMom, lastLower):
            signalText = "Oversold"
            signalColor = lowerBandColor
    G_paint_overlay("overlay", J.obj(("position", "top_right")), J.obj(("rows", J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", J.template("Signal: ", signalText)), ("color", signalColor), ("border", "solid var(--border-color) 1px"), ("padding", 5)), J.obj(("text", J.template("Momentum: ", (J.get(lastMom, "toFixed")(2) if J.truthy(lastMom) else "N/A"))), ("color", "var(--text-color)"), ("border", "solid var(--border-color) 1px"), ("padding", 5)), J.obj(("text", J.template("Volume: ", (J.add(J.get(J.mul(lastVolRatio, 100), "toFixed")(0), "%") if J.truthy(lastVolRatio) else "N/A"))), ("color", "var(--text-color)"), ("border", "solid var(--border-color) 1px"), ("padding", 5))])))]))))


register_store_indicator(
    script,
    name='volume_weighted_adaptive_momentum_oscillator_vwamo_TS',
    title='Volume-Weighted Adaptive Momentum Oscillator (VWAMO)',
    developer='Aliu Kehinde',
    url='https://trendspider.com/trading-tools-store/indicators/68aa6e-volume-weighted-adaptive-momentum-oscillator-vwamo/',
    position='lower',
    inputs=[{'id': 'momentum_period', 'title': 'Momentum Period', 'type': 'number', 'default': 14}, {'id': 'volume_multiplier', 'title': 'Volume Multiplier', 'type': 'number', 'default': 1.5}, {'id': 'atr_period', 'title': 'ATR Period', 'type': 'number', 'default': 20}, {'id': 'band_tightness', 'title': 'Band Tightness', 'type': 'number', 'default': 2}],
    outputs=['vwamo', 'upper_band', 'lower_band', 'volume_ratio', 'buy_signal', 'sell_signal', 'vwamo_bullish_signal', 'vwamo_bearish_signal'],
    signals=['vwamo_bullish_signal', 'vwamo_bearish_signal'],
    requires=[],
    parity='exact',
)
