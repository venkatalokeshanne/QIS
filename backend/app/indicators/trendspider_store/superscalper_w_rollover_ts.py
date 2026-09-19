"""
SuperScalper w/ Rollover -- TrendSpider store indicator by Rock Regan.

Registered as "superscalper_w_rollover_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/69dafa-superscalper-w-rollover/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_atr = G["atr"]
    G_close = G["close"]
    G_color_candles = G["color_candles"]
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_fill = G["fill"]
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_highest = G["highest"]
    G_input = G["input"]
    G_low = G["low"]
    G_lowest = G["lowest"]
    G_market = G["market"]
    G_open = G["open"]
    G_paint = G["paint"]
    G_paint_label_at_line = G["paint_label_at_line"]
    G_register_signal = G["register_signal"]
    G_sma = G["sma"]
    G_describe_indicator("SuperScalper w/ Rollover")
    periods = J.get(G_input, "number")("ATR Period", 10, J.obj(("min", 1), ("max", 100)))
    sourceType = J.get(G_input, "select")("Source", "hl2", J.get(G_constants, "price_source_options"))
    source = J.get(G_market, sourceType)
    multiplier = J.get(G_input, "number")("ATR Multi (1.75=Scalp)", 1.75, J.obj(("min", 0.1), ("max", 10)))
    showSignals = J.get(G_input, "boolean")("Show Buy/Sell Signals ?", True)
    highlighting = J.get(G_input, "boolean")("Highlighter On/Off ?", False)
    showPrice = J.get(G_input, "boolean")("Show Price in Labels ?", False)
    enableRollover = J.get(G_input, "boolean")("Enable Rollover Signal ?", True)
    smaFastLength = J.get(G_input, "number")("RO Fast Close SMA Len", 5, J.obj(("min", 1), ("step", 1)))
    stochLen = J.get(G_input, "number")("RO Stochastic Length", 14, J.obj(("min", 1), ("step", 1)))
    stochKSmooth = J.get(G_input, "number")("RO %K Smoothing", 3, J.obj(("min", 1), ("step", 1)))
    stochDSmooth = J.get(G_input, "number")("RO %D Smoothing", 3, J.obj(("min", 1), ("step", 1)))
    obThreshold = J.get(G_input, "number")("RO Overbought Threshold", 80, J.obj(("min", 0), ("step", 1)))
    roColor = J.get(G_input, "color")("RO Label Color", "white")
    roBgColor = J.get(G_input, "color")("RO Background Color", "#fff9c4")
    roOffset = J.get(G_input, "number")("RO Label Offset", 50, J.obj(("min", 0), ("step", 1)))
    myAtr = G_atr(G_high, G_low, G_close, periods)
    def _f1(_source=J.undefined, _atr=J.undefined, _close=J.undefined, _prevUp=J.undefined, _index=J.undefined, *_args):
        rawUp = J.sub(_source, J.mul(multiplier, _atr))
        if J.seq(_index, 0):
            return rawUp
        up1 = (_prevUp if (_prevUp is not None) else rawUp)
        return (J.get(G_Math, "max")(rawUp, up1) if J.gt(J.get(G_close, J.sub(_index, 1)), up1) else rawUp)
    myUp = G_for_every(source, myAtr, G_close, _f1)
    def _f2(_source=J.undefined, _atr=J.undefined, _close=J.undefined, _prevDn=J.undefined, _index=J.undefined, *_args):
        rawDn = J.add(_source, J.mul(multiplier, _atr))
        if J.seq(_index, 0):
            return rawDn
        dn1 = (_prevDn if (_prevDn is not None) else rawDn)
        return (J.get(G_Math, "min")(rawDn, dn1) if J.lt(J.get(G_close, J.sub(_index, 1)), dn1) else rawDn)
    myDn = G_for_every(source, myAtr, G_close, _f2)
    def _f3(_close=J.undefined, _up=J.undefined, _dn=J.undefined, _prevTrend=J.undefined, _index=J.undefined, *_args):
        if J.seq(_index, 0):
            return 1
        prevTrend = (_prevTrend if (_prevTrend is not None) else 1)
        prevUp = J.get(myUp, J.sub(_index, 1))
        prevDn = J.get(myDn, J.sub(_index, 1))
        if (J.seq(prevTrend, (-1)) and J.gt(_close, prevDn)):
            return 1
        if (J.seq(prevTrend, 1) and J.lt(_close, prevUp)):
            return (-1)
        return prevTrend
    myTrend = G_for_every(G_close, myUp, myDn, _f3)
    def _f4(_trend=J.undefined, _up=J.undefined, *_args):
        return (_up if J.seq(_trend, 1) else None)
    myUpTrendLine = G_for_every(myTrend, myUp, _f4)
    def _f5(_trend=J.undefined, _dn=J.undefined, *_args):
        return (_dn if J.seq(_trend, (-1)) else None)
    myDnTrendLine = G_for_every(myTrend, myDn, _f5)
    def _f6(_trend=J.undefined, _prev=J.undefined, _index=J.undefined, *_args):
        if J.seq(_index, 0):
            return False
        return (J.seq(J.get(myTrend, J.sub(_index, 1)), (-1)) if J.truthy(_t1 := J.seq(_trend, 1)) else _t1)
    myBuySignal = G_for_every(myTrend, _f6)
    def _f7(_trend=J.undefined, _prev=J.undefined, _index=J.undefined, *_args):
        if J.seq(_index, 0):
            return False
        return (J.seq(J.get(myTrend, J.sub(_index, 1)), 1) if J.truthy(_t1 := J.seq(_trend, (-1))) else _t1)
    mySellSignal = G_for_every(myTrend, _f7)
    upTrendId = G_paint(myUpTrendLine, J.obj(("name", "Up Trend"), ("style", "line"), ("color", "green")))
    dnTrendId = G_paint(myDnTrendLine, J.obj(("name", "Down Trend"), ("style", "line"), ("color", "red")))
    def _f8(_trend=J.undefined, _close=J.undefined, _up=J.undefined, *_args):
        return (J.get(G_Math, "max")(_close, _up) if J.seq(_trend, 1) else None)
    cloudTopBuy = G_for_every(myTrend, G_close, myUp, _f8)
    def _f9(_trend=J.undefined, _close=J.undefined, _up=J.undefined, *_args):
        return (J.get(G_Math, "min")(_close, _up) if J.seq(_trend, 1) else None)
    cloudBottomBuy = G_for_every(myTrend, G_close, myUp, _f9)
    def _f10(_trend=J.undefined, _close=J.undefined, _dn=J.undefined, *_args):
        return (J.get(G_Math, "max")(_close, _dn) if J.seq(_trend, (-1)) else None)
    cloudTopSell = G_for_every(myTrend, G_close, myDn, _f10)
    def _f11(_trend=J.undefined, _close=J.undefined, _dn=J.undefined, *_args):
        return (J.get(G_Math, "min")(_close, _dn) if J.seq(_trend, (-1)) else None)
    cloudBottomSell = G_for_every(myTrend, G_close, myDn, _f11)
    cloudTopBuyId = G_paint(cloudTopBuy, J.obj(("name", "CloudTopBuy"), ("style", "line"), ("hidden", True)))
    cloudBottomBuyId = G_paint(cloudBottomBuy, J.obj(("name", "CloudBottomBuy"), ("style", "line"), ("hidden", True)))
    G_fill(cloudTopBuyId, cloudBottomBuyId, "green", 0.2)
    cloudTopSellId = G_paint(cloudTopSell, J.obj(("name", "CloudTopSell"), ("style", "line"), ("hidden", True)))
    cloudBottomSellId = G_paint(cloudBottomSell, J.obj(("name", "CloudBottomSell"), ("style", "line"), ("hidden", True)))
    G_fill(cloudTopSellId, cloudBottomSellId, "red", 0.2)
    i = 0
    while J.lt(i, J.get(G_close, "length")):
        if (J.truthy(J.get(myBuySignal, i)) and J.truthy(showSignals)):
            labelText = (J.template("BULLn$", J.get(J.get(G_close, i), "toFixed")(2)) if J.truthy(showPrice) else "BULL")
            G_paint_label_at_line(upTrendId, i, labelText, J.obj(("color", "white"), ("background_color", "green"), ("vertical_align", "bottom")))
        if (J.truthy(J.get(mySellSignal, i)) and J.truthy(showSignals)):
            labelText_2 = (J.template("BEARn$", J.get(J.get(G_close, i), "toFixed")(2)) if J.truthy(showPrice) else "BEAR")
            G_paint_label_at_line(dnTrendId, i, labelText_2, J.obj(("color", "white"), ("background_color", "red"), ("vertical_align", "top")))
        i = J.inc(i)
    def _f12(_trend=J.undefined, *_args):
        if (not J.truthy(highlighting)):
            return None
        return ("green" if J.seq(_trend, 1) else "red")
    myCandleColors = G_for_every(myTrend, _f12)
    G_color_candles(myCandleColors)
    def _f13(_trend=J.undefined, _prev=J.undefined, _index=J.undefined, *_args):
        if J.seq(_index, 0):
            return False
        return J.sne(_trend, J.get(myTrend, J.sub(_index, 1)))
    myChangeCond = G_for_every(myTrend, _f13)
    smaCloseFast = G_sma(G_close, smaFastLength)
    lowArr = G_lowest(G_low, stochLen)
    highArr = G_highest(G_high, stochLen)
    def _f14(c=J.undefined, i_2=J.undefined, *_args):
        return (J.div(J.mul(100, J.sub(c, J.get(lowArr, i_2))), J.sub(J.get(highArr, i_2), J.get(lowArr, i_2))) if J.sne(J.sub(J.get(highArr, i_2), J.get(lowArr, i_2)), 0) else 0)
    stochK = J.get(G_close, "map")(_f14)
    stochBck = G_sma(stochK, stochKSmooth)
    stochBcd = G_sma(stochBck, stochDSmooth)
    def _f15(c=J.undefined, i_2=J.undefined, *_args):
        return (J.le(J.get(stochBcd, i_2), obThreshold) if J.truthy(_t1 := (J.gt(J.get(stochBcd, J.sub(i_2, 1)), obThreshold) if J.truthy(_t2 := (J.lt(J.get(G_low, i_2), J.get(G_low, J.sub(i_2, 1))) if J.truthy(_t3 := (J.lt(c, J.get(G_open, i_2)) if J.truthy(_t4 := (J.lt(c, J.get(smaCloseFast, i_2)) if J.truthy(_t5 := J.gt(i_2, 0)) else _t5)) else _t4)) else _t3)) else _t2)) else _t1)
    isROArr = J.get(G_close, "map")(_f15)
    def _f16(v=J.undefined, *_args):
        return ("⚠️" if (J.truthy(v) and J.truthy(enableRollover)) else None)
    G_paint(J.get(isROArr, "map")(_f16), J.obj(("name", "Rollover"), ("style", "labels_above"), ("verticalOffset", roOffset), ("color", roColor), ("background_color", roBgColor)))
    G_register_signal(myBuySignal, "SuperScalper Buy")
    G_register_signal(mySellSignal, "SuperScalper Sell")
    G_register_signal(myChangeCond, "SuperScalper Trend Flip")
    G_register_signal(isROArr, "SuperScalper Rollover")


register_store_indicator(
    script,
    name='superscalper_w_rollover_TS',
    title='SuperScalper w/ Rollover',
    developer='Rock Regan',
    url='https://trendspider.com/trading-tools-store/indicators/69dafa-superscalper-w-rollover/',
    position='price',
    inputs=[{'id': 'atr_period', 'title': 'ATR Period', 'type': 'number', 'default': 10}, {'id': 'source', 'title': 'Source', 'type': 'select_wide', 'default': 'hl2', 'options': ['open', 'high', 'low', 'close', 'hl2', 'oc2', 'hlc3', 'ohlc4', 'wclose']}, {'id': 'atr_multi__1_75_scalp_', 'title': 'ATR Multi (1.75=Scalp)', 'type': 'number', 'default': 1.75}, {'id': 'show_buy_sell_signals__', 'title': 'Show Buy/Sell Signals ?', 'type': 'boolean', 'default': True}, {'id': 'highlighter_on_off__', 'title': 'Highlighter On/Off ?', 'type': 'boolean', 'default': False}, {'id': 'show_price_in_labels__', 'title': 'Show Price in Labels ?', 'type': 'boolean', 'default': False}, {'id': 'enable_rollover_signal__', 'title': 'Enable Rollover Signal ?', 'type': 'boolean', 'default': True}, {'id': 'ro_fast_close_sma_len', 'title': 'RO Fast Close SMA Len', 'type': 'number', 'default': 5}, {'id': 'ro_stochastic_length', 'title': 'RO Stochastic Length', 'type': 'number', 'default': 14}, {'id': 'ro__k_smoothing', 'title': 'RO %K Smoothing', 'type': 'number', 'default': 3}, {'id': 'ro__d_smoothing', 'title': 'RO %D Smoothing', 'type': 'number', 'default': 3}, {'id': 'ro_overbought_threshold', 'title': 'RO Overbought Threshold', 'type': 'number', 'default': 80}, {'id': 'ro_label_color', 'title': 'RO Label Color', 'type': 'color', 'default': 'white'}, {'id': 'ro_background_color', 'title': 'RO Background Color', 'type': 'color', 'default': '#fff9c4'}, {'id': 'ro_label_offset', 'title': 'RO Label Offset', 'type': 'number', 'default': 50}],
    outputs=['up_trend', 'down_trend', 'cloudtopbuy', 'cloudbottombuy', 'cloudtopsell', 'cloudbottomsell', 'cdl', 'rollover', 'superscalper_buy', 'superscalper_sell', 'superscalper_trend_flip', 'superscalper_rollover'],
    signals=['superscalper_buy', 'superscalper_sell', 'superscalper_trend_flip', 'superscalper_rollover'],
    requires=[],
    parity='exact',
)
