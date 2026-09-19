"""
Full Timeframe Continuity Candle Colors -- TrendSpider store indicator by TrendSpider Team.

Registered as "full_timeframe_continuity_candle_colors_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/full-timeframe-continuity-candle-colors/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
aapl_d: both-error, syn_5m: OK.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Error = G["Error"]
    G_Math = G["Math"]
    G_close = G["close"]
    G_color_candles = G["color_candles"]
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_input = G["input"]
    G_isNaN = G["isNaN"]
    G_library = G["library"]
    G_open = G["open"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    G_time_of = G["time_of"]
    G_describe_indicator("Full Time Frame Continuity", J.obj(("shortName", "FTFC")))
    COLOR_UNCERTAIN = "silver"
    COLOR_FTFC_UP = "rgb(44, 165, 153)"
    COLOR_FTFC_DOWN = "rgb(238, 84, 81)"
    resolution1 = G_input("TF1", 30, J.obj(("min", 5), ("max", 240)))
    resolution2 = G_input("TF2", 60, J.obj(("min", 5), ("max", 240)))
    resolution3 = G_input("TF3", 240, J.obj(("min", 5), ("max", 240)))
    minTimeFrame = J.get(G_Math, "min")(resolution1, resolution2, resolution3)
    if (J.truthy(G_isNaN(J.get(G_constants, "resolution"))) or J.gt(J.get(G_constants, "resolution"), minTimeFrame)):
        raise J.js_throw(G_Error(J.template("This indicator only works for time frames <= ", minTimeFrame, " minutes")))
    moment = G_library("moment-timezone")
    FTFCColors = G_series_of(None)
    def candleIndexAtResolution(timestamp=J.undefined, resolution=J.undefined, *_args):
        sessionStart = J.get(J.get(J.get(J.get(moment(timestamp), "hours")(J.get(J.get(J.get(G_constants, "session"), "start"), "hours")), "minutes")(J.get(J.get(J.get(G_constants, "session"), "start"), "minutes")), "seconds")(0), "milliseconds")(0)
        if J.truthy(J.get(J.get(G_constants, "session"), "overnight")):
            J.get(sessionStart, "subtract")(1, "day")
        return J.get(G_Math, "floor")(J.div(J.sub(timestamp, sessionStart), J.mul(J.mul(resolution, 60), 1000)))
    intradayResolutions = J.JSArray([resolution1, resolution2, resolution3])
    RANK_MAX = J.add(J.get(intradayResolutions, "length"), 1)
    candleStartByResolution = J.obj()
    candleIndex = 1
    while J.lt(candleIndex, J.get(G_time, "length")):
        FTFCRank = 0
        for resolution in J.iter_of(intradayResolutions):
            if J.ne(candleIndexAtResolution(J.mul(J.get(G_time, candleIndex), 1000), resolution), candleIndexAtResolution(J.mul(J.get(G_time, J.sub(candleIndex, 1)), 1000), resolution)):
                J.set(candleStartByResolution, resolution, candleIndex)
            if J.truthy(J.get(candleStartByResolution, resolution)):
                if J.gt(J.get(G_close, candleIndex), J.get(G_open, J.get(candleStartByResolution, resolution))):
                    FTFCRank = J.add(FTFCRank, 1)
                else:
                    FTFCRank = J.sub(FTFCRank, 1)
        if J.ne(J.get(G_time_of(J.get(G_time, candleIndex)), "dayOfYear"), J.get(G_time_of(J.get(G_time, J.sub(candleIndex, 1))), "dayOfYear")):
            J.set(candleStartByResolution, "D", candleIndex)
        if J.truthy(J.get(candleStartByResolution, "D")):
            currentDailyCandleOpen = J.get(G_open, J.get(candleStartByResolution, "D"))
            currentDailyCandleClose = J.get(G_close, candleIndex)
            if J.gt(currentDailyCandleClose, currentDailyCandleOpen):
                FTFCRank = J.add(FTFCRank, 1)
            else:
                FTFCRank = J.sub(FTFCRank, 1)
        def _f1(*_args):
            if J.eq(FTFCRank, J.neg(RANK_MAX)):
                return COLOR_FTFC_DOWN
            if J.eq(FTFCRank, RANK_MAX):
                return COLOR_FTFC_UP
            return COLOR_UNCERTAIN
        J.set(FTFCColors, candleIndex, _f1())
        candleIndex = J.add(candleIndex, 1)
    G_color_candles(FTFCColors)


register_store_indicator(
    script,
    name='full_timeframe_continuity_candle_colors_TS',
    title='Full Timeframe Continuity Candle Colors',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/full-timeframe-continuity-candle-colors/',
    position='price',
    inputs=[{'id': 'tf1', 'title': 'TF1', 'type': 'number', 'default': 30}, {'id': 'tf2', 'title': 'TF2', 'type': 'number', 'default': 60}, {'id': 'tf3', 'title': 'TF3', 'type': 'number', 'default': 240}],
    outputs=[],
    signals=[],
    requires=[],
    parity='aapl_d: both-error, syn_5m: OK',
)
