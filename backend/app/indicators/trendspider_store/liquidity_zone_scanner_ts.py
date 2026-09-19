"""
Liquidity Zone Scanner -- TrendSpider store indicator by Aliu Kehinde.

Registered as "liquidity_zone_scanner_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68a90b-liquidity-zone-scanner/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
aapl_d: both-error, syn_5m: both-error.

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
    G_fractal_high = G["fractal_high"]
    G_fractal_low = G["fractal_low"]
    G_high = G["high"]
    G_horizontal_line = G["horizontal_line"]
    G_indexed_points_of = G["indexed_points_of"]
    G_input = G["input"]
    G_library = G["library"]
    G_low = G["low"]
    G_paint = G["paint"]
    G_sma = G["sma"]
    G_volume = G["volume"]
    G_describe_indicator("Liquidity Zone Scanner")
    tinycolor = G_library("tinycolor2")
    myHighs = G_fractal_high(G_high, 5)
    myLows = G_fractal_low(G_low, 5)
    myClusterTolerance = J.get(G_input, "number")("Cluster Tolerance", 0.005, J.obj(("min", 0.001), ("max", 0.1), ("step", 0.001)))
    def cluster_values(series=J.undefined, tolerance=J.undefined, *_args):
        clusters = J.JSArray([])
        nonNullValues = G_indexed_points_of(series)
        for point in J.iter_of(nonNullValues):
            foundCluster = False
            for cluster in J.iter_of(clusters):
                if J.le(J.div(J.get(G_Math, "abs")(J.sub(J.get(point, "value"), J.get(cluster, "price"))), J.get(cluster, "price")), tolerance):
                    J.update_member(cluster, "count", J.inc, True)
                    J.set(cluster, "price", J.div(J.add(J.mul(J.get(cluster, "price"), J.get(cluster, "count")), J.get(point, "value")), J.add(J.get(cluster, "count"), 1)))
                    foundCluster = True
                    break
            if (not J.truthy(foundCluster)):
                J.get(clusters, "push")(J.obj(("price", J.get(point, "value")), ("count", 1), ("firstIndex", J.get(point, "candleIndex"))))
        return clusters
    myHighLevels = cluster_values(myHighs, myClusterTolerance)
    myLowLevels = cluster_values(myLows, myClusterTolerance)
    myVolumeThreshold = J.get(G_input, "number")("Volume Threshold", 1.5, J.obj(("min", 1), ("max", 5), ("step", 0.1)))
    myVolumePeriod = J.get(G_input, "number")("Volume Period", 20, J.obj(("min", 5), ("max", 100)))
    myAvgVolume = G_sma(G_volume, myVolumePeriod)
    def _f1(v=J.undefined, avg=J.undefined, *_args):
        return (1 if J.gt(v, J.mul(avg, myVolumeThreshold)) else 0)
    myHighVolume = G_for_every(G_volume, myAvgVolume, _f1)
    def _f2(hv=J.undefined, c=J.undefined, *_args):
        return (c if J.truthy(hv) else None)
    myHvnLevels = cluster_values(G_for_every(myHighVolume, G_close, _f2), myClusterTolerance)
    myAllKeyLevels = J.JSArray([*J.spread(myHighLevels), *J.spread(myLowLevels), *J.spread(myHvnLevels)])
    for myLevel in J.iter_of(myAllKeyLevels):
        myStrength = J.get(G_Math, "min")(J.div(J.get(myLevel, "count"), 5), 1)
        myColor = J.get(J.get(tinycolor(("red" if J.gt(myStrength, 0.6) else "blue")), "setAlpha")(J.add(0.2, J.mul(myStrength, 0.3))), "toRgbString")()
        G_paint(G_horizontal_line(J.get(myLevel, "price"), J.get(myLevel, "firstIndex")), J.obj(("color", myColor), ("linewidth", 2), ("name", J.template("Zone ~", J.get(J.get(myLevel, "price"), "toFixed")(2))), ("style", "dotted")))


register_store_indicator(
    script,
    name='liquidity_zone_scanner_TS',
    title='Liquidity Zone Scanner',
    developer='Aliu Kehinde',
    url='https://trendspider.com/trading-tools-store/indicators/68a90b-liquidity-zone-scanner/',
    position='price',
    inputs=[{'id': 'cluster_tolerance', 'title': 'Cluster Tolerance', 'type': 'number', 'default': 0.005}, {'id': 'volume_threshold', 'title': 'Volume Threshold', 'type': 'number', 'default': 1.5}, {'id': 'volume_period', 'title': 'Volume Period', 'type': 'number', 'default': 20}],
    outputs=['zone__213_51', 'zone__212_40', 'zone__215_75', 'zone__230_99', 'zone__235_11', 'zone__233_41', 'zone__241_29', 'zone__257_26', 'zone__259_24', 'zone__265_29', 'zone__276_84', 'zone__280_38', 'zone__288_14', 'zone__275_05', 'zone__262_07', 'zone__266_82', 'zone__302_94', 'zone__316_89', 'zone__334_98', 'zone__344_57', 'zone__320_28', 'zone__330_81', 'zone__207_33', 'zone__201_50', 'zone__224_08', 'zone__226_63', 'zone__253_87', 'zone__244_74', 'zone__255_50', 'zone__266_00', 'zone__276_15', 'zone__269_56', 'zone__252_18', 'zone__271_70', 'zone__258_16', 'zone__249_52', 'zone__246_00', 'zone__294_91', 'zone__305_03', 'zone__287_38', 'zone__273_75', 'zone__311_91', 'zone__319_35', 'zone__300_19', 'zone__307_01', 'zone__207_57', 'zone__202_38', 'zone__213_28', 'zone__220_03', 'zone__229_35', 'zone__226_79', 'zone__245_90', 'zone__255_90', 'zone__262_24', 'zone__271_13', 'zone__273_67', 'zone__259_48', 'zone__276_04', 'zone__247_99', 'zone__253_50', 'zone__280_14', 'zone__301_54', 'zone__298_01', 'zone__283_78', 'zone__308_91'],
    signals=[],
    requires=[],
    parity='aapl_d: both-error, syn_5m: both-error',
)
