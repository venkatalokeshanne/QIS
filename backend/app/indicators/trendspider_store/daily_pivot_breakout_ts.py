"""
Daily Pivot Breakout -- TrendSpider store indicator by Mike.

Registered as "daily_pivot_breakout_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/69c15c-daily-pivot-breakout-strategy-indicator/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
aapl_d: OK, syn_5m: both-error.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_assert = G["assert"]
    G_color_candles = G["color_candles"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_input = G["input"]
    G_interpolate_sparse_series = G["interpolate_sparse_series"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_request = G["request"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    def isDailyPivotHigh(idx=J.undefined, *_args):
        if (J.lt(J.sub(idx, leftStrength), 0) or J.ge(J.add(idx, rightStrength), J.get(J.get(dailyData, "high"), "length"))):
            return False
        ph = J.get(J.get(dailyData, "high"), idx)
        j_2 = J.sub(idx, leftStrength)
        while J.le(j_2, J.add(idx, rightStrength)):
            if J.seq(j_2, idx):
                j_2 = J.inc(j_2)
                continue
            if J.le(ph, J.get(J.get(dailyData, "high"), j_2)):
                return False
            j_2 = J.inc(j_2)
        return True
    def getMostRecentPivot(currentBar=J.undefined, *_args):
        lookback = rightStrength
        while J.le(lookback, J.get(G_Math, "min")(pivotLookback, currentBar)):
            pivotBar = J.sub(currentBar, lookback)
            if (J.ge(pivotBar, 0) and (J.get(dailySwingHigh, pivotBar) is not None)):
                return J.get(dailySwingHigh, pivotBar)
            lookback = J.inc(lookback)
        return None
    G_describe_indicator("Daily Pivot Breakout")
    leftStrength = J.get(G_input, "number")("Left Strength", 5, J.obj(("min", 1)))
    rightStrength = J.get(G_input, "number")("Right Strength", 5, J.obj(("min", 1)))
    pivotLookback = J.get(G_input, "number")("Pivot Lookback", 100, J.obj(("min", 1)))
    rocPeriod = J.get(G_input, "number")("ROC Period (days)", 100, J.obj(("min", 1)))
    minimumROC = J.get(G_input, "number")("Minimum ROC (%)", 30, J.obj(("min", 0)))
    rvolPeriod = J.get(G_input, "number")("RVOL Period (days)", 20, J.obj(("min", 1)))
    minimumRVOL = J.get(G_input, "number")("Minimum Daily RVOL (0 = Off)", 1, J.obj(("min", 0)))
    emaLength = J.get(G_input, "number")("EMA Length", 100, J.obj(("min", 1), ("max", 2000)))
    slopeLookback = J.get(G_input, "number")("EMA Slope Lookback", 100, J.obj(("min", 1), ("max", 2000)))
    smoothLen = J.get(G_input, "number")("EMA Smooth Length", 1, J.obj(("min", 1), ("max", 200)))
    minimumEmaSlope = J.get(G_input, "number")("Min EMA Slope %", 20, J.obj(("min", (-100))))
    trailingStopPercent = J.get(G_input, "number")("Trailing Stop Percent", 20, J.obj(("min", 0.1), ("max", 99)))
    trailingStopMultiplier = J.sub(1, J.div(trailingStopPercent, 100))
    enableCandleColors = J.get(G_input, "boolean")("Enable Momentum Candle Colors", True)
    dailyData = J.get(G_request, "history")(J.get(G_current, "ticker"), "D")
    G_assert((not J.truthy(J.get(dailyData, "error"))), J.template("Error fetching daily data: ", J.get(dailyData, "error")))
    G_assert(J.ge(J.get(J.get(dailyData, "close"), "length"), J.get(G_Math, "max")(rocPeriod, rvolPeriod, pivotLookback)), J.template("Insufficient daily data. Need at least ", J.get(G_Math, "max")(rocPeriod, rvolPeriod, pivotLookback), " days"))
    dailyROC = G_series_of(0)
    i = rocPeriod
    while J.lt(i, J.get(J.get(dailyData, "close"), "length")):
        if J.sne(J.get(J.get(dailyData, "close"), J.sub(i, rocPeriod)), 0):
            J.set(dailyROC, i, J.mul(J.div(J.sub(J.get(J.get(dailyData, "close"), i), J.get(J.get(dailyData, "close"), J.sub(i, rocPeriod))), J.get(J.get(dailyData, "close"), J.sub(i, rocPeriod))), 100))
        else:
            J.set(dailyROC, i, 0)
        i = J.inc(i)
    dailyEMA = G_series_of(None)
    emaMultiplier = J.div(2, J.add(emaLength, 1))
    i_2 = 0
    while J.lt(i_2, J.get(J.get(dailyData, "close"), "length")):
        if J.seq(i_2, 0):
            J.set(dailyEMA, i_2, J.get(J.get(dailyData, "close"), i_2))
        else:
            J.set(dailyEMA, i_2, J.add(J.mul(J.sub(J.get(J.get(dailyData, "close"), i_2), J.get(dailyEMA, J.sub(i_2, 1))), emaMultiplier), J.get(dailyEMA, J.sub(i_2, 1))))
        i_2 = J.inc(i_2)
    dailyEmaSlope = G_series_of(None)
    i_3 = slopeLookback
    while J.lt(i_3, J.get(J.get(dailyData, "close"), "length")):
        pastEMA = J.get(dailyEMA, J.sub(i_3, slopeLookback))
        currEMA = J.get(dailyEMA, i_3)
        if (((pastEMA is not None) and J.sne(pastEMA, 0)) and (currEMA is not None)):
            J.set(dailyEmaSlope, i_3, J.mul(J.div(J.sub(currEMA, pastEMA), pastEMA), 100))
        i_3 = J.inc(i_3)
    dailyEmaSlopeSmoothed = G_series_of(None)
    i_4 = J.sub(J.add(slopeLookback, smoothLen), 1)
    while J.lt(i_4, J.get(J.get(dailyData, "close"), "length")):
        slopeTotal = 0
        slopeCount = 0
        j = J.add(J.sub(i_4, smoothLen), 1)
        while J.le(j, i_4):
            if (J.get(dailyEmaSlope, j) is not None):
                slopeTotal = J.add(slopeTotal, J.get(dailyEmaSlope, j))
                slopeCount = J.inc(slopeCount)
            j = J.inc(j)
        if J.seq(slopeCount, smoothLen):
            J.set(dailyEmaSlopeSmoothed, i_4, J.div(slopeTotal, smoothLen))
        i_4 = J.inc(i_4)
    dailyColorState = G_series_of(None)
    i_5 = 0
    while J.lt(i_5, J.get(J.get(dailyData, "close"), "length")):
        rocVal = J.get(dailyROC, i_5)
        emaVal = J.get(dailyEmaSlopeSmoothed, i_5)
        rocBull = J.ge(rocVal, minimumROC)
        rocBear = J.le(rocVal, J.neg(minimumROC))
        emaHasVal = ((emaVal is not J.undefined) if J.truthy(_t1 := (emaVal is not None)) else _t1)
        emaBull = (J.ge(emaVal, minimumEmaSlope) if J.truthy(_t2 := emaHasVal) else _t2)
        emaBear = (J.le(emaVal, J.neg(minimumEmaSlope)) if J.truthy(_t3 := emaHasVal) else _t3)
        if (J.truthy(rocBull) and J.truthy(emaBull)):
            J.set(dailyColorState, i_5, "#16C172")
        elif (J.truthy(rocBear) and J.truthy(emaBear)):
            J.set(dailyColorState, i_5, "#FF3B30")
        elif ((J.truthy(rocBull) and J.truthy(emaBear)) or (J.truthy(rocBear) and J.truthy(emaBull))):
            J.set(dailyColorState, i_5, "#AF52DE")
        elif (J.truthy(rocBull) or J.truthy(emaBull)):
            J.set(dailyColorState, i_5, "#00BCFF")
        elif (J.truthy(rocBear) or J.truthy(emaBear)):
            J.set(dailyColorState, i_5, "#FF9F0A")
        else:
            J.set(dailyColorState, i_5, "#8E8E93")
        i_5 = J.inc(i_5)
    dailyRVOL = G_series_of(0)
    i_6 = rvolPeriod
    while J.lt(i_6, J.get(J.get(dailyData, "volume"), "length")):
        def _f4(sum=J.undefined, vol=J.undefined, *_args):
            return J.add(sum, vol)
        avgVolume = J.div(J.get(J.get(J.get(dailyData, "volume"), "slice")(J.sub(i_6, rvolPeriod), i_6), "reduce")(_f4, 0), rvolPeriod)
        if J.sne(avgVolume, 0):
            J.set(dailyRVOL, i_6, J.div(J.get(J.get(dailyData, "volume"), i_6), avgVolume))
        else:
            J.set(dailyRVOL, i_6, 0)
        i_6 = J.inc(i_6)
    dailySwingHigh = G_series_of(None)
    dailySwingHighBarIndex = G_series_of(None)
    b = 0
    while J.lt(b, J.get(J.get(dailyData, "high"), "length")):
        if J.truthy(isDailyPivotHigh(b)):
            J.set(dailySwingHigh, b, J.get(J.get(dailyData, "high"), b))
            J.set(dailySwingHighBarIndex, b, b)
        b = J.inc(b)
    dailySignals = G_series_of(False)
    lastPivotHigh = None
    firedForPivot = False
    i_7 = 1
    while J.lt(i_7, J.get(J.get(dailyData, "close"), "length")):
        ph = getMostRecentPivot(i_7)
        if (((ph is not None) and J.sne(ph, (-1))) and J.sne(ph, lastPivotHigh)):
            lastPivotHigh = ph
            firedForPivot = False
        if (((((lastPivotHigh is not None) and J.gt(lastPivotHigh, 0)) and J.le(J.get(J.get(dailyData, "close"), J.sub(i_7, 1)), lastPivotHigh)) and J.gt(J.get(J.get(dailyData, "close"), i_7), lastPivotHigh)) and (not J.truthy(firedForPivot))):
            rocFilter = J.ge(J.get(dailyROC, i_7), minimumROC)
            emaSlopeFilter = (J.ge(J.get(dailyEmaSlopeSmoothed, i_7), minimumEmaSlope) if J.truthy(_t5 := (J.get(dailyEmaSlopeSmoothed, i_7) is not None)) else _t5)
            rvolFilter = (_t6 if J.truthy(_t6 := J.le(minimumRVOL, 0)) else J.gt(J.get(dailyRVOL, i_7), minimumRVOL))
            momentumFilter = (_t7 if J.truthy(_t7 := rocFilter) else emaSlopeFilter)
            if (J.truthy(momentumFilter) and J.truthy(rvolFilter)):
                J.set(dailySignals, i_7, True)
                firedForPivot = True
        i_7 = J.inc(i_7)
    dailyPivPrice = G_series_of(None)
    i_8 = 0
    while J.lt(i_8, J.get(J.get(dailyData, "close"), "length")):
        J.set(dailyPivPrice, i_8, getMostRecentPivot(i_8))
        i_8 = J.inc(i_8)
    dailyStopLevel = G_series_of(None)
    activePosition = J.obj(("isActive", False), ("entryBar", None), ("entryPrice", None), ("highestPrice", None), ("stopLevel", None), ("stopHitBar", None))
    i_9 = 1
    while J.lt(i_9, J.get(J.get(dailyData, "close"), "length")):
        if (J.seq(J.get(dailySignals, J.sub(i_9, 1)), True) and (not J.truthy(J.get(activePosition, "isActive")))):
            J.set(activePosition, "isActive", True)
            J.set(activePosition, "entryBar", i_9)
            J.set(activePosition, "entryPrice", J.get(J.get(dailyData, "open"), i_9))
            J.set(activePosition, "highestPrice", J.get(J.get(dailyData, "open"), i_9))
            J.set(activePosition, "stopLevel", J.mul(J.get(activePosition, "highestPrice"), trailingStopMultiplier))
            J.set(activePosition, "stopHitBar", None)
        if J.truthy(J.get(activePosition, "isActive")):
            isEntryBar = J.seq(i_9, J.get(activePosition, "entryBar"))
            if ((not J.truthy(isEntryBar)) and (J.get(activePosition, "stopHitBar") is None)):
                if J.le(J.get(J.get(dailyData, "low"), J.sub(i_9, 1)), J.get(activePosition, "stopLevel")):
                    J.set(activePosition, "stopHitBar", J.sub(i_9, 1))
            if (J.get(activePosition, "stopHitBar") is None):
                if J.gt(J.get(J.get(dailyData, "high"), J.sub(i_9, 1)), J.get(activePosition, "highestPrice")):
                    J.set(activePosition, "highestPrice", J.get(J.get(dailyData, "high"), J.sub(i_9, 1)))
                    J.set(activePosition, "stopLevel", J.mul(J.get(activePosition, "highestPrice"), trailingStopMultiplier))
            if ((J.get(activePosition, "stopHitBar") is None) or J.le(i_9, J.add(J.get(activePosition, "stopHitBar"), 1))):
                J.set(dailyStopLevel, i_9, J.get(activePosition, "stopLevel"))
            else:
                J.set(dailyStopLevel, i_9, None)
            if ((J.get(activePosition, "stopHitBar") is not None) and J.gt(i_9, J.add(J.get(activePosition, "stopHitBar"), 1))):
                J.set(activePosition, "isActive", False)
        i_9 = J.inc(i_9)
    mappedPivotPrice = G_interpolate_sparse_series(G_land_points_onto_series(J.get(dailyData, "time"), dailyPivPrice, G_time, "le"), "constant")
    mappedTrailingStop = G_land_points_onto_series(J.get(dailyData, "time"), dailyStopLevel, G_time, "le")
    mappedCandleColor = G_interpolate_sparse_series(G_land_points_onto_series(J.get(dailyData, "time"), dailyColorState, G_time, "le"), "constant")
    mappedSignals_Day0 = G_land_points_onto_series(J.get(dailyData, "time"), dailySignals, G_time, "le")
    dailySignalsNextDay = G_series_of(False)
    i_10 = 0
    while J.lt(i_10, J.sub(J.get(J.get(dailyData, "time"), "length"), 1)):
        if J.seq(J.get(dailySignals, i_10), True):
            J.set(dailySignalsNextDay, J.add(i_10, 1), True)
        i_10 = J.inc(i_10)
    mappedSignals = G_land_points_onto_series(J.get(dailyData, "time"), dailySignalsNextDay, G_time, "le")
    entrySignals = G_series_of(None)
    entryLabels = G_series_of(None)
    i_11 = 1
    while J.lt(i_11, J.get(G_time, "length")):
        if J.seq(J.get(mappedSignals, i_11), True):
            currentTime = J.get(G_time, i_11)
            prevTime = J.get(G_time, J.sub(i_11, 1))
            currentDayStart = J.mul(J.get(G_Math, "floor")(J.div(currentTime, J.mul(J.mul(24, 60), 60))), J.mul(J.mul(24, 60), 60))
            prevDayStart = J.mul(J.get(G_Math, "floor")(J.div(prevTime, J.mul(J.mul(24, 60), 60))), J.mul(J.mul(24, 60), 60))
            isFirstCandleOfDay = J.gt(currentDayStart, prevDayStart)
            if J.truthy(isFirstCandleOfDay):
                J.set(entrySignals, i_11, True)
                J.set(entryLabels, i_11, "▲ Breakout")
        i_11 = J.inc(i_11)
    G_paint(mappedPivotPrice, J.obj(("name", "Pivot High"), ("color", "#16c172"), ("style", "line"), ("width", 2), ("ignoreWhenScaling", True)))
    G_paint(mappedTrailingStop, J.obj(("name", "Trailing Stop"), ("color", "#00BCFF"), ("style", "dotted"), ("thickness", 2), ("ignoreWhenScaling", True)))
    G_paint(entryLabels, J.obj(("name", "Entry Signals"), ("style", "labels_below"), ("color", "green"), ("backgroundColor", "green"), ("fontSize", 14), ("verticalOffset", 15), ("ignoreWhenScaling", True)))
    if J.truthy(enableCandleColors):
        G_color_candles(mappedCandleColor)
    G_register_signal(entrySignals, "5PivotBreakout_Strategy")
    G_register_signal(mappedSignals_Day0, "5PivotBreakout_Scan")


register_store_indicator(
    script,
    name='daily_pivot_breakout_TS',
    title='Daily Pivot Breakout',
    developer='Mike',
    url='https://trendspider.com/trading-tools-store/indicators/69c15c-daily-pivot-breakout-strategy-indicator/',
    position='price',
    inputs=[{'id': 'left_strength', 'title': 'Left Strength', 'type': 'number', 'default': 5}, {'id': 'right_strength', 'title': 'Right Strength', 'type': 'number', 'default': 5}, {'id': 'pivot_lookback', 'title': 'Pivot Lookback', 'type': 'number', 'default': 100}, {'id': 'roc_period__days_', 'title': 'ROC Period (days)', 'type': 'number', 'default': 100}, {'id': 'minimum_roc____', 'title': 'Minimum ROC (%)', 'type': 'number', 'default': 30}, {'id': 'rvol_period__days_', 'title': 'RVOL Period (days)', 'type': 'number', 'default': 20}, {'id': 'minimum_daily_rvol__0___off_', 'title': 'Minimum Daily RVOL (0 = Off)', 'type': 'number', 'default': 1}, {'id': 'ema_length', 'title': 'EMA Length', 'type': 'number', 'default': 100}, {'id': 'ema_slope_lookback', 'title': 'EMA Slope Lookback', 'type': 'number', 'default': 100}, {'id': 'ema_smooth_length', 'title': 'EMA Smooth Length', 'type': 'number', 'default': 1}, {'id': 'min_ema_slope__', 'title': 'Min EMA Slope %', 'type': 'number', 'default': 20}, {'id': 'trailing_stop_percent', 'title': 'Trailing Stop Percent', 'type': 'number', 'default': 20}, {'id': 'enable_momentum_candle_colors', 'title': 'Enable Momentum Candle Colors', 'type': 'boolean', 'default': True}],
    outputs=['pivot_high', 'trailing_stop', 'entry_signals', 'cdl', '5pivotbreakout_strategy', '5pivotbreakout_scan'],
    signals=['5pivotbreakout_strategy', '5pivotbreakout_scan'],
    requires=['history'],
    parity='aapl_d: OK, syn_5m: both-error',
)
