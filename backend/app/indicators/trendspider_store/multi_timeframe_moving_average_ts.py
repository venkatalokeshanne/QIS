"""
Multi-Timeframe Moving Average -- TrendSpider store indicator by TrendSpider Team.

Registered as "multi_timeframe_moving_average_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/multi-timeframe-moving-average/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_assert = G["assert"]
    G_close = G["close"]
    G_color_candles = G["color_candles"]
    G_constants = G["constants"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_indicators = G["indicators"]
    G_input = G["input"]
    G_interpolate_sparse_series = G["interpolate_sparse_series"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_open = G["open"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_request = G["request"]
    G_time = G["time"]
    G_describe_indicator("Multi-Timeframe Moving Average")
    myMaLength = J.get(G_input, "number")("MA Length", 20, J.obj(("min", 1)))
    myMaType = J.get(G_input, "select")("MA Type", "sma", J.get(G_constants, "ma_types"))
    myTf1 = J.get(G_input, "select")("Timeframe 1", "5", J.get(G_constants, "time_frames"))
    myTf2 = J.get(G_input, "select")("Timeframe 2", "15", J.get(G_constants, "time_frames"))
    myTf3 = J.get(G_input, "select")("Timeframe 3", "30", J.get(G_constants, "time_frames"))
    myTf4 = J.get(G_input, "select")("Timeframe 4", "60", J.get(G_constants, "time_frames"))
    myTf5 = J.get(G_input, "select")("Timeframe 5", "120", J.get(G_constants, "time_frames"))
    myShowMa1 = J.get(G_input, "boolean")("Show MA 1", True)
    myShowMa2 = J.get(G_input, "boolean")("Show MA 2", True)
    myShowMa3 = J.get(G_input, "boolean")("Show MA 3", True)
    myShowMa4 = J.get(G_input, "boolean")("Show MA 4", True)
    myShowMa5 = J.get(G_input, "boolean")("Show MA 5", True)
    def calculateMA(_timeframe=J.undefined, *_args):
        myData = J.get(G_request, "history")(J.get(G_current, "ticker"), _timeframe)
        G_assert((not J.truthy(J.get(myData, "error"))), J.template("Error fetching data for ", _timeframe, " timeframe: ", J.get(myData, "error")))
        myMa = J.get(G_indicators, myMaType)(J.get(myData, "close"), myMaLength)
        myMaLanded = G_land_points_onto_series(J.get(myData, "time"), myMa, G_time, "le")
        return G_interpolate_sparse_series(myMaLanded, "constant")
    myMa1 = calculateMA(myTf1)
    myMa2 = calculateMA(myTf2)
    myMa3 = calculateMA(myTf3)
    myMa4 = calculateMA(myTf4)
    myMa5 = calculateMA(myTf5)
    def _f1(_open=J.undefined, _close=J.undefined, _ma1=J.undefined, _ma2=J.undefined, _ma3=J.undefined, _ma4=J.undefined, _ma5=J.undefined, *_args):
        maValues = J.JSArray([_ma1, _ma2, _ma3, _ma4, _ma5])
        def _f1(ma=J.undefined, *_args):
            return (J.gt(_close, ma) if J.truthy(_t1 := J.gt(_open, ma)) else _t1)
        def _f2(ma=J.undefined, *_args):
            return (J.lt(_close, ma) if J.truthy(_t1 := J.lt(_open, ma)) else _t1)
        if J.truthy(J.get(maValues, "every")(_f1)):
            return "green"
        elif J.truthy(J.get(maValues, "every")(_f2)):
            return "red"
        else:
            return "gray"
    myCandleColors = G_for_every(G_open, G_close, myMa1, myMa2, myMa3, myMa4, myMa5, _f1)
    G_color_candles(myCandleColors)
    if J.truthy(myShowMa1):
        G_paint(myMa1, J.obj(("color", "blue"), ("name", J.template("MA ", myTf1))))
    if J.truthy(myShowMa2):
        G_paint(myMa2, J.obj(("color", "red"), ("name", J.template("MA ", myTf2))))
    if J.truthy(myShowMa3):
        G_paint(myMa3, J.obj(("color", "green"), ("name", J.template("MA ", myTf3))))
    if J.truthy(myShowMa4):
        G_paint(myMa4, J.obj(("color", "purple"), ("name", J.template("MA ", myTf4))))
    if J.truthy(myShowMa5):
        G_paint(myMa5, J.obj(("color", "orange"), ("name", J.template("MA ", myTf5))))
    def _f2(_color=J.undefined, *_args):
        return (1 if J.seq(_color, "green") else 0)
    myGreenSignal = G_for_every(myCandleColors, _f2)
    def _f3(_color=J.undefined, *_args):
        return (1 if J.seq(_color, "red") else 0)
    myRedSignal = G_for_every(myCandleColors, _f3)
    G_register_signal(myGreenSignal, "Green Candle Signal")
    G_register_signal(myRedSignal, "Red Candle Signal")


register_store_indicator(
    script,
    name='multi_timeframe_moving_average_TS',
    title='Multi-Timeframe Moving Average',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/multi-timeframe-moving-average/',
    position='price',
    inputs=[{'id': 'ma_length', 'title': 'MA Length', 'type': 'number', 'default': 20}, {'id': 'ma_type', 'title': 'MA Type', 'type': 'select_wide', 'default': 'sma', 'options': ['ema', 'sma', 'wildma', 'vwma', 'wma', 'hullma', 'kama', 'alma', 'twap']}, {'id': 'timeframe_1', 'title': 'Timeframe 1', 'type': 'select_wide', 'default': '5', 'options': ['1', '2', '3', '4', '5', '6', '10', '12', '15', '30', '45', '60', '65', '90', '120', '240', '1440', 'D', 'W', 'M', 'Q', 'Y']}, {'id': 'timeframe_2', 'title': 'Timeframe 2', 'type': 'select_wide', 'default': '15', 'options': ['1', '2', '3', '4', '5', '6', '10', '12', '15', '30', '45', '60', '65', '90', '120', '240', '1440', 'D', 'W', 'M', 'Q', 'Y']}, {'id': 'timeframe_3', 'title': 'Timeframe 3', 'type': 'select_wide', 'default': '30', 'options': ['1', '2', '3', '4', '5', '6', '10', '12', '15', '30', '45', '60', '65', '90', '120', '240', '1440', 'D', 'W', 'M', 'Q', 'Y']}, {'id': 'timeframe_4', 'title': 'Timeframe 4', 'type': 'select_wide', 'default': '60', 'options': ['1', '2', '3', '4', '5', '6', '10', '12', '15', '30', '45', '60', '65', '90', '120', '240', '1440', 'D', 'W', 'M', 'Q', 'Y']}, {'id': 'timeframe_5', 'title': 'Timeframe 5', 'type': 'select_wide', 'default': '120', 'options': ['1', '2', '3', '4', '5', '6', '10', '12', '15', '30', '45', '60', '65', '90', '120', '240', '1440', 'D', 'W', 'M', 'Q', 'Y']}, {'id': 'show_ma_1', 'title': 'Show MA 1', 'type': 'boolean', 'default': True}, {'id': 'show_ma_2', 'title': 'Show MA 2', 'type': 'boolean', 'default': True}, {'id': 'show_ma_3', 'title': 'Show MA 3', 'type': 'boolean', 'default': True}, {'id': 'show_ma_4', 'title': 'Show MA 4', 'type': 'boolean', 'default': True}, {'id': 'show_ma_5', 'title': 'Show MA 5', 'type': 'boolean', 'default': True}],
    outputs=['cdl', 'ma_5', 'ma_15', 'ma_30', 'ma_60', 'ma_120', 'green_candle_signal', 'red_candle_signal'],
    signals=['green_candle_signal', 'red_candle_signal'],
    requires=['history'],
    parity='exact',
)
