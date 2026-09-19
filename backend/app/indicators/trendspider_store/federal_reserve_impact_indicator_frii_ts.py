"""
Federal Reserve Impact Indicator (FRII) -- TrendSpider store indicator by Aliu Kehinde.

Registered as "federal_reserve_impact_indicator_frii_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68aa79-federal-reserve-impact-indicator-frii/)
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
    G_color_cloud = G["color_cloud"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_input = G["input"]
    G_paint = G["paint"]
    G_paint_overlay = G["paint_overlay"]
    G_register_signal = G["register_signal"]
    G_series_of = G["series_of"]
    def fetchEconomicData(seriesId=J.undefined, *_args):
        try:
            simulatedData = G_series_of(None)
            i = 0
            while J.lt(i, J.get(G_close, "length")):
                if J.seq(seriesId, fedFundsId):
                    J.set(simulatedData, i, J.add(4.5, J.mul(J.get(G_Math, "sin")(J.div(i, 100)), 1)))
                elif J.seq(seriesId, gdpId):
                    J.set(simulatedData, i, J.add(1, J.mul(J.get(G_Math, "sin")(J.div(i, 200)), 3)))
                elif J.seq(seriesId, unemploymentId):
                    J.set(simulatedData, i, J.add(4.5, J.mul(J.get(G_Math, "cos")(J.div(i, 150)), 1.5)))
                elif J.seq(seriesId, inflationId):
                    J.set(simulatedData, i, J.add(3.5, J.mul(J.get(G_Math, "sin")(J.div(i, 120)), 2.5)))
                i = J.inc(i)
            return simulatedData
        except Exception as _e1:
            error = J.catch_value(_e1)
            raise J.js_throw(J.template("Error fetching ", seriesId, ": ", error))
    G_describe_indicator("Federal Reserve Impact Indicator (FRII)", "lower", J.obj(("shortName", "FRII")))
    economicDataWeight = J.get(G_input, "number")("Economic Data Weight %", 40, J.obj(("min", 10), ("max", 90), ("step", 5)))
    momentumPeriod = J.get(G_input, "number")("Momentum Period", 20, J.obj(("min", 10), ("max", 50), ("step", 1)))
    signalThreshold = J.get(G_input, "number")("Signal Threshold", 2, J.obj(("min", 1), ("max", 5), ("step", 0.1)))
    fedFundsId = "FEDFUNDS"
    gdpId = "GDP"
    unemploymentId = "UNRATE"
    inflationId = "CPIAUCSL"
    accommodativeColor = "#08998120"
    restrictiveColor = "#F2364520"
    oscillatorColor = "#5D3FD3"
    buySignalColor = "#089981"
    sellSignalColor = "#F23645"
    fedFundsRate = fetchEconomicData(fedFundsId)
    gdpGrowth = fetchEconomicData(gdpId)
    unemploymentRate = fetchEconomicData(unemploymentId)
    inflationRate = fetchEconomicData(inflationId)
    def normalizeSeries(series=J.undefined, _p1=J.undefined, *_args):
        _t2 = _p1
        if _t2 is J.undefined:
            _t2 = False
        invert = _t2
        minVal = 0
        maxVal = 10
        def _f3(val=J.undefined, *_args):
            if (val is None):
                return 50
            normalized = J.mul(J.div(J.sub(val, minVal), J.sub(maxVal, minVal)), 100)
            normalized = J.get(G_Math, "max")(0, J.get(G_Math, "min")(100, normalized))
            return (J.sub(100, normalized) if J.truthy(invert) else normalized)
        return G_for_every(series, _f3)
    normFedFunds = normalizeSeries(fedFundsRate, True)
    normGDP = normalizeSeries(gdpGrowth, False)
    normUnemployment = normalizeSeries(unemploymentRate, True)
    normInflation = normalizeSeries(inflationRate, True)
    def _f1(ff=J.undefined, gdp=J.undefined, unemp=J.undefined, inf=J.undefined, *_args):
        if ((((ff is None) or (gdp is None)) or (unemp is None)) or (inf is None)):
            return 50
        return J.add(J.add(J.add(J.mul(ff, 0.3), J.mul(gdp, 0.3)), J.mul(unemp, 0.2)), J.mul(inf, 0.2))
    economicScore = G_for_every(normFedFunds, normGDP, normUnemployment, normInflation, _f1)
    def _f2(c=J.undefined, i=J.undefined, *_args):
        if J.lt(i, momentumPeriod):
            return 50
        pastClose = J.get(G_close, J.sub(i, momentumPeriod))
        if ((pastClose is None) or (c is None)):
            return 50
        return J.add(J.mul(J.div(J.sub(c, pastClose), pastClose), 100), 50)
    priceMomentum = G_for_every(G_close, _f2)
    def _f3(econ=J.undefined, mom=J.undefined, *_args):
        if ((econ is None) or (mom is None)):
            return 50
        econWeight = J.div(economicDataWeight, 100)
        momWeight = J.sub(1, econWeight)
        return J.add(J.mul(econ, econWeight), J.mul(mom, momWeight))
    compositeOscillator = G_for_every(economicScore, priceMomentum, _f3)
    bullSignal = G_series_of(None)
    bearSignal = G_series_of(None)
    i = 1
    while J.lt(i, J.get(compositeOscillator, "length")):
        currentValue = J.get(compositeOscillator, i)
        previousValue = J.get(compositeOscillator, J.sub(i, 1))
        if ((currentValue is not None) and (previousValue is not None)):
            if ((J.lt(previousValue, 50) and J.ge(currentValue, 50)) and J.gt(J.sub(currentValue, previousValue), signalThreshold)):
                J.set(bullSignal, i, currentValue)
            if ((J.gt(previousValue, 50) and J.le(currentValue, 50)) and J.gt(J.sub(previousValue, currentValue), signalThreshold)):
                J.set(bearSignal, i, currentValue)
        i = J.inc(i)
    oscLine = G_paint(compositeOscillator, J.obj(("name", "FRII Oscillator"), ("color", oscillatorColor), ("thickness", 2)))
    def _f4(score=J.undefined, *_args):
        if (score is None):
            return 0
        return (1 if J.gt(score, 60) else ((-1) if J.lt(score, 40) else 0))
    policyStance = G_for_every(economicScore, _f4)
    upperBound = G_series_of(100)
    lowerBound = G_series_of(0)
    G_color_cloud(upperBound, compositeOscillator, accommodativeColor, restrictiveColor)
    G_paint(bullSignal, J.obj(("name", "Bullish Signal"), ("color", buySignalColor), ("style", "labels_above")))
    G_paint(bearSignal, J.obj(("name", "Bearish Signal"), ("color", sellSignalColor), ("style", "labels_below")))
    lastFedFunds = J.get(fedFundsRate, J.sub(J.get(fedFundsRate, "length"), 1))
    lastGDP = J.get(gdpGrowth, J.sub(J.get(gdpGrowth, "length"), 1))
    lastUnemployment = J.get(unemploymentRate, J.sub(J.get(unemploymentRate, "length"), 1))
    lastInflation = J.get(inflationRate, J.sub(J.get(inflationRate, "length"), 1))
    G_paint_overlay("Economic Data", J.obj(("position", "top_left")), J.obj(("rows", J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", "Economic Indicator"), ("color", "white"), ("background", "#2C2C2C"), ("align", "left"), ("width", "50%")), J.obj(("text", "Current Value"), ("color", "white"), ("background", "#2C2C2C"), ("align", "center"), ("width", "50%"))]))), J.obj(("cells", J.JSArray([J.obj(("text", "Fed Funds Rate"), ("color", "var(--text-color)"), ("align", "left"), ("width", "50%")), J.obj(("text", (J.template(J.get(lastFedFunds, "toFixed")(2), "%") if J.truthy(lastFedFunds) else "N/A")), ("color", "var(--text-color)"), ("align", "center"), ("width", "50%"))]))), J.obj(("cells", J.JSArray([J.obj(("text", "GDP Growth"), ("color", "var(--text-color)"), ("align", "left"), ("width", "50%")), J.obj(("text", (J.template(J.get(lastGDP, "toFixed")(2), "%") if J.truthy(lastGDP) else "N/A")), ("color", "var(--text-color)"), ("align", "center"), ("width", "50%"))]))), J.obj(("cells", J.JSArray([J.obj(("text", "Unemployment"), ("color", "var(--text-color)"), ("align", "left"), ("width", "50%")), J.obj(("text", (J.template(J.get(lastUnemployment, "toFixed")(2), "%") if J.truthy(lastUnemployment) else "N/A")), ("color", "var(--text-color)"), ("align", "center"), ("width", "50%"))]))), J.obj(("cells", J.JSArray([J.obj(("text", "Inflation"), ("color", "var(--text-color)"), ("align", "left"), ("width", "50%")), J.obj(("text", (J.template(J.get(lastInflation, "toFixed")(2), "%") if J.truthy(lastInflation) else "N/A")), ("color", "var(--text-color)"), ("align", "center"), ("width", "50%"))])))]))))
    G_register_signal(bullSignal, "FRII Bullish Signal")
    G_register_signal(bearSignal, "FRII Bearish Signal")


register_store_indicator(
    script,
    name='federal_reserve_impact_indicator_frii_TS',
    title='Federal Reserve Impact Indicator (FRII)',
    developer='Aliu Kehinde',
    url='https://trendspider.com/trading-tools-store/indicators/68aa79-federal-reserve-impact-indicator-frii/',
    position='lower',
    inputs=[{'id': 'economic_data_weight__', 'title': 'Economic Data Weight %', 'type': 'number', 'default': 40}, {'id': 'momentum_period', 'title': 'Momentum Period', 'type': 'number', 'default': 20}, {'id': 'signal_threshold', 'title': 'Signal Threshold', 'type': 'number', 'default': 2}],
    outputs=['frii_oscillator', 'line_2', 'line_3', 'line_5', 'line_6', 'bullish_signal', 'bearish_signal', 'frii_bullish_signal', 'frii_bearish_signal'],
    signals=['frii_bullish_signal', 'frii_bearish_signal'],
    requires=[],
    parity='exact',
)
