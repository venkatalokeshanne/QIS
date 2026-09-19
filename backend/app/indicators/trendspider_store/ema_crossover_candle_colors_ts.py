"""
EMA Crossover Candle Colors -- TrendSpider store indicator by TrendSpider Team.

Registered as "ema_crossover_candle_colors_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/ema-crossover-candle-colors/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_close = G["close"]
    G_color_candles = G["color_candles"]
    G_describe_indicator = G["describe_indicator"]
    G_ema = G["ema"]
    G_for_every = G["for_every"]
    G_input = G["input"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_describe_indicator("EMA Crossover Candle Colors")
    fastLength = J.get(G_input, "number")("Fast EMA Length", 8, J.obj(("min", 1)))
    slowLength = J.get(G_input, "number")("Slow EMA Length", 21, J.obj(("min", 1)))
    bullishColor = J.get(G_input, "color")("Bullish Candle Color", "green")
    bearishColor = J.get(G_input, "color")("Bearish Candle Color", "red")
    neutralColor = J.get(G_input, "color")("Neutral Candle Color", "gray")
    fastEMA = G_ema(G_close, fastLength)
    slowEMA = G_ema(G_close, slowLength)
    def _f1(_fast=J.undefined, _slow=J.undefined, *_args):
        return J.gt(_fast, _slow)
    G_register_signal(G_for_every(fastEMA, slowEMA, _f1), "Bullish")
    def _f2(_fast=J.undefined, _slow=J.undefined, *_args):
        return J.lt(_fast, _slow)
    G_register_signal(G_for_every(fastEMA, slowEMA, _f2), "Bearish")
    def _f3(_fast=J.undefined, _slow=J.undefined, *_args):
        if J.gt(_fast, _slow):
            return bullishColor
        elif J.lt(_fast, _slow):
            return bearishColor
        return neutralColor
    candleColors = G_for_every(fastEMA, slowEMA, _f3)
    G_color_candles(candleColors)
    G_paint(fastEMA, J.obj(("color", "blue"), ("name", J.template(fastLength, " EMA"))))
    G_paint(slowEMA, J.obj(("color", "orange"), ("name", J.template(slowLength, " EMA"))))


register_store_indicator(
    script,
    name='ema_crossover_candle_colors_TS',
    title='EMA Crossover Candle Colors',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/ema-crossover-candle-colors/',
    position='price',
    inputs=[{'id': 'fast_ema_length', 'title': 'Fast EMA Length', 'type': 'number', 'default': 8}, {'id': 'slow_ema_length', 'title': 'Slow EMA Length', 'type': 'number', 'default': 21}, {'id': 'bullish_candle_color', 'title': 'Bullish Candle Color', 'type': 'color', 'default': 'green'}, {'id': 'bearish_candle_color', 'title': 'Bearish Candle Color', 'type': 'color', 'default': 'red'}, {'id': 'neutral_candle_color', 'title': 'Neutral Candle Color', 'type': 'color', 'default': 'gray'}],
    outputs=['bullish', 'bearish', 'cdl', '8_ema', '21_ema'],
    signals=['bullish', 'bearish'],
    requires=[],
    parity='exact',
)
