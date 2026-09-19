"""
RSI, MACD Confluence -- TrendSpider store indicator by TrendSpider Team.

Registered as "rsi_macd_confluence_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/rsi-macd-confluence/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Boolean = G["Boolean"]
    G_close = G["close"]
    G_color_candles = G["color_candles"]
    G_describe_indicator = G["describe_indicator"]
    G_ema = G["ema"]
    G_for_every = G["for_every"]
    G_input = G["input"]
    G_register_signal = G["register_signal"]
    G_rsi = G["rsi"]
    G_sub = G["sub"]
    G_describe_indicator("RSI, MACD Confluence")
    rsiLength = J.get(G_input, "number")("RSI Length", 14, J.obj(("min", 1)))
    macdFastLength = J.get(G_input, "number")("MACD Fast Length", 12, J.obj(("min", 1)))
    macdSlowLength = J.get(G_input, "number")("MACD Slow Length", 26, J.obj(("min", 1)))
    macdSignalLength = J.get(G_input, "number")("MACD Signal Length", 9, J.obj(("min", 1)))
    myRsi = G_rsi(G_close, rsiLength)
    myMacdLine = G_sub(G_ema(G_close, macdFastLength), G_ema(G_close, macdSlowLength))
    mySignalLine = G_ema(myMacdLine, macdSignalLength)
    myHistogram = G_sub(myMacdLine, mySignalLine)
    def _f1(r=J.undefined, *_args):
        return J.gt(r, 50)
    rsiCondition = G_for_every(myRsi, _f1)
    def _f2(m=J.undefined, s=J.undefined, *_args):
        return J.gt(m, s)
    macdOverSignalCondition = G_for_every(myMacdLine, mySignalLine, _f2)
    def _f3(rsi=J.undefined, macdSignal=J.undefined, *_args):
        trueCount = J.get(J.get(J.JSArray([rsi, macdSignal]), "filter")(G_Boolean), "length")
        if J.seq(trueCount, 2):
            return "#2fcc56"
        if J.gt(trueCount, 0):
            return "lightgray"
        return "red"
    candleColors = G_for_every(rsiCondition, macdOverSignalCondition, _f3)
    G_color_candles(candleColors)
    def _f4(c=J.undefined, *_args):
        return J.seq(c, "#2fcc56")
    G_register_signal(G_for_every(candleColors, _f4), "Strong Bullish (Green)")
    def _f5(c=J.undefined, *_args):
        return J.seq(c, "lightgray")
    G_register_signal(G_for_every(candleColors, _f5), "Neutral (Gray)")
    def _f6(c=J.undefined, *_args):
        return J.seq(c, "red")
    G_register_signal(G_for_every(candleColors, _f6), "Bearish (Red)")


register_store_indicator(
    script,
    name='rsi_macd_confluence_TS',
    title='RSI, MACD Confluence',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/rsi-macd-confluence/',
    position='price',
    inputs=[{'id': 'rsi_length', 'title': 'RSI Length', 'type': 'number', 'default': 14}, {'id': 'macd_fast_length', 'title': 'MACD Fast Length', 'type': 'number', 'default': 12}, {'id': 'macd_slow_length', 'title': 'MACD Slow Length', 'type': 'number', 'default': 26}, {'id': 'macd_signal_length', 'title': 'MACD Signal Length', 'type': 'number', 'default': 9}],
    outputs=['cdl', 'strong_bullish__green_', 'neutral__gray_', 'bearish__red_'],
    signals=['strong_bullish__green_', 'neutral__gray_', 'bearish__red_'],
    requires=[],
    parity='exact',
)
