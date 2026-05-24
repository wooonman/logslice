"""Additional numeric-focused tests for logslice.profiler."""

import pytest
from logslice.profiler import _numeric_stats, profile_field


def test_single_value_stats():
    stats = _numeric_stats([42.0])
    assert stats["min"] == 42.0
    assert stats["max"] == 42.0
    assert stats["mean"] == 42.0
    assert stats["stddev"] == 0.0
    assert stats["median"] == 42.0
    assert stats["count"] == 1


def test_two_values_mean():
    stats = _numeric_stats([0.0, 10.0])
    assert stats["mean"] == pytest.approx(5.0)


def test_two_values_median():
    stats = _numeric_stats([0.0, 10.0])
    assert stats["median"] == pytest.approx(5.0)


def test_stddev_known_values():
    # population stddev of [2,4,4,4,5,5,7,9] == 2.0
    stats = _numeric_stats([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0])
    assert stats["stddev"] == pytest.approx(2.0)


def test_float_records_profiled():
    records = [{"rt": 1.5}, {"rt": 2.5}, {"rt": 3.5}]
    result = profile_field(records, "rt")
    assert "numeric" in result
    assert result["numeric"]["count"] == 3


def test_mixed_numeric_and_missing():
    records = [{"v": 10}, {"v": 20}, {"other": 1}]
    result = profile_field(records, "v")
    assert result["numeric"]["count"] == 2
    assert result["missing"] == 1


def test_large_stream_stddev_positive():
    import random
    random.seed(0)
    records = [{"x": random.gauss(100, 15)} for _ in range(500)]
    result = profile_field(records, "x")
    assert result["numeric"]["stddev"] > 0


def test_all_missing_no_numeric_key():
    records = [{"a": 1}, {"a": 2}]
    result = profile_field(records, "b")
    assert "numeric" not in result
    assert result["missing"] == 2
