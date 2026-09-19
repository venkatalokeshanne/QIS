"""
Bearish Doji Candle Identifier -- TrendSpider store indicator by Brandon Hawn.

Registered as "bearish_doji_candle_identifier_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68a295-bearish-doji-candle-identifier/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_atr = G["atr"]
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_input = G["input"]
    G_low = G["low"]
    G_open = G["open"]
    G_paint = G["paint"]
    G_paint_label_at_line = G["paint_label_at_line"]
    G_describe_indicator("Bearish Doji Candle Identifier", "price")
    myDojiTolerance = J.get(G_input, "number")("Doji Tolerance (%)", 5, J.obj(("min", 0), ("max", 20), ("step", 0.1)))
    myMinCandleSize = J.get(G_input, "number")("Min Candle Size (% ATR)", 50, J.obj(("min", 10), ("max", 200), ("step", 5)))
    myAtrLength = 14
    myAtr = G_atr(G_high, G_low, G_close, myAtrLength)
    def isBearishDoji(_open=J.undefined, _high=J.undefined, _low=J.undefined, _close=J.undefined, _atr=J.undefined, _index=J.undefined, *_args):
        myRange = J.sub(_high, _low)
        myBody = J.get(G_Math, "abs")(J.sub(_open, _close))
        myBodyPercentage = J.mul(J.div(myBody, myRange), 100)
        myCandleSizePercentage = J.mul(J.div(myRange, _atr), 100)
        return (J.lt(_low, J.get(G_Math, "min")(_open, _close)) if J.truthy(_t1 := (J.gt(_high, J.get(G_Math, "max")(_open, _close)) if J.truthy(_t2 := (J.ge(myCandleSizePercentage, myMinCandleSize) if J.truthy(_t3 := (J.le(myBodyPercentage, myDojiTolerance) if J.truthy(_t4 := J.lt(_close, _open)) else _t4)) else _t3)) else _t2)) else _t1)
    def _f1(_o=J.undefined, _h=J.undefined, _l=J.undefined, _c=J.undefined, _atr=J.undefined, _i=J.undefined, *_args):
        return (_l if J.truthy(isBearishDoji(_o, _h, _l, _c, _atr, _i)) else None)
    myBearishDoji = G_for_every(G_open, G_high, G_low, G_close, myAtr, _f1)
    G_paint(myBearishDoji, J.obj(("name", "Bearish Doji"), ("color", "red"), ("style", "labels_below"), ("text", "▼")))
    lineRef = G_paint(myBearishDoji)
    i = 0
    while J.lt(i, J.get(myBearishDoji, "length")):
        if (J.get(myBearishDoji, i) is not None):
            G_paint_label_at_line(lineRef, i, "Bearish Doji", J.obj(("color", "white"), ("background_color", "red"), ("border_color", "darkred"), ("vertical_align", "bottom")))
        i = J.inc(i)


register_store_indicator(
    script,
    name='bearish_doji_candle_identifier_TS',
    title='Bearish Doji Candle Identifier',
    developer='Brandon Hawn',
    url='https://trendspider.com/trading-tools-store/indicators/68a295-bearish-doji-candle-identifier/',
    position='price',
    inputs=[{'id': 'doji_tolerance____', 'title': 'Doji Tolerance (%)', 'type': 'number', 'default': 5}, {'id': 'min_candle_size____atr_', 'title': 'Min Candle Size (% ATR)', 'type': 'number', 'default': 50}],
    outputs=['bearish_doji', 'line_2'],
    signals=[],
    requires=[],
    parity='exact',
)
