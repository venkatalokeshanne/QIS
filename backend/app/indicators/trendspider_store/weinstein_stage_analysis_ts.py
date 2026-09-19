"""
Weinstein Stage Analysis -- TrendSpider store indicator by TrendSpider Team.

Registered as "weinstein_stage_analysis_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/weinstein-stage-analysis/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_assert = G["assert"]
    G_color_candles = G["color_candles"]
    G_constants = G["constants"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_indicators = G["indicators"]
    G_input = G["input"]
    G_interpolate_sparse_series = G["interpolate_sparse_series"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_mult = G["mult"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_request = G["request"]
    G_shift = G["shift"]
    G_time = G["time"]
    G_describe_indicator("Weinstein Stage Analysis")
    smaLength = J.get(G_input, "number")("MA Length", 30, J.obj(("min", 1)))
    withinRangePercent = J.get(G_input, "number")("Within Range %", 5, J.obj(("min", 0), ("max", 25)))
    maType = J.get(G_input, "select")("MA Type", "sma", J.get(G_constants, "ma_types"))
    computeMA = J.get(G_indicators, maType)
    stage2Color = J.get(G_input, "color")("Stage 2 Color", "green")
    stage3Color = J.get(G_input, "color")("Stage 3 Color", "orange")
    stage4Color = J.get(G_input, "color")("Stage 4 Color", "red")
    stage1Color = J.get(G_input, "color")("Stage 1 Color", "lightgreen")
    weeklyData = J.get(G_request, "history")(J.get(G_current, "ticker"), "W")
    G_assert((not J.truthy(J.get(weeklyData, "error"))), J.template("Error fetching weekly data: ", J.get(weeklyData, "error")))
    weeklyMA = computeMA(J.get(weeklyData, "close"), smaLength)
    withinRange = G_mult(weeklyMA, J.div(withinRangePercent, 100))
    currentTrend = ""
    def _f1(_open=J.undefined, _close=J.undefined, _pOpen=J.undefined, _pClose=J.undefined, _ma=J.undefined, _pMa=J.undefined, _withinRange=J.undefined, _prevColor=J.undefined, *_args):
        nonlocal currentTrend
        myBodyLow = J.get(G_Math, "min")(_open, _close)
        myBodyHigh = J.get(G_Math, "max")(_open, _close)
        if (J.gt(myBodyLow, J.add(_ma, _withinRange)) and J.lt(_pMa, _ma)):
            currentTrend = "upward"
            return stage2Color
        if (J.lt(myBodyHigh, J.sub(_ma, _withinRange)) and J.gt(_pMa, _ma)):
            currentTrend = "downward"
            return stage4Color
        if J.eq(currentTrend, "upward"):
            return stage3Color
        if J.eq(currentTrend, "downward"):
            return stage1Color
        return (_t1 if J.truthy(_t1 := _prevColor) else None)
    myColors = G_for_every(J.get(weeklyData, "open"), J.get(weeklyData, "close"), G_shift(J.get(weeklyData, "open"), 1), G_shift(J.get(weeklyData, "close"), 1), weeklyMA, G_shift(weeklyMA, 1), withinRange, _f1)
    myMappedColors = G_interpolate_sparse_series(G_land_points_onto_series(J.get(weeklyData, "time"), myColors, G_time, "le"), "constant")
    G_color_candles(myMappedColors)
    myMappedMA = G_land_points_onto_series(J.get(weeklyData, "time"), weeklyMA, G_time, "le")
    myInterpolatedMA = G_interpolate_sparse_series(myMappedMA, "linear")
    G_paint(myInterpolatedMA, J.obj(("name", J.template("Weekly ", J.get(maType, "toUpperCase")())), ("color", "white")))
    def _f2(_color=J.undefined, *_args):
        return (1 if J.seq(_color, stage2Color) else 0)
    myGreenSignal = G_for_every(myMappedColors, _f2)
    def _f3(_color=J.undefined, *_args):
        return (1 if J.seq(_color, stage3Color) else 0)
    myOrangeSignal = G_for_every(myMappedColors, _f3)
    def _f4(_color=J.undefined, *_args):
        return (1 if J.seq(_color, stage4Color) else 0)
    myRedSignal = G_for_every(myMappedColors, _f4)
    def _f5(_color=J.undefined, *_args):
        return (1 if J.seq(_color, stage1Color) else 0)
    myLightGreenSignal = G_for_every(myMappedColors, _f5)
    G_register_signal(myGreenSignal, "Stage 2")
    G_register_signal(myOrangeSignal, "Stage 3")
    G_register_signal(myRedSignal, "Stage 4")
    G_register_signal(myLightGreenSignal, "Stage 1")


register_store_indicator(
    script,
    name='weinstein_stage_analysis_TS',
    title='Weinstein Stage Analysis',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/weinstein-stage-analysis/',
    position='price',
    inputs=[{'id': 'ma_length', 'title': 'MA Length', 'type': 'number', 'default': 30}, {'id': 'within_range__', 'title': 'Within Range %', 'type': 'number', 'default': 5}, {'id': 'ma_type', 'title': 'MA Type', 'type': 'select_wide', 'default': 'sma', 'options': ['ema', 'sma', 'wildma', 'vwma', 'wma', 'hullma', 'kama', 'alma', 'twap']}, {'id': 'stage_2_color', 'title': 'Stage 2 Color', 'type': 'color', 'default': 'green'}, {'id': 'stage_3_color', 'title': 'Stage 3 Color', 'type': 'color', 'default': 'orange'}, {'id': 'stage_4_color', 'title': 'Stage 4 Color', 'type': 'color', 'default': 'red'}, {'id': 'stage_1_color', 'title': 'Stage 1 Color', 'type': 'color', 'default': 'lightgreen'}],
    outputs=['cdl', 'weekly_sma', 'stage_2', 'stage_3', 'stage_4', 'stage_1'],
    signals=['stage_2', 'stage_3', 'stage_4', 'stage_1'],
    requires=['history'],
    parity='exact',
)
