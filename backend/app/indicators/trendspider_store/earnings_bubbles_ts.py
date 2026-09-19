"""
Earnings Bubbles -- TrendSpider store indicator by TrendSpider.

Registered as "earnings_bubbles_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6893ca-earnings-bubbles/)
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
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_input = G["input"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_paint = G["paint"]
    G_request = G["request"]
    G_time = G["time"]
    G_describe_indicator("Earnings Bubbles")
    surpriseType = J.get(G_input, "select")("Surprise Type", "earnings", J.JSArray(["earnings", "revenue"]))
    showLabels = J.get(G_input, "boolean")("Show Labels", True)
    beatColor = J.get(G_input, "color")("Beat Color", "#8ac14b")
    missColor = J.get(G_input, "color")("Miss Color", "#ff0000")
    inlineColor = J.get(G_input, "color")("Inline Color", "grey")
    earnings = J.get(G_request, "earnings")(J.get(G_constants, "ticker"))
    def _f1(record=J.undefined, *_args):
        return J.get(record, "timestamp")
    nmdTime = J.get(earnings, "map")(_f1)
    def _f2(record=J.undefined, *_args):
        return J.get(record, "eps_surprise_percent")
    def _f3(record=J.undefined, *_args):
        return J.get(record, "revenue_surprise_percent")
    surpriseValues = (J.get(earnings, "map")(_f2) if J.seq(surpriseType, "earnings") else J.get(earnings, "map")(_f3))
    surpriseLanded = G_land_points_onto_series(nmdTime, surpriseValues, G_time, "ge")
    def _f4(surprise=J.undefined, c=J.undefined, *_args):
        if (J.nullish(surprise)):
            return None
        size = J.add(10, J.mul(J.get(G_Math, "log10")(J.add(J.get(G_Math, "abs")(surprise), 1)), 20))
        return J.obj(("y", c), ("z", size))
    bubbles = G_for_every(surpriseLanded, G_close, _f4)
    def _f5(surprise=J.undefined, *_args):
        if J.gt(surprise, 0):
            return beatColor
        if J.lt(surprise, 0):
            return missColor
        return inlineColor
    bubblesColors = G_for_every(surpriseLanded, _f5)
    G_paint(bubbles, J.obj(("style", "bubble"), ("color", bubblesColors)))
    def _f6(surprise=J.undefined, *_args):
        if (J.nullish(surprise)):
            return None
        return J.template(("+" if J.gt(surprise, 0) else ""), J.get(surprise, "toFixed")(2), "%")
    labels = G_for_every(surpriseLanded, _f6)
    def _f7(surprise=J.undefined, label=J.undefined, *_args):
        return (label if J.gt(surprise, 0) else None)
    positiveLabels = G_for_every(surpriseLanded, labels, _f7)
    def _f8(surprise=J.undefined, label=J.undefined, *_args):
        return (label if J.lt(surprise, 0) else None)
    negativeLabels = G_for_every(surpriseLanded, labels, _f8)
    def _f9(surprise=J.undefined, label=J.undefined, *_args):
        return (label if J.seq(surprise, 0) else None)
    zeroLabels = G_for_every(surpriseLanded, labels, _f9)
    if J.truthy(showLabels):
        G_paint(positiveLabels, J.obj(("style", "labels_above"), ("color", beatColor), ("name", "Surprise Label")))
        G_paint(negativeLabels, J.obj(("style", "labels_below"), ("color", missColor), ("name", "Miss Label")))
        G_paint(zeroLabels, J.obj(("style", "labels_above"), ("color", inlineColor), ("name", "Inline Label")))


register_store_indicator(
    script,
    name='earnings_bubbles_TS',
    title='Earnings Bubbles',
    developer='TrendSpider',
    url='https://trendspider.com/trading-tools-store/indicators/6893ca-earnings-bubbles/',
    position='price',
    inputs=[{'id': 'surprise_type', 'title': 'Surprise Type', 'type': 'select_wide', 'default': 'earnings', 'options': ['earnings', 'revenue']}, {'id': 'show_labels', 'title': 'Show Labels', 'type': 'boolean', 'default': True}, {'id': 'beat_color', 'title': 'Beat Color', 'type': 'color', 'default': '#8ac14b'}, {'id': 'miss_color', 'title': 'Miss Color', 'type': 'color', 'default': '#ff0000'}, {'id': 'inline_color', 'title': 'Inline Color', 'type': 'color', 'default': 'grey'}],
    outputs=['line_1', 'surprise_label', 'miss_label', 'inline_label'],
    signals=[],
    requires=['earnings'],
    parity='exact',
)
