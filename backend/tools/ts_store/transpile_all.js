const fs=require('fs'),path=require('path');const {transpile}=require('./transpile');
const dir=path.join(__dirname,'clean'),out=path.join(__dirname,'out_py');let ok=0;const errs={};
for(const f of fs.readdirSync(dir)){try{const r=transpile(fs.readFileSync(path.join(dir,f),'utf8'));fs.writeFileSync(path.join(out,f.replace(/\.js$/,'.py')),'from app.indicators.trendspider_store._runtime import js as J\n\n'+r.code);ok++;}catch(e){const k=e.message.slice(0,60);(errs[k]=errs[k]||[]).push(f);}}
console.log('ok',ok);for(const[k,v]of Object.entries(errs))console.log(v.length,k,v.slice(0,3).join(' '));
