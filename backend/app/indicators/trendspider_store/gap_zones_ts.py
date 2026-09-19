"""
Gap Zones -- TrendSpider store indicator by Trade Seekers.

Registered as "gap_zones_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68a115-gap-zones/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
aapl_d: OK, syn_5m: both-error.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_assert = G["assert"]
    G_constants = G["constants"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_fill = G["fill"]
    G_input = G["input"]
    G_interpolate_sparse_series = G["interpolate_sparse_series"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_paint = G["paint"]
    G_request = G["request"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    G_describe_indicator("Gap Zones", J.obj(("decimals", 2)))
    maxZones = 5
    zoneColor = "rgba(0, 150, 136, 0.2)"
    midlineColor = "rgba(0, 150, 136, 0.5)"
    timeframe = J.get(G_input, "select")("Timeframe", "W", J.get(G_constants, "time_frames"))
    data = J.get(G_request, "history")(J.get(G_current, "ticker"), timeframe)
    G_assert((not J.truthy(J.get(data, "error"))), J.template("Error fetching data: ", J.get(data, "error")))
    zones = J.JSArray([])
    lastClose = None
    i = 1
    while J.lt(i, J.get(J.get(data, "close"), "length")):
        prevClose = J.get(J.get(data, "close"), J.sub(i, 1))
        currOpen = J.get(J.get(data, "open"), i)
        if J.sne(prevClose, currOpen):
            J.get(zones, "push")(J.obj(("start", J.get(J.get(data, "time"), i)), ("high", J.get(G_Math, "max")(prevClose, currOpen)), ("low", J.get(G_Math, "min")(prevClose, currOpen)), ("mid", J.div(J.add(prevClose, currOpen), 2))))
        lastClose = J.get(J.get(data, "close"), i)
        i = J.inc(i)
    activeZones = J.JSArray([])
    i_2 = J.sub(J.get(zones, "length"), 1)
    while (J.ge(i_2, 0) and J.lt(J.get(activeZones, "length"), maxZones)):
        zone = J.get(zones, i_2)
        def _f1(az=J.undefined, *_args):
            return (J.le(J.get(zone, "low"), J.get(az, "low")) if J.truthy(_t1 := J.ge(J.get(zone, "high"), J.get(az, "high"))) else _t1)
        engulfedIndex = J.get(activeZones, "findIndex")(_f1)
        if J.sne(engulfedIndex, (-1)):
            J.get(activeZones, "splice")(engulfedIndex)
        J.get(activeZones, "unshift")(zone)
        i_2 = J.dec(i_2)
    zoneItr = 0
    while J.lt(zoneItr, J.get(activeZones, "length")):
        zone_2 = J.get(activeZones, zoneItr)
        zoneHigh = G_land_points_onto_series(J.JSArray([J.get(zone_2, "start")]), J.JSArray([J.get(zone_2, "high")]), G_time, "ge")
        zoneLow = G_land_points_onto_series(J.JSArray([J.get(zone_2, "start")]), J.JSArray([J.get(zone_2, "low")]), G_time, "ge")
        zoneMid = G_land_points_onto_series(J.JSArray([J.get(zone_2, "start")]), J.JSArray([J.get(zone_2, "mid")]), G_time, "ge")
        interpolatedHigh = G_interpolate_sparse_series(zoneHigh, "constant")
        interpolatedLow = G_interpolate_sparse_series(zoneLow, "constant")
        interpolatedMid = G_interpolate_sparse_series(zoneMid, "constant")
        zoneNamePrefix = J.template("Zone ", J.add(zoneItr, 1))
        G_fill(G_paint(interpolatedHigh, J.obj(("style", "line"), ("name", J.template(zoneNamePrefix, " High")), ("color", zoneColor), ("ignoreWhenScaling", True), ("hideInLegend", True))), G_paint(interpolatedLow, J.obj(("style", "line"), ("name", J.template(zoneNamePrefix, " Low")), ("color", zoneColor), ("ignoreWhenScaling", True), ("hideInLegend", True))), zoneColor, 0.2, J.template(zoneNamePrefix, " Fill"))
        G_paint(interpolatedMid, J.obj(("style", "dotted"), ("name", J.template(zoneNamePrefix, " Mid")), ("color", midlineColor), ("linewidth", 1), ("ignoreWhenScaling", True), ("hideInLegend", True)))
        zoneItr = J.inc(zoneItr)
    i_3 = J.add(J.get(activeZones, "length"), 1)
    while J.le(i_3, maxZones):
        zoneNamePrefix_2 = J.template("Zone ", i_3)
        G_fill(G_paint(G_series_of(None), J.obj(("style", "line"), ("name", J.template(zoneNamePrefix_2, " High")), ("color", zoneColor), ("hidden", True), ("ignoreWhenScaling", True), ("hideInLegend", True))), G_paint(G_series_of(None), J.obj(("style", "line"), ("name", J.template(zoneNamePrefix_2, " Low")), ("color", zoneColor), ("hidden", True), ("ignoreWhenScaling", True), ("hideInLegend", True))), 0.2, zoneColor, J.template(zoneNamePrefix_2, " Fill"))
        G_paint(G_series_of(None), J.obj(("style", "dotted"), ("name", J.template(zoneNamePrefix_2, " Mid")), ("color", midlineColor), ("linewidth", 1), ("ignoreWhenScaling", True), ("hideInLegend", True)))
        i_3 = J.inc(i_3)


register_store_indicator(
    script,
    name='gap_zones_TS',
    title='Gap Zones',
    developer='Trade Seekers',
    url='https://trendspider.com/trading-tools-store/indicators/68a115-gap-zones/',
    position='price',
    inputs=[{'id': 'timeframe', 'title': 'Timeframe', 'type': 'select_wide', 'default': 'W', 'options': ['1', '2', '3', '4', '5', '6', '10', '12', '15', '30', '45', '60', '65', '90', '120', '240', '1440', 'D', 'W', 'M', 'Q', 'Y']}],
    outputs=['zone_1_high', 'zone_1_low', 'zone_1_mid', 'zone_2_high', 'zone_2_low', 'zone_2_mid', 'zone_3_high', 'zone_3_low', 'zone_3_mid', 'zone_4_high', 'zone_4_low', 'zone_4_mid', 'zone_5_high', 'zone_5_low', 'zone_5_mid'],
    signals=[],
    requires=['history'],
    parity='aapl_d: OK, syn_5m: both-error',
)
