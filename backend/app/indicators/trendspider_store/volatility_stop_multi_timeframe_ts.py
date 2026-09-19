"""
Volatility Stop Multi-Timeframe -- TrendSpider store indicator by khaled elsokkary.

Registered as "volatility_stop_multi_timeframe_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68aa15-volatility-stop-multi-timeframe/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
aapl_d: OK, syn_5m: both-error.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_assert = G["assert"]
    G_atr = G["atr"]
    G_close = G["close"]
    G_color_candles = G["color_candles"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_highest = G["highest"]
    G_input = G["input"]
    G_interpolate_sparse_series = G["interpolate_sparse_series"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_lowest = G["lowest"]
    G_paint = G["paint"]
    G_request = G["request"]
    G_time = G["time"]
    G_describe_indicator("Volatility Stop Multi-Timeframe")
    length = J.get(G_input, "number")("ATR Length", 14, J.obj(("min", 1)))
    multiplier = J.get(G_input, "number")("ATR Multiplier", 3, J.obj(("min", 0.1)))
    def calculateVolatilityStop(resolution=J.undefined, *_args):
        data = J.get(G_request, "history")(J.get(G_current, "ticker"), resolution)
        G_assert((not J.truthy(J.get(data, "error"))), J.template("Error fetching ", resolution, " data: ", J.get(data, "error")))
        atrData = G_atr(J.get(data, "high"), J.get(data, "low"), J.get(data, "close"), length)
        highestHigh = G_highest(J.get(data, "high"), length)
        lowestLow = G_lowest(J.get(data, "low"), length)
        def _f1(c=J.undefined, a=J.undefined, h=J.undefined, l=J.undefined, *_args):
            return (J.sub(h, J.mul(multiplier, a)) if J.gt(c, J.sub(h, J.mul(multiplier, a))) else J.add(l, J.mul(multiplier, a)))
        volatilityStop = G_for_every(J.get(data, "close"), atrData, highestHigh, lowestLow, _f1)
        return G_land_points_onto_series(J.get(data, "time"), volatilityStop, G_time, "ge")
    dailyStop = calculateVolatilityStop("D")
    weeklyStop = calculateVolatilityStop("W")
    monthlyStop = calculateVolatilityStop("M")
    dailyStopInterpolated = G_interpolate_sparse_series(dailyStop, "constant")
    weeklyStopInterpolated = G_interpolate_sparse_series(weeklyStop, "constant")
    monthlyStopInterpolated = G_interpolate_sparse_series(monthlyStop, "constant")
    def _f1(c=J.undefined, d=J.undefined, w=J.undefined, m=J.undefined, *_args):
        return ("green" if ((J.gt(c, d) and J.gt(c, w)) and J.gt(c, m)) else "violet")
    candleColors = G_for_every(G_close, dailyStopInterpolated, weeklyStopInterpolated, monthlyStopInterpolated, _f1)
    G_color_candles(candleColors)
    G_paint(dailyStopInterpolated, J.obj(("name", "Daily Volatility Stop"), ("color", "blue")))
    G_paint(weeklyStopInterpolated, J.obj(("name", "Weekly Volatility Stop"), ("color", "orange")))
    G_paint(monthlyStopInterpolated, J.obj(("name", "Monthly Volatility Stop"), ("color", "red")))


register_store_indicator(
    script,
    name='volatility_stop_multi_timeframe_TS',
    title='Volatility Stop Multi-Timeframe',
    developer='khaled elsokkary',
    url='https://trendspider.com/trading-tools-store/indicators/68aa15-volatility-stop-multi-timeframe/',
    position='price',
    inputs=[{'id': 'atr_length', 'title': 'ATR Length', 'type': 'number', 'default': 14}, {'id': 'atr_multiplier', 'title': 'ATR Multiplier', 'type': 'number', 'default': 3}],
    outputs=['cdl', 'daily_volatility_stop', 'weekly_volatility_stop', 'monthly_volatility_stop'],
    signals=[],
    requires=['history'],
    parity='aapl_d: OK, syn_5m: both-error',
)
