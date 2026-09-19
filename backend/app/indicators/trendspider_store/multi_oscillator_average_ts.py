"""
Multi-Oscillator Average -- TrendSpider store indicator by QXEM.

Registered as "multi_oscillator_average_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/689623-multi-oscillator-average/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_add = G["add"]
    G_cci = G["cci"]
    G_close = G["close"]
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_div = G["div"]
    G_ema = G["ema"]
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_hlc3 = G["hlc3"]
    G_indicators = G["indicators"]
    G_input = G["input"]
    G_low = G["low"]
    G_mfi = G["mfi"]
    G_mult = G["mult"]
    G_paint = G["paint"]
    G_rsi = G["rsi"]
    G_stdev = G["stdev"]
    G_stochastic = G["stochastic"]
    G_sub = G["sub"]
    G_volume = G["volume"]
    G_describe_indicator("Multi-Oscillator Average", "lower")
    rsiLength = J.get(G_input, "number")("RSI Length", 14, J.obj(("min", 1)))
    macdFastLength = J.get(G_input, "number")("MACD Fast Length", 12, J.obj(("min", 1)))
    macdSlowLength = J.get(G_input, "number")("MACD Slow Length", 26, J.obj(("min", 1)))
    macdSignalLength = J.get(G_input, "number")("MACD Signal Length", 9, J.obj(("min", 1)))
    ppoFastLength = J.get(G_input, "number")("PPO Fast Length", 12, J.obj(("min", 1)))
    ppoSlowLength = J.get(G_input, "number")("PPO Slow Length", 26, J.obj(("min", 1)))
    ppoSignalLength = J.get(G_input, "number")("PPO Signal Length", 9, J.obj(("min", 1)))
    cciLength = J.get(G_input, "number")("CCI Length", 20, J.obj(("min", 1)))
    mfiLength = J.get(G_input, "number")("MFI Length", 14, J.obj(("min", 1)))
    dssLength = J.get(G_input, "number")("DSS Blau Length", 13, J.obj(("min", 1)))
    dssStochLength = J.get(G_input, "number")("DSS Blau Stochastic Length", 8, J.obj(("min", 1)))
    dssMaType = J.get(G_input, "select")("DSS Blau MA Type", "ema", J.get(G_constants, "ma_types"))
    multiOscMaLength = J.get(G_input, "number")("Multi-Oscillator MA Length", 9, J.obj(("min", 1)))
    multiOscMaType = J.get(G_input, "select")("Multi-Oscillator MA Type", "sma", J.get(G_constants, "ma_types"))
    stdDevMultiplier = J.get(G_input, "number")("Std Dev Band Multiplier", 2, J.obj(("min", 0.1), ("max", 5), ("step", 0.1)))
    myRsi = G_rsi(G_close, rsiLength)
    myMacd = G_sub(G_sub(G_ema(G_close, macdFastLength), G_ema(G_close, macdSlowLength)), G_ema(G_sub(G_ema(G_close, macdFastLength), G_ema(G_close, macdSlowLength)), macdSignalLength))
    myPpo = G_sub(G_div(G_sub(G_ema(G_close, ppoFastLength), G_ema(G_close, ppoSlowLength)), G_ema(G_close, ppoSlowLength)), G_ema(G_div(G_sub(G_ema(G_close, ppoFastLength), G_ema(G_close, ppoSlowLength)), G_ema(G_close, ppoSlowLength)), ppoSignalLength))
    myCci = G_cci(G_hlc3, cciLength)
    myMfi = G_mfi(G_hlc3, G_volume, mfiLength)
    computeMA = J.get(G_indicators, dssMaType)
    myStoch = G_stochastic(G_close, G_high, G_low, dssStochLength)
    myDssBlau = computeMA(myStoch, dssLength)
    normalizeRsi = myRsi
    def _f1(m=J.undefined, *_args):
        return J.mul(J.add(m, 2), 25)
    normalizeMacd = G_for_every(myMacd, _f1)
    def _f2(p=J.undefined, *_args):
        return J.mul(J.add(p, 4), 12.5)
    normalizePpo = G_for_every(myPpo, _f2)
    def _f3(c=J.undefined, *_args):
        return J.div(J.add(c, 200), 4)
    normalizeCci = G_for_every(myCci, _f3)
    normalizeMfi = myMfi
    normalizeDssBlau = myDssBlau
    myMultiOscillator = G_div(G_add(normalizeRsi, normalizeMacd, normalizePpo, normalizeCci, normalizeMfi, normalizeDssBlau), 6)
    computeMultiOscMA = J.get(G_indicators, multiOscMaType)
    myMultiOscillatorMA = computeMultiOscMA(myMultiOscillator, multiOscMaLength)
    myStdDev = G_stdev(myMultiOscillator, multiOscMaLength)
    myUpperBand = G_add(myMultiOscillatorMA, G_mult(myStdDev, stdDevMultiplier))
    myLowerBand = G_sub(myMultiOscillatorMA, G_mult(myStdDev, stdDevMultiplier))
    overboughtLevel = 70
    oversoldLevel = 30
    G_paint(myMultiOscillator, J.obj(("name", "Multi-Oscillator Average"), ("color", "#fff49b"), ("thickness", 2)))
    G_paint(myMultiOscillatorMA, J.obj(("name", "Multi-Oscillator MA"), ("color", "#cccccc"), ("style", "dotted")))
    G_paint(myUpperBand, J.obj(("name", "Upper Std Dev Band"), ("color", "#cccccc"), ("style", "ladder")))
    G_paint(myLowerBand, J.obj(("name", "Lower Std Dev Band"), ("color", "#cccccc"), ("style", "ladder")))


register_store_indicator(
    script,
    name='multi_oscillator_average_TS',
    title='Multi-Oscillator Average',
    developer='QXEM',
    url='https://trendspider.com/trading-tools-store/indicators/689623-multi-oscillator-average/',
    position='lower',
    inputs=[{'id': 'rsi_length', 'title': 'RSI Length', 'type': 'number', 'default': 14}, {'id': 'macd_fast_length', 'title': 'MACD Fast Length', 'type': 'number', 'default': 12}, {'id': 'macd_slow_length', 'title': 'MACD Slow Length', 'type': 'number', 'default': 26}, {'id': 'macd_signal_length', 'title': 'MACD Signal Length', 'type': 'number', 'default': 9}, {'id': 'ppo_fast_length', 'title': 'PPO Fast Length', 'type': 'number', 'default': 12}, {'id': 'ppo_slow_length', 'title': 'PPO Slow Length', 'type': 'number', 'default': 26}, {'id': 'ppo_signal_length', 'title': 'PPO Signal Length', 'type': 'number', 'default': 9}, {'id': 'cci_length', 'title': 'CCI Length', 'type': 'number', 'default': 20}, {'id': 'mfi_length', 'title': 'MFI Length', 'type': 'number', 'default': 14}, {'id': 'dss_blau_length', 'title': 'DSS Blau Length', 'type': 'number', 'default': 13}, {'id': 'dss_blau_stochastic_length', 'title': 'DSS Blau Stochastic Length', 'type': 'number', 'default': 8}, {'id': 'dss_blau_ma_type', 'title': 'DSS Blau MA Type', 'type': 'select_wide', 'default': 'ema', 'options': ['ema', 'sma', 'wildma', 'vwma', 'wma', 'hullma', 'kama', 'alma', 'twap']}, {'id': 'multi_oscillator_ma_length', 'title': 'Multi-Oscillator MA Length', 'type': 'number', 'default': 9}, {'id': 'multi_oscillator_ma_type', 'title': 'Multi-Oscillator MA Type', 'type': 'select_wide', 'default': 'sma', 'options': ['ema', 'sma', 'wildma', 'vwma', 'wma', 'hullma', 'kama', 'alma', 'twap']}, {'id': 'std_dev_band_multiplier', 'title': 'Std Dev Band Multiplier', 'type': 'number', 'default': 2}],
    outputs=['multi_oscillator_average', 'multi_oscillator_ma', 'upper_std_dev_band', 'lower_std_dev_band'],
    signals=[],
    requires=[],
    parity='exact',
)
