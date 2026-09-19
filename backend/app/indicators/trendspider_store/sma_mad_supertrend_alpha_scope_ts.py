"""
SMA MAD SuperTrend | Alpha Scope -- TrendSpider store indicator by Alpha Scope.

Registered as "sma_mad_supertrend_alpha_scope_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/69c715-sma-mad-supertrend-alpha-scope/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_absdev = G["absdev"]
    G_add = G["add"]
    G_close = G["close"]
    G_color_candles = G["color_candles"]
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_div = G["div"]
    G_fill = G["fill"]
    G_for_every = G["for_every"]
    G_input = G["input"]
    G_market = G["market"]
    G_open = G["open"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_sma = G["sma"]
    G_describe_indicator("SMA MAD SuperTrend | Alpha Scope")
    src = J.get(G_input, "select")("Source", "close", J.get(G_constants, "price_source_options"))
    price = J.get(G_market, src)
    smaLen = J.get(G_input, "number")("SMA Length", 25, J.obj(("min", 1), ("max", 500)))
    factorValue = J.get(G_input, "number")("Factor", 2.3, J.obj(("min", 0.05), ("max", 10)))
    madLen = J.get(G_input, "number")("MAD Length", 25, J.obj(("min", 1), ("max", 500)))
    mySma = G_sma(price, smaLen)
    myMad = G_absdev(price, madLen)
    def _f1(_price=J.undefined, _sma=J.undefined, _mad=J.undefined, prevValue=J.undefined, index=J.undefined, *_args):
        if J.seq(index, 0):
            return J.obj(("st", None), ("dir", 1))
        myUpperband = J.add(_sma, J.mul(factorValue, _mad))
        myLowerband = J.sub(_sma, J.mul(factorValue, _mad))
        prevUpperband = (myUpperband if J.nullish(_t1 := J.chain_end(J.oget(prevValue, "upperband"))) else _t1)
        prevLowerband = (myLowerband if J.nullish(_t2 := J.chain_end(J.oget(prevValue, "lowerband"))) else _t2)
        prevClose = J.get(price, J.sub(index, 1))
        upperband = (myUpperband if (J.lt(myUpperband, prevUpperband) or J.gt(prevClose, prevUpperband)) else prevUpperband)
        lowerband = (myLowerband if (J.gt(myLowerband, prevLowerband) or J.lt(prevClose, prevLowerband)) else prevLowerband)
        myDir = J.undefined
        prevSt = (None if J.nullish(_t3 := J.chain_end(J.oget(prevValue, "st"))) else _t3)
        prevDir = (1 if J.nullish(_t4 := J.chain_end(J.oget(prevValue, "dir"))) else _t4)
        if (J.chain_end(J.oget(prevValue, "mad")) is None):
            myDir = 1
        elif J.seq(prevSt, prevUpperband):
            myDir = ((-1) if J.gt(_price, upperband) else 1)
        else:
            myDir = (1 if J.lt(_price, lowerband) else (-1))
        mySt = (lowerband if J.seq(myDir, (-1)) else upperband)
        return J.obj(("st", mySt), ("dir", myDir), ("upperband", upperband), ("lowerband", lowerband), ("mad", _mad))
    smaMadSupertrend = G_for_every(price, mySma, myMad, _f1)
    def _f2(v=J.undefined, *_args):
        return (None if J.nullish(_t1 := J.chain_end(J.oget(v, "st"))) else _t1)
    stValues = J.get(smaMadSupertrend, "map")(_f2)
    def _f3(v=J.undefined, *_args):
        return (1 if J.nullish(_t1 := J.chain_end(J.oget(v, "dir"))) else _t1)
    dirValues = J.get(smaMadSupertrend, "map")(_f3)
    def _f4(v=J.undefined, *_args):
        return (None if J.nullish(_t1 := J.chain_end(J.oget(v, "upperband"))) else _t1)
    upperbandValues = J.get(smaMadSupertrend, "map")(_f4)
    def _f5(v=J.undefined, *_args):
        return (None if J.nullish(_t1 := J.chain_end(J.oget(v, "lowerband"))) else _t1)
    lowerbandValues = J.get(smaMadSupertrend, "map")(_f5)
    def _f6(d=J.undefined, *_args):
        return J.lt(d, 0)
    stLong = J.get(dirValues, "map")(_f6)
    def _f7(d=J.undefined, *_args):
        return J.gt(d, 0)
    stShort = J.get(dirValues, "map")(_f7)
    as_ = J.JSArray([])
    i = 0
    while J.lt(i, J.get(G_close, "length")):
        currentLong = J.get(stLong, i)
        currentShort = J.get(stShort, i)
        prevAs = (J.get(as_, J.sub(i, 1)) if J.gt(i, 0) else 0)
        if (J.truthy(currentLong) and (not J.truthy(currentShort))):
            J.get(as_, "push")(1)
        elif J.truthy(currentShort):
            J.get(as_, "push")((-1))
        else:
            J.get(as_, "push")(prevAs)
        i = J.inc(i)
    asGreen = "#1fd325"
    asPurple = "#bc08db"
    def _f8(__=J.undefined, index=J.undefined, *_args):
        return (asGreen if J.seq(J.get(as_, index), 1) else (asPurple if J.seq(J.get(as_, index), (-1)) else None))
    colors = G_for_every(G_close, _f8)
    def _f9(_dir=J.undefined, _st=J.undefined, *_args):
        return (_st if J.lt(_dir, 0) else None)
    stUp = G_for_every(dirValues, stValues, _f9)
    def _f10(_dir=J.undefined, _st=J.undefined, *_args):
        return (_st if J.gt(_dir, 0) else None)
    stDown = G_for_every(dirValues, stValues, _f10)
    stUpPainted = G_paint(stUp, J.obj(("name", "ST UP"), ("color", asGreen), ("style", "line")))
    stDownPainted = G_paint(stDown, J.obj(("name", "ST Down"), ("color", asPurple), ("style", "line")))
    myOc2 = G_div(G_add(G_open, G_close), 2)
    oc2Painted = G_paint(myOc2, J.obj(("name", "Plot oc2"), ("color", colors)))
    G_fill(stUpPainted, oc2Painted, asGreen, 0.15)
    G_fill(stDownPainted, oc2Painted, asPurple, 0.15)
    G_color_candles(colors)
    def _f11(__=J.undefined, index=J.undefined, *_args):
        if J.seq(index, 0):
            return False
        prevAs_2 = J.get(as_, J.sub(index, 1))
        currentAs = J.get(as_, index)
        return (J.gt(currentAs, 0) if J.truthy(_t1 := J.le(prevAs_2, 0)) else _t1)
    asLongSignal = G_for_every(G_close, _f11)
    def _f12(__=J.undefined, index=J.undefined, *_args):
        if J.seq(index, 0):
            return False
        prevAs_2 = J.get(as_, J.sub(index, 1))
        currentAs = J.get(as_, index)
        return (J.lt(currentAs, 0) if J.truthy(_t1 := J.ge(prevAs_2, 0)) else _t1)
    asShortSignal = G_for_every(G_close, _f12)
    G_register_signal(asLongSignal, "SMA MAD SuperTrend Long")
    G_register_signal(asShortSignal, "SMA MAD SuperTrend Short")


register_store_indicator(
    script,
    name='sma_mad_supertrend_alpha_scope_TS',
    title='SMA MAD SuperTrend | Alpha Scope',
    developer='Alpha Scope',
    url='https://trendspider.com/trading-tools-store/indicators/69c715-sma-mad-supertrend-alpha-scope/',
    position='price',
    inputs=[{'id': 'source', 'title': 'Source', 'type': 'select_wide', 'default': 'close', 'options': ['open', 'high', 'low', 'close', 'hl2', 'oc2', 'hlc3', 'ohlc4', 'wclose']}, {'id': 'sma_length', 'title': 'SMA Length', 'type': 'number', 'default': 25}, {'id': 'factor', 'title': 'Factor', 'type': 'number', 'default': 2.3}, {'id': 'mad_length', 'title': 'MAD Length', 'type': 'number', 'default': 25}],
    outputs=['st_up', 'st_down', 'plot_oc2', 'cdl', 'sma_mad_supertrend_long', 'sma_mad_supertrend_short'],
    signals=['sma_mad_supertrend_long', 'sma_mad_supertrend_short'],
    requires=[],
    parity='exact',
)
