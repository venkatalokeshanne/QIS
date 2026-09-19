"""
Cross-Asset Momentum Divergence -- TrendSpider store indicator by Grant Pratt.

Registered as "cross_asset_momentum_divergence_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68ab23-cross-asset-momentum-divergence/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
aapl_d: MISMATCH, syn_5m: MISMATCH.

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
    G_input = G["input"]
    G_paint = G["paint"]
    G_series_of = G["series_of"]
    G_sliding_window_function = G["sliding_window_function"]
    G_time = G["time"]
    G_describe_indicator("Cross-Asset Momentum Divergence", "lower", J.obj(("shortName", "CAMD"), ("decimals", 2)))
    momentumPeriod = J.get(G_input, "number")("Momentum Period", 20, J.obj(("min", 5), ("max", 50), ("step", 1)))
    divergenceThreshold = J.get(G_input, "number")("Divergence Threshold", 0.75, J.obj(("min", 0.3), ("max", 1.5), ("step", 0.05)))
    bondYieldSymbol = J.get(G_input, "text")("Bond Yield Symbol", "TNX")
    vixSymbol = J.get(G_input, "text")("VIX Symbol", "VIX")
    dollarIndexSymbol = J.get(G_input, "text")("Dollar Index Symbol", "DXY")
    goldSymbol = J.get(G_input, "text")("Gold Symbol", "GLD")
    oilSymbol = J.get(G_input, "text")("Oil Symbol", "USO")
    enableRotationSignals = J.get(G_input, "boolean")("Enable Rotation Signals", True)
    primaryMomentum = G_series_of(0)
    bondImpact = G_series_of(0)
    currencyImpact = G_series_of(0)
    commodityImpact = G_series_of(0)
    vixDivergence = G_series_of(0)
    rotationSignal = G_series_of(0)
    divergenceStrength = G_series_of(0)
    def _f1(_t=J.undefined, *_args):
        myBaseValue = 2.5
        myNoise = J.mul(J.sub(J.get(G_Math, "random")(), 0.5), 0.1)
        myTrend = J.mul(J.get(G_Math, "sin")(J.mul(_t, 0.0001)), 0.05)
        return J.mul(myBaseValue, J.add(J.add(1, myTrend), myNoise))
    simulatedBondYield = G_for_every(G_time, _f1)
    def _f2(_t=J.undefined, *_args):
        myBaseValue = 20
        myNoise = J.mul(J.sub(J.get(G_Math, "random")(), 0.5), 0.2)
        myTrend = J.mul(J.get(G_Math, "sin")(J.add(J.mul(_t, 0.0001), 1)), 0.1)
        return J.mul(myBaseValue, J.add(J.add(1, myTrend), myNoise))
    simulatedVIX = G_for_every(G_time, _f2)
    def _f3(_t=J.undefined, *_args):
        myBaseValue = 100
        myNoise = J.mul(J.sub(J.get(G_Math, "random")(), 0.5), 0.05)
        myTrend = J.mul(J.get(G_Math, "sin")(J.add(J.mul(_t, 0.0001), 2)), 0.03)
        return J.mul(myBaseValue, J.add(J.add(1, myTrend), myNoise))
    simulatedDXY = G_for_every(G_time, _f3)
    def _f4(_t=J.undefined, *_args):
        myBaseValue = 2000
        myNoise = J.mul(J.sub(J.get(G_Math, "random")(), 0.5), 0.05)
        myTrend = J.mul(J.get(G_Math, "sin")(J.add(J.mul(_t, 0.0001), 3)), 0.02)
        return J.mul(myBaseValue, J.add(J.add(1, myTrend), myNoise))
    simulatedGold = G_for_every(G_time, _f4)
    def _f5(_t=J.undefined, *_args):
        myBaseValue = 80
        myNoise = J.mul(J.sub(J.get(G_Math, "random")(), 0.5), 0.1)
        myTrend = J.mul(J.get(G_Math, "sin")(J.add(J.mul(_t, 0.0001), 4)), 0.05)
        return J.mul(myBaseValue, J.add(J.add(1, myTrend), myNoise))
    simulatedOil = G_for_every(G_time, _f5)
    def _f6(_values=J.undefined, *_args):
        if J.lt(J.get(_values, "length"), 2):
            return 0
        myCurrentPrice = J.get(_values, J.sub(J.get(_values, "length"), 1))
        myPastPrice = J.get(_values, 0)
        return J.mul(J.div(J.sub(myCurrentPrice, myPastPrice), myPastPrice), 100)
    equityMomentum = G_sliding_window_function(G_close, momentumPeriod, _f6)
    def _f7(_values=J.undefined, *_args):
        if J.lt(J.get(_values, "length"), 2):
            return 0
        myCurrentYield = J.get(_values, J.sub(J.get(_values, "length"), 1))
        myPastYield = J.get(_values, 0)
        myYieldChange = J.mul(J.div(J.sub(myCurrentYield, myPastYield), myPastYield), 100)
        myYieldImpactFactor = (-0.5)
        return J.mul(myYieldChange, myYieldImpactFactor)
    bondYieldImpact = G_sliding_window_function(simulatedBondYield, momentumPeriod, _f7)
    def _f8(_values=J.undefined, *_args):
        if J.lt(J.get(_values, "length"), 2):
            return 0
        myCurrentDXY = J.get(_values, J.sub(J.get(_values, "length"), 1))
        myPastDXY = J.get(_values, 0)
        myDollarMomentum = J.mul(J.div(J.sub(myCurrentDXY, myPastDXY), myPastDXY), 100)
        myCurrencyImpactFactor = (-0.3)
        return J.mul(myDollarMomentum, myCurrencyImpactFactor)
    dollarImpact = G_sliding_window_function(simulatedDXY, momentumPeriod, _f8)
    def _f9(_gold=J.undefined, _oil=J.undefined, *_args):
        myGoldMomentumApprox = J.mul(J.get(G_Math, "sin")(J.div(_gold, 100)), 5)
        myOilMomentumApprox = J.mul(J.get(G_Math, "sin")(J.div(_oil, 10)), 3)
        myCommodityImpact = 0
        myCommodityImpact = J.add(myCommodityImpact, J.mul(myGoldMomentumApprox, 0.2))
        myCommodityImpact = J.add(myCommodityImpact, J.mul(myOilMomentumApprox, (-0.1)))
        return myCommodityImpact
    commodityImpactCalc = G_for_every(simulatedGold, simulatedOil, _f9)
    def _f10(_equityMom=J.undefined, _vixLevel=J.undefined, *_args):
        myVixMomentumApprox = J.mul(J.neg(J.get(G_Math, "sin")(J.div(_vixLevel, 5))), 10)
        myActualDivergence = J.sub(_equityMom, myVixMomentumApprox)
        return J.div(myActualDivergence, 10)
    vixDivergenceCalc = G_for_every(equityMomentum, simulatedVIX, _f10)
    def _f11(_equityMom=J.undefined, _bondImp=J.undefined, _currImp=J.undefined, *_args):
        if (not J.truthy(enableRotationSignals)):
            return 0
        myRotationScore = 0
        if J.lt(_bondImp, (-2)):
            myRotationScore = J.add(myRotationScore, 2)
        if J.gt(_bondImp, 2):
            myRotationScore = J.sub(myRotationScore, 2)
        if J.lt(_currImp, (-1)):
            myRotationScore = J.add(myRotationScore, 1)
        if J.gt(_currImp, 1):
            myRotationScore = J.sub(myRotationScore, 1)
        if J.gt(J.get(G_Math, "abs")(_equityMom), 5):
            myRotationScore = J.add(myRotationScore, (1 if J.gt(_equityMom, 0) else (-1)))
        return myRotationScore
    rotationSignalCalc = G_for_every(equityMomentum, bondYieldImpact, dollarImpact, _f11)
    def _f12(_bondImp=J.undefined, _currImp=J.undefined, _commImp=J.undefined, _vixDiv=J.undefined, *_args):
        myImpacts = J.JSArray([_bondImp, _currImp, _commImp, _vixDiv])
        def _f1(sum=J.undefined, val=J.undefined, *_args):
            return J.add(sum, val)
        myMean = J.div(J.get(myImpacts, "reduce")(_f1, 0), J.get(myImpacts, "length"))
        def _f2(sum=J.undefined, val=J.undefined, *_args):
            return J.add(sum, J.get(G_Math, "pow")(J.sub(val, myMean), 2))
        myVariance = J.div(J.get(myImpacts, "reduce")(_f2, 0), J.get(myImpacts, "length"))
        myStdDev = J.get(G_Math, "sqrt")(myVariance)
        return J.get(G_Math, "min")(J.div(myStdDev, divergenceThreshold), 2)
    divergenceStrengthCalc = G_for_every(bondYieldImpact, dollarImpact, commodityImpactCalc, vixDivergenceCalc, _f12)
    i = 0
    while J.lt(i, J.get(G_close, "length")):
        J.set(primaryMomentum, i, J.get(equityMomentum, i))
        J.set(bondImpact, i, J.get(bondYieldImpact, i))
        J.set(currencyImpact, i, J.get(dollarImpact, i))
        J.set(commodityImpact, i, J.get(commodityImpactCalc, i))
        J.set(vixDivergence, i, J.get(vixDivergenceCalc, i))
        J.set(rotationSignal, i, J.get(rotationSignalCalc, i))
        J.set(divergenceStrength, i, J.get(divergenceStrengthCalc, i))
        i = J.inc(i)
    G_paint(primaryMomentum, J.obj(("color", "grey"), ("name", "Relative Momentum"), ("lineWidth", 2)))
    G_paint(bondImpact, J.obj(("color", "orange"), ("name", "Bond Yield Impact"), ("lineWidth", 2)))
    G_paint(currencyImpact, J.obj(("color", "green"), ("name", "Currency Impact"), ("lineWidth", 2)))
    G_paint(commodityImpact, J.obj(("color", "brown"), ("name", "Commodity Impact"), ("lineWidth", 2)))
    G_paint(vixDivergence, J.obj(("color", "red"), ("name", "VIX Divergence"), ("lineWidth", 1)))
    G_paint(rotationSignal, J.obj(("color", "purple"), ("name", "Rotation Signal"), ("style", "histogram")))
    G_paint(divergenceStrength, J.obj(("color", "yellow"), ("name", "Divergence Strength"), ("lineWidth", 1)))


register_store_indicator(
    script,
    name='cross_asset_momentum_divergence_TS',
    title='Cross-Asset Momentum Divergence',
    developer='Grant Pratt',
    url='https://trendspider.com/trading-tools-store/indicators/68ab23-cross-asset-momentum-divergence/',
    position='lower',
    inputs=[{'id': 'momentum_period', 'title': 'Momentum Period', 'type': 'number', 'default': 20}, {'id': 'divergence_threshold', 'title': 'Divergence Threshold', 'type': 'number', 'default': 0.75}, {'id': 'bond_yield_symbol', 'title': 'Bond Yield Symbol', 'type': 'text', 'default': 'TNX'}, {'id': 'vix_symbol', 'title': 'VIX Symbol', 'type': 'text', 'default': 'VIX'}, {'id': 'dollar_index_symbol', 'title': 'Dollar Index Symbol', 'type': 'text', 'default': 'DXY'}, {'id': 'gold_symbol', 'title': 'Gold Symbol', 'type': 'text', 'default': 'GLD'}, {'id': 'oil_symbol', 'title': 'Oil Symbol', 'type': 'text', 'default': 'USO'}, {'id': 'enable_rotation_signals', 'title': 'Enable Rotation Signals', 'type': 'boolean', 'default': True}],
    outputs=['relative_momentum', 'bond_yield_impact', 'currency_impact', 'commodity_impact', 'vix_divergence', 'rotation_signal', 'divergence_strength'],
    signals=[],
    requires=[],
    parity='aapl_d: MISMATCH, syn_5m: MISMATCH',
)
