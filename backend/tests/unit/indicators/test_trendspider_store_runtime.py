"""JS semantics the translated TrendSpider store scripts depend on.

Each case is a place where naive Python gives a different answer than the
JavaScript TrendSpider runs -- the reason every operator in the generated
code goes through app.indicators.trendspider_store._runtime.js.
"""

import math

import pytest

from app.indicators.trendspider_store._runtime import js as J


def test_out_of_range_and_negative_indexing_is_undefined():
    a = J.JSArray([1, 2, 3])
    assert J.get(a, -1) is J.undefined  # Python would give 3
    assert J.get(a, 3) is J.undefined
    assert J.get(a, 1.0) == 2


def test_null_and_undefined_arithmetic():
    assert J.add(None, 1) == 1
    assert math.isnan(J.add(J.undefined, 1))
    assert J.sub(5, None) == 5
    assert J.add("a", 1) == "a1"
    assert J.add(1, "2") == "12"
    assert J.mul("3", 2) == 6


def test_truthiness_differs_from_python():
    assert J.truthy(J.JSArray()) is True  # [] is truthy in JS
    assert J.truthy(J.JSObject()) is True
    assert J.truthy(float("nan")) is False
    assert J.truthy("0") is True


def test_comparisons_with_null_and_nan():
    assert J.lt(None, 1) is True  # null -> 0
    assert J.lt(J.undefined, 1) is False  # undefined -> NaN
    assert J.le(float("nan"), 1) is False
    assert J.eq(None, J.undefined) is True
    assert J.seq(None, J.undefined) is False
    assert J.seq(True, 1) is False  # Python True == 1
    assert J.eq(True, 1) is True
    assert J.eq("1", 1) is True


def test_rounding_and_formatting_match_js():
    assert J.js_round(2.5) == 3 and J.js_round(-2.5) == -2  # Python round() gives 2 / -2
    assert J.n_toFixed(2.5, 0) == "3"
    assert J.n_toFixed(1.005, 2) == "1.00"  # binary value is below 1.005
    assert J.to_str(1.0) == "1"
    assert J.to_str(1e21) == "1e+21"
    assert J.to_str(0.000001) == "0.000001"
    assert J.to_str(1e-7) == "1e-7"


def test_default_sort_is_lexicographic():
    a = J.JSArray([10, 9, 1, 100])
    J.a_sort(a)
    assert list(a) == [1, 10, 100, 9]


def test_modulo_sign_follows_dividend():
    assert J.mod(-7, 3) == -1  # Python -7 % 3 == 2
    assert math.isnan(J.mod(1, 0))


def test_math_max_min_edge_cases():
    assert J._max() == -math.inf
    assert math.isnan(J._max(1, J.undefined))
    assert J._max(1, None) == 1


def test_parse_int_and_float_prefixes():
    assert J.parseInt("15px") == 15
    assert math.isnan(J.parseInt("px"))
    assert J.parseFloat("3.5abc") == 3.5
    assert J.parseInt("0x1f") == 31


@pytest.mark.parametrize("v,expected", [(0.1 + 0.2, "0.30000000000000004"), (123456789012, "123456789012"), (-0.5, "-0.5")])
def test_number_to_string(v, expected):
    assert J.to_str(v) == expected
