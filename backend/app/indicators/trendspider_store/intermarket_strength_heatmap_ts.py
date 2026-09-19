"""
Intermarket Strength Heatmap -- TrendSpider store indicator by Aliu Kehinde.

Registered as "intermarket_strength_heatmap_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68aa73-intermarket-strength-heatmap/)
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
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_input = G["input"]
    G_paint_overlay = G["paint_overlay"]
    G_request = G["request"]
    G_sma = G["sma"]
    G_stdev = G["stdev"]
    def fetchSymbolData(symbol=J.undefined, *_args):
        data = J.get(G_request, "history")(symbol, J.get(G_current, "resolution"))
        G_assert((not J.truthy(J.get(data, "error"))), J.template("Could not fetch data for ", symbol, ": ", J.get(data, "error")))
        return J.get(data, "close")
    def trimSeries(series=J.undefined, length=J.undefined, *_args):
        return J.get(series, "slice")(J.neg(length))
    def calculateStrength(assetData=J.undefined, benchmarkData_2=J.undefined, *_args):
        def _f1(asset=J.undefined, bench=J.undefined, *_args):
            if (((asset is None) or (bench is None)) or J.seq(bench, 0)):
                return None
            return J.div(asset, bench)
        return G_for_every(assetData, benchmarkData_2, _f1)
    def calculateZScore(strengthSeries=J.undefined, period=J.undefined, *_args):
        myMean = G_sma(strengthSeries, period)
        myStdDev = G_stdev(strengthSeries, period)
        def _f1(_str=J.undefined, _m=J.undefined, _sd=J.undefined, *_args):
            if ((((_str is None) or (_m is None)) or (_sd is None)) or J.seq(_sd, 0)):
                return None
            return J.div(J.sub(_str, _m), _sd)
        return G_for_every(strengthSeries, myMean, myStdDev, _f1)
    def createHeatmapRow(symbol=J.undefined, zScoreSeries=J.undefined, *_args):
        lastZScore = J.get(zScoreSeries, J.sub(J.get(zScoreSeries, "length"), 1))
        bgColor = neutralColor
        textColor = "var(--text-color)"
        displayValue = "N/A"
        if (lastZScore is not None):
            displayValue = J.get(lastZScore, "toFixed")(2)
            if J.gt(lastZScore, strengthThreshold):
                bgColor = strongBullish
                textColor = "white"
            elif J.gt(lastZScore, J.div(strengthThreshold, 2)):
                bgColor = weakBullish
            elif J.lt(lastZScore, J.neg(strengthThreshold)):
                bgColor = strongBearish
                textColor = "white"
            elif J.lt(lastZScore, J.div(J.neg(strengthThreshold), 2)):
                bgColor = weakBearish
        return J.obj(("cells", J.JSArray([J.obj(("text", symbol), ("color", textColor), ("align", "left"), ("width", "40%")), J.obj(("text", displayValue), ("color", textColor), ("background", bgColor), ("align", "center"), ("width", "60%"))])))
    G_describe_indicator("Intermarket Strength Heatmap", "overlay", J.obj(("shortName", "IM Heatmap")))
    benchmarkSymbol = J.get(G_input, "symbol")("Benchmark", "SPY")
    asset1Symbol = J.get(G_input, "symbol")("Asset 1", "QQQ")
    asset2Symbol = J.get(G_input, "symbol")("Asset 2", "TLT")
    asset3Symbol = J.get(G_input, "symbol")("Asset 3", "GLD")
    asset4Symbol = J.get(G_input, "symbol")("Asset 4", "DBA")
    lookbackPeriod = J.get(G_input, "number")("Lookback Period (Bars)", 50, J.obj(("min", 20), ("max", 100), ("step", 1)))
    strengthThreshold = J.get(G_input, "number")("Strength Threshold (Z-Score)", 0.5, J.obj(("min", 0.2), ("max", 1.5), ("step", 0.1)))
    strongBullish = "#00CC0050"
    weakBullish = "#00CC0020"
    neutralColor = "#00000000"
    weakBearish = "#FF000020"
    strongBearish = "#FF000050"
    benchmarkData = fetchSymbolData(benchmarkSymbol)
    asset1Data = fetchSymbolData(asset1Symbol)
    asset2Data = fetchSymbolData(asset2Symbol)
    asset3Data = fetchSymbolData(asset3Symbol)
    asset4Data = fetchSymbolData(asset4Symbol)
    minLength = J.get(G_Math, "min")(J.get(benchmarkData, "length"), J.get(asset1Data, "length"), J.get(asset2Data, "length"), J.get(asset3Data, "length"), J.get(asset4Data, "length"))
    myBenchmarkData = trimSeries(benchmarkData, minLength)
    myAsset1Data = trimSeries(asset1Data, minLength)
    myAsset2Data = trimSeries(asset2Data, minLength)
    myAsset3Data = trimSeries(asset3Data, minLength)
    myAsset4Data = trimSeries(asset4Data, minLength)
    strength1 = calculateStrength(myAsset1Data, myBenchmarkData)
    strength2 = calculateStrength(myAsset2Data, myBenchmarkData)
    strength3 = calculateStrength(myAsset3Data, myBenchmarkData)
    strength4 = calculateStrength(myAsset4Data, myBenchmarkData)
    zScore1 = calculateZScore(strength1, lookbackPeriod)
    zScore2 = calculateZScore(strength2, lookbackPeriod)
    zScore3 = calculateZScore(strength3, lookbackPeriod)
    zScore4 = calculateZScore(strength4, lookbackPeriod)
    G_paint_overlay("Intermarket Heatmap", J.obj(("position", "top_right"), ("width", 220)), J.obj(("rows", J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", "Asset"), ("color", "white"), ("background", "#2C2C2C"), ("align", "left"), ("width", "40%")), J.obj(("text", "Vs Benchmark"), ("color", "white"), ("background", "#2C2C2C"), ("align", "center"), ("width", "60%"))]))), createHeatmapRow(asset1Symbol, zScore1), createHeatmapRow(asset2Symbol, zScore2), createHeatmapRow(asset3Symbol, zScore3), createHeatmapRow(asset4Symbol, zScore4)]))))


register_store_indicator(
    script,
    name='intermarket_strength_heatmap_TS',
    title='Intermarket Strength Heatmap',
    developer='Aliu Kehinde',
    url='https://trendspider.com/trading-tools-store/indicators/68aa73-intermarket-strength-heatmap/',
    position='price',
    inputs=[{'id': 'sym-benchmark', 'title': 'Benchmark', 'type': 'symbol-search', 'default': 'SPY'}, {'id': 'sym-asset_1', 'title': 'Asset 1', 'type': 'symbol-search', 'default': 'QQQ'}, {'id': 'sym-asset_2', 'title': 'Asset 2', 'type': 'symbol-search', 'default': 'TLT'}, {'id': 'sym-asset_3', 'title': 'Asset 3', 'type': 'symbol-search', 'default': 'GLD'}, {'id': 'sym-asset_4', 'title': 'Asset 4', 'type': 'symbol-search', 'default': 'DBA'}, {'id': 'lookback_period__bars_', 'title': 'Lookback Period (Bars)', 'type': 'number', 'default': 50}, {'id': 'strength_threshold__z_score_', 'title': 'Strength Threshold (Z-Score)', 'type': 'number', 'default': 0.5}],
    outputs=[],
    signals=[],
    requires=['history'],
    parity='exact',
)
