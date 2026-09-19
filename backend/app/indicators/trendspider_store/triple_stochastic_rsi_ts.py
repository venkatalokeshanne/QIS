"""
Triple Stochastic RSI -- TrendSpider store indicator by Trade Seekers.

Registered as "triple_stochastic_rsi_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68a13a-triple-stochastic-rsi/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_fill = G["fill"]
    G_for_every = G["for_every"]
    G_horizontal_line = G["horizontal_line"]
    G_input = G["input"]
    G_paint = G["paint"]
    G_paint_overlay = G["paint_overlay"]
    G_register_signal = G["register_signal"]
    G_shift = G["shift"]
    G_sma = G["sma"]
    G_stochastic_rsi = G["stochastic_rsi"]
    G_describe_indicator("Triple Stochastic RSI", "lower", J.obj(("decimals", 2), ("warmup", "1000")))
    kInput = J.get(G_input, "number")("K", 3, J.obj(("min", 1), ("max", 50)))
    dInput = J.get(G_input, "number")("D", 3, J.obj(("min", 1), ("max", 50)))
    rsiInput = J.get(G_input, "number")("RSI", 14, J.obj(("min", 1), ("max", 50)))
    multiInput = J.get(G_input, "number")("2nd Multi", 3, J.obj(("min", 2), ("max", 50)))
    multi2Input = J.get(G_input, "number")("3rd Multi", 6, J.obj(("min", 2), ("max", 50)))
    overboughtInput = J.get(G_input, "number")("Overbought", 80, J.obj(("min", 0), ("max", 100)))
    oversoldInput = J.get(G_input, "number")("Oversold", 20, J.obj(("min", 0), ("max", 100)))
    showStatsInput = J.eq(G_input("Show Stats Overlay?", "Yes", J.JSArray(["Yes", "No"])), "Yes")
    def calculateAverageStreakLength(_series=J.undefined, *_args):
        streaks = J.JSArray([])
        currentStreak = 0
        i = 0
        while J.lt(i, J.get(_series, "length")):
            if J.truthy(J.get(_series, i)):
                currentStreak = J.inc(currentStreak)
            elif J.gt(currentStreak, 0):
                J.get(streaks, "push")(currentStreak)
                currentStreak = 0
            i = J.inc(i)
        if J.gt(currentStreak, 0):
            J.get(streaks, "push")(currentStreak)
        def _f1(a=J.undefined, b=J.undefined, *_args):
            return J.add(a, b)
        return (J.div(J.get(streaks, "reduce")(_f1, 0), J.get(streaks, "length")) if J.gt(J.get(streaks, "length"), 0) else 0)
    def calculateCurrentStreakLength(_series=J.undefined, *_args):
        currentStreak = 0
        i = J.sub(J.get(_series, "length"), 1)
        while J.ge(i, 0):
            if J.truthy(J.get(_series, i)):
                currentStreak = J.inc(currentStreak)
            else:
                break
            i = J.dec(i)
        return currentStreak
    def createOverlayStochStatRow(currentAboveMid=J.undefined, currentBelowMid=J.undefined, avgAboveMid=J.undefined, avgBelowMid=J.undefined, stochTitle=J.undefined, stochTextColor=J.undefined, *_args):
        return J.obj(("cells", J.JSArray([J.obj(("text", J.template(stochTitle)), ("color", stochTextColor), ("paddingRight", "1.5em")), J.obj(("text", J.template((currentAboveMid if J.gt(currentAboveMid, 0) else currentBelowMid), " ", ("▲" if J.gt(currentAboveMid, 0) else "▼"))), ("color", stochTextColor), ("paddingRight", "1.5em"), ("textAlign", "center")), J.obj(("text", J.template(J.get(avgAboveMid, "toFixed")(0), " ▲ / ", J.get(avgBelowMid, "toFixed")(0), " ▼")), ("color", stochTextColor), ("textAlign", "center"))])))
    fastK = G_stochastic_rsi(G_close, rsiInput, kInput)
    fastD = G_sma(fastK, dInput)
    slowK = G_stochastic_rsi(G_close, J.mul(rsiInput, multiInput), J.mul(kInput, multiInput))
    slowD = G_sma(slowK, J.mul(dInput, multiInput))
    slowestK = G_stochastic_rsi(G_close, J.mul(rsiInput, multi2Input), J.mul(kInput, multi2Input))
    slowestD = G_sma(slowestK, J.mul(dInput, multi2Input))
    def _f1(k=J.undefined, d=J.undefined, pk=J.undefined, pd=J.undefined, *_args):
        return ("▼" if (J.gt(k, d) and J.lt(pk, pd)) else ("▲" if (J.lt(k, d) and J.gt(pk, pd)) else None))
    fastTrendFlips = G_for_every(fastK, fastD, G_shift(fastK, (-1)), G_shift(fastD, (-1)), _f1)
    def _f2(k=J.undefined, d=J.undefined, pk=J.undefined, pd=J.undefined, *_args):
        return ("▼" if (J.gt(k, d) and J.lt(pk, pd)) else ("▲" if (J.lt(k, d) and J.gt(pk, pd)) else None))
    slowTrendFlips = G_for_every(slowK, slowD, G_shift(slowK, (-1)), G_shift(slowD, (-1)), _f2)
    def _f3(k=J.undefined, d=J.undefined, *_args):
        return J.gt(k, d)
    fastTrendLong = G_for_every(fastK, fastD, _f3)
    def _f4(k=J.undefined, d=J.undefined, *_args):
        return J.lt(k, d)
    fastTrendShort = G_for_every(fastK, fastD, _f4)
    def _f5(k=J.undefined, d=J.undefined, *_args):
        return J.gt(k, d)
    slowTrendLong = G_for_every(slowK, slowD, _f5)
    def _f6(k=J.undefined, d=J.undefined, *_args):
        return J.lt(k, d)
    slowTrendShort = G_for_every(slowK, slowD, _f6)
    def _f7(k=J.undefined, d=J.undefined, *_args):
        return J.gt(k, d)
    slowestTrendLong = G_for_every(slowestK, slowestD, _f7)
    def _f8(k=J.undefined, d=J.undefined, *_args):
        return J.lt(k, d)
    slowestTrendShort = G_for_every(slowestK, slowestD, _f8)
    def _f9(k=J.undefined, *_args):
        return J.ge(k, 51)
    fastTrendBullish = G_for_every(fastK, _f9)
    def _f10(k=J.undefined, *_args):
        return J.le(k, 49)
    fastTrendBearish = G_for_every(fastK, _f10)
    def _f11(k=J.undefined, *_args):
        return J.ge(k, 51)
    slowTrendBullish = G_for_every(slowK, _f11)
    def _f12(k=J.undefined, *_args):
        return J.le(k, 49)
    slowTrendBearish = G_for_every(slowK, _f12)
    def _f13(k=J.undefined, *_args):
        return J.ge(k, 51)
    slowestTrendBullish = G_for_every(slowestK, _f13)
    def _f14(k=J.undefined, *_args):
        return J.le(k, 49)
    slowestTrendBearish = G_for_every(slowestK, _f14)
    def _f15(_k=J.undefined, *_args):
        return J.gt(_k, 50)
    fastAboveMid = calculateAverageStreakLength(J.get(fastK, "map")(_f15))
    def _f16(_k=J.undefined, *_args):
        return J.lt(_k, 50)
    fastBelowMid = calculateAverageStreakLength(J.get(fastK, "map")(_f16))
    def _f17(_k=J.undefined, *_args):
        return J.gt(_k, 50)
    slowAboveMid = calculateAverageStreakLength(J.get(slowK, "map")(_f17))
    def _f18(_k=J.undefined, *_args):
        return J.lt(_k, 50)
    slowBelowMid = calculateAverageStreakLength(J.get(slowK, "map")(_f18))
    def _f19(_k=J.undefined, *_args):
        return J.gt(_k, 50)
    slowestAboveMid = calculateAverageStreakLength(J.get(slowestK, "map")(_f19))
    def _f20(_k=J.undefined, *_args):
        return J.lt(_k, 50)
    slowestBelowMid = calculateAverageStreakLength(J.get(slowestK, "map")(_f20))
    def _f21(_k=J.undefined, *_args):
        return J.gt(_k, 50)
    currentFastAboveMid = calculateCurrentStreakLength(J.get(fastK, "map")(_f21))
    def _f22(_k=J.undefined, *_args):
        return J.lt(_k, 50)
    currentFastBelowMid = calculateCurrentStreakLength(J.get(fastK, "map")(_f22))
    def _f23(_k=J.undefined, *_args):
        return J.gt(_k, 50)
    currentSlowAboveMid = calculateCurrentStreakLength(J.get(slowK, "map")(_f23))
    def _f24(_k=J.undefined, *_args):
        return J.lt(_k, 50)
    currentSlowBelowMid = calculateCurrentStreakLength(J.get(slowK, "map")(_f24))
    def _f25(_k=J.undefined, *_args):
        return J.gt(_k, 50)
    currentSlowestAboveMid = calculateCurrentStreakLength(J.get(slowestK, "map")(_f25))
    def _f26(_k=J.undefined, *_args):
        return J.lt(_k, 50)
    currentSlowestBelowMid = calculateCurrentStreakLength(J.get(slowestK, "map")(_f26))
    def _f27(_slow=J.undefined, _slowest=J.undefined, _fast=J.undefined, *_args):
        if (J.gt(_slow, 50) and J.gt(_slowest, 50)):
            return ("Bullish Sentiment, Buy Zone" if J.lt(_fast, oversoldInput) else "Bullish Sentiment")
        elif (J.lt(_slow, 50) and J.lt(_slowest, 50)):
            return ("Bearish Sentiment, Sell Zone" if J.gt(_fast, overboughtInput) else "Bearish Sentiment")
        return "Neutral Sentiment"
    sentiment = G_for_every(slowK, slowestK, fastK, _f27)
    currentSentiment = J.get(sentiment, J.sub(J.get(sentiment, "length"), 1))
    def _f28(_k=J.undefined, _i=J.undefined, *_args):
        return (J.ge(currentFastAboveMid, fastAboveMid) if J.truthy(_t1 := J.gt(_k, 50)) else _t1)
    fastAboveAvgSignal = G_for_every(fastK, _f28)
    def _f29(_k=J.undefined, _i=J.undefined, *_args):
        return (J.ge(currentFastBelowMid, fastBelowMid) if J.truthy(_t1 := J.lt(_k, 50)) else _t1)
    fastBelowAvgSignal = G_for_every(fastK, _f29)
    def _f30(_k=J.undefined, _i=J.undefined, *_args):
        return (J.ge(currentSlowAboveMid, slowAboveMid) if J.truthy(_t1 := J.gt(_k, 50)) else _t1)
    slowAboveAvgSignal = G_for_every(slowK, _f30)
    def _f31(_k=J.undefined, _i=J.undefined, *_args):
        return (J.ge(currentSlowBelowMid, slowBelowMid) if J.truthy(_t1 := J.lt(_k, 50)) else _t1)
    slowBelowAvgSignal = G_for_every(slowK, _f31)
    def _f32(_k=J.undefined, _i=J.undefined, *_args):
        return (J.ge(currentSlowestAboveMid, slowestAboveMid) if J.truthy(_t1 := J.gt(_k, 50)) else _t1)
    slowestAboveAvgSignal = G_for_every(slowestK, _f32)
    def _f33(_k=J.undefined, _i=J.undefined, *_args):
        return (J.ge(currentSlowestBelowMid, slowestBelowMid) if J.truthy(_t1 := J.lt(_k, 50)) else _t1)
    slowestBelowAvgSignal = G_for_every(slowestK, _f33)
    plotSlowestK = G_paint(slowestK, J.obj(("name", "Slowest K"), ("color", "#E37222"), ("thickness", 2)))
    plotSlowestD = G_paint(slowestD, J.obj(("name", "Slowest D"), ("color", "#C95d10")))
    plotSlowK = G_paint(slowK, J.obj(("name", "Slow K"), ("color", "#E040FB"), ("thickness", 2)))
    plotSlowD = G_paint(slowD, J.obj(("name", "Slow D"), ("color", "#9E04B9")))
    plotFastK = G_paint(fastK, J.obj(("name", "Fast K"), ("color", "#00E676"), ("thickness", 2)))
    plotFastD = G_paint(fastD, J.obj(("name", "Fast D"), ("color", "#00A857")))
    G_fill(plotSlowestK, plotSlowestD, "#C95d10", 0.2, "Slowest Fill")
    G_fill(plotSlowK, plotSlowD, "#9E04B9", 0.2, "Slow Fill")
    G_fill(plotFastK, plotFastD, "#00A857", 0.2, "Fast Fill")
    plotOB = G_paint(G_horizontal_line(overboughtInput), J.obj(("name", "Overbought"), ("color", "#666666")))
    G_paint(G_horizontal_line(50), J.obj(("name", "Mid"), ("color", "#444444")))
    plotOS = G_paint(G_horizontal_line(oversoldInput), J.obj(("name", "Oversold"), ("color", "#666666")))
    G_fill(plotOB, plotOS, "#444444", 0.2, "Channel Fill")
    G_paint_overlay("Stochastic Stats", J.obj(("position", "center_right")), J.obj(("padding", "2.5em"), ("rows", (J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", J.template("Stochastic Mid Stats (", J.get(fastK, "length"), " Bars)")), ("color", "var(--text-color)"), ("colspan", 3), ("textAlign", "center"))]))), J.obj(("cells", J.JSArray([J.obj(("text", "Stoch"), ("color", "var(--text-color)"), ("paddingRight", "1.5em")), J.obj(("text", "Current"), ("color", "var(--text-color)"), ("paddingRight", "1.5em"), ("textAlign", "center")), J.obj(("text", "Averages"), ("color", "var(--text-color)"), ("textAlign", "center"))]))), createOverlayStochStatRow(currentFastAboveMid, currentFastBelowMid, fastAboveMid, fastBelowMid, "Fast", "#00E676"), createOverlayStochStatRow(currentSlowAboveMid, currentSlowBelowMid, slowAboveMid, slowBelowMid, "Slow", "#E040FB"), createOverlayStochStatRow(currentSlowestAboveMid, currentSlowestBelowMid, slowestAboveMid, slowestBelowMid, "Slowest", "#E37222"), J.obj(("cells", J.JSArray([J.obj(("text", J.template(currentSentiment)), ("color", "var(--text-color)"), ("colspan", 3), ("textAlign", "center"))])))]) if J.truthy(showStatsInput) else J.JSArray([])))))
    def _f34(_value=J.undefined, *_args):
        return J.seq(_value, True)
    G_register_signal(J.get(fastTrendLong, "map")(_f34), "Fast Trend Long")
    def _f35(_value=J.undefined, *_args):
        return J.seq(_value, True)
    G_register_signal(J.get(fastTrendShort, "map")(_f35), "Fast Trend Short")
    def _f36(_value=J.undefined, *_args):
        return J.seq(_value, True)
    G_register_signal(J.get(slowTrendLong, "map")(_f36), "Slow Trend Long")
    def _f37(_value=J.undefined, *_args):
        return J.seq(_value, True)
    G_register_signal(J.get(slowTrendShort, "map")(_f37), "Slow Trend Short")
    def _f38(_value=J.undefined, *_args):
        return J.seq(_value, True)
    G_register_signal(J.get(slowestTrendLong, "map")(_f38), "Slowest Trend Long")
    def _f39(_value=J.undefined, *_args):
        return J.seq(_value, True)
    G_register_signal(J.get(slowestTrendShort, "map")(_f39), "Slowest Trend Short")
    def _f40(_value=J.undefined, *_args):
        return J.seq(_value, True)
    G_register_signal(J.get(fastTrendBullish, "map")(_f40), "Fast Stoch Long")
    def _f41(_value=J.undefined, *_args):
        return J.seq(_value, True)
    G_register_signal(J.get(fastTrendBearish, "map")(_f41), "Fast Stoch Short")
    def _f42(_value=J.undefined, *_args):
        return J.seq(_value, True)
    G_register_signal(J.get(slowTrendBullish, "map")(_f42), "Slow Stoch Long")
    def _f43(_value=J.undefined, *_args):
        return J.seq(_value, True)
    G_register_signal(J.get(slowTrendBearish, "map")(_f43), "Slow Stoch Short")
    def _f44(_value=J.undefined, *_args):
        return J.seq(_value, True)
    G_register_signal(J.get(slowestTrendBullish, "map")(_f44), "Slowest Stoch Long")
    def _f45(_value=J.undefined, *_args):
        return J.seq(_value, True)
    G_register_signal(J.get(slowestTrendBearish, "map")(_f45), "Slowest Stoch Short")
    G_register_signal(fastAboveAvgSignal, "Fast Stoch At/Over Average Above Streak")
    G_register_signal(fastBelowAvgSignal, "Fast Stoch At/Over Average Below Streak")
    G_register_signal(slowAboveAvgSignal, "Slow Stoch At/Over Average Above Streak")
    G_register_signal(slowBelowAvgSignal, "Slow Stoch At/Over Average Below Streak")
    G_register_signal(slowestAboveAvgSignal, "Slowest Stoch At/Over Average Above Streak")
    G_register_signal(slowestBelowAvgSignal, "Slowest Stoch At/Over Average Below Streak")


register_store_indicator(
    script,
    name='triple_stochastic_rsi_TS',
    title='Triple Stochastic RSI',
    developer='Trade Seekers',
    url='https://trendspider.com/trading-tools-store/indicators/68a13a-triple-stochastic-rsi/',
    position='lower',
    inputs=[{'id': 'warmup', 'title': 'Warmup', 'type': 'number', 'default': '1000'}, {'id': 'k', 'title': 'K', 'type': 'number', 'default': 3}, {'id': 'd', 'title': 'D', 'type': 'number', 'default': 3}, {'id': 'rsi', 'title': 'RSI', 'type': 'number', 'default': 14}, {'id': '2nd_multi', 'title': '2nd Multi', 'type': 'number', 'default': 3}, {'id': '3rd_multi', 'title': '3rd Multi', 'type': 'number', 'default': 6}, {'id': 'overbought', 'title': 'Overbought', 'type': 'number', 'default': 80}, {'id': 'oversold', 'title': 'Oversold', 'type': 'number', 'default': 20}, {'id': 'show_stats_overlay_', 'title': 'Show Stats Overlay?', 'type': 'select_wide', 'default': 'Yes', 'options': ['Yes', 'No']}],
    outputs=['slowest_k', 'slowest_d', 'slow_k', 'slow_d', 'fast_k', 'fast_d', 'overbought', 'mid', 'oversold', 'fast_trend_long', 'fast_trend_short', 'slow_trend_long', 'slow_trend_short', 'slowest_trend_long', 'slowest_trend_short', 'fast_stoch_long', 'fast_stoch_short', 'slow_stoch_long', 'slow_stoch_short', 'slowest_stoch_long', 'slowest_stoch_short', 'fast_stoch_at_over_average_above_streak', 'fast_stoch_at_over_average_below_streak', 'slow_stoch_at_over_average_above_streak', 'slow_stoch_at_over_average_below_streak', 'slowest_stoch_at_over_average_above_streak', 'slowest_stoch_at_over_average_below_streak'],
    signals=['fast_trend_long', 'fast_trend_short', 'slow_trend_long', 'slow_trend_short', 'slowest_trend_long', 'slowest_trend_short', 'fast_stoch_long', 'fast_stoch_short', 'slow_stoch_long', 'slow_stoch_short', 'slowest_stoch_long', 'slowest_stoch_short', 'fast_stoch_at_over_average_above_streak', 'fast_stoch_at_over_average_below_streak', 'slow_stoch_at_over_average_above_streak', 'slow_stoch_at_over_average_below_streak', 'slowest_stoch_at_over_average_above_streak', 'slowest_stoch_at_over_average_below_streak'],
    requires=[],
    parity='exact',
)
