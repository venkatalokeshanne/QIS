"""
Candle Streak Analysis -- TrendSpider store indicator by QXEM.

Registered as "candle_streak_analysis_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/689aad-candle-streak-analysis/)
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
    G_open = G["open"]
    G_paint_overlay = G["paint_overlay"]
    G_describe_indicator("Candle Streak Analysis")
    def computeStats(*_args):
        totalCandles = J.get(G_close, "length")
        redCandles = 0
        greenCandles = 0
        currentRedStreak = 0
        currentGreenStreak = 0
        maxRedStreak = 0
        maxGreenStreak = 0
        redStreaks = J.JSArray([])
        greenStreaks = J.JSArray([])
        redStreakCount = 0
        greenStreakCount = 0
        i = 0
        while J.lt(i, totalCandles):
            if J.lt(J.get(G_close, i), J.get(G_open, i)):
                redCandles = J.inc(redCandles)
                currentRedStreak = J.inc(currentRedStreak)
                if J.seq(currentRedStreak, 2):
                    redStreakCount = J.inc(redStreakCount)
                if J.gt(currentGreenStreak, 1):
                    J.get(greenStreaks, "push")(currentGreenStreak)
                currentGreenStreak = 0
                maxRedStreak = J.get(G_Math, "max")(maxRedStreak, currentRedStreak)
            elif J.gt(J.get(G_close, i), J.get(G_open, i)):
                greenCandles = J.inc(greenCandles)
                currentGreenStreak = J.inc(currentGreenStreak)
                if J.seq(currentGreenStreak, 2):
                    greenStreakCount = J.inc(greenStreakCount)
                if J.gt(currentRedStreak, 1):
                    J.get(redStreaks, "push")(currentRedStreak)
                currentRedStreak = 0
                maxGreenStreak = J.get(G_Math, "max")(maxGreenStreak, currentGreenStreak)
            else:
                if J.gt(currentRedStreak, 1):
                    J.get(redStreaks, "push")(currentRedStreak)
                if J.gt(currentGreenStreak, 1):
                    J.get(greenStreaks, "push")(currentGreenStreak)
                currentRedStreak = 0
                currentGreenStreak = 0
            i = J.inc(i)
        if J.gt(currentRedStreak, 1):
            J.get(redStreaks, "push")(currentRedStreak)
        if J.gt(currentGreenStreak, 1):
            J.get(greenStreaks, "push")(currentGreenStreak)
        redPercent = J.get(J.mul(J.div(redCandles, totalCandles), 100), "toFixed")(2)
        greenPercent = J.get(J.mul(J.div(greenCandles, totalCandles), 100), "toFixed")(2)
        def _f1(a=J.undefined, b=J.undefined, *_args):
            return J.add(a, b)
        avgRedStreak = (J.get(J.div(J.get(redStreaks, "reduce")(_f1, 0), J.get(redStreaks, "length")), "toFixed")(2) if J.gt(J.get(redStreaks, "length"), 0) else "0.00")
        def _f2(a=J.undefined, b=J.undefined, *_args):
            return J.add(a, b)
        avgGreenStreak = (J.get(J.div(J.get(greenStreaks, "reduce")(_f2, 0), J.get(greenStreaks, "length")), "toFixed")(2) if J.gt(J.get(greenStreaks, "length"), 0) else "0.00")
        return J.obj(("totalCandles", totalCandles), ("redPercent", redPercent), ("greenPercent", greenPercent), ("maxRedStreak", maxRedStreak), ("maxGreenStreak", maxGreenStreak), ("avgRedStreak", avgRedStreak), ("avgGreenStreak", avgGreenStreak), ("redStreakCount", redStreakCount), ("greenStreakCount", greenStreakCount))
    stats = computeStats()
    G_paint_overlay("CandleAnalysis", J.obj(("position", "bottom_left"), ("offset_x", 20), ("offset_y", (-50))), J.obj(("rows", J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", "Candle Streak Analysis"), ("color", "var(--text-color)"))]))), J.obj(("cells", J.JSArray([J.obj(("text", J.template("Total Candles: ", J.get(stats, "totalCandles"))), ("color", "var(--text-color)"))]))), J.obj(("cells", J.JSArray([J.obj(("text", J.template("Red Candles: ", J.get(stats, "redPercent"), "%")), ("color", "red"))]))), J.obj(("cells", J.JSArray([J.obj(("text", J.template("Green Candles: ", J.get(stats, "greenPercent"), "%")), ("color", "green"))]))), J.obj(("cells", J.JSArray([J.obj(("text", J.template("Max Red Streak: ", J.get(stats, "maxRedStreak"))), ("color", "red"))]))), J.obj(("cells", J.JSArray([J.obj(("text", J.template("Max Green Streak: ", J.get(stats, "maxGreenStreak"))), ("color", "green"))]))), J.obj(("cells", J.JSArray([J.obj(("text", J.template("Red Streaks (>1): ", J.get(stats, "redStreakCount"))), ("color", "red"))]))), J.obj(("cells", J.JSArray([J.obj(("text", J.template("Green Streaks (>1): ", J.get(stats, "greenStreakCount"))), ("color", "green"))]))), J.obj(("cells", J.JSArray([J.obj(("text", J.template("Avg Red Streak: ", J.get(stats, "avgRedStreak"))), ("color", "red"))]))), J.obj(("cells", J.JSArray([J.obj(("text", J.template("Avg Green Streak: ", J.get(stats, "avgGreenStreak"))), ("color", "green"))])))]))))


register_store_indicator(
    script,
    name='candle_streak_analysis_TS',
    title='Candle Streak Analysis',
    developer='QXEM',
    url='https://trendspider.com/trading-tools-store/indicators/689aad-candle-streak-analysis/',
    position='price',
    inputs=[],
    outputs=[],
    signals=[],
    requires=[],
    parity='exact',
)
