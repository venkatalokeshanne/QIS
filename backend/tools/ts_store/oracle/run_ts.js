// Run a TrendSpider store script through TrendSpider's own engine.
// usage: node run_ts.js <job.json>   (job: {script, bars, inputs, ticker, resolution, histories})
// bars: {time:[unix s], open, high, low, close, volume}; histories: {"TICKER|RES": bars}
const fs = require('fs');
const {loadEngine} = require('./load_engine');

const SESSIONS = {
  regular: {identifier: 'us_regular', timezone: 'America/New_York', start: {hours: 9, minutes: 30}, end: {hours: 16, minutes: 0}, lengthMinutes: 390, marketDays: [1, 2, 3, 4, 5]},
  extended: {identifier: 'us_extended', timezone: 'America/New_York', start: {hours: 4, minutes: 0}, end: {hours: 20, minutes: 0}, lengthMinutes: 960, marketDays: [1, 2, 3, 4, 5]},
  pre: {identifier: 'us_pre', timezone: 'America/New_York', start: {hours: 4, minutes: 0}, end: {hours: 9, minutes: 30}, lengthMinutes: 330, marketDays: [1, 2, 3, 4, 5]},
  post: {identifier: 'us_post', timezone: 'America/New_York', start: {hours: 16, minutes: 0}, end: {hours: 20, minutes: 0}, lengthMinutes: 240, marketDays: [1, 2, 3, 4, 5]},
};

async function runJob(job) {
  const eng = loadEngine()(77);
  const b = job.bars;
  const candles = b.time.map((t, i) => [t * 1000, b.open[i], b.high[i], b.low[i], b.close[i], b.volume[i]]);
  const symbolInfo = {
    ticker: job.ticker || 'AAPL', decimals: 2, type: job.assetType || 'stock', hasVolume: true,
    session: SESSIONS.regular, extendedSession: SESSIONS.extended,
    preMarketSession: SESSIONS.pre, postMarketSession: SESSIONS.post,
    industry: job.industry || 'Consumer Electronics', sector: job.sector || 'Technology', root: job.ticker || 'AAPL',
  };
  const histories = job.histories || {};
  const alt = job.alt || {};
  const served = {};
  const altHandler = kind => async (...args) => {
    const list = alt[kind] || [];
    const i = served[kind] = (served[kind] || 0);
    served[kind] = i + 1;
    if (i >= list.length) return {error: `no recorded ${kind} response #${i}`};
    return JSON.parse(JSON.stringify(list[i]));
  };
  const handlers = {
    history: async (ticker, res, opts) => {
      const k = `${ticker}|${res}`;
      if (!histories[k]) return {error: `no history provided for ${k}`};
      return JSON.parse(JSON.stringify(histories[k]));
    },
  };
  for (const kind of ['analyst_ratings', 'crypto_fear', 'dark_pool', 'dividends', 'earnings', 'fred_series', 'insider_trading',
    'market_breadth', 'splits', 'news', 'retail_trading', 'relative_performance', 'short_volume', 'unusual_options',
    'options_schedule', 'options_data_for_expiration', 'options_data_for_all_expirations', 'congress_trading',
    'wallstreetbets', 'seasonality', 'http', 'fundamentals_distribution']) handlers[kind] = altHandler(kind);
  handlers.fundamentals = altHandler('fundamental');
  const out = await eng.calculateScript(fs.readFileSync(job.script, 'utf8'), job.inputs || {}, candles, {
    symbolInfo, resolution: job.resolution || 'D', externalCallsHandlers: handlers,
    neverAppendTime: false, is_ext_hours: false,
  });
  return out;
}

if (require.main === module) {
  const job = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  runJob(job).then(out => {
    const s = JSON.stringify(out, (k, v) => (typeof v === 'number' && !Number.isFinite(v)) ? {__num: String(v)} : v);
    if (process.argv[3]) fs.writeFileSync(process.argv[3], s); else process.stdout.write(s);
  }).catch(e => { console.error(e); process.exit(1); });
}
module.exports = {runJob, SESSIONS};
