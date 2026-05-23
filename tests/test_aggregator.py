"""Tests for logslice.aggregator."""

from __future__ import annotations

import pytest

from logslice.aggregator import collect_values, count_by, group_by, summarise

RECORDS = [
    {"level": "info",  "latency": 12,  "service": "api"},
    {"level": "error", "latency": 340, "service": "api"},
    {"level": "info",  "latency": 5,   "service": "worker"},
    {"level": "warn",  "latency": 88,  "service": "worker"},
    {"level": "info",  "service": "api"},  # no latency
]


# --- count_by ----------------------------------------------------------------

def test_count_by_basic():
    result = count_by(RECORDS, "level")
    assert result["info"] == 3
    assert result["error"] == 1
    assert result["warn"] == 1


def test_count_by_most_common_first():
    result = count_by(RECORDS, "level")
    keys = list(result.keys())
    assert keys[0] == "info"


def test_count_by_missing_field_uses_null():
    records = [{"a": 1}, {"b": 2}, {"a": 1}]
    result = count_by(records, "a")
    assert result["1"] == 2
    assert result["<null>"] == 1


def test_count_by_empty():
    assert count_by([], "level") == {}


# --- collect_values ----------------------------------------------------------

def test_collect_values_skips_missing():
    values = collect_values(RECORDS, "latency")
    assert len(values) == 4  # one record has no latency


def test_collect_values_empty():
    assert collect_values([], "x") == []


# --- summarise ---------------------------------------------------------------

def test_summarise_basic():
    result = summarise(RECORDS, "latency")
    assert result["count"] == 4
    assert result["min"] == 5
    assert result["max"] == 340
    assert result["sum"] == pytest.approx(12 + 340 + 5 + 88)
    assert result["mean"] == pytest.approx((12 + 340 + 5 + 88) / 4)


def test_summarise_no_numeric_values():
    records = [{"level": "info"}, {"level": "warn"}]
    result = summarise(records, "latency")
    assert result["count"] == 0
    assert result["mean"] is None


def test_summarise_skips_non_numeric():
    records = [{"v": 10}, {"v": "oops"}, {"v": 20}]
    result = summarise(records, "v")
    assert result["count"] == 2
    assert result["mean"] == 15.0


# --- group_by ----------------------------------------------------------------

def test_group_by_basic():
    groups = group_by(RECORDS, "service")
    assert set(groups.keys()) == {"api", "worker"}
    assert len(groups["api"]) == 3
    assert len(groups["worker"]) == 2


def test_group_by_empty():
    assert group_by([], "service") == {}
