"""
Market Sentiment Indicator -- TrendSpider store indicator by TrendSpider.

Registered as "market_sentiment_indicator_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6a7ba0-market-sentiment-indicator/)
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
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_input = G["input"]
    G_isFinite = G["isFinite"]
    G_isNaN = G["isNaN"]
    G_low = G["low"]
    G_paint = G["paint"]
    G_paint_overlay = G["paint_overlay"]
    G_parseInt = G["parseInt"]
    G_rsi = G["rsi"]
    G_series_of = G["series_of"]
    G_sma = G["sma"]
    G_stochastic = G["stochastic"]
    G_stochastic_rsi = G["stochastic_rsi"]
    G_volume = G["volume"]
    def clamp255(n=J.undefined, *_args):
        return J.get(G_Math, "max")(0, J.get(G_Math, "min")(255, J.get(G_Math, "round")(n)))
    def hex2(n=J.undefined, *_args):
        s = J.get(clamp255(n), "toString")(16)
        return (J.add("0", s) if J.lt(J.get(s, "length"), 2) else s)
    def toRgb(hexStr=J.undefined, fallback=J.undefined, *_args):
        if J.sne(J.typeof(hexStr), "string"):
            return fallback
        h = J.get(hexStr, "trim")()
        if J.sne(J.get(h, "charAt")(0), "#"):
            return fallback
        h = J.get(h, "substring")(1)
        if J.seq(J.get(h, "length"), 3):
            h = J.add(J.add(J.add(J.add(J.add(J.get(h, "charAt")(0), J.get(h, "charAt")(0)), J.get(h, "charAt")(1)), J.get(h, "charAt")(1)), J.get(h, "charAt")(2)), J.get(h, "charAt")(2))
        if J.sne(J.get(h, "length"), 6):
            return fallback
        r = G_parseInt(J.get(h, "substring")(0, 2), 16)
        g = G_parseInt(J.get(h, "substring")(2, 4), 16)
        b = G_parseInt(J.get(h, "substring")(4, 6), 16)
        if ((J.truthy(G_isNaN(r)) or J.truthy(G_isNaN(g))) or J.truthy(G_isNaN(b))):
            return fallback
        return J.JSArray([r, g, b])
    def rgbToHex(c=J.undefined, *_args):
        return J.add(J.add(J.add("#", hex2(J.get(c, 0))), hex2(J.get(c, 1))), hex2(J.get(c, 2)))
    def mixRgb(c1=J.undefined, c2=J.undefined, t=J.undefined, *_args):
        u = J.get(G_Math, "max")(0, J.get(G_Math, "min")(1, t))
        return J.JSArray([J.add(J.get(c1, 0), J.mul(J.sub(J.get(c2, 0), J.get(c1, 0)), u)), J.add(J.get(c1, 1), J.mul(J.sub(J.get(c2, 1), J.get(c1, 1)), u)), J.add(J.get(c1, 2), J.mul(J.sub(J.get(c2, 2), J.get(c1, 2)), u))])
    def scoreToColor(v=J.undefined, *_args):
        s = J.get(G_Math, "max")(0, J.get(G_Math, "min")(100, v))
        if J.ge(s, 50):
            return rgbToHex(mixRgb(NEUT_RGB, BULL_RGB, J.div(J.sub(s, 50), 50)))
        return rgbToHex(mixRgb(NEUT_RGB, BEAR_RGB, J.div(J.sub(50, s), 50)))
    def safeVal(arr=J.undefined, i=J.undefined, *_args):
        v = (J.get(arr, i) if J.truthy(_t1 := arr) else _t1)
        return (v if J.truthy(G_isFinite(v)) else 0)
    def ptsColor(v=J.undefined, *_args):
        if J.gt(v, 0.5):
            return BULL_HEX
        if J.lt(v, (-0.5)):
            return BEAR_HEX
        return NEUT_HEX
    def ptsRow(label=J.undefined, v=J.undefined, *_args):
        return J.obj(("cells", J.JSArray([J.obj(("text", label), ("background", BG), ("color", "#6b7488"), ("fontSize", "10px"), ("padding", "2px 8px"), ("borderTop", DIVIDER)), J.obj(("text", J.add(("+" if J.ge(v, 0) else ""), J.get(v, "toFixed")(1))), ("background", BG), ("color", ptsColor(v)), ("fontSize", "10px"), ("fontWeight", "700"), ("textAlign", "right"), ("padding", "2px 8px"), ("borderTop", DIVIDER))])))
    G_describe_indicator("Market Sentiment Indicator", "lower")
    volumePeriod = J.get(G_input, "number")("Volume SMA Period", 20, J.obj(("min", 1)))
    oscillatorType = J.get(G_input, "select")("Oscillator Type", "RSI", J.JSArray(["RSI", "Stochastic", "Stochastic RSI"]))
    oscillatorPeriod = J.get(G_input, "number")("Oscillator Period", 14, J.obj(("min", 1)))
    bullishColor = J.get(G_input, "color")("Bullish Color", "#4ade80")
    bearishColor = J.get(G_input, "color")("Bearish Color", "#f0616d")
    neutralColor = J.get(G_input, "color")("Neutral Color", "#7d8799")
    BULL_RGB = toRgb(bullishColor, J.JSArray([74, 222, 128]))
    BEAR_RGB = toRgb(bearishColor, J.JSArray([240, 97, 109]))
    NEUT_RGB = toRgb(neutralColor, J.JSArray([125, 135, 153]))
    BULL_HEX = rgbToHex(BULL_RGB)
    BEAR_HEX = rgbToHex(BEAR_RGB)
    NEUT_HEX = rgbToHex(NEUT_RGB)
    volumeSMA = G_sma(G_volume, volumePeriod)
    def _f1(*_args):
        _t1 = oscillatorType
        if J.seq(_t1, "RSI"):
            _t2 = 0
        elif J.seq(_t1, "Stochastic"):
            _t2 = 1
        elif J.seq(_t1, "Stochastic RSI"):
            _t2 = 2
        else:
            _t2 = 3
        _c3 = False
        for _once in (0,):
            if _t2 <= 0:
                return G_rsi(G_close, oscillatorPeriod)
            if _t2 <= 1:
                return G_stochastic(G_close, G_high, G_low, oscillatorPeriod)
            if _t2 <= 2:
                return G_stochastic_rsi(G_close, oscillatorPeriod, 3, 3)
            if _t2 <= 3:
                raise J.js_throw("Invalid oscillator type")
            pass
    oscillator = _f1()
    def _f2(c=J.undefined, _prev=J.undefined, i=J.undefined, *_args):
        return (0 if J.seq(i, 0) else J.mul(J.div(J.sub(c, J.get(G_close, J.sub(i, 1))), J.get(G_close, J.sub(i, 1))), 100))
    priceChange = G_for_every(G_close, _f2)
    def _f3(c=J.undefined, osc=J.undefined, vol=J.undefined, avgVol=J.undefined, pChange=J.undefined, _prev=J.undefined, i=J.undefined, *_args):
        if J.seq(i, 0):
            return 50
        score = 50
        score = J.add(score, J.mul(pChange, 2))
        volumeRatio = J.div(vol, avgVol)
        if (J.gt(pChange, 0) and J.gt(volumeRatio, 1)):
            score = J.add(score, J.mul(15, J.sub(volumeRatio, 1)))
        elif (J.lt(pChange, 0) and J.gt(volumeRatio, 1)):
            score = J.sub(score, J.mul(15, J.sub(volumeRatio, 1)))
        if J.gt(osc, 50):
            score = J.add(score, J.mul(J.sub(osc, 50), 0.6))
        else:
            score = J.sub(score, J.mul(J.sub(50, osc), 0.6))
        return J.get(G_Math, "max")(0, J.get(G_Math, "min")(100, score))
    sentimentScore = G_for_every(G_close, oscillator, G_volume, volumeSMA, priceChange, _f3)
    def _f4(s=J.undefined, *_args):
        return (scoreToColor(s) if J.truthy(G_isFinite(s)) else None)
    gradColor = G_for_every(sentimentScore, _f4)
    G_paint(sentimentScore, J.obj(("name", "Market Sentiment"), ("color", gradColor), ("thickness", 2), ("style", "line")))
    G_paint(G_series_of(70), J.obj(("name", "Overbought"), ("color", BULL_HEX), ("thickness", 1), ("style", "dotted")))
    G_paint(G_series_of(30), J.obj(("name", "Oversold"), ("color", BEAR_HEX), ("thickness", 1), ("style", "dotted")))
    BG = "rgba(13, 17, 26, 0.94)"
    DIVIDER = "1px solid #1c2231"
    idx = J.sub(J.get(G_close, "length"), 1)
    nowScore = safeVal(sentimentScore, idx)
    prevScore = safeVal(sentimentScore, J.sub(idx, 1))
    delta = J.sub(nowScore, prevScore)
    pNow = safeVal(priceChange, idx)
    vNow = safeVal(G_volume, idx)
    vAvgNow = safeVal(volumeSMA, idx)
    oNow = safeVal(oscillator, idx)
    pPts = J.mul(pNow, 2)
    vRatio = (J.div(vNow, vAvgNow) if J.gt(vAvgNow, 0) else 1)
    vPts = 0
    if (J.gt(pNow, 0) and J.gt(vRatio, 1)):
        vPts = J.mul(15, J.sub(vRatio, 1))
    elif (J.lt(pNow, 0) and J.gt(vRatio, 1)):
        vPts = J.mul((-15), J.sub(vRatio, 1))
    oPts = J.mul(J.sub(oNow, 50), 0.6)
    regime = "Neutral"
    regimeColor = NEUT_HEX
    if J.gt(nowScore, 70):
        regime = "Overbought"
        regimeColor = BULL_HEX
    elif J.gt(nowScore, 55):
        regime = "Bullish"
        regimeColor = BULL_HEX
    elif J.ge(nowScore, 45):
        regime = "Neutral"
        regimeColor = NEUT_HEX
    elif J.ge(nowScore, 30):
        regime = "Bearish"
        regimeColor = BEAR_HEX
    else:
        regime = "Oversold"
        regimeColor = BEAR_HEX
    rows = J.JSArray([])
    J.get(rows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", "MARKET SENTIMENT"), ("colspan", 2), ("background", BG), ("color", "#8a93a6"), ("fontSize", "9px"), ("fontWeight", "700"), ("letterSpacing", "1px"), ("padding", "4px 8px 3px 8px"), ("borderBottom", DIVIDER))]))))
    J.get(rows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", J.get(nowScore, "toFixed")(1)), ("background", BG), ("color", scoreToColor(nowScore)), ("fontSize", "22px"), ("fontWeight", "700"), ("padding", "4px 8px 0 8px")), J.obj(("text", regime), ("background", BG), ("color", regimeColor), ("fontSize", "11px"), ("fontWeight", "700"), ("textAlign", "right"), ("padding", "8px 8px 0 8px"))]))))
    J.get(rows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", J.add(J.add(("u25B2 +" if J.ge(delta, 0) else "u25BC "), J.get(delta, "toFixed")(1)), " vs prior bar")), ("colspan", 2), ("background", BG), ("color", (BULL_HEX if J.ge(delta, 0) else BEAR_HEX)), ("fontSize", "9px"), ("padding", "0 8px 5px 8px"))]))))
    J.get(rows, "push")(ptsRow("Price Action", pPts))
    J.get(rows, "push")(ptsRow("Volume", vPts))
    J.get(rows, "push")(ptsRow("Oscillator", oPts))
    J.get(rows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", "Rel Volume"), ("background", BG), ("color", "#6b7488"), ("fontSize", "10px"), ("padding", "2px 8px 4px 8px"), ("borderTop", DIVIDER)), J.obj(("text", J.add(J.get(vRatio, "toFixed")(2), "x")), ("background", BG), ("color", "#c8cedb"), ("fontSize", "10px"), ("fontWeight", "700"), ("textAlign", "right"), ("padding", "2px 8px 4px 8px"), ("borderTop", DIVIDER))]))))
    G_paint_overlay("Sentiment Panel", J.obj(("position", "top_right"), ("offset_x", (-10)), ("offset_y", 8)), J.obj(("background_color", BG), ("order", "above_all"), ("width", 190), ("rows", rows)))


register_store_indicator(
    script,
    name='market_sentiment_indicator_TS',
    title='Market Sentiment Indicator',
    developer='TrendSpider',
    url='https://trendspider.com/trading-tools-store/indicators/6a7ba0-market-sentiment-indicator/',
    position='lower',
    inputs=[{'id': 'volume_sma_period', 'title': 'Volume SMA Period', 'type': 'number', 'default': 20}, {'id': 'oscillator_type', 'title': 'Oscillator Type', 'type': 'select_wide', 'default': 'RSI', 'options': ['RSI', 'Stochastic', 'Stochastic RSI']}, {'id': 'oscillator_period', 'title': 'Oscillator Period', 'type': 'number', 'default': 14}, {'id': 'bullish_color', 'title': 'Bullish Color', 'type': 'color', 'default': '#4ade80'}, {'id': 'bearish_color', 'title': 'Bearish Color', 'type': 'color', 'default': '#f0616d'}, {'id': 'neutral_color', 'title': 'Neutral Color', 'type': 'color', 'default': '#7d8799'}],
    outputs=['market_sentiment', 'overbought', 'oversold'],
    signals=[],
    requires=[],
    parity='exact',
)
