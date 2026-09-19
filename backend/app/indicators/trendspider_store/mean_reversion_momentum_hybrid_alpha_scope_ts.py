"""
Mean Reversion & Momentum Hybrid | Alpha Scope -- TrendSpider store indicator by Alpha Scope.

Registered as "mean_reversion_momentum_hybrid_alpha_scope_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/69ca4c-mean-reversion-momentum-hybrid-alpha-scope/)
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
    G_atr = G["atr"]
    G_close = G["close"]
    G_color_cloud = G["color_cloud"]
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_div = G["div"]
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_horizontal_line = G["horizontal_line"]
    G_input = G["input"]
    G_low = G["low"]
    G_market = G["market"]
    G_mult = G["mult"]
    G_open = G["open"]
    G_paint = G["paint"]
    G_series_of = G["series_of"]
    G_sliding_window_function = G["sliding_window_function"]
    G_sma = G["sma"]
    G_stdev = G["stdev"]
    G_sub = G["sub"]
    G_wildma = G["wildma"]
    G_describe_indicator("Mean Reversion & Momentum Hybrid | Alpha-Scope", "lower")
    mySource = J.get(G_input, "select")("Source", "close", J.get(G_constants, "price_source_options"))
    myPrice = J.get(G_market, mySource)
    myBbLength = J.get(G_input, "number")("Bollinger Bands Length", 20, J.obj(("min", 1)))
    myBbMult = J.get(G_input, "number")("Bollinger Bands Multiplier", 2, J.obj(("min", 0.1)))
    myMinBbWidth = J.get(G_input, "number")("Minimum BB Width (% of Price)", 0.5, J.obj(("min", 0)))
    myLongThreshold = J.get(G_input, "number")("BB% Long Threshold (L)", 55, J.obj(("min", 0), ("max", 100)))
    myShortThreshold = J.get(G_input, "number")("BB% Short Threshold (S)", 45, J.obj(("min", 0), ("max", 100)))
    myLookback = J.get(G_input, "number")("RMA length", 15, J.obj(("min", 1)))
    myAtrLookback = J.get(G_input, "number")("ATR length", 20, J.obj(("min", 1)))
    myMomentumLength = J.get(G_input, "number")("Momentum Length", 25, J.obj(("min", 1)))
    myMult75 = J.get(G_input, "number")("mult_75", 1.3, J.obj(("min", 0.1)))
    myMult25 = J.get(G_input, "number")("mult_25", 1.3, J.obj(("min", 0.1)))
    myUseBgColor = J.get(G_input, "boolean")("Use Background Color for Signals", False)
    myBbBasis = G_sma(G_close, myBbLength)
    myBbDev = G_mult(G_stdev(G_close, myBbLength), myBbMult)
    myBbUpper = G_add(myBbBasis, myBbDev)
    myBbLower = G_sub(myBbBasis, myBbDev)
    myBbWidth = G_mult(G_div(G_sub(myBbUpper, myBbLower), myBbBasis), 100)
    myRma = G_wildma(myPrice, myLookback)
    myAtr = G_atr(G_high, G_low, G_close, myAtrLookback)
    def _f1(_price=J.undefined, _rma=J.undefined, _atr=J.undefined, *_args):
        return J.gt(_price, J.add(_rma, _atr))
    myLongFil = G_for_every(myPrice, myRma, myAtr, _f1)
    def _f2(_price=J.undefined, _rma=J.undefined, _atr=J.undefined, *_args):
        return J.lt(_price, J.sub(_rma, _atr))
    myShortFil = G_for_every(myPrice, myRma, myAtr, _f2)
    def _f3(_long=J.undefined, _short=J.undefined, _prev=J.undefined, *_args):
        if (J.truthy(_long) and (not J.truthy(_short))):
            return 1
        if J.truthy(_short):
            return (-1)
        return (_t1 if J.truthy(_t1 := _prev) else 0)
    myScore = G_for_every(myLongFil, myShortFil, _f3)
    def _f4(_window=J.undefined, *_args):
        def _f1(a=J.undefined, b=J.undefined, *_args):
            return J.sub(a, b)
        mySorted = J.get(J.get(_window, "slice")(), "sort")(_f1)
        myIndex = J.get(G_Math, "floor")(J.mul(J.get(mySorted, "length"), 0.75))
        return J.get(mySorted, myIndex)
    myPercentile75 = G_sliding_window_function(myPrice, myMomentumLength, _f4)
    def _f5(_window=J.undefined, *_args):
        def _f1(a=J.undefined, b=J.undefined, *_args):
            return J.sub(a, b)
        mySorted = J.get(J.get(_window, "slice")(), "sort")(_f1)
        myIndex = J.get(G_Math, "floor")(J.mul(J.get(mySorted, "length"), 0.25))
        return J.get(mySorted, myIndex)
    myPercentile25 = G_sliding_window_function(myPrice, myMomentumLength, _f5)
    myMult75Series = G_series_of(myMult75)
    myMult25Series = G_series_of(myMult25)
    def _f6(_close=J.undefined, _p75=J.undefined, _atr=J.undefined, _mult75=J.undefined, *_args):
        return J.gt(_close, J.add(_p75, J.mul(_mult75, _atr)))
    myLongMomentum = G_for_every(G_close, myPercentile75, myAtr, myMult75Series, _f6)
    def _f7(_close=J.undefined, _p25=J.undefined, _atr=J.undefined, _mult25=J.undefined, *_args):
        return J.lt(_close, J.sub(_p25, J.mul(_mult25, _atr)))
    myShortMomentum = G_for_every(G_close, myPercentile25, myAtr, myMult25Series, _f7)
    def _f8(_long=J.undefined, _short=J.undefined, _prev=J.undefined, *_args):
        if (J.truthy(_long) and (not J.truthy(_short))):
            return 1
        if J.truthy(_short):
            return (-1)
        return (_t1 if J.truthy(_t1 := _prev) else 0)
    mySig = G_for_every(myLongFil, myShortFil, _f8)
    def _f9(_c=J.undefined, _o=J.undefined, _h=J.undefined, _l=J.undefined, *_args):
        return J.div(J.add(J.add(J.add(_c, _o), _h), _l), 4)
    myBbPercentSrc = G_for_every(G_close, G_open, G_high, G_low, _f9)
    myBbPercentBasis = G_sma(myBbPercentSrc, myBbLength)
    myBbPercentDev = G_mult(G_stdev(myBbPercentSrc, myBbLength), myBbMult)
    myBbPercentUpper = G_add(myBbPercentBasis, myBbPercentDev)
    myBbPercentLower = G_sub(myBbPercentBasis, myBbPercentDev)
    myPositionBetweenBands = G_mult(G_div(G_sub(myBbPercentSrc, myBbPercentLower), G_sub(myBbPercentUpper, myBbPercentLower)), 100)
    myLongThresholdSeries = G_series_of(myLongThreshold)
    myShortThresholdSeries = G_series_of(myShortThreshold)
    def _f10(_pos=J.undefined, _longTh=J.undefined, _shortTh=J.undefined, _prev=J.undefined, *_args):
        if J.gt(_pos, _longTh):
            return 1
        if J.lt(_pos, _shortTh):
            return (-1)
        return (_t1 if J.truthy(_t1 := _prev) else 0)
    myBbPercentSig = G_for_every(myPositionBetweenBands, myLongThresholdSeries, myShortThresholdSeries, _f10)
    myMinBbWidthSeries = G_series_of(myMinBbWidth)
    def _f11(_bbSig=J.undefined, _sig=J.undefined, _score=J.undefined, _width=J.undefined, _minWidth=J.undefined, *_args):
        return (J.gt(_width, _minWidth) if J.truthy(_t1 := (J.seq(_score, 1) if J.truthy(_t2 := (J.seq(_sig, 1) if J.truthy(_t3 := J.seq(_bbSig, 1)) else _t3)) else _t2)) else _t1)
    myBuyCondition = G_for_every(myBbPercentSig, mySig, myScore, myBbWidth, myMinBbWidthSeries, _f11)
    def _f12(_bbSig=J.undefined, _sig=J.undefined, _score=J.undefined, _width=J.undefined, _minWidth=J.undefined, *_args):
        return (J.gt(_width, _minWidth) if J.truthy(_t1 := (J.seq(_score, (-1)) if J.truthy(_t2 := (J.seq(_sig, (-1)) if J.truthy(_t3 := J.seq(_bbSig, (-1))) else _t3)) else _t2)) else _t1)
    mySellCondition = G_for_every(myBbPercentSig, mySig, myScore, myBbWidth, myMinBbWidthSeries, _f12)
    myDecayRate = 0.1
    def _f13(_buy=J.undefined, _sell=J.undefined, _prev=J.undefined, *_args):
        if J.truthy(_buy):
            return 1
        if J.truthy(_sell):
            return (-1)
        return J.mul((_t1 if J.truthy(_t1 := _prev) else 0), J.sub(1, myDecayRate))
    myFadeSignal = G_for_every(myBuyCondition, mySellCondition, _f13)
    def _f14(_fade=J.undefined, *_args):
        myAbsFade = J.get(G_Math, "abs")(_fade)
        if J.gt(_fade, 0):
            myR = J.get(G_Math, "round")(J.add(255, J.mul(J.sub(0, 255), myAbsFade)))
            myG = J.get(G_Math, "round")(J.add(255, J.mul(J.sub(123, 255), myAbsFade)))
            myB = J.get(G_Math, "round")(J.add(255, J.mul(J.sub(167, 255), myAbsFade)))
            return J.template("rgb(", myR, ", ", myG, ", ", myB, ")")
        elif J.lt(_fade, 0):
            myR_2 = J.get(G_Math, "round")(J.add(255, J.mul(J.sub(200, 255), myAbsFade)))
            myG_2 = J.get(G_Math, "round")(J.add(255, J.mul(J.sub(60, 255), myAbsFade)))
            myB_2 = J.get(G_Math, "round")(J.add(255, J.mul(J.sub(60, 255), myAbsFade)))
            return J.template("rgb(", myR_2, ", ", myG_2, ", ", myB_2, ")")
        return "rgb(95, 92, 92)"
    myGradientColor = G_for_every(myFadeSignal, _f14)
    def _f15(_buy=J.undefined, _prev=J.undefined, *_args):
        if (J.truthy(_buy) and (not J.truthy(_prev))):
            return True
        return False
    myLongSignal = G_for_every(myBuyCondition, _f15)
    def _f16(_sell=J.undefined, _prev=J.undefined, *_args):
        if (J.truthy(_sell) and (not J.truthy(_prev))):
            return True
        return False
    myShortSignal = G_for_every(mySellCondition, _f16)
    def _f17(_long=J.undefined, _fade=J.undefined, *_args):
        return (_fade if J.truthy(_long) else None)
    myLongVerticalLine = G_for_every(myLongSignal, myFadeSignal, _f17)
    def _f18(_short=J.undefined, _fade=J.undefined, *_args):
        return (_fade if J.truthy(_short) else None)
    myShortVerticalLine = G_for_every(myShortSignal, myFadeSignal, _f18)
    myZeroLineSeries = G_horizontal_line(0)
    myZeroLine = G_paint(myZeroLineSeries, J.obj(("color", "rgba(77, 74, 74, 0.21)"), ("name", "Zero Line"), ("style", "line")))
    mySignalLine = G_paint(myFadeSignal, J.obj(("color", myGradientColor), ("name", "Gradient Signal Line"), ("style", "line")))
    G_paint(myLongVerticalLine, J.obj(("style", "column"), ("color", "rgba(0, 123, 167, 0.5)"), ("name", "Long Signal")))
    G_paint(myShortVerticalLine, J.obj(("style", "column"), ("color", "rgba(200, 60, 60, 0.5)"), ("name", "Short Signal")))
    def _f19(_fade=J.undefined, *_args):
        return (_fade if J.ge(_fade, 0) else None)
    myPositiveSignal = G_for_every(myFadeSignal, _f19)
    def _f20(_fade=J.undefined, *_args):
        return (_fade if J.lt(_fade, 0) else None)
    myNegativeSignal = G_for_every(myFadeSignal, _f20)
    def _f21(_fade=J.undefined, *_args):
        if J.ge(_fade, 0):
            myAbsFade = J.get(G_Math, "abs")(_fade)
            myOpacity = J.mul(myAbsFade, 0.3)
            myR = J.get(G_Math, "round")(J.add(255, J.mul(J.sub(0, 255), myAbsFade)))
            myG = J.get(G_Math, "round")(J.add(255, J.mul(J.sub(123, 255), myAbsFade)))
            myB = J.get(G_Math, "round")(J.add(255, J.mul(J.sub(167, 255), myAbsFade)))
            return J.template("rgba(", myR, ", ", myG, ", ", myB, ", ", myOpacity, ")")
        return "rgba(0, 0, 0, 0)"
    myFillColorPositive = G_for_every(myFadeSignal, _f21)
    def _f22(_fade=J.undefined, *_args):
        if J.lt(_fade, 0):
            myAbsFade = J.get(G_Math, "abs")(_fade)
            myOpacity = J.mul(myAbsFade, 0.3)
            myR = J.get(G_Math, "round")(J.add(255, J.mul(J.sub(200, 255), myAbsFade)))
            myG = J.get(G_Math, "round")(J.add(255, J.mul(J.sub(60, 255), myAbsFade)))
            myB = J.get(G_Math, "round")(J.add(255, J.mul(J.sub(60, 255), myAbsFade)))
            return J.template("rgba(", myR, ", ", myG, ", ", myB, ", ", myOpacity, ")")
        return "rgba(0, 0, 0, 0)"
    myFillColorNegative = G_for_every(myFadeSignal, _f22)
    G_color_cloud(myZeroLineSeries, myFadeSignal, "rgba(200, 60, 60, 0.3)", "rgba(0, 123, 167, 0.3)")


register_store_indicator(
    script,
    name='mean_reversion_momentum_hybrid_alpha_scope_TS',
    title='Mean Reversion & Momentum Hybrid | Alpha Scope',
    developer='Alpha Scope',
    url='https://trendspider.com/trading-tools-store/indicators/69ca4c-mean-reversion-momentum-hybrid-alpha-scope/',
    position='lower',
    inputs=[{'id': 'source', 'title': 'Source', 'type': 'select_wide', 'default': 'close', 'options': ['open', 'high', 'low', 'close', 'hl2', 'oc2', 'hlc3', 'ohlc4', 'wclose']}, {'id': 'bollinger_bands_length', 'title': 'Bollinger Bands Length', 'type': 'number', 'default': 20}, {'id': 'bollinger_bands_multiplier', 'title': 'Bollinger Bands Multiplier', 'type': 'number', 'default': 2}, {'id': 'minimum_bb_width____of_price_', 'title': 'Minimum BB Width (% of Price)', 'type': 'number', 'default': 0.5}, {'id': 'bb__long_threshold__l_', 'title': 'BB% Long Threshold (L)', 'type': 'number', 'default': 55}, {'id': 'bb__short_threshold__s_', 'title': 'BB% Short Threshold (S)', 'type': 'number', 'default': 45}, {'id': 'rma_length', 'title': 'RMA length', 'type': 'number', 'default': 15}, {'id': 'atr_length', 'title': 'ATR length', 'type': 'number', 'default': 20}, {'id': 'momentum_length', 'title': 'Momentum Length', 'type': 'number', 'default': 25}, {'id': 'mult_75', 'title': 'mult_75', 'type': 'number', 'default': 1.3}, {'id': 'mult_25', 'title': 'mult_25', 'type': 'number', 'default': 1.3}, {'id': 'use_background_color_for_signals', 'title': 'Use Background Color for Signals', 'type': 'boolean', 'default': False}],
    outputs=['zero_line', 'gradient_signal_line', 'long_signal', 'short_signal', 'line_6', 'line_7', 'line_9', 'line_10'],
    signals=[],
    requires=[],
    parity='exact',
)
