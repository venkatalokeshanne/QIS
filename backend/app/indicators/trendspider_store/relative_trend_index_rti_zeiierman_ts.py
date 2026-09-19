"""
Relative Trend Index [RTI] (Zeiierman) -- TrendSpider store indicator by Zeiierman Trading.

Registered as "relative_trend_index_rti_zeiierman_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68e78e-relative-trend-index-rti-by-zeiierman/)
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
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_fill = G["fill"]
    G_input = G["input"]
    G_paint = G["paint"]
    G_sma = G["sma"]
    G_describe_indicator("Relative Trend Index [RTI] (Zeiierman)", "lower", J.obj(("decimals", 0), ("shortName", "RTI (Zeiierman)"), ("mainColorInheritFrom", "text")))
    trend_data_count = G_input("Trend Length", 100, J.obj(("min", 1), ("max", 500)))
    signal_length = G_input("Signal Length", 20, J.obj(("min", 1), ("max", 500)))
    ob = G_input("OB", 80, J.obj(("min", 1), ("max", 500)))
    os = G_input("OS", 20, J.obj(("min", 1), ("max", 500)))
    upper_trend = J.get(G_Array(J.get(G_close, "length")), "fill")(0)
    lower_trend = J.get(G_Array(J.get(G_close, "length")), "fill")(0)
    RelativeTrendIndex = J.get(G_Array(J.get(G_close, "length")), "fill")(0)
    overboughtLine = J.get(G_Array(J.get(G_close, "length")), "fill")(ob)
    oversoldLine = J.get(G_Array(J.get(G_close, "length")), "fill")(os)
    midLine = J.get(G_Array(J.get(G_close, "length")), "fill")(50)
    i = trend_data_count
    while J.lt(i, J.get(G_close, "length")):
        J.set(upper_trend, i, J.get(G_Math, "max")(*J.spread(J.get(G_close, "slice")(J.sub(i, trend_data_count), i))))
        J.set(lower_trend, i, J.get(G_Math, "min")(*J.spread(J.get(G_close, "slice")(J.sub(i, trend_data_count), i))))
        J.set(RelativeTrendIndex, i, J.mul(J.div(J.sub(J.get(G_close, i), J.get(lower_trend, i)), J.sub(J.get(upper_trend, i), J.get(lower_trend, i))), 100))
        i = J.inc(i)
    ma_RTI = G_sma(RelativeTrendIndex, signal_length)
    RTI = G_paint(RelativeTrendIndex, "Relative Trend Index (RTI)", "#00897B")
    G_paint(ma_RTI, "RTI Signal Line", "#00bcd4")
    G_paint(overboughtLine, "Overbought", "#606060")
    G_paint(oversoldLine, "Oversold", "#606060")
    G_paint(midLine, "Mid", "#606060", "dotted")
    i_2 = 0
    while J.lt(i_2, J.get(RelativeTrendIndex, "length")):
        J.set(overboughtLine, i_2, (ob if J.gt(J.get(RelativeTrendIndex, i_2), ob) else None))
        J.set(oversoldLine, i_2, (os if J.lt(J.get(RelativeTrendIndex, i_2), os) else None))
        i_2 = J.inc(i_2)
    aboveOBLinePainted = G_paint(overboughtLine, "Above OB", "#606060")
    belowOSLinePainted = G_paint(oversoldLine, "Below OS", "#606060")
    G_fill(RTI, aboveOBLinePainted, "lime", 0.2)
    G_fill(RTI, belowOSLinePainted, "red", 0.2)


register_store_indicator(
    script,
    name='relative_trend_index_rti_zeiierman_TS',
    title='Relative Trend Index [RTI] (Zeiierman)',
    developer='Zeiierman Trading',
    url='https://trendspider.com/trading-tools-store/indicators/68e78e-relative-trend-index-rti-by-zeiierman/',
    position='lower',
    inputs=[{'id': 'trend_length', 'title': 'Trend Length', 'type': 'number', 'default': 100}, {'id': 'signal_length', 'title': 'Signal Length', 'type': 'number', 'default': 20}, {'id': 'ob', 'title': 'OB', 'type': 'number', 'default': 80}, {'id': 'os', 'title': 'OS', 'type': 'number', 'default': 20}],
    outputs=['relative_trend_index__rti_', 'rti_signal_line', 'overbought', 'oversold', 'mid', 'above_ob', 'below_os'],
    signals=[],
    requires=[],
    parity='exact',
)
