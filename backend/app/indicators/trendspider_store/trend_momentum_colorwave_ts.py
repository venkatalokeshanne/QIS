"""
Trend Momentum ColorWave -- TrendSpider store indicator by James Chambers.

Registered as "trend_momentum_colorwave_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/trend-momentum-colorwave/)
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
    G_sma = G["sma"]
    G_sub = G["sub"]
    G_supertrend = G["supertrend"]
    G_describe_indicator("Trend Momentum ColorWave")
    fastLength = 12
    slowLength = 26
    signalSmoothing = 9
    fastMA = G_ema(G_close, fastLength)
    slowMA = G_ema(G_close, slowLength)
    macdLine = G_sub(fastMA, slowMA)
    signalLine = G_sma(macdLine, signalSmoothing)
    superTrendValues = G_supertrend(14, 3)
    def _f1(price=J.undefined, macd=J.undefined, signal=J.undefined, superTrend=J.undefined, *_args):
        if (J.gt(price, superTrend) and J.gt(macd, signal)):
            return "green"
        elif (J.lt(price, superTrend) and J.lt(macd, signal)):
            return "red"
        elif (J.lt(price, superTrend) and J.gt(macd, signal)):
            return "orange"
        elif (J.gt(price, superTrend) and J.lt(macd, signal)):
            return "purple"
        else:
            return "blue"
    candleColors = G_for_every(G_close, macdLine, signalLine, superTrendValues, _f1)
    G_color_candles(candleColors)


register_store_indicator(
    script,
    name='trend_momentum_colorwave_TS',
    title='Trend Momentum ColorWave',
    developer='James Chambers',
    url='https://trendspider.com/trading-tools-store/indicators/trend-momentum-colorwave/',
    position='price',
    inputs=[],
    outputs=['cdl'],
    signals=[],
    requires=[],
    parity='exact',
)
