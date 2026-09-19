"""
Drawdown from ATH % -- TrendSpider store indicator by TrendSpider.

Registered as "drawdown_from_ath_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/69effd-drawdown-from-ath/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_horizontal_line = G["horizontal_line"]
    G_paint = G["paint"]
    G_describe_indicator("Drawdown from ATH %", "lower")
    def _f1(_close=J.undefined, _prevATH=J.undefined, *_args):
        if (_prevATH is None):
            return _close
        return J.get(G_Math, "max")(_close, _prevATH)
    myAllTimeHigh = G_for_every(G_close, _f1)
    def _f2(_close=J.undefined, _ath=J.undefined, *_args):
        return J.mul(J.div(J.sub(_close, _ath), _ath), 100)
    myDrawdownPercent = G_for_every(G_close, myAllTimeHigh, _f2)
    G_paint(myDrawdownPercent, J.obj(("name", "Drawdown %"), ("color", "#ff3333"), ("style", "stacked_column")))
    G_paint(G_horizontal_line(0), J.obj(("name", "Zero Line"), ("color", "gray"), ("style", "dotted")))


register_store_indicator(
    script,
    name='drawdown_from_ath_TS',
    title='Drawdown from ATH %',
    developer='TrendSpider',
    url='https://trendspider.com/trading-tools-store/indicators/69effd-drawdown-from-ath/',
    position='lower',
    inputs=[],
    outputs=['drawdown__', 'zero_line'],
    signals=[],
    requires=[],
    parity='exact',
)
