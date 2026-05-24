"""Tests for logslice.profiler."""

import pytest
from logslice.profiler import profile_field, profile_all, _median, _numeric_stats


def _records():
    return [
        {"level": "info", "latency": 10, "code": 200},
        {"level": "warn", "latency": 20, "code": 404},
        {"level": "info", "latency": 30},
        {"level": "error"},
        {"level": "info", "latency": 40, "code": 200},
    ]


def test_profile_field_counts_total():
    result = profile_field(_records(), "latency")
    assert result["total"] == 5


def test_profile_field_present_and_missing():
    result = profile_field(_records(), "latency")
    assert result["present"] == 4
    assert result["missing"] == 1


def test_profile_field_types():
    result = profile_field(_records(), "latency")
    assert result["types"] == {"int": 4}


def test_profile_field_numeric_stats_present():
    result = profile_field(_records(), "latency")
    assert "numeric" in result
    assert result["numeric"]["min"] == 10.0
    assert result["numeric"]["max"] == 40.0


def test_profile_field_mean():
    result = profile_field(_records(), "latency")
    assert result["numeric"]["mean"] == pytest.approx(25.0)


def test_profile_field_median_even():
    assert _median([1.0, 2.0, 3.0, 4.0]) == 2.5


def test_profile_field_median_odd():
    assert _median([1.0, 2.0, 3.0]) == 2.0


def test_profile_field_no_numeric_for_string_field():
    result = profile_field(_records(), "level")
    assert "numeric" not in result


def test_profile_field_top_values_limited_to_five():
    records = [{"x": i} for i in range(20)]
    result = profile_field(records, "x")
    assert len(result["top_values"]) == 5


def test_profile_field_empty_stream():
    result = profile_field([], "level")
    assert result["total"] == 0
    assert result["missing"] == 0
    assert result["present"] == 0


def test_profile_all_discovers_fields():
    results = profile_all(_records())
    field_names = {r["field"] for r in results}
    assert "level" in field_names
    assert "latency" in field_names
    assert "code" in field_names


def test_profile_all_specific_fields():
    results = profile_all(_records(), fields=["level"])
    assert len(results) == 1
    assert results[0]["field"] == "level"


def test_numeric_stats_stddev_zero_for_identical_values():
    stats = _numeric_stats([5.0, 5.0, 5.0])
    assert stats["stddev"] == 0.0


def test_profile_field_bool_not_treated_as_numeric():
    records = [{"flag": True}, {"flag": False}]
    result = profile_field(records, "flag")
    assert "numeric" not in result
    assert result["types"].get("bool") == 2
