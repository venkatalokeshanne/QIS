"""
Multi-Timeframe High/Low Levels -- TrendSpider store indicator by TrendSpider Team.

Registered as "multi_timeframe_high_low_levels_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/multi-timeframe-high-low-levels/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Infinity = G["Infinity"]
    G_Math = G["Math"]
    G_bar_at = G["bar_at"]
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_high = G["high"]
    G_input = G["input"]
    G_low = G["low"]
    G_paint = G["paint"]
    G_paint_label_at_line = G["paint_label_at_line"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    G_describe_indicator("Multi-Timeframe High/Low Levels")
    showDaily = J.get(G_input, "boolean")("Show Daily Levels", True)
    showWeekly = J.get(G_input, "boolean")("Show Weekly Levels", True)
    showMonthly = J.get(G_input, "boolean")("Show Monthly Levels", True)
    showYearly = J.get(G_input, "boolean")("Show Yearly Levels", True)
    show52Week = J.get(G_input, "boolean")("Show 52 Week Levels", True)
    def calculateHighLow(timeframe=J.undefined, *_args):
        myHigh = G_series_of(None)
        myLow = G_series_of(None)
        lastPeriod = None
        i = 0
        while J.lt(i, J.get(G_time, "length")):
            currentPeriod = J.undefined
            if J.seq(timeframe, "day"):
                currentPeriod = J.get(G_bar_at(J.get(G_time, i)), "session")
            elif J.seq(timeframe, "week"):
                currentPeriod = J.get(G_bar_at(J.get(G_time, i), "W"), "session")
            elif J.seq(timeframe, "month"):
                currentPeriod = J.get(G_bar_at(J.get(G_time, i), "M"), "session")
            elif J.seq(timeframe, "year"):
                currentPeriod = J.get(G_bar_at(J.get(G_time, i), "Y"), "session")
            if J.sne(currentPeriod, lastPeriod):
                J.set(myHigh, i, J.get(G_high, i))
                J.set(myLow, i, J.get(G_low, i))
            else:
                J.set(myHigh, i, J.get(G_Math, "max")(J.get(myHigh, J.sub(i, 1)), J.get(G_high, i)))
                J.set(myLow, i, J.get(G_Math, "min")(J.get(myLow, J.sub(i, 1)), J.get(G_low, i)))
            lastPeriod = currentPeriod
            i = J.inc(i)
        return J.obj(("high", myHigh), ("low", myLow))
    dailyLevels = calculateHighLow("day")
    weeklyLevels = calculateHighLow("week")
    monthlyLevels = calculateHighLow("month")
    yearlyLevels = calculateHighLow("year")
    def calculate52WeekLevels(*_args):
        myHigh = G_series_of(None)
        myLow = G_series_of(None)
        period = J.mul(J.mul(J.mul(J.mul(52, 7), 24), 60), 60)
        i = 0
        while J.lt(i, J.get(G_time, "length")):
            startTime = J.sub(J.get(G_time, i), period)
            periodHigh = J.neg(G_Infinity)
            periodLow = G_Infinity
            j = J.get(G_Math, "max")(0, J.sub(i, 365))
            while J.le(j, i):
                if J.ge(J.get(G_time, j), startTime):
                    periodHigh = J.get(G_Math, "max")(periodHigh, J.get(G_high, j))
                    periodLow = J.get(G_Math, "min")(periodLow, J.get(G_low, j))
                j = J.inc(j)
            J.set(myHigh, i, periodHigh)
            J.set(myLow, i, periodLow)
            i = J.inc(i)
        return J.obj(("high", myHigh), ("low", myLow))
    week52Levels = calculate52WeekLevels()
    if J.truthy(showDaily):
        dailyHighLine = G_paint(J.get(dailyLevels, "high"), J.obj(("name", "Daily High"), ("color", "lightblue"), ("style", "ladder")))
        dailyLowLine = G_paint(J.get(dailyLevels, "low"), J.obj(("name", "Daily Low"), ("color", "lightblue"), ("style", "ladder")))
        G_paint_label_at_line(dailyHighLine, J.sub(J.get(G_close, "length"), 1), "Daily High", J.obj(("color", "lightblue")))
        G_paint_label_at_line(dailyLowLine, J.sub(J.get(G_close, "length"), 1), "Daily Low", J.obj(("color", "lightblue")))
    if J.truthy(showWeekly):
        weeklyHighLine = G_paint(J.get(weeklyLevels, "high"), J.obj(("name", "Weekly High"), ("color", "blue"), ("style", "ladder")))
        weeklyLowLine = G_paint(J.get(weeklyLevels, "low"), J.obj(("name", "Weekly Low"), ("color", "blue"), ("style", "ladder")))
        G_paint_label_at_line(weeklyHighLine, J.sub(J.get(G_close, "length"), 1), "Weekly High", J.obj(("color", "blue")))
        G_paint_label_at_line(weeklyLowLine, J.sub(J.get(G_close, "length"), 1), "Weekly Low", J.obj(("color", "blue")))
    if J.truthy(showMonthly):
        monthlyHighLine = G_paint(J.get(monthlyLevels, "high"), J.obj(("name", "Monthly High"), ("color", "green"), ("style", "ladder")))
        monthlyLowLine = G_paint(J.get(monthlyLevels, "low"), J.obj(("name", "Monthly Low"), ("color", "green"), ("style", "ladder")))
        G_paint_label_at_line(monthlyHighLine, J.sub(J.get(G_close, "length"), 1), "Monthly High", J.obj(("color", "green")))
        G_paint_label_at_line(monthlyLowLine, J.sub(J.get(G_close, "length"), 1), "Monthly Low", J.obj(("color", "green")))
    if J.truthy(showYearly):
        yearlyHighLine = G_paint(J.get(yearlyLevels, "high"), J.obj(("name", "Yearly High"), ("color", "red"), ("style", "ladder")))
        yearlyLowLine = G_paint(J.get(yearlyLevels, "low"), J.obj(("name", "Yearly Low"), ("color", "red"), ("style", "ladder")))
        G_paint_label_at_line(yearlyHighLine, J.sub(J.get(G_close, "length"), 1), "Yearly High", J.obj(("color", "red")))
        G_paint_label_at_line(yearlyLowLine, J.sub(J.get(G_close, "length"), 1), "Yearly Low", J.obj(("color", "red")))
    if J.truthy(show52Week):
        week52HighLine = G_paint(J.get(week52Levels, "high"), J.obj(("name", "52 Week High"), ("color", "purple"), ("style", "ladder")))
        week52LowLine = G_paint(J.get(week52Levels, "low"), J.obj(("name", "52 Week Low"), ("color", "purple"), ("style", "ladder")))
        G_paint_label_at_line(week52HighLine, J.sub(J.get(G_close, "length"), 1), "52 Week High", J.obj(("color", "purple")))
        G_paint_label_at_line(week52LowLine, J.sub(J.get(G_close, "length"), 1), "52 Week Low", J.obj(("color", "purple")))


register_store_indicator(
    script,
    name='multi_timeframe_high_low_levels_TS',
    title='Multi-Timeframe High/Low Levels',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/multi-timeframe-high-low-levels/',
    position='price',
    inputs=[{'id': 'show_daily_levels', 'title': 'Show Daily Levels', 'type': 'boolean', 'default': True}, {'id': 'show_weekly_levels', 'title': 'Show Weekly Levels', 'type': 'boolean', 'default': True}, {'id': 'show_monthly_levels', 'title': 'Show Monthly Levels', 'type': 'boolean', 'default': True}, {'id': 'show_yearly_levels', 'title': 'Show Yearly Levels', 'type': 'boolean', 'default': True}, {'id': 'show_52_week_levels', 'title': 'Show 52 Week Levels', 'type': 'boolean', 'default': True}],
    outputs=['daily_high', 'daily_low', 'weekly_high', 'weekly_low', 'monthly_high', 'monthly_low', 'yearly_high', 'yearly_low', '52_week_high', '52_week_low'],
    signals=[],
    requires=[],
    parity='exact',
)
