const fs=require('fs'),path=require('path'),acorn=require('acorn'),walk=require('acorn-walk');
const dir=path.join(__dirname,'clean');const cnt={},files={};
const ops={};
for(const f of fs.readdirSync(dir).filter(f=>f.endsWith('.js'))){
 const ast=acorn.parse(fs.readFileSync(path.join(dir,f),'utf8'),{ecmaVersion:'latest',sourceType:'module',allowAwaitOutsideFunction:true,allowReturnOutsideFunction:true});
 walk.full(ast,n=>{cnt[n.type]=(cnt[n.type]||0)+1;(files[n.type]=files[n.type]||new Set()).add(f);
  if(n.type==='BinaryExpression'||n.type==='LogicalExpression'||n.type==='AssignmentExpression'||n.type==='UnaryExpression'||n.type==='UpdateExpression'){const k=n.type[0]+':'+n.operator;ops[k]=(ops[k]||0)+1;}
  if(n.type==='VariableDeclaration'){const k='decl:'+n.kind;ops[k]=(ops[k]||0)+1;}
  if(n.type==='FunctionExpression'||n.type==='ArrowFunctionExpression'||n.type==='FunctionDeclaration'){ if(n.async){ops.async=(ops.async||0)+1} if(n.generator){ops.gen=(ops.gen||0)+1}}
  if(n.type==='MemberExpression'&&n.optional){ops.optchain=(ops.optchain||0)+1}
  if(n.type==='CallExpression'&&n.optional){ops.optcall=(ops.optcall||0)+1}
 });
}
for(const [k,v] of Object.entries(cnt).sort((a,b)=>b[1]-a[1])) console.log(v.toString().padStart(7),String(files[k].size).padStart(4),k);
console.log(ops);
