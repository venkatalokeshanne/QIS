"""
NVDA Earnings + EMO (CSV) -- TrendSpider store indicator by Christian Park.

Registered as "nvda_earnings_emo_csv_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68abc0-nvda-earnings-emo-csv/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_E = G["E"]
    G_M = G["M"]
    G_Math = G["Math"]
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_draw = G["draw"]
    G_ema = G["ema"]
    G_emoLine = G["emoLine"]
    G_emoStep = G["emoStep"]
    G_ev = G["ev"]
    G_for_every = G["for_every"]
    G_g40 = G["g40"]
    G_g50 = G["g50"]
    G_g60 = G["g60"]
    G_input = G["input"]
    G_isNaN = G["isNaN"]
    G_osc = G["osc"]
    G_parseFloat = G["parseFloat"]
    G_plot = G["plot"]
    G_series_of = G["series_of"]
    G_t = G["t"]
    G_topSide = G["topSide"]
    i = J.undefined
    impulse = J.undefined
    lastVal = J.undefined
    j = J.undefined
    def isISO(d=J.undefined, *_args):
        return (J.seq(J.get(d, 7), "-") if J.truthy(_t1 := (J.seq(J.get(d, 4), "-") if J.truthy(_t2 := (J.seq(J.get(d, "length"), 10) if J.truthy(_t3 := d) else _t3)) else _t2)) else _t1)
    def splitCSVRow(s=J.undefined, *_args):
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
                elif J.seq(ch, ","):
                    J.get(o, "push")(c)
                    c = ""
                else:
                    c = J.add(c, ch)
            i_2 = J.inc(i_2)
        J.get(o, "push")(c)
        return o
    def toFixedPct(x=J.undefined, *_args):
        n = J.undefined
        r = J.undefined
        n = G_parseFloat(x)
        if J.truthy(G_isNaN(n)):
            return ""
        r = J.div(J.get(G_Math, "round")(J.mul(n, 100)), 100)
        return J.add(J.get(r, "toFixed")(2), "%")
    def parseE(csv=J.undefined, *_args):
        out = J.undefined
        rows = J.undefined
        start = J.undefined
        hdr = J.undefined
        i_2 = J.undefined
        r = J.undefined
        p = J.undefined
        d = J.undefined
        typ = J.undefined
        eps = J.undefined
        L = J.undefined
        out = J.JSArray([])
        rows = J.get(csv, "split")("n")
        if J.lt(J.get(rows, "length"), 2):
            return out
        start = 0
        hdr = J.get(J.get((_t1 if J.truthy(_t1 := J.get(rows, 0)) else ""), "trim")(), "toLowerCase")()
        if J.sne(J.get(hdr, "indexOf")("date"), (-1)):
            start = 1
        i_2 = start
        while J.lt(i_2, J.get(rows, "length")):
            r = J.get((_t2 if J.truthy(_t2 := J.get(rows, i_2)) else ""), "trim")()
            if ((not J.truthy(r)) or J.seq(r, "...")):
                i_2 = J.inc(i_2)
                continue
            p = splitCSVRow(r)
            d = J.get((_t3 if J.truthy(_t3 := J.get(p, 0)) else ""), "trim")()
            if ((not J.truthy(isISO(d))) or J.lt(d, MIN_DATE)):
                i_2 = J.inc(i_2)
                continue
            typ = J.get((_t4 if J.truthy(_t4 := J.get(p, 1)) else ""), "trim")()
            eps = J.get((_t5 if J.truthy(_t5 := J.get(p, 2)) else ""), "trim")()
            L = J.get((_t6 if J.truthy(_t6 := J.get(p, 3)) else ""), "trim")()
            if (not J.truthy(L)):
                L = (_t7 if J.truthy(_t7 := typ) else "E")
            J.get(out, "push")(J.obj(("d", d), ("eps", eps), ("label", L)))
            i_2 = J.inc(i_2)
        def _f8(a=J.undefined, b=J.undefined, *_args):
            return (1 if J.lt(J.get(a, "d"), J.get(b, "d")) else ((-1) if J.gt(J.get(a, "d"), J.get(b, "d")) else 0))
        J.get(out, "sort")(_f8)
        if J.gt(J.get(out, "length"), TopK):
            out = J.get(out, "slice")(0, TopK)
        return out
    def parseEMO(csv=J.undefined, *_args):
        out = J.undefined
        rows = J.undefined
        start = J.undefined
        hdr = J.undefined
        i_2 = J.undefined
        r = J.undefined
        p = J.undefined
        d = J.undefined
        emo = J.undefined
        sig = J.undefined
        L = J.undefined
        out = J.JSArray([])
        rows = J.get(csv, "split")("n")
        if J.lt(J.get(rows, "length"), 2):
            return out
        start = 0
        hdr = J.get(J.get((_t1 if J.truthy(_t1 := J.get(rows, 0)) else ""), "trim")(), "toLowerCase")()
        if J.sne(J.get(hdr, "indexOf")("date"), (-1)):
            start = 1
        i_2 = start
        while J.lt(i_2, J.get(rows, "length")):
            r = J.get((_t2 if J.truthy(_t2 := J.get(rows, i_2)) else ""), "trim")()
            if ((not J.truthy(r)) or J.seq(r, "...")):
                i_2 = J.inc(i_2)
                continue
            p = splitCSVRow(r)
            d = J.get((_t3 if J.truthy(_t3 := J.get(p, 0)) else ""), "trim")()
            if ((not J.truthy(isISO(d))) or J.lt(d, MIN_DATE)):
                i_2 = J.inc(i_2)
                continue
            emo = G_parseFloat(J.get((_t4 if J.truthy(_t4 := J.get(p, 1)) else ""), "trim")())
            sig = J.get((_t5 if J.truthy(_t5 := J.get(p, 2)) else ""), "trim")()
            L = J.get((_t6 if J.truthy(_t6 := J.get(p, 3)) else ""), "trim")()
            if J.truthy(G_isNaN(emo)):
                i_2 = J.inc(i_2)
                continue
            J.get(out, "push")(J.obj(("d", d), ("emo", emo), ("sig", sig), ("label", L)))
            i_2 = J.inc(i_2)
        def _f7(a=J.undefined, b=J.undefined, *_args):
            return (1 if J.gt(J.get(a, "d"), J.get(b, "d")) else ((-1) if J.lt(J.get(a, "d"), J.get(b, "d")) else 0))
        J.get(out, "sort")(_f7)
        return out
    G_describe_indicator("NVDA Earnings + EMO (CSV) — #TSBuild25")
    CSV_EARNINGS = J.get(J.template("\n\ndate,type,eps,label\n\n2025-04-27,Earnings,0.76,Q1 2026: $0.76\n\n2025-01-26,Earnings,,Q4 2025\n\n2024-07-28,Earnings,0.67,Q2 2025: $0.67\n\n2024-04-28,Earnings,5.98,Q1 2025: $5.98\n\n2024-01-28,Earnings,4.92,Q4 2024: $4.92\n\n2023-10-29,Earnings,3.71,Q3 2024: $3.71\n\n2023-07-30,Earnings,2.48,Q2 2024: $2.48\n\n2023-04-30,Earnings,0.82,Q1 2024: $0.82\n\n2023-01-29,Earnings,0.5700000000000001,Q4 2023: $0.57\n\n2022-10-30,Earnings,0.27,Q3 2023: $0.27\n\n2022-07-31,Earnings,0.26,Q2 2023: $0.26\n\n2022-05-01,Earnings,0.64,Q1 2023: $0.64\n\n2022-01-30,Earnings,1.1800000000000002,Q4 2022: $1.18\n\n2021-10-31,Earnings,0.97,Q3 2022: $0.97\n\n2021-08-01,Earnings,0.94,Q2 2022: $0.94\n\n...\n\n2013-07-28,Earnings,0.16,Q2 2014: $0.16\n\n2013-04-28,Earnings,0.13,Q1 2014: $0.13\n\n2013-01-27,Earnings,0.28,Q4 2013: $0.28\n\n2012-10-28,Earnings,0.33,Q3 2013: $0.33\n\n2012-07-29,Earnings,0.19,Q2 2013: $0.19\n\n2012-04-29,Earnings,0.1,Q1 2013: $0.10\n\n2012-01-29,Earnings,0.19,Q4 2012: $0.19\n\n2011-10-30,Earnings,0.29,Q3 2012: $0.29\n\n2011-07-31,Earnings,0.25,Q2 2012: $0.25\n\n2011-05-01,Earnings,0.22,Q1 2012: $0.22\n\n2011-01-30,Earnings,0.29,Q4 2011: $0.29\n\n2010-10-29,Earnings,0.15,Q3 2011: $0.15\n\n2010-07-29,Earnings,-0.25,Q2 2011: $-0.25\n\n2010-04-29,Earnings,0.23,Q1 2011: $0.23\n\n"), "trim")()
    CSV_EMO = J.get(J.template("\n\ndate,emo,signal,label,qoq_growth,yoy_growth,acceleration,consistency,eps\n\n2025-04-27,30.45,BULLISH,EMO: 30.4 (BULLISH),13.43,0,102.23,10.2,0.76\n\n2024-07-28,-69.34,BEARISH,EMO: -69.3 (BEARISH),-88.8,-72.98,-110.34,39.9,0.67\n\n2024-04-28,100,BULLISH,EMO: 100 (BULLISH),21.54,629.27,-11.07,64.6,5.98\n\n2024-01-28,100,BULLISH,EMO: 100 (BULLISH),32.61,763.16,-16.98,41.25,4.92\n\n2023-10-29,100,BULLISH,EMO: 100 (BULLISH),49.6,1274.07,-152.84,22.04,3.71\n\n2023-07-30,100,BULLISH,EMO: 100 (BULLISH),202.44,853.85,158.58,4.42,2.48\n\n2023-04-30,10.61,NEUTRAL,EMO: 10.6 (NEUTRAL),43.86,28.12,-67.25,44.07,0.82\n\n2023-01-29,44.66,BULLISH,EMO: 44.7 (BULLISH),111.11,-51.69,107.26,54.39,0.5700000000000001\n\n2022-10-30,-4.54,NEUTRAL,EMO: -4.5 (NEUTRAL),3.85,-72.16,63.22,26.34,0.27\n\n2022-07-31,-36.47,BEARISH,EMO: -36.5 (BEARISH),-59.38,-72.34,-13.61,47.28,0.26\n\n2022-05-01,-44.48,BEARISH,EMO: -44.5 (BEARISH),-45.76,-78.88,-67.41,76.16,0.64\n\n2022-01-30,-1.95,NEUTRAL,EMO: -2.0 (NEUTRAL),21.65,-48.92,18.46,34.27,1.1800000000000002\n\n2021-10-31,6.31,NEUTRAL,EMO: 6.3 (NEUTRAL),3.19,-54.25,72.17,43.01,0.97\n\n2021-08-01,-35.24,BEARISH,EMO: -35.2 (BEARISH),-68.98,-5.05,-100.15,58.71,0.94\n\n2021-05-02,59.49,BULLISH,EMO: 59.5 (BULLISH),31.17,106.12,22.21,60.01,3.03\n\n"), "trim")()
    TopK = J.get(G_input, "number")("Most recent K earnings", 7, J.obj(("min", 1), ("max", 20)))
    LabelTop = J.get(G_input, "number")("Labels: 1 top / 0 alt", 1, J.obj(("min", 0), ("max", 1)))
    ViewSm = J.get(G_input, "number")("EMO display smoothing", 5, J.obj(("min", 0), ("max", 30)))
    MIN_DATE = "2022-01-01"
    EPS = 1.0e-9
    G_E = parseE(CSV_EARNINGS)
    G_M = parseEMO(CSV_EMO)
    def _f1(_c=J.undefined, *_args):
        return 0
    impulse = G_for_every(G_close, _f1)
    i = 0
    while J.lt(i, J.get(G_M, "length")):
        def _f2(v=J.undefined, *_args):
            nonlocal impulse
            sig = J.undefined
            sig = G_series_of(J.get(v, "d"))
            def _f1(acc=J.undefined, s=J.undefined, *_args):
                return J.add(acc, (J.get(v, "emo") if J.truthy(s) else 0))
            impulse = G_for_every(impulse, sig, _f1)
        _f2(J.get(G_M, i))
        i = J.inc(i)
    lastVal = None
    def _f3(x=J.undefined, *_args):
        nonlocal lastVal
        if (J.truthy(x) and J.sne(x, 0)):
            lastVal = x
        return (0 if (lastVal is None) else lastVal)
    G_emoStep = G_for_every(impulse, _f3)
    G_emoLine = (G_ema(G_emoStep, ViewSm) if J.gt(ViewSm, 0) else G_emoStep)
    def _f4(v=J.undefined, *_args):
        x = J.undefined
        x = v
        if J.gt(x, 100):
            x = 100
        if J.lt(x, (-100)):
            x = (-100)
        return J.mul(J.add(x, 100), 0.5)
    G_osc = G_for_every(G_emoLine, _f4)
    def _f5(*_args):
        return 50
    G_g50 = G_for_every(G_close, _f5)
    def _f6(*_args):
        return 60
    G_g60 = G_for_every(G_close, _f6)
    def _f7(*_args):
        return 40
    G_g40 = G_for_every(G_close, _f7)
    G_plot(G_g50, J.obj(("name", "__emo50"), ("color", "#666")))
    G_plot(G_g60, J.obj(("name", "__emo60"), ("color", "#3f63cc")))
    G_plot(G_g40, J.obj(("name", "__emo40"), ("color", "#b94b4b")))
    G_plot(G_osc, J.obj(("name", "EMO"), ("color", "#dddddd")))
    j = 0
    while J.lt(j, J.get(G_E, "length")):
        G_ev = J.get(G_E, j)
        try:
            if (J.truthy(G_draw) and J.truthy(J.get(G_draw, "vline"))):
                J.get(G_draw, "vline")(J.get(G_ev, "d"), J.obj(("color", "#909090"), ("width", 1), ("style", "dashed")))
        except Exception as _e8:
            __ = J.catch_value(_e8)
            pass
        try:
            if (J.truthy(G_draw) and J.truthy(J.get(G_draw, "label"))):
                G_t = (J.add("EPS ", J.get(G_ev, "eps")) if J.truthy(J.get(G_ev, "eps")) else J.get(G_ev, "label"))
                G_topSide = (True if J.seq(LabelTop, 1) else J.seq(J.mod(j, 2), 0))
                J.get(G_draw, "label")(J.get(G_ev, "d"), G_close, G_t, J.obj(("color", "#cfcfcf"), ("valign", ("top" if J.truthy(G_topSide) else "bottom"))))
        except Exception as _e9:
            ___2 = J.catch_value(_e9)
            pass
        j = J.inc(j)


register_store_indicator(
    script,
    name='nvda_earnings_emo_csv_TS',
    title='NVDA Earnings + EMO (CSV)',
    developer='Christian Park',
    url='https://trendspider.com/trading-tools-store/indicators/68abc0-nvda-earnings-emo-csv/',
    position='price',
    inputs=[{'id': 'most_recent_k_earnings', 'title': 'Most recent K earnings', 'type': 'number', 'default': 7}, {'id': 'labels__1_top___0_alt', 'title': 'Labels: 1 top / 0 alt', 'type': 'number', 'default': 1}, {'id': 'emo_display_smoothing', 'title': 'EMO display smoothing', 'type': 'number', 'default': 5}],
    outputs=['__emo50', '__emo60', '__emo40', 'emo'],
    signals=[],
    requires=[],
    parity='exact',
)
