"""
Ripster MTF Clouds -- TrendSpider store indicator by Ripster G.

Registered as "ripster_mtf_clouds_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/691ab7-ripster-mtf-clouds/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Promise = G["Promise"]
    G_color_cloud = G["color_cloud"]
    G_constants = G["constants"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_indicators = G["indicators"]
    G_input = G["input"]
    G_interpolate_sparse_series = G["interpolate_sparse_series"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_paint = G["paint"]
    G_request = G["request"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    G_describe_indicator("Ripster MTF Clouds", "price", J.obj(("mainColorInheritFrom", "#000000")))
    lowerTimeFrame = J.get(G_input, "select")("Lower Timeframe", "60", J.get(G_constants, "time_frames"))
    lowerShortLength = J.get(G_input, "number")("Cloud 1 Short", 34, J.obj(("min", 1), ("max", 200), ("hide_in_legend", True)))
    lowerLongLength = J.get(G_input, "number")("Cloud 1 Long", 50, J.obj(("min", 1), ("max", 200), ("hide_in_legend", True)))
    showLowerCloud = J.get(G_input, "boolean")("Show Cloud 1", True)
    higherTimeFrame = J.get(G_input, "select")("Higher Timeframe", "D", J.get(G_constants, "time_frames"))
    higherShortLength = J.get(G_input, "number")("Cloud 2 Short", 20, J.obj(("min", 1), ("max", 200), ("hide_in_legend", True)))
    higherLongLength = J.get(G_input, "number")("Cloud 2 Long", 21, J.obj(("min", 1), ("max", 200), ("hide_in_legend", True)))
    showHigherCloud = J.get(G_input, "boolean")("Show Cloud 2", True)
    thirdTimeFrame = J.get(G_input, "select")("Third Timeframe", "D", J.get(G_constants, "time_frames"))
    thirdShortLength = J.get(G_input, "number")("Cloud 3 Short", 50, J.obj(("min", 1), ("max", 200), ("hide_in_legend", True)))
    thirdLongLength = J.get(G_input, "number")("Cloud 3 Long", 55, J.obj(("min", 1), ("max", 200), ("hide_in_legend", True)))
    showThirdCloud = J.get(G_input, "boolean")("Show Cloud 3", True)
    fourthTimeFrame = J.get(G_input, "select")("Fourth Timeframe", "W", J.get(G_constants, "time_frames"))
    fourthShortLength = J.get(G_input, "number")("Cloud 4 Short", 8, J.obj(("min", 1), ("max", 200), ("hide_in_legend", True)))
    fourthLongLength = J.get(G_input, "number")("Cloud 4 Long", 9, J.obj(("min", 1), ("max", 200), ("hide_in_legend", True)))
    showFourthCloud = J.get(G_input, "boolean")("Show Cloud 4", False)
    fifthTimeFrame = J.get(G_input, "select")("Fifth Timeframe", "W", J.get(G_constants, "time_frames"))
    fifthShortLength = J.get(G_input, "number")("Cloud 5 Short", 20, J.obj(("min", 1), ("max", 200), ("hide_in_legend", True)))
    fifthLongLength = J.get(G_input, "number")("Cloud 5 Long", 21, J.obj(("min", 1), ("max", 200), ("hide_in_legend", True)))
    showFifthCloud = J.get(G_input, "boolean")("Show Cloud 5", False)
    maType = J.get(G_input, "select")("MA Type", "ema", J.JSArray(["ema", "sma", "wma", "vwma"]))
    includeExtHours = J.get(G_input, "boolean")("Include Extended Hours", True)
    _t1 = J.iter_of(J.get(G_Promise, "all")(J.JSArray([J.get(G_request, "history")(J.get(G_current, "ticker"), lowerTimeFrame, J.obj(("ext_session", includeExtHours))), J.get(G_request, "history")(J.get(G_current, "ticker"), higherTimeFrame, J.obj(("ext_session", includeExtHours))), J.get(G_request, "history")(J.get(G_current, "ticker"), thirdTimeFrame, J.obj(("ext_session", includeExtHours))), J.get(G_request, "history")(J.get(G_current, "ticker"), fourthTimeFrame, J.obj(("ext_session", includeExtHours))), J.get(G_request, "history")(J.get(G_current, "ticker"), fifthTimeFrame, J.obj(("ext_session", includeExtHours)))])))
    lowerTimeFrameData = (_t1[0] if 0 < len(_t1) else J.undefined)
    higherTimeFrameData = (_t1[1] if 1 < len(_t1) else J.undefined)
    thirdTimeFrameData = (_t1[2] if 2 < len(_t1) else J.undefined)
    fourthTimeFrameData = (_t1[3] if 3 < len(_t1) else J.undefined)
    fifthTimeFrameData = (_t1[4] if 4 < len(_t1) else J.undefined)
    lowerShortEMA = J.get(G_indicators, maType)(J.get(lowerTimeFrameData, "close"), lowerShortLength)
    lowerLongEMA = J.get(G_indicators, maType)(J.get(lowerTimeFrameData, "close"), lowerLongLength)
    higherShortEMA = J.get(G_indicators, maType)(J.get(higherTimeFrameData, "close"), higherShortLength)
    higherLongEMA = J.get(G_indicators, maType)(J.get(higherTimeFrameData, "close"), higherLongLength)
    thirdShortEMA = J.get(G_indicators, maType)(J.get(thirdTimeFrameData, "close"), thirdShortLength)
    thirdLongEMA = J.get(G_indicators, maType)(J.get(thirdTimeFrameData, "close"), thirdLongLength)
    fourthShortEMA = J.get(G_indicators, maType)(J.get(fourthTimeFrameData, "close"), fourthShortLength)
    fourthLongEMA = J.get(G_indicators, maType)(J.get(fourthTimeFrameData, "close"), fourthLongLength)
    fifthShortEMA = J.get(G_indicators, maType)(J.get(fifthTimeFrameData, "close"), fifthShortLength)
    fifthLongEMA = J.get(G_indicators, maType)(J.get(fifthTimeFrameData, "close"), fifthLongLength)
    landedLowerShortEMA = G_land_points_onto_series(J.get(lowerTimeFrameData, "time"), lowerShortEMA, G_time, "ge")
    landedLowerLongEMA = G_land_points_onto_series(J.get(lowerTimeFrameData, "time"), lowerLongEMA, G_time, "ge")
    landedHigherShortEMA = G_land_points_onto_series(J.get(higherTimeFrameData, "time"), higherShortEMA, G_time, "ge")
    landedHigherLongEMA = G_land_points_onto_series(J.get(higherTimeFrameData, "time"), higherLongEMA, G_time, "ge")
    landedThirdShortEMA = G_land_points_onto_series(J.get(thirdTimeFrameData, "time"), thirdShortEMA, G_time, "ge")
    landedThirdLongEMA = G_land_points_onto_series(J.get(thirdTimeFrameData, "time"), thirdLongEMA, G_time, "ge")
    landedFourthShortEMA = G_land_points_onto_series(J.get(fourthTimeFrameData, "time"), fourthShortEMA, G_time, "ge")
    landedFourthLongEMA = G_land_points_onto_series(J.get(fourthTimeFrameData, "time"), fourthLongEMA, G_time, "ge")
    landedFifthShortEMA = G_land_points_onto_series(J.get(fifthTimeFrameData, "time"), fifthShortEMA, G_time, "ge")
    landedFifthLongEMA = G_land_points_onto_series(J.get(fifthTimeFrameData, "time"), fifthLongEMA, G_time, "ge")
    interpolatedLowerShortEMA = G_interpolate_sparse_series(landedLowerShortEMA, "constant")
    interpolatedLowerLongEMA = G_interpolate_sparse_series(landedLowerLongEMA, "constant")
    interpolatedHigherShortEMA = G_interpolate_sparse_series(landedHigherShortEMA, "constant")
    interpolatedHigherLongEMA = G_interpolate_sparse_series(landedHigherLongEMA, "constant")
    interpolatedThirdShortEMA = G_interpolate_sparse_series(landedThirdShortEMA, "constant")
    interpolatedThirdLongEMA = G_interpolate_sparse_series(landedThirdLongEMA, "constant")
    interpolatedFourthShortEMA = G_interpolate_sparse_series(landedFourthShortEMA, "constant")
    interpolatedFourthLongEMA = G_interpolate_sparse_series(landedFourthLongEMA, "constant")
    interpolatedFifthShortEMA = G_interpolate_sparse_series(landedFifthShortEMA, "constant")
    interpolatedFifthLongEMA = G_interpolate_sparse_series(landedFifthLongEMA, "constant")
    G_color_cloud((interpolatedLowerShortEMA if J.truthy(showLowerCloud) else G_series_of(None)), (interpolatedLowerLongEMA if J.truthy(showLowerCloud) else G_series_of(None)), "rgba(0,255,0,0.5)", "rgba(255,0,0,0.5)")
    G_color_cloud((interpolatedHigherShortEMA if J.truthy(showHigherCloud) else G_series_of(None)), (interpolatedHigherLongEMA if J.truthy(showHigherCloud) else G_series_of(None)), "rgba(0,0,255,0.5)", "rgba(255,165,0,0.5)")
    G_color_cloud((interpolatedThirdShortEMA if J.truthy(showThirdCloud) else G_series_of(None)), (interpolatedThirdLongEMA if J.truthy(showThirdCloud) else G_series_of(None)), "rgba(218,165,32,0.5)", "rgba(128,0,128,0.5)")
    G_color_cloud((interpolatedFourthShortEMA if J.truthy(showFourthCloud) else G_series_of(None)), (interpolatedFourthLongEMA if J.truthy(showFourthCloud) else G_series_of(None)), "rgba(0,255,255,0.5)", "rgba(255,0,255,0.5)")
    G_color_cloud((interpolatedFifthShortEMA if J.truthy(showFifthCloud) else G_series_of(None)), (interpolatedFifthLongEMA if J.truthy(showFifthCloud) else G_series_of(None)), "rgba(255,255,0,0.5)", "rgba(0,128,128,0.5)")
    def _f2(s=J.undefined, l=J.undefined, *_args):
        return ("rgba(0,255,0,0.5)" if J.gt(s, l) else "rgba(255,0,0,0.5)")
    lowerLineColor = G_for_every(interpolatedLowerShortEMA, interpolatedLowerLongEMA, _f2)
    G_paint((interpolatedLowerShortEMA if J.truthy(showLowerCloud) else G_series_of(None)), J.obj(("name", "Cloud 1 Short"), ("color", lowerLineColor)))
    G_paint((interpolatedLowerLongEMA if J.truthy(showLowerCloud) else G_series_of(None)), J.obj(("name", "Cloud 1 Long"), ("color", lowerLineColor)))
    def _f3(s=J.undefined, l=J.undefined, *_args):
        return ("rgba(0,0,255,0.5)" if J.gt(s, l) else "rgba(255,165,0,0.5)")
    higherLineColor = G_for_every(interpolatedHigherShortEMA, interpolatedHigherLongEMA, _f3)
    G_paint((interpolatedHigherShortEMA if J.truthy(showHigherCloud) else G_series_of(None)), J.obj(("name", "Cloud 2 Short"), ("color", higherLineColor)))
    G_paint((interpolatedHigherLongEMA if J.truthy(showHigherCloud) else G_series_of(None)), J.obj(("name", "Cloud 2 Long"), ("color", higherLineColor)))
    def _f4(s=J.undefined, l=J.undefined, *_args):
        return ("rgba(218,165,32,0.5)" if J.gt(s, l) else "rgba(128,0,128,0.5)")
    thirdLineColor = G_for_every(interpolatedThirdShortEMA, interpolatedThirdLongEMA, _f4)
    G_paint((interpolatedThirdShortEMA if J.truthy(showThirdCloud) else G_series_of(None)), J.obj(("name", "Cloud 3 Short"), ("color", thirdLineColor)))
    G_paint((interpolatedThirdLongEMA if J.truthy(showThirdCloud) else G_series_of(None)), J.obj(("name", "Cloud 3 Long"), ("color", thirdLineColor)))
    def _f5(s=J.undefined, l=J.undefined, *_args):
        return ("rgba(0,255,255,0.5)" if J.gt(s, l) else "rgba(255,0,255,0.5)")
    fourthLineColor = G_for_every(interpolatedFourthShortEMA, interpolatedFourthLongEMA, _f5)
    G_paint((interpolatedFourthShortEMA if J.truthy(showFourthCloud) else G_series_of(None)), J.obj(("name", "Cloud 4 Short"), ("color", fourthLineColor)))
    G_paint((interpolatedFourthLongEMA if J.truthy(showFourthCloud) else G_series_of(None)), J.obj(("name", "Cloud 4 Long"), ("color", fourthLineColor)))
    def _f6(s=J.undefined, l=J.undefined, *_args):
        return ("rgba(255,255,0,0.5)" if J.gt(s, l) else "rgba(0,128,128,0.5)")
    fifthLineColor = G_for_every(interpolatedFifthShortEMA, interpolatedFifthLongEMA, _f6)
    G_paint((interpolatedFifthShortEMA if J.truthy(showFifthCloud) else G_series_of(None)), J.obj(("name", "Cloud 5 Short"), ("color", fifthLineColor)))
    G_paint((interpolatedFifthLongEMA if J.truthy(showFifthCloud) else G_series_of(None)), J.obj(("name", "Cloud 5 Long"), ("color", fifthLineColor)))


register_store_indicator(
    script,
    name='ripster_mtf_clouds_TS',
    title='Ripster MTF Clouds',
    developer='Ripster G',
    url='https://trendspider.com/trading-tools-store/indicators/691ab7-ripster-mtf-clouds/',
    position='price',
    inputs=[{'id': 'lower_timeframe', 'title': 'Lower Timeframe', 'type': 'select_wide', 'default': '60', 'options': ['1', '2', '3', '4', '5', '6', '10', '12', '15', '30', '45', '60', '65', '90', '120', '240', '1440', 'D', 'W', 'M', 'Q', 'Y']}, {'id': 'cloud_1_short', 'title': 'Cloud 1 Short', 'type': 'number', 'default': 34}, {'id': 'cloud_1_long', 'title': 'Cloud 1 Long', 'type': 'number', 'default': 50}, {'id': 'show_cloud_1', 'title': 'Show Cloud 1', 'type': 'boolean', 'default': True}, {'id': 'higher_timeframe', 'title': 'Higher Timeframe', 'type': 'select_wide', 'default': 'D', 'options': ['1', '2', '3', '4', '5', '6', '10', '12', '15', '30', '45', '60', '65', '90', '120', '240', '1440', 'D', 'W', 'M', 'Q', 'Y']}, {'id': 'cloud_2_short', 'title': 'Cloud 2 Short', 'type': 'number', 'default': 20}, {'id': 'cloud_2_long', 'title': 'Cloud 2 Long', 'type': 'number', 'default': 21}, {'id': 'show_cloud_2', 'title': 'Show Cloud 2', 'type': 'boolean', 'default': True}, {'id': 'third_timeframe', 'title': 'Third Timeframe', 'type': 'select_wide', 'default': 'D', 'options': ['1', '2', '3', '4', '5', '6', '10', '12', '15', '30', '45', '60', '65', '90', '120', '240', '1440', 'D', 'W', 'M', 'Q', 'Y']}, {'id': 'cloud_3_short', 'title': 'Cloud 3 Short', 'type': 'number', 'default': 50}, {'id': 'cloud_3_long', 'title': 'Cloud 3 Long', 'type': 'number', 'default': 55}, {'id': 'show_cloud_3', 'title': 'Show Cloud 3', 'type': 'boolean', 'default': True}, {'id': 'fourth_timeframe', 'title': 'Fourth Timeframe', 'type': 'select_wide', 'default': 'W', 'options': ['1', '2', '3', '4', '5', '6', '10', '12', '15', '30', '45', '60', '65', '90', '120', '240', '1440', 'D', 'W', 'M', 'Q', 'Y']}, {'id': 'cloud_4_short', 'title': 'Cloud 4 Short', 'type': 'number', 'default': 8}, {'id': 'cloud_4_long', 'title': 'Cloud 4 Long', 'type': 'number', 'default': 9}, {'id': 'show_cloud_4', 'title': 'Show Cloud 4', 'type': 'boolean', 'default': False}, {'id': 'fifth_timeframe', 'title': 'Fifth Timeframe', 'type': 'select_wide', 'default': 'W', 'options': ['1', '2', '3', '4', '5', '6', '10', '12', '15', '30', '45', '60', '65', '90', '120', '240', '1440', 'D', 'W', 'M', 'Q', 'Y']}, {'id': 'cloud_5_short', 'title': 'Cloud 5 Short', 'type': 'number', 'default': 20}, {'id': 'cloud_5_long', 'title': 'Cloud 5 Long', 'type': 'number', 'default': 21}, {'id': 'show_cloud_5', 'title': 'Show Cloud 5', 'type': 'boolean', 'default': False}, {'id': 'ma_type', 'title': 'MA Type', 'type': 'select_wide', 'default': 'ema', 'options': ['ema', 'sma', 'wma', 'vwma']}, {'id': 'include_extended_hours', 'title': 'Include Extended Hours', 'type': 'boolean', 'default': True}],
    outputs=['line_1', 'line_2', 'line_4', 'line_5', 'line_7', 'line_8', 'line_10', 'line_11', 'line_13', 'line_14', 'line_16', 'line_17', 'line_19', 'line_20', 'line_22', 'line_23', 'line_25', 'line_26', 'line_28', 'line_29', 'cloud_1_short', 'cloud_1_long', 'cloud_2_short', 'cloud_2_long', 'cloud_3_short', 'cloud_3_long', 'cloud_4_short', 'cloud_4_long', 'cloud_5_short', 'cloud_5_long'],
    signals=[],
    requires=['history'],
    parity='exact',
)
