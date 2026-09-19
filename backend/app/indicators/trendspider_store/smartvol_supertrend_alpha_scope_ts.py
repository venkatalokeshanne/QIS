"""
SmartVol SuperTrend | Alpha Scope -- TrendSpider store indicator by Alpha Scope.

Registered as "smartvol_supertrend_alpha_scope_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/699daa-smartvol-supertrend-alpha-scope/)
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
    G_div = G["div"]
    G_ema = G["ema"]
    G_fill = G["fill"]
    G_for_every = G["for_every"]
    G_input = G["input"]
    G_market = G["market"]
    G_mult = G["mult"]
    G_oc2 = G["oc2"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_sub = G["sub"]
    G_sum = G["sum"]
    G_volume = G["volume"]
    G_vwma = G["vwma"]
    G_describe_indicator("SmartVol SuperTrend | Alpha Scope")
    mySourceOption = J.get(G_input, "select")("Source", "close", J.get(G_constants, "price_source_options"))
    mySrc = J.get(G_market, mySourceOption)
    myEmaLen = J.get(G_input, "number")("EMA Length", 5, J.obj(("min", 1), ("max", 500)))
    myVwsdLen = J.get(G_input, "number")("VWSD Length", 30, J.obj(("min", 1), ("max", 500)))
    myFactor = J.get(G_input, "number")("Factor", 1.8, J.obj(("min", 0.1), ("max", 10)))
    myEma = G_ema(mySrc, myEmaLen)
    def volumesd(series=J.undefined, length=J.undefined, *_args):
        myMean = G_vwma(series, length)
        def _f1(_s=J.undefined, _v=J.undefined, _m=J.undefined, _prev=J.undefined, i=J.undefined, *_args):
            myAccumulator = 0
            j = 0
            while (J.lt(j, length) and J.ge(J.sub(i, j), 0)):
                diff = J.sub(J.get(series, J.sub(i, j)), _m)
                myAccumulator = J.add(myAccumulator, J.mul(J.get(G_volume, J.sub(i, j)), J.get(G_Math, "pow")(diff, 2)))
                j = J.inc(j)
            return myAccumulator
        mySumSq = G_for_every(series, G_volume, myMean, _f1)
        myVolSum = G_sum(G_volume, length)
        myVariance = G_div(mySumSq, myVolSum)
        def _f2(_v=J.undefined, *_args):
            return J.get(G_Math, "sqrt")(_v)
        return G_for_every(myVariance, _f2)
    myVwsd = volumesd(mySrc, myVwsdLen)
    myUpperBandRaw = G_add(myEma, G_mult(myVwsd, myFactor))
    myLowerBandRaw = G_sub(myEma, G_mult(myVwsd, myFactor))
    def _f1(_upper=J.undefined, _lower=J.undefined, _close=J.undefined, _prev=J.undefined, i=J.undefined, *_args):
        if J.seq(i, 0):
            return J.obj(("upperBand", _upper), ("lowerBand", _lower), ("dir", 1), ("superTrend", _upper))
        prevResult = (_t1 if J.truthy(_t1 := _prev) else J.obj(("upperBand", _upper), ("lowerBand", _lower), ("dir", 1), ("superTrend", _upper)))
        lowerBand = (_lower if (J.gt(_lower, J.get(prevResult, "lowerBand")) or J.lt(J.get(G_close, J.sub(i, 1)), J.get(prevResult, "lowerBand"))) else J.get(prevResult, "lowerBand"))
        upperBand = (_upper if (J.lt(_upper, J.get(prevResult, "upperBand")) or J.gt(J.get(G_close, J.sub(i, 1)), J.get(prevResult, "upperBand"))) else J.get(prevResult, "upperBand"))
        dir = J.undefined
        if J.seq(J.get(prevResult, "superTrend"), J.get(prevResult, "upperBand")):
            dir = ((-1) if J.gt(_close, upperBand) else 1)
        else:
            dir = (1 if J.lt(_close, lowerBand) else (-1))
        superTrend = (lowerBand if J.seq(dir, (-1)) else upperBand)
        return J.obj(("upperBand", upperBand), ("lowerBand", lowerBand), ("dir", dir), ("superTrend", superTrend))
    myResult = G_for_every(myUpperBandRaw, myLowerBandRaw, G_close, _f1)
    def _f2(_r=J.undefined, *_args):
        return (J.get(_r, "superTrend") if J.truthy(_r) else None)
    mySt = G_for_every(myResult, _f2)
    def _f3(_r=J.undefined, *_args):
        return (J.get(_r, "dir") if J.truthy(_r) else None)
    myDir = G_for_every(myResult, _f3)
    def _f4(_d=J.undefined, *_args):
        return J.lt(_d, 0)
    myLong = G_for_every(myDir, _f4)
    def _f5(_d=J.undefined, *_args):
        return J.gt(_d, 0)
    myShort = G_for_every(myDir, _f5)
    def _f6(_long=J.undefined, _short=J.undefined, _prev=J.undefined, *_args):
        prevValue = (_t1 if J.truthy(_t1 := _prev) else 0)
        if (J.truthy(_long) and (not J.truthy(_short))):
            return 1
        if J.truthy(_short):
            return (-1)
        return prevValue
    myOquant = G_for_every(myLong, myShort, _f6)
    myOquantGreen = "#1fd325"
    myOquantPurple = "#bc08db"
    def _f7(_o=J.undefined, *_args):
        return (myOquantGreen if J.seq(_o, 1) else (myOquantPurple if J.seq(_o, (-1)) else None))
    myColors = G_for_every(myOquant, _f7)
    def _f8(_o=J.undefined, _st=J.undefined, *_args):
        return (_st if J.seq(_o, 1) else None)
    myStUp = G_for_every(myOquant, mySt, _f8)
    def _f9(_o=J.undefined, _st=J.undefined, *_args):
        return (_st if J.seq(_o, (-1)) else None)
    myStDown = G_for_every(myOquant, mySt, _f9)
    myPlotStUp = G_paint(myStUp, J.obj(("name", "Up direction"), ("color", myOquantGreen), ("style", "line")))
    myPlotStDown = G_paint(myStDown, J.obj(("name", "Down direction"), ("color", myOquantPurple), ("style", "line")))
    myPlotOc2 = G_paint(G_oc2, J.obj(("name", "Plot oc2"), ("color", myColors), ("style", "line")))
    G_fill(myPlotOc2, myPlotStUp, myOquantGreen, 0.2)
    G_fill(myPlotOc2, myPlotStDown, myOquantPurple, 0.2)
    G_color_candles(myColors)
    def _f10(v=J.undefined, i=J.undefined, *_args):
        return (J.gt(v, 0) if J.truthy(_t1 := J.lt(J.get(myOquant, J.sub(i, 1)), 0)) else _t1)
    G_register_signal(J.get(myOquant, "map")(_f10), "SmartVol SuperTrend Bullish")
    def _f11(v=J.undefined, i=J.undefined, *_args):
        return (J.lt(v, 0) if J.truthy(_t1 := J.gt(J.get(myOquant, J.sub(i, 1)), 0)) else _t1)
    G_register_signal(J.get(myOquant, "map")(_f11), "SmartVol SuperTrend Bearish")


register_store_indicator(
    script,
    name='smartvol_supertrend_alpha_scope_TS',
    title='SmartVol SuperTrend | Alpha Scope',
    developer='Alpha Scope',
    url='https://trendspider.com/trading-tools-store/indicators/699daa-smartvol-supertrend-alpha-scope/',
    position='price',
    inputs=[{'id': 'source', 'title': 'Source', 'type': 'select_wide', 'default': 'close', 'options': ['open', 'high', 'low', 'close', 'hl2', 'oc2', 'hlc3', 'ohlc4', 'wclose']}, {'id': 'ema_length', 'title': 'EMA Length', 'type': 'number', 'default': 5}, {'id': 'vwsd_length', 'title': 'VWSD Length', 'type': 'number', 'default': 30}, {'id': 'factor', 'title': 'Factor', 'type': 'number', 'default': 1.8}],
    outputs=['up_direction', 'down_direction', 'plot_oc2', 'cdl', 'smartvol_supertrend_bullish', 'smartvol_supertrend_bearish'],
    signals=['smartvol_supertrend_bullish', 'smartvol_supertrend_bearish'],
    requires=[],
    parity='exact',
)
