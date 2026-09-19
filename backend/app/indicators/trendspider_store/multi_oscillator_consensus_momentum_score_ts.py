"""
Multi-Oscillator Consensus Momentum Score -- TrendSpider store indicator by QXEM.

Registered as "multi_oscillator_consensus_momentum_score_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/682f83-multi-oscillator-consensus-momentum-score/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_add = G["add"]
    G_cci = G["cci"]
    G_close = G["close"]
    G_cmo = G["cmo"]
    G_describe_indicator = G["describe_indicator"]
    G_div = G["div"]
    G_ema = G["ema"]
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_hl2 = G["hl2"]
    G_hlc3 = G["hlc3"]
    G_input = G["input"]
    G_low = G["low"]
    G_mfi = G["mfi"]
    G_mult = G["mult"]
    G_paint = G["paint"]
    G_paint_label_at_line = G["paint_label_at_line"]
    G_register_signal = G["register_signal"]
    G_roc = G["roc"]
    G_rsi = G["rsi"]
    G_sliding_window_function = G["sliding_window_function"]
    G_sma = G["sma"]
    G_stdev = G["stdev"]
    G_stochastic_rsi = G["stochastic_rsi"]
    G_sub = G["sub"]
    G_volume = G["volume"]
    G_describe_indicator("Multi-Oscillator Consensus Momentum Score")
    macdFast = J.get(G_input, "number")("MACD Fast Length", 12, J.obj(("min", 1)))
    macdSlow = J.get(G_input, "number")("MACD Slow Length", 26, J.obj(("min", 1)))
    macdSignal = J.get(G_input, "number")("MACD Signal Length", 9, J.obj(("min", 1)))
    rsiLength = J.get(G_input, "number")("RSI Length", 14, J.obj(("min", 1)))
    ppoFast = J.get(G_input, "number")("PPO Fast Length", 12, J.obj(("min", 1)))
    ppoSlow = J.get(G_input, "number")("PPO Slow Length", 26, J.obj(("min", 1)))
    ppoSignal = J.get(G_input, "number")("PPO Signal Length", 9, J.obj(("min", 1)))
    mfiLength = J.get(G_input, "number")("MFI Length", 14, J.obj(("min", 1)))
    cciLength = J.get(G_input, "number")("CCI Length", 20, J.obj(("min", 1)))
    stochRsiLength = J.get(G_input, "number")("Stoch RSI Length", 14, J.obj(("min", 1)))
    fischerLength = J.get(G_input, "number")("Fischer Length", 9, J.obj(("min", 1)))
    cmoLength = J.get(G_input, "number")("CMO Length", 14, J.obj(("min", 1)))
    kstRoc1 = J.get(G_input, "number")("KST ROC1", 10, J.obj(("min", 1)))
    kstRoc2 = J.get(G_input, "number")("KST ROC2", 15, J.obj(("min", 1)))
    kstRoc3 = J.get(G_input, "number")("KST ROC3", 20, J.obj(("min", 1)))
    kstRoc4 = J.get(G_input, "number")("KST ROC4", 30, J.obj(("min", 1)))
    kstSma1 = J.get(G_input, "number")("KST SMA1", 10, J.obj(("min", 1)))
    kstSma2 = J.get(G_input, "number")("KST SMA2", 10, J.obj(("min", 1)))
    kstSma3 = J.get(G_input, "number")("KST SMA3", 10, J.obj(("min", 1)))
    kstSma4 = J.get(G_input, "number")("KST SMA4", 15, J.obj(("min", 1)))
    kstSignal = J.get(G_input, "number")("KST Signal", 9, J.obj(("min", 1)))
    smLength = J.get(G_input, "number")("Stoch Mom Length", 10, J.obj(("min", 1)))
    smSmoothK = J.get(G_input, "number")("SM %K", 3, J.obj(("min", 1)))
    smSmoothD = J.get(G_input, "number")("SM %D", 3, J.obj(("min", 1)))
    aroonLength = J.get(G_input, "number")("Aroon Length", 14, J.obj(("min", 1)))
    awesomeOscFast = J.get(G_input, "number")("AO Fast Length", 5, J.obj(("min", 1)))
    awesomeOscSlow = J.get(G_input, "number")("AO Slow Length", 34, J.obj(("min", 1)))
    overboughtThreshold = J.get(G_input, "number")("Overbought Threshold", 5, J.obj(("min", 1), ("max", 10)))
    oversoldThreshold = J.get(G_input, "number")("Oversold Threshold", (-5), J.obj(("max", (-1)), ("min", (-10))))
    filterDuplicates = J.get(G_input, "boolean")("Filter Duplicate Signals", False)
    mySma50Length = J.get(G_input, "number")("SMA 50 Length", 50, J.obj(("min", 1)))
    mySma200Length = J.get(G_input, "number")("SMA 200 Length", 200, J.obj(("min", 1)))
    myStdDevLength = J.get(G_input, "number")("Standard Deviation Length", 20, J.obj(("min", 1)))
    myBBLength = J.get(G_input, "number")("%B Length", 20, J.obj(("min", 1)))
    myBBMultiplier = J.get(G_input, "number")("%B Multiplier", 2, J.obj(("min", 0.1)))
    myMacd = G_sub(G_ema(G_close, macdFast), G_ema(G_close, macdSlow))
    myMacdSignal = G_ema(myMacd, macdSignal)
    myMacdHist = G_sub(myMacd, myMacdSignal)
    myRsi = G_rsi(G_close, rsiLength)
    myPpo = G_mult(G_div(G_sub(G_ema(G_close, ppoFast), G_ema(G_close, ppoSlow)), G_ema(G_close, ppoSlow)), 100)
    myPpoSignal = G_ema(myPpo, ppoSignal)
    myPpoHist = G_sub(myPpo, myPpoSignal)
    myMfi = G_mfi(G_hlc3, G_volume, mfiLength)
    myCci = G_cci(G_hlc3, cciLength)
    myStochRsi = G_stochastic_rsi(G_close, stochRsiLength, 3)
    def _f1(_window=J.undefined, *_args):
        myHigh = J.get(G_Math, "max")(*J.spread(_window))
        myLow = J.get(G_Math, "min")(*J.spread(_window))
        val = J.add(J.mul(J.mul(0.33, 2), J.sub(J.div(J.sub(J.get(_window, J.sub(J.get(_window, "length"), 1)), myLow), J.sub(myHigh, myLow)), 0.5)), J.mul(0.67, (_t1 if J.truthy(_t1 := J.get(_window, J.sub(J.get(_window, "length"), 2))) else 0)))
        return J.mul(0.5, J.get(G_Math, "log")(J.div(J.add(1, val), J.sub(1, val))))
    myFischer = G_sliding_window_function(G_close, fischerLength, _f1)
    myCmo = G_cmo(G_close, cmoLength)
    def _f2(_c=J.undefined, _pc=J.undefined, i=J.undefined, *_args):
        if J.lt(i, J.sub(J.add(kstRoc4, kstSma4), 1)):
            return None
        roc1 = G_sma(G_roc(G_close, kstRoc1), kstSma1)
        roc2 = G_sma(G_roc(G_close, kstRoc2), kstSma2)
        roc3 = G_sma(G_roc(G_close, kstRoc3), kstSma3)
        roc4 = G_sma(G_roc(G_close, kstRoc4), kstSma4)
        return J.add(J.add(J.add(J.get(roc1, i), J.mul(2, J.get(roc2, i))), J.mul(3, J.get(roc3, i))), J.mul(4, J.get(roc4, i)))
    myKst = G_for_every(G_close, _f2)
    myKstSignal = G_ema(myKst, kstSignal)
    myKstHist = G_sub(myKst, myKstSignal)
    def _f3(_window=J.undefined, *_args):
        myHigh = J.get(G_Math, "max")(*J.spread(_window))
        myLow = J.get(G_Math, "min")(*J.spread(_window))
        return J.div(J.mul(100, J.sub(J.get(_window, J.sub(J.get(_window, "length"), 1)), myLow)), J.sub(myHigh, myLow))
    myStochMomentum = G_sliding_window_function(G_close, smLength, _f3)
    mySmK = G_sma(myStochMomentum, smSmoothK)
    mySmD = G_sma(mySmK, smSmoothD)
    def _f4(_h=J.undefined, _ph=J.undefined, i=J.undefined, *_args):
        if J.lt(i, aroonLength):
            return None
        window = J.get(G_high, "slice")(J.add(J.sub(i, aroonLength), 1), J.add(i, 1))
        return J.div(J.mul(100, J.sub(aroonLength, J.get(window, "lastIndexOf")(J.get(G_Math, "max")(*J.spread(window))))), aroonLength)
    myAroonUp = G_for_every(G_high, _f4)
    def _f5(_l=J.undefined, _pl=J.undefined, i=J.undefined, *_args):
        if J.lt(i, aroonLength):
            return None
        window = J.get(G_low, "slice")(J.add(J.sub(i, aroonLength), 1), J.add(i, 1))
        return J.div(J.mul(100, J.sub(aroonLength, J.get(window, "lastIndexOf")(J.get(G_Math, "min")(*J.spread(window))))), aroonLength)
    myAroonDown = G_for_every(G_low, _f5)
    myAroonOsc = G_sub(myAroonUp, myAroonDown)
    myAwesomeOsc = G_sub(G_sma(G_hl2, awesomeOscFast), G_sma(G_hl2, awesomeOscSlow))
    mySma50 = G_sma(G_close, mySma50Length)
    mySma200 = G_sma(G_close, mySma200Length)
    myStdDev = G_stdev(G_close, myStdDevLength)
    def _f6(_sma50=J.undefined, _sma200=J.undefined, _stdDev=J.undefined, *_args):
        if J.ge(J.sub(_sma50, _sma200), _stdDev):
            return 1
        if J.ge(J.sub(_sma200, _sma50), _stdDev):
            return (-1)
        return 0
    mySmaCrossover = G_for_every(mySma50, mySma200, myStdDev, _f6)
    myBBMid = G_sma(G_close, myBBLength)
    myBBDev = G_mult(G_stdev(G_close, myBBLength), myBBMultiplier)
    myBBUpper = G_add(myBBMid, myBBDev)
    myBBLower = G_sub(myBBMid, myBBDev)
    def _f7(_c=J.undefined, _u=J.undefined, _l=J.undefined, *_args):
        return J.div(J.sub(_c, _l), J.sub(_u, _l))
    myPercentB = G_for_every(G_close, myBBUpper, myBBLower, _f7)
    def getZoneScore(_v=J.undefined, _hi=J.undefined, _lo=J.undefined, *_args):
        return (1 if J.ge(_v, _hi) else ((-1) if J.le(_v, _lo) else 0))
    def _f8(_h=J.undefined, *_args):
        return getZoneScore(_h, 0.5, (-0.5))
    macdZoneScore = G_for_every(myMacdHist, _f8)
    def _f9(_r=J.undefined, *_args):
        return getZoneScore(_r, 70, 30)
    rsiZoneScore = G_for_every(myRsi, _f9)
    def _f10(_p=J.undefined, *_args):
        return getZoneScore(_p, 0.5, (-0.5))
    ppoZoneScore = G_for_every(myPpoHist, _f10)
    def _f11(_m=J.undefined, *_args):
        return getZoneScore(_m, 80, 20)
    mfiZoneScore = G_for_every(myMfi, _f11)
    def _f12(_c=J.undefined, *_args):
        return getZoneScore(_c, 100, (-100))
    cciZoneScore = G_for_every(myCci, _f12)
    def _f13(_s=J.undefined, *_args):
        return getZoneScore(_s, 80, 20)
    stochRsiZoneScore = G_for_every(myStochRsi, _f13)
    def _f14(_f=J.undefined, *_args):
        return getZoneScore(_f, 2, (-2))
    fischerZoneScore = G_for_every(myFischer, _f14)
    def _f15(_c=J.undefined, *_args):
        return getZoneScore(_c, 50, (-50))
    cmoZoneScore = G_for_every(myCmo, _f15)
    def _f16(_k=J.undefined, *_args):
        return getZoneScore(_k, 0.5, (-0.5))
    kstZoneScore = G_for_every(myKstHist, _f16)
    def _f17(_s=J.undefined, *_args):
        return getZoneScore(_s, 20, (-20))
    smZoneScore = G_for_every(G_sub(mySmK, mySmD), _f17)
    def _f18(_a=J.undefined, *_args):
        return getZoneScore(_a, 50, (-50))
    aroonOscZoneScore = G_for_every(myAroonOsc, _f18)
    def _f19(_a=J.undefined, *_args):
        return getZoneScore(_a, 0.5, (-0.5))
    awesomeOscZoneScore = G_for_every(myAwesomeOsc, _f19)
    def _f20(_b=J.undefined, *_args):
        return getZoneScore(_b, 1, 0)
    percentBZoneScore = G_for_every(myPercentB, _f20)
    def _f21(_macd=J.undefined, _rsi=J.undefined, _ppo=J.undefined, _mfi=J.undefined, _cci=J.undefined, _stochRsi=J.undefined, _fischer=J.undefined, _cmo=J.undefined, _kst=J.undefined, _sm=J.undefined, _aroon=J.undefined, _awesome=J.undefined, _sma=J.undefined, _percentB=J.undefined, *_args):
        scores = J.JSArray([_macd, _rsi, _ppo, _mfi, _cci, _stochRsi, _fischer, _cmo, _kst, _sm, _aroon, _awesome, _sma, _percentB])
        def _f1(_s=J.undefined, *_args):
            return J.seq(_s, 1)
        overboughtCount = J.get(J.get(scores, "filter")(_f1), "length")
        def _f2(_s=J.undefined, *_args):
            return J.seq(_s, (-1))
        oversoldCount = J.get(J.get(scores, "filter")(_f2), "length")
        return J.sub(overboughtCount, oversoldCount)
    aggregateScore = G_for_every(macdZoneScore, rsiZoneScore, ppoZoneScore, mfiZoneScore, cciZoneScore, stochRsiZoneScore, fischerZoneScore, cmoZoneScore, kstZoneScore, smZoneScore, aroonOscZoneScore, awesomeOscZoneScore, mySmaCrossover, percentBZoneScore, _f21)
    lastSignal = None
    lastCount = 0
    def _f22(_s=J.undefined, _p=J.undefined, i=J.undefined, *_args):
        nonlocal lastSignal, lastCount
        score = J.get(aggregateScore, i)
        agreeingIndicators_2 = J.obj(("overbought", score), ("oversold", J.neg(score)))
        if (J.le(score, oversoldThreshold) and (((not J.truthy(filterDuplicates)) or J.sne(lastSignal, "oversold")) or J.sne(lastCount, J.get(agreeingIndicators_2, "oversold")))):
            lastSignal = "oversold"
            lastCount = J.get(agreeingIndicators_2, "oversold")
            return "oversold"
        if (J.ge(score, overboughtThreshold) and (((not J.truthy(filterDuplicates)) or J.sne(lastSignal, "overbought")) or J.sne(lastCount, J.get(agreeingIndicators_2, "overbought")))):
            lastSignal = "overbought"
            lastCount = J.get(agreeingIndicators_2, "overbought")
            return "overbought"
        return None
    signals = G_for_every(aggregateScore, _f22)
    myHighPainted = G_paint(G_high, J.obj(("name", "highs"), ("color", "white"), ("style", "dotted")))
    myLowPainted = G_paint(G_low, J.obj(("name", "lows"), ("color", "white"), ("style", "dotted")))
    def _f23(_macd=J.undefined, _rsi=J.undefined, _ppo=J.undefined, _mfi=J.undefined, _cci=J.undefined, _stochRsi=J.undefined, _fischer=J.undefined, _cmo=J.undefined, _kst=J.undefined, _sm=J.undefined, _aroon=J.undefined, _awesome=J.undefined, _sma=J.undefined, _percentB=J.undefined, *_args):
        scores = J.JSArray([_macd, _rsi, _ppo, _mfi, _cci, _stochRsi, _fischer, _cmo, _kst, _sm, _aroon, _awesome, _sma, _percentB])
        def _f1(_s=J.undefined, *_args):
            return J.seq(_s, 1)
        overboughtCount = J.get(J.get(scores, "filter")(_f1), "length")
        def _f2(_s=J.undefined, *_args):
            return J.seq(_s, (-1))
        oversoldCount = J.get(J.get(scores, "filter")(_f2), "length")
        return J.obj(("overbought", overboughtCount), ("oversold", oversoldCount))
    agreeingIndicators = G_for_every(macdZoneScore, rsiZoneScore, ppoZoneScore, mfiZoneScore, cciZoneScore, stochRsiZoneScore, fischerZoneScore, cmoZoneScore, kstZoneScore, smZoneScore, aroonOscZoneScore, awesomeOscZoneScore, mySmaCrossover, percentBZoneScore, _f23)
    i = 0
    while J.lt(i, J.get(signals, "length")):
        if J.seq(J.get(signals, i), "oversold"):
            G_paint_label_at_line(myLowPainted, i, J.template("▲", J.get(J.get(agreeingIndicators, i), "oversold")), J.obj(("color", "green"), ("vertical_align", "bottom")))
        elif J.seq(J.get(signals, i), "overbought"):
            G_paint_label_at_line(myHighPainted, i, J.template("▼", J.get(J.get(agreeingIndicators, i), "overbought")), J.obj(("color", "red"), ("vertical_align", "top")))
        i = J.inc(i)
    def _f24(_s=J.undefined, *_args):
        return J.seq(_s, "oversold")
    G_register_signal(G_for_every(signals, _f24), "Oversold Signal")
    def _f25(_s=J.undefined, *_args):
        return J.seq(_s, "overbought")
    G_register_signal(G_for_every(signals, _f25), "Overbought Signal")


register_store_indicator(
    script,
    name='multi_oscillator_consensus_momentum_score_TS',
    title='Multi-Oscillator Consensus Momentum Score',
    developer='QXEM',
    url='https://trendspider.com/trading-tools-store/indicators/682f83-multi-oscillator-consensus-momentum-score/',
    position='price',
    inputs=[{'id': 'macd_fast_length', 'title': 'MACD Fast Length', 'type': 'number', 'default': 12}, {'id': 'macd_slow_length', 'title': 'MACD Slow Length', 'type': 'number', 'default': 26}, {'id': 'macd_signal_length', 'title': 'MACD Signal Length', 'type': 'number', 'default': 9}, {'id': 'rsi_length', 'title': 'RSI Length', 'type': 'number', 'default': 14}, {'id': 'ppo_fast_length', 'title': 'PPO Fast Length', 'type': 'number', 'default': 12}, {'id': 'ppo_slow_length', 'title': 'PPO Slow Length', 'type': 'number', 'default': 26}, {'id': 'ppo_signal_length', 'title': 'PPO Signal Length', 'type': 'number', 'default': 9}, {'id': 'mfi_length', 'title': 'MFI Length', 'type': 'number', 'default': 14}, {'id': 'cci_length', 'title': 'CCI Length', 'type': 'number', 'default': 20}, {'id': 'stoch_rsi_length', 'title': 'Stoch RSI Length', 'type': 'number', 'default': 14}, {'id': 'fischer_length', 'title': 'Fischer Length', 'type': 'number', 'default': 9}, {'id': 'cmo_length', 'title': 'CMO Length', 'type': 'number', 'default': 14}, {'id': 'kst_roc1', 'title': 'KST ROC1', 'type': 'number', 'default': 10}, {'id': 'kst_roc2', 'title': 'KST ROC2', 'type': 'number', 'default': 15}, {'id': 'kst_roc3', 'title': 'KST ROC3', 'type': 'number', 'default': 20}, {'id': 'kst_roc4', 'title': 'KST ROC4', 'type': 'number', 'default': 30}, {'id': 'kst_sma1', 'title': 'KST SMA1', 'type': 'number', 'default': 10}, {'id': 'kst_sma2', 'title': 'KST SMA2', 'type': 'number', 'default': 10}, {'id': 'kst_sma3', 'title': 'KST SMA3', 'type': 'number', 'default': 10}, {'id': 'kst_sma4', 'title': 'KST SMA4', 'type': 'number', 'default': 15}, {'id': 'kst_signal', 'title': 'KST Signal', 'type': 'number', 'default': 9}, {'id': 'stoch_mom_length', 'title': 'Stoch Mom Length', 'type': 'number', 'default': 10}, {'id': 'sm__k', 'title': 'SM %K', 'type': 'number', 'default': 3}, {'id': 'sm__d', 'title': 'SM %D', 'type': 'number', 'default': 3}, {'id': 'aroon_length', 'title': 'Aroon Length', 'type': 'number', 'default': 14}, {'id': 'ao_fast_length', 'title': 'AO Fast Length', 'type': 'number', 'default': 5}, {'id': 'ao_slow_length', 'title': 'AO Slow Length', 'type': 'number', 'default': 34}, {'id': 'overbought_threshold', 'title': 'Overbought Threshold', 'type': 'number', 'default': 5}, {'id': 'oversold_threshold', 'title': 'Oversold Threshold', 'type': 'number', 'default': -5}, {'id': 'filter_duplicate_signals', 'title': 'Filter Duplicate Signals', 'type': 'boolean', 'default': False}, {'id': 'sma_50_length', 'title': 'SMA 50 Length', 'type': 'number', 'default': 50}, {'id': 'sma_200_length', 'title': 'SMA 200 Length', 'type': 'number', 'default': 200}, {'id': 'standard_deviation_length', 'title': 'Standard Deviation Length', 'type': 'number', 'default': 20}, {'id': '_b_length', 'title': '%B Length', 'type': 'number', 'default': 20}, {'id': '_b_multiplier', 'title': '%B Multiplier', 'type': 'number', 'default': 2}],
    outputs=['highs', 'lows', 'oversold_signal', 'overbought_signal'],
    signals=['oversold_signal', 'overbought_signal'],
    requires=[],
    parity='exact',
)
