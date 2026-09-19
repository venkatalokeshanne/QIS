"""
Harmonic Flow & Velocity | Alpha Scope -- TrendSpider store indicator by Alpha Scope.

Registered as "harmonic_flow_velocity_alpha_scope_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/69c2f3-harmonic-flow-velocity-d_quant/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_add = G["add"]
    G_assert = G["assert"]
    G_cci = G["cci"]
    G_close = G["close"]
    G_color_candles = G["color_candles"]
    G_constants = G["constants"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_ema = G["ema"]
    G_for_every = G["for_every"]
    G_input = G["input"]
    G_interpolate_sparse_series = G["interpolate_sparse_series"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_mult = G["mult"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_request = G["request"]
    G_sub = G["sub"]
    G_time = G["time"]
    G_describe_indicator("Harmonic Flow & Velocity | Alpha-Scope", "price")
    col_mercury_bright = "#00e1ff"
    col_mercury_mid = "#0089a8"
    col_navy_deep = "#001f3f"
    col_navy_mid = " #0074D9"
    col_neutral = "#78909C"
    tf_in = J.get(G_input, "select")("Calculation Timeframe", "D", J.get(G_constants, "time_frames"))
    tema_len = J.get(G_input, "number")("TEMA Length", 50, J.obj(("min", 1), ("max", 500)))
    cci_len = J.get(G_input, "number")("CCI Length", 40, J.obj(("min", 1), ("max", 500)))
    dema_len = J.get(G_input, "number")("Signal DEMA Length", 30, J.obj(("min", 1), ("max", 500)))
    base_len = J.get(G_input, "number")("Baseline Overlay Length", 50, J.obj(("min", 1), ("max", 500)))
    def compute_tema(_close=J.undefined, _len=J.undefined, *_args):
        ema1 = G_ema(_close, _len)
        ema2 = G_ema(ema1, _len)
        ema3 = G_ema(ema2, _len)
        tema_line = G_add(G_mult(G_sub(ema1, ema2), 3), ema3)
        def _f1(_c=J.undefined, _t=J.undefined, *_args):
            return (1 if J.gt(_c, _t) else ((-1) if J.lt(_c, _t) else 0))
        return G_for_every(_close, tema_line, _f1)
    def compute_cci(_close=J.undefined, _len=J.undefined, *_args):
        cci_val = G_cci(_close, _len)
        def _f1(_v=J.undefined, *_args):
            return (1 if J.gt(_v, 0) else ((-1) if J.lt(_v, 0) else 0))
        return G_for_every(cci_val, _f1)
    def compute_dema(_src=J.undefined, _len=J.undefined, *_args):
        ema1 = G_ema(_src, _len)
        ema2 = G_ema(ema1, _len)
        return G_sub(G_mult(ema1, 2), ema2)
    myData = J.get(G_request, "history")(J.get(G_current, "ticker"), tf_in, J.obj(("chart_type", J.get(G_current, "chart_type")), ("ext_session", J.get(G_current, "is_ext_hours"))))
    G_assert((not J.truthy(J.get(myData, "error"))), J.template("Error fetching data: ", J.get(myData, "error")))
    s_tema = compute_tema(J.get(myData, "close"), tema_len)
    s_cci = compute_cci(J.get(myData, "close"), cci_len)
    s_tema_landed = G_land_points_onto_series(J.get(myData, "time"), s_tema, G_time, "ge")
    s_cci_landed = G_land_points_onto_series(J.get(myData, "time"), s_cci, G_time, "ge")
    s_tema_interpolated = G_interpolate_sparse_series(s_tema_landed, "constant")
    s_cci_interpolated = G_interpolate_sparse_series(s_cci_landed, "constant")
    def _f1(_t=J.undefined, _c=J.undefined, *_args):
        return J.div(J.add(_t, _c), 2)
    raw_sig = G_for_every(s_tema_interpolated, s_cci_interpolated, _f1)
    smoothed_sig = compute_dema(raw_sig, dema_len)
    baseline_ma = compute_dema(G_close, base_len)
    def _f2(_s=J.undefined, *_args):
        return (col_mercury_bright if J.ge(_s, 0.5) else (col_mercury_mid if J.gt(_s, 0) else (col_navy_deep if J.le(_s, (-0.5)) else (col_navy_mid if J.lt(_s, 0) else col_neutral))))
    bar_colors = G_for_every(smoothed_sig, _f2)
    G_color_candles(bar_colors)
    G_paint(baseline_ma, J.obj(("color", bar_colors), ("name", "Baseline MA"), ("style", "line")))
    def _f3(_s=J.undefined, *_args):
        return (col_mercury_bright if J.ge(_s, 0.95) else None)
    bg_bull = G_for_every(smoothed_sig, _f3)
    def _f4(_s=J.undefined, *_args):
        return (col_navy_deep if J.le(_s, (-0.95)) else None)
    bg_bear = G_for_every(smoothed_sig, _f4)
    G_paint(bg_bull, J.obj(("style", "labels_above"), ("color", col_mercury_bright), ("name", "Strong Bull BG"), ("hidden", True)))
    G_paint(bg_bear, J.obj(("style", "labels_below"), ("color", col_navy_deep), ("name", "Strong Bear BG"), ("hidden", True)))
    def _f5(_s=J.undefined, _prev=J.undefined, *_args):
        return (1 if (J.le(_prev, 0.3) and J.gt(_s, 0.3)) else 0)
    go_long = G_for_every(smoothed_sig, _f5)
    def _f6(_s=J.undefined, _prev=J.undefined, *_args):
        return (1 if (J.ge(_prev, (-0.3)) and J.lt(_s, (-0.3))) else 0)
    go_short = G_for_every(smoothed_sig, _f6)
    G_register_signal(go_long, "Long Signal")
    G_register_signal(go_short, "Short Signal")


register_store_indicator(
    script,
    name='harmonic_flow_velocity_alpha_scope_TS',
    title='Harmonic Flow & Velocity | Alpha Scope',
    developer='Alpha Scope',
    url='https://trendspider.com/trading-tools-store/indicators/69c2f3-harmonic-flow-velocity-d_quant/',
    position='price',
    inputs=[{'id': 'calculation_timeframe', 'title': 'Calculation Timeframe', 'type': 'select_wide', 'default': 'D', 'options': ['1', '2', '3', '4', '5', '6', '10', '12', '15', '30', '45', '60', '65', '90', '120', '240', '1440', 'D', 'W', 'M', 'Q', 'Y']}, {'id': 'tema_length', 'title': 'TEMA Length', 'type': 'number', 'default': 50}, {'id': 'cci_length', 'title': 'CCI Length', 'type': 'number', 'default': 40}, {'id': 'signal_dema_length', 'title': 'Signal DEMA Length', 'type': 'number', 'default': 30}, {'id': 'baseline_overlay_length', 'title': 'Baseline Overlay Length', 'type': 'number', 'default': 50}],
    outputs=['cdl', 'baseline_ma', 'strong_bull_bg', 'strong_bear_bg', 'long_signal', 'short_signal'],
    signals=['long_signal', 'short_signal'],
    requires=['history'],
    parity='exact',
)
