"""
Liquidity Map AVWAP -- TrendSpider store indicator by Feliks Ba\u0144ka.

Registered as "liquidity_map_avwap_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68a605-liquidity-map-avwap/)
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
    G_ema = G["ema"]
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_input = G["input"]
    G_low = G["low"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    G_volume = G["volume"]
    def move(s=J.undefined, k=J.undefined, *_args):
        o = G_series_of(None)
        i = 0
        while J.lt(i, J.get(s, "length")):
            j = J.sub(i, k)
            J.set(o, i, (J.get(s, j) if J.ge(j, 0) else None))
            i = J.inc(i)
        return o
    def is_pivot_high(i=J.undefined, L=J.undefined, R=J.undefined, *_args):
        if (J.lt(J.sub(i, L), 0) or J.ge(J.add(i, R), J.get(G_time, "length"))):
            return False
        v = J.get(G_high, i)
        if (J.nullish(v)):
            return False
        k = J.sub(i, L)
        while J.le(k, J.add(i, R)):
            if ((not J.nullish(J.get(G_high, k))) and J.gt(J.get(G_high, k), v)):
                return False
            k = J.inc(k)
        return True
    def is_pivot_low(i=J.undefined, L=J.undefined, R=J.undefined, *_args):
        if (J.lt(J.sub(i, L), 0) or J.ge(J.add(i, R), J.get(G_time, "length"))):
            return False
        v = J.get(G_low, i)
        if (J.nullish(v)):
            return False
        k = J.sub(i, L)
        while J.le(k, J.add(i, R)):
            if ((not J.nullish(J.get(G_low, k))) and J.lt(J.get(G_low, k), v)):
                return False
            k = J.inc(k)
        return True
    def avwap_from_anchor(idx=J.undefined, *_args):
        out = G_series_of(None)
        num = 0
        den = 0
        i = idx
        while J.lt(i, J.get(G_time, "length")):
            if ((not J.nullish(J.get(G_close, i))) and (not J.nullish(J.get(G_volume, i)))):
                num = J.add(num, J.mul(J.get(G_close, i), J.get(G_volume, i)))
                den = J.add(den, J.get(G_volume, i))
                J.set(out, i, J.div(num, den))
            else:
                J.set(out, i, (J.get(out, J.sub(i, 1)) if J.gt(i, idx) else None))
            i = J.inc(i)
        return out
    G_describe_indicator("Liquidity Map AVWAP #TSBuild25", "price", J.obj(("shortName", "LM-AVWAP"), ("decimals", 2)))
    lbL = J.get(G_input, "number")("Pivot Left", 5)
    lbR = J.get(G_input, "number")("Pivot Right", 5)
    nHigh = J.get(G_input, "number")("Last N High Pivots", 2)
    nLow = J.get(G_input, "number")("Last N Low Pivots", 2)
    proxatrr = J.get(G_input, "number")("Proximity (× atrr)", 0.5)
    lenatrr = J.get(G_input, "number")("atrr Len", 14)
    prevClose = move(G_close, 1)
    def _f1(h=J.undefined, l=J.undefined, pc=J.undefined, *_args):
        if (((J.nullish(h)) or (J.nullish(l))) or (J.nullish(pc))):
            return None
        return J.get(G_Math, "max")(J.get(G_Math, "abs")(J.sub(h, l)), J.get(G_Math, "abs")(J.sub(h, pc)), J.get(G_Math, "abs")(J.sub(l, pc)))
    tr = G_for_every(G_high, G_low, prevClose, _f1)
    atrr = G_ema(tr, lenatrr)
    hiIdx = J.JSArray([])
    loIdx = J.JSArray([])
    i = 0
    while J.lt(i, J.get(G_time, "length")):
        if J.truthy(is_pivot_high(i, lbL, lbR)):
            J.get(hiIdx, "push")(i)
        if J.truthy(is_pivot_low(i, lbL, lbR)):
            J.get(loIdx, "push")(i)
        i = J.inc(i)
    hiIdx = J.get(hiIdx, "slice")(J.neg(nHigh))
    loIdx = J.get(loIdx, "slice")(J.neg(nLow))
    proxTouch = G_series_of(False)
    for idx in J.iter_of(J.JSArray([*J.spread(hiIdx), *J.spread(loIdx)])):
        av = avwap_from_anchor(idx)
        G_paint(av, J.obj(("color", "#4DA3FF"), ("style", "line")))
        def _f2(v=J.undefined, a=J.undefined, *_args):
            return (J.add(v, J.mul(a, proxatrr)) if ((not J.nullish(v)) and (not J.nullish(a))) else None)
        up = G_for_every(av, atrr, _f2)
        def _f3(v=J.undefined, a=J.undefined, *_args):
            return (J.sub(v, J.mul(a, proxatrr)) if ((not J.nullish(v)) and (not J.nullish(a))) else None)
        dn = G_for_every(av, atrr, _f3)
        G_paint(up, J.obj(("color", "#999"), ("style", "dotted")))
        G_paint(dn, J.obj(("color", "#999"), ("style", "dotted")))
        def _f4(c=J.undefined, u=J.undefined, l=J.undefined, *_args):
            return ((J.ge(c, l) if J.truthy(_t4 := J.le(c, u)) else _t4) if J.truthy(_t1 := ((not J.nullish(l)) if J.truthy(_t2 := ((not J.nullish(u)) if J.truthy(_t3 := (not J.nullish(c))) else _t3)) else _t2)) else _t1)
        touch = G_for_every(G_close, up, dn, _f4)
        def _f5(a=J.undefined, b=J.undefined, *_args):
            return (_t1 if J.truthy(_t1 := a) else b)
        proxTouch = G_for_every(proxTouch, touch, _f5)
    G_register_signal(proxTouch, "LM: In AVWAP Zone")


register_store_indicator(
    script,
    name='liquidity_map_avwap_TS',
    title='Liquidity Map AVWAP',
    developer='Feliks Ba\\u0144ka',
    url='https://trendspider.com/trading-tools-store/indicators/68a605-liquidity-map-avwap/',
    position='price',
    inputs=[{'id': 'pivot_left', 'title': 'Pivot Left', 'type': 'number', 'default': 5}, {'id': 'pivot_right', 'title': 'Pivot Right', 'type': 'number', 'default': 5}, {'id': 'last_n_high_pivots', 'title': 'Last N High Pivots', 'type': 'number', 'default': 2}, {'id': 'last_n_low_pivots', 'title': 'Last N Low Pivots', 'type': 'number', 'default': 2}, {'id': 'proximity____atrr_', 'title': 'Proximity (× atrr)', 'type': 'number', 'default': 0.5}, {'id': 'atrr_len', 'title': 'atrr Len', 'type': 'number', 'default': 14}],
    outputs=['line_1', 'line_2', 'line_3', 'line_4', 'line_5', 'line_6', 'line_7', 'line_8', 'line_9', 'line_10', 'line_11', 'line_12', 'lm__in_avwap_zone'],
    signals=['lm__in_avwap_zone'],
    requires=[],
    parity='exact',
)
