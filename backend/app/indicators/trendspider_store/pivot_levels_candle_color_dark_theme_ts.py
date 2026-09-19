"""
Pivot Levels & Candle Color (Dark Theme) -- TrendSpider store indicator by Mat Reeves.

Registered as "pivot_levels_candle_color_dark_theme_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6a4795-pivot-levels-candle-color-dark-theme/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Infinity = G["Infinity"]
    G_Math = G["Math"]
    G_Number = G["Number"]
    G_close = G["close"]
    G_color_candles = G["color_candles"]
    G_constants = G["constants"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_input = G["input"]
    G_interpolate_sparse_series = G["interpolate_sparse_series"]
    G_isNaN = G["isNaN"]
    G_low = G["low"]
    G_paint = G["paint"]
    G_series_of = G["series_of"]
    G_describe_indicator("Pivot Levels & Candle Color (Dark Theme)")
    pivotLeftBars = J.get(G_input, "number")("Pivot Left Bars", 10, J.obj(("min", 1), ("max", 50)))
    pivotRightBars = J.get(G_input, "number")("Pivot Right Bars", 10, J.obj(("min", 1), ("max", 50)))
    neutralLookbackBars = J.get(G_input, "number")("Neutral Lookback Bars", 5, J.obj(("min", 2), ("max", 20)))
    myResolutionMinutes = (1440 if J.truthy(G_isNaN(J.get(G_current, "resolution"))) else G_Number(J.get(G_current, "resolution")))
    myBaselineMinutes = 240
    myTimeframeSensitivity = J.get(G_Math, "sqrt")(J.div(myResolutionMinutes, myBaselineMinutes))
    myBreakoutConfirmationFactor = J.add(0.995, J.mul(J.sub(1, myTimeframeSensitivity), 0.003))
    myBreakdownConfirmationFactor = J.sub(1.005, J.mul(J.sub(1, myTimeframeSensitivity), 0.003))
    myBullishProgressRelaxation = J.mul(J.sub(myTimeframeSensitivity, 1), 0.002)
    myBearishProgressRelaxation = J.mul(J.sub(myTimeframeSensitivity, 1), 0.002)
    myRangeTightnessMultiplier = J.add(0.4, J.mul(J.sub(myTimeframeSensitivity, 1), 0.15))
    myPivotHighs = G_series_of(None)
    myPivotLows = G_series_of(None)
    myPotentialPivotHighs = J.JSArray([])
    myPotentialPivotLows = J.JSArray([])
    i = pivotLeftBars
    while J.lt(i, J.sub(J.get(G_high, "length"), pivotRightBars)):
        myIsHighCandidate = True
        myCurrentHigh = J.get(G_high, i)
        j = 1
        while J.le(j, pivotLeftBars):
            if J.gt(J.get(G_high, J.sub(i, j)), myCurrentHigh):
                myIsHighCandidate = False
                break
            j = J.add(j, 1)
        if J.truthy(myIsHighCandidate):
            myConfirmedReversal = False
            myRightSideMax = J.neg(G_Infinity)
            j_2 = 1
            while J.le(j_2, pivotRightBars):
                myRightSideMax = J.get(G_Math, "max")(myRightSideMax, J.get(G_high, J.add(i, j_2)))
                if J.lt(J.get(G_high, J.add(i, j_2)), J.mul(myCurrentHigh, myBreakoutConfirmationFactor)):
                    myConfirmedReversal = True
                j_2 = J.add(j_2, 1)
            if (J.truthy(myConfirmedReversal) and J.lt(myRightSideMax, myCurrentHigh)):
                J.get(myPotentialPivotHighs, "push")(J.obj(("index", i), ("value", myCurrentHigh)))
        myIsLowCandidate = True
        myCurrentLow = J.get(G_low, i)
        j_3 = 1
        while J.le(j_3, pivotLeftBars):
            if J.lt(J.get(G_low, J.sub(i, j_3)), myCurrentLow):
                myIsLowCandidate = False
                break
            j_3 = J.add(j_3, 1)
        if J.truthy(myIsLowCandidate):
            myConfirmedReversal_2 = False
            myRightSideMin = G_Infinity
            j_4 = 1
            while J.le(j_4, pivotRightBars):
                myRightSideMin = J.get(G_Math, "min")(myRightSideMin, J.get(G_low, J.add(i, j_4)))
                if J.gt(J.get(G_low, J.add(i, j_4)), J.mul(myCurrentLow, myBreakdownConfirmationFactor)):
                    myConfirmedReversal_2 = True
                j_4 = J.add(j_4, 1)
            if (J.truthy(myConfirmedReversal_2) and J.gt(myRightSideMin, myCurrentLow)):
                J.get(myPotentialPivotLows, "push")(J.obj(("index", i), ("value", myCurrentLow)))
        i = J.add(i, 1)
    myMinPivotSpacing = J.get(G_Math, "max")(5, J.get(G_Math, "floor")(J.div(J.add(pivotLeftBars, pivotRightBars), 3)))
    i_2 = 0
    while J.lt(i_2, J.get(myPotentialPivotHighs, "length")):
        myCurrentPivot = J.get(myPotentialPivotHighs, i_2)
        myIsSignificant = True
        j_5 = 0
        while J.lt(j_5, J.get(myPotentialPivotHighs, "length")):
            if J.seq(i_2, j_5):
                j_5 = J.add(j_5, 1)
                continue
            myOtherPivot = J.get(myPotentialPivotHighs, j_5)
            myDistance = J.get(G_Math, "abs")(J.sub(J.get(myCurrentPivot, "index"), J.get(myOtherPivot, "index")))
            if (J.lt(myDistance, myMinPivotSpacing) and J.gt(J.get(myOtherPivot, "value"), J.get(myCurrentPivot, "value"))):
                myIsSignificant = False
                break
            j_5 = J.add(j_5, 1)
        if J.truthy(myIsSignificant):
            J.set(myPivotHighs, J.get(myCurrentPivot, "index"), J.get(myCurrentPivot, "value"))
        i_2 = J.add(i_2, 1)
    i_3 = 0
    while J.lt(i_3, J.get(myPotentialPivotLows, "length")):
        myCurrentPivot_2 = J.get(myPotentialPivotLows, i_3)
        myIsSignificant_2 = True
        j_6 = 0
        while J.lt(j_6, J.get(myPotentialPivotLows, "length")):
            if J.seq(i_3, j_6):
                j_6 = J.add(j_6, 1)
                continue
            myOtherPivot_2 = J.get(myPotentialPivotLows, j_6)
            myDistance_2 = J.get(G_Math, "abs")(J.sub(J.get(myCurrentPivot_2, "index"), J.get(myOtherPivot_2, "index")))
            if (J.lt(myDistance_2, myMinPivotSpacing) and J.lt(J.get(myOtherPivot_2, "value"), J.get(myCurrentPivot_2, "value"))):
                myIsSignificant_2 = False
                break
            j_6 = J.add(j_6, 1)
        if J.truthy(myIsSignificant_2):
            J.set(myPivotLows, J.get(myCurrentPivot_2, "index"), J.get(myCurrentPivot_2, "value"))
        i_3 = J.add(i_3, 1)
    bullishBreakoutMarker = G_series_of(None)
    bearishBreakdownMarker = G_series_of(None)
    trendState = G_series_of(None)
    myLastActivePivotHigh = None
    myLastActivePivotLow = None
    myCurrentTrendState = "neutral"
    myLastBullishBreakoutIndex = (-999)
    myLastBearishBreakdownIndex = (-999)
    myBullishHighWaterMark = J.neg(G_Infinity)
    myBearishLowWaterMark = G_Infinity
    myBullishLegReactionLow = G_Infinity
    myBearishLegReactionHigh = J.neg(G_Infinity)
    myLastBullishBreakoutLevel = J.neg(G_Infinity)
    myLastBearishBreakdownLevel = G_Infinity
    i_4 = 0
    while J.lt(i_4, J.get(G_close, "length")):
        if (J.get(myPivotHighs, i_4) is not None):
            myLastActivePivotHigh = J.get(myPivotHighs, i_4)
        if (J.get(myPivotLows, i_4) is not None):
            myLastActivePivotLow = J.get(myPivotLows, i_4)
        if ((myLastActivePivotHigh is not None) and J.gt(J.get(G_close, i_4), myLastActivePivotHigh)):
            J.set(bullishBreakoutMarker, i_4, J.get(G_low, i_4))
            myCurrentTrendState = "bullish"
            myLastBullishBreakoutLevel = myLastActivePivotHigh
            myLastActivePivotHigh = None
            myLastBullishBreakoutIndex = i_4
            myBullishHighWaterMark = J.get(G_high, i_4)
            myBullishLegReactionLow = J.get(G_low, i_4)
        if ((myLastActivePivotLow is not None) and J.lt(J.get(G_close, i_4), myLastActivePivotLow)):
            J.set(bearishBreakdownMarker, i_4, J.get(G_high, i_4))
            myCurrentTrendState = "bearish"
            myLastBearishBreakdownLevel = myLastActivePivotLow
            myLastActivePivotLow = None
            myLastBearishBreakdownIndex = i_4
            myBearishLowWaterMark = J.get(G_low, i_4)
            myBearishLegReactionHigh = J.get(G_high, i_4)
        if (J.seq(myCurrentTrendState, "neutral") and J.gt(myLastBullishBreakoutLevel, J.neg(G_Infinity))):
            if (J.gt(J.get(G_close, i_4), myLastBullishBreakoutLevel) and J.gt(J.get(G_high, i_4), myBullishHighWaterMark)):
                myCurrentTrendState = "bullish"
                myLastBullishBreakoutIndex = i_4
                myBullishHighWaterMark = J.get(G_high, i_4)
                myBullishLegReactionLow = J.get(G_low, i_4)
        if (J.seq(myCurrentTrendState, "neutral") and J.lt(myLastBearishBreakdownLevel, G_Infinity)):
            if (J.lt(J.get(G_close, i_4), myLastBearishBreakdownLevel) and J.lt(J.get(G_low, i_4), myBearishLowWaterMark)):
                myCurrentTrendState = "bearish"
                myLastBearishBreakdownIndex = i_4
                myBearishLowWaterMark = J.get(G_low, i_4)
                myBearishLegReactionHigh = J.get(G_high, i_4)
        if J.seq(myCurrentTrendState, "bullish"):
            myPreviousHigh = myBullishHighWaterMark
            myBullishHighWaterMark = J.get(G_Math, "max")(myBullishHighWaterMark, J.get(G_high, i_4))
            if J.gt(J.get(G_high, i_4), myPreviousHigh):
                myBullishLegReactionLow = G_Infinity
                j_7 = myLastBullishBreakoutIndex
                while J.le(j_7, i_4):
                    myBullishLegReactionLow = J.get(G_Math, "min")(myBullishLegReactionLow, J.get(G_low, j_7))
                    j_7 = J.add(j_7, 1)
            myBarsSinceBreakout = J.sub(i_4, myLastBullishBreakoutIndex)
            if (J.ge(myBarsSinceBreakout, 2) and J.lt(J.get(G_low, i_4), myBullishLegReactionLow)):
                myCurrentTrendState = "neutral"
            elif J.ge(myBarsSinceBreakout, J.mul(neutralLookbackBars, 3)):
                myWindowStart = J.get(G_Math, "max")(0, J.add(J.sub(i_4, neutralLookbackBars), 1))
                myRecentHighestHigh = J.get(G_Math, "max")(*J.spread(J.get(G_high, "slice")(myWindowStart, J.add(i_4, 1))))
                myRecentLowestLow = J.get(G_Math, "min")(*J.spread(J.get(G_low, "slice")(myWindowStart, J.add(i_4, 1))))
                myRecentRange = J.sub(myRecentHighestHigh, myRecentLowestLow)
                myProgressThreshold = J.mul(myBullishHighWaterMark, J.sub(0.997, myBullishProgressRelaxation))
                myNoMeaningfulProgress = J.lt(myRecentHighestHigh, myProgressThreshold)
                myRangeTight = J.lt(myRecentRange, J.mul(J.sub(myBullishHighWaterMark, myRecentLowestLow), myRangeTightnessMultiplier))
                myMidpointHover = J.lt(J.get(G_Math, "abs")(J.sub(J.get(G_close, i_4), J.div(J.add(myRecentHighestHigh, myRecentLowestLow), 2))), J.mul(myRecentRange, 0.35))
                if ((J.truthy(myNoMeaningfulProgress) and J.truthy(myRangeTight)) and J.truthy(myMidpointHover)):
                    myCurrentTrendState = "neutral"
        if J.seq(myCurrentTrendState, "bearish"):
            myPreviousLow = myBearishLowWaterMark
            myBearishLowWaterMark = J.get(G_Math, "min")(myBearishLowWaterMark, J.get(G_low, i_4))
            if J.lt(J.get(G_low, i_4), myPreviousLow):
                myBearishLegReactionHigh = J.neg(G_Infinity)
                j_8 = myLastBearishBreakdownIndex
                while J.le(j_8, i_4):
                    myBearishLegReactionHigh = J.get(G_Math, "max")(myBearishLegReactionHigh, J.get(G_high, j_8))
                    j_8 = J.add(j_8, 1)
            myBarsSinceBreakdown = J.sub(i_4, myLastBearishBreakdownIndex)
            if (J.ge(myBarsSinceBreakdown, 2) and J.gt(J.get(G_high, i_4), myBearishLegReactionHigh)):
                myCurrentTrendState = "neutral"
            elif J.ge(myBarsSinceBreakdown, J.mul(neutralLookbackBars, 3)):
                myWindowStart_2 = J.get(G_Math, "max")(0, J.add(J.sub(i_4, neutralLookbackBars), 1))
                myRecentLowestLow_2 = J.get(G_Math, "min")(*J.spread(J.get(G_low, "slice")(myWindowStart_2, J.add(i_4, 1))))
                myRecentHighestHigh_2 = J.get(G_Math, "max")(*J.spread(J.get(G_high, "slice")(myWindowStart_2, J.add(i_4, 1))))
                myRecentRange_2 = J.sub(myRecentHighestHigh_2, myRecentLowestLow_2)
                myProgressThreshold_2 = J.mul(myBearishLowWaterMark, J.add(1.003, myBearishProgressRelaxation))
                myNoMeaningfulProgress_2 = J.gt(myRecentLowestLow_2, myProgressThreshold_2)
                myRangeTight_2 = J.lt(myRecentRange_2, J.mul(J.sub(myRecentHighestHigh_2, myBearishLowWaterMark), myRangeTightnessMultiplier))
                myMidpointHover_2 = J.lt(J.get(G_Math, "abs")(J.sub(J.get(G_close, i_4), J.div(J.add(myRecentHighestHigh_2, myRecentLowestLow_2), 2))), J.mul(myRecentRange_2, 0.35))
                if ((J.truthy(myNoMeaningfulProgress_2) and J.truthy(myRangeTight_2)) and J.truthy(myMidpointHover_2)):
                    myCurrentTrendState = "neutral"
        J.set(trendState, i_4, myCurrentTrendState)
        i_4 = J.add(i_4, 1)
    def _f1(_state=J.undefined, *_args):
        if J.seq(_state, "bullish"):
            return "#7bed9f"
        elif J.seq(_state, "bearish"):
            return "#ff6b81"
        else:
            return "#95a5a6"
    myCandleColors = G_for_every(trendState, _f1)
    G_color_candles(myCandleColors)
    G_paint(G_interpolate_sparse_series(myPivotHighs, "constant"), J.obj(("name", "Pivot High"), ("style", "ladder"), ("color", "#e74c3c"), ("thickness", 2)))
    G_paint(G_interpolate_sparse_series(myPivotLows, "constant"), J.obj(("name", "Pivot Low"), ("style", "ladder"), ("color", "#2ecc71"), ("thickness", 2)))
    def _f2(_marker=J.undefined, *_args):
        return (J.get(J.get(G_constants, "icons"), "triangle_up") if (_marker is not None) else None)
    bullishBreakoutIcons = G_for_every(bullishBreakoutMarker, _f2)
    def _f3(_marker=J.undefined, *_args):
        return (J.get(J.get(G_constants, "icons"), "triangle_down") if (_marker is not None) else None)
    bearishBreakdownIcons = G_for_every(bearishBreakdownMarker, _f3)
    G_paint(bullishBreakoutIcons, J.obj(("name", "Bullish Breakout"), ("style", "labels_below"), ("color", "#2ecc71")))
    G_paint(bearishBreakdownIcons, J.obj(("name", "Bearish Breakdown"), ("style", "labels_above"), ("color", "#e74c3c")))


register_store_indicator(
    script,
    name='pivot_levels_candle_color_dark_theme_TS',
    title='Pivot Levels & Candle Color (Dark Theme)',
    developer='Mat Reeves',
    url='https://trendspider.com/trading-tools-store/indicators/6a4795-pivot-levels-candle-color-dark-theme/',
    position='price',
    inputs=[{'id': 'pivot_left_bars', 'title': 'Pivot Left Bars', 'type': 'number', 'default': 10}, {'id': 'pivot_right_bars', 'title': 'Pivot Right Bars', 'type': 'number', 'default': 10}, {'id': 'neutral_lookback_bars', 'title': 'Neutral Lookback Bars', 'type': 'number', 'default': 5}],
    outputs=['cdl', 'pivot_high', 'pivot_low', 'bullish_breakout', 'bearish_breakdown'],
    signals=[],
    requires=[],
    parity='exact',
)
