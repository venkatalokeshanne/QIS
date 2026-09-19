"""
Fundamental Strength with weightings -- TrendSpider store indicator by James Chambers.

Registered as "fundamental_strength_with_weightings_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/fundamental-strength-with-weightings/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_assert = G["assert"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_input = G["input"]
    G_library = G["library"]
    G_paint = G["paint"]
    G_request = G["request"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    def getMetricData(data=J.undefined, metric=J.undefined, *_args):
        def _f1(dp=J.undefined, *_args):
            return J.obj(("value", J.get(dp, "value")), ("timestamp", J.get(dp, "reportdate")))
        return J.get(J.get(data, metric), "map")(_f1)
    def normalize(data=J.undefined, *_args):
        def _f1(d=J.undefined, *_args):
            return J.get(d, "value")
        values = J.get(data, "map")(_f1)
        min = J.get(G_Math, "min")(*J.spread(values))
        max = J.get(G_Math, "max")(*J.spread(values))
        def _f2(d=J.undefined, *_args):
            return J.obj(*J.obj_spread(d), ("value", J.div(J.sub(J.get(d, "value"), min), J.sub(max, min))))
        return J.get(data, "map")(_f2)
    moment = G_library("moment-timezone")
    G_describe_indicator("Fundamental Strength Indicator Final w/ Weighting", "lower", J.obj(("shortName", "CFSI"), ("decimals", 2)))
    quarters = G_input("Number of Quarters", 29)
    metric1 = G_input("Metric 1", "gross_profit_margin", J.JSArray(["gross_profit_margin", "return_on_equity", "current_ratio", "debt_ratio", "free_cash_flow", "net_income", "operating_margin", "revenue", "ebitda", "fcf_to_net_income", "book_to_market_value", "cash_cash_equivalents", "debt_to_equity_ratio", "net_profit_margin", "total_assets", "total_equity", "total_liabilities", "pretax_income_loss_adj", "net_income_discontinued_operations", "eps_diluted"]))
    weight1 = G_input("Weight 1", 0.2, J.obj(("min", 0), ("max", 1), ("step", 0.01)))
    metric2 = G_input("Metric 2", "return_on_equity", J.JSArray(["gross_profit_margin", "return_on_equity", "current_ratio", "debt_ratio", "free_cash_flow", "net_income", "operating_margin", "revenue", "ebitda", "fcf_to_net_income", "book_to_market_value", "cash_cash_equivalents", "debt_to_equity_ratio", "net_profit_margin", "total_assets", "total_equity", "total_liabilities", "pretax_income_loss_adj", "net_income_discontinued_operations", "eps_diluted"]))
    weight2 = G_input("Weight 2", 0.2, J.obj(("min", 0), ("max", 1), ("step", 0.01)))
    metric3 = G_input("Metric 3", "current_ratio", J.JSArray(["gross_profit_margin", "return_on_equity", "current_ratio", "debt_ratio", "free_cash_flow", "net_income", "operating_margin", "revenue", "ebitda", "fcf_to_net_income", "book_to_market_value", "cash_cash_equivalents", "debt_to_equity_ratio", "net_profit_margin", "total_assets", "total_equity", "total_liabilities", "pretax_income_loss_adj", "net_income_discontinued_operations", "eps_diluted"]))
    weight3 = G_input("Weight 3", 0.2, J.obj(("min", 0), ("max", 1), ("step", 0.01)))
    metric4 = G_input("Metric 4", "debt_ratio", J.JSArray(["gross_profit_margin", "return_on_equity", "current_ratio", "debt_ratio", "free_cash_flow", "net_income", "operating_margin", "revenue", "ebitda", "fcf_to_net_income", "book_to_market_value", "cash_cash_equivalents", "debt_to_equity_ratio", "net_profit_margin", "total_assets", "total_equity", "total_liabilities", "pretax_income_loss_adj", "net_income_discontinued_operations", "eps_diluted"]))
    weight4 = G_input("Weight 4", 0.2, J.obj(("min", 0), ("max", 1), ("step", 0.01)))
    metric5 = G_input("Metric 5", "free_cash_flow", J.JSArray(["gross_profit_margin", "return_on_equity", "current_ratio", "debt_ratio", "free_cash_flow", "net_income", "operating_margin", "revenue", "ebitda", "fcf_to_net_income", "book_to_market_value", "cash_cash_equivalents", "debt_to_equity_ratio", "net_profit_margin", "total_assets", "total_equity", "total_liabilities", "pretax_income_loss_adj", "net_income_discontinued_operations", "eps_diluted"]))
    weight5 = G_input("Weight 5", 0.2, J.obj(("min", 0), ("max", 1), ("step", 0.01)))
    metrics = J.JSArray([metric1, metric2, metric3, metric4, metric5])
    weights = J.JSArray([weight1, weight2, weight3, weight4, weight5])
    ticker = J.get(G_current, "ticker")
    fundamentalData = J.get(G_request, "fundamental")(ticker, metrics, quarters)
    G_assert((not J.truthy(J.get(fundamentalData, "error"))), J.template("Error fetching fundamental data: ", J.get(fundamentalData, "error")))
    metricSeries = J.obj()
    def _f1(metric=J.undefined, index=J.undefined, *_args):
        data = getMetricData(fundamentalData, metric)
        normalizedData = normalize(data)
        J.set(metricSeries, J.template("metric", J.add(index, 1)), G_series_of(None))
        i = 0
        while J.lt(i, J.get(G_time, "length")):
            currentTimestamp = J.get(G_time, i)
            def _f1(d=J.undefined, *_args):
                return J.le(J.get(d, "timestamp"), currentTimestamp)
            value = J.get(normalizedData, "find")(_f1)
            J.set(J.get(metricSeries, J.template("metric", J.add(index, 1))), i, (J.get(value, "value") if J.truthy(value) else None))
            i = J.inc(i)
    J.get(metrics, "forEach")(_f1)
    compositeScoreSeries = G_series_of(None)
    compositeScoreColors = G_series_of(None)
    i = 0
    while J.lt(i, J.get(G_time, "length")):
        def _f2(metric=J.undefined, index=J.undefined, *_args):
            return J.get(J.get(metricSeries, J.template("metric", J.add(index, 1))), i)
        scores = J.get(metrics, "map")(_f2)
        def _f3(score=J.undefined, *_args):
            return (score is not None)
        if J.truthy(J.get(scores, "every")(_f3)):
            def _f4(acc=J.undefined, score=J.undefined, index=J.undefined, *_args):
                return J.add(acc, J.mul(score, J.get(weights, index)))
            compositeScore = J.get(scores, "reduce")(_f4, 0)
            J.set(compositeScoreSeries, i, compositeScore)
            J.set(compositeScoreColors, i, ("darkgreen" if J.gt(compositeScore, 0.6) else ("lightgreen" if J.gt(compositeScore, 0.5) else ("lightred" if J.gt(compositeScore, 0.4) else "darkred"))))
        else:
            J.set(compositeScoreSeries, i, None)
            J.set(compositeScoreColors, i, None)
        i = J.inc(i)
    G_paint(compositeScoreSeries, J.obj(("name", "Fundamental Strength Indicator"), ("color", compositeScoreColors), ("thickness", 2), ("style", "column")))


register_store_indicator(
    script,
    name='fundamental_strength_with_weightings_TS',
    title='Fundamental Strength with weightings',
    developer='James Chambers',
    url='https://trendspider.com/trading-tools-store/indicators/fundamental-strength-with-weightings/',
    position='lower',
    inputs=[{'id': 'number_of_quarters', 'title': 'Number of Quarters', 'type': 'number', 'default': 29}, {'id': 'metric_1', 'title': 'Metric 1', 'type': 'select_wide', 'default': 'gross_profit_margin', 'options': ['gross_profit_margin', 'return_on_equity', 'current_ratio', 'debt_ratio', 'free_cash_flow', 'net_income', 'operating_margin', 'revenue', 'ebitda', 'fcf_to_net_income', 'book_to_market_value', 'cash_cash_equivalents', 'debt_to_equity_ratio', 'net_profit_margin', 'total_assets', 'total_equity', 'total_liabilities', 'pretax_income_loss_adj', 'net_income_discontinued_operations', 'eps_diluted']}, {'id': 'weight_1', 'title': 'Weight 1', 'type': 'number', 'default': 0.2}, {'id': 'metric_2', 'title': 'Metric 2', 'type': 'select_wide', 'default': 'return_on_equity', 'options': ['gross_profit_margin', 'return_on_equity', 'current_ratio', 'debt_ratio', 'free_cash_flow', 'net_income', 'operating_margin', 'revenue', 'ebitda', 'fcf_to_net_income', 'book_to_market_value', 'cash_cash_equivalents', 'debt_to_equity_ratio', 'net_profit_margin', 'total_assets', 'total_equity', 'total_liabilities', 'pretax_income_loss_adj', 'net_income_discontinued_operations', 'eps_diluted']}, {'id': 'weight_2', 'title': 'Weight 2', 'type': 'number', 'default': 0.2}, {'id': 'metric_3', 'title': 'Metric 3', 'type': 'select_wide', 'default': 'current_ratio', 'options': ['gross_profit_margin', 'return_on_equity', 'current_ratio', 'debt_ratio', 'free_cash_flow', 'net_income', 'operating_margin', 'revenue', 'ebitda', 'fcf_to_net_income', 'book_to_market_value', 'cash_cash_equivalents', 'debt_to_equity_ratio', 'net_profit_margin', 'total_assets', 'total_equity', 'total_liabilities', 'pretax_income_loss_adj', 'net_income_discontinued_operations', 'eps_diluted']}, {'id': 'weight_3', 'title': 'Weight 3', 'type': 'number', 'default': 0.2}, {'id': 'metric_4', 'title': 'Metric 4', 'type': 'select_wide', 'default': 'debt_ratio', 'options': ['gross_profit_margin', 'return_on_equity', 'current_ratio', 'debt_ratio', 'free_cash_flow', 'net_income', 'operating_margin', 'revenue', 'ebitda', 'fcf_to_net_income', 'book_to_market_value', 'cash_cash_equivalents', 'debt_to_equity_ratio', 'net_profit_margin', 'total_assets', 'total_equity', 'total_liabilities', 'pretax_income_loss_adj', 'net_income_discontinued_operations', 'eps_diluted']}, {'id': 'weight_4', 'title': 'Weight 4', 'type': 'number', 'default': 0.2}, {'id': 'metric_5', 'title': 'Metric 5', 'type': 'select_wide', 'default': 'free_cash_flow', 'options': ['gross_profit_margin', 'return_on_equity', 'current_ratio', 'debt_ratio', 'free_cash_flow', 'net_income', 'operating_margin', 'revenue', 'ebitda', 'fcf_to_net_income', 'book_to_market_value', 'cash_cash_equivalents', 'debt_to_equity_ratio', 'net_profit_margin', 'total_assets', 'total_equity', 'total_liabilities', 'pretax_income_loss_adj', 'net_income_discontinued_operations', 'eps_diluted']}, {'id': 'weight_5', 'title': 'Weight 5', 'type': 'number', 'default': 0.2}],
    outputs=['fundamental_strength_indicator'],
    signals=[],
    requires=['fundamental'],
    parity='exact',
)
