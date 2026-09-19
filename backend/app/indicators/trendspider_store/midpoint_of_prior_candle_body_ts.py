"""
MidPoint of Prior Candle Body -- TrendSpider store indicator by TrendSpider Team.

Registered as "midpoint_of_prior_candle_body_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/midpoint-of-prior-candle-body/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_input = G["input"]
    G_open = G["open"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_describe_indicator("Midpoint of Prior Candle", "price")
    myPeriodOffset = J.get(G_input, "number")("Period Offset", 1, J.obj(("min", 1)))
    def _f1(o=J.undefined, c=J.undefined, prev=J.undefined, i=J.undefined, *_args):
        if J.lt(i, myPeriodOffset):
            return None
        priorOpen = J.get(G_open, J.sub(i, myPeriodOffset))
        priorClose = J.get(G_close, J.sub(i, myPeriodOffset))
        return J.div(J.add(priorOpen, priorClose), 2)
    myMidpoint = G_for_every(G_open, G_close, _f1)
    G_paint(myMidpoint, J.obj(("name", "Prior Midpoint"), ("color", "white"), ("style", "line")))
    G_register_signal(myMidpoint, "Prior Candle Midpoint")


register_store_indicator(
    script,
    name='midpoint_of_prior_candle_body_TS',
    title='MidPoint of Prior Candle Body',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/midpoint-of-prior-candle-body/',
    position='price',
    inputs=[{'id': 'period_offset', 'title': 'Period Offset', 'type': 'number', 'default': 1}],
    outputs=['prior_midpoint', 'prior_candle_midpoint'],
    signals=['prior_candle_midpoint'],
    requires=[],
    parity='exact',
)
