"""
SPX Circuit Breaker Levels -- TrendSpider store indicator by TrendSpider.

Registered as "spx_circuit_breaker_levels_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/688d1d-spx-circuit-breaker-levels/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_bar_at = G["bar_at"]
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_input = G["input"]
    G_paint = G["paint"]
    G_paint_label_at_line = G["paint_label_at_line"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    def getPreviousDayClose(*_args):
        out = G_series_of(None)
        lastSession = None
        i = 0
        while J.lt(i, J.get(G_close, "length")):
            sess = J.get(G_bar_at(J.get(G_time, i)), "session")
            if J.sne(sess, lastSession):
                J.set(out, i, (J.get(G_close, J.sub(i, 1)) if J.gt(i, 0) else None))
                lastSession = sess
            else:
                J.set(out, i, J.get(out, J.sub(i, 1)))
            i = J.inc(i)
        return out
    G_describe_indicator("SPX Circuit Breaker Levels")
    lvl1Pct = J.get(G_input, "number")("Level 1 CB %", 7, J.obj(("min", 1), ("max", 20)))
    lvl2Pct = J.get(G_input, "number")("Level 2 CB %", 13, J.obj(("min", 1), ("max", 20)))
    lvl3Pct = J.get(G_input, "number")("Level 3 CB %", 20, J.obj(("min", 1), ("max", 20)))
    L1_COLOR = "#32cd32"
    L2_COLOR = "orange"
    L3_COLOR = "red"
    prevClose = getPreviousDayClose()
    def _f1(pc=J.undefined, *_args):
        return (J.mul(pc, J.sub(1, J.div(lvl1Pct, 100))) if J.truthy(pc) else None)
    level1 = G_for_every(prevClose, _f1)
    def _f2(pc=J.undefined, *_args):
        return (J.mul(pc, J.sub(1, J.div(lvl2Pct, 100))) if J.truthy(pc) else None)
    level2 = G_for_every(prevClose, _f2)
    def _f3(pc=J.undefined, *_args):
        return (J.mul(pc, J.sub(1, J.div(lvl3Pct, 100))) if J.truthy(pc) else None)
    level3 = G_for_every(prevClose, _f3)
    l1Line = G_paint(level1, J.obj(("color", L1_COLOR), ("thickness", 2), ("style", "line"), ("name", "CB Level 1")))
    l2Line = G_paint(level2, J.obj(("color", L2_COLOR), ("thickness", 2), ("style", "line"), ("name", "CB Level 2")))
    l3Line = G_paint(level3, J.obj(("color", L3_COLOR), ("thickness", 2), ("style", "line"), ("name", "CB Level 3")))
    lastIdx = J.sub(J.get(G_close, "length"), 1)
    G_paint_label_at_line(l1Line, lastIdx, J.template("Level 1 (", lvl1Pct, "%)"), J.obj(("color", L1_COLOR), ("background_color", "black"), ("vertical_align", "bottom")))
    G_paint_label_at_line(l2Line, lastIdx, J.template("Level 2 (", lvl2Pct, "%)"), J.obj(("color", L2_COLOR), ("background_color", "black"), ("vertical_align", "bottom")))
    G_paint_label_at_line(l3Line, lastIdx, J.template("Level 3 (", lvl3Pct, "%)"), J.obj(("color", L3_COLOR), ("background_color", "black"), ("vertical_align", "bottom")))


register_store_indicator(
    script,
    name='spx_circuit_breaker_levels_TS',
    title='SPX Circuit Breaker Levels',
    developer='TrendSpider',
    url='https://trendspider.com/trading-tools-store/indicators/688d1d-spx-circuit-breaker-levels/',
    position='price',
    inputs=[{'id': 'level_1_cb__', 'title': 'Level 1 CB %', 'type': 'number', 'default': 7}, {'id': 'level_2_cb__', 'title': 'Level 2 CB %', 'type': 'number', 'default': 13}, {'id': 'level_3_cb__', 'title': 'Level 3 CB %', 'type': 'number', 'default': 20}],
    outputs=['cb_level_1', 'cb_level_2', 'cb_level_3'],
    signals=[],
    requires=[],
    parity='exact',
)
