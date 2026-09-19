"""
Auto Fib -- TrendSpider store indicator by TrendSpider Team.

Registered as "auto_fib_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/auto-fib/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Array = G["Array"]
    G_Math = G["Math"]
    G_assert = G["assert"]
    G_describe_indicator = G["describe_indicator"]
    G_high = G["high"]
    G_interpolate_sparse_series = G["interpolate_sparse_series"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_low = G["low"]
    G_paint = G["paint"]
    G_paint_projection = G["paint_projection"]
    G_time = G["time"]
    G_describe_indicator("Auto Fib", "price", J.obj(("shortName", "Fib+")))
    lookbackPeriod = 50
    offsetPeriod = 25
    projectionBars = 50
    fibLevels = J.JSArray([J.obj(("level", (-1)), ("color", "#4A00E0"), ("name", "-100%"), ("thickness", 1)), J.obj(("level", (-0.786)), ("color", "#7B68EE"), ("name", "-78.6%"), ("thickness", 1)), J.obj(("level", (-0.618)), ("color", "#9370DB"), ("name", "-61.8%"), ("thickness", 1)), J.obj(("level", (-0.5)), ("color", "#BA55D3"), ("name", "-50%"), ("thickness", 1)), J.obj(("level", (-0.382)), ("color", "#DA70D6"), ("name", "-38.2%"), ("thickness", 1)), J.obj(("level", (-0.236)), ("color", "#EE82EE"), ("name", "-23.6%"), ("thickness", 1)), J.obj(("level", 0), ("color", "white"), ("name", "0%"), ("thickness", 3)), J.obj(("level", 0.236), ("color", "#FFD700"), ("name", "23.6%"), ("thickness", 1)), J.obj(("level", 0.382), ("color", "#FFA500"), ("name", "38.2%"), ("thickness", 1)), J.obj(("level", 0.5), ("color", "#FF8C00"), ("name", "50%"), ("thickness", 1)), J.obj(("level", 0.618), ("color", "#FF4500"), ("name", "61.8%"), ("thickness", 1)), J.obj(("level", 0.786), ("color", "#FF6347"), ("name", "78.6%"), ("thickness", 1)), J.obj(("level", 1), ("color", "white"), ("name", "100%"), ("thickness", 3)), J.obj(("level", 1.382), ("color", "#FF69B4"), ("name", "138.2%"), ("thickness", 1)), J.obj(("level", 1.618), ("color", "#FF1493"), ("name", "161.8%"), ("thickness", 1)), J.obj(("level", 2), ("color", "#DC143C"), ("name", "200%"), ("thickness", 1)), J.obj(("level", 2.618), ("color", "#B22222"), ("name", "261.8%"), ("thickness", 1)), J.obj(("level", 4.236), ("color", "#8B0000"), ("name", "423.6%"), ("thickness", 1))])
    startIndex = J.sub(J.sub(J.get(G_time, "length"), offsetPeriod), lookbackPeriod)
    endIndex = J.sub(J.get(G_time, "length"), offsetPeriod)
    G_assert(J.ge(startIndex, 0), "Not enough data to calculate Fibonacci levels.")
    highRange = J.get(G_high, "slice")(startIndex, endIndex)
    lowRange = J.get(G_low, "slice")(startIndex, endIndex)
    highestHigh = J.get(G_Math, "max")(*J.spread(highRange))
    lowestLow = J.get(G_Math, "min")(*J.spread(lowRange))
    range = J.sub(highestHigh, lowestLow)
    def _f1(_p1=J.undefined, *_args):
        _t2 = J.require_object(_p1)
        level = J.get(_t2, "level")
        color = J.get(_t2, "color")
        name = J.get(_t2, "name")
        thickness = J.get(_t2, "thickness")
        fibValue = J.add(lowestLow, J.mul(range, level))
        series = G_land_points_onto_series(J.JSArray([J.get(G_time, startIndex), J.get(G_time, J.sub(J.get(G_time, "length"), 1))]), J.JSArray([fibValue, fibValue]), G_time)
        fibSeries = G_interpolate_sparse_series(series, "constant")
        lineRef = G_paint(fibSeries, J.obj(("name", J.template(name)), ("color", color), ("thickness", thickness), ("style", "ladder"), ("ignoreWhenScaling", True)))
        projectionValues = J.get(G_Array(projectionBars), "fill")(fibValue)
        G_paint_projection(lineRef, projectionValues)
    J.get(fibLevels, "forEach")(_f1)


register_store_indicator(
    script,
    name='auto_fib_TS',
    title='Auto Fib',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/auto-fib/',
    position='price',
    inputs=[],
    outputs=['_100_', '_78_6_', '_61_8_', '_50_', '_38_2_', '_23_6_', '0_', '23_6_', '38_2_', '50_', '61_8_', '78_6_', '100_', '138_2_', '161_8_', '200_', '261_8_', '423_6_'],
    signals=[],
    requires=[],
    parity='exact',
)
