"""
V8's Math.exp / Math.log, bit-for-bit.

(Math.pow/sin/cos/atan2 are NOT ported: V8 uses table-driven routines for
those whose results differ from the C runtime's only in the last bit for a
small fraction of inputs; the parity harness reports such cases as "ULP".)

V8 implements these with fdlibm (src/base/ieee754.cc); the platform C
library Python's math module uses rounds differently in the last bit for
a few percent of inputs. Porting fdlibm keeps the *_TS indicators
bit-identical to TrendSpider (verified by fuzzing against Node).
"""

from __future__ import annotations

import math
import struct

_pack_d = struct.Struct("<d")
_pack_q = struct.Struct("<Q")


def _hi_lo(x):
    b = _pack_q.unpack(_pack_d.pack(x))[0]
    return b >> 32, b & 0xFFFFFFFF


def _from_words(hi, lo):
    return _pack_d.unpack(_pack_q.pack(((hi & 0xFFFFFFFF) << 32) | (lo & 0xFFFFFFFF)))[0]


def _signed(v):
    return v - (1 << 32) if v & 0x80000000 else v


_HALF = (0.5, -0.5)
_O_THRESHOLD = 7.09782712893383973096e02
_U_THRESHOLD = -7.45133219101941108420e02
_LN2HI = (6.93147180369123816490e-01, -6.93147180369123816490e-01)
_LN2LO = (1.90821492927058770002e-10, -1.90821492927058770002e-10)
_INVLN2 = 1.44269504088896338700e00
_P1 = 1.66666666666666019037e-01
_P2 = -2.77777777770155933842e-03
_P3 = 6.61375632143793436117e-05
_P4 = -1.65339022054652515390e-06
_P5 = 4.13813679705723846039e-08
_TWOM1000 = 9.33263618503218878990e-302
_TWO1023 = 8.988465674311579539e307


def exp(x: float) -> float:
    x = float(x)
    hx, lx = _hi_lo(x)
    xsb = (hx >> 31) & 1
    hx &= 0x7FFFFFFF
    hi = lo = 0.0
    k = 0
    if hx >= 0x40862E42:
        if hx >= 0x7FF00000:
            if ((hx & 0xFFFFF) | lx) != 0:
                return x + x
            return x if xsb == 0 else 0.0
        if x > _O_THRESHOLD:
            return math.inf
        if x < _U_THRESHOLD:
            return 0.0
    if hx > 0x3FD62E42:
        if hx < 0x3FF0A2B2:
            if x == 1.0:
                return math.e
            hi = x - _LN2HI[xsb]
            lo = _LN2LO[xsb]
            k = 1 - xsb - xsb
        else:
            k = int(_INVLN2 * x + _HALF[xsb])
            t = float(k)
            hi = x - t * _LN2HI[0]
            lo = t * _LN2LO[0]
        x = hi - lo
    elif hx < 0x3E300000:
        return 1.0 + x
    else:
        k = 0
    t = x * x
    if k >= -1021:
        twopk = _from_words(0x3FF00000 + (k << 20), 0)
    else:
        twopk = _from_words(0x3FF00000 + ((k + 1000) << 20), 0)
    c = x - t * (_P1 + t * (_P2 + t * (_P3 + t * (_P4 + t * _P5))))
    if k == 0:
        return 1.0 - ((x * c) / (c - 2.0) - x)
    y = 1.0 - ((lo - (x * c) / (2.0 - c)) - hi)
    if k >= -1021:
        if k == 1024:
            return y * 2.0 * _TWO1023
        return y * twopk
    return y * twopk * _TWOM1000


_LN2_HI = 6.93147180369123816490e-01
_LN2_LO = 1.90821492927058770002e-10
_TWO54 = 1.80143985094819840000e16
_LG1 = 6.666666666666735130e-01
_LG2 = 3.999999999940941908e-01
_LG3 = 2.857142874366239149e-01
_LG4 = 2.222219843214978396e-01
_LG5 = 1.818357216161805012e-01
_LG6 = 1.531383769920937332e-01
_LG7 = 1.479819860511658591e-01


def log(x: float) -> float:
    x = float(x)
    hx, lx = _hi_lo(x)
    hx = _signed(hx)
    k = 0
    if hx < 0x00100000:
        if ((hx & 0x7FFFFFFF) | lx) == 0:
            return -math.inf
        if hx < 0:
            return math.nan
        k -= 54
        x *= _TWO54
        hx = _signed(_hi_lo(x)[0])
    if hx >= 0x7FF00000:
        return x + x
    k += (hx >> 20) - 1023
    hx &= 0x000FFFFF
    i = (hx + 0x95F64) & 0x100000
    x = _from_words(hx | (i ^ 0x3FF00000), _hi_lo(x)[1])
    k += i >> 20
    f = x - 1.0
    if (0x000FFFFF & (2 + hx)) < 3:
        if f == 0.0:
            if k == 0:
                return 0.0
            dk = float(k)
            return dk * _LN2_HI + dk * _LN2_LO
        R = f * f * (0.5 - 0.33333333333333333 * f)
        if k == 0:
            return f - R
        dk = float(k)
        return dk * _LN2_HI - ((R - dk * _LN2_LO) - f)
    s = f / (2.0 + f)
    dk = float(k)
    z = s * s
    i = hx - 0x6147A
    w = z * z
    j = 0x6B851 - hx
    t1 = w * (_LG2 + w * (_LG4 + w * _LG6))
    t2 = z * (_LG1 + w * (_LG3 + w * (_LG5 + w * _LG7)))
    i |= j
    R = t2 + t1
    if i > 0:
        hfsq = 0.5 * f * f
        if k == 0:
            return f - (hfsq - s * (hfsq + R))
        return dk * _LN2_HI - ((hfsq - (s * (hfsq + R) + dk * _LN2_LO)) - f)
    if k == 0:
        return f - s * (f - R)
    return dk * _LN2_HI - ((s * (f - R) - dk * _LN2_LO) - f)

