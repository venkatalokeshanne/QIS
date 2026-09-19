// Loads TrendSpider's own custom-scripting worker bundle in Node and
// exposes its webpack module loader, so scripts can be computed by the
// real engine as the ground-truth oracle for the Python ports.
const fs = require('fs'), path = require('path'), vm = require('vm');
const BUNDLE = process.env.TS_BUNDLE || 'C:/Users/annev/Downloads/trendspider-automation/data/extraction/runtime_bundle/00_pretty.js';
let cached = null;
function loadEngine() {
  if (cached) return cached;
  let src = fs.readFileSync(BUNDLE, 'utf8');
  const marker = '  const r = self.assert = (e, t) => {';
  if (!src.includes(marker)) throw new Error('bundle layout changed: loader marker not found');
  src = src.replace(marker, '  globalThis.__wpreq = n;\n' + marker);
  const sandbox = {
    console, setTimeout, clearTimeout, setInterval, clearInterval, setImmediate, Promise, URL,
    TextEncoder, TextDecoder, queueMicrotask, structuredClone,
    addEventListener() {}, postMessage() {}, performance,
  };
  sandbox.self = sandbox; sandbox.globalThis = sandbox; sandbox.window = undefined;
  vm.createContext(sandbox);
  vm.runInContext(src, sandbox, {filename: 'ts_engine.js'});
  cached = sandbox.__wpreq;
  return cached;
}
module.exports = {loadEngine};
