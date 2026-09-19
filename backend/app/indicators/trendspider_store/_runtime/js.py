"""
JavaScript value semantics for the transpiled TrendSpider store scripts.

The *_TS indicators are mechanical translations of TrendSpider's own
JavaScript. JS and Python disagree on details that change results --
`a[i-1]` at i=0 is `undefined` in JS but the LAST element in Python,
`null + 1` is 1, `[] ` is truthy, `Math.round(2.5)` is 3, `(2.5).toFixed(0)`
is "3", `===` distinguishes true from 1, default sort is lexicographic.
Every operator in the generated code goes through these helpers so the
Python reproduces the JS exactly, not approximately.

Conventions:
  * JS `null`      -> Python None
  * JS `undefined` -> the `undefined` singleton below
  * numbers        -> int/float (bool is kept distinct wherever JS does)
  * arrays         -> JSArray (a list subclass with JS indexing)
  * objects        -> JSObject (a dict subclass with string keys)
"""

from __future__ import annotations

import functools
import json as _json
import math
import random as _random
import re as _re
import time as _time
from decimal import ROUND_HALF_UP, Decimal

from app.indicators.trendspider_store._runtime import fdlibm as _fd

NaN = float("nan")
Infinity = float("inf")


class _Undefined:
    _inst = None

    def __new__(cls):
        if cls._inst is None:
            cls._inst = super().__new__(cls)
        return cls._inst

    def __repr__(self):
        return "undefined"

    def __bool__(self):
        return False


undefined = _Undefined()


class _Hole:
    """An array slot that was never assigned (or was deleted): reads as
    undefined, but forEach/map/filter/... skip it, as in JS."""

    def __repr__(self):
        return "<hole>"

    def __bool__(self):
        return False


HOLE = _Hole()


class _Short:
    """Marker propagated through an optional chain once it short-circuits."""

    def __repr__(self):
        return "<short>"


SHORT = _Short()


class JSError(Exception):
    """A JS `throw`. `value` is whatever was thrown."""

    def __init__(self, value):
        self.value = value
        super().__init__(to_str(get(value, "message")) if is_object(value) else to_str(value))


class Unsupported(Exception):
    """The script needs something this runtime cannot provide."""


def make_error(message, name="Error"):
    return JSObject(name=name, message=to_str(message) if message is not undefined else "")


def js_throw(value):
    return JSError(value)


def type_error(msg):
    return JSError(make_error(msg, "TypeError"))


def catch_value(exc):
    """What a JS `catch (e)` binds for a Python-side exception."""
    if isinstance(exc, JSError):
        return exc.value
    if isinstance(exc, Unsupported):
        raise exc  # never swallow a capability gap
    return make_error(str(exc), type(exc).__name__)


# ----------------------------------------------------------------------------
# containers
# ----------------------------------------------------------------------------


class JSArray(list):
    __slots__ = ("props",)

    def __init__(self, *a):
        super().__init__(*a)
        self.props = None

    def __repr__(self):
        return "JSArray(" + list.__repr__(self) + ")"

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return self is other

    def __ne__(self, other):
        return self is not other


class JSObject(dict):
    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return self is other

    def __ne__(self, other):
        return self is not other

    def __repr__(self):
        return "JSObject(" + dict.__repr__(self) + ")"


def arr(*items):
    return JSArray(items)


def obj(*pairs):
    o = JSObject()
    for k, v in pairs:
        o[prop_key(k)] = v
    return o


def _unhole(items):
    return [undefined if x is HOLE else x for x in items]


def spread(v):
    """Elements of an iterable for `...v`."""
    if isinstance(v, str):
        return list(v)
    if isinstance(v, (list, tuple)):
        return _unhole(v)
    if isinstance(v, JSIterator):
        return list(v.items)
    if v is None or v is undefined:
        raise type_error("object is not iterable")
    if isinstance(v, dict):  # object spread into object literal
        return list(v.items())
    raise type_error(f"{to_str(v)} is not iterable")


def obj_spread(v):
    if v is None or v is undefined:
        return []
    if isinstance(v, JSArray):
        return [(str(i), x) for i, x in enumerate(v)]
    if isinstance(v, dict):
        return list(v.items())
    if isinstance(v, str):
        return [(str(i), c) for i, c in enumerate(v)]
    return []


class JSIterator:
    """What arr.keys()/entries()/values() return -- consumed by for..of/spread."""

    def __init__(self, items):
        self.items = list(items)

    def __iter__(self):
        return iter(self.items)


# ----------------------------------------------------------------------------
# type predicates / conversions
# ----------------------------------------------------------------------------


def is_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def is_object(v):
    return isinstance(v, (dict, list)) or callable(v) or isinstance(v, (JSDate, JSRegExp))


def nullish(v):
    return v is None or v is undefined


def truthy(v):
    if v is True:
        return True
    if v is False or v is None or v is undefined:
        return False
    if isinstance(v, (int, float)):
        return v == v and v != 0
    if isinstance(v, str):
        return v != ""
    return True


def not_(v):
    return not truthy(v)


def typeof(v):
    if v is undefined:
        return "undefined"
    if v is None:
        return "object"
    if isinstance(v, bool):
        return "boolean"
    if isinstance(v, (int, float)):
        return "number"
    if isinstance(v, str):
        return "string"
    if callable(v) and not isinstance(v, (dict, list)):
        return "function"
    return "object"


def to_primitive(v, hint="default"):
    if isinstance(v, JSArray):
        return array_join(v, ",")
    if isinstance(v, JSDate):
        return v.ms if hint == "number" else v.to_string()
    if isinstance(v, JSObject):
        vo = v.get("valueOf")
        if callable(vo):
            return vo()
        ts = v.get("toString")
        if callable(ts):
            return ts()
        return "[object Object]"
    if isinstance(v, JSRegExp):
        return v.source_str()
    if isinstance(v, Moment):
        return v.value_of() if hint != "string" else v.format()
    if callable(v) and not isinstance(v, (int, float, str, bool)):
        return "function () { [native code] }"
    return v


_NUM_RE = _re.compile(r"^[+-]?(?:(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?|Infinity)$")


def to_number(v):
    if v is None:
        return 0
    if v is undefined:
        return NaN
    if isinstance(v, bool):
        return 1 if v else 0
    if isinstance(v, (int, float)):
        return v
    if isinstance(v, str):
        s = v.strip()
        if s == "":
            return 0
        if _NUM_RE.match(s):
            f = float(s)
            return int(f) if f.is_integer() and abs(f) < 2**53 and "e" not in s.lower() and "." not in s else f
        low = s.lower()
        try:
            if low.startswith("0x"):
                return int(s[2:], 16)
            if low.startswith("0b"):
                return int(s[2:], 2)
            if low.startswith("0o"):
                return int(s[2:], 8)
        except ValueError:
            return NaN
        return NaN
    return to_number(to_primitive(v, "number"))


tonum = to_number


def _num_to_str(x):
    if isinstance(x, bool):
        return "true" if x else "false"
    if isinstance(x, int):
        if abs(x) >= 10**21:
            return _num_to_str(float(x))
        return str(x)
    if x != x:
        return "NaN"
    if x == math.inf:
        return "Infinity"
    if x == -math.inf:
        return "-Infinity"
    if x == 0:
        return "0"
    if x.is_integer() and abs(x) < 1e21:
        return str(int(x))
    r = repr(x)  # shortest round-trip digits, like JS
    if "e" in r or "E" in r:
        mant, exp = r.lower().split("e")
        exp = int(exp)
    else:
        mant, exp = r, 0
    neg = mant.startswith("-")
    mant = mant.lstrip("-")
    if "." in mant:
        ip, fp = mant.split(".")
    else:
        ip, fp = mant, ""
    digits = (ip + fp).lstrip("0")
    # decimal exponent n such that value = 0.digits * 10^n
    n = len(ip) + exp if ip != "0" else exp - (len(fp) - len(fp.lstrip("0")))
    digits = digits.rstrip("0") or "0"
    k = len(digits)
    if k <= n <= 21:
        s = digits + "0" * (n - k)
    elif 0 < n <= 21:
        s = digits[:n] + "." + digits[n:]
    elif -6 < n <= 0:
        s = "0." + "0" * (-n) + digits
    else:
        e = n - 1
        es = ("+" if e >= 0 else "-") + str(abs(e))
        s = digits[0] + ("." + digits[1:] if k > 1 else "") + "e" + es
    return ("-" if neg else "") + s


def to_str(v):
    if isinstance(v, str):
        return v
    if v is None:
        return "null"
    if v is undefined:
        return "undefined"
    if isinstance(v, (bool, int, float)):
        return _num_to_str(v)
    p = to_primitive(v, "string")
    if p is v:
        return "[object]"
    return to_str(p)


def prop_key(k):
    if isinstance(k, str):
        return k
    if isinstance(k, float) and k.is_integer():
        return str(int(k))
    return to_str(k)


def to_int32(v):
    n = to_number(v)
    if n != n or n in (math.inf, -math.inf):
        return 0
    n = int(n) & 0xFFFFFFFF
    return n - 0x100000000 if n >= 0x80000000 else n


def to_uint32(v):
    n = to_number(v)
    if n != n or n in (math.inf, -math.inf):
        return 0
    return int(n) & 0xFFFFFFFF


def _index(k):
    """Integer array index for key k, or None if k is not an index."""
    if isinstance(k, bool):
        return None
    if isinstance(k, int):
        return k
    if isinstance(k, float):
        return int(k) if k.is_integer() else None
    if isinstance(k, str) and k.isdigit() and (k == "0" or not k.startswith("0")):
        return int(k)
    return None


# ----------------------------------------------------------------------------
# operators
# ----------------------------------------------------------------------------


def add(a, b):
    ta, tb = type(a), type(b)
    if (ta is int or ta is float) and (tb is int or tb is float):
        return a + b
    if ta is str and tb is str:
        return a + b
    pa, pb = to_primitive(a), to_primitive(b)
    if isinstance(pa, str) or isinstance(pb, str):
        return to_str(pa) + to_str(pb)
    return to_number(pa) + to_number(pb)


def _nums(a, b):
    ta, tb = type(a), type(b)
    if (ta is int or ta is float) and (tb is int or tb is float):
        return a, b
    return to_number(a), to_number(b)


def sub(a, b):
    ta, tb = type(a), type(b)
    if (ta is float or ta is int) and (tb is float or tb is int):
        return a - b
    a, b = to_number(a), to_number(b)
    return a - b


def mul(a, b):
    a, b = _nums(a, b)
    try:
        return a * b
    except OverflowError:
        return math.inf if (a > 0) == (b > 0) else -math.inf


def div(a, b):
    a, b = _nums(a, b)
    if b == 0:
        if a != a or a == 0:
            return NaN
        neg = (a < 0) != (math.copysign(1.0, b) < 0)
        return -math.inf if neg else math.inf
    try:
        return a / b
    except OverflowError:
        return math.inf if (a > 0) == (b > 0) else -math.inf


def mod(a, b):
    a, b = _nums(a, b)
    if b == 0 or a != a or b != b or a in (math.inf, -math.inf):
        return NaN
    if b in (math.inf, -math.inf):
        return a
    if isinstance(a, int) and isinstance(b, int):
        r = abs(a) % abs(b)
        return -r if a < 0 else r
    return math.fmod(a, b)


def pow_(a, b):
    a, b = _nums(a, b)
    if b != b:
        return NaN
    if b == 0:
        return 1
    if b == 2:
        return a * a  # V8's Math.pow(x, 2) is exactly x*x; C pow() is not always
    try:
        r = a**b
    except ZeroDivisionError:
        return math.inf
    except OverflowError:
        return math.inf
    if isinstance(r, complex):
        return NaN
    return r


def neg(a):
    a = to_number(a)
    if a == 0 and isinstance(a, int):
        return -0.0
    return -a


def pos(a):
    return to_number(a)


def inc(a):
    if type(a) is int or type(a) is float:
        return a + 1
    return to_number(a) + 1


def dec(a):
    return to_number(a) - 1


def bit_or(a, b):
    return to_int32(to_int32(a) | to_int32(b))


def bit_and(a, b):
    return to_int32(to_int32(a) & to_int32(b))


def bit_xor(a, b):
    return to_int32(to_int32(a) ^ to_int32(b))


def bit_not(a):
    return to_int32(~to_int32(a))


def shl(a, b):
    return to_int32(to_int32(a) << (to_uint32(b) & 31))


def shr(a, b):
    return to_int32(a) >> (to_uint32(b) & 31)


def ushr(a, b):
    return to_uint32(a) >> (to_uint32(b) & 31)


def _cmp_prims(a, b):
    ta, tb = type(a), type(b)
    if (ta is int or ta is float) and (tb is int or tb is float):
        return a, b
    pa, pb = to_primitive(a, "number"), to_primitive(b, "number")
    if isinstance(pa, str) and isinstance(pb, str):
        return pa, pb
    return to_number(pa), to_number(pb)


def lt(a, b):
    ta, tb = type(a), type(b)
    if (ta is float or ta is int) and (tb is float or tb is int):
        return a < b
    a, b = _cmp_prims(a, b)
    return a < b


def gt(a, b):
    ta, tb = type(a), type(b)
    if (ta is float or ta is int) and (tb is float or tb is int):
        return a > b
    a, b = _cmp_prims(a, b)
    return a > b


def le(a, b):
    ta, tb = type(a), type(b)
    if (ta is float or ta is int) and (tb is float or tb is int):
        return a <= b
    a, b = _cmp_prims(a, b)
    if a != a or b != b:
        return False
    return a <= b


def ge(a, b):
    ta, tb = type(a), type(b)
    if (ta is float or ta is int) and (tb is float or tb is int):
        return a >= b
    a, b = _cmp_prims(a, b)
    if a != a or b != b:
        return False
    return a >= b


def seq(a, b):
    """`===`"""
    ta, tb = type(a), type(b)
    if ta is bool or tb is bool:
        return ta is tb and a == b
    if (ta is int or ta is float) and (tb is int or tb is float):
        return a == b
    if ta is str and tb is str:
        return a == b
    if isinstance(a, (list, dict)) or isinstance(b, (list, dict)):
        return a is b
    if a is None or b is None or a is undefined or b is undefined:
        return a is b
    if isinstance(a, JSDate) or isinstance(b, JSDate) or isinstance(a, Moment) or isinstance(b, Moment):
        return a is b
    if ta is not tb:
        return False
    return a == b


def sne(a, b):
    return not seq(a, b)


def eq(a, b):
    """`==`"""
    if nullish(a) and nullish(b):
        return True
    if nullish(a) or nullish(b):
        return False
    if isinstance(a, bool):
        a = 1 if a else 0
    if isinstance(b, bool):
        b = 1 if b else 0
    na, nb = is_number(a), is_number(b)
    if na and nb:
        return a == b
    if isinstance(a, str) and isinstance(b, str):
        return a == b
    if na and isinstance(b, str):
        return a == to_number(b)
    if nb and isinstance(a, str):
        return to_number(a) == b
    ao, bo = is_object(a), is_object(b)
    if ao and bo:
        return a is b
    if ao:
        return eq(to_primitive(a), b)
    if bo:
        return eq(a, to_primitive(b))
    return False


def ne(a, b):
    return not eq(a, b)


def has(key, o):
    """`key in o`"""
    if isinstance(o, JSArray):
        i = _index(key)
        if i is not None:
            return 0 <= i < len(o)
        return prop_key(key) == "length" or bool(o.props and prop_key(key) in o.props)
    if isinstance(o, dict):
        return prop_key(key) in o
    raise type_error("Cannot use 'in' operator")


def delete(o, key):
    if isinstance(o, dict):
        o.pop(prop_key(key), None)
    elif isinstance(o, JSArray):
        i = _index(key)
        if i is not None and 0 <= i < len(o):
            list.__setitem__(o, i, HOLE)
    return True


def template(*parts):
    return "".join(p if isinstance(p, str) else to_str(p) for p in parts)


# ----------------------------------------------------------------------------
# property access
# ----------------------------------------------------------------------------


def get(o, k):
    t = type(o)
    if t is JSArray:
        tk = type(k)
        if tk is int:
            if 0 <= k < len(o):
                v = list.__getitem__(o, k)
                return undefined if v is HOLE else v
            return undefined
        i = _index(k)
        if i is not None:
            if 0 <= i < len(o):
                v = list.__getitem__(o, i)
                return undefined if v is HOLE else v
            return undefined
        k = prop_key(k)
        if k == "length":
            return len(o)
        if o.props and k in o.props:
            return o.props[k]
        m = ARRAY_METHODS.get(k)
        if m is not None:
            return functools.partial(m, o)
        return undefined
    if t is JSObject or isinstance(o, dict):
        v = o.get(prop_key(k), undefined)
        if v is undefined and prop_key(k) in OBJECT_PROTO:
            return functools.partial(OBJECT_PROTO[prop_key(k)], o)
        return v
    if t is str:
        i = _index(k)
        if i is not None:
            return o[i] if 0 <= i < len(o) else undefined
        k = prop_key(k)
        if k == "length":
            return len(o)
        m = STRING_METHODS.get(k)
        if m is not None:
            return functools.partial(m, o)
        return undefined
    if o is SHORT:
        return SHORT
    if o is None or o is undefined:
        raise type_error(f"Cannot read properties of {to_str(o)} (reading '{prop_key(k)}')")
    if t is int or t is float or t is bool:
        m = NUMBER_METHODS.get(prop_key(k))
        if m is not None:
            return functools.partial(m, o)
        return undefined
    if isinstance(o, list):  # plain list from Python-side code
        return get(JSArray(o), k)
    attr = getattr(o, "js_get", None)
    if attr is not None:
        return attr(prop_key(k))
    if callable(o):
        k = prop_key(k)
        if k == "apply":
            return lambda _this=undefined, args=JSArray(), *r: o(*(args if isinstance(args, list) else []))
        if k == "call":
            return lambda _this=undefined, *args: o(*args)
        if k == "bind":
            return lambda _this=undefined, *bound: (lambda *args: o(*bound, *args))
        v = getattr(o, k, undefined)
        return v
    return undefined


def oget(o, k):
    """`o?.k`"""
    if o is None or o is undefined or o is SHORT:
        return SHORT
    return get(o, k)


def ocall(f, *args):
    """`f?.(...)`"""
    if f is None or f is undefined or f is SHORT:
        return SHORT
    return f(*args)


def call(f, *args):
    if f is SHORT:
        return SHORT
    if not callable(f):
        raise type_error(f"{typeof(f)} is not a function")
    return f(*args)


def chain_end(v):
    return undefined if v is SHORT else v


def set(o, k, v):
    t = type(o)
    if t is JSArray:
        i = _index(k)
        if i is not None:
            n = len(o)
            if i < n:
                list.__setitem__(o, i, v)
            else:
                if i > n:
                    o.extend([HOLE] * (i - n))
                o.append(v)
            return v
        k = prop_key(k)
        if k == "length":
            n = int(to_number(v))
            if n < len(o):
                del o[n:]
            else:
                o.extend([HOLE] * (n - len(o)))
            return v
        if o.props is None:
            o.props = {}
        o.props[k] = v
        return v
    if isinstance(o, dict):
        o[prop_key(k)] = v
        return v
    if o is None or o is undefined:
        raise type_error(f"Cannot set properties of {to_str(o)} (setting '{prop_key(k)}')")
    if isinstance(o, list):
        i = _index(k)
        if i is not None:
            while len(o) <= i:
                o.append(undefined)
            o[i] = v
        return v
    setter = getattr(o, "js_set", None)
    if setter is not None:
        setter(prop_key(k), v)
    return v


def update_member(o, k, fn, prefix):
    old = to_number(get(o, k))
    new = fn(old)
    set(o, k, new)
    return new if prefix else old


# ----------------------------------------------------------------------------
# iteration
# ----------------------------------------------------------------------------


def iter_of(v):
    if isinstance(v, (list, tuple)):
        return _unhole(v)
    if isinstance(v, str):
        return list(v)
    if isinstance(v, JSIterator):
        return v.items
    if v is None or v is undefined:
        raise type_error(f"{to_str(v)} is not iterable")
    it = getattr(v, "js_iter", None)
    if it is not None:
        return it()
    raise type_error("object is not iterable")


def iter_in(v):
    if isinstance(v, JSArray):
        keys = [str(i) for i in range(len(v)) if list.__getitem__(v, i) is not HOLE]
        return keys + (list(v.props) if v.props else [])
    if isinstance(v, dict):
        return list(v.keys())
    if isinstance(v, str):
        return [str(i) for i in range(len(v))]
    return []


# ----------------------------------------------------------------------------
# Array.prototype
# ----------------------------------------------------------------------------


def _cb(fn):
    if not callable(fn):
        raise type_error(f"{to_str(fn)} is not a function")
    return fn


def _rel(i, n, default):
    if i is undefined:
        return default
    i = to_number(i)
    if i != i:
        return 0
    if i in (math.inf,):
        return n
    if i == -math.inf:
        return 0
    i = int(i)
    return max(n + i, 0) if i < 0 else min(i, n)


def a_push(a, *items):
    a.extend(items)
    return len(a)


def a_pop(a):
    return a.pop() if a else undefined


def a_shift(a):
    return a.pop(0) if a else undefined


def a_unshift(a, *items):
    a[0:0] = items
    return len(a)


def a_slice(a, start=undefined, end=undefined):
    n = len(a)
    s = _rel(start, n, 0)
    e = _rel(end, n, n)
    return JSArray(list.__getitem__(a, slice(s, e)) if e > s else [])


def a_splice(a, start=undefined, delete_count=undefined, *items):
    n = len(a)
    s = _rel(start, n, 0)
    if start is undefined:
        return JSArray()
    if delete_count is undefined:
        dc = n - s
    else:
        dc = max(0, min(int(to_number(delete_count) if to_number(delete_count) == to_number(delete_count) else 0), n - s))
    removed = JSArray(list.__getitem__(a, slice(s, s + dc)))
    list.__setitem__(a, slice(s, s + dc), list(items))
    return removed


def _present(a, i):
    return list.__getitem__(a, i) is not HOLE


def a_map(a, fn, *_):
    fn = _cb(fn)
    return JSArray([fn(list.__getitem__(a, i), i, a) if _present(a, i) else HOLE for i in range(len(a))])


def a_forEach(a, fn, *_):
    fn = _cb(fn)
    n = len(a)
    for i in range(n):
        if i >= len(a):
            break
        if _present(a, i):
            fn(list.__getitem__(a, i), i, a)
    return undefined


def a_filter(a, fn, *_):
    fn = _cb(fn)
    out = JSArray()
    for i in range(len(a)):
        v = list.__getitem__(a, i)
        if v is not HOLE and truthy(fn(v, i, a)):
            out.append(v)
    return out


def a_reduce(a, fn, *init):
    fn = _cb(fn)
    n = len(a)
    idx = [i for i in range(n) if _present(a, i)]
    if init:
        acc = init[0]
    else:
        if not idx:
            raise type_error("Reduce of empty array with no initial value")
        acc, idx = list.__getitem__(a, idx[0]), idx[1:]
    for i in idx:
        acc = fn(acc, list.__getitem__(a, i), i, a)
    return acc


def a_reduceRight(a, fn, *init):
    fn = _cb(fn)
    n = len(a)
    if init:
        acc, start = init[0], n - 1
    else:
        if n == 0:
            raise type_error("Reduce of empty array with no initial value")
        acc, start = list.__getitem__(a, n - 1), n - 2
    for i in range(start, -1, -1):
        acc = fn(acc, list.__getitem__(a, i), i, a)
    return acc


def a_find(a, fn, *_):
    fn = _cb(fn)
    for i in range(len(a)):
        v = get(a, i)
        if truthy(fn(v, i, a)):
            return v
    return undefined


def a_findIndex(a, fn, *_):
    fn = _cb(fn)
    for i in range(len(a)):
        if truthy(fn(get(a, i), i, a)):
            return i
    return -1


def a_findLast(a, fn, *_):
    fn = _cb(fn)
    for i in range(len(a) - 1, -1, -1):
        v = list.__getitem__(a, i)
        if truthy(fn(v, i, a)):
            return v
    return undefined


def a_findLastIndex(a, fn, *_):
    fn = _cb(fn)
    for i in range(len(a) - 1, -1, -1):
        if truthy(fn(list.__getitem__(a, i), i, a)):
            return i
    return -1


def a_some(a, fn, *_):
    fn = _cb(fn)
    return any(truthy(fn(list.__getitem__(a, i), i, a)) for i in range(len(a)) if _present(a, i))


def a_every(a, fn, *_):
    fn = _cb(fn)
    return all(truthy(fn(list.__getitem__(a, i), i, a)) for i in range(len(a)) if _present(a, i))


def _same_value_zero(x, y):
    if is_number(x) and is_number(y):
        return x == y or (x != x and y != y)
    return seq(x, y)


def a_includes(a, v, start=undefined):
    s = _rel(start, len(a), 0)
    return any(_same_value_zero(get(a, i), v) for i in range(s, len(a)))


def a_indexOf(a, v, start=undefined):
    for i in range(_rel(start, len(a), 0), len(a)):
        if seq(list.__getitem__(a, i), v):
            return i
    return -1


def a_lastIndexOf(a, v, *_):
    for i in range(len(a) - 1, -1, -1):
        if seq(list.__getitem__(a, i), v):
            return i
    return -1


def array_join(a, sep=","):
    if sep is undefined:
        sep = ","
    return to_str(sep).join("" if (nullish(x) or x is HOLE) else to_str(x) for x in a)


def a_join(a, sep=undefined):
    return array_join(a, sep)


def a_concat(a, *others):
    out = JSArray(a)
    for o in others:
        if isinstance(o, list):
            out.extend(o)
        else:
            out.append(o)
    return out


def a_reverse(a):
    a.reverse()
    return a


def a_sort(a, cmp=undefined):
    vals = list(a)
    holes = [v for v in vals if v is HOLE]
    undef = [v for v in vals if v is undefined]
    rest = [v for v in vals if v is not undefined and v is not HOLE]
    if cmp is undefined:
        rest.sort(key=to_str)
    else:
        def c(x, y):
            r = to_number(cmp(x, y))
            if r != r:
                return 0
            return -1 if r < 0 else (1 if r > 0 else 0)

        rest.sort(key=functools.cmp_to_key(c))
    a[:] = rest + undef + holes
    return a


def a_fill(a, v, start=undefined, end=undefined):
    n = len(a)
    for i in range(_rel(start, n, 0), _rel(end, n, n)):
        list.__setitem__(a, i, v)
    return a


def a_flat(a, depth=1):
    depth = 1 if depth is undefined else to_number(depth)

    def f(x, d):
        out = []
        for v in x:
            if isinstance(v, list) and d > 0:
                out.extend(f(v, d - 1))
            else:
                out.append(v)
        return out

    return JSArray(f(a, depth))


def a_flatMap(a, fn, *_):
    return a_flat(a_map(a, fn), 1)


def a_at(a, i):
    i = int(to_number(i))
    if i < 0:
        i += len(a)
    return list.__getitem__(a, i) if 0 <= i < len(a) else undefined


def a_keys(a):
    return JSIterator(range(len(a)))


def a_values(a):
    return JSIterator(list(a))


def a_entries(a):
    return JSIterator(JSArray([i, v]) for i, v in enumerate(a))


def a_toString(a):
    return array_join(a, ",")


ARRAY_METHODS = {
    name[2:]: fn
    for name, fn in list(globals().items())
    if name.startswith("a_") and callable(fn)
}


# ----------------------------------------------------------------------------
# Object.prototype (the few used on plain objects)
# ----------------------------------------------------------------------------


def _o_hasOwnProperty(o, k):
    return prop_key(k) in o


OBJECT_PROTO = {
    "hasOwnProperty": _o_hasOwnProperty,
    "toString": lambda o: "[object Object]",
}


# ----------------------------------------------------------------------------
# String.prototype
# ----------------------------------------------------------------------------


def s_substring(s, a=undefined, b=undefined):
    n = len(s)

    def clamp(x, d):
        if x is undefined:
            return d
        x = to_number(x)
        if x != x:
            return 0
        return int(max(0, min(x, n)))

    i, j = clamp(a, 0), clamp(b, n)
    if i > j:
        i, j = j, i
    return s[i:j]


def s_substr(s, start=undefined, length=undefined):
    n = len(s)
    st = _rel(start, n, 0)
    ln = n - st if length is undefined else int(max(0, to_number(length)))
    return s[st : st + ln]


def s_slice(s, a=undefined, b=undefined):
    n = len(s)
    i, j = _rel(a, n, 0), _rel(b, n, n)
    return s[i:j] if j > i else ""


def s_toUpperCase(s):
    return s.upper()


def s_toLowerCase(s):
    return s.lower()


def s_trim(s):
    return s.strip()


def s_trimStart(s):
    return s.lstrip()


def s_trimEnd(s):
    return s.rstrip()


def s_padStart(s, n, fill=" "):
    n = int(to_number(n))
    fill = " " if fill is undefined else to_str(fill)
    if len(s) >= n or not fill:
        return s
    pad = (fill * n)[: n - len(s)]
    return pad + s


def s_padEnd(s, n, fill=" "):
    n = int(to_number(n))
    fill = " " if fill is undefined else to_str(fill)
    if len(s) >= n or not fill:
        return s
    return s + (fill * n)[: n - len(s)]


def s_charAt(s, i=0):
    i = int(to_number(i)) if i is not undefined else 0
    return s[i] if 0 <= i < len(s) else ""


def s_charCodeAt(s, i=0):
    i = int(to_number(i)) if i is not undefined else 0
    return ord(s[i]) if 0 <= i < len(s) else NaN


def s_indexOf(s, sub, start=0):
    return s.find(to_str(sub), int(to_number(start)) if start is not undefined else 0)


def s_lastIndexOf(s, sub, *_):
    return s.rfind(to_str(sub))


def s_includes(s, sub, *_):
    return to_str(sub) in s


def s_startsWith(s, sub, pos=0):
    return s.startswith(to_str(sub), int(to_number(pos)) if pos is not undefined else 0)


def s_endsWith(s, sub, *_):
    return s.endswith(to_str(sub))


def s_split(s, sep=undefined, limit=undefined):
    if sep is undefined:
        out = [s]
    elif isinstance(sep, JSRegExp):
        out = sep.rx.split(s)
    else:
        sep = to_str(sep)
        out = list(s) if sep == "" else s.split(sep)
    if limit is not undefined:
        out = out[: int(to_number(limit))]
    return JSArray(out)


def _expand_replacement(rep, m):
    def sub_(mm):
        t = mm.group(0)
        if t == "$$":
            return "$"
        if t == "$&":
            return m.group(0)
        g = int(t[1:])
        try:
            return m.group(g) or ""
        except (IndexError, _re.error):
            return t

    return _re.sub(r"\$\$|\$&|\$\d{1,2}", sub_, rep)


def _replace(s, pat, rep, all_):
    if isinstance(pat, JSRegExp):
        count = 0 if (pat.glob or all_) else 1

        def f(m):
            if callable(rep):
                return to_str(rep(m.group(0), *[(g if g is not None else undefined) for g in m.groups()], m.start(), s))
            return _expand_replacement(to_str(rep), m)

        return pat.rx.sub(f, s, count=count)
    pat = to_str(pat)
    if callable(rep):
        if all_:
            out, i = [], 0
            while True:
                j = s.find(pat, i)
                if j < 0:
                    break
                out.append(s[i:j] + to_str(rep(pat, j, s)))
                i = j + len(pat)
            return "".join(out) + s[i:]
        j = s.find(pat)
        return s if j < 0 else s[:j] + to_str(rep(pat, j, s)) + s[j + len(pat) :]
    rep = to_str(rep).replace("$$", "$")
    return s.replace(pat, rep) if all_ else s.replace(pat, rep, 1)


def s_replace(s, pat, rep):
    return _replace(s, pat, rep, False)


def s_replaceAll(s, pat, rep):
    return _replace(s, pat, rep, True)


def s_match(s, rx):
    if not isinstance(rx, JSRegExp):
        rx = JSRegExp(to_str(rx), "")
    if rx.glob:
        found = [m.group(0) for m in rx.rx.finditer(s)]
        return JSArray(found) if found else None
    m = rx.rx.search(s)
    return _match_arr(m, s) if m else None


def s_matchAll(s, rx):
    if not isinstance(rx, JSRegExp):
        rx = JSRegExp(re_escape_none(to_str(rx)), "g")
    return JSIterator(_match_arr(m, s) for m in rx.rx.finditer(s))


def _match_arr(m, s):
    a = JSArray([m.group(0)] + [(g if g is not None else undefined) for g in m.groups()])
    a.props = {"index": m.start(), "input": s, "groups": JSObject(m.groupdict()) if m.groupdict() else undefined}
    return a


def re_escape_none(p):
    return p  # new RegExp(string): the string IS the pattern


def s_search(s, rx):
    if not isinstance(rx, JSRegExp):
        rx = JSRegExp(to_str(rx), "")
    m = rx.rx.search(s)
    return m.start() if m else -1


def s_repeat(s, n):
    return s * int(to_number(n))


def s_toString(s):
    return s


def s_valueOf(s):
    return s


def s_concat(s, *parts):
    return s + "".join(to_str(p) for p in parts)


def s_localeCompare(s, other, *_):
    other = to_str(other)
    return -1 if s < other else (1 if s > other else 0)


def s_at(s, i):
    i = int(to_number(i))
    if i < 0:
        i += len(s)
    return s[i] if 0 <= i < len(s) else undefined


def s_normalize(s, *_):
    return s


STRING_METHODS = {
    name[2:]: fn
    for name, fn in list(globals().items())
    if name.startswith("s_") and callable(fn)
}


# ----------------------------------------------------------------------------
# Number.prototype
# ----------------------------------------------------------------------------


def n_toFixed(x, digits=0):
    d = 0 if digits is undefined else int(to_number(digits))
    x = to_number(x)
    if x != x:
        return "NaN"
    if abs(x) >= 1e21 or x in (math.inf, -math.inf):
        return to_str(x)
    q = Decimal(x).quantize(Decimal(1).scaleb(-d), rounding=ROUND_HALF_UP)
    s = format(q, "f")
    if s.startswith("-") and float(q) == 0:
        s = s[1:]  # (-0.001).toFixed(2) === "-0.00" in JS actually; keep sign rule below
        if x < 0:
            s = "-" + s
    return s


def n_toString(x, radix=undefined):
    if radix is undefined or to_number(radix) == 10:
        return to_str(x)
    r = int(to_number(radix))
    n = int(to_number(x))
    if n == 0:
        return "0"
    digs = "0123456789abcdefghijklmnopqrstuvwxyz"
    neg, n = n < 0, abs(n)
    out = ""
    while n:
        out = digs[n % r] + out
        n //= r
    return ("-" if neg else "") + out


def n_toPrecision(x, p=undefined):
    if p is undefined:
        return to_str(x)
    p = int(to_number(p))
    x = to_number(x)
    if x == 0:
        return "0" if p == 1 else "0." + "0" * (p - 1)
    e = math.floor(math.log10(abs(x)))
    if e < -6 or e >= p:
        m = Decimal(x).scaleb(-e).quantize(Decimal(1).scaleb(-(p - 1)), rounding=ROUND_HALF_UP)
        ms = format(m, "f")
        return f"{ms}e{'+' if e >= 0 else '-'}{abs(e)}"
    return n_toFixed(x, p - 1 - e)


def n_toLocaleString(x, locale=undefined, opts=undefined):
    x = to_number(x)
    mn = mx = None
    if isinstance(opts, dict):
        mn = opts.get("minimumFractionDigits")
        mx = opts.get("maximumFractionDigits")
    mx = 3 if mx in (None, undefined) else int(mx)
    mn = 0 if mn in (None, undefined) else int(mn)
    mx = max(mx, mn)
    s = n_toFixed(x, mx)
    if "." in s:
        ip, fp = s.split(".")
        fp = fp.rstrip("0")
        if len(fp) < mn:
            fp = fp + "0" * (mn - len(fp))
    else:
        ip, fp = s, "0" * mn
    neg = ip.startswith("-")
    ip = f"{int(ip.lstrip('-')):,}"
    return ("-" if neg else "") + ip + ("." + fp if fp else "")


def n_valueOf(x):
    return x


NUMBER_METHODS = {
    name[2:]: fn
    for name, fn in list(globals().items())
    if name.startswith("n_") and callable(fn)
}


# ----------------------------------------------------------------------------
# RegExp
# ----------------------------------------------------------------------------


class JSRegExp:
    def __init__(self, pattern, flags=""):
        self.pattern, self.flags = pattern, flags
        pyflags = 0
        if "i" in flags:
            pyflags |= _re.I
        if "m" in flags:
            pyflags |= _re.M
        if "s" in flags:
            pyflags |= _re.S
        py = _re.sub(r"\(\?<([A-Za-z_]\w*)>", r"(?P<\1>", pattern)
        py = py.replace("\\/", "/")
        self.rx = _re.compile(py, pyflags)
        self.glob = "g" in flags
        self.lastIndex = 0

    def source_str(self):
        return f"/{self.pattern}/{self.flags}"

    def js_get(self, k):
        if k == "test":
            return self.test
        if k == "exec":
            return self.exec
        if k == "lastIndex":
            return self.lastIndex
        if k in ("source",):
            return self.pattern
        if k == "flags":
            return self.flags
        if k == "global":
            return self.glob
        return undefined

    def js_set(self, k, v):
        if k == "lastIndex":
            self.lastIndex = int(to_number(v))

    def test(self, s=undefined):
        return self.exec(s) is not None

    def exec(self, s=undefined):
        s = to_str(s)
        start = self.lastIndex if self.glob else 0
        m = self.rx.search(s, start)
        if not m:
            self.lastIndex = 0
            return None
        if self.glob:
            self.lastIndex = m.end() if m.end() > m.start() else m.end() + 1
        return _match_arr(m, s)


def regex(pattern, flags=""):
    return JSRegExp(pattern, flags)


# ----------------------------------------------------------------------------
# Math / Number / global functions
# ----------------------------------------------------------------------------


def _mathfn(f):
    def g(x=undefined, *_):
        x = to_number(x)
        try:
            return f(x)
        except (ValueError, OverflowError):
            return NaN

    return g


def js_round(x=undefined, *_):
    x = to_number(x)
    if x != x or x in (math.inf, -math.inf):
        return x
    r = math.floor(x + 0.5)
    if r == 0 and x < 0:
        return -0.0
    return r


def _max(*args):
    r = -math.inf
    for a in args:
        a = to_number(a)
        if a != a:
            return NaN
        if a > r or (a == 0 and r == 0 and math.copysign(1, r) < 0):
            r = a
    return r


def _min(*args):
    r = math.inf
    for a in args:
        a = to_number(a)
        if a != a:
            return NaN
        if a < r or (a == 0 and r == 0 and math.copysign(1, a) < 0):
            r = a
    return r


def _log(x):
    if x == 0:
        return -math.inf
    if x < 0:
        return NaN
    if x == math.inf:
        return math.inf
    return math.log(x)


def _sqrt(x):
    if x < 0:
        return NaN
    return math.sqrt(x)


def _sign(x):
    if x != x:
        return NaN
    return 1 if x > 0 else (-1 if x < 0 else x)


def _trunc(x):
    if x != x or x in (math.inf, -math.inf):
        return x
    return math.trunc(x)


def _floor(x):
    if x != x or x in (math.inf, -math.inf):
        return x
    return math.floor(x)


def _ceil(x):
    if x != x or x in (math.inf, -math.inf):
        return x
    return math.ceil(x)


def _imul(a=undefined, b=undefined, *_):
    return to_int32(to_int32(a) * to_int32(b))


def _exp(x):
    try:
        return math.exp(x)
    except OverflowError:
        return math.inf


Math = JSObject(
    abs=_mathfn(abs),
    floor=_mathfn(_floor),
    ceil=_mathfn(_ceil),
    round=js_round,
    trunc=_mathfn(_trunc),
    sign=_mathfn(_sign),
    sqrt=_mathfn(_sqrt),
    cbrt=_mathfn(lambda x: math.copysign(abs(x) ** (1 / 3), x)),
    log=_mathfn(lambda x: _fd.log(x)),
    log10=_mathfn(lambda x: _log(x) / math.log(10) if x > 0 else _log(x)),
    log2=_mathfn(lambda x: math.log2(x) if x > 0 else _log(x)),
    log1p=_mathfn(math.log1p),
    exp=_mathfn(lambda x: _fd.exp(x)),
    expm1=_mathfn(math.expm1),
    sin=_mathfn(math.sin),
    cos=_mathfn(math.cos),
    tan=_mathfn(math.tan),
    asin=_mathfn(math.asin),
    acos=_mathfn(math.acos),
    atan=_mathfn(math.atan),
    sinh=_mathfn(math.sinh),
    cosh=_mathfn(math.cosh),
    tanh=_mathfn(math.tanh),
    atan2=lambda y=undefined, x=undefined, *_: math.atan2(to_number(y), to_number(x)),
    pow=lambda a=undefined, b=undefined, *_: pow_(a, b),
    max=_max,
    min=_min,
    hypot=lambda *a: math.hypot(*[to_number(x) for x in a]),
    random=lambda *_: _random.random(),
    imul=_imul,
    PI=math.pi,
    E=math.e,
    LN2=math.log(2),
    LN10=math.log(10),
    LOG2E=1 / math.log(2),
    LOG10E=1 / math.log(10),
    SQRT2=math.sqrt(2),
    SQRT1_2=math.sqrt(0.5),
)


def isNaN(x=undefined, *_):
    x = to_number(x)
    return x != x


def isFinite(x=undefined, *_):
    x = to_number(x)
    return x == x and x not in (math.inf, -math.inf)


_FLOAT_PREFIX = _re.compile(r"^[+-]?(?:Infinity|(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)")


def parseFloat(s=undefined, *_):
    s = to_str(s).lstrip()
    m = _FLOAT_PREFIX.match(s)
    if not m:
        return NaN
    f = float(m.group(0))
    return int(f) if f.is_integer() and abs(f) < 2**53 else f


def parseInt(s=undefined, radix=undefined, *_):
    s = to_str(s).strip()
    r = 0 if radix is undefined else int(to_number(radix)) if to_number(radix) == to_number(radix) else 0
    sign = 1
    if s[:1] in "+-" and s:
        sign = -1 if s[0] == "-" else 1
        s = s[1:]
    if r in (0, 16) and s[:2].lower() == "0x":
        s, r = s[2:], 16
    if r == 0:
        r = 10
    if not 2 <= r <= 36:
        return NaN
    digs = "0123456789abcdefghijklmnopqrstuvwxyz"[:r]
    n = 0
    j = 0
    for j, ch in enumerate(s.lower()):
        if ch not in digs:
            break
        n = n * r + digs.index(ch)
    else:
        j = len(s)
    if j == 0:
        return NaN
    return sign * n


class _Callable(JSObject):
    """A JS function object that also carries properties (Number, String...)."""

    def __init__(self, fn, **props):
        super().__init__(**props)
        self._fn = fn

    def __call__(self, *args):
        return self._fn(*args)

    __hash__ = JSObject.__hash__


def _number_call(v=0, *_):
    return to_number(v) if v is not undefined else 0


Number = _Callable(
    _number_call,
    isFinite=lambda x=undefined, *_: is_number(x) and x == x and x not in (math.inf, -math.inf),
    isNaN=lambda x=undefined, *_: is_number(x) and x != x,
    isInteger=lambda x=undefined, *_: is_number(x) and x == x and x not in (math.inf, -math.inf) and float(x).is_integer(),
    isSafeInteger=lambda x=undefined, *_: is_number(x) and x == x and float(x).is_integer() and abs(x) <= 2**53 - 1,
    parseFloat=parseFloat,
    parseInt=parseInt,
    EPSILON=2.220446049250313e-16,
    MAX_SAFE_INTEGER=2**53 - 1,
    MIN_SAFE_INTEGER=-(2**53 - 1),
    MAX_VALUE=1.7976931348623157e308,
    MIN_VALUE=5e-324,
    POSITIVE_INFINITY=math.inf,
    NEGATIVE_INFINITY=-math.inf,
    NaN=NaN,
)

String = _Callable(
    lambda v="", *_: to_str(v) if v is not undefined else "",
    fromCharCode=lambda *codes: "".join(chr(int(to_number(c))) for c in codes),
)

Boolean = _Callable(lambda v=undefined, *_: truthy(v))


def _array_call(*args):
    if len(args) == 1 and is_number(args[0]):
        return JSArray([HOLE] * int(args[0]))
    return JSArray(args)


def _array_from(src=undefined, fn=undefined, *_):
    if isinstance(src, dict) and "length" in src and not isinstance(src, JSArray):
        items = [undefined] * int(to_number(src["length"]))
    elif isinstance(src, (list, str, JSIterator)):
        items = list(iter_of(src))
    else:
        items = []
    if fn is not undefined:
        return JSArray(fn(v, i) for i, v in enumerate(items))
    return JSArray(items)


Array = _Callable(
    _array_call,
    isArray=lambda v=undefined, *_: isinstance(v, list),
    of=lambda *a: JSArray(a),
)
Array["from"] = _array_from


def _keys(o=undefined, *_):
    if isinstance(o, JSArray):
        return JSArray(iter_in(o))
    if isinstance(o, dict):
        return JSArray(o.keys())
    if isinstance(o, str):
        return JSArray(str(i) for i in range(len(o)))
    if nullish(o):
        raise type_error("Cannot convert undefined or null to object")
    return JSArray()


def _values(o=undefined, *_):
    if isinstance(o, JSArray):
        return JSArray(o)
    if isinstance(o, dict):
        return JSArray(o.values())
    return JSArray()


def _entries(o=undefined, *_):
    if isinstance(o, JSArray):
        return JSArray(JSArray([str(i), v]) for i, v in enumerate(o))
    if isinstance(o, dict):
        return JSArray(JSArray([k, v]) for k, v in o.items())
    return JSArray()


def _assign(target, *sources):
    for s in sources:
        for k, v in obj_spread(s):
            set(target, k, v)
    return target


def _from_entries(pairs=undefined, *_):
    o = JSObject()
    for p in iter_of(pairs):
        o[prop_key(get(p, 0))] = get(p, 1)
    return o


Object = _Callable(
    lambda v=undefined, *_: JSObject() if nullish(v) else v,
    keys=_keys,
    values=_values,
    entries=_entries,
    assign=_assign,
    fromEntries=_from_entries,
    freeze=lambda o=undefined, *_: o,
)


def _to_json_value(v, _seen=None):
    if v is undefined or callable(v) and not isinstance(v, (dict, list)):
        return undefined
    if v is None or isinstance(v, (bool, str)):
        return v
    if isinstance(v, (int, float)):
        return v if v == v and v not in (math.inf, -math.inf) else None
    if isinstance(v, list):
        out = []
        for x in v:
            j = _to_json_value(x)
            out.append(None if j is undefined else j)
        return out
    if isinstance(v, dict):
        out = {}
        for k, x in v.items():
            j = _to_json_value(x)
            if j is not undefined:
                out[k] = j
        return out
    if isinstance(v, JSDate):
        return v.to_iso()
    return None


def _json_num(o):
    if isinstance(o, float) and o.is_integer():
        return str(int(o))
    return to_str(o)


def _stringify(v=undefined, replacer=undefined, space=undefined, *_):
    j = _to_json_value(v)
    if j is undefined:
        return undefined
    indent = None
    if is_number(space):
        indent = int(space) or None
    elif isinstance(space, str) and space:
        indent = space

    class Enc(_json.JSONEncoder):
        def iterencode(self, o, _one_shot=False):
            return super().iterencode(o, _one_shot)

    def conv(o):
        if isinstance(o, float) and o.is_integer():
            return int(o)
        if isinstance(o, list):
            return [conv(x) for x in o]
        if isinstance(o, dict):
            return {k: conv(x) for k, x in o.items()}
        return o

    s = _json.dumps(conv(j), ensure_ascii=False, indent=indent, separators=(",", ":") if indent is None else (",", ": "))
    return s


def _from_json(v):
    if isinstance(v, list):
        return JSArray(_from_json(x) for x in v)
    if isinstance(v, dict):
        return JSObject((k, _from_json(x)) for k, x in v.items())
    if isinstance(v, float) and v.is_integer() and abs(v) < 2**53:
        return v
    return v


def _parse(s=undefined, *_):
    try:
        return _from_json(_json.loads(to_str(s)))
    except ValueError as exc:
        raise JSError(make_error(str(exc), "SyntaxError"))


JSON = JSObject(stringify=_stringify, parse=_parse)


def to_utf16(s):
    """Python str -> JS string representation (non-BMP chars as surrogate pairs)."""
    if all(ord(c) < 0x10000 for c in s):
        return s
    return s.encode("utf-16-le", "surrogatepass").decode("utf-16-le", "surrogatepass") if False else "".join(
        c if ord(c) < 0x10000 else chr(0xD800 + ((ord(c) - 0x10000) >> 10)) + chr(0xDC00 + ((ord(c) - 0x10000) & 0x3FF))
        for c in s)


def from_utf16(s):
    """JS string representation -> normal Python str (pairs joined, lone surrogates kept)."""
    if not any(0xD800 <= ord(c) <= 0xDFFF for c in s):
        return s
    return s.encode("utf-16-le", "surrogatepass").decode("utf-16-le", "replace")


def from_python(v):
    """Convert plain Python data (lists/dicts from providers) to JS values."""
    if isinstance(v, str):
        return to_utf16(v)
    if isinstance(v, list):
        return JSArray(from_python(x) for x in v)
    if isinstance(v, dict):
        return JSObject((to_utf16(k), from_python(x)) for k, x in v.items())
    return v


class _Console(JSObject):
    pass


def _noop(*_a):
    return undefined


console = JSObject(log=_noop, warn=_noop, error=_noop, info=_noop, debug=_noop)


def encodeURIComponent(s=undefined, *_):
    from urllib.parse import quote

    return quote(to_str(s), safe="-_.!~*'()")


def js_error_ctor(name):
    return _Callable(lambda msg=undefined, *_: make_error(msg, name))


Error = js_error_ctor("Error")
TypeError_ = js_error_ctor("TypeError")
RangeError_ = js_error_ctor("RangeError")


# ----------------------------------------------------------------------------
# Date (UTC-based; `new` is banned in TrendSpider scripts, so only the
# static helpers and Date(...) calls appear)
# ----------------------------------------------------------------------------


class JSDate:
    def __init__(self, ms):
        self.ms = ms

    def to_iso(self):
        import datetime as dt

        d = dt.datetime.fromtimestamp(self.ms / 1000, dt.timezone.utc)
        return d.strftime("%Y-%m-%dT%H:%M:%S.") + f"{int(self.ms % 1000):03d}Z"

    def to_string(self):
        return self.to_iso()

    def js_get(self, k):
        import datetime as dt

        d = dt.datetime.fromtimestamp(self.ms / 1000, dt.timezone.utc)
        table = {
            "getTime": lambda *_: self.ms,
            "valueOf": lambda *_: self.ms,
            "getUTCFullYear": lambda *_: d.year,
            "getUTCMonth": lambda *_: d.month - 1,
            "getUTCDate": lambda *_: d.day,
            "getUTCDay": lambda *_: (d.weekday() + 1) % 7,
            "getUTCHours": lambda *_: d.hour,
            "getUTCMinutes": lambda *_: d.minute,
            "getUTCSeconds": lambda *_: d.second,
            "toISOString": lambda *_: self.to_iso(),
            "toJSON": lambda *_: self.to_iso(),
        }
        # TrendSpider's workers run in UTC for our purposes: local == UTC.
        for utc_name in list(table):
            if utc_name.startswith("getUTC"):
                table["get" + utc_name[6:]] = table[utc_name]
        return table.get(k, undefined)


def _date_utc(y=undefined, m=0, d=1, h=0, mi=0, s=0, ms=0, *_):
    import calendar

    y, m = int(to_number(y)), int(to_number(m))
    y += m // 12
    m = m % 12
    days = calendar.timegm((y, m + 1, 1, 0, 0, 0)) // 86400 + int(to_number(d)) - 1
    return days * 86400000 + int(to_number(h)) * 3600000 + int(to_number(mi)) * 60000 + int(to_number(s)) * 1000 + int(to_number(ms))


def _date_parse(s=undefined, *_):
    import datetime as dt

    s = to_str(s).strip()
    try:
        if len(s) == 10:
            d = dt.datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=dt.timezone.utc)
        else:
            d = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
            if d.tzinfo is None:
                d = d.replace(tzinfo=dt.timezone.utc)
        return int(d.timestamp() * 1000)
    except ValueError:
        return NaN


Date = _Callable(
    lambda *a: JSDate(int(_time.time() * 1000)).to_string(),
    UTC=_date_utc,
    now=lambda *_: int(_time.time() * 1000),
    parse=_date_parse,
)


class _NumberFormat:
    def __init__(self, locale=undefined, opts=undefined):
        self.opts = opts if isinstance(opts, dict) else {}

    def js_get(self, k):
        if k == "format":
            return self.format
        return undefined

    def format(self, v=undefined, *_):
        x = to_number(v)
        mx = self.opts.get("maximumFractionDigits", undefined)
        if self.opts.get("notation") == "compact":
            mx = 0 if mx is undefined else int(mx)
            for div_, suf in ((1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "K")):
                if abs(x) >= div_:
                    return n_toLocaleString(x / div_, undefined, JSObject(maximumFractionDigits=mx)) + suf
            return n_toLocaleString(x, undefined, JSObject(maximumFractionDigits=mx))
        return n_toLocaleString(x, undefined, JSObject(self.opts))


Intl = JSObject(NumberFormat=lambda locale=undefined, opts=undefined, *_: _NumberFormat(locale, opts))


def _promise_all(items=undefined, *_):
    return JSArray(iter_of(items))


Promise = JSObject(
    all=_promise_all,
    allSettled=lambda items=undefined, *_: JSArray(JSObject(status="fulfilled", value=v) for v in iter_of(items)),
    resolve=lambda v=undefined, *_: v,
)


class Moment:  # defined in moment.py; placeholder for isinstance checks
    def value_of(self):
        return NaN

    def format(self, *_):
        return ""


BUILTINS = {
    "Math": Math,
    "Number": Number,
    "String": String,
    "Boolean": Boolean,
    "Array": Array,
    "Object": Object,
    "JSON": JSON,
    "Date": Date,
    "Intl": Intl,
    "Promise": Promise,
    "console": console,
    "isNaN": isNaN,
    "isFinite": isFinite,
    "parseInt": parseInt,
    "parseFloat": parseFloat,
    "encodeURIComponent": encodeURIComponent,
    "Error": Error,
    "TypeError": TypeError_,
    "RangeError": RangeError_,
    "NaN": NaN,
    "Infinity": Infinity,
    "undefined": undefined,
}


def require_object(v):
    """Source of an object-destructuring pattern: null/undefined throw, like JS."""
    if v is None or v is undefined:
        raise type_error(f"Cannot destructure '{to_str(v)}' as it is {to_str(v)}.")
    return v


def obj_rest(o, used):
    return JSObject((k, v) for k, v in obj_spread(o) if k not in used)


def instanceof(v, ctor):
    if ctor is Array:
        return isinstance(v, list)
    if ctor is Object:
        return is_object(v)
    return False


def new(ctor, *args):
    return ctor(*args)
