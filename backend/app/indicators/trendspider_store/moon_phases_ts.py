"""
Moon Phases -- TrendSpider store indicator by TrendSpider Team.

Registered as "moon_phases_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/moon-phases/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_describe_indicator = G["describe_indicator"]
    G_library = G["library"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    def getMoonPhase(julianDate=J.undefined, *_args):
        knownNewMoon = 2451550.1
        synodicMonth = 29.53058867
        daysSinceNewMoon = J.sub(julianDate, knownNewMoon)
        newMoons = J.get(G_Math, "floor")(J.div(daysSinceNewMoon, synodicMonth))
        phase = J.sub(daysSinceNewMoon, J.mul(newMoons, synodicMonth))
        return J.div(phase, synodicMonth)
    def toJulianDate(timestamp=J.undefined, *_args):
        date = J.get(moment, "tz")(J.mul(timestamp, 1000), "UTC")
        year = J.get(date, "year")()
        month = J.add(J.get(date, "month")(), 1)
        day = J.get(date, "date")()
        hours = J.get(date, "hours")()
        minutes = J.get(date, "minutes")()
        seconds = J.get(date, "seconds")()
        a = J.get(G_Math, "floor")(J.div(J.sub(14, month), 12))
        y = J.sub(J.add(year, 4800), a)
        m = J.sub(J.add(month, J.mul(12, a)), 3)
        jd = J.sub(J.add(J.sub(J.add(J.add(J.add(day, J.get(G_Math, "floor")(J.div(J.add(J.mul(153, m), 2), 5))), J.mul(365, y)), J.get(G_Math, "floor")(J.div(y, 4))), J.get(G_Math, "floor")(J.div(y, 100))), J.get(G_Math, "floor")(J.div(y, 400))), 32045)
        dayFraction = J.div(J.add(J.add(hours, J.div(minutes, 60)), J.div(seconds, 3600)), 24)
        return J.add(jd, dayFraction)
    G_describe_indicator("Moon Phases", "price", J.obj(("shortName", "Moon Phases")))
    moment = G_library("moment-timezone")
    symbols = G_series_of(None)
    newMoonSignal = G_series_of(False)
    firstQuarterSignal = G_series_of(False)
    fullMoonSignal = G_series_of(False)
    lastQuarterSignal = G_series_of(False)
    previousPhase = None
    i = 0
    while J.lt(i, J.get(G_time, "length")):
        julianDate = toJulianDate(J.get(G_time, i))
        moonPhase = getMoonPhase(julianDate)
        if ((previousPhase is None) or J.sne(J.get(G_Math, "floor")(J.mul(previousPhase, 8)), J.get(G_Math, "floor")(J.mul(moonPhase, 8)))):
            symbol = J.undefined
            if (J.lt(moonPhase, 0.025) or J.ge(moonPhase, 0.975)):
                symbol = "\ud83c\udf11"
                J.set(newMoonSignal, i, True)
            elif (J.ge(moonPhase, 0.025) and J.lt(moonPhase, 0.225)):
                symbol = "\ud83c\udf12"
            elif (J.ge(moonPhase, 0.225) and J.lt(moonPhase, 0.275)):
                symbol = "\ud83c\udf13"
                J.set(firstQuarterSignal, i, True)
            elif (J.ge(moonPhase, 0.275) and J.lt(moonPhase, 0.475)):
                symbol = "\ud83c\udf14"
            elif (J.ge(moonPhase, 0.475) and J.lt(moonPhase, 0.525)):
                symbol = "\ud83c\udf15"
                J.set(fullMoonSignal, i, True)
            elif (J.ge(moonPhase, 0.525) and J.lt(moonPhase, 0.725)):
                symbol = "\ud83c\udf16"
            elif (J.ge(moonPhase, 0.725) and J.lt(moonPhase, 0.775)):
                symbol = "\ud83c\udf17"
                J.set(lastQuarterSignal, i, True)
            elif (J.ge(moonPhase, 0.775) and J.lt(moonPhase, 0.975)):
                symbol = "\ud83c\udf18"
            J.set(symbols, i, symbol)
        previousPhase = moonPhase
        i = J.inc(i)
    G_paint(symbols, J.obj(("name", "Moon Phase"), ("style", "labels_above"), ("color", "white"), ("thickness", 1)))
    G_register_signal(newMoonSignal, "New Moon")
    G_register_signal(firstQuarterSignal, "First Quarter Moon")
    G_register_signal(fullMoonSignal, "Full Moon")
    G_register_signal(lastQuarterSignal, "Last Quarter Moon")


register_store_indicator(
    script,
    name='moon_phases_TS',
    title='Moon Phases',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/moon-phases/',
    position='price',
    inputs=[],
    outputs=['moon_phase', 'new_moon', 'first_quarter_moon', 'full_moon', 'last_quarter_moon'],
    signals=['new_moon', 'first_quarter_moon', 'full_moon', 'last_quarter_moon'],
    requires=[],
    parity='exact',
)
