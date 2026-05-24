"""Tests for logslice.splitter."""

import pytest

from logslice.splitter import iter_bucket, split_by_query, split_by_value


def _records():
    return [
        {"level": "info", "msg": "started"},
        {"level": "error", "msg": "boom"},
        {"level": "info", "msg": "running"},
        {"level": "warn", "msg": "slow"},
        {"msg": "no level"},
    ]


# --- split_by_value ---

def test_split_by_value_basic():
    buckets = split_by_value(_records(), "level")
    assert set(buckets["info"]) == {
        frozenset({"level": "info", "msg": "started"}.items()),
        frozenset({"level": "info", "msg": "running"}.items()),
    } or len(buckets["info"]) == 2
    assert len(buckets["error"]) == 1
    assert len(buckets["warn"]) == 1


def test_split_by_value_missing_field_goes_to_default():
    buckets = split_by_value(_records(), "level")
    assert "__other__" in buckets
    assert buckets["__other__"][0]["msg"] == "no level"


def test_split_by_value_custom_default_bucket():
    buckets = split_by_value(_records(), "level", default_bucket="unknown")
    assert "unknown" in buckets
    assert "__other__" not in buckets


def test_split_by_value_empty_stream():
    buckets = split_by_value([], "level")
    assert buckets == {}


def test_split_by_value_all_missing():
    records = [{"msg": "a"}, {"msg": "b"}]
    buckets = split_by_value(records, "level")
    assert list(buckets.keys()) == ["__other__"]
    assert len(buckets["__other__"]) == 2


# --- split_by_query ---

def test_split_by_query_basic():
    queries = {"errors": "level=error", "infos": "level=info"}
    buckets = split_by_query(_records(), queries)
    assert len(buckets["errors"]) == 1
    assert len(buckets["infos"]) == 2


def test_split_by_query_first_match_wins():
    queries = {"first": "level=info", "second": "level=info"}
    buckets = split_by_query(_records(), queries)
    assert len(buckets.get("first", [])) == 2
    assert len(buckets.get("second", [])) == 0


def test_split_by_query_unmatched_dropped_without_default():
    queries = {"errors": "level=error"}
    buckets = split_by_query(_records(), queries)
    assert "__other__" not in buckets
    total = sum(len(v) for v in buckets.values())
    assert total == 1


def test_split_by_query_unmatched_goes_to_default():
    queries = {"errors": "level=error"}
    buckets = split_by_query(_records(), queries, default_bucket="rest")
    assert len(buckets["rest"]) == 4


def test_split_by_query_empty_stream():
    buckets = split_by_query([], {"errors": "level=error"})
    assert buckets == {}


# --- iter_bucket ---

def test_iter_bucket_yields_matching():
    result = list(iter_bucket(_records(), "level", "info"))
    assert len(result) == 2


def test_iter_bucket_no_match():
    result = list(iter_bucket(_records(), "level", "debug"))
    assert result == []


def test_iter_bucket_empty_stream():
    assert list(iter_bucket([], "level", "info")) == []
