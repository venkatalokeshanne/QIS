"""
Fractal Support & Resistance -- TrendSpider store indicator by Grant Pratt.

Registered as "fractal_support_resistance_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68ab25-fractal-support-resistance/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_describe_indicator = G["describe_indicator"]
    G_fractal_high = G["fractal_high"]
    G_fractal_low = G["fractal_low"]
    G_high = G["high"]
    G_horizontal_line = G["horizontal_line"]
    G_indexed_points_of = G["indexed_points_of"]
    G_input = G["input"]
    G_low = G["low"]
    G_paint = G["paint"]
    G_series_of = G["series_of"]
    G_describe_indicator("Fractal Support & Resistance", "price", J.obj(("decimals", "by_symbol"), ("shortName", "Frac.SR")))
    length = G_input("Fractal Length", 5, J.obj(("min", 3), ("max", 21)))
    showLevels = G_input("Show Levels", 29, J.obj(("min", 1), ("max", 70)))
    fractalHighs = G_fractal_high(G_high, length)
    fractalLows = G_fractal_low(G_low, length)
    indexedHighs = G_indexed_points_of(fractalHighs)
    indexedLows = G_indexed_points_of(fractalLows)
    fractalHighDots = G_series_of(None)
    fractalLowDots = G_series_of(None)
    supportLevels = J.JSArray([])
    i = 0
    while (J.lt(i, showLevels) and J.lt(i, J.get(indexedLows, "length"))):
        fractalLow = J.get(indexedLows, J.sub(J.sub(J.get(indexedLows, "length"), 1), i))
        J.set(fractalLowDots, J.get(fractalLow, "candleIndex"), J.get(fractalLow, "value"))
        J.get(supportLevels, "push")(G_horizontal_line(J.get(fractalLow, "value"), J.get(fractalLow, "candleIndex")))
        i = J.inc(i)
    resistanceLevels = J.JSArray([])
    i_2 = 0
    while (J.lt(i_2, showLevels) and J.lt(i_2, J.get(indexedHighs, "length"))):
        fractalHigh = J.get(indexedHighs, J.sub(J.sub(J.get(indexedHighs, "length"), 1), i_2))
        J.set(fractalHighDots, J.get(fractalHigh, "candleIndex"), J.get(fractalHigh, "value"))
        J.get(resistanceLevels, "push")(G_horizontal_line(J.get(fractalHigh, "value"), J.get(fractalHigh, "candleIndex")))
        i_2 = J.inc(i_2)
    G_paint(fractalHighDots, "Fractal Highs", "#ee5451", "dotted", 3)
    G_paint(fractalLowDots, "Fractal Lows", "#2ca599", "dotted", 3)
    i_3 = 0
    while J.lt(i_3, J.get(supportLevels, "length")):
        alpha = J.sub(100, J.mul(i_3, 2))
        G_paint(J.get(supportLevels, i_3), J.template("Support ", J.add(i_3, 1)), J.template("#2ca599", J.get(J.get(alpha, "toString")(16), "padStart")(2, "0")))
        i_3 = J.inc(i_3)
    i_4 = 0
    while J.lt(i_4, J.get(resistanceLevels, "length")):
        alpha_2 = J.sub(100, J.mul(i_4, 2))
        G_paint(J.get(resistanceLevels, i_4), J.template("Resistance ", J.add(i_4, 1)), J.template("#ee5451", J.get(J.get(alpha_2, "toString")(16), "padStart")(2, "0")))
        i_4 = J.inc(i_4)


register_store_indicator(
    script,
    name='fractal_support_resistance_TS',
    title='Fractal Support & Resistance',
    developer='Grant Pratt',
    url='https://trendspider.com/trading-tools-store/indicators/68ab25-fractal-support-resistance/',
    position='price',
    inputs=[{'id': 'fractal_length', 'title': 'Fractal Length', 'type': 'number', 'default': 5}, {'id': 'show_levels', 'title': 'Show Levels', 'type': 'number', 'default': 29}],
    outputs=['fractal_highs', 'fractal_lows', 'support_1', 'support_2', 'support_3', 'support_4', 'support_5', 'support_6', 'support_7', 'support_8', 'support_9', 'support_10', 'support_11', 'support_12', 'support_13', 'support_14', 'support_15', 'support_16', 'support_17', 'support_18', 'support_19', 'support_20', 'support_21', 'support_22', 'support_23', 'support_24', 'support_25', 'support_26', 'support_27', 'support_28', 'support_29', 'resistance_1', 'resistance_2', 'resistance_3', 'resistance_4', 'resistance_5', 'resistance_6', 'resistance_7', 'resistance_8', 'resistance_9', 'resistance_10', 'resistance_11', 'resistance_12', 'resistance_13', 'resistance_14', 'resistance_15', 'resistance_16', 'resistance_17', 'resistance_18', 'resistance_19', 'resistance_20', 'resistance_21', 'resistance_22', 'resistance_23', 'resistance_24', 'resistance_25', 'resistance_26', 'resistance_27', 'resistance_28', 'resistance_29'],
    signals=[],
    requires=[],
    parity='exact',
)
