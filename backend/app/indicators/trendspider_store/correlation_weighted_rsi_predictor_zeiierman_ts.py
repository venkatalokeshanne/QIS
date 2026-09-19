"""
Correlation-Weighted RSI Predictor (Zeiierman) -- TrendSpider store indicator by Zeiierman Trading.

Registered as "correlation_weighted_rsi_predictor_zeiierman_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68e793-ai-weighted-rsi-zeiierman/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_add = G["add"]
    G_atr = G["atr"]
    G_close = G["close"]
    G_color_cloud = G["color_cloud"]
    G_correlation = G["correlation"]
    G_describe_indicator = G["describe_indicator"]
    G_div = G["div"]
    G_fill = G["fill"]
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_horizontal_line = G["horizontal_line"]
    G_input = G["input"]
    G_low = G["low"]
    G_mult = G["mult"]
    G_paint = G["paint"]
    G_rsi = G["rsi"]
    G_series_of = G["series_of"]
    G_shift = G["shift"]
    G_sma = G["sma"]
    G_stdev = G["stdev"]
    G_sub = G["sub"]
    G_volume = G["volume"]
    G_describe_indicator("Correlation-Weighted RSI Predictor (Zeiierman)", "lower", J.obj(("decimals", 0), ("mainColorInheritFrom", "text"), ("shortName", "Correlation-Weighted RSI Predictor (Zeiierman)")))
    t1 = "RSI lookback length computed on the current timeframe."
    t2 = "Moving Average lookback length computed on RSI."
    t3 = "Rolling window for correlation learning and z-scoring."
    rsiLen = J.get(G_input, "number")("RSI Length", 14, J.obj(("min", 2), ("max", 300)))
    sigLen = J.get(G_input, "number")("Signal Length", 20, J.obj(("min", 2), ("max", 300)))
    learnLen = J.get(G_input, "number")("Learning Window", 20, J.obj(("min", 1), ("max", 300)))
    def _f1(_c=J.undefined, _prev=J.undefined, _idx=J.undefined, *_args):
        prevClose = (J.get(G_close, J.sub(_idx, 1)) if J.gt(_idx, 0) else _c)
        return J.get(G_Math, "log")(J.div(_c, prevClose))
    retLog = G_for_every(G_close, _f1)
    rsiVal = G_rsi(G_close, rsiLen)
    atrPct = G_div(G_atr(G_high, G_low, G_close, 200), G_close)
    def _f2(_v=J.undefined, _prev=J.undefined, _idx=J.undefined, *_args):
        prevVol = (J.get(G_volume, J.sub(_idx, 1)) if J.gt(_idx, 0) else _v)
        return J.get(G_Math, "log")(J.div(_v, prevVol))
    volLogChg = G_for_every(G_volume, _f2)
    y_rsi = G_shift(rsiVal, 1)
    x_ret = G_shift(retLog, 1)
    x_rsi = G_shift(rsiVal, 1)
    x_atrp = G_shift(atrPct, 1)
    x_vchg = G_shift(volLogChg, 1)
    x_vol = G_shift(G_volume, 1)
    def f_z(src=J.undefined, length=J.undefined, *_args):
        myMean = G_sma(src, length)
        myStdev = G_stdev(src, length)
        return G_div(G_sub(src, myMean), myStdev)
    def _f3(v=J.undefined, *_args):
        return J.get(G_Math, "abs")((_t1 if J.truthy(_t1 := v) else 0))
    corrs_abs_ret = J.get(G_correlation(y_rsi, x_ret, learnLen), "map")(_f3)
    def _f4(v=J.undefined, *_args):
        return J.get(G_Math, "abs")((_t1 if J.truthy(_t1 := v) else 0))
    corrs_abs_rsi = J.get(G_correlation(y_rsi, x_rsi, learnLen), "map")(_f4)
    def _f5(v=J.undefined, *_args):
        return J.get(G_Math, "abs")((_t1 if J.truthy(_t1 := v) else 0))
    corrs_abs_atrp = J.get(G_correlation(y_rsi, x_atrp, learnLen), "map")(_f5)
    def _f6(v=J.undefined, *_args):
        return J.get(G_Math, "abs")((_t1 if J.truthy(_t1 := v) else 0))
    corrs_abs_vchg = J.get(G_correlation(y_rsi, x_vchg, learnLen), "map")(_f6)
    def _f7(v=J.undefined, *_args):
        return J.get(G_Math, "abs")((_t1 if J.truthy(_t1 := v) else 0))
    corrs_abs_vol = J.get(G_correlation(y_rsi, x_vol, learnLen), "map")(_f7)
    xz_ret = f_z(x_ret, learnLen)
    xz_rsi = f_z(x_rsi, learnLen)
    xz_atrp = f_z(x_atrp, learnLen)
    xz_vchg = f_z(x_vchg, learnLen)
    xz_vol = f_z(x_vol, learnLen)
    coef_ret = G_correlation(y_rsi, x_ret, learnLen)
    coef_rsi = G_series_of(1)
    coef_atrp = G_correlation(y_rsi, x_atrp, learnLen)
    coef_vchg = G_correlation(y_rsi, x_vchg, learnLen)
    coef_vol = G_correlation(y_rsi, x_vol, learnLen)
    def _f8(_cr=J.undefined, _ci=J.undefined, _ca=J.undefined, _cv=J.undefined, _co=J.undefined, _zr=J.undefined, _zi=J.undefined, _za=J.undefined, _zv=J.undefined, _zo=J.undefined, _cfr=J.undefined, _cfi=J.undefined, _cfa=J.undefined, _cfv=J.undefined, _cfo=J.undefined, *_args):
        corrs = J.JSArray([_cr, _ci, _ca, _cv, _co])
        zscores = J.JSArray([_zr, _zi, _za, _zv, _zo])
        coefs = J.JSArray([_cfr, _cfi, _cfa, _cfv, _cfo])
        def _f1(v=J.undefined, i=J.undefined, *_args):
            return J.obj(("v", (_t1 if J.truthy(_t1 := v) else 0)), ("i", i))
        def _f2(a=J.undefined, b=J.undefined, *_args):
            return J.sub(J.get(b, "v"), J.get(a, "v"))
        def _f3(x=J.undefined, *_args):
            return J.get(x, "i")
        indices = J.get(J.get(J.get(J.get(corrs, "map")(_f1), "sort")(_f2), "slice")(0, 5), "map")(_f3)
        mySum = 0
        for idx in J.iter_of(indices):
            mySum = J.add(mySum, J.mul((_t4 if J.truthy(_t4 := J.get(coefs, idx)) else 0), (_t5 if J.truthy(_t5 := J.get(zscores, idx)) else 0)))
        return mySum
    pred_rsi_z = G_for_every(corrs_abs_ret, corrs_abs_rsi, corrs_abs_atrp, corrs_abs_vchg, corrs_abs_vol, xz_ret, xz_rsi, xz_atrp, xz_vchg, xz_vol, coef_ret, coef_rsi, coef_atrp, coef_vchg, coef_vol, _f8)
    rsi_mean = G_sma(y_rsi, learnLen)
    rsi_std = G_stdev(y_rsi, learnLen)
    pred_rsi = G_add(rsi_mean, G_mult(rsi_std, pred_rsi_z))
    def _f9(_p=J.undefined, *_args):
        weight = J.mul(J.get(G_Math, "max")((-2), J.get(G_Math, "min")(2, J.div(J.sub(50, (_t1 if J.truthy(_t1 := _p) else 0)), 50))), (-1))
        return weight
    rsiWeight = G_for_every(pred_rsi, _f9)
    ma_rsi = G_sma(rsiWeight, sigLen)
    def _f10(_w=J.undefined, *_args):
        return (_w if J.gt(_w, 0.5) else None)
    overboughtTop = G_for_every(rsiWeight, _f10)
    def _f11(_w=J.undefined, *_args):
        return (0.5 if J.gt(_w, 0.5) else None)
    overboughtBottom = G_for_every(rsiWeight, _f11)
    def _f12(_w=J.undefined, *_args):
        return ((-0.5) if J.lt(_w, (-0.5)) else None)
    oversoldTop = G_for_every(rsiWeight, _f12)
    def _f13(_w=J.undefined, *_args):
        return (_w if J.lt(_w, (-0.4)) else None)
    oversoldBottom = G_for_every(rsiWeight, _f13)
    rsiPlot = G_paint(rsiWeight, J.obj(("name", "Correlation-Weighted RSI Predictor"), ("color", "#7E57C2")))
    G_paint(ma_rsi, J.obj(("name", "Correlation-Weighted RSI Predictor Signal Line"), ("color", "orange")))
    upperBand = G_paint(G_horizontal_line(0.5), J.obj(("name", "Correlation-Weighted RSI Predictor Upper Band"), ("color", "#787B86"), ("style", "dotted")))
    midLine = G_paint(G_horizontal_line(0), J.obj(("name", "Correlation-Weighted RSI Predictor Middle Band"), ("color", "#787B86"), ("style", "dotted")))
    lowerBand = G_paint(G_horizontal_line((-0.5)), J.obj(("name", "Correlation-Weighted RSI Predictor Lower Band"), ("color", "#787B86"), ("style", "dotted")))
    G_fill(upperBand, lowerBand, "rgba(126, 87, 194, 0.1)", 0.1, "Correlation-Weighted RSI PredictorI Background Fill")
    G_color_cloud(overboughtTop, overboughtBottom, "rgba(0, 255, 0, 0)", "rgba(0, 255, 0, 1)", "Overbought Gradient Top", "Overbought Gradient Bottom", 0.5)
    G_color_cloud(oversoldTop, oversoldBottom, "rgba(255, 0, 0, 1)", "rgba(255, 0, 0, 0)", "Oversold Gradient Top", "Oversold Gradient Bottom", 0.5)


register_store_indicator(
    script,
    name='correlation_weighted_rsi_predictor_zeiierman_TS',
    title='Correlation-Weighted RSI Predictor (Zeiierman)',
    developer='Zeiierman Trading',
    url='https://trendspider.com/trading-tools-store/indicators/68e793-ai-weighted-rsi-zeiierman/',
    position='lower',
    inputs=[{'id': 'rsi_length', 'title': 'RSI Length', 'type': 'number', 'default': 14}, {'id': 'signal_length', 'title': 'Signal Length', 'type': 'number', 'default': 20}, {'id': 'learning_window', 'title': 'Learning Window', 'type': 'number', 'default': 20}],
    outputs=['correlation_weighted_rsi_predictor', 'correlation_weighted_rsi_predictor_signal_line', 'correlation_weighted_rsi_predictor_upper_band', 'correlation_weighted_rsi_predictor_middle_band', 'correlation_weighted_rsi_predictor_lower_band', 'line_7', 'line_8', 'line_10', 'line_11', 'line_13', 'line_14', 'line_16', 'line_17'],
    signals=[],
    requires=[],
    parity='exact',
)
