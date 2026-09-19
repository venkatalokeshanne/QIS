"""
Fearzone - Contrarian Indicator (Zeiierman) -- TrendSpider store indicator by Zeiierman Trading.

Registered as "fearzone_contrarian_indicator_zeiierman_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68f10f-fearzone-contrarian-indicator/)
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
    G_close = G["close"]
    G_color_candles = G["color_candles"]
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_highest = G["highest"]
    G_indicators = G["indicators"]
    G_input = G["input"]
    G_low = G["low"]
    G_market = G["market"]
    G_mult = G["mult"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_stdev = G["stdev"]
    G_sub = G["sub"]
    G_describe_indicator("Fearzone - Contrarian Indicator (Zeiierman)", "price", J.obj(("shortName", "Fearzone (Zeiierman)")))
    mySource = J.get(G_input, "select")("Source", "ohlc4", J.get(G_constants, "price_source_options"))
    myPrice = J.get(G_market, mySource)
    myHighPeriod = J.get(G_input, "number")("High Period", 30, J.obj(("min", 1), ("max", 500)))
    myStdevPeriod = J.get(G_input, "number")("Stdev Period", 50, J.obj(("min", 1), ("max", 500)))
    myMaType = J.get(G_input, "select")("Select Moving Average", "wma", J.get(G_constants, "ma_types"))
    myAlertCircle = J.get(G_input, "boolean")("Show FearZone Circle?", True)
    myAlertCircleColor = J.get(G_input, "color")("FearZone Circle Color", "#FC6C85")
    myColorCandles = J.get(G_input, "boolean")("Color Candles in FearZone?", True)
    myCandleColor = J.get(G_input, "color")("Candle Color in FearZone", "red")
    myComputeMA = J.get(G_indicators, myMaType)
    def myCalcFZ1(_source=J.undefined, _highPeriod=J.undefined, _stdevPeriod=J.undefined, *_args):
        myHighestSource = G_highest(_source, _highPeriod)
        def _f1(_s=J.undefined, _h=J.undefined, *_args):
            return J.div(J.sub(_h, _s), _h)
        myFZ1_2 = G_for_every(_source, myHighestSource, _f1)
        myAVG1 = myComputeMA(myFZ1_2, _stdevPeriod)
        mySTDEV1 = G_stdev(myFZ1_2, _stdevPeriod)
        myFZ1Limit_2 = G_add(myAVG1, mySTDEV1)
        return J.obj(("myFZ1", myFZ1_2), ("myFZ1Limit", myFZ1Limit_2))
    def myCalcFZ2(_source=J.undefined, _highPeriod=J.undefined, _stdevPeriod=J.undefined, *_args):
        myFZ2_2 = myComputeMA(_source, _highPeriod)
        myAVG2 = myComputeMA(myFZ2_2, _stdevPeriod)
        mySTDEV2 = G_stdev(myFZ2_2, _stdevPeriod)
        myFZ2Limit_2 = G_sub(myAVG2, mySTDEV2)
        return J.obj(("myFZ2", myFZ2_2), ("myFZ2Limit", myFZ2Limit_2))
    _t1 = J.require_object(myCalcFZ1(myPrice, myHighPeriod, myStdevPeriod))
    myFZ1 = J.get(_t1, "myFZ1")
    myFZ1Limit = J.get(_t1, "myFZ1Limit")
    _t2 = J.require_object(myCalcFZ2(myPrice, myHighPeriod, myStdevPeriod))
    myFZ2 = J.get(_t2, "myFZ2")
    myFZ2Limit = J.get(_t2, "myFZ2Limit")
    def _f3(_fz1=J.undefined, _fz1Limit=J.undefined, _fz2=J.undefined, _fz2Limit=J.undefined, *_args):
        return (J.lt(_fz2, _fz2Limit) if J.truthy(_t1 := J.gt(_fz1, _fz1Limit)) else _t1)
    myFearzoneCondition = G_for_every(myFZ1, myFZ1Limit, myFZ2, myFZ2Limit, _f3)
    def _f4(_condition=J.undefined, *_args):
        return (myCandleColor if (J.truthy(_condition) and J.truthy(myColorCandles)) else None)
    myCandleColors = G_for_every(myFearzoneCondition, _f4)
    G_color_candles(myCandleColors)
    def _f5(_h=J.undefined, _l=J.undefined, _c=J.undefined, _prevOutput=J.undefined, _index=J.undefined, *_args):
        if J.seq(_index, 0):
            return J.sub(_h, _l)
        myPrevClose = J.get(G_close, J.sub(_index, 1))
        return J.get(G_Math, "max")(J.sub(_h, _l), J.get(G_Math, "abs")(J.sub(_h, myPrevClose)), J.get(G_Math, "abs")(J.sub(_l, myPrevClose)))
    myTrueRange = G_for_every(G_high, G_low, G_close, _f5)
    myBubbleSize = G_mult(myTrueRange, 0.3)
    def _f6(_condition=J.undefined, _low=J.undefined, *_args):
        return (_low if J.truthy(_condition) else None)
    myBubbleTop = G_for_every(myFearzoneCondition, G_low, _f6)
    def _f7(_condition=J.undefined, _low=J.undefined, _bubbleSize=J.undefined, *_args):
        return (J.sub(_low, _bubbleSize) if J.truthy(_condition) else None)
    myBubbleBottom = G_for_every(myFearzoneCondition, G_low, myBubbleSize, _f7)
    def _f8(_condition=J.undefined, *_args):
        return (J.get(J.get(G_constants, "icons"), "circle") if (J.truthy(_condition) and J.truthy(myAlertCircle)) else None)
    myAlertCircleValues = G_for_every(myFearzoneCondition, _f8)
    G_paint(myAlertCircleValues, J.obj(("style", "labels_below"), ("color", myAlertCircleColor), ("name", "FearZone Circles")))
    def _f9(_condition=J.undefined, _prevOutput=J.undefined, _index=J.undefined, *_args):
        if J.seq(_index, 0):
            return False
        myPrevCondition = J.get(myFearzoneCondition, J.sub(_index, 1))
        return ((not J.truthy(myPrevCondition)) if J.truthy(_t1 := _condition) else _t1)
    myFearZoneSignal = G_for_every(myFearzoneCondition, _f9)
    G_register_signal(myFearZoneSignal, "FearZone detected")


register_store_indicator(
    script,
    name='fearzone_contrarian_indicator_zeiierman_TS',
    title='Fearzone - Contrarian Indicator (Zeiierman)',
    developer='Zeiierman Trading',
    url='https://trendspider.com/trading-tools-store/indicators/68f10f-fearzone-contrarian-indicator/',
    position='price',
    inputs=[{'id': 'source', 'title': 'Source', 'type': 'select_wide', 'default': 'ohlc4', 'options': ['open', 'high', 'low', 'close', 'hl2', 'oc2', 'hlc3', 'ohlc4', 'wclose']}, {'id': 'high_period', 'title': 'High Period', 'type': 'number', 'default': 30}, {'id': 'stdev_period', 'title': 'Stdev Period', 'type': 'number', 'default': 50}, {'id': 'select_moving_average', 'title': 'Select Moving Average', 'type': 'select_wide', 'default': 'wma', 'options': ['ema', 'sma', 'wildma', 'vwma', 'wma', 'hullma', 'kama', 'alma', 'twap']}, {'id': 'show_fearzone_circle_', 'title': 'Show FearZone Circle?', 'type': 'boolean', 'default': True}, {'id': 'fearzone_circle_color', 'title': 'FearZone Circle Color', 'type': 'color', 'default': '#FC6C85'}, {'id': 'color_candles_in_fearzone_', 'title': 'Color Candles in FearZone?', 'type': 'boolean', 'default': True}, {'id': 'candle_color_in_fearzone', 'title': 'Candle Color in FearZone', 'type': 'color', 'default': 'red'}],
    outputs=['cdl', 'fearzone_circles', 'fearzone_detected'],
    signals=['fearzone_detected'],
    requires=[],
    parity='exact',
)
