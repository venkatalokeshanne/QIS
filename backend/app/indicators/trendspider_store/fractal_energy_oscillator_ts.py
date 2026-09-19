"""
Fractal Energy Oscillator -- TrendSpider store indicator by Feliks Ba\u0144ka.

Registered as "fractal_energy_oscillator_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68a606-fractal-energy-oscillator/)
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
    G_input = G["input"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_series_of = G["series_of"]
    G_sliding_window_function = G["sliding_window_function"]
    G_sma = G["sma"]
    def move(s=J.undefined, k=J.undefined, *_args):
        out = G_series_of(None)
        i = 0
        while J.lt(i, J.get(s, "length")):
            j = J.sub(i, k)
            J.set(out, i, (J.get(s, j) if J.ge(j, 0) else None))
            i = J.inc(i)
        return out
    G_describe_indicator("Fractal Energy Oscillator #TSBuild25", "lower", J.obj(("shortName", "FE"), ("decimals", 2)))
    grpCore = "① Core"
    grpDisp = "② Display"
    lenFE = J.get(G_input, "number")("Lookback (N)", 34, J.obj(("min", 5), ("step", 1), ("group", grpCore)))
    smooth = J.get(G_input, "number")("Smoothing", 5, J.obj(("min", 1), ("step", 1), ("group", grpCore)))
    thTrend = J.get(G_input, "number")("Trend Zone (≤)", 30, J.obj(("min", 5), ("max", 50), ("step", 1), ("group", grpDisp)))
    thRange = J.get(G_input, "number")("Range Zone (≥)", 70, J.obj(("min", 50), ("max", 95), ("step", 1), ("group", grpDisp)))
    prev = move(G_close, 1)
    def _f1(c=J.undefined, p=J.undefined, *_args):
        return (J.get(G_Math, "abs")(J.sub(c, p)) if ((not J.nullish(c)) and (not J.nullish(p))) else None)
    oneStepAbs = G_for_every(G_close, prev, _f1)
    def _f2(vals=J.undefined, *_args):
        s = 0
        cnt = 0
        for v in J.iter_of(vals):
            if (not J.nullish(v)):
                s = J.add(s, v)
                cnt = J.inc(cnt)
        return (s if J.gt(cnt, 0) else None)
    sumAbs = G_sliding_window_function(oneStepAbs, lenFE, _f2)
    def _f3(vals=J.undefined, *_args):
        if J.lt(J.get(vals, "length"), J.add(lenFE, 1)):
            return None
        first = J.get(vals, 0)
        last = J.get(vals, J.sub(J.get(vals, "length"), 1))
        if ((J.nullish(first)) or (J.nullish(last))):
            return None
        return J.get(G_Math, "abs")(J.sub(last, first))
    backN = G_sliding_window_function(G_close, J.add(lenFE, 1), _f3)
    def _f4(dn=J.undefined, sabs=J.undefined, *_args):
        return (J.div(dn, sabs) if (((not J.nullish(dn)) and (not J.nullish(sabs))) and J.gt(sabs, 0)) else None)
    ER = G_for_every(backN, sumAbs, _f4)
    def _f5(e=J.undefined, *_args):
        return (None if (J.nullish(e)) else J.sub(1, e))
    FEraw = G_for_every(ER, _f5)
    FEsm = G_sma(FEraw, smooth)
    def _f6(v=J.undefined, *_args):
        return (None if (J.nullish(v)) else J.mul(v, 100))
    FEosc = G_for_every(FEsm, _f6)
    G_paint(FEosc, J.obj(("name", "FE"), ("style", "line"), ("thickness", 2), ("color", "#FFA500")))
    G_paint(G_horizontal_line(thTrend), J.obj(("name", "Trend"), ("color", "#B0B0B0"), ("style", "dotted")))
    G_paint(G_horizontal_line(50), J.obj(("name", "Mid"), ("color", "#B0B0B0"), ("style", "dotted")))
    G_paint(G_horizontal_line(thRange), J.obj(("name", "Range"), ("color", "#B0B0B0"), ("style", "dotted")))
    prevFE = move(FEosc, 1)
    def _f7(p=J.undefined, c=J.undefined, *_args):
        return (True if ((((not J.nullish(p)) and (not J.nullish(c))) and J.gt(p, thTrend)) and J.le(c, thTrend)) else False)
    enterTrend = G_for_every(prevFE, FEosc, _f7)
    def _f8(p=J.undefined, c=J.undefined, *_args):
        return (True if ((((not J.nullish(p)) and (not J.nullish(c))) and J.lt(p, thRange)) and J.ge(c, thRange)) else False)
    enterRange = G_for_every(prevFE, FEosc, _f8)
    def _f9(v=J.undefined, *_args):
        return (J.le(v, thTrend) if J.truthy(_t1 := (not J.nullish(v))) else _t1)
    inTrend = G_for_every(FEosc, _f9)
    def _f10(v=J.undefined, *_args):
        return (J.ge(v, thRange) if J.truthy(_t1 := (not J.nullish(v))) else _t1)
    inRange = G_for_every(FEosc, _f10)
    G_register_signal(enterTrend, "FE: Enter Trend (cross ↓)")
    G_register_signal(enterRange, "FE: Enter Range (cross ↑)")
    G_register_signal(inTrend, "FE: Trending Zone")
    G_register_signal(inRange, "FE: Ranging Zone")


register_store_indicator(
    script,
    name='fractal_energy_oscillator_TS',
    title='Fractal Energy Oscillator',
    developer='Feliks Ba\\u0144ka',
    url='https://trendspider.com/trading-tools-store/indicators/68a606-fractal-energy-oscillator/',
    position='lower',
    inputs=[{'id': 'lookback__n_', 'title': 'Lookback (N)', 'type': 'number', 'default': 34}, {'id': 'smoothing', 'title': 'Smoothing', 'type': 'number', 'default': 5}, {'id': 'trend_zone____', 'title': 'Trend Zone (≤)', 'type': 'number', 'default': 30}, {'id': 'range_zone____', 'title': 'Range Zone (≥)', 'type': 'number', 'default': 70}],
    outputs=['fe', 'trend', 'mid', 'range', 'fe__enter_trend__cross___', 'fe__enter_range__cross___', 'fe__trending_zone', 'fe__ranging_zone'],
    signals=['fe__enter_trend__cross___', 'fe__enter_range__cross___', 'fe__trending_zone', 'fe__ranging_zone'],
    requires=[],
    parity='exact',
)
