"""
Daily ATR Support and Resistance Levels -- TrendSpider store indicator by TrendSpider Team.

Registered as "daily_atr_support_and_resistance_levels_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/daily-atr-support-and-resistance-levels/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_atr = G["atr"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_input = G["input"]
    G_interpolate_sparse_series = G["interpolate_sparse_series"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_paint = G["paint"]
    G_request = G["request"]
    G_time = G["time"]
    G_describe_indicator("ATR Support and Resistance Levels", "overlay", J.obj(("shortName", "ATR S/R")))
    atrPeriod = J.get(G_input, "number")("ATR Period", 14)
    multiplierS1 = J.get(G_input, "number")("S1 Multiplier", (-1), J.obj(("min", (-10)), ("max", 0)))
    multiplierS2 = J.get(G_input, "number")("S2 Multiplier", (-1.5), J.obj(("min", (-10)), ("max", 0)))
    multiplierR1 = J.get(G_input, "number")("R1 Multiplier", 1, J.obj(("min", 0), ("max", 10)))
    multiplierR2 = J.get(G_input, "number")("R2 Multiplier", 1.5, J.obj(("min", 0), ("max", 10)))
    dailyData = J.get(G_request, "history")(J.get(G_current, "ticker"), "D", J.obj(("land_onto_current_candles", False)))
    dailyATR = G_atr(J.get(dailyData, "high"), J.get(dailyData, "low"), J.get(dailyData, "close"), atrPeriod)
    def _f1(closePrice=J.undefined, index=J.undefined, *_args):
        return (J.add(J.get(J.get(dailyData, "close"), J.sub(index, 1)), J.mul(multiplierS1, J.get(dailyATR, J.sub(index, 1)))) if J.gt(index, 0) else None)
    s1_daily = J.get(J.get(dailyData, "close"), "map")(_f1)
    def _f2(closePrice=J.undefined, index=J.undefined, *_args):
        return (J.add(J.get(J.get(dailyData, "close"), J.sub(index, 1)), J.mul(multiplierS2, J.get(dailyATR, J.sub(index, 1)))) if J.gt(index, 0) else None)
    s2_daily = J.get(J.get(dailyData, "close"), "map")(_f2)
    def _f3(closePrice=J.undefined, index=J.undefined, *_args):
        return (J.add(J.get(J.get(dailyData, "close"), J.sub(index, 1)), J.mul(multiplierR1, J.get(dailyATR, J.sub(index, 1)))) if J.gt(index, 0) else None)
    r1_daily = J.get(J.get(dailyData, "close"), "map")(_f3)
    def _f4(closePrice=J.undefined, index=J.undefined, *_args):
        return (J.add(J.get(J.get(dailyData, "close"), J.sub(index, 1)), J.mul(multiplierR2, J.get(dailyATR, J.sub(index, 1)))) if J.gt(index, 0) else None)
    r2_daily = J.get(J.get(dailyData, "close"), "map")(_f4)
    s1_intraday = G_land_points_onto_series(J.get(dailyData, "time"), s1_daily, G_time)
    s2_intraday = G_land_points_onto_series(J.get(dailyData, "time"), s2_daily, G_time)
    r1_intraday = G_land_points_onto_series(J.get(dailyData, "time"), r1_daily, G_time)
    r2_intraday = G_land_points_onto_series(J.get(dailyData, "time"), r2_daily, G_time)
    G_paint(G_interpolate_sparse_series(s1_intraday, "constant"), J.obj(("name", "S1"), ("color", "#38751d"), ("thickness", 2)))
    G_paint(G_interpolate_sparse_series(s2_intraday, "constant"), J.obj(("name", "S2"), ("color", "#5d9445"), ("thickness", 2)))
    G_paint(G_interpolate_sparse_series(r1_intraday, "constant"), J.obj(("name", "R1"), ("color", "#982414"), ("thickness", 2)))
    G_paint(G_interpolate_sparse_series(r2_intraday, "constant"), J.obj(("name", "R2"), ("color", "#cb5949"), ("thickness", 2)))


register_store_indicator(
    script,
    name='daily_atr_support_and_resistance_levels_TS',
    title='Daily ATR Support and Resistance Levels',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/daily-atr-support-and-resistance-levels/',
    position='price',
    inputs=[{'id': 'atr_period', 'title': 'ATR Period', 'type': 'number', 'default': 14}, {'id': 's1_multiplier', 'title': 'S1 Multiplier', 'type': 'number', 'default': -1}, {'id': 's2_multiplier', 'title': 'S2 Multiplier', 'type': 'number', 'default': -1.5}, {'id': 'r1_multiplier', 'title': 'R1 Multiplier', 'type': 'number', 'default': 1}, {'id': 'r2_multiplier', 'title': 'R2 Multiplier', 'type': 'number', 'default': 1.5}],
    outputs=['s1', 's2', 'r1', 'r2'],
    signals=[],
    requires=['history'],
    parity='exact',
)
