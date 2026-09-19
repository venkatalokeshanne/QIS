// Batch oracle: node run_batch.js jobs.json results.json
// Runs each job through TrendSpider's own engine (see run_ts.js).
process.on('unhandledRejection', () => {});
process.env.TZ = process.env.TZ || 'America/New_York';
const fs = require('fs');
const {runJob} = require('./run_ts');
const enc = (k, v) => (typeof v === 'number' && !Number.isFinite(v)) ? {__num: String(v)} : (v === undefined ? {__undef: 1} : v);
(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const out = [];
  for (const job of jobs) {
    try {
      const r = await runJob(job);
      const series = {};
      for (const [k, v] of Object.entries(r.outSeries || {})) series[k] = v.map(p => Array.isArray(p) ? p[1] : p);
      out.push({id: job.id, error: r.error || null, series, inputs: (r.metadata || {}).inputs || [],
                appearance: (r.metadata || {}).appearance || {}, signals: (r.metadata || {}).signals || []});
    } catch (e) {
      out.push({id: job.id, error: 'ORACLE CRASH: ' + (e && e.message), series: {}});
    }
  }
  fs.writeFileSync(process.argv[3], JSON.stringify(out, enc));
})();
