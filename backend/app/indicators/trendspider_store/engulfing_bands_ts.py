"""
Engulfing Bands -- TrendSpider store indicator by TrendSpider Team.

Registered as "engulfing_bands_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/engulfing-bands/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_close = G["close"]
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_fill = G["fill"]
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_horizontal_line = G["horizontal_line"]
    G_low = G["low"]
    G_max_of = G["max_of"]
    G_min_of = G["min_of"]
    G_open = G["open"]
    G_paint = G["paint"]
    G_shift = G["shift"]
    G_describe_indicator("Engulfing Levels")
    bodyTop = G_max_of(G_open, G_close)
    bodyBottom = G_min_of(G_open, G_close)
    def _f1(bt=J.undefined, pbt=J.undefined, bb=J.undefined, pbb=J.undefined, *_args):
        return (J.lt(bb, pbb) if J.truthy(_t1 := J.gt(bt, pbt)) else _t1)
    bodyEngulfings = G_for_every(bodyTop, G_shift(bodyTop, 1), bodyBottom, G_shift(bodyBottom, 1), _f1)
    numberOfRemainingAreas = 5
    candleIndex = J.sub(J.get(bodyEngulfings, "length"), 1)
    while J.gt(candleIndex, 0):
        if (J.truthy(J.get(bodyEngulfings, candleIndex)) and J.gt(numberOfRemainingAreas, 0)):
            fillColor = ("rgba(0, 255, 0, 0.2)" if J.ge(J.get(G_close, candleIndex), J.get(G_open, candleIndex)) else "rgba(255, 0, 0, 0.2)")
            G_fill(G_paint(G_horizontal_line(J.get(G_high, candleIndex), candleIndex), J.obj(("name", J.template("Top line ", numberOfRemainingAreas)), ("color", "blue"))), G_paint(G_horizontal_line(J.get(G_low, candleIndex), candleIndex), J.obj(("name", J.template("Bottom line ", numberOfRemainingAreas)), ("color", "blue"))), fillColor)
            numberOfRemainingAreas = J.dec(numberOfRemainingAreas)
        candleIndex = J.dec(candleIndex)
    while J.gt(numberOfRemainingAreas, 0):
        G_fill(G_paint(J.get(G_constants, "empty_series"), J.obj(("name", J.template("Top line ", numberOfRemainingAreas)), ("color", "blue"))), G_paint(J.get(G_constants, "empty_series"), J.obj(("name", J.template("Bottom line ", numberOfRemainingAreas)), ("color", "blue"))), "rgba(0, 0, 0, 0)")
        numberOfRemainingAreas = J.dec(numberOfRemainingAreas)


register_store_indicator(
    script,
    name='engulfing_bands_TS',
    title='Engulfing Bands',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/engulfing-bands/',
    position='price',
    inputs=[],
    outputs=['top_line_5', 'bottom_line_5', 'top_line_4', 'bottom_line_4', 'top_line_3', 'bottom_line_3', 'top_line_2', 'bottom_line_2', 'top_line_1', 'bottom_line_1'],
    signals=[],
    requires=[],
    parity='exact',
)
