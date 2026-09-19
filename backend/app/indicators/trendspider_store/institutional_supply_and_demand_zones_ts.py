"""
Institutional Supply and Demand Zones -- TrendSpider store indicator by TrendSpider Team.

Registered as "institutional_supply_and_demand_zones_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/institutional-supply-and-demand-zones/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Array = G["Array"]
    G_Object = G["Object"]
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_fill = G["fill"]
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_horizontal_line = G["horizontal_line"]
    G_low = G["low"]
    G_open = G["open"]
    G_paint = G["paint"]
    G_describe_indicator("Institutional Supply and Demand Zones", "price", J.obj(("shortName", "Supply/Demand Zones")))
    maxNumberOfAreas = 5
    def _f1(o=J.undefined, h=J.undefined, c=J.undefined, l=J.undefined, lastOHCL=J.undefined, index=J.undefined, *_args):
        if J.seq(index, 0):
            lastOHCL = J.obj(("o", o), ("h", h), ("c", c), ("l", l), ("demandZones", J.JSArray([])), ("supplyZones", J.JSArray([])))
            return lastOHCL
        def _f1(value=J.undefined, index_2=J.undefined, *_args):
            if J.lt(l, J.get(value, "bottom")):
                J.delete(J.get(lastOHCL, "demandZones"), index_2)
        J.get(J.get(lastOHCL, "demandZones"), "forEach")(_f1)
        def _f2(value=J.undefined, index_2=J.undefined, *_args):
            if J.gt(h, J.get(value, "top")):
                J.delete(J.get(lastOHCL, "supplyZones"), index_2)
        J.get(J.get(lastOHCL, "supplyZones"), "forEach")(_f2)
        if J.gt(J.get(lastOHCL, "o"), J.get(lastOHCL, "c")):
            prevCandleBodySize = J.sub(J.get(lastOHCL, "o"), J.get(lastOHCL, "c"))
            if J.gt(c, o):
                currentCandleBodySize = J.sub(c, o)
                if ((J.ge(currentCandleBodySize, J.mul(prevCandleBodySize, 2)) and J.le(J.get(lastOHCL, "l"), l)) or (J.le(o, J.get(lastOHCL, "c")) and J.ge(c, J.get(lastOHCL, "o")))):
                    top = J.get(lastOHCL, "o")
                    bottom = J.undefined
                    demandZoneIndex = J.undefined
                    if J.le(o, J.get(lastOHCL, "c")):
                        if J.lt(J.get(lastOHCL, "l"), l):
                            bottom = J.get(lastOHCL, "l")
                            demandZoneIndex = J.sub(index, 1)
                        else:
                            bottom = l
                            demandZoneIndex = index
                    else:
                        bottom = J.get(lastOHCL, "l")
                    if J.truthy(J.get(G_Array, "isArray")(J.get(lastOHCL, "demandZones"))):
                        J.set(J.get(lastOHCL, "demandZones"), J.sub(index, 1), J.obj(("top", top), ("bottom", bottom)))
                    else:
                        J.set(lastOHCL, "demandZones", J.JSArray([]))
        elif J.lt(J.get(lastOHCL, "o"), J.get(lastOHCL, "c")):
            prevCandleBodySize_2 = J.sub(J.get(lastOHCL, "c"), J.get(lastOHCL, "o"))
            if J.lt(c, o):
                currentCandleBodySize_2 = J.sub(o, c)
                if ((J.ge(currentCandleBodySize_2, J.mul(prevCandleBodySize_2, 2)) and J.ge(J.get(lastOHCL, "h"), h)) or (J.ge(o, J.get(lastOHCL, "c")) and J.le(c, J.get(lastOHCL, "o")))):
                    bottom_2 = J.get(lastOHCL, "o")
                    top_2 = J.undefined
                    supplyZoneIndex = J.undefined
                    if J.ge(o, J.get(lastOHCL, "c")):
                        if J.lt(J.get(lastOHCL, "h"), h):
                            top_2 = h
                            supplyZoneIndex = index
                        else:
                            top_2 = J.get(lastOHCL, "h")
                            supplyZoneIndex = J.sub(index, 1)
                    else:
                        top_2 = J.get(lastOHCL, "h")
                    if J.truthy(J.get(G_Array, "isArray")(J.get(lastOHCL, "supplyZones"))):
                        J.set(J.get(lastOHCL, "supplyZones"), J.sub(index, 1), J.obj(("top", top_2), ("bottom", bottom_2)))
                    else:
                        J.set(lastOHCL, "supplyZones", J.JSArray([]))
        elif J.seq(J.get(lastOHCL, "o"), J.get(lastOHCL, "c")):
            prevCandleBodySize_3 = 0
            if J.gt(c, o):
                currentCandleBodySize_3 = J.sub(c, o)
                if ((J.ge(currentCandleBodySize_3, J.mul(prevCandleBodySize_3, 2)) and J.le(J.get(lastOHCL, "l"), l)) or (J.le(o, J.get(lastOHCL, "c")) and J.ge(c, J.get(lastOHCL, "o")))):
                    top_3 = J.get(lastOHCL, "o")
                    bottom_3 = J.undefined
                    demandZoneIndex_2 = J.undefined
                    if J.le(o, J.get(lastOHCL, "c")):
                        if J.lt(J.get(lastOHCL, "l"), l):
                            bottom_3 = J.get(lastOHCL, "l")
                            demandZoneIndex_2 = J.sub(index, 1)
                        else:
                            bottom_3 = l
                            demandZoneIndex_2 = index
                    else:
                        bottom_3 = J.get(lastOHCL, "l")
                    if J.truthy(J.get(G_Array, "isArray")(J.get(lastOHCL, "demandZones"))):
                        J.set(J.get(lastOHCL, "demandZones"), J.sub(index, 1), J.obj(("top", top_3), ("bottom", bottom_3)))
                    else:
                        J.set(lastOHCL, "demandZones", J.JSArray([]))
            if J.lt(c, o):
                currentCandleBodySize_4 = J.sub(o, c)
                if ((J.ge(currentCandleBodySize_4, J.mul(prevCandleBodySize_3, 2)) and J.ge(J.get(lastOHCL, "h"), h)) or (J.ge(o, J.get(lastOHCL, "c")) and J.le(c, J.get(lastOHCL, "o")))):
                    bottom_4 = J.get(lastOHCL, "o")
                    top_4 = J.undefined
                    supplyZoneIndex_2 = J.undefined
                    if J.ge(o, J.get(lastOHCL, "c")):
                        if J.lt(J.get(lastOHCL, "h"), h):
                            top_4 = h
                            supplyZoneIndex_2 = index
                        else:
                            top_4 = J.get(lastOHCL, "h")
                            supplyZoneIndex_2 = J.sub(index, 1)
                    else:
                        top_4 = J.get(lastOHCL, "h")
                    if J.truthy(J.get(G_Array, "isArray")(J.get(lastOHCL, "supplyZones"))):
                        J.set(J.get(lastOHCL, "supplyZones"), J.sub(index, 1), J.obj(("top", top_4), ("bottom", bottom_4)))
                    else:
                        J.set(lastOHCL, "supplyZones", J.JSArray([]))
        lastOHCL = J.obj(("o", o), ("h", h), ("c", c), ("l", l), ("demandZones", J.get(lastOHCL, "demandZones")), ("supplyZones", J.get(lastOHCL, "supplyZones")))
        return lastOHCL
    series = G_for_every(G_open, G_high, G_close, G_low, _f1)
    series = J.get(series, "slice")((-1))
    demandZones = J.get(J.get(series, 0), "demandZones")
    supplyZones = J.get(J.get(series, 0), "supplyZones")
    areaIndex = 0
    while J.lt(areaIndex, maxNumberOfAreas):
        demandZoneIndex = (J.get(J.get(G_Object, "keys")(demandZones), J.sub(J.sub(J.get(J.get(G_Object, "keys")(demandZones), "length"), areaIndex), 1)) if J.ge(J.get(J.get(G_Object, "keys")(demandZones), "length"), areaIndex) else None)
        demandZone = (J.get(demandZones, demandZoneIndex) if J.truthy(demandZoneIndex) else J.obj(("top", None), ("bottom", None)))
        G_fill(G_paint(G_horizontal_line(J.get(demandZone, "top"), demandZoneIndex), J.add(J.add("Demand Top ", areaIndex), 1), "green", "line", 1, True), G_paint(G_horizontal_line(J.get(demandZone, "bottom"), demandZoneIndex), J.add(J.add("Demand Bottom ", areaIndex), 1), "green", "line", 1, True), "green", 0.2, "Demand")
        supplyZoneIndex = (J.get(J.get(G_Object, "keys")(supplyZones), J.sub(J.sub(J.get(J.get(G_Object, "keys")(supplyZones), "length"), areaIndex), 1)) if J.ge(J.get(J.get(G_Object, "keys")(supplyZones), "length"), areaIndex) else None)
        supplyZone = (J.get(supplyZones, supplyZoneIndex) if J.truthy(supplyZoneIndex) else J.obj(("top", None), ("bottom", None)))
        G_fill(G_paint(G_horizontal_line(J.get(supplyZone, "top"), supplyZoneIndex), J.add(J.add("Supply Top ", areaIndex), 1), "red", "line", 1, True), G_paint(G_horizontal_line(J.get(supplyZone, "bottom"), supplyZoneIndex), J.add(J.add("Supply Bottom ", areaIndex), 1), "red", "line", 1, True), "red", 0.2, "Supply")
        areaIndex = J.inc(areaIndex)


register_store_indicator(
    script,
    name='institutional_supply_and_demand_zones_TS',
    title='Institutional Supply and Demand Zones',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/institutional-supply-and-demand-zones/',
    position='price',
    inputs=[],
    outputs=['demand_top_01', 'demand_bottom_01', 'supply_top_01', 'supply_bottom_01', 'demand_top_11', 'demand_bottom_11', 'supply_top_11', 'supply_bottom_11', 'demand_top_21', 'demand_bottom_21', 'supply_top_21', 'supply_bottom_21', 'demand_top_31', 'demand_bottom_31', 'supply_top_31', 'supply_bottom_31', 'demand_top_41', 'demand_bottom_41', 'supply_top_41', 'supply_bottom_41'],
    signals=[],
    requires=[],
    parity='exact',
)
