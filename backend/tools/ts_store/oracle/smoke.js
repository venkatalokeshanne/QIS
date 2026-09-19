const {loadEngine} = require('./load_engine');
const req = loadEngine();
const eng = req(77);
console.log(Object.keys(eng));
