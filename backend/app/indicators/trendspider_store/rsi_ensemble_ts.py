"""
RSI Ensemble -- TrendSpider store indicator by TrendSpider Team.

Registered as "rsi_ensemble_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/rsi-ensemble/)
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
    G_for_every = G["for_every"]
    G_register_signal = G["register_signal"]
    G_rsi = G["rsi"]
    G_describe_indicator("RSI Ensemble")
    OVERBOUGHT_LEVEL = 80
    COLOR_BY_SCORE = J.obj(("0", "gray"), ("1", "yellow"), ("2", "orange"), ("3", "red"))
    def scoreOfRSI(length=J.undefined, *_args):
        def _f1(rsiValue=J.undefined, *_args):
            return (1 if J.gt(rsiValue, OVERBOUGHT_LEVEL) else 0)
        return G_for_every(G_rsi(G_close, length), _f1)
    summaryScores = G_add(scoreOfRSI(14), scoreOfRSI(9), scoreOfRSI(5))
    def _f1(score=J.undefined, *_args):
        return J.get(COLOR_BY_SCORE, score)
    G_color_candles(G_for_every(summaryScores, _f1))
    def _f2(value=J.undefined, *_args):
        return J.seq(value, 3)
    G_register_signal(J.get(summaryScores, "map")(_f2), "Surely Overbought")
    def _f3(value=J.undefined, *_args):
        return J.seq(value, 2)
    G_register_signal(J.get(summaryScores, "map")(_f3), "Probably Overbought")


register_store_indicator(
    script,
    name='rsi_ensemble_TS',
    title='RSI Ensemble',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/rsi-ensemble/',
    position='price',
    inputs=[],
    outputs=['cdl', 'surely_overbought', 'probably_overbought'],
    signals=['surely_overbought', 'probably_overbought'],
    requires=[],
    parity='exact',
)
