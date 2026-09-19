"""
Greedzone - Contrarian Indicator (Zeiierman) -- TrendSpider store indicator by Zeiierman Trading.

Registered as "greedzone_contrarian_indicator_zeiierman_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6a05c7-greedzone-contrarian-indicator-zeiierman/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_add = G["add"]
    G_color_candles = G["color_candles"]
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_indicators = G["indicators"]
    G_input = G["input"]
    G_lowest = G["lowest"]
    G_market = G["market"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_stdev = G["stdev"]
    G_sub = G["sub"]
    G_describe_indicator("Greedzone - Contrarian Indicator (Zeiierman)", "price", J.obj(("mainColorInheritFrom", "text"), ("shortName", "Greedzone (Zeiierman)")))
    mySource = J.get(G_input, "select")("Source", "ohlc4", J.get(G_constants, "price_source_options"))
    myPrice = J.get(G_market, mySource)
    myLowPeriod = J.get(G_input, "number")("Low Period", 30, J.obj(("min", 1), ("max", 500)))
    myStdevPeriod = J.get(G_input, "number")("Stdev Period", 50, J.obj(("min", 1), ("max", 500)))
    myMaType = J.get(G_input, "select")("Select Moving Average", "wma", J.get(G_constants, "ma_types"))
    myShowGreedZoneCircles = J.get(G_input, "boolean")("Show GreedZone Circles?", True)
    myColorCandles = J.get(G_input, "boolean")("Color Candles in GreedZone?", True)
    myGreedZoneColor = J.get(G_input, "color")("GreedZone Color", "#90EE90")
    myComputeMA = J.get(G_indicators, myMaType)
    def myCalcGZ1(_source=J.undefined, _lowPeriod=J.undefined, _stdevPeriod=J.undefined, *_args):
        myLowestSource = G_lowest(_source, _lowPeriod)
        def _f1(_s=J.undefined, _l=J.undefined, *_args):
            return J.div(J.sub(_l, _s), _l)
        myGZ1_2 = G_for_every(_source, myLowestSource, _f1)
        myAVG1 = myComputeMA(myGZ1_2, _stdevPeriod)
        mySTDEV1 = G_stdev(myGZ1_2, _stdevPeriod)
        myGZ1Limit_2 = G_sub(myAVG1, mySTDEV1)
        return J.obj(("myGZ1", myGZ1_2), ("myGZ1Limit", myGZ1Limit_2))
    def myCalcGZ2(_source=J.undefined, _lowPeriod=J.undefined, _stdevPeriod=J.undefined, *_args):
        myGZ2_2 = myComputeMA(_source, _lowPeriod)
        myAVG2 = myComputeMA(myGZ2_2, _stdevPeriod)
        mySTDEV2 = G_stdev(myGZ2_2, _stdevPeriod)
        myGZ2Limit_2 = G_add(myAVG2, mySTDEV2)
        return J.obj(("myGZ2", myGZ2_2), ("myGZ2Limit", myGZ2Limit_2))
    _t1 = J.require_object(myCalcGZ1(myPrice, myLowPeriod, myStdevPeriod))
    myGZ1 = J.get(_t1, "myGZ1")
    myGZ1Limit = J.get(_t1, "myGZ1Limit")
    _t2 = J.require_object(myCalcGZ2(myPrice, myLowPeriod, myStdevPeriod))
    myGZ2 = J.get(_t2, "myGZ2")
    myGZ2Limit = J.get(_t2, "myGZ2Limit")
    def _f3(_gz1=J.undefined, _gz1Limit=J.undefined, _gz2=J.undefined, _gz2Limit=J.undefined, *_args):
        return (J.gt(_gz2, _gz2Limit) if J.truthy(_t1 := J.lt(_gz1, _gz1Limit)) else _t1)
    myGreedzoneCondition = G_for_every(myGZ1, myGZ1Limit, myGZ2, myGZ2Limit, _f3)
    def _f4(_condition=J.undefined, *_args):
        return (myGreedZoneColor if (J.truthy(_condition) and J.truthy(myColorCandles)) else None)
    myCandleColors = G_for_every(myGreedzoneCondition, _f4)
    G_color_candles(myCandleColors)
    def _f5(_condition=J.undefined, *_args):
        return (J.get(J.get(G_constants, "icons"), "circle") if (J.truthy(_condition) and J.truthy(myShowGreedZoneCircles)) else None)
    myAlertCircleValues = G_for_every(myGreedzoneCondition, _f5)
    G_paint(myAlertCircleValues, J.obj(("style", "labels_above"), ("color", myGreedZoneColor), ("name", "GreedZone Circles")))
    def _f6(_condition=J.undefined, _prevOutput=J.undefined, _index=J.undefined, *_args):
        if J.seq(_index, 0):
            return False
        myPrevCondition = J.get(myGreedzoneCondition, J.sub(_index, 1))
        return ((not J.truthy(myPrevCondition)) if J.truthy(_t1 := _condition) else _t1)
    myGreedZoneSignal = G_for_every(myGreedzoneCondition, _f6)
    G_register_signal(myGreedZoneSignal, "GreedZone detected")


register_store_indicator(
    script,
    name='greedzone_contrarian_indicator_zeiierman_TS',
    title='Greedzone - Contrarian Indicator (Zeiierman)',
    developer='Zeiierman Trading',
    url='https://trendspider.com/trading-tools-store/indicators/6a05c7-greedzone-contrarian-indicator-zeiierman/',
    position='price',
    inputs=[{'id': 'source', 'title': 'Source', 'type': 'select_wide', 'default': 'ohlc4', 'options': ['open', 'high', 'low', 'close', 'hl2', 'oc2', 'hlc3', 'ohlc4', 'wclose']}, {'id': 'low_period', 'title': 'Low Period', 'type': 'number', 'default': 30}, {'id': 'stdev_period', 'title': 'Stdev Period', 'type': 'number', 'default': 50}, {'id': 'select_moving_average', 'title': 'Select Moving Average', 'type': 'select_wide', 'default': 'wma', 'options': ['ema', 'sma', 'wildma', 'vwma', 'wma', 'hullma', 'kama', 'alma', 'twap']}, {'id': 'show_greedzone_circles_', 'title': 'Show GreedZone Circles?', 'type': 'boolean', 'default': True}, {'id': 'color_candles_in_greedzone_', 'title': 'Color Candles in GreedZone?', 'type': 'boolean', 'default': True}, {'id': 'greedzone_color', 'title': 'GreedZone Color', 'type': 'color', 'default': '#90EE90'}],
    outputs=['cdl', 'greedzone_circles', 'greedzone_detected'],
    signals=['greedzone_detected'],
    requires=[],
    parity='exact',
)
