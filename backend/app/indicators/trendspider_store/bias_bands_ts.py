"""
Bias Bands -- TrendSpider store indicator by Longinus.

Registered as "bias_bands_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/689db6-bias-bands/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_add = G["add"]
    G_atr = G["atr"]
    G_close = G["close"]
    G_color_candles = G["color_candles"]
    G_describe_indicator = G["describe_indicator"]
    G_div = G["div"]
    G_ema = G["ema"]
    G_for_every = G["for_every"]
    G_input = G["input"]
    G_mult = G["mult"]
    G_paint = G["paint"]
    G_plot = G["plot"]
    G_register_signal = G["register_signal"]
    G_series_of = G["series_of"]
    G_sma = G["sma"]
    G_sub = G["sub"]
    G_volume = G["volume"]
    G_describe_indicator("Bias Bands", "price", J.obj(("warmup", 300)))
    lenEMA = J.get(G_input, "number")("Baseline EMA length", 34, J.obj(("min", 1), ("max", 500)))
    lenATR = J.get(G_input, "number")("ATR length", 14, J.obj(("min", 1), ("max", 500)))
    bandHalf = J.get(G_input, "number")("Band 1 (±0.5 ATR)", 0.5, J.obj(("step", 0.1), ("min", 0)))
    bandOne = J.get(G_input, "number")("Band 2 (±1.0 ATR)", 1, J.obj(("step", 0.1), ("min", 0)))
    bandOneHalf = J.get(G_input, "number")("Band 3 (±1.5 ATR)", 1.5, J.obj(("step", 0.1), ("min", 0)))
    rvolLookback = J.get(G_input, "number")("RVOL lookback", 20, J.obj(("min", 1)))
    rvolThreshold = J.get(G_input, "number")("RVOL threshold", 1.3, J.obj(("min", 1), ("step", 0.01)))
    useRvolSMA = J.get(G_input, "boolean")("Smooth RVOL with SMA(3)", True)
    minRvolFloor = J.get(G_input, "number")("Min RVOL floor", 1.05, J.obj(("min", 1), ("step", 0.01)))
    showHalfBands = J.get(G_input, "boolean")("Show ±0.5 ATR & ±1.5 ATR lines", False)
    showSignals = J.get(G_input, "boolean")("Show chart signal markers", True)
    colorCandles = J.get(G_input, "boolean")("Color candles by bias", True)
    fadeBars = J.get(G_input, "number")("Bias color fade length (bars)", 2, J.obj(("min", 0), ("max", 5)))
    showRVOLplot = J.get(G_input, "boolean")("Show RVOL debug plot", False)
    colStrongBull = J.get(G_input, "color")("Color - Strong Bull candle", "#0f9d58")
    colBull = J.get(G_input, "color")("Color - Bull candle", "#66bb6a")
    colNeutral = J.get(G_input, "color")("Color - Neutral candle", "#9e9e9e")
    colBear = J.get(G_input, "color")("Color - Bear candle", "#ef5350")
    colStrongBear = J.get(G_input, "color")("Color - Strong Bear candle", "#c62828")
    colFade = J.get(G_input, "color")("Color - Bias fade", "#bdbdbd")
    colBaseline = J.get(G_input, "color")("Color - Baseline line", "#1565c0")
    colPosRef = J.get(G_input, "color")("Color - Plus 1.0 ATR line", "#42a5f5")
    colNegRef = J.get(G_input, "color")("Color - Minus 1.0 ATR line", "#ff7043")
    base = G_ema(G_close, lenEMA)
    tr = G_atr(lenATR)
    bH_u = G_add(base, G_mult(tr, bandHalf))
    b1_u = G_add(base, G_mult(tr, bandOne))
    b3_u = G_add(base, G_mult(tr, bandOneHalf))
    bH_d = G_sub(base, G_mult(tr, bandHalf))
    b1_d = G_sub(base, G_mult(tr, bandOne))
    b3_d = G_sub(base, G_mult(tr, bandOneHalf))
    baseAvg2 = G_sma(base, 2)
    def _f1(b=J.undefined, m=J.undefined, *_args):
        return J.gt(b, m)
    baseRising = G_for_every(base, baseAvg2, _f1)
    rawRvol = G_div(G_volume, G_sma(G_volume, rvolLookback))
    rvolEff = (G_sma(rawRvol, 3) if J.truthy(useRvolSMA) else rawRvol)
    effThresh = (rvolThreshold if J.gt(rvolThreshold, minRvolFloor) else minRvolFloor)
    def _f2(rv=J.undefined, th=J.undefined, *_args):
        return J.ge(rv, th)
    rvolOK = G_for_every(rvolEff, G_series_of(effThresh), _f2)
    lastState = 0
    def _f3(c=J.undefined, _b3u=J.undefined, _b1u=J.undefined, _b1d=J.undefined, _b3d=J.undefined, *_args):
        nonlocal lastState
        state = J.undefined
        if J.ge(c, _b3u):
            state = 5
        elif J.ge(c, _b1u):
            state = 4
        elif J.le(c, _b3d):
            state = 1
        elif J.le(c, _b1d):
            state = 2
        else:
            state = 3
        if (J.gt(fadeBars, 0) and J.sne(state, lastState)):
            lastState = state
            return colFade
        lastState = state
        _t1 = state
        if J.seq(_t1, 5):
            _t2 = 0
        elif J.seq(_t1, 4):
            _t2 = 1
        elif J.seq(_t1, 1):
            _t2 = 2
        elif J.seq(_t1, 2):
            _t2 = 3
        else:
            _t2 = 4
        _c3 = False
        for _once in (0,):
            if _t2 <= 0:
                return colStrongBull
            if _t2 <= 1:
                return colBull
            if _t2 <= 2:
                return colStrongBear
            if _t2 <= 3:
                return colBear
            if _t2 <= 4:
                return colNeutral
            pass
    candleColors = G_for_every(G_close, b3_u, b1_u, b1_d, b3_d, _f3)
    if J.truthy(colorCandles):
        G_color_candles(candleColors)
    G_paint(base, J.obj(("name", "BiasBand Baseline"), ("color", colBaseline), ("thickness", 2)))
    G_paint(b1_u, J.obj(("name", "BiasBand +1.0x Up"), ("color", colPosRef), ("thickness", 2)))
    G_paint(b1_d, J.obj(("name", "BiasBand -1.0x Down"), ("color", colNegRef), ("thickness", 2)))
    G_paint((bH_u if J.truthy(showHalfBands) else G_series_of(None)), J.obj(("name", "BiasBand +0.5x Up"), ("color", "#64b5f6")))
    G_paint((b3_u if J.truthy(showHalfBands) else G_series_of(None)), J.obj(("name", "BiasBand +1.5x Up"), ("color", "#1e88e5")))
    G_paint((bH_d if J.truthy(showHalfBands) else G_series_of(None)), J.obj(("name", "BiasBand -0.5x Down"), ("color", "#ffab91")))
    G_paint((b3_d if J.truthy(showHalfBands) else G_series_of(None)), J.obj(("name", "BiasBand -1.5x Down"), ("color", "#f4511e")))
    def _f4(c=J.undefined, u=J.undefined, rising=J.undefined, rvok=J.undefined, *_args):
        return ((not (not J.truthy(rvok))) if J.truthy(_t1 := ((not (not J.truthy(rising))) if J.truthy(_t2 := J.gt(c, u)) else _t2)) else _t1)
    longTrigger = G_for_every(G_close, b1_u, baseRising, rvolOK, _f4)
    def _f5(c=J.undefined, m=J.undefined, rising=J.undefined, *_args):
        return ((not J.truthy(rising)) if J.truthy(_t1 := J.lt(c, m)) else _t1)
    exitTrend = G_for_every(G_close, base, baseRising, _f5)
    def _f6(c=J.undefined, d=J.undefined, rvok=J.undefined, *_args):
        return ((not (not J.truthy(rvok))) if J.truthy(_t1 := J.le(c, d)) else _t1)
    exitPanic = G_for_every(G_close, bH_d, rvolOK, _f6)
    G_register_signal(longTrigger, "BIAS LONG")
    G_register_signal(exitTrend, "BIAS EXIT")
    G_register_signal(exitPanic, "BIAS EXIT_PANIC")
    if J.truthy(showRVOLplot):
        G_plot(rvolEff, J.obj(("name", "RVOL"), ("color", "#ffa000")))
        G_plot(G_series_of(effThresh), J.obj(("name", "RVOL Threshold"), ("color", "#f4511e")))


register_store_indicator(
    script,
    name='bias_bands_TS',
    title='Bias Bands',
    developer='Longinus',
    url='https://trendspider.com/trading-tools-store/indicators/689db6-bias-bands/',
    position='price',
    inputs=[{'id': 'warmup', 'title': 'Warmup', 'type': 'number', 'default': 300}, {'id': 'baseline_ema_length', 'title': 'Baseline EMA length', 'type': 'number', 'default': 34}, {'id': 'atr_length', 'title': 'ATR length', 'type': 'number', 'default': 14}, {'id': 'band_1___0_5_atr_', 'title': 'Band 1 (±0.5 ATR)', 'type': 'number', 'default': 0.5}, {'id': 'band_2___1_0_atr_', 'title': 'Band 2 (±1.0 ATR)', 'type': 'number', 'default': 1}, {'id': 'band_3___1_5_atr_', 'title': 'Band 3 (±1.5 ATR)', 'type': 'number', 'default': 1.5}, {'id': 'rvol_lookback', 'title': 'RVOL lookback', 'type': 'number', 'default': 20}, {'id': 'rvol_threshold', 'title': 'RVOL threshold', 'type': 'number', 'default': 1.3}, {'id': 'smooth_rvol_with_sma_3_', 'title': 'Smooth RVOL with SMA(3)', 'type': 'boolean', 'default': True}, {'id': 'min_rvol_floor', 'title': 'Min RVOL floor', 'type': 'number', 'default': 1.05}, {'id': 'show__0_5_atr____1_5_atr_lines', 'title': 'Show ±0.5 ATR & ±1.5 ATR lines', 'type': 'boolean', 'default': False}, {'id': 'show_chart_signal_markers', 'title': 'Show chart signal markers', 'type': 'boolean', 'default': True}, {'id': 'color_candles_by_bias', 'title': 'Color candles by bias', 'type': 'boolean', 'default': True}, {'id': 'bias_color_fade_length__bars_', 'title': 'Bias color fade length (bars)', 'type': 'number', 'default': 2}, {'id': 'show_rvol_debug_plot', 'title': 'Show RVOL debug plot', 'type': 'boolean', 'default': False}, {'id': 'color___strong_bull_candle', 'title': 'Color - Strong Bull candle', 'type': 'color', 'default': '#0f9d58'}, {'id': 'color___bull_candle', 'title': 'Color - Bull candle', 'type': 'color', 'default': '#66bb6a'}, {'id': 'color___neutral_candle', 'title': 'Color - Neutral candle', 'type': 'color', 'default': '#9e9e9e'}, {'id': 'color___bear_candle', 'title': 'Color - Bear candle', 'type': 'color', 'default': '#ef5350'}, {'id': 'color___strong_bear_candle', 'title': 'Color - Strong Bear candle', 'type': 'color', 'default': '#c62828'}, {'id': 'color___bias_fade', 'title': 'Color - Bias fade', 'type': 'color', 'default': '#bdbdbd'}, {'id': 'color___baseline_line', 'title': 'Color - Baseline line', 'type': 'color', 'default': '#1565c0'}, {'id': 'color___plus_1_0_atr_line', 'title': 'Color - Plus 1.0 ATR line', 'type': 'color', 'default': '#42a5f5'}, {'id': 'color___minus_1_0_atr_line', 'title': 'Color - Minus 1.0 ATR line', 'type': 'color', 'default': '#ff7043'}],
    outputs=['cdl', 'biasband_baseline', 'biasband__1_0x_up', 'biasband__1_0x_down', 'biasband__0_5x_up', 'biasband__1_5x_up', 'biasband__0_5x_down', 'biasband__1_5x_down', 'bias_long', 'bias_exit', 'bias_exit_panic'],
    signals=['bias_long', 'bias_exit', 'bias_exit_panic'],
    requires=[],
    parity='exact',
)
