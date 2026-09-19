"""
Daily EMA 8/21/50 Band [RKPDTRADE5] -- TrendSpider store indicator by Raj Kothari.

Registered as "daily_ema_8_21_50_band_rkpdtrade5_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6aa3ab-daily-ema-8-21-50-band-rkpdtrade5/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_color_cloud = G["color_cloud"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_ema = G["ema"]
    G_for_every = G["for_every"]
    G_input = G["input"]
    G_interpolate_sparse_series = G["interpolate_sparse_series"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_request = G["request"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    def offsetSeries(series=J.undefined, bars=J.undefined, *_args):
        if J.seq(bars, 0):
            return series
        output = G_series_of(None)
        i = 0
        while J.lt(i, J.get(series, "length")):
            sourceIndex = J.sub(i, bars)
            if (J.lt(sourceIndex, 0) or J.ge(sourceIndex, J.get(series, "length"))):
                J.set(output, i, None)
            else:
                J.set(output, i, J.get(series, sourceIndex))
            i = J.inc(i)
        return output
    G_describe_indicator("Daily EMA 8/21/50 Band [RKPDTRADE5]", "price")
    sourceInput = J.get(G_input, "select")("Source", "Close", J.JSArray(["Close", "Open", "High", "Low", "HL2", "HLC3", "OHLC4"]))
    offset = J.get(G_input, "number")("Offset", 0, J.obj(("min", (-100)), ("max", 100), ("step", 1)))
    dailyData = J.get(G_request, "history")(J.get(G_current, "ticker"), "D")
    def _f1(h=J.undefined, l=J.undefined, *_args):
        if ((J.nullish(h)) or (J.nullish(l))):
            return None
        return J.div(J.add(h, l), 2)
    dailyHL2 = G_for_every(J.get(dailyData, "high"), J.get(dailyData, "low"), _f1)
    def _f2(h=J.undefined, l=J.undefined, c=J.undefined, *_args):
        if (((J.nullish(h)) or (J.nullish(l))) or (J.nullish(c))):
            return None
        return J.div(J.add(J.add(h, l), c), 3)
    dailyHLC3 = G_for_every(J.get(dailyData, "high"), J.get(dailyData, "low"), J.get(dailyData, "close"), _f2)
    def _f3(o=J.undefined, h=J.undefined, l=J.undefined, c=J.undefined, *_args):
        if ((((J.nullish(o)) or (J.nullish(h))) or (J.nullish(l))) or (J.nullish(c))):
            return None
        return J.div(J.add(J.add(J.add(o, h), l), c), 4)
    dailyOHLC4 = G_for_every(J.get(dailyData, "open"), J.get(dailyData, "high"), J.get(dailyData, "low"), J.get(dailyData, "close"), _f3)
    dailySource = J.get(dailyData, "close")
    if J.seq(sourceInput, "Open"):
        dailySource = J.get(dailyData, "open")
    elif J.seq(sourceInput, "High"):
        dailySource = J.get(dailyData, "high")
    elif J.seq(sourceInput, "Low"):
        dailySource = J.get(dailyData, "low")
    elif J.seq(sourceInput, "HL2"):
        dailySource = dailyHL2
    elif J.seq(sourceInput, "HLC3"):
        dailySource = dailyHLC3
    elif J.seq(sourceInput, "OHLC4"):
        dailySource = dailyOHLC4
    dailyEMA8 = G_ema(dailySource, 8)
    dailyEMA21 = G_ema(dailySource, 21)
    dailyEMA50 = G_ema(dailySource, 50)
    ema8Landed = G_land_points_onto_series(J.get(dailyData, "time"), dailyEMA8, G_time)
    ema21Landed = G_land_points_onto_series(J.get(dailyData, "time"), dailyEMA21, G_time)
    ema50Landed = G_land_points_onto_series(J.get(dailyData, "time"), dailyEMA50, G_time)
    ema8Mapped = G_interpolate_sparse_series(ema8Landed, "constant")
    ema21Mapped = G_interpolate_sparse_series(ema21Landed, "constant")
    ema50Mapped = G_interpolate_sparse_series(ema50Landed, "constant")
    ema8 = offsetSeries(ema8Mapped, offset)
    ema21 = offsetSeries(ema21Mapped, offset)
    ema50 = offsetSeries(ema50Mapped, offset)
    EMA8_COLOR = "#4CAF50"
    EMA21_COLOR = "#16B9D4"
    EMA50_COLOR = "#FF7A75"
    G_paint(ema8, J.obj(("name", "8-Day EMA"), ("color", EMA8_COLOR), ("style", "line"), ("width", 2)))
    G_paint(ema21, J.obj(("name", "21-Day EMA"), ("color", EMA21_COLOR), ("style", "line"), ("width", 2)))
    G_paint(ema50, J.obj(("name", "50-Day EMA"), ("color", EMA50_COLOR), ("style", "line"), ("width", 2)))
    G_color_cloud(ema8, ema21, "rgba(70,130,75,0.20)", "rgba(145,65,75,0.20)", "Bullish EMA Band", "Bearish EMA Band")
    def _f4(fast=J.undefined, slow=J.undefined, __=J.undefined, index=J.undefined, *_args):
        if J.lt(index, 1):
            return False
        previousFast = J.get(ema8, J.sub(index, 1))
        previousSlow = J.get(ema21, J.sub(index, 1))
        if ((((J.nullish(fast)) or (J.nullish(slow))) or (J.nullish(previousFast))) or (J.nullish(previousSlow))):
            return False
        return (J.gt(fast, slow) if J.truthy(_t1 := J.le(previousFast, previousSlow)) else _t1)
    bullishCross = G_for_every(ema8, ema21, _f4)
    def _f5(fast=J.undefined, slow=J.undefined, __=J.undefined, index=J.undefined, *_args):
        if J.lt(index, 1):
            return False
        previousFast = J.get(ema8, J.sub(index, 1))
        previousSlow = J.get(ema21, J.sub(index, 1))
        if ((((J.nullish(fast)) or (J.nullish(slow))) or (J.nullish(previousFast))) or (J.nullish(previousSlow))):
            return False
        return (J.lt(fast, slow) if J.truthy(_t1 := J.ge(previousFast, previousSlow)) else _t1)
    bearishCross = G_for_every(ema8, ema21, _f5)
    G_register_signal(bullishCross, "Daily EMA 8 Cross Above EMA 21")
    G_register_signal(bearishCross, "Daily EMA 8 Cross Below EMA 21")


register_store_indicator(
    script,
    name='daily_ema_8_21_50_band_rkpdtrade5_TS',
    title='Daily EMA 8/21/50 Band [RKPDTRADE5]',
    developer='Raj Kothari',
    url='https://trendspider.com/trading-tools-store/indicators/6aa3ab-daily-ema-8-21-50-band-rkpdtrade5/',
    position='price',
    inputs=[{'id': 'source', 'title': 'Source', 'type': 'select_wide', 'default': 'Close', 'options': ['Close', 'Open', 'High', 'Low', 'HL2', 'HLC3', 'OHLC4']}, {'id': 'offset', 'title': 'Offset', 'type': 'number', 'default': 0}],
    outputs=['8_day_ema', '21_day_ema', '50_day_ema', 'line_4', 'line_5', 'line_7', 'line_8', 'daily_ema_8_cross_above_ema_21', 'daily_ema_8_cross_below_ema_21'],
    signals=['daily_ema_8_cross_above_ema_21', 'daily_ema_8_cross_below_ema_21'],
    requires=['history'],
    parity='exact',
)
