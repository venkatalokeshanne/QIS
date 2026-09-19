"""
Red Dragon MCDX -- TrendSpider store indicator by Rock Regan.

Registered as "red_dragon_mcdx_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68ae72-red-dragon-mcdx/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_add = G["add"]
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_div = G["div"]
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_highest = G["highest"]
    G_input = G["input"]
    G_low = G["low"]
    G_lowest = G["lowest"]
    G_mult = G["mult"]
    G_paint = G["paint"]
    G_paint_overlay = G["paint_overlay"]
    G_register_signal = G["register_signal"]
    G_series_of = G["series_of"]
    G_sma = G["sma"]
    G_sub = G["sub"]
    G_volume = G["volume"]
    G_describe_indicator("Red Dragon MCDX", "lower")
    mcdx_length = J.get(G_input, "number")("MCDX Length", 100, J.obj(("min", 1)))
    avg_length = J.get(G_input, "number")("Average Length", 5, J.obj(("min", 1)))
    showTable = J.get(G_input, "boolean")("Show Table", True)
    hh = G_highest(G_high, mcdx_length)
    ll = G_lowest(G_low, mcdx_length)
    rg = G_sub(hh, ll)
    mid = G_div(G_add(hh, ll), 2)
    pc1 = G_mult(G_div(G_sub(G_close, ll), rg), 100)
    pc2 = G_mult(G_div(G_sub(G_close, mid), rg), 100)
    pc3 = G_add(G_div(G_add(pc1, pc2), 2), 25)
    def _f1(v=J.undefined, *_args):
        return J.get(G_Math, "min")(100, J.get(G_Math, "max")(0, v))
    profitChips = G_for_every(pc3, _f1)
    lc1 = G_div(G_sub(hh, G_close), rg)
    lc2 = G_mult(lc1, 100)
    lc3 = G_sub(G_series_of(100), lc2)
    lc4 = G_add(lc3, 25)
    def _f2(v=J.undefined, *_args):
        return J.get(G_Math, "min")(100, J.get(G_Math, "max")(0, v))
    floatChips = G_for_every(lc4, _f2)
    lockedChips = G_sub(G_series_of(100), floatChips)
    rockChips = G_sub(G_series_of(100), G_add(profitChips, lockedChips))
    avgProfit = G_sma(profitChips, avg_length)
    avgLocked = G_sma(lockedChips, avg_length)
    avgRock = G_sma(rockChips, avg_length)
    avgVol = G_sma(G_volume, avg_length)
    volRatio = G_div(G_volume, avgVol)
    def _f3(v=J.undefined, *_args):
        return ("#DB7093" if J.lt(v, 50) else "red")
    profitColor = G_for_every(profitChips, _f3)
    G_paint(lockedChips, J.obj(("style", "stacked_histogram"), ("color", "limegreen"), ("name", "Locked (Retail)"), ("padding", 0.05)))
    G_paint(rockChips, J.obj(("style", "stacked_histogram"), ("color", "#f4e203"), ("name", "Rock (Float)"), ("padding", 0.05)))
    G_paint(profitChips, J.obj(("style", "stacked_histogram"), ("color", profitColor), ("name", "Profit (Instl)"), ("padding", 0.05)))
    G_paint(avgProfit, J.obj(("style", "line"), ("color", "darkred"), ("name", "Avg Profit")))
    G_paint(avgLocked, J.obj(("style", "line"), ("color", "darkgreen"), ("name", "Avg Locked")))
    G_paint(avgRock, J.obj(("style", "line"), ("color", "#b7a800"), ("name", "Avg Rock")))
    def _f4(v=J.undefined, *_args):
        return J.gt(v, 50)
    G_register_signal(G_for_every(profitChips, _f4), "Profit Chips > 50")
    last = J.get(G_Math, "max")(0, J.sub(J.get(G_close, "length"), 1))
    visibleRows = J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", "Instl:"), ("color", "white"), ("background", J.get(profitColor, last)), ("padding", "1px 6px")), J.obj(("text", J.get(J.get(profitChips, last), "toFixed")(1)), ("color", "white"), ("background", J.get(profitColor, last)), ("padding", "1px 6px")), J.obj(("text", "Retail:"), ("color", "white"), ("background", "green"), ("padding", "1px 6px")), J.obj(("text", J.get(J.get(lockedChips, last), "toFixed")(1)), ("color", "white"), ("background", "green"), ("padding", "1px 6px")), J.obj(("text", "Float:"), ("color", "black"), ("background", "#f4e203"), ("padding", "1px 6px")), J.obj(("text", J.get(J.get(rockChips, last), "toFixed")(1)), ("color", "black"), ("background", "#f4e203"), ("padding", "1px 6px")), J.obj(("text", "Vol Ratio:"), ("color", "white"), ("background", "blue"), ("padding", "1px 6px")), J.obj(("text", J.get(J.get(volRatio, last), "toFixed")(2)), ("color", "white"), ("background", "blue"), ("padding", "1px 6px"))])))])
    hiddenRows = J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", ""), ("color", "transparent"), ("background", "transparent"), ("padding", "0"))])))])
    overlayStyle = (J.obj(("fontSize", 12), ("rowGap", "2px"), ("opacity", 1)) if J.truthy(showTable) else J.obj(("fontSize", 1), ("rowGap", "0px"), ("opacity", 0), ("padding", 0), ("margin", 0), ("border", "none")))
    G_paint_overlay("RedDragonOverlay", J.obj(("position", "bottom_right"), ("order", "above_all"), ("offset_x", (-40)), ("offset_y", 0)), J.obj(*J.obj_spread(overlayStyle), ("rows", (visibleRows if J.truthy(showTable) else hiddenRows))))


register_store_indicator(
    script,
    name='red_dragon_mcdx_TS',
    title='Red Dragon MCDX',
    developer='Rock Regan',
    url='https://trendspider.com/trading-tools-store/indicators/68ae72-red-dragon-mcdx/',
    position='lower',
    inputs=[{'id': 'mcdx_length', 'title': 'MCDX Length', 'type': 'number', 'default': 100}, {'id': 'average_length', 'title': 'Average Length', 'type': 'number', 'default': 5}, {'id': 'show_table', 'title': 'Show Table', 'type': 'boolean', 'default': True}],
    outputs=['locked__retail_', 'rock__float_', 'profit__instl_', 'avg_profit', 'avg_locked', 'avg_rock', 'profit_chips___50'],
    signals=['profit_chips___50'],
    requires=[],
    parity='exact',
)
