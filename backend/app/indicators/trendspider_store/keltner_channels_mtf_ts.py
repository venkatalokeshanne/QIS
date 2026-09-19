"""
Keltner Channels (MTF) -- TrendSpider store indicator by TrendSpider Team.

Registered as "keltner_channels_mtf_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/keltner-channels-mtf/)
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
    G_color_cloud = G["color_cloud"]
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_indicators = G["indicators"]
    G_input = G["input"]
    G_interpolate_sparse_series = G["interpolate_sparse_series"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_mult = G["mult"]
    G_paint = G["paint"]
    G_request = G["request"]
    G_sub = G["sub"]
    G_time = G["time"]
    def computeATR(h=J.undefined, l=J.undefined, c=J.undefined, length=J.undefined, *_args):
        return G_atr(h, l, c, length)
    def computeKeltnerChannels(c=J.undefined, h=J.undefined, l=J.undefined, length=J.undefined, atrLength=J.undefined, multiplier=J.undefined, maType_2=J.undefined, *_args):
        midLine = J.get(G_indicators, maType_2)(c, length)
        theATR = computeATR(h, l, c, atrLength)
        upperBand = G_add(midLine, G_mult(theATR, multiplier))
        lowerBand = G_sub(midLine, G_mult(theATR, multiplier))
        return J.obj(("midLine", midLine), ("upperBand", upperBand), ("lowerBand", lowerBand))
    G_describe_indicator("Keltner Channels (Multi-Timeframe)", "price")
    lowerTimeFrame = J.get(G_input, "select")("Lower Timeframe", "60", J.get(G_constants, "time_frames"))
    lowerLength = J.get(G_input, "number")("Lower EMA Length", 20, J.obj(("min", 1), ("max", 200)))
    lowerATRLength = J.get(G_input, "number")("Lower ATR Length", 10, J.obj(("min", 1), ("max", 200)))
    lowerMultiplier = J.get(G_input, "number")("Lower Multiplier", 2, J.obj(("min", 0.5), ("max", 10), ("step", 0.5)))
    higherTimeFrame = J.get(G_input, "select")("Higher Timeframe", "D", J.get(G_constants, "time_frames"))
    higherLength = J.get(G_input, "number")("Higher EMA Length", 20, J.obj(("min", 1), ("max", 200)))
    higherATRLength = J.get(G_input, "number")("Higher ATR Length", 10, J.obj(("min", 1), ("max", 200)))
    higherMultiplier = J.get(G_input, "number")("Higher Multiplier", 2, J.obj(("min", 0.5), ("max", 10), ("step", 0.5)))
    maType = J.get(G_input, "select")("MA Type", "ema", J.JSArray(["ema", "sma", "wma", "vwma"]))
    lowerData = J.get(G_request, "history")(J.get(G_constants, "ticker"), lowerTimeFrame)
    lowerKC = computeKeltnerChannels(J.get(lowerData, "close"), J.get(lowerData, "high"), J.get(lowerData, "low"), lowerLength, lowerATRLength, lowerMultiplier, maType)
    higherData = J.get(G_request, "history")(J.get(G_constants, "ticker"), higherTimeFrame)
    higherKC = computeKeltnerChannels(J.get(higherData, "close"), J.get(higherData, "high"), J.get(higherData, "low"), higherLength, higherATRLength, higherMultiplier, maType)
    landedLowerMid = G_land_points_onto_series(J.get(lowerData, "time"), J.get(lowerKC, "midLine"), G_time)
    landedLowerUpper = G_land_points_onto_series(J.get(lowerData, "time"), J.get(lowerKC, "upperBand"), G_time)
    landedLowerLower = G_land_points_onto_series(J.get(lowerData, "time"), J.get(lowerKC, "lowerBand"), G_time)
    landedHigherMid = G_land_points_onto_series(J.get(higherData, "time"), J.get(higherKC, "midLine"), G_time)
    landedHigherUpper = G_land_points_onto_series(J.get(higherData, "time"), J.get(higherKC, "upperBand"), G_time)
    landedHigherLower = G_land_points_onto_series(J.get(higherData, "time"), J.get(higherKC, "lowerBand"), G_time)
    interpLowerMid = G_interpolate_sparse_series(landedLowerMid, "constant")
    interpLowerUpper = G_interpolate_sparse_series(landedLowerUpper, "constant")
    interpLowerLower = G_interpolate_sparse_series(landedLowerLower, "constant")
    interpHigherMid = G_interpolate_sparse_series(landedHigherMid, "constant")
    interpHigherUpper = G_interpolate_sparse_series(landedHigherUpper, "constant")
    interpHigherLower = G_interpolate_sparse_series(landedHigherLower, "constant")
    G_paint(interpLowerMid, J.obj(("name", "Lower Mid Keltner"), ("color", "grey"), ("style", "line"), ("thickness", 1)))
    G_paint(interpLowerUpper, J.obj(("name", "Lower Upper Keltner"), ("color", "grey"), ("style", "line"), ("thickness", 1)))
    G_paint(interpLowerLower, J.obj(("name", "Lower Lower Keltner"), ("color", "grey"), ("style", "line"), ("thickness", 1)))
    G_paint(interpHigherMid, J.obj(("name", "Higher Mid Keltner"), ("color", "grey"), ("style", "line"), ("thickness", 1)))
    G_paint(interpHigherUpper, J.obj(("name", "Higher Upper Keltner"), ("color", "grey"), ("style", "line"), ("thickness", 1)))
    G_paint(interpHigherLower, J.obj(("name", "Higher Lower Keltner"), ("color", "grey"), ("style", "line"), ("thickness", 1)))
    G_color_cloud(interpLowerUpper, interpLowerLower, "green", "red")
    G_color_cloud(interpHigherUpper, interpHigherLower, "blue", "orange")


register_store_indicator(
    script,
    name='keltner_channels_mtf_TS',
    title='Keltner Channels (MTF)',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/keltner-channels-mtf/',
    position='price',
    inputs=[{'id': 'lower_timeframe', 'title': 'Lower Timeframe', 'type': 'select_wide', 'default': '60', 'options': ['1', '2', '3', '4', '5', '6', '10', '12', '15', '30', '45', '60', '65', '90', '120', '240', '1440', 'D', 'W', 'M', 'Q', 'Y']}, {'id': 'lower_ema_length', 'title': 'Lower EMA Length', 'type': 'number', 'default': 20}, {'id': 'lower_atr_length', 'title': 'Lower ATR Length', 'type': 'number', 'default': 10}, {'id': 'lower_multiplier', 'title': 'Lower Multiplier', 'type': 'number', 'default': 2}, {'id': 'higher_timeframe', 'title': 'Higher Timeframe', 'type': 'select_wide', 'default': 'D', 'options': ['1', '2', '3', '4', '5', '6', '10', '12', '15', '30', '45', '60', '65', '90', '120', '240', '1440', 'D', 'W', 'M', 'Q', 'Y']}, {'id': 'higher_ema_length', 'title': 'Higher EMA Length', 'type': 'number', 'default': 20}, {'id': 'higher_atr_length', 'title': 'Higher ATR Length', 'type': 'number', 'default': 10}, {'id': 'higher_multiplier', 'title': 'Higher Multiplier', 'type': 'number', 'default': 2}, {'id': 'ma_type', 'title': 'MA Type', 'type': 'select_wide', 'default': 'ema', 'options': ['ema', 'sma', 'wma', 'vwma']}],
    outputs=['lower_mid_keltner', 'lower_upper_keltner', 'lower_lower_keltner', 'higher_mid_keltner', 'higher_upper_keltner', 'higher_lower_keltner', 'line_7', 'line_8', 'line_10', 'line_11', 'line_13', 'line_14', 'line_16', 'line_17'],
    signals=[],
    requires=['history'],
    parity='exact',
)
