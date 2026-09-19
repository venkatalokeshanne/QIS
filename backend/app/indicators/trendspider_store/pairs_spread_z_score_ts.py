"""
Pairs Spread Z-Score -- TrendSpider store indicator by Gustivus.

Registered as "pairs_spread_z_score_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/689d04-pairs-spread-z-score/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_Number = G["Number"]
    G_assert = G["assert"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_horizontal_line = G["horizontal_line"]
    G_input = G["input"]
    G_isFinite = G["isFinite"]
    G_paint = G["paint"]
    G_paint_overlay = G["paint_overlay"]
    G_register_signal = G["register_signal"]
    G_request = G["request"]
    G_sliding_window_function = G["sliding_window_function"]
    G_sma = G["sma"]
    G_stdev = G["stdev"]
    G_time = G["time"]
    G_describe_indicator("Pairs Spread Z-Score", "lower", J.obj(("shortName", "Pairs Z+")))
    ticker1 = J.get(G_input, "symbol")("Ticker 1 (y)", "MMM")
    ticker2 = J.get(G_input, "symbol")("Ticker 2 (x)", "AEP")
    betaMode = J.get(G_input, "select")("Beta Mode", "Fixed", J.JSArray(["Fixed", "Auto OLS"]))
    betaFixed = J.get(G_input, "number")("Beta (Fixed mode)", 1.35, J.obj(("min", 0.01), ("max", 5), ("step", 0.01)))
    betaLen = J.get(G_input, "number")("Beta Lookback (Auto OLS)", 120, J.obj(("min", 20), ("max", 500), ("step", 1)))
    useLog = J.seq(J.get(G_input, "select")("Use Log Prices?", "Yes", J.JSArray(["Yes", "No"])), "Yes")
    window = J.get(G_input, "number")("Z-Score Lookback", 60, J.obj(("min", 10), ("max", 500), ("step", 1)))
    upperThr = J.get(G_input, "number")("Upper Entry Threshold", 2, J.obj(("min", 0.5), ("max", 5), ("step", 0.1)))
    lowerThr = J.get(G_input, "number")("Lower Entry Threshold", (-2), J.obj(("min", (-5)), ("max", (-0.5)), ("step", 0.1)))
    exitThr = J.get(G_input, "number")("Exit Threshold (abs)", 0.5, J.obj(("min", 0.1), ("max", 2), ("step", 0.1)))
    confirmN = J.get(G_input, "number")("Confirm Bars", 1, J.obj(("min", 1), ("max", 5), ("step", 1)))
    hlLen = J.get(G_input, "number")("Half-Life Lookback (bars)", 120, J.obj(("min", 30), ("max", 500), ("step", 1)))
    closeOnlySel = J.get(G_input, "select")("Close-Only Mode", "On", J.JSArray(["On", "Off"]))
    closeOnly = J.seq(closeOnlySel, "On")
    yRes = J.get(G_request, "history")(ticker1, J.get(G_current, "resolution"))
    G_assert((not J.truthy(J.get(yRes, "error"))), J.template("Error fetching data for ", ticker1, ": ", J.get(yRes, "error")))
    xRes = J.get(G_request, "history")(ticker2, J.get(G_current, "resolution"))
    G_assert((not J.truthy(J.get(xRes, "error"))), J.template("Error fetching data for ", ticker2, ": ", J.get(xRes, "error")))
    def lag1(series=J.undefined, *_args):
        def _f1(vals=J.undefined, *_args):
            return J.get(vals, 0)
        return G_sliding_window_function(series, 2, _f1)
    def alignByChartTime(y=J.undefined, yTime=J.undefined, x=J.undefined, xTime=J.undefined, chartTime_2=J.undefined, *_args):
        yMap = J.obj()
        i = 0
        while J.lt(i, J.get(yTime, "length")):
            J.set(yMap, J.get(yTime, i), J.get(y, i))
            i = J.inc(i)
        xMap = J.obj()
        i_2 = 0
        while J.lt(i_2, J.get(xTime, "length")):
            J.set(xMap, J.get(xTime, i_2), J.get(x, i_2))
            i_2 = J.inc(i_2)
        yA = J.JSArray([])
        xA = J.JSArray([])
        i_3 = 0
        while J.lt(i_3, J.get(chartTime_2, "length")):
            t = J.get(chartTime_2, i_3)
            J.get(yA, "push")((None if J.nullish(_t1 := J.get(yMap, t)) else _t1))
            J.get(xA, "push")((None if J.nullish(_t2 := J.get(xMap, t)) else _t2))
            i_3 = J.inc(i_3)
        return J.JSArray([yA, xA])
    def ols_beta(yArr=J.undefined, xArr=J.undefined, N=J.undefined, fallback=J.undefined, *_args):
        y = J.JSArray([])
        x = J.JSArray([])
        i = J.get(G_Math, "max")(0, J.sub(J.get(yArr, "length"), N))
        while J.lt(i, J.get(yArr, "length")):
            yy = J.get(yArr, i)
            xx_2 = J.get(xArr, i)
            if ((((not J.nullish(yy)) and (not J.nullish(xx_2))) and J.truthy(G_isFinite(yy))) and J.truthy(G_isFinite(xx_2))):
                J.get(y, "push")(yy)
                J.get(x, "push")(xx_2)
            i = J.inc(i)
        n = J.get(x, "length")
        if J.lt(n, 5):
            return fallback
        xSum = 0
        ySum = 0
        xx = 0
        xy = 0
        i_2 = 0
        while J.lt(i_2, n):
            xSum = J.add(xSum, J.get(x, i_2))
            ySum = J.add(ySum, J.get(y, i_2))
            xx = J.add(xx, J.mul(J.get(x, i_2), J.get(x, i_2)))
            xy = J.add(xy, J.mul(J.get(x, i_2), J.get(y, i_2)))
            i_2 = J.inc(i_2)
        den = J.sub(J.mul(n, xx), J.mul(xSum, xSum))
        if J.seq(den, 0):
            return fallback
        return J.div(J.sub(J.mul(n, xy), J.mul(xSum, ySum)), den)
    def safeZ(s=J.undefined, m=J.undefined, sd=J.undefined, *_args):
        if (((J.nullish(s)) or (J.nullish(m))) or (J.nullish(sd))):
            return None
        if ((not J.truthy(G_isFinite(sd))) or J.seq(sd, 0)):
            return None
        return J.div(J.sub(s, m), sd)
    def confirmBars(condSeries=J.undefined, n=J.undefined, *_args):
        def _f1(vals=J.undefined, *_args):
            i = 0
            while J.lt(i, J.get(vals, "length")):
                if (not J.truthy(J.get(vals, i))):
                    return None
                i = J.inc(i)
            return 1
        return G_sliding_window_function(condSeries, n, _f1)
    def ar1_half_life(series=J.undefined, N=J.undefined, *_args):
        s = J.JSArray([])
        i = J.get(G_Math, "max")(0, J.sub(J.get(series, "length"), N))
        while J.lt(i, J.get(series, "length")):
            v = J.get(series, i)
            if ((not J.nullish(v)) and J.truthy(G_isFinite(v))):
                J.get(s, "push")(v)
            i = J.inc(i)
        if J.lt(J.get(s, "length"), 20):
            return J.obj(("phi", None), ("hl", None))
        y = J.JSArray([])
        x = J.JSArray([])
        i_2 = 1
        while J.lt(i_2, J.get(s, "length")):
            J.get(y, "push")(J.get(s, i_2))
            J.get(x, "push")(J.get(s, J.sub(i_2, 1)))
            i_2 = J.inc(i_2)
        xSum = 0
        ySum = 0
        xx = 0
        xy = 0
        n = J.get(x, "length")
        i_3 = 0
        while J.lt(i_3, n):
            xSum = J.add(xSum, J.get(x, i_3))
            ySum = J.add(ySum, J.get(y, i_3))
            xx = J.add(xx, J.mul(J.get(x, i_3), J.get(x, i_3)))
            xy = J.add(xy, J.mul(J.get(x, i_3), J.get(y, i_3)))
            i_3 = J.inc(i_3)
        den = J.sub(J.mul(n, xx), J.mul(xSum, xSum))
        if J.seq(den, 0):
            return J.obj(("phi", None), ("hl", None))
        phi_2 = J.div(J.sub(J.mul(n, xy), J.mul(xSum, ySum)), den)
        if (((not J.truthy(G_isFinite(phi_2))) or J.le(phi_2, 0)) or J.ge(phi_2, 1)):
            return J.obj(("phi", phi_2), ("hl", None))
        hl_2 = J.div(J.neg(J.get(G_Math, "log")(2)), J.get(G_Math, "log")(phi_2))
        return J.obj(("phi", phi_2), ("hl", hl_2))
    chartTime = G_time
    _t1 = J.iter_of(alignByChartTime(J.get(yRes, "close"), J.get(yRes, "time"), J.get(xRes, "close"), J.get(xRes, "time"), chartTime))
    yAlnRaw = (_t1[0] if 0 < len(_t1) else J.undefined)
    xAlnRaw = (_t1[1] if 1 < len(_t1) else J.undefined)
    def _f2(v=J.undefined, *_args):
        return (J.get(G_Math, "log")(v) if (not J.nullish(v)) else None)
    yAligned0 = (G_for_every(yAlnRaw, _f2) if J.truthy(useLog) else yAlnRaw)
    def _f3(v=J.undefined, *_args):
        return (J.get(G_Math, "log")(v) if (not J.nullish(v)) else None)
    xAligned0 = (G_for_every(xAlnRaw, _f3) if J.truthy(useLog) else xAlnRaw)
    yAligned = (lag1(yAligned0) if J.truthy(closeOnly) else yAligned0)
    xAligned = (lag1(xAligned0) if J.truthy(closeOnly) else xAligned0)
    beta = (ols_beta(yAligned, xAligned, betaLen, betaFixed) if J.seq(betaMode, "Auto OLS") else betaFixed)
    def _f4(y=J.undefined, x=J.undefined, *_args):
        return (J.sub(y, J.mul(beta, x)) if ((not J.nullish(y)) and (not J.nullish(x))) else None)
    spread = G_for_every(yAligned, xAligned, _f4)
    spreadMean = G_sma(spread, window)
    spreadStd = G_stdev(spread, window)
    def _f5(s=J.undefined, m=J.undefined, sd=J.undefined, *_args):
        return safeZ(s, m, sd)
    zScore = G_for_every(spread, spreadMean, spreadStd, _f5)
    def _f6(z=J.undefined, *_args):
        return (True if ((not J.nullish(z)) and J.lt(z, lowerThr)) else False)
    longCond = G_for_every(zScore, _f6)
    def _f7(z=J.undefined, *_args):
        return (True if ((not J.nullish(z)) and J.gt(z, upperThr)) else False)
    shortCond = G_for_every(zScore, _f7)
    def _f8(z=J.undefined, *_args):
        return (True if ((not J.nullish(z)) and J.lt(J.get(G_Math, "abs")(z), exitThr)) else False)
    exitCond = G_for_every(zScore, _f8)
    longSignal = confirmBars(longCond, J.get(G_Math, "max")(1, confirmN))
    shortSignal = confirmBars(shortCond, J.get(G_Math, "max")(1, confirmN))
    exitSignal = confirmBars(exitCond, J.get(G_Math, "max")(1, confirmN))
    _t9 = J.require_object(ar1_half_life(spread, hlLen))
    phi = J.get(_t9, "phi")
    hl = J.get(_t9, "hl")
    G_paint(zScore, J.obj(("name", "Spread Z-score"), ("color", "blue")))
    G_paint(G_horizontal_line(upperThr), J.obj(("name", "Upper"), ("color", "red"), ("style", "dotted")))
    G_paint(G_horizontal_line(0), J.obj(("name", "Mean"), ("color", "gray"), ("style", "dotted")))
    G_paint(G_horizontal_line(lowerThr), J.obj(("name", "Lower"), ("color", "green"), ("style", "dotted")))
    G_paint(G_horizontal_line(exitThr), J.obj(("name", "Exit Upper"), ("color", "silver"), ("style", "line")))
    G_paint(G_horizontal_line(J.neg(exitThr)), J.obj(("name", "Exit Lower"), ("color", "silver"), ("style", "line")))
    G_register_signal(longSignal, "Long")
    G_register_signal(shortSignal, "Short")
    G_register_signal(exitSignal, "Exit")
    lastZ = J.get(zScore, J.sub(J.get(zScore, "length"), 1))
    betaText = (J.template("β(rolling ", betaLen, ")") if J.seq(betaMode, "Auto OLS") else J.template("β(fixed)"))
    G_paint_overlay("overlay", J.obj(("position", "bottom_right")), J.obj(("rows", J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", J.template("Pair: ", ticker1, "-", ticker2)), ("color", "var(--text-color)"), ("border", "solid var(--border-color) 1px"), ("padding", 5)), J.obj(("text", J.template(betaText, ": ", J.get(G_Number(beta), "toFixed")(4))), ("color", "var(--text-color)"), ("border", "solid var(--border-color) 1px"), ("padding", 5)), J.obj(("text", J.template("z: ", ("N/A" if (J.nullish(lastZ)) else J.get(lastZ, "toFixed")(2)))), ("color", "var(--text-color)"), ("border", "solid var(--border-color) 1px"), ("padding", 5)), J.obj(("text", J.template("HL(", hlLen, "): ", ("N/A" if (J.nullish(hl)) else J.get(hl, "toFixed")(1)), " bars")), ("color", "var(--text-color)"), ("border", "solid var(--border-color) 1px"), ("padding", 5)), J.obj(("text", J.template("Log: ", ("Yes" if J.truthy(useLog) else "No"))), ("color", "var(--text-color)"), ("border", "solid var(--border-color) 1px"), ("padding", 5)), J.obj(("text", J.template("Close-only: ", ("On" if J.truthy(closeOnly) else "Off"))), ("color", "var(--text-color)"), ("border", "solid var(--border-color) 1px"), ("padding", 5))])))]))))


register_store_indicator(
    script,
    name='pairs_spread_z_score_TS',
    title='Pairs Spread Z-Score',
    developer='Gustivus',
    url='https://trendspider.com/trading-tools-store/indicators/689d04-pairs-spread-z-score/',
    position='lower',
    inputs=[{'id': 'sym-ticker_1__y_', 'title': 'Ticker 1 (y)', 'type': 'symbol-search', 'default': 'MMM'}, {'id': 'sym-ticker_2__x_', 'title': 'Ticker 2 (x)', 'type': 'symbol-search', 'default': 'AEP'}, {'id': 'beta_mode', 'title': 'Beta Mode', 'type': 'select_wide', 'default': 'Fixed', 'options': ['Fixed', 'Auto OLS']}, {'id': 'beta__fixed_mode_', 'title': 'Beta (Fixed mode)', 'type': 'number', 'default': 1.35}, {'id': 'beta_lookback__auto_ols_', 'title': 'Beta Lookback (Auto OLS)', 'type': 'number', 'default': 120}, {'id': 'use_log_prices_', 'title': 'Use Log Prices?', 'type': 'select_wide', 'default': 'Yes', 'options': ['Yes', 'No']}, {'id': 'z_score_lookback', 'title': 'Z-Score Lookback', 'type': 'number', 'default': 60}, {'id': 'upper_entry_threshold', 'title': 'Upper Entry Threshold', 'type': 'number', 'default': 2}, {'id': 'lower_entry_threshold', 'title': 'Lower Entry Threshold', 'type': 'number', 'default': -2}, {'id': 'exit_threshold__abs_', 'title': 'Exit Threshold (abs)', 'type': 'number', 'default': 0.5}, {'id': 'confirm_bars', 'title': 'Confirm Bars', 'type': 'number', 'default': 1}, {'id': 'half_life_lookback__bars_', 'title': 'Half-Life Lookback (bars)', 'type': 'number', 'default': 120}, {'id': 'close_only_mode', 'title': 'Close-Only Mode', 'type': 'select_wide', 'default': 'On', 'options': ['On', 'Off']}],
    outputs=['spread_z_score', 'upper', 'mean', 'lower', 'exit_upper', 'exit_lower', 'long', 'short', 'exit'],
    signals=['long', 'short', 'exit'],
    requires=['history'],
    parity='exact',
)
