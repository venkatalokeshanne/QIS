// Inventory every global/free identifier and namespaced API the scripts use,
// so the runtime implements exactly what is needed -- nothing guessed.
const fs = require('fs'), path = require('path');
const acorn = require('acorn'), walk = require('acorn-walk');
const dir = path.join(__dirname, 'clean');
const freq = {}, ns = {}, parseFail = [];
const NAMESPACES = new Set(['request','current','constants','input','indicators','market','Math','JSON','Object','Array','Number','String','Date','console','moment']);
for (const f of fs.readdirSync(dir)) {
  const src = fs.readFileSync(path.join(dir, f), 'utf8');
  let ast;
  try { ast = acorn.parse(src, {ecmaVersion: 'latest', sourceType: 'module', allowAwaitOutsideFunction: true, allowReturnOutsideFunction: true}); }
  catch (e) { parseFail.push(`${f}: ${e.message}`); continue; }
  const declared = new Set(), used = new Set(), members = new Set();
  walk.full(ast, n => {
    if (n.type === 'VariableDeclarator' && n.id.type === 'Identifier') declared.add(n.id.name);
    if ((n.type === 'FunctionDeclaration') && n.id) declared.add(n.id.name);
    if (['FunctionDeclaration','FunctionExpression','ArrowFunctionExpression'].includes(n.type))
      for (const p of n.params) walk.full(p, q => { if (q.type === 'Identifier') declared.add(q.name); });
    if (n.type === 'MemberExpression' && n.object.type === 'Identifier' && NAMESPACES.has(n.object.name) && !n.computed)
      members.add(`${n.object.name}.${n.property.name}`);
  });
  walk.ancestor(ast, {Identifier(n, st, anc) {
    const p = anc[anc.length - 2];
    if (p && p.type === 'MemberExpression' && p.property === n && !p.computed) return;
    if (p && p.type === 'Property' && p.key === n && !p.computed) return;
    used.add(n.name);
  }});
  for (const u of used) if (!declared.has(u)) freq[u] = (freq[u] || 0) + 1;
  for (const m of members) ns[m] = (ns[m] || 0) + 1;
}
const sort = o => Object.entries(o).sort((a, b) => b[1] - a[1]);
console.log('PARSE FAILURES:', parseFail.length); parseFail.forEach(x => console.log('  ', x));
console.log('\nFREE IDENTIFIERS (files using):'); console.log(sort(freq).map(([k, v]) => `${k}:${v}`).join('  '));
console.log('\nNAMESPACED APIS:'); console.log(sort(ns).map(([k, v]) => `${k}:${v}`).join('  '));
