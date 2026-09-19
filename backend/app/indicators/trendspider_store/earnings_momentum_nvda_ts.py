"""
Earnings + Momentum (NVDA) -- TrendSpider store indicator by Christian Park.

Registered as "earnings_momentum_nvda_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68abb1-earnings-momentum-nvda-tsbuild25/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_EV = G["EV"]
    G_Math = G["Math"]
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_draw = G["draw"]
    G_e = G["e"]
    G_ema = G["ema"]
    G_for_every = G["for_every"]
    G_input = G["input"]
    G_isNaN = G["isNaN"]
    G_lbl = G["lbl"]
    G_parseFloat = G["parseFloat"]
    G_plot = G["plot"]
    G_vwap = G["vwap"]
    i = J.undefined
    def splitCSV(s=J.undefined, *_args):
        o = J.undefined
        c = J.undefined
        q = J.undefined
        i_2 = J.undefined
        ch = J.undefined
        o = J.JSArray([])
        c = ""
        q = False
        i_2 = 0
        while J.lt(i_2, J.get(s, "length")):
            ch = J.get(s, i_2)
            if J.truthy(q):
                if J.eq(ch, "\""):
                    if (J.lt(J.add(i_2, 1), J.get(s, "length")) and J.eq(J.get(s, J.add(i_2, 1)), "\"")):
                        c = J.add(c, "\"")
                        i_2 = J.inc(i_2)
                    else:
                        q = False
                else:
                    c = J.add(c, ch)
            else:
                if J.eq(ch, "\""):
                    q = True
                elif J.eq(ch, ","):
                    J.get(o, "push")(c)
                    c = ""
                else:
                    c = J.add(c, ch)
            i_2 = J.inc(i_2)
        J.get(o, "push")(c)
        return o
    def iso(d=J.undefined, *_args):
        return (J.seq(J.get(d, 7), "-") if J.truthy(_t1 := (J.seq(J.get(d, 4), "-") if J.truthy(_t2 := (J.seq(J.get(d, "length"), 10) if J.truthy(_t3 := d) else _t3)) else _t2)) else _t1)
    def pct(x=J.undefined, *_args):
        n = J.undefined
        n = G_parseFloat(x)
        return ("" if J.truthy(G_isNaN(n)) else J.add(J.get(J.div(J.get(G_Math, "round")(J.mul(n, 100)), 100), "toFixed")(2), "%"))
    def arrow(v=J.undefined, *_args):
        n = J.undefined
        n = G_parseFloat(v)
        if (J.truthy(G_isNaN(n)) or J.seq(n, 0)):
            return "•"
        return ("▲" if J.gt(n, 0) else "▼")
    def col(v=J.undefined, *_args):
        n = J.undefined
        n = G_parseFloat(v)
        return ("#cfcfcf" if J.truthy(G_isNaN(n)) else ("#4cc38a" if J.ge(n, 0) else "#e25555"))
    def abs_s(x=J.undefined, *_args):
        def _f1(v=J.undefined, *_args):
            return (J.neg(v) if J.lt(v, 0) else v)
        return G_for_every(x, _f1)
    def clip_s(x=J.undefined, c=J.undefined, *_args):
        def _f1(v=J.undefined, *_args):
            return (c if J.gt(v, c) else (J.neg(c) if J.lt(v, J.neg(c)) else v))
        return G_for_every(x, _f1)
    def norm_z(x=J.undefined, len=J.undefined, *_args):
        d = G_ema(abs_s(x), len)
        def _f1(a=J.undefined, den=J.undefined, *_args):
            return J.div(a, (den if (J.truthy(den) and J.sne(den, 0)) else EPS))
        return G_for_every(x, d, _f1)
    def delta(s=J.undefined, *_args):
        p = None
        def _f1(v=J.undefined, *_args):
            nonlocal p
            d = J.undefined
            d = (0 if (p is None) else J.sub(v, p))
            p = v
            return d
        return G_for_every(s, _f1)
    def rocN(s=J.undefined, n=J.undefined, *_args):
        b = J.JSArray([])
        def _f1(v=J.undefined, *_args):
            if J.lt(J.get(b, "length"), n):
                J.get(b, "push")(v)
                return 0
            base = (_t1 if J.truthy(_t1 := J.get(b, 0)) else v)
            J.get(b, "push")(v)
            J.get(b, "shift")()
            return J.div(J.sub(v, base), (base if J.sne(base, 0) else EPS))
        return G_for_every(s, _f1)
    def eventsFromCSV(csv=J.undefined, *_args):
        out = J.undefined
        r = J.undefined
        st = J.undefined
        h = J.undefined
        i_2 = J.undefined
        rowStr = J.undefined
        p = J.undefined
        d = J.undefined
        g = J.undefined
        f = J.undefined
        L = J.undefined
        score = J.undefined
        out = J.JSArray([])
        r = J.get(csv, "split")("n")
        if J.lt(J.get(r, "length"), 2):
            return out
        st = 0
        h = J.get(J.get((_t1 if J.truthy(_t1 := J.get(r, 0)) else ""), "trim")(), "toLowerCase")()
        if J.sne(J.get(h, "indexOf")("date"), (-1)):
            st = 1
        i_2 = st
        while J.lt(i_2, J.get(r, "length")):
            rowStr = J.get((_t2 if J.truthy(_t2 := J.get(r, i_2)) else ""), "trim")()
            if ((not J.truthy(rowStr)) or J.seq(rowStr, "...")):
                i_2 = J.inc(i_2)
                continue
            p = splitCSV(rowStr)
            d = J.get((_t3 if J.truthy(_t3 := J.get(p, 0)) else ""), "trim")()
            if (not J.truthy(iso(d))):
                i_2 = J.inc(i_2)
                continue
            g = J.get((_t4 if J.truthy(_t4 := J.get(p, 1)) else ""), "trim")()
            f = J.get((_t5 if J.truthy(_t5 := J.get(p, 2)) else ""), "trim")()
            L = J.get((_t6 if J.truthy(_t6 := J.get(p, 3)) else ""), "trim")()
            if (not J.truthy(L)):
                L = "E"
            score = J.add(J.mul(0.7, J.get(G_Math, "abs")((_t7 if J.truthy(_t7 := G_parseFloat(g)) else 0))), J.mul(0.3, J.get(G_Math, "abs")((_t8 if J.truthy(_t8 := G_parseFloat(f)) else 0))))
            J.get(out, "push")(J.obj(("d", d), ("g", g), ("f", f), ("l", L), ("s", score)))
            i_2 = J.inc(i_2)
        def _f9(a=J.undefined, b=J.undefined, *_args):
            return J.sub(J.get(b, "s"), J.get(a, "s"))
        J.get(out, "sort")(_f9)
        if J.gt(J.get(out, "length"), TopK):
            out = J.get(out, "slice")(0, TopK)
        def _f10(a=J.undefined, b=J.undefined, *_args):
            return (1 if J.lt(J.get(a, "d"), J.get(b, "d")) else ((-1) if J.gt(J.get(a, "d"), J.get(b, "d")) else 0))
        J.get(out, "sort")(_f10)
        return out
    def mark(d=J.undefined, txt=J.undefined, c=J.undefined, top=J.undefined, *_args):
        ok = J.undefined
        ok = False
        try:
            if (J.truthy(G_draw) and J.truthy(J.get(G_draw, "vline"))):
                J.get(G_draw, "vline")(d, J.obj(("color", c), ("width", 1), ("style", "dashed")))
                ok = True
        except Exception as _e1:
            e = J.catch_value(_e1)
            pass
        try:
            if (J.truthy(G_draw) and J.truthy(J.get(G_draw, "label"))):
                J.get(G_draw, "label")(d, G_close, txt, J.obj(("color", c), ("valign", ("top" if J.truthy(top) else "bottom"))))
                ok = True
        except Exception as _e2:
            e_2 = J.catch_value(_e2)
            pass
        return ok
    G_describe_indicator("Earnings + Momentum (NVDA) — #TSBuild25")
    CSV_DATA = J.get(J.template("\n\ndate,gap_pct,drift5_pct,label\n\n2025-04-27,6.4,9.1,E 0.76\n\n2025-01-26,-2.7,1.2,E\n\n2024-07-28,4.2,7.6,E 0.67\n\n2024-04-28,8.9,15.3,E 5.98\n\n2024-01-28,7.1,10.4,E 4.92\n\n"), "trim")()
    TopK = J.get(G_input, "number")("Top K markers", 5, J.obj(("min", 1), ("max", 12)))
    RocLen = J.get(G_input, "number")("ROC len", 10, J.obj(("min", 2), ("max", 200)))
    EmaLen = J.get(G_input, "number")("EMA len", 20, J.obj(("min", 5), ("max", 200)))
    PressLen = J.get(G_input, "number")("Press len", 10, J.obj(("min", 2), ("max", 200)))
    NormLen = J.get(G_input, "number")("Norm len", 50, J.obj(("min", 5), ("max", 300)))
    CalcSm = J.get(G_input, "number")("Calc smooth", 3, J.obj(("min", 0), ("max", 20)))
    ViewSm = J.get(G_input, "number")("View smooth", 8, J.obj(("min", 0), ("max", 30)))
    Cap = J.get(G_input, "number")("Clip |Z|", 3, J.obj(("min", 1), ("max", 10)))
    Wroc = J.get(G_input, "number")("W ROC", 1, J.obj(("min", 0), ("max", 3), ("step", 0.1)))
    Wslope = J.get(G_input, "number")("W Slope", 1, J.obj(("min", 0), ("max", 3), ("step", 0.1)))
    Wpress = J.get(G_input, "number")("W Press", 1, J.obj(("min", 0), ("max", 3), ("step", 0.1)))
    EPS = 1.0e-9
    G_EV = eventsFromCSV(CSV_DATA)
    zRoc = norm_z(rocN(G_close, RocLen), NormLen)
    emaC = G_ema(G_close, EmaLen)
    def _f1(d=J.undefined, c=J.undefined, *_args):
        return J.div(d, (c if (J.truthy(c) and J.sne(c, 0)) else EPS))
    zSlope = norm_z(G_for_every(delta(emaC), G_close, _f1), NormLen)
    vw = G_vwap()
    def _f2(c=J.undefined, v=J.undefined, *_args):
        return J.div(J.sub(c, (_t1 if J.truthy(_t1 := v) else 1)), (_t2 if J.truthy(_t2 := v) else 1))
    zPress = norm_z(G_ema(G_for_every(G_close, vw, _f2), PressLen), NormLen)
    def _f3(r=J.undefined, s=J.undefined, p=J.undefined, *_args):
        return J.add(J.add(J.mul(Wroc, r), J.mul(Wslope, s)), J.mul(Wpress, p))
    zRaw = G_for_every(zRoc, zSlope, zPress, _f3)
    zClip = clip_s((G_ema(zRaw, CalcSm) if J.gt(CalcSm, 0) else zRaw), Cap)
    def _f4(v=J.undefined, *_args):
        x = J.undefined
        x = J.div(v, Cap)
        if J.gt(x, 1):
            x = 1
        if J.lt(x, (-1)):
            x = (-1)
        return J.mul(J.add(x, 1), 50)
    osc = G_for_every(zClip, _f4)
    oscLine = (G_ema(osc, ViewSm) if J.gt(ViewSm, 0) else osc)
    def _f5(__=J.undefined, *_args):
        return 50
    def _f6(__=J.undefined, *_args):
        return 60
    def _f7(__=J.undefined, *_args):
        return 40
    g50 = G_for_every(G_close, _f5)
    g60 = G_for_every(G_close, _f6)
    g40 = G_for_every(G_close, _f7)
    G_plot(g50, J.obj(("name", "EM_base50"), ("color", "#666")))
    G_plot(g60, J.obj(("name", "EM_upper"), ("color", "#3f63cc")))
    G_plot(g40, J.obj(("name", "EM_lower"), ("color", "#b94b4b")))
    G_plot(oscLine, J.obj(("name", "EM"), ("color", "#dddddd")))
    i = 0
    while J.lt(i, J.get(G_EV, "length")):
        G_e = J.get(G_EV, i)
        G_lbl = J.add(J.add(J.add(J.add(arrow(J.get(G_e, "g")), " "), pct(J.get(G_e, "g"))), "/"), pct(J.get(G_e, "f")))
        mark(J.get(G_e, "d"), G_lbl, col(J.get(G_e, "g")), J.seq(J.mod(i, 2), 0))
        i = J.inc(i)


register_store_indicator(
    script,
    name='earnings_momentum_nvda_TS',
    title='Earnings + Momentum (NVDA)',
    developer='Christian Park',
    url='https://trendspider.com/trading-tools-store/indicators/68abb1-earnings-momentum-nvda-tsbuild25/',
    position='price',
    inputs=[{'id': 'top_k_markers', 'title': 'Top K markers', 'type': 'number', 'default': 5}, {'id': 'roc_len', 'title': 'ROC len', 'type': 'number', 'default': 10}, {'id': 'ema_len', 'title': 'EMA len', 'type': 'number', 'default': 20}, {'id': 'press_len', 'title': 'Press len', 'type': 'number', 'default': 10}, {'id': 'norm_len', 'title': 'Norm len', 'type': 'number', 'default': 50}, {'id': 'calc_smooth', 'title': 'Calc smooth', 'type': 'number', 'default': 3}, {'id': 'view_smooth', 'title': 'View smooth', 'type': 'number', 'default': 8}, {'id': 'clip__z_', 'title': 'Clip |Z|', 'type': 'number', 'default': 3}, {'id': 'w_roc', 'title': 'W ROC', 'type': 'number', 'default': 1}, {'id': 'w_slope', 'title': 'W Slope', 'type': 'number', 'default': 1}, {'id': 'w_press', 'title': 'W Press', 'type': 'number', 'default': 1}],
    outputs=['em_base50', 'em_upper', 'em_lower', 'em'],
    signals=[],
    requires=[],
    parity='exact',
)
