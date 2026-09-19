"""
Fundamentals Strip -- TrendSpider store indicator by TrendSpider.

Registered as "fundamentals_strip_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6893d0-fundamentals-strip/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
aapl_d: OK, syn_5m: both-error.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Intl = G["Intl"]
    G_Math = G["Math"]
    G_Promise = G["Promise"]
    G_assert = G["assert"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_input = G["input"]
    G_isNaN = G["isNaN"]
    G_library = G["library"]
    G_paint_overlay = G["paint_overlay"]
    G_parseInt = G["parseInt"]
    G_request = G["request"]
    G_time = G["time"]
    G_describe_indicator("Fundamentals Strip")
    backgroundColor = J.get(G_input, "color")("Background Color", "#000000")
    backgroundOpacity = J.get(G_input, "number")("Background Opacity", 0.3, J.obj(("min", 0), ("max", 1), ("step", 0.1)))
    fontSize = J.get(G_input, "number")("Font Size", 13, J.obj(("min", 8), ("max", 20), ("step", 1)))
    beatTextColor = J.get(G_input, "color")("Beat Text Color", "#2ecc53")
    missTextColor = J.get(G_input, "color")("Miss Text Color", "#ff0000")
    moment = G_library("moment-timezone")
    _t1 = J.iter_of(J.get(G_Promise, "all")(J.JSArray([J.get(G_request, "history")(J.get(G_current, "ticker"), "W"), J.get(G_request, "fundamental")(J.get(G_current, "ticker"), J.JSArray(["revenue", "market_cap", "cash_cash_equivalents", "long_term_debt", "gross_profit", "operating_income_loss", "net_income", "dividends_paid", "cash_from_repurchase_equity", "free_cash_flow", "enterprise_value", "debt_ratio", "current_ratio", "ps_ratio_ttm", "pe_ratio_ttm", "price_to_book_value"]), 20), J.get(G_request, "earnings")(J.get(G_current, "ticker"), J.obj(("filters", J.JSArray([J.obj(("field", "timestamp"), ("filter", "greater"), ("value", 0))])))), J.get(G_request, "insider_trading")(J.get(G_current, "ticker"))])))
    weeklyHistory = (_t1[0] if 0 < len(_t1) else J.undefined)
    fundamentals = (_t1[1] if 1 < len(_t1) else J.undefined)
    earnings = (_t1[2] if 2 < len(_t1) else J.undefined)
    insider = (_t1[3] if 3 < len(_t1) else J.undefined)
    G_assert((not J.truthy(J.get(weeklyHistory, "error"))), J.template("Error fetching W data: ", J.get(weeklyHistory, "error")))
    G_assert((not J.truthy(J.get(fundamentals, "error"))), J.template("Error fetching fundamentals: ", J.get(fundamentals, "error")))
    G_assert((not J.truthy(J.get(earnings, "error"))), J.template("Error fetching earnings: ", J.get(earnings, "error")))
    G_assert((not J.truthy(J.get(insider, "error"))), J.template("Error fetching insider_trading: ", J.get(insider, "error")))
    def formatLargeNumber(value=J.undefined, _p1=J.undefined, *_args):
        _t2 = _p1
        if _t2 is J.undefined:
            _t2 = 0
        decimals = _t2
        return ("—" if J.truthy(G_isNaN(value)) else J.get(J.get(G_Intl, "NumberFormat")("en-US", J.obj(("notation", "compact"), ("maximumFractionDigits", decimals))), "format")(value))
    def formatRatio(value=J.undefined, *_args):
        return ("—" if J.truthy(G_isNaN(value)) else J.get(value, "toFixed")(2))
    def currentFundamental(metricId=J.undefined, *_args):
        return (J.get(J.get(J.get(fundamentals, metricId), 0), "value") if J.truthy(J.get(J.get(fundamentals, metricId), 0)) else J.undefined)
    cashValue = (J.template("$", formatLargeNumber(currentFundamental("cash_cash_equivalents"), 1)) if J.truthy(currentFundamental("cash_cash_equivalents")) else "—")
    longTermDebtValue = (J.template("$", formatLargeNumber(currentFundamental("long_term_debt"), 1)) if J.truthy(currentFundamental("long_term_debt")) else "—")
    def _f2(sum=J.undefined, record=J.undefined, *_args):
        return J.add(sum, J.get(record, "value"))
    trailingFourQuartersRevenue = J.get(J.get(J.get(fundamentals, "revenue"), "slice")(0, 4), "reduce")(_f2, 0)
    def _f3(sum=J.undefined, record=J.undefined, *_args):
        return J.add(sum, J.get(record, "value"))
    previousFourQuartersRevenue = J.get(J.get(J.get(fundamentals, "revenue"), "slice")(4, 8), "reduce")(_f3, 0)
    revenueYoYChange = (J.get(J.mul(J.div(J.sub(trailingFourQuartersRevenue, previousFourQuartersRevenue), previousFourQuartersRevenue), 100), "toFixed")(1) if J.truthy(previousFourQuartersRevenue) else "—")
    revenueBaseValue = (J.template("$", formatLargeNumber(trailingFourQuartersRevenue, 1)) if J.truthy(trailingFourQuartersRevenue) else "—")
    revenueChangeValue = (J.template(revenueYoYChange, "% YoY") if J.sne(revenueYoYChange, "—") else "")
    def _f4(sum=J.undefined, record=J.undefined, *_args):
        return J.add(sum, J.get(record, "value"))
    trailingFourQuartersGrossProfit = J.get(J.get(J.get(fundamentals, "gross_profit"), "slice")(0, 4), "reduce")(_f4, 0)
    def _f5(sum=J.undefined, record=J.undefined, *_args):
        return J.add(sum, J.get(record, "value"))
    previousFourQuartersGrossProfit = J.get(J.get(J.get(fundamentals, "gross_profit"), "slice")(4, 8), "reduce")(_f5, 0)
    trailingGrossMargin = (J.get(J.mul(J.div(trailingFourQuartersGrossProfit, trailingFourQuartersRevenue), 100), "toFixed")(1) if J.truthy(trailingFourQuartersRevenue) else "—")
    previousGrossMargin = (J.get(J.mul(J.div(previousFourQuartersGrossProfit, previousFourQuartersRevenue), 100), "toFixed")(1) if J.truthy(previousFourQuartersRevenue) else "—")
    grossMarginYoYChange = (J.get(J.mul(J.div(J.sub(trailingGrossMargin, previousGrossMargin), previousGrossMargin), 100), "toFixed")(1) if J.sne(previousGrossMargin, "—") else "—")
    grossMarginBaseValue = (J.template(trailingGrossMargin, "%") if J.sne(trailingGrossMargin, "—") else "—")
    grossMarginChangeValue = (J.template(grossMarginYoYChange, "% YoY") if J.sne(grossMarginYoYChange, "—") else "")
    def _f6(sum=J.undefined, record=J.undefined, *_args):
        return J.add(sum, J.get(record, "value"))
    trailingFourQuartersOperatingIncome = J.get(J.get(J.get(fundamentals, "operating_income_loss"), "slice")(0, 4), "reduce")(_f6, 0)
    def _f7(sum=J.undefined, record=J.undefined, *_args):
        return J.add(sum, J.get(record, "value"))
    previousFourQuartersOperatingIncome = J.get(J.get(J.get(fundamentals, "operating_income_loss"), "slice")(4, 8), "reduce")(_f7, 0)
    operatingIncomeYoYChange = (J.get(J.mul(J.div(J.sub(trailingFourQuartersOperatingIncome, previousFourQuartersOperatingIncome), previousFourQuartersOperatingIncome), 100), "toFixed")(1) if J.truthy(previousFourQuartersOperatingIncome) else "—")
    operatingIncomeBaseValue = (J.template("$", formatLargeNumber(trailingFourQuartersOperatingIncome, 1)) if (trailingFourQuartersOperatingIncome is not J.undefined) else "—")
    operatingIncomeChangeValue = (J.template(operatingIncomeYoYChange, "% YoY") if J.sne(operatingIncomeYoYChange, "—") else "")
    def _f8(sum=J.undefined, record=J.undefined, *_args):
        return J.add(sum, J.get(record, "value"))
    trailingFourQuartersNetIncome = J.get(J.get(J.get(fundamentals, "net_income"), "slice")(0, 4), "reduce")(_f8, 0)
    def _f9(sum=J.undefined, record=J.undefined, *_args):
        return J.add(sum, J.get(record, "value"))
    previousFourQuartersNetIncome = J.get(J.get(J.get(fundamentals, "net_income"), "slice")(4, 8), "reduce")(_f9, 0)
    netIncomeYoYChange = (J.get(J.mul(J.div(J.sub(trailingFourQuartersNetIncome, previousFourQuartersNetIncome), previousFourQuartersNetIncome), 100), "toFixed")(1) if J.truthy(previousFourQuartersNetIncome) else "—")
    netIncomeBaseValue = (J.template("$", formatLargeNumber(trailingFourQuartersNetIncome, 1)) if (trailingFourQuartersNetIncome is not J.undefined) else "—")
    netIncomeChangeValue = (J.template(netIncomeYoYChange, "% YoY") if J.sne(netIncomeYoYChange, "—") else "")
    latestQuarterDebtRatio = (_t10 if J.truthy(_t10 := J.chain_end(J.oget(J.get(J.get(fundamentals, "debt_ratio"), 0), "value"))) else 0)
    previousQuarterDebtRatio = (_t11 if J.truthy(_t11 := J.chain_end(J.oget(J.get(J.get(fundamentals, "debt_ratio"), 1), "value"))) else 0)
    debtRatioQoQChange = (J.get(J.mul(J.div(J.sub(latestQuarterDebtRatio, previousQuarterDebtRatio), previousQuarterDebtRatio), 100), "toFixed")(1) if J.truthy(previousQuarterDebtRatio) else "—")
    debtRatioBaseValue = (formatRatio(latestQuarterDebtRatio) if J.truthy(latestQuarterDebtRatio) else "—")
    debtRatioChangeValue = (J.template(debtRatioQoQChange, "% QoQ") if J.sne(debtRatioQoQChange, "—") else "")
    latestQuarterCurrentRatio = (_t12 if J.truthy(_t12 := J.chain_end(J.oget(J.get(J.get(fundamentals, "current_ratio"), 0), "value"))) else 0)
    previousQuarterCurrentRatio = (_t13 if J.truthy(_t13 := J.chain_end(J.oget(J.get(J.get(fundamentals, "current_ratio"), 1), "value"))) else 0)
    currentRatioQoQChange = (J.get(J.mul(J.div(J.sub(latestQuarterCurrentRatio, previousQuarterCurrentRatio), previousQuarterCurrentRatio), 100), "toFixed")(1) if J.truthy(previousQuarterCurrentRatio) else "—")
    currentRatioBaseValue = (formatRatio(latestQuarterCurrentRatio) if J.truthy(latestQuarterCurrentRatio) else "—")
    currentRatioChangeValue = (J.template(currentRatioQoQChange, "% QoQ") if J.sne(currentRatioQoQChange, "—") else "")
    latestQuarterCash = (_t14 if J.truthy(_t14 := J.chain_end(J.oget(J.get(J.get(fundamentals, "cash_cash_equivalents"), 0), "value"))) else 0)
    previousQuarterCash = (_t15 if J.truthy(_t15 := J.chain_end(J.oget(J.get(J.get(fundamentals, "cash_cash_equivalents"), 1), "value"))) else 0)
    cashQoQChange = (J.get(J.mul(J.div(J.sub(latestQuarterCash, previousQuarterCash), previousQuarterCash), 100), "toFixed")(1) if J.truthy(previousQuarterCash) else "—")
    cashBaseValue = J.template("$", formatLargeNumber(latestQuarterCash, 1))
    cashChangeValue = (J.template(cashQoQChange, "% QoQ") if J.sne(cashQoQChange, "—") else "")
    latestQuarterLongTermDebt = (_t16 if J.truthy(_t16 := J.chain_end(J.oget(J.get(J.get(fundamentals, "long_term_debt"), 0), "value"))) else 0)
    previousQuarterLongTermDebt = (_t17 if J.truthy(_t17 := J.chain_end(J.oget(J.get(J.get(fundamentals, "long_term_debt"), 1), "value"))) else 0)
    longTermDebtQoQChange = (J.get(J.mul(J.div(J.sub(latestQuarterLongTermDebt, previousQuarterLongTermDebt), previousQuarterLongTermDebt), 100), "toFixed")(1) if J.truthy(previousQuarterLongTermDebt) else "—")
    longTermDebtBaseValue = J.template("$", formatLargeNumber(latestQuarterLongTermDebt, 1))
    longTermDebtChangeValue = (J.template(longTermDebtQoQChange, "% QoQ") if J.sne(longTermDebtQoQChange, "—") else "")
    def _f18(sum=J.undefined, record=J.undefined, *_args):
        return J.add(sum, J.get(record, "value"))
    trailingFourQuartersOperatingActivities = J.get(J.get(J.get(fundamentals, "dividends_paid"), "slice")(0, 4), "reduce")(_f18, 0)
    def _f19(sum=J.undefined, record=J.undefined, *_args):
        return J.add(sum, J.get(record, "value"))
    previousFourQuartersOperatingActivities = J.get(J.get(J.get(fundamentals, "dividends_paid"), "slice")(4, 8), "reduce")(_f19, 0)
    operatingActivitiesYoYChange = (J.get(J.mul(J.div(J.sub(trailingFourQuartersOperatingActivities, previousFourQuartersOperatingActivities), previousFourQuartersOperatingActivities), 100), "toFixed")(1) if J.truthy(previousFourQuartersOperatingActivities) else "—")
    operatingActivitiesBaseValue = (J.template("$", formatLargeNumber(trailingFourQuartersOperatingActivities, 1)) if (trailingFourQuartersOperatingActivities is not J.undefined) else "—")
    operatingActivitiesChangeValue = (J.template(operatingActivitiesYoYChange, "% YoY") if J.sne(operatingActivitiesYoYChange, "—") else "")
    def _f20(sum=J.undefined, record=J.undefined, *_args):
        return J.add(sum, J.get(record, "value"))
    trailingFourQuartersEquityRepurchase = J.get(J.get(J.get(fundamentals, "cash_from_repurchase_equity"), "slice")(0, 4), "reduce")(_f20, 0)
    def _f21(sum=J.undefined, record=J.undefined, *_args):
        return J.add(sum, J.get(record, "value"))
    previousFourQuartersEquityRepurchase = J.get(J.get(J.get(fundamentals, "cash_from_repurchase_equity"), "slice")(4, 8), "reduce")(_f21, 0)
    equityRepurchaseYoYChange = (J.get(J.mul(J.div(J.sub(trailingFourQuartersEquityRepurchase, previousFourQuartersEquityRepurchase), previousFourQuartersEquityRepurchase), 100), "toFixed")(1) if J.truthy(previousFourQuartersEquityRepurchase) else "—")
    equityRepurchaseBaseValue = (J.template("$", formatLargeNumber(trailingFourQuartersEquityRepurchase, 1)) if (trailingFourQuartersEquityRepurchase is not J.undefined) else "—")
    equityRepurchaseChangeValue = (J.template(equityRepurchaseYoYChange, "% YoY") if J.sne(equityRepurchaseYoYChange, "—") else "")
    def _f22(sum=J.undefined, record=J.undefined, *_args):
        return J.add(sum, J.get(record, "value"))
    trailingFourQuartersFCF = J.get(J.get(J.get(fundamentals, "free_cash_flow"), "slice")(0, 4), "reduce")(_f22, 0)
    def _f23(sum=J.undefined, record=J.undefined, *_args):
        return J.add(sum, J.get(record, "value"))
    previousFourQuartersFCF = J.get(J.get(J.get(fundamentals, "free_cash_flow"), "slice")(4, 8), "reduce")(_f23, 0)
    fcfYoYChange = (J.get(J.mul(J.div(J.sub(trailingFourQuartersFCF, previousFourQuartersFCF), previousFourQuartersFCF), 100), "toFixed")(1) if J.truthy(previousFourQuartersFCF) else "—")
    fcfBaseValue = (J.template("$", formatLargeNumber(trailingFourQuartersFCF, 1)) if (trailingFourQuartersFCF is not J.undefined) else "—")
    fcfChangeValue = (J.template(fcfYoYChange, "% YoY") if J.sne(fcfYoYChange, "—") else "")
    def headCell(text=J.undefined, *_args):
        return J.obj(("text", J.template(text)), ("fontWeight", "bold"), ("color", "var(--text-color)"), ("padding", "1px 5px"))
    def valueCell(text=J.undefined, *_args):
        return J.obj(("text", J.template(text)), ("color", "var(--text-color)"), ("padding", "3px 7px"))
    def leftTitleCell(text=J.undefined, *_args):
        return J.obj(("text", J.template(text)), ("fontWeight", "bold"), ("color", "var(--text-color)"), ("padding", "1px 7px"), ("width", "45%"))
    def valueCellStyle(text=J.undefined, _p1=J.undefined, *_args):
        _t2 = _p1
        if _t2 is J.undefined:
            _t2 = "var(--text-color)"
        color = _t2
        return J.obj(("text", J.template(text)), ("color", color), ("textAlign", "right"), ("padding", "1px 5px"), ("width", "15%"))
    def changeCellStyle(text=J.undefined, color=J.undefined, *_args):
        return J.obj(("text", J.template(text)), ("color", (_t1 if J.truthy(_t1 := color) else "var(--text-color)")), ("fontSize", 10), ("textAlign", "right"), ("padding", "1px 5px"), ("width", "40%"))
    SEPARATOR = J.obj(("cells", J.JSArray([J.obj(("text", ""), ("colspan", 3), ("borderBottom", "1px solid var(--border-color)"))])))
    marketCap = J.template("$", formatLargeNumber(currentFundamental("market_cap")))
    enterpriseValue = J.template("$", formatLargeNumber(currentFundamental("enterprise_value")))
    psRatio = (formatRatio(currentFundamental("ps_ratio_ttm")) if J.truthy(currentFundamental("ps_ratio_ttm")) else "—")
    peRatio = (formatRatio(currentFundamental("pe_ratio_ttm")) if J.truthy(currentFundamental("pe_ratio_ttm")) else "—")
    pbRatio = (formatRatio(currentFundamental("price_to_book_value")) if J.truthy(currentFundamental("price_to_book_value")) else "—")
    def _f24(record=J.undefined, *_args):
        return J.get(record, "isFuture")
    nextEarnings = J.get(earnings, "find")(_f24)
    DAYS_IN_SECONDS = J.mul(J.mul(24, 60), 60)
    daysUntilNextEarnings = J.get(G_Math, "floor")(J.div(J.sub(J.get(nextEarnings, "timestamp"), J.get(G_time, J.sub(J.get(G_time, "length"), 1))), DAYS_IN_SECONDS))
    def titleValueRow(title=J.undefined, value=J.undefined, *_args):
        return J.obj(("cells", J.JSArray([leftTitleCell(title), J.obj(("text", ""), ("width", "25%")), valueCellStyle(value)])))
    G_paint_overlay("Table", J.obj(("position", "bottom_right"), ("offset_x", (-65)), ("offset_y", (-175)), ("order", "above_all")), J.obj(("fontSize", fontSize), ("border", "0px solid var(--border-color)"), ("background", J.template("rgba(", G_parseInt(J.get(backgroundColor, "slice")(1, 3), 16), ", ", G_parseInt(J.get(backgroundColor, "slice")(3, 5), 16), ", ", G_parseInt(J.get(backgroundColor, "slice")(5, 7), 16), ", ", backgroundOpacity, ")")), ("width", "250px"), ("rows", J.JSArray([J.obj(("cells", J.JSArray([J.obj(("colspan", 3), ("text", J.template(J.get(G_current, "ticker"))), ("color", "var(--text-color)"), ("padding", "3px 7px"))]))), J.obj(("cells", J.JSArray([J.obj(("colspan", 3), ("table", J.obj(("width", "100%"), ("rows", J.JSArray([J.obj(("cells", J.JSArray([J.obj(*J.obj_spread(valueCell(J.template("Next earnings: ", J.get(moment(J.mul(J.get(nextEarnings, "timestamp"), 1000)), "format")("DD-MM-YYYY"), " (in ", daysUntilNextEarnings, " days)"))), ("colspan", 3))]))), SEPARATOR, titleValueRow("Mkt Cap", marketCap), titleValueRow("EV", enterpriseValue), titleValueRow("P/S Ratio", psRatio), titleValueRow("P/E Ratio", peRatio), titleValueRow("P/B Ratio", pbRatio), SEPARATOR, J.obj(("cells", J.JSArray([J.obj(("text", "Income Statement:"), ("fontSize", 13), ("fontWeight", "bold"), ("color", "var(--text-color)"), ("padding", "2px 7px"), ("colspan", 3))]))), J.obj(("cells", J.JSArray([J.obj(("text", ""), ("padding", "2px"), ("colspan", 3))]))), J.obj(("cells", J.JSArray([leftTitleCell("Revenue"), valueCellStyle(revenueBaseValue), changeCellStyle(revenueChangeValue, (beatTextColor if J.gt(revenueYoYChange, 0) else missTextColor))]))), J.obj(("cells", J.JSArray([leftTitleCell("Gross Margin"), valueCellStyle(grossMarginBaseValue), changeCellStyle(grossMarginChangeValue, (beatTextColor if J.gt(grossMarginYoYChange, 0) else missTextColor))]))), J.obj(("cells", J.JSArray([leftTitleCell("Op. Income"), valueCellStyle(operatingIncomeBaseValue), changeCellStyle(operatingIncomeChangeValue, (beatTextColor if J.gt(operatingIncomeYoYChange, 0) else missTextColor))]))), J.obj(("cells", J.JSArray([leftTitleCell("Net Income"), valueCellStyle(netIncomeBaseValue), changeCellStyle(netIncomeChangeValue, (beatTextColor if J.gt(netIncomeYoYChange, 0) else missTextColor))]))), SEPARATOR, J.obj(("cells", J.JSArray([J.obj(("text", "Balance Sheet:"), ("fontSize", 13), ("fontWeight", "bold"), ("color", "var(--text-color)"), ("padding", "2px 7px"), ("colspan", 3))]))), J.obj(("cells", J.JSArray([J.obj(("text", ""), ("padding", "2px"), ("colspan", 3))]))), J.obj(("cells", J.JSArray([leftTitleCell("Cash"), valueCellStyle(cashBaseValue), changeCellStyle(cashChangeValue, (beatTextColor if J.gt(cashQoQChange, 0) else missTextColor))]))), J.obj(("cells", J.JSArray([leftTitleCell("LT Debt"), valueCellStyle(longTermDebtBaseValue), changeCellStyle(longTermDebtChangeValue, (beatTextColor if J.gt(longTermDebtQoQChange, 0) else missTextColor))]))), J.obj(("cells", J.JSArray([leftTitleCell("Debt Ratio"), valueCellStyle(debtRatioBaseValue), changeCellStyle(debtRatioChangeValue, (beatTextColor if J.gt(debtRatioQoQChange, 0) else missTextColor))]))), J.obj(("cells", J.JSArray([leftTitleCell("Current Ratio"), valueCellStyle(currentRatioBaseValue), changeCellStyle(currentRatioChangeValue, (beatTextColor if J.gt(currentRatioQoQChange, 0) else missTextColor))]))), SEPARATOR, J.obj(("cells", J.JSArray([J.obj(("text", "Cash Flow Statement:"), ("fontSize", 13), ("fontWeight", "bold"), ("color", "var(--text-color)"), ("padding", "1px 7px"), ("colspan", 3))]))), J.obj(("cells", J.JSArray([J.obj(("text", ""), ("padding", "2px"), ("colspan", 3))]))), J.obj(("cells", J.JSArray([leftTitleCell("FCF"), valueCellStyle(fcfBaseValue), changeCellStyle(fcfChangeValue, (beatTextColor if J.gt(fcfYoYChange, 0) else missTextColor))]))), J.obj(("cells", J.JSArray([leftTitleCell("Dividends Paid"), valueCellStyle(operatingActivitiesBaseValue), changeCellStyle(operatingActivitiesChangeValue, (beatTextColor if J.gt(operatingActivitiesYoYChange, 0) else missTextColor))]))), J.obj(("cells", J.JSArray([leftTitleCell("Buybacks"), valueCellStyle(equityRepurchaseBaseValue), changeCellStyle(equityRepurchaseChangeValue, (beatTextColor if J.gt(equityRepurchaseYoYChange, 0) else missTextColor))]))), SEPARATOR])))))])))]))))


register_store_indicator(
    script,
    name='fundamentals_strip_TS',
    title='Fundamentals Strip',
    developer='TrendSpider',
    url='https://trendspider.com/trading-tools-store/indicators/6893d0-fundamentals-strip/',
    position='price',
    inputs=[{'id': 'background_color', 'title': 'Background Color', 'type': 'color', 'default': '#000000'}, {'id': 'background_opacity', 'title': 'Background Opacity', 'type': 'number', 'default': 0.3}, {'id': 'font_size', 'title': 'Font Size', 'type': 'number', 'default': 13}, {'id': 'beat_text_color', 'title': 'Beat Text Color', 'type': 'color', 'default': '#2ecc53'}, {'id': 'miss_text_color', 'title': 'Miss Text Color', 'type': 'color', 'default': '#ff0000'}],
    outputs=[],
    signals=[],
    requires=['earnings', 'fundamental', 'history', 'insider_trading'],
    parity='aapl_d: OK, syn_5m: both-error',
)
