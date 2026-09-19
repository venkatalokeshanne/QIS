"""
Equal Weighted Index -- TrendSpider store indicator by TrendSpider Team.

Registered as "equal_weighted_index_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/equal-weighted-index/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_assert = G["assert"]
    G_close = G["close"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_input = G["input"]
    G_interpolate_sparse_series = G["interpolate_sparse_series"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_paint = G["paint"]
    G_request = G["request"]
    G_time = G["time"]
    G_describe_indicator("Equal weighted index", "lower")
    def _f1(value=J.undefined, *_args):
        return J.get(value, "trim")()
    SYMBOLS = J.get(J.get(J.get(G_input, "text")("Symbols", "AAPL,AMGN,AMZN,AXP,BA,CAT,CRM,CSCO,CVX,DIS,GS,HD,HON,IBM,JNJ,JPM,KO,MCD,MMM,MRK,MSFT,NKE,NVDA,PG,SHW,TRV,UNH,V,VZ,WMT", J.obj(("hide_in_legend", True))), "split")(","), "map")(_f1)
    BATCH_SIZE_SYMBOLS = 9
    MAX_HISTORY_CALLS = 6
    totalSymbols = J.get(SYMBOLS, "length")
    G_assert(J.lt(J.get(SYMBOLS, "length"), J.mul(BATCH_SIZE_SYMBOLS, MAX_HISTORY_CALLS)), J.template("Too many symbols requested"))
    def getSymbolInputs(batchIndex=J.undefined, *_args):
        return J.get(SYMBOLS, "slice")(J.mul(batchIndex, BATCH_SIZE_SYMBOLS), J.add(J.mul(batchIndex, BATCH_SIZE_SYMBOLS), BATCH_SIZE_SYMBOLS))
    def fetchBatchData(symbols=J.undefined, *_args):
        symbolString = J.get(symbols, "join")(" + ")
        data = J.get(G_request, "history")(J.template("=", symbolString), J.get(G_current, "resolution"))
        G_assert((not J.truthy(J.get(data, "error"))), J.template("Error fetching data: ", J.get(data, "error")))
        return G_interpolate_sparse_series(G_land_points_onto_series(J.get(data, "time"), J.get(data, "close"), G_time), "constant")
    numberOfBatches = J.get(G_Math, "ceil")(J.div(totalSymbols, BATCH_SIZE_SYMBOLS))
    batchesData = J.JSArray([])
    batchIndex = 0
    while J.lt(batchIndex, numberOfBatches):
        symbols = getSymbolInputs(batchIndex)
        batchData = fetchBatchData(symbols)
        J.get(batchesData, "push")(batchData)
        batchIndex = J.add(batchIndex, 1)
    def _f2(dummy=J.undefined, candleIndex=J.undefined, *_args):
        def _f1(acc=J.undefined, partialSeries=J.undefined, *_args):
            return J.add(acc, J.get(partialSeries, candleIndex))
        allValueAtThatIndex = J.get(batchesData, "reduce")(_f1, 0)
        return allValueAtThatIndex
    indexValues = J.get(G_close, "map")(_f2)
    G_paint(indexValues, J.obj(("color", "grey")))


register_store_indicator(
    script,
    name='equal_weighted_index_TS',
    title='Equal Weighted Index',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/equal-weighted-index/',
    position='lower',
    inputs=[{'id': 'symbols', 'title': 'Symbols', 'type': 'text', 'default': 'AAPL,AMGN,AMZN,AXP,BA,CAT,CRM,CSCO,CVX,DIS,GS,HD,HON,IBM,JNJ,JPM,KO,MCD,MMM,MRK,MSFT,NKE,NVDA,PG,SHW,TRV,UNH,V,VZ,WMT'}],
    outputs=['line_1'],
    signals=[],
    requires=['history'],
    parity='exact',
)
