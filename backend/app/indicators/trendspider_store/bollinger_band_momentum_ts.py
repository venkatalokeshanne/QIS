"""
Bollinger Band Momentum -- TrendSpider store indicator by TrendSpider Team.

Registered as "bollinger_band_momentum_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/bollinger-band-momentum/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_add = G["add"]
    G_close = G["close"]
    G_color_candles = G["color_candles"]
    G_describe_indicator = G["describe_indicator"]
    G_ema = G["ema"]
    G_for_every = G["for_every"]
    G_input = G["input"]
    G_mult = G["mult"]
    G_register_signal = G["register_signal"]
    G_sma = G["sma"]
    G_stdev = G["stdev"]
    G_sub = G["sub"]
    G_describe_indicator("Bollinger Band Momentum")
    bbPeriod = J.get(G_input, "number")("BB Period", 20, J.obj(("min", 1)))
    bbDeviation = J.get(G_input, "number")("BB Deviation", 2, J.obj(("min", 0.1), ("step", 0.1)))
    macdFastPeriod = J.get(G_input, "number")("MACD Fast Period", 12, J.obj(("min", 1)))
    macdSlowPeriod = J.get(G_input, "number")("MACD Slow Period", 26, J.obj(("min", 1)))
    macdSignalPeriod = J.get(G_input, "number")("MACD Signal Period", 9, J.obj(("min", 1)))
    bullishColor = J.get(G_input, "color")("Bullish Color", "green")
    bearishColor = J.get(G_input, "color")("Bearish Color", "red")
    neutralColor = J.get(G_input, "color")("Neutral Color", "grey")
    bbMA = G_sma(G_close, bbPeriod)
    bbStdDev = G_stdev(G_close, bbPeriod)
    bbUpper = G_add(bbMA, G_mult(bbStdDev, bbDeviation))
    bbLower = G_sub(bbMA, G_mult(bbStdDev, bbDeviation))
    macdFast = G_ema(G_close, macdFastPeriod)
    macdSlow = G_ema(G_close, macdSlowPeriod)
    macdLine = G_sub(macdFast, macdSlow)
    signalLine = G_ema(macdLine, macdSignalPeriod)
    macdHistogram = G_sub(macdLine, signalLine)
    def _f1(_close=J.undefined, _bbUpper=J.undefined, _bbLower=J.undefined, _macdHistogram=J.undefined, *_args):
        if (J.gt(_close, _bbUpper) and J.gt(_macdHistogram, 0)):
            return bullishColor
        elif (J.lt(_close, _bbLower) and J.lt(_macdHistogram, 0)):
            return bearishColor
        else:
            return neutralColor
    candleColors = G_for_every(G_close, bbUpper, bbLower, macdHistogram, _f1)
    G_color_candles(candleColors)
    def _f2(_close=J.undefined, _bbUpper=J.undefined, _macdHistogram=J.undefined, *_args):
        return (J.gt(_macdHistogram, 0) if J.truthy(_t1 := J.gt(_close, _bbUpper)) else _t1)
    G_register_signal(G_for_every(G_close, bbUpper, macdHistogram, _f2), "Bullish Signal")
    def _f3(_close=J.undefined, _bbLower=J.undefined, _macdHistogram=J.undefined, *_args):
        return (J.lt(_macdHistogram, 0) if J.truthy(_t1 := J.lt(_close, _bbLower)) else _t1)
    G_register_signal(G_for_every(G_close, bbLower, macdHistogram, _f3), "Bearish Signal")


register_store_indicator(
    script,
    name='bollinger_band_momentum_TS',
    title='Bollinger Band Momentum',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/bollinger-band-momentum/',
    position='price',
    inputs=[{'id': 'bb_period', 'title': 'BB Period', 'type': 'number', 'default': 20}, {'id': 'bb_deviation', 'title': 'BB Deviation', 'type': 'number', 'default': 2}, {'id': 'macd_fast_period', 'title': 'MACD Fast Period', 'type': 'number', 'default': 12}, {'id': 'macd_slow_period', 'title': 'MACD Slow Period', 'type': 'number', 'default': 26}, {'id': 'macd_signal_period', 'title': 'MACD Signal Period', 'type': 'number', 'default': 9}, {'id': 'bullish_color', 'title': 'Bullish Color', 'type': 'color', 'default': 'green'}, {'id': 'bearish_color', 'title': 'Bearish Color', 'type': 'color', 'default': 'red'}, {'id': 'neutral_color', 'title': 'Neutral Color', 'type': 'color', 'default': 'grey'}],
    outputs=['cdl', 'bullish_signal', 'bearish_signal'],
    signals=['bullish_signal', 'bearish_signal'],
    requires=[],
    parity='exact',
)
