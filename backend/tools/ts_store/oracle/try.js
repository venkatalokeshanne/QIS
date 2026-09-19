const {runJob} = require('./run_ts');
const n = 60, t0 = Date.UTC(2024,0,2,14,30)/1000;
const bars = {time:[],open:[],high:[],low:[],close:[],volume:[]};
for (let i=0;i<n;i++){const c=100+10*Math.sin(i/5)+i*0.1; bars.time.push(t0+i*86400); bars.open.push(c-0.5); bars.high.push(c+1); bars.low.push(c-1); bars.close.push(c); bars.volume.push(1000+i);}
(async()=>{
 for (const f of process.argv.slice(2)) {
  const out = await runJob({script: __dirname + '/../clean/' + f, bars});
  console.log(f, out.error || '', Object.keys(out.outSeries||{}), JSON.stringify(out.metadata.inputs).slice(0,300));
  for (const [k,v] of Object.entries(out.outSeries||{})) console.log('  ',k, JSON.stringify(v.slice(0,20)));
 }
})();
