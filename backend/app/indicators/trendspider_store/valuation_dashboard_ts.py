"""
Valuation Dashboard -- TrendSpider store indicator by Feliks Ba\u0144ka.

Registered as "valuation_dashboard_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68abad-valuation-dashboard/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
aapl_d: both-error, syn_5m: both-error.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_assert = G["assert"]
    G_close = G["close"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_encodeURIComponent = G["encodeURIComponent"]
    G_input = G["input"]
    G_isFinite = G["isFinite"]
    G_paint_overlay = G["paint_overlay"]
    G_request = G["request"]
    def toNum(x=J.undefined, *_args):
        if (J.nullish(x)):
            return None
        v = J.pos(x)
        return (v if J.truthy(G_isFinite(v)) else None)
    def normalize(v=J.undefined, min=J.undefined, max=J.undefined, *_args):
        if (J.nullish(v)):
            return None
        return J.get(G_Math, "max")(0, J.get(G_Math, "min")(1, J.div(J.sub(v, min), J.sub(max, min))))
    def addPart(val=J.undefined, w=J.undefined, *_args):
        nonlocal total, weight
        if (not J.nullish(val)):
            total = J.add(total, J.mul(val, w))
            weight = J.add(weight, w)
    G_describe_indicator("Valuation Dashboard #TSBuild25", "onchart", J.obj(("shortName", "Valuation"), ("decimals", 2)))
    grpW = "① User Weights"
    wPE = J.get(G_input, "number")("Weight P/E", 1, J.obj(("step", 0.1), ("group", grpW)))
    wFwdPE = J.get(G_input, "number")("Weight Forward P/E", 1, J.obj(("step", 0.1), ("group", grpW)))
    wPB = J.get(G_input, "number")("Weight P/B", 1, J.obj(("step", 0.1), ("group", grpW)))
    wPEG = J.get(G_input, "number")("Weight PEG", 1, J.obj(("step", 0.1), ("group", grpW)))
    wROE = J.get(G_input, "number")("Weight ROE", 1, J.obj(("step", 0.1), ("group", grpW)))
    wROA = J.get(G_input, "number")("Weight ROA", 1, J.obj(("step", 0.1), ("group", grpW)))
    wDY = J.get(G_input, "number")("Weight Div Yield", 1, J.obj(("step", 0.1), ("group", grpW)))
    wTP = J.get(G_input, "number")("Weight Target/Price", 1, J.obj(("step", 0.1), ("group", grpW)))
    wF = J.get(G_input, "number")("Weight Piotroski F", 1, J.obj(("step", 0.1), ("group", grpW)))
    wZ = J.get(G_input, "number")("Weight Altman Z", 1, J.obj(("step", 0.1), ("group", grpW)))
    wMF = J.get(G_input, "number")("Weight Magic Formula", 1.5, J.obj(("step", 0.1), ("group", grpW)))
    avKey = J.get(G_input, "text")("Alpha Vantage Key", "your_alpha_vantage_api_key")
    cacheTTL = 86400
    url = J.add(J.add(J.add(J.add("https://www.alphavantage.co/query?function=OVERVIEW", "&symbol="), G_encodeURIComponent(J.get(G_current, "ticker"))), "&apikey="), G_encodeURIComponent(avKey))
    data = J.get(G_request, "http")(url, cacheTTL, J.obj(("accept", "application/json")))
    G_assert((J.get(data, "Symbol") if J.truthy(_t1 := data) else _t1), "Alpha Vantage OVERVIEW failed or quota hit.")
    pe = toNum(J.get(data, "PERatio"))
    fwdPE = toNum(J.get(data, "ForwardPE"))
    pb = toNum(J.get(data, "PriceToBookRatio"))
    peg = toNum(J.get(data, "PEGRatio"))
    roe = toNum(J.get(data, "ReturnOnEquityTTM"))
    roa = toNum(J.get(data, "ReturnOnAssetsTTM"))
    dy = toNum(J.get(data, "DividendYield"))
    tpRatio = (J.div(toNum(J.get(data, "AnalystTargetPrice")), J.get(G_close, J.sub(J.get(G_close, "length"), 1))) if (J.truthy(toNum(J.get(data, "AnalystTargetPrice"))) and J.truthy(J.get(G_close, J.sub(J.get(G_close, "length"), 1)))) else None)
    fApprox = J.add(J.add((1 if J.gt(roe, 0) else 0), (1 if J.gt(roa, 0) else 0)), (1 if J.gt(dy, 0) else 0))
    zApprox = J.add((_t2 if J.truthy(_t2 := roe) else 0), (_t3 if J.truthy(_t3 := roa) else 0))
    earnYield = (J.div(1, pe) if (J.truthy(pe) and J.gt(pe, 0)) else None)
    rocProxy = (J.div(J.add(roe, roa), 2) if ((not J.nullish(roe)) and (not J.nullish(roa))) else (roa if J.nullish(_t4 := roe) else _t4))
    nEY = (normalize(J.mul(earnYield, 100), 0, 20) if (not J.nullish(earnYield)) else None)
    nROC = (normalize(rocProxy, 0, 20) if (not J.nullish(rocProxy)) else None)
    magicFormula = (J.add(J.mul(0.5, nEY), J.mul(0.5, nROC)) if ((not J.nullish(nEY)) and (not J.nullish(nROC))) else None)
    total = 0
    weight = 0
    addPart(J.div(1, (_t5 if J.truthy(_t5 := pe) else 1)), wPE)
    addPart(J.div(1, (_t6 if J.truthy(_t6 := fwdPE) else 1)), wFwdPE)
    addPart(J.div(1, (_t7 if J.truthy(_t7 := pb) else 1)), wPB)
    addPart(J.div(1, (_t8 if J.truthy(_t8 := peg) else 1)), wPEG)
    addPart(roe, wROE)
    addPart(roa, wROA)
    addPart(dy, wDY)
    addPart(tpRatio, wTP)
    addPart(fApprox, wF)
    addPart(zApprox, wZ)
    addPart(magicFormula, wMF)
    composite = (J.div(total, weight) if J.gt(weight, 0) else None)
    textColor = J.get(G_input, "color")("Text Color", "white")
    G_paint_overlay("Valuation Dashboard", J.obj(("position", "bottom_right")), J.obj(("border", "solid var(--border-color) 1px"), ("borderRadius", "6px"), ("background", "var(--background-color)"), ("padding", "6px"), ("rows", J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", J.template("Valuation Dashboard — ", J.get(data, "Symbol"))), ("colspan", 2), ("textAlign", "center"), ("background", "var(--active-element-color)"), ("color", textColor), ("fontSize", "14px"), ("fontWeight", "bold"), ("padding", 6))]))), J.obj(("cells", J.JSArray([J.obj(("text", J.template("Composite Score: ", (J.get(composite, "toFixed")(2) if (not J.nullish(composite)) else "N/A"))), ("colspan", 2), ("textAlign", "center"), ("background", "var(--active-element-color)"), ("color", textColor), ("fontSize", "13px"), ("fontWeight", "bold"), ("padding", 6))]))), J.obj(("cells", J.JSArray([J.obj(("text", "P/E"), ("color", textColor)), J.obj(("text", (J.get(pe, "toFixed")(2) if (not J.nullish(pe)) else "N/A")), ("color", textColor))]))), J.obj(("cells", J.JSArray([J.obj(("text", "Forward P/E"), ("color", textColor)), J.obj(("text", (J.get(fwdPE, "toFixed")(2) if (not J.nullish(fwdPE)) else "N/A")), ("color", textColor))]))), J.obj(("cells", J.JSArray([J.obj(("text", "P/B"), ("color", textColor)), J.obj(("text", (J.get(pb, "toFixed")(2) if (not J.nullish(pb)) else "N/A")), ("color", textColor))]))), J.obj(("cells", J.JSArray([J.obj(("text", "PEG"), ("color", textColor)), J.obj(("text", (J.get(peg, "toFixed")(2) if (not J.nullish(peg)) else "N/A")), ("color", textColor))]))), J.obj(("cells", J.JSArray([J.obj(("text", "ROE %"), ("color", textColor)), J.obj(("text", (J.add(J.get(J.mul(roe, 100), "toFixed")(1), "%") if (not J.nullish(roe)) else "N/A")), ("color", textColor))]))), J.obj(("cells", J.JSArray([J.obj(("text", "ROA %"), ("color", textColor)), J.obj(("text", (J.add(J.get(J.mul(roa, 100), "toFixed")(1), "%") if (not J.nullish(roa)) else "N/A")), ("color", textColor))]))), J.obj(("cells", J.JSArray([J.obj(("text", "Div Yield %"), ("color", textColor)), J.obj(("text", (J.add(J.get(J.mul(dy, 100), "toFixed")(2), "%") if (not J.nullish(dy)) else "N/A")), ("color", textColor))]))), J.obj(("cells", J.JSArray([J.obj(("text", "Target/Price"), ("color", textColor)), J.obj(("text", (J.add(J.get(tpRatio, "toFixed")(2), "x") if (not J.nullish(tpRatio)) else "N/A")), ("color", textColor))]))), J.obj(("cells", J.JSArray([J.obj(("text", "Piotroski F (approx)"), ("color", textColor)), J.obj(("text", J.get(fApprox, "toFixed")(1)), ("color", textColor))]))), J.obj(("cells", J.JSArray([J.obj(("text", "Altman Z (proxy)"), ("color", textColor)), J.obj(("text", J.get(zApprox, "toFixed")(2)), ("color", textColor))]))), J.obj(("cells", J.JSArray([J.obj(("text", "Magic Formula Score"), ("color", textColor)), J.obj(("text", (J.get(magicFormula, "toFixed")(2) if (not J.nullish(magicFormula)) else "N/A")), ("color", textColor))])))]))))


register_store_indicator(
    script,
    name='valuation_dashboard_TS',
    title='Valuation Dashboard',
    developer='Feliks Ba\\u0144ka',
    url='https://trendspider.com/trading-tools-store/indicators/68abad-valuation-dashboard/',
    position='price',
    inputs=[{'id': 'weight_p_e', 'title': 'Weight P/E', 'type': 'number', 'default': 1}, {'id': 'weight_forward_p_e', 'title': 'Weight Forward P/E', 'type': 'number', 'default': 1}, {'id': 'weight_p_b', 'title': 'Weight P/B', 'type': 'number', 'default': 1}, {'id': 'weight_peg', 'title': 'Weight PEG', 'type': 'number', 'default': 1}, {'id': 'weight_roe', 'title': 'Weight ROE', 'type': 'number', 'default': 1}, {'id': 'weight_roa', 'title': 'Weight ROA', 'type': 'number', 'default': 1}, {'id': 'weight_div_yield', 'title': 'Weight Div Yield', 'type': 'number', 'default': 1}, {'id': 'weight_target_price', 'title': 'Weight Target/Price', 'type': 'number', 'default': 1}, {'id': 'weight_piotroski_f', 'title': 'Weight Piotroski F', 'type': 'number', 'default': 1}, {'id': 'weight_altman_z', 'title': 'Weight Altman Z', 'type': 'number', 'default': 1}, {'id': 'weight_magic_formula', 'title': 'Weight Magic Formula', 'type': 'number', 'default': 1.5}, {'id': 'alpha_vantage_key', 'title': 'Alpha Vantage Key', 'type': 'text', 'default': 'your_alpha_vantage_api_key'}],
    outputs=[],
    signals=[],
    requires=['http'],
    parity='aapl_d: both-error, syn_5m: both-error',
)
