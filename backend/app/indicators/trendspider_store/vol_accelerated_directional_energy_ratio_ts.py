"""
Vol. Accelerated Directional Energy Ratio -- TrendSpider store indicator by Kodexius.

Registered as "vol_accelerated_directional_energy_ratio_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/690d22-vol-accelerated-directional-energy-ratio/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_close = G["close"]
    G_constants = G["constants"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_div = G["div"]
    G_fill = G["fill"]
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_horizontal_line = G["horizontal_line"]
    G_indicators = G["indicators"]
    G_input = G["input"]
    G_low = G["low"]
    G_mult = G["mult"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_series_of = G["series_of"]
    G_sub = G["sub"]
    G_volume = G["volume"]
    G_wma = G["wma"]
    G_describe_indicator("Vol. Accelerated Directional Energy Ratio", "lower")
    length = J.get(G_input, "number")("Length", 10, J.obj(("min", 1)))
    DER_avg = J.get(G_input, "number")("DER Average", 5, J.obj(("min", 1)))
    MA_Type = J.get(G_input, "select")("DER MA Type", "wma", J.get(G_constants, "ma_types"))
    smooth = J.get(G_input, "number")("Smooth", 3, J.obj(("min", 1)))
    show_senti = J.get(G_input, "boolean")("Show Sentiment", False)
    senti = J.get(G_input, "number")("Sentiment Length", 20, J.obj(("min", 1)))
    v_calc = J.get(G_input, "select")("Volume Calculation", "Relative", J.JSArray(["Relative", "Full", "None"]))
    vlookbk = J.get(G_input, "number")("Volume Lookback", 20, J.obj(("min", 1)))
    def _f1(_v=J.undefined, _prevOut=J.undefined, _index=J.undefined, *_args):
        if (J.seq(v_calc, "None") or (not J.truthy(J.get(G_current, "volumeDataAvailable")))):
            return 1
        if J.seq(v_calc, "Relative"):
            myVolWindow = J.get(G_volume, "slice")(J.get(G_Math, "max")(0, J.add(J.sub(_index, vlookbk), 1)), J.add(_index, 1))
            myHighestVol = J.get(G_Math, "max")(*J.spread(myVolWindow))
            myLowestVol = J.get(G_Math, "min")(*J.spread(myVolWindow))
            return (0 if J.seq(myHighestVol, myLowestVol) else J.div(J.div(J.mul(100, J.sub(_v, myLowestVol)), J.sub(myHighestVol, myLowestVol)), 100))
        return _v
    myVola = G_for_every(G_volume, _f1)
    def _f2(_h=J.undefined, _l=J.undefined, _prevOut=J.undefined, _index=J.undefined, *_args):
        if J.lt(_index, 1):
            return None
        myHigh2 = J.get(G_Math, "max")(J.get(G_high, _index), J.get(G_high, J.sub(_index, 1)))
        myLow2 = J.get(G_Math, "min")(J.get(G_low, _index), J.get(G_low, J.sub(_index, 1)))
        return J.div(J.sub(myHigh2, myLow2), 2)
    myR = G_for_every(G_high, G_low, _f2)
    def _f3(_close=J.undefined, _r=J.undefined, _vola=J.undefined, _prevOut=J.undefined, _index=J.undefined, *_args):
        if ((J.lt(_index, 1) or (_r is None)) or J.seq(_r, 0)):
            return 0
        myPriceChange = J.sub(_close, J.get(G_close, J.sub(_index, 1)))
        mySr = J.div(myPriceChange, _r)
        myRsr = J.get(G_Math, "max")(J.get(G_Math, "min")(mySr, 1), (-1))
        return J.mul(myRsr, _vola)
    myC = G_for_every(G_close, myR, myVola, _f3)
    def _f4(_c=J.undefined, *_args):
        return J.get(G_Math, "max")(_c, 0)
    myCPlus = J.get(myC, "map")(_f4)
    def _f5(_c=J.undefined, *_args):
        return J.neg(J.get(G_Math, "min")(_c, 0))
    myCMinus = J.get(myC, "map")(_f5)
    myAvgVola = J.get(G_indicators, MA_Type)(myVola, length)
    myDem = G_div(J.get(G_indicators, MA_Type)(myCPlus, length), myAvgVola)
    mySup = G_div(J.get(G_indicators, MA_Type)(myCMinus, length), myAvgVola)
    myAdp = G_mult(G_wma(myDem, DER_avg), 100)
    myAsp = G_mult(G_wma(mySup, DER_avg), 100)
    myAnp = G_sub(myAdp, myAsp)
    myAnpS = G_wma(myAnp, smooth)
    mySAdp = G_mult(G_wma(myDem, senti), 100)
    mySAsp = G_mult(G_wma(mySup, senti), 100)
    myLongSenti = G_wma(G_sub(mySAdp, mySAsp), smooth)
    def _f6(_senti=J.undefined, _prevOut=J.undefined, _index=J.undefined, *_args):
        if J.lt(_index, 1):
            return "#1b5e2080"
        myIsUp = J.ge(_senti, 0)
        myIsGrowing = J.ge(J.get(G_Math, "abs")(_senti), J.get(G_Math, "abs")(J.get(myLongSenti, J.sub(_index, 1))))
        if J.truthy(myIsUp):
            return ("#1b5e2080" if J.truthy(myIsGrowing) else "#66bb6a80")
        else:
            return ("#dc4c4a80" if J.truthy(myIsGrowing) else "#ef8e9880")
    mySentimentColor = G_for_every(myLongSenti, _f6)
    G_paint((myLongSenti if J.truthy(show_senti) else G_series_of(None)), J.obj(("name", "Sentiment"), ("style", "column"), ("color", mySentimentColor)))
    mySupplyLine = G_paint(myAsp, J.obj(("name", "Supply Energy"), ("color", "#ffa500"), ("style", "dotted")))
    myDemandLine = G_paint(myAdp, J.obj(("name", "Demand Energy"), ("color", "#00ffff"), ("style", "dotted")))
    G_fill(myDemandLine, mySupplyLine, "#00ff00", 0.3)
    def _f7(_v=J.undefined, *_args):
        return ("#359bfc" if J.ge(_v, 0) else "#f57f17")
    mySignalColor = J.get(myAnpS, "map")(_f7)
    G_paint(myAnpS, J.obj(("name", "Net Energy Signal"), ("color", mySignalColor), ("thickness", 2)))
    G_paint(G_horizontal_line(0), J.obj(("name", "Zero Line"), ("color", "#ffee00"), ("style", "dotted")))
    def _f8(_anp=J.undefined, _prevOut=J.undefined, _index=J.undefined, *_args):
        if J.lt(_index, 1):
            return False
        return (J.ge(_anp, 0) if J.truthy(_t1 := J.lt(J.get(myAnpS, J.sub(_index, 1)), 0)) else _t1)
    myAlertUp = G_for_every(myAnpS, _f8)
    def _f9(_anp=J.undefined, _prevOut=J.undefined, _index=J.undefined, *_args):
        if J.lt(_index, 1):
            return False
        return (J.le(_anp, 0) if J.truthy(_t1 := J.gt(J.get(myAnpS, J.sub(_index, 1)), 0)) else _t1)
    myAlertDown = G_for_every(myAnpS, _f9)
    def _f10(_anp=J.undefined, _senti=J.undefined, _prevOut=J.undefined, _index=J.undefined, *_args):
        if J.lt(_index, 1):
            return False
        return (J.gt(_anp, _senti) if J.truthy(_t1 := J.le(J.get(myAnpS, J.sub(_index, 1)), J.get(myLongSenti, J.sub(_index, 1)))) else _t1)
    mySpeedUp = G_for_every(myAnpS, myLongSenti, _f10)
    def _f11(_anp=J.undefined, _senti=J.undefined, _prevOut=J.undefined, _index=J.undefined, *_args):
        if J.lt(_index, 1):
            return False
        return (J.lt(_anp, _senti) if J.truthy(_t1 := J.ge(J.get(myAnpS, J.sub(_index, 1)), J.get(myLongSenti, J.sub(_index, 1)))) else _t1)
    mySlowDown = G_for_every(myAnpS, myLongSenti, _f11)
    G_register_signal(myAlertUp, "Energy Crossing Up")
    G_register_signal(myAlertDown, "Energy Crossing Down")
    G_register_signal(mySpeedUp, "Energy Speeding Up")
    G_register_signal(mySlowDown, "Energy Slowing Down")


register_store_indicator(
    script,
    name='vol_accelerated_directional_energy_ratio_TS',
    title='Vol. Accelerated Directional Energy Ratio',
    developer='Kodexius',
    url='https://trendspider.com/trading-tools-store/indicators/690d22-vol-accelerated-directional-energy-ratio/',
    position='lower',
    inputs=[{'id': 'length', 'title': 'Length', 'type': 'number', 'default': 10}, {'id': 'der_average', 'title': 'DER Average', 'type': 'number', 'default': 5}, {'id': 'der_ma_type', 'title': 'DER MA Type', 'type': 'select_wide', 'default': 'wma', 'options': ['ema', 'sma', 'wildma', 'vwma', 'wma', 'hullma', 'kama', 'alma', 'twap']}, {'id': 'smooth', 'title': 'Smooth', 'type': 'number', 'default': 3}, {'id': 'show_sentiment', 'title': 'Show Sentiment', 'type': 'boolean', 'default': False}, {'id': 'sentiment_length', 'title': 'Sentiment Length', 'type': 'number', 'default': 20}, {'id': 'volume_calculation', 'title': 'Volume Calculation', 'type': 'select_wide', 'default': 'Relative', 'options': ['Relative', 'Full', 'None']}, {'id': 'volume_lookback', 'title': 'Volume Lookback', 'type': 'number', 'default': 20}],
    outputs=['sentiment', 'supply_energy', 'demand_energy', 'net_energy_signal', 'zero_line', 'energy_crossing_up', 'energy_crossing_down', 'energy_speeding_up', 'energy_slowing_down'],
    signals=['energy_crossing_up', 'energy_crossing_down', 'energy_speeding_up', 'energy_slowing_down'],
    requires=[],
    parity='exact',
)
