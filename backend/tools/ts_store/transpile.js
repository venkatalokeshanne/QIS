// JS -> Python translator for TrendSpider store scripts.
//
// Produces Python that runs on app/indicators/trendspider_store/_runtime,
// preserving JS semantics exactly (every operator goes through js.py
// helpers). Output is checked against TrendSpider's own engine by
// oracle/compare.py, so the translation is verified, not trusted.
//
// usage: node transpile.js <script.js>        -> python source on stdout
'use strict';
const fs = require('fs');
const acorn = require('acorn');

const PY_KEYWORDS = new Set(('False None True and as assert async await break class continue def del elif else ' +
  'except finally for from global if import in is lambda nonlocal not or pass raise return try while with yield ' +
  'match case type print J G _').split(' '));

class TranspileError extends Error {}

function pyStr(s) {
  // JSON string literals are valid Python literals, except lone surrogates.
  let out = JSON.stringify(s);
  const LS = String.fromCharCode(0x2028), PS = String.fromCharCode(0x2029);
  out = out.split(LS).join('\\u2028').split(PS).join('\\u2029');
  // JS strings are UTF-16: an emoji is two code units (length 2, indexes and
  // regex quantifiers see halves). Emit surrogate escapes so the Python str
  // holds the same code units; the runtime converts back on output.
  let res = '';
  for (let i = 0; i < out.length; i++) {
    const c = out.charCodeAt(i);
    res += (c >= 0xd800 && c <= 0xdfff) ? '\\u' + c.toString(16) : out[i];
  }
  return res;
}

function pyNum(v) {
  if (Number.isInteger(v) && Math.abs(v) < 2 ** 53) return String(v);
  if (v === Infinity) return 'J.Infinity';
  if (Number.isNaN(v)) return 'J.NaN';
  let s = String(v);
  if (/e/.test(s) && !/\./.test(s.split('e')[0])) s = s.replace('e', '.0e');
  return s;
}

// ----------------------------------------------------------------------------
// scope analysis
// ----------------------------------------------------------------------------

class FnScope {
  constructor(node, parent) {
    this.node = node; this.parent = parent;
    this.pyNames = new Set(); this.nonlocals = new Set();
    this.varDecls = []; this.tempN = 0;
  }
  claim(base) {
    let name = PY_KEYWORDS.has(base) || /^_[tf]\d+$/.test(base) || base.startsWith('__') ? base + '_' : base;
    name = name.replace(/\$/g, '_S');
    let n = name, k = 2;
    while (this.pyNames.has(n) || isAncestorName(this, n)) n = `${name}_${k++}`;
    this.pyNames.add(n);
    return n;
  }
  temp(prefix = '_t') { const n = `${prefix}${++this.tempN}`; this.pyNames.add(n); return n; }
}
function isAncestorName(fn, n) {
  // Avoid shadowing an outer function's name that inner code also reads:
  // Python closures bind by name, so an inner local with the same name as
  // an outer variable would hide it. Unique names per nesting chain.
  for (let p = fn.parent; p; p = p.parent) if (p.pyNames.has(n)) return true;
  return false;
}
class Block {
  constructor(fn, parent) { this.fn = fn; this.parent = parent; this.names = new Map(); }
  lookup(name) {
    for (let b = this; b; b = b.parent) if (b.names.has(name)) return b.names.get(name);
    return null;
  }
}

class Analyzer {
  constructor() {
    this.refs = new Map();        // Identifier node -> decl | null (global)
    this.declOf = new Map();      // declaring Identifier node -> decl
    this.fnOf = new Map();        // function node -> FnScope
    this.blockOf = new Map();     // node -> Block
    this.globalsUsed = new Set();
    this.globalsAssigned = new Set();
  }
  declare(blk, name, kind, idNode) {
    if (blk.names.has(name)) {
      const d = blk.names.get(name);
      if (idNode) this.declOf.set(idNode, d);
      return d;
    }
    const d = {jsName: name, pyName: blk.fn.claim(name), fn: blk.fn, kind};
    blk.names.set(name, d);
    if (kind === 'var') blk.fn.varDecls.push(d);
    if (idNode) this.declOf.set(idNode, d);
    return d;
  }
  patternNames(p, out = []) {
    if (!p) return out;
    switch (p.type) {
      case 'Identifier': out.push(p); break;
      case 'ObjectPattern': for (const pr of p.properties) this.patternNames(pr.type === 'RestElement' ? pr.argument : pr.value, out); break;
      case 'ArrayPattern': for (const e of p.elements) this.patternNames(e, out); break;
      case 'AssignmentPattern': this.patternNames(p.left, out); break;
      case 'RestElement': this.patternNames(p.argument, out); break;
      case 'MemberExpression': break;
      default: throw new TranspileError('pattern ' + p.type);
    }
    return out;
  }
  hoistVars(body, blk) {
    // `var` anywhere in this function (not nested functions) -> function scope.
    const visit = n => {
      if (!n || typeof n.type !== 'string') return;
      if (/Function/.test(n.type)) return;
      if (n.type === 'VariableDeclaration' && n.kind === 'var')
        for (const d of n.declarations) for (const id of this.patternNames(d.id)) this.declare(blk, id.name, 'var', id);
      for (const k of Object.keys(n)) {
        const v = n[k];
        if (Array.isArray(v)) v.forEach(visit); else if (v && typeof v.type === 'string' && k !== 'type') visit(v);
      }
    };
    visit(body);
  }
  declareBlockLevel(stmts, blk) {
    for (const s of stmts) {
      if (s.type === 'VariableDeclaration' && s.kind !== 'var')
        for (const d of s.declarations) for (const id of this.patternNames(d.id)) this.declare(blk, id.name, s.kind, id);
      if (s.type === 'FunctionDeclaration') this.declare(blk, s.id.name, 'function', s.id);
    }
  }
  analyzeProgram(ast, implicit = []) {
    const fn = new FnScope(ast, null);
    this.fnOf.set(ast, fn);
    const blk = new Block(fn, null);
    this.blockOf.set(ast, blk);
    for (const name of implicit) this.declare(blk, name, 'var', null);
    this.hoistVars(ast.body, blk);
    this.declareBlockLevel(ast.body, blk);
    for (const s of ast.body) this.visit(s, blk);
    this.root = fn;
  }
  ref(id, blk, assigned) {
    const d = blk.lookup(id.name);
    this.refs.set(id, d);
    if (!d) {
      this.globalsUsed.add(id.name);
      if (assigned) this.globalsAssigned.add(id.name);
      return;
    }
    if (assigned && d.fn !== blk.fn) blk.fn.nonlocals.add(d.pyName), this.markNonlocalChain(blk.fn, d);
  }
  markNonlocalChain(fn, d) {
    // intermediate functions don't need nonlocal: Python resolves to the
    // nearest enclosing binding, which is d's function.
  }
  visitPatternTarget(p, blk, isDecl) {
    switch (p.type) {
      case 'Identifier': if (!isDecl) this.ref(p, blk, true); break;
      case 'MemberExpression': this.visit(p, blk); break;
      case 'ObjectPattern':
        for (const pr of p.properties) {
          if (pr.type === 'RestElement') { this.visitPatternTarget(pr.argument, blk, isDecl); continue; }
          if (pr.computed) this.visit(pr.key, blk);
          this.visitPatternTarget(pr.value, blk, isDecl);
        }
        break;
      case 'ArrayPattern': for (const e of p.elements) if (e) this.visitPatternTarget(e, blk, isDecl); break;
      case 'AssignmentPattern': this.visit(p.right, blk); this.visitPatternTarget(p.left, blk, isDecl); break;
      case 'RestElement': this.visitPatternTarget(p.argument, blk, isDecl); break;
      default: throw new TranspileError('target ' + p.type);
    }
  }
  visitFunction(n, blk) {
    const fn = new FnScope(n, blk.fn);
    this.fnOf.set(n, fn);
    const fblk = new Block(fn, blk);
    this.blockOf.set(n, fblk);
    for (const p of n.params) for (const id of this.patternNames(p)) this.declare(fblk, id.name, 'param', id);
    // defaults/destructuring in params evaluate in function scope
    for (const p of n.params) if (p.type !== 'Identifier') this.visitPatternTarget(p, fblk, true);
    if (n.body.type === 'BlockStatement') {
      this.hoistVars(n.body, fblk);
      this.declareBlockLevel(n.body.body, fblk);
      this.blockOf.set(n.body, fblk);
      for (const s of n.body.body) this.visit(s, fblk);
    } else this.visit(n.body, fblk);
  }
  visit(n, blk) {
    if (!n) return;
    switch (n.type) {
      case 'Program': throw new TranspileError('nested program');
      case 'ExpressionStatement': this.visit(n.expression, blk); break;
      case 'ChainExpression': this.visit(n.expression, blk); break;
      case 'Identifier': this.ref(n, blk, false); break;
      case 'Literal': case 'ThisExpression': case 'EmptyStatement': case 'DebuggerStatement': break;
      case 'TemplateLiteral': n.expressions.forEach(e => this.visit(e, blk)); break;
      case 'ArrayExpression': n.elements.forEach(e => this.visit(e, blk)); break;
      case 'ObjectExpression':
        for (const p of n.properties) {
          if (p.type === 'SpreadElement') { this.visit(p.argument, blk); continue; }
          if (p.computed) this.visit(p.key, blk);
          this.visit(p.value, blk);
        }
        break;
      case 'SpreadElement': this.visit(n.argument, blk); break;
      case 'MemberExpression': this.visit(n.object, blk); if (n.computed) this.visit(n.property, blk); break;
      case 'CallExpression': case 'NewExpression': this.visit(n.callee, blk); n.arguments.forEach(a => this.visit(a, blk)); break;
      case 'BinaryExpression': case 'LogicalExpression': this.visit(n.left, blk); this.visit(n.right, blk); break;
      case 'UnaryExpression': this.visit(n.argument, blk); break;
      case 'AwaitExpression': this.visit(n.argument, blk); break;
      case 'UpdateExpression':
        if (n.argument.type === 'Identifier') this.ref(n.argument, blk, true); else this.visit(n.argument, blk);
        break;
      case 'AssignmentExpression':
        this.visit(n.right, blk);
        if (n.left.type === 'Identifier') this.ref(n.left, blk, true); else this.visitPatternTarget(n.left, blk, false);
        break;
      case 'SequenceExpression': n.expressions.forEach(e => this.visit(e, blk)); break;
      case 'ConditionalExpression': this.visit(n.test, blk); this.visit(n.consequent, blk); this.visit(n.alternate, blk); break;
      case 'ArrowFunctionExpression': case 'FunctionExpression': this.visitFunction(n, blk); break;
      case 'FunctionDeclaration': this.visitFunction(n, blk); break;
      case 'VariableDeclaration':
        for (const d of n.declarations) {
          if (d.init) this.visit(d.init, blk);
          this.visitPatternTarget(d.id, blk, true);
          for (const id of this.patternNames(d.id)) this.refs.set(id, blk.lookup(id.name));
        }
        break;
      case 'BlockStatement': {
        const b = new Block(blk.fn, blk);
        this.blockOf.set(n, b);
        this.declareBlockLevel(n.body, b);
        n.body.forEach(s => this.visit(s, b));
        break;
      }
      case 'IfStatement': this.visit(n.test, blk); this.visit(n.consequent, blk); this.visit(n.alternate, blk); break;
      case 'ForStatement': {
        const b = new Block(blk.fn, blk);
        this.blockOf.set(n, b);
        if (n.init && n.init.type === 'VariableDeclaration') this.declareBlockLevel([n.init], b);
        this.visit(n.init, b); this.visit(n.test, b); this.visit(n.update, b); this.visit(n.body, b);
        break;
      }
      case 'ForOfStatement': case 'ForInStatement': {
        const b = new Block(blk.fn, blk);
        this.blockOf.set(n, b);
        this.visit(n.right, blk);
        if (n.left.type === 'VariableDeclaration') {
          this.declareBlockLevel([n.left], b);
          for (const d of n.left.declarations) { this.visitPatternTarget(d.id, b, true); for (const id of this.patternNames(d.id)) this.refs.set(id, b.lookup(id.name)); }
        } else this.visitPatternTarget(n.left, b, false);
        this.visit(n.body, b);
        break;
      }
      case 'WhileStatement': case 'DoWhileStatement': this.visit(n.test, blk); this.visit(n.body, blk); break;
      case 'ReturnStatement': case 'ThrowStatement': this.visit(n.argument, blk); break;
      case 'BreakStatement': case 'ContinueStatement': break;
      case 'LabeledStatement': this.visit(n.body, blk); break;
      case 'SwitchStatement': {
        this.visit(n.discriminant, blk);
        const b = new Block(blk.fn, blk);
        this.blockOf.set(n, b);
        for (const c of n.cases) this.declareBlockLevel(c.consequent, b);
        for (const c of n.cases) { this.visit(c.test, b); c.consequent.forEach(s => this.visit(s, b)); }
        break;
      }
      case 'TryStatement': {
        this.visit(n.block, blk);
        if (n.handler) {
          const b = new Block(blk.fn, blk);
          this.blockOf.set(n.handler, b);
          if (n.handler.param) for (const id of this.patternNames(n.handler.param)) { this.declare(b, id.name, 'let', id); this.refs.set(id, b.lookup(id.name)); }
          if (n.handler.param && n.handler.param.type !== 'Identifier') this.visitPatternTarget(n.handler.param, b, true);
          this.visit(n.handler.body, b);
        }
        this.visit(n.finalizer, blk);
        break;
      }
      default: throw new TranspileError('unsupported node ' + n.type);
    }
  }
}

// ----------------------------------------------------------------------------
// emission
// ----------------------------------------------------------------------------

const BIN = {
  '+': 'J.add', '-': 'J.sub', '*': 'J.mul', '/': 'J.div', '%': 'J.mod', '**': 'J.pow_',
  '<': 'J.lt', '>': 'J.gt', '<=': 'J.le', '>=': 'J.ge',
  '===': 'J.seq', '!==': 'J.sne', '==': 'J.eq', '!=': 'J.ne',
  '|': 'J.bit_or', '&': 'J.bit_and', '^': 'J.bit_xor', '<<': 'J.shl', '>>': 'J.shr', '>>>': 'J.ushr',
};
const BOOL_OPS = new Set(['<', '>', '<=', '>=', '===', '!==', '==', '!=', 'in', 'instanceof']);

class Emitter {
  constructor(an, opts = {}) {
    this.an = an; this.lines = []; this.fnStack = []; this.pre = null; this.loops = [];
    this.opts = opts;
  }
  get fn() { return this.fnStack[this.fnStack.length - 1]; }
  line(ind, s) { this.lines.push('    '.repeat(ind) + s); }
  name(id) {
    if (!this.an.refs.has(id) && !this.an.declOf.has(id)) throw new TranspileError('unresolved identifier node ' + id.name);
    const d = this.an.refs.get(id) || this.an.declOf.get(id);
    if (d) return d.pyName;
    return globalName(id.name);
  }

  // ---- expressions ---------------------------------------------------------
  test(n) {
    // A Python expression whose truthiness equals JS truthiness of n.
    switch (n.type) {
      case 'LogicalExpression':
        if (n.operator === '&&') return `(${this.test(n.left)} and ${this.test(n.right)})`;
        if (n.operator === '||') return `(${this.test(n.left)} or ${this.test(n.right)})`;
        break;
      case 'UnaryExpression':
        if (n.operator === '!') return `(not ${this.test(n.argument)})`;
        break;
      case 'BinaryExpression':
        if (BOOL_OPS.has(n.operator)) return this.expr(n);
        break;
      case 'Literal':
        if (typeof n.value === 'boolean') return n.value ? 'True' : 'False';
        break;
    }
    return `J.truthy(${this.expr(n)})`;
  }
  args(list) {
    return list.map(a => a.type === 'SpreadElement' ? `*J.spread(${this.expr(a.argument)})` : this.expr(a)).join(', ');
  }
  memberKey(n) {
    if (n.computed) {
      if (n.property.type === 'Literal' && typeof n.property.value === 'string') return pyStr(n.property.value);
      return this.expr(n.property);
    }
    return pyStr(n.property.name);
  }
  expr(n) {
    switch (n.type) {
      case 'Identifier': return this.name(n);
      case 'ThisExpression': return 'G["__this__"]';
      case 'Literal':
        if (n.regex) return `J.regex(${pyStr(n.regex.pattern)}, ${pyStr(n.regex.flags)})`;
        if (n.value === null) return 'None';
        if (typeof n.value === 'boolean') return n.value ? 'True' : 'False';
        if (typeof n.value === 'number') return pyNum(n.value);
        if (typeof n.value === 'string') return pyStr(n.value);
        throw new TranspileError('literal ' + typeof n.value);
      case 'TemplateLiteral': {
        const parts = [];
        n.quasis.forEach((q, i) => {
          if (q.value.cooked) parts.push(pyStr(q.value.cooked));
          if (i < n.expressions.length) parts.push(this.expr(n.expressions[i]));
        });
        return `J.template(${parts.join(', ')})`;
      }
      case 'ArrayExpression':
        return `J.JSArray([${n.elements.map(e => e === null ? 'J.undefined' : e.type === 'SpreadElement' ? `*J.spread(${this.expr(e.argument)})` : this.expr(e)).join(', ')}])`;
      case 'ObjectExpression': {
        const items = n.properties.map(p => {
          if (p.type === 'SpreadElement') return `*J.obj_spread(${this.expr(p.argument)})`;
          if (p.kind !== 'init') throw new TranspileError('getter/setter');
          const k = p.computed ? `J.prop_key(${this.expr(p.key)})` : pyStr(p.key.type === 'Identifier' ? p.key.name : String(p.key.value));
          return `(${k}, ${this.expr(p.value)})`;
        });
        return `J.obj(${items.join(', ')})`;
      }
      case 'MemberExpression':
        return `J.${n.optional ? 'oget' : 'get'}(${this.expr(n.object)}, ${this.memberKey(n)})`;
      case 'ChainExpression':
        return `J.chain_end(${this.expr(n.expression)})`;
      case 'CallExpression': {
        const callee = this.expr(n.callee);
        if (n.optional) return `J.ocall(${callee}, ${this.args(n.arguments)})`;
        if (n.callee.type === 'MemberExpression' && n.callee.optional) return `J.call(${callee}${n.arguments.length ? ', ' : ''}${this.args(n.arguments)})`;
        if (this.inChain(n)) return `J.call(${callee}${n.arguments.length ? ', ' : ''}${this.args(n.arguments)})`;
        return `${callee}(${this.args(n.arguments)})`;
      }
      case 'NewExpression':
        return `J.new(${this.expr(n.callee)}${n.arguments.length ? ', ' : ''}${this.args(n.arguments)})`;
      case 'AwaitExpression': return this.expr(n.argument);
      case 'SequenceExpression': return `(${n.expressions.map(e => this.expr(e)).join(', ')})[-1]`;
      case 'ConditionalExpression':
        return `(${this.expr(n.consequent)} if ${this.test(n.test)} else ${this.expr(n.alternate)})`;
      case 'LogicalExpression': {
        const t = this.fn.temp();
        const l = this.expr(n.left), r = this.expr(n.right);
        if (n.operator === '&&') return `(${r} if J.truthy(${t} := ${l}) else ${t})`;
        if (n.operator === '||') return `(${t} if J.truthy(${t} := ${l}) else ${r})`;
        if (n.operator === '??') return `(${r} if J.nullish(${t} := ${l}) else ${t})`;
        throw new TranspileError('logical ' + n.operator);
      }
      case 'BinaryExpression': {
        const op = n.operator;
        // x === null / x == null style checks, kept readable
        const isNull = e => e.type === 'Literal' && e.value === null && !e.regex;
        const isUndef = e => e.type === 'Identifier' && e.name === 'undefined' && !this.an.refs.get(e);
        if ((op === '===' || op === '!==') && (isNull(n.right) || isUndef(n.right) || isNull(n.left) || isUndef(n.left))) {
          const other = (isNull(n.right) || isUndef(n.right)) ? n.left : n.right;
          const lit = (isNull(n.right) || isUndef(n.right)) ? n.right : n.left;
          return `(${this.expr(other)} ${op === '===' ? 'is' : 'is not'} ${isNull(lit) ? 'None' : 'J.undefined'})`;
        }
        if ((op === '==' || op === '!=') && (isNull(n.right) || isUndef(n.right) || isNull(n.left) || isUndef(n.left))) {
          const other = (isNull(n.right) || isUndef(n.right)) ? n.left : n.right;
          return `(${op === '==' ? '' : 'not '}J.nullish(${this.expr(other)}))`;
        }
        if (op === 'in') return `J.has(${this.expr(n.left)}, ${this.expr(n.right)})`;
        if (op === 'instanceof') return `J.instanceof(${this.expr(n.left)}, ${this.expr(n.right)})`;
        const f = BIN[op];
        if (!f) throw new TranspileError('binary ' + op);
        return `${f}(${this.expr(n.left)}, ${this.expr(n.right)})`;
      }
      case 'UnaryExpression': {
        const a = n.argument;
        switch (n.operator) {
          case '!': return `(not ${this.test(a)})`;
          case '-':
            if (a.type === 'Literal' && typeof a.value === 'number') return a.value === 0 ? '-0.0' : `(-${pyNum(a.value)})`;
            return `J.neg(${this.expr(a)})`;
          case '+': return `J.pos(${this.expr(a)})`;
          case '~': return `J.bit_not(${this.expr(a)})`;
          case 'typeof':
            if (a.type === 'Identifier' && !this.an.refs.get(a) && !KNOWN_GLOBALS.has(a.name)) return pyStr('undefined');
            return `J.typeof(${this.expr(a)})`;
          case 'void': return `(${this.expr(a)}, J.undefined)[1]`;
          case 'delete':
            if (a.type !== 'MemberExpression') return 'True';
            return `J.delete(${this.expr(a.object)}, ${this.memberKey(a)})`;
        }
        throw new TranspileError('unary ' + n.operator);
      }
      case 'UpdateExpression': {
        const fnName = n.operator === '++' ? 'J.inc' : 'J.dec';
        const a = n.argument;
        if (a.type === 'Identifier') {
          const v = this.name(a);
          if (n.prefix) return `(${v} := ${fnName}(${v}))`;
          const t = this.fn.temp();
          return `((${t} := J.tonum(${v})), (${v} := ${fnName}(${t})))[0]`;
        }
        if (a.type === 'MemberExpression')
          return `J.update_member(${this.expr(a.object)}, ${this.memberKey(a)}, ${fnName}, ${n.prefix ? 'True' : 'False'})`;
        throw new TranspileError('update target');
      }
      case 'AssignmentExpression': return this.assignExpr(n);
      case 'ArrowFunctionExpression': case 'FunctionExpression': return this.hoistFunction(n, null);
      case 'SpreadElement': throw new TranspileError('spread outside call/array');
      default: throw new TranspileError('unsupported expression ' + n.type);
    }
  }
  inChain(n) { return false; }
  compoundValue(op, cur, rhsNode) {
    const bop = op.slice(0, -1);
    if (bop === '&&') { const t = this.fn.temp(); return `(${this.expr(rhsNode)} if J.truthy(${t} := ${cur}) else ${t})`; }
    if (bop === '||') { const t = this.fn.temp(); return `(${t} if J.truthy(${t} := ${cur}) else ${this.expr(rhsNode)})`; }
    if (bop === '??') { const t = this.fn.temp(); return `(${this.expr(rhsNode)} if J.nullish(${t} := ${cur}) else ${t})`; }
    return `${BIN[bop]}(${cur}, ${this.expr(rhsNode)})`;
  }
  assignExpr(n) {
    const L = n.left;
    if (L.type === 'Identifier') {
      const v = this.name(L);
      const val = n.operator === '=' ? this.expr(n.right) : this.compoundValue(n.operator, v, n.right);
      return `(${v} := ${val})`;
    }
    if (L.type === 'MemberExpression') {
      const o = this.fn.temp(), k = this.fn.temp();
      const oe = `(${o} := ${this.expr(L.object)})`, ke = `(${k} := ${this.memberKey(L)})`;
      if (n.operator === '=') return `J.set(${this.expr(L.object)}, ${this.memberKey(L)}, ${this.expr(n.right)})`;
      return `J.set(${oe}, ${ke}, ${this.compoundValue(n.operator, `J.get(${o}, ${k})`, n.right)})`;
    }
    // destructuring assignment used as expression: do it via a helper def
    const t = this.fn.temp();
    const lines = [];
    this.destructure(L, t, lines, false);
    const f = this.fn.temp('_f');
    this.pre.push({def: f, params: [t], body: [...lines, `return ${t}`], nonlocal: this.namesAssignedIn(L)});
    return `${f}(${this.expr(n.right)})`;
  }
  namesAssignedIn(p) { return this.an.patternNames(p).map(id => this.name(id)); }

  // destructure JS pattern from python expr `src` into statements (strings)
  destructure(p, src, out, isDecl) {
    switch (p.type) {
      case 'Identifier': out.push(`${this.name(p)} = ${src}`); break;
      case 'MemberExpression': out.push(`J.set(${this.expr(p.object)}, ${this.memberKey(p)}, ${src})`); break;
      case 'AssignmentPattern': {
        const t = this.fn.temp();
        out.push(`${t} = ${src}`);
        out.push(`if ${t} is J.undefined:`);
        const sub = [];
        const saved = this.pre; this.pre = [];
        const dv = this.expr(p.right);
        const defs = this.pre; this.pre = saved;
        for (const d of defs) this.pre.push(d);
        out.push(`    ${t} = ${dv}`);
        this.destructure(p.left, t, out, isDecl);
        break;
      }
      case 'ObjectPattern': {
        const t = this.fn.temp();
        out.push(`${t} = J.require_object(${src})`);
        const used = [];
        for (const pr of p.properties) {
          if (pr.type === 'RestElement') {
            out.push(`${this.name(pr.argument)} = J.obj_rest(${t}, [${used.join(', ')}])`);
            continue;
          }
          const key = pr.computed ? `J.prop_key(${this.expr(pr.key)})` : pyStr(pr.key.type === 'Identifier' ? pr.key.name : String(pr.key.value));
          used.push(key);
          this.destructure(pr.value, `J.get(${t}, ${key})`, out, isDecl);
        }
        break;
      }
      case 'ArrayPattern': {
        const t = this.fn.temp();
        out.push(`${t} = J.iter_of(${src})`);
        p.elements.forEach((e, i) => {
          if (!e) return;
          if (e.type === 'RestElement') this.destructure(e.argument, `J.JSArray(${t}[${i}:])`, out, isDecl);
          else this.destructure(e, `(${t}[${i}] if ${i} < len(${t}) else J.undefined)`, out, isDecl);
        });
        break;
      }
      default: throw new TranspileError('destructure ' + p.type);
    }
  }

  hoistFunction(n, forcedName) {
    const fs_ = this.an.fnOf.get(n);
    const name = forcedName || this.fn.temp('_f');
    this.pre.push({fnNode: n, name});
    return name;
  }

  // ---- statements ----------------------------------------------------------
  flushPre(ind) {
    const pre = this.pre; this.pre = [];
    for (const p of pre) {
      if (p.fnNode) this.emitFunction(p.fnNode, p.name, ind);
      else {
        this.line(ind, `def ${p.def}(${p.params.join(', ')}):`);
        const nl = p.nonlocal.filter(x => x);
        if (nl.length) this.line(ind + 1, `nonlocal ${nl.join(', ')}`);
        for (const b of p.body) this.line(ind + 1, b);
      }
    }
  }
  withPre(ind, fn) {
    // translate a statement: collect hoisted defs, emit them first
    const saved = this.pre; this.pre = [];
    const start = this.lines.length;
    fn();
    const body = this.lines.splice(start);
    this.flushPre(ind);
    this.lines.push(...body);
    this.pre = saved;
  }
  block(stmts, ind) {
    const start = this.lines.length;
    // function declarations hoist to the top of their block
    for (const s of stmts) if (s.type === 'FunctionDeclaration') this.emitFunction(s, this.name(s.id), ind);
    for (const s of stmts) if (s.type !== 'FunctionDeclaration') this.stmt(s, ind);
    if (this.lines.length === start) this.line(ind, 'pass');
  }
  body(n, ind) {
    if (n.type === 'BlockStatement') this.block(n.body, ind); else this.block([n], ind);
  }
  stmt(n, ind) {
    switch (n.type) {
      case 'EmptyStatement': return;
      case 'BlockStatement': {
        const start = this.lines.length;
        this.block(n.body, ind);
        // drop a lone `pass` from an empty inline block
        if (this.lines.length === start + 1 && this.lines[start].trim() === 'pass') this.lines.pop();
        return;
      }
      case 'ExpressionStatement': return this.withPre(ind, () => this.exprStmt(n.expression, ind));
      case 'VariableDeclaration': return this.withPre(ind, () => {
        for (const d of n.declarations) {
          if (d.id.type === 'Identifier') {
            const v = this.name(d.id);
            if (d.init && (d.init.type === 'ArrowFunctionExpression' || d.init.type === 'FunctionExpression')) {
              this.hoistFunction(d.init, v);
              continue;
            }
            this.line(ind, `${v} = ${d.init ? this.expr(d.init) : 'J.undefined'}`);
          } else {
            if (!d.init) throw new TranspileError('destructuring declaration without init');
            const out = [];
            this.destructure(d.id, this.expr(d.init), out, true);
            for (const l of out) this.line(ind, l);
          }
        }
      });
      case 'FunctionDeclaration': return this.emitFunction(n, this.name(n.id), ind);
      case 'ReturnStatement': return this.withPre(ind, () => this.line(ind, n.argument ? `return ${this.expr(n.argument)}` : 'return J.undefined'));
      case 'ThrowStatement': return this.withPre(ind, () => this.line(ind, `raise J.js_throw(${this.expr(n.argument)})`));
      case 'IfStatement': return this.withPre(ind, () => this.ifStmt(n, ind, 'if'));
      case 'ForStatement': return this.forStmt(n, ind);
      case 'WhileStatement': return this.withPre(ind, () => {
        this.line(ind, `while ${this.test(n.test)}:`);
        this.loops.push({kind: 'while'});
        this.body(n.body, ind + 1);
        this.loops.pop();
      });
      case 'DoWhileStatement': return this.withPre(ind, () => {
        this.line(ind, 'while True:');
        this.loops.push({kind: 'dowhile'});
        this.body(n.body, ind + 1);
        this.loops.pop();
        this.line(ind + 1, `if not ${this.test(n.test)}:`);
        this.line(ind + 2, 'break');
      });
      case 'ForOfStatement': case 'ForInStatement': return this.withPre(ind, () => {
        const it = n.type === 'ForOfStatement' ? `J.iter_of(${this.expr(n.right)})` : `J.iter_in(${this.expr(n.right)})`;
        const target = n.left.type === 'VariableDeclaration' ? n.left.declarations[0].id : n.left;
        if (target.type === 'Identifier') {
          this.line(ind, `for ${this.name(target)} in ${it}:`);
          this.loops.push({kind: 'for'});
          this.body(n.body, ind + 1);
          this.loops.pop();
        } else {
          const t = this.fn.temp();
          this.line(ind, `for ${t} in ${it}:`);
          const out = [];
          this.destructure(target, t, out, true);
          for (const l of out) this.line(ind + 1, l);
          this.loops.push({kind: 'for'});
          this.body(n.body, ind + 1);
          this.loops.pop();
        }
      });
      case 'BreakStatement':
        if (n.label) throw new TranspileError('labeled break');
        return this.breakStmt(ind);
      case 'ContinueStatement':
        if (n.label) throw new TranspileError('labeled continue');
        return this.continueStmt(ind);
      case 'SwitchStatement': return this.switchStmt(n, ind);
      case 'TryStatement': return this.tryStmt(n, ind);
      case 'LabeledStatement':
        if (n.body.type === 'ExpressionStatement') return this.stmt(n.body, ind);
        throw new TranspileError('label on ' + n.body.type);
      default: throw new TranspileError('unsupported statement ' + n.type);
    }
  }
  exprStmt(e, ind) {
    if (e.type === 'AssignmentExpression') {
      const L = e.left;
      if (L.type === 'Identifier') {
        const v = this.name(L);
        if (e.operator === '=' && (e.right.type === 'ArrowFunctionExpression' || e.right.type === 'FunctionExpression')) {
          const f = this.hoistFunction(e.right, null);
          return this.line(ind, `${v} = ${f}`);
        }
        const val = e.operator === '=' ? this.expr(e.right) : this.compoundValue(e.operator, v, e.right);
        return this.line(ind, `${v} = ${val}`);
      }
      if (L.type === 'MemberExpression') {
        if (e.operator === '=') return this.line(ind, `J.set(${this.expr(L.object)}, ${this.memberKey(L)}, ${this.expr(e.right)})`);
        const simple = x => x.type === 'Identifier' || x.type === 'Literal' || x.type === 'ThisExpression';
        let o = this.expr(L.object), k = this.memberKey(L);
        if (!simple(L.object)) { const t = this.fn.temp(); this.line(ind, `${t} = ${o}`); o = t; }
        if (L.computed && !simple(L.property)) { const t = this.fn.temp(); this.line(ind, `${t} = ${k}`); k = t; }
        return this.line(ind, `J.set(${o}, ${k}, ${this.compoundValue(e.operator, `J.get(${o}, ${k})`, e.right)})`);
      }
      if (e.operator !== '=') throw new TranspileError('compound destructuring');
      const out = [];
      const t = this.fn.temp();
      this.line(ind, `${t} = ${this.expr(e.right)}`);
      this.destructure(L, t, out, false);
      for (const l of out) this.line(ind, l);
      return;
    }
    if (e.type === 'UpdateExpression') {
      const f = e.operator === '++' ? 'J.inc' : 'J.dec';
      if (e.argument.type === 'Identifier') { const v = this.name(e.argument); return this.line(ind, `${v} = ${f}(${v})`); }
      return this.line(ind, `J.update_member(${this.expr(e.argument.object)}, ${this.memberKey(e.argument)}, ${f}, True)`);
    }
    if (e.type === 'LogicalExpression' && (e.operator === '&&' || e.operator === '||')) {
      // `cond && doIt()` as a statement
      this.line(ind, `if ${e.operator === '&&' ? '' : 'not '}${this.test(e.left)}:`);
      this.nonEmpty(ind + 1, () => this.withPre(ind + 1, () => this.exprStmt(e.right, ind + 1)));
      return;
    }
    if (e.type === 'ConditionalExpression') {
      this.line(ind, `if ${this.test(e.test)}:`);
      this.nonEmpty(ind + 1, () => this.withPre(ind + 1, () => this.exprStmt(e.consequent, ind + 1)));
      this.line(ind, 'else:');
      this.nonEmpty(ind + 1, () => this.withPre(ind + 1, () => this.exprStmt(e.alternate, ind + 1)));
      return;
    }
    if (e.type === 'SequenceExpression') { for (const x of e.expressions) this.exprStmt(x, ind); return; }
    if (e.type === 'AwaitExpression') return this.exprStmt(e.argument, ind);
    if (e.type === 'Literal') return; // 'use strict' etc.
    this.line(ind, this.expr(e));
  }
  nonEmpty(ind, fn) {
    const start = this.lines.length;
    fn();
    if (this.lines.length === start) this.line(ind, 'pass');
  }
  ifStmt(n, ind, kw) {
    this.line(ind, `${kw} ${this.test(n.test)}:`);
    this.body(n.consequent, ind + 1);
    if (!n.alternate) return;
    if (n.alternate.type === 'IfStatement') {
      // elif: hoisted defs from the elif test must precede the whole chain,
      // which withPre of the outer if already guarantees.
      return this.ifStmt(n.alternate, ind, 'elif');
    }
    this.line(ind, 'else:');
    this.body(n.alternate, ind + 1);
  }
  forStmt(n, ind) {
    this.withPre(ind, () => {
      if (n.init) {
        if (n.init.type === 'VariableDeclaration') this.stmtNoPre(n.init, ind);
        else this.exprStmt(n.init, ind);
      }
      const loop = {kind: 'for3', update: n.update};
      this.line(ind, `while ${n.test ? this.test(n.test) : 'True'}:`);
      this.loops.push(loop);
      this.body(n.body, ind + 1);
      this.loops.pop();
      if (n.update) this.exprStmt(n.update, ind + 1);
    });
  }
  stmtNoPre(n, ind) {
    for (const d of n.declarations) {
      if (d.id.type !== 'Identifier') throw new TranspileError('for-init destructuring');
      this.line(ind, `${this.name(d.id)} = ${d.init ? this.expr(d.init) : 'J.undefined'}`);
    }
  }
  currentLoop() {
    for (let i = this.loops.length - 1; i >= 0; i--) if (this.loops[i].kind !== 'switch') return {loop: this.loops[i], viaSwitch: i < this.loops.length - 1};
    return {loop: null};
  }
  breakStmt(ind) {
    // break targets the innermost loop OR switch
    this.line(ind, 'break');
  }
  continueStmt(ind) {
    const top = this.loops[this.loops.length - 1];
    if (top && top.kind === 'switch') {
      // leave the switch's single-pass loop, then continue the real loop
      top.needsContinue = true;
      this.line(ind, `${top.flag} = True`);
      this.line(ind, 'break');
      return;
    }
    if (top && top.kind === 'for3' && top.update) this.exprStmt(top.update, ind);
    if (top && top.kind === 'dowhile') throw new TranspileError('continue in do-while');
    this.line(ind, 'continue');
  }
  switchStmt(n, ind) {
    this.withPre(ind, () => {
      const d = this.fn.temp(), k = this.fn.temp(), flag = this.fn.temp('_c');
      this.line(ind, `${d} = ${this.expr(n.discriminant)}`);
      let defaultIdx = -1;
      let first = true;
      n.cases.forEach((c, i) => {
        if (!c.test) { defaultIdx = i; return; }
        this.line(ind, `${first ? 'if' : 'elif'} J.seq(${d}, ${this.expr(c.test)}):`);
        this.line(ind + 1, `${k} = ${i}`);
        first = false;
      });
      const fallback = defaultIdx >= 0 ? defaultIdx : n.cases.length;
      if (first) this.line(ind, `${k} = ${fallback}`);
      else { this.line(ind, 'else:'); this.line(ind + 1, `${k} = ${fallback}`); }
      this.line(ind, `${flag} = False`);
      this.line(ind, 'for _once in (0,):');
      const sw = {kind: 'switch', flag};
      this.loops.push(sw);
      n.cases.forEach((c, i) => {
        if (!c.consequent.length) return;
        this.line(ind + 1, `if ${k} <= ${i}:`);
        this.block(c.consequent, ind + 2);
      });
      this.line(ind + 1, 'pass');
      this.loops.pop();
      if (sw.needsContinue) {
        this.line(ind, `if ${flag}:`);
        this.continueStmt(ind + 1);
      }
    });
  }
  tryStmt(n, ind) {
    this.line(ind, 'try:');
    this.body(n.block, ind + 1);
    if (n.handler) {
      const e = this.fn.temp('_e');
      this.line(ind, `except Exception as ${e}:`);
      if (n.handler.param) {
        if (n.handler.param.type === 'Identifier') this.line(ind + 1, `${this.name(n.handler.param)} = J.catch_value(${e})`);
        else { const out = []; this.destructure(n.handler.param, `J.catch_value(${e})`, out, true); out.forEach(l => this.line(ind + 1, l)); }
      } else this.line(ind + 1, `J.catch_value(${e})`);
      this.body(n.handler.body, ind + 1);
    }
    if (n.finalizer) {
      this.line(ind, 'finally:');
      this.body(n.finalizer, ind + 1);
    }
  }

  emitFunction(n, name, ind) {
    const fs_ = this.an.fnOf.get(n);
    this.fnStack.push(fs_);
    const savedLoops = this.loops; this.loops = [];
    const savedPre = this.pre; this.pre = [];
    const params = [], prologue = [];
    let rest = null;
    n.params.forEach((p, i) => {
      if (p.type === 'Identifier') params.push(`${this.name(p)}=J.undefined`);
      else if (p.type === 'RestElement') { rest = p.argument; }
      else {
        const t = fs_.temp('_p');
        params.push(`${t}=J.undefined`);
        const out = [];
        this.destructure(p, t, out, true);
        prologue.push(...out);
      }
    });
    if (rest) {
      if (rest.type !== 'Identifier') throw new TranspileError('rest destructuring');
      params.push(`*${this.name(rest)}`);
      prologue.unshift(`${this.name(rest)} = J.JSArray(${this.name(rest)})`);
    } else params.push('*_args');
    const header = `def ${name}(${params.join(', ')}):`;
    const bodyStart = this.lines.length;
    const innerInd = ind + 1;
    // body first (so temps/nonlocals are known), then splice in the prologue
    const bodyLines = [];
    const start = this.lines.length;
    if (n.body.type === 'BlockStatement') this.block(n.body.body, innerInd);
    else this.withPre(innerInd, () => this.line(innerInd, `return ${this.expr(n.body)}`));
    const body = this.lines.splice(start);
    const pre = [];
    if (fs_.nonlocals.size) pre.push(`nonlocal ${[...fs_.nonlocals].join(', ')}`);
    for (const d of fs_.varDecls) if (d.kind === 'var' && !n.params.some(p => p.type === 'Identifier' && p.name === d.jsName)) pre.push(`${d.pyName} = J.undefined`);
    // the pre-defs created while emitting default-param expressions:
    const pendingPre = this.pre; this.pre = [];
    this.line(ind, header);
    for (const l of pre) this.line(innerInd, l);
    for (const l of prologue) this.line(innerInd, l);
    const s2 = this.lines.length;
    this.pre = pendingPre; this.flushPre(innerInd);
    this.lines.push(...body.filter((l, i) => !(l.trim() === 'pass' && body.length > 1 && i === body.length - 1 && false)));
    this.pre = savedPre;
    this.loops = savedLoops;
    this.fnStack.pop();
  }
}

// names the runtime supplies (TrendSpider API + JS builtins)
const KNOWN_GLOBALS = new Set();
function globalName(name) { return name === 'undefined' ? 'J.undefined' : 'G_' + name.replace(/\$/g, '_S'); }

function transpile(src, meta = {}) {
  const ast = acorn.parse(src, {ecmaVersion: 'latest', sourceType: 'script', allowAwaitOutsideFunction: true, allowReturnOutsideFunction: true});
  let an = new Analyzer();
  an.analyzeProgram(ast);
  const implicit = [...an.globalsAssigned];
  if (implicit.length) {
    // Assignment to an undeclared name: TrendSpider runs scripts in strict
    // mode inside `with (api)`, where this throws ReferenceError at run time.
    // Keep that behavior: the name exists but reading/writing it raises.
    an = new Analyzer();
    an.analyzeProgram(ast, implicit);
    an.implicitGlobals = implicit;
  }
  const em = new Emitter(an);
  em.fnStack.push(an.root);
  em.pre = [];
  const start = em.lines.length;
  em.block(ast.body, 1);
  const body = em.lines.splice(start);
  const out = [];
  const globals = [...an.globalsUsed].filter(g => g !== 'undefined').sort();
  out.push('def script(G):');
  for (const g of globals) out.push(`    ${globalName(g)} = G[${pyStr(g)}]`);
  for (const d of an.root.varDecls) out.push(`    ${d.pyName} = J.undefined`);
  out.push(...body);
  return {code: out.join('\n') + '\n', globals};
}

module.exports = {transpile, TranspileError};

if (require.main === module) {
  const src = fs.readFileSync(process.argv[2], 'utf8');
  try {
    process.stdout.write(transpile(src).code);
  } catch (e) {
    console.error('TRANSPILE ERROR:', e.message);
    process.exit(2);
  }
}
