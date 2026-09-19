"""
ALMA Trend -- TrendSpider store indicator by Chirag Patnaik.

Registered as "alma_trend_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68a1ee-alma/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_input = G["input"]
    G_market = G["market"]
    G_paint = G["paint"]
    G_series_of = G["series_of"]
    G_describe_indicator("ALMA")
    source = J.get(G_input, "select")("Source", "close", J.get(G_constants, "price_source_options"))
    myAlmaLength = J.get(G_input, "number")("Arnaud Legoux MA Length", 48, J.obj(("min", 1)))
    myAlmaOffset = J.get(G_input, "number")("ALMA Offset", 0.15, J.obj(("min", 0.0001)))
    myAlmaSigma = J.get(G_input, "number")("ALMA Sigma Value", 6, J.obj(("min", 1)))
    myM = J.mul(myAlmaOffset, J.sub(myAlmaLength, 1))
    myS = J.div(myAlmaLength, myAlmaSigma)
    def computeALMA(price=J.undefined, length=J.undefined, m=J.undefined, s=J.undefined, *_args):
        myWeightedSum = G_series_of(0)
        myWeightSum = G_series_of(0)
        myTrendALMA_2 = G_series_of(None)
        i = J.sub(length, 1)
        while J.lt(i, J.get(price, "length")):
            weightedSum = 0
            weightSum = 0
            j = 0
            while J.lt(j, length):
                w = J.get(G_Math, "exp")(J.div(J.neg(J.mul(J.sub(j, m), J.sub(j, m))), J.mul(J.mul(2, s), s)))
                weightedSum = J.add(weightedSum, J.mul(J.get(price, J.sub(i, j)), w))
                weightSum = J.add(weightSum, w)
                j = J.inc(j)
            J.set(myWeightedSum, i, weightedSum)
            J.set(myWeightSum, i, weightSum)
            J.set(myTrendALMA_2, i, J.div(weightedSum, weightSum))
            i = J.inc(i)
        return myTrendALMA_2
    myTrendALMA = computeALMA(J.get(G_market, source), myAlmaLength, myM, myS)
    myAlmaColor = "aqua"
    G_paint(myTrendALMA)
    G_paint(myTrendALMA, J.obj(("color", myAlmaColor), ("linewidth", 3), ("name", "ALMA Line")))


register_store_indicator(
    script,
    name='alma_trend_TS',
    title='ALMA Trend',
    developer='Chirag Patnaik',
    url='https://trendspider.com/trading-tools-store/indicators/68a1ee-alma/',
    position='price',
    inputs=[{'id': 'source', 'title': 'Source', 'type': 'select_wide', 'default': 'close', 'options': ['open', 'high', 'low', 'close', 'hl2', 'oc2', 'hlc3', 'ohlc4', 'wclose']}, {'id': 'arnaud_legoux_ma_length', 'title': 'Arnaud Legoux MA Length', 'type': 'number', 'default': 48}, {'id': 'alma_offset', 'title': 'ALMA Offset', 'type': 'number', 'default': 0.15}, {'id': 'alma_sigma_value', 'title': 'ALMA Sigma Value', 'type': 'number', 'default': 6}],
    outputs=['line_1', 'alma_line'],
    signals=[],
    requires=[],
    parity='exact',
)
