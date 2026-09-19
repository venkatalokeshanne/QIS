"""
Volume & Trend Confluence -- TrendSpider store indicator by TrendSpider Team.

Registered as "volume_trend_confluence_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/volume-trend-confluence/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_close = G["close"]
    G_color_candles = G["color_candles"]
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_indicators = G["indicators"]
    G_input = G["input"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_volume = G["volume"]
    G_describe_indicator("Volume & Trend Confluence")
    obvTrendPeriod = J.get(G_input, "number")("OBV Trend Period", 14, J.obj(("min", 1)))
    smaPeriod = J.get(G_input, "number")("Price MA Period", 50, J.obj(("min", 1)))
    maType = J.get(G_input, "select")("MA Type", "sma", J.get(G_constants, "ma_types"))
    bullishColor = J.get(G_input, "color")("Bullish Color", "green")
    bearishColor = J.get(G_input, "color")("Bearish Color", "red")
    neutralColor = J.get(G_input, "color")("Neutral Color", "gray")
    def _f1(c=J.undefined, v=J.undefined, prevObv=J.undefined, i=J.undefined, *_args):
        if J.seq(i, 0):
            return v
        return (J.add(prevObv, v) if J.gt(c, J.get(G_close, J.sub(i, 1))) else (J.sub(prevObv, v) if J.lt(c, J.get(G_close, J.sub(i, 1))) else prevObv))
    myObv = G_for_every(G_close, G_volume, _f1)
    myObvTrend = J.get(G_indicators, maType)(myObv, obvTrendPeriod)
    myPriceMa = J.get(G_indicators, maType)(G_close, smaPeriod)
    def _f2(c=J.undefined, obv=J.undefined, obvTrend=J.undefined, priceMa=J.undefined, prevSignal=J.undefined, i=J.undefined, *_args):
        if J.seq(i, 0):
            return 0
        obvTrendUp = J.gt(obv, obvTrend)
        priceAboveMa = J.gt(c, priceMa)
        if (J.truthy(obvTrendUp) and J.truthy(priceAboveMa)):
            return 1
        elif ((not J.truthy(obvTrendUp)) and (not J.truthy(priceAboveMa))):
            return (-1)
        else:
            return 0
    mySignal = G_for_every(G_close, myObv, myObvTrend, myPriceMa, _f2)
    def _f3(s=J.undefined, *_args):
        if J.seq(s, 1):
            return bullishColor
        if J.seq(s, (-1)):
            return bearishColor
        return neutralColor
    myCandleColors = G_for_every(mySignal, _f3)
    G_color_candles(myCandleColors)
    G_paint(myPriceMa, J.obj(("color", "blue"), ("name", J.template(smaPeriod, " ", J.get(maType, "toUpperCase")()))))
    def _f4(s=J.undefined, *_args):
        return J.seq(s, 1)
    G_register_signal(G_for_every(mySignal, _f4), "Bullish Signal")
    def _f5(s=J.undefined, *_args):
        return J.seq(s, (-1))
    G_register_signal(G_for_every(mySignal, _f5), "Bearish Signal")


register_store_indicator(
    script,
    name='volume_trend_confluence_TS',
    title='Volume & Trend Confluence',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/volume-trend-confluence/',
    position='price',
    inputs=[{'id': 'obv_trend_period', 'title': 'OBV Trend Period', 'type': 'number', 'default': 14}, {'id': 'price_ma_period', 'title': 'Price MA Period', 'type': 'number', 'default': 50}, {'id': 'ma_type', 'title': 'MA Type', 'type': 'select_wide', 'default': 'sma', 'options': ['ema', 'sma', 'wildma', 'vwma', 'wma', 'hullma', 'kama', 'alma', 'twap']}, {'id': 'bullish_color', 'title': 'Bullish Color', 'type': 'color', 'default': 'green'}, {'id': 'bearish_color', 'title': 'Bearish Color', 'type': 'color', 'default': 'red'}, {'id': 'neutral_color', 'title': 'Neutral Color', 'type': 'color', 'default': 'gray'}],
    outputs=['cdl', '50_sma', 'bullish_signal', 'bearish_signal'],
    signals=['bullish_signal', 'bearish_signal'],
    requires=[],
    parity='exact',
)
