"""
Momentum with Moving Average -- TrendSpider store indicator by James Chambers.

Registered as "momentum_with_moving_average_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/momentum-with-moving-average/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_color_cloud = G["color_cloud"]
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_ema = G["ema"]
    G_input = G["input"]
    G_paint = G["paint"]
    G_prices = G["prices"]
    G_sma = G["sma"]
    G_wma = G["wma"]
    def calculateMA(data=J.undefined, length=J.undefined, type_=J.undefined, *_args):
        maValues_2 = J.JSArray([])
        _t1 = type_
        if J.seq(_t1, "ema"):
            _t2 = 0
        elif J.seq(_t1, "wma"):
            _t2 = 1
        else:
            _t2 = 2
        _c3 = False
        for _once in (0,):
            if _t2 <= 0:
                maValues_2 = G_ema(data, length)
                break
            if _t2 <= 1:
                maValues_2 = G_wma(data, length)
                break
            if _t2 <= 2:
                maValues_2 = G_sma(data, length)
                break
            pass
        return maValues_2
    G_describe_indicator("Momentum with Custom Moving Average", "lower", J.obj(("shortName", "MoMA"), ("decimals", 2)))
    momentumLength = J.get(G_input, "number")("Momentum Length", 14, J.obj(("min", 1), ("max", 100)))
    maType = G_input("MA type", "sma", J.get(G_constants, "ma_types"))
    priceSource = G_input("Price Source", "close", J.get(G_constants, "price_source_options"))
    maLength = J.get(G_input, "number")("Moving Average Length", 20, J.obj(("min", 1), ("max", 100)))
    priceData = J.get(G_prices, priceSource)
    def _f1(value=J.undefined, index=J.undefined, *_args):
        if J.lt(index, momentumLength):
            return None
        return J.sub(value, J.get(priceData, J.sub(index, momentumLength)))
    momentumValues = J.get(priceData, "map")(_f1)
    maValues = calculateMA(momentumValues, maLength, maType)
    paintedMomentum = G_paint(momentumValues, J.obj(("name", "Momentum"), ("color", "green"), ("thickness", 2)))
    paintedMA = G_paint(maValues, J.obj(("name", "MA"), ("color", "black"), ("thickness", 2)))
    G_color_cloud(maValues, momentumValues, "red", "green")


register_store_indicator(
    script,
    name='momentum_with_moving_average_TS',
    title='Momentum with Moving Average',
    developer='James Chambers',
    url='https://trendspider.com/trading-tools-store/indicators/momentum-with-moving-average/',
    position='lower',
    inputs=[{'id': 'momentum_length', 'title': 'Momentum Length', 'type': 'number', 'default': 14}, {'id': 'ma_type', 'title': 'MA type', 'type': 'select_wide', 'default': 'sma', 'options': ['ema', 'sma', 'wildma', 'vwma', 'wma', 'hullma', 'kama', 'alma', 'twap']}, {'id': 'price_source', 'title': 'Price Source', 'type': 'select_wide', 'default': 'close', 'options': ['open', 'high', 'low', 'close', 'hl2', 'oc2', 'hlc3', 'ohlc4', 'wclose']}, {'id': 'moving_average_length', 'title': 'Moving Average Length', 'type': 'number', 'default': 20}],
    outputs=['momentum', 'ma', 'line_3', 'line_4', 'line_6', 'line_7'],
    signals=[],
    requires=[],
    parity='exact',
)
