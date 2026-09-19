# TrendSpider store indicators -> `*_TS` QIS indicators

Pipeline that turns the TrendSpider store scripts (JavaScript) into the
291 Python indicators in `app/indicators/trendspider_store/`, registered
as `<name>_TS`, and proves them against TrendSpider's own engine.

1. `python clean_sources.py` - strips the store HTML wrapper from
   `trendspider-automation/data/store_indicators/*` into `clean/*.js`
   and writes `index.json` (title / developer / url).
2. `node transpile.js clean/<x>.js` - JS -> Python translator (acorn AST).
   Every operator goes through `_runtime/js.py`, which reproduces JS
   semantics exactly (undefined vs null, holes, UTF-16 strings, `==`,
   truthiness, toFixed/Math.round rounding, lexicographic sort, ...).
   `node transpile_all.js` writes all translations to `out_py/`.
3. `_runtime/api.py` is TrendSpider's scripting API ported from TrendSpider's
   own client-side engine (sma/ema/rsi/atr/wildma/..., paint, for_every,
   land_points_onto_series, inputs, request.*). Note TrendSpider's
   conventions: ema seeds from the first value (not an SMA), atr's Wilder
   smoothing starts at 0, rsi uses wildma seeded with a single value.
4. **Oracle**: `oracle/load_engine.js` loads TrendSpider's own scripting
   worker bundle (captured by `trendspider-automation/scripts/capture_scripting_runtime.py`,
   kept outside this repo) in Node. `python oracle/compare.py` runs every
   original script through it and the Python translation through the
   runtime on the same bars / histories / alt-data fixtures and compares
   every output value. Report: `oracle/parity_report.json`.
5. `python build_modules.py` (from `backend/`) - writes the final modules,
   each carrying its inputs, outputs and parity status.

Parity (AAPL daily from TrendSpider + synthetic 5-minute bars, 582 runs):
542 bit-identical, 35 fail with TrendSpider's identical error (mostly a
script refusing the timeframe, e.g. "intraday only"), 3 differ only in the
last floating-point bit (V8's Math.pow/sin/cos vs the C runtime; exp/log
are ported bit-exact from V8's fdlibm), and 2 runs (one script, which uses Math.random) are
nondeterministic by design.
