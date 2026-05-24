"""Tests for logslice.merger."""

import pytest

from logslice.merger import merge, merge_sorted, merge_unordered


def _r(ts, **kwargs):
    return {"timestamp": ts, **kwargs}


# ---------------------------------------------------------------------------
# merge_sorted
# ---------------------------------------------------------------------------

def test_merge_sorted_two_streams():
    a = [_r("2024-01-01T00:00:01"), _r("2024-01-01T00:00:03")]
    b = [_r("2024-01-01T00:00:02"), _r("2024-01-01T00:00:04")]
    result = list(merge_sorted([a, b]))
    timestamps = [r["timestamp"] for r in result]
    assert timestamps == sorted(timestamps)
    assert len(result) == 4


def test_merge_sorted_empty_streams():
    result = list(merge_sorted([[], []]))
    assert result == []


def test_merge_sorted_single_stream():
    stream = [_r("2024-01-01T00:00:01"), _r("2024-01-01T00:00:02")]
    result = list(merge_sorted([stream]))
    assert result == stream


def test_merge_sorted_one_empty_one_not():
    a = []
    b = [_r("2024-01-01T00:00:01"), _r("2024-01-01T00:00:02")]
    result = list(merge_sorted([a, b]))
    assert len(result) == 2


def test_merge_sorted_missing_key_sorts_first():
    a = [{"msg": "no ts"}, _r("2024-01-01T00:00:05")]
    b = [_r("2024-01-01T00:00:01")]
    result = list(merge_sorted([a, b]))
    assert result[0] == {"msg": "no ts"}


def test_merge_sorted_custom_key():
    a = [{"t": "10:00", "src": "a"}, {"t": "10:02", "src": "a"}]
    b = [{"t": "10:01", "src": "b"}]
    result = list(merge_sorted([a, b], key="t"))
    assert [r["t"] for r in result] == ["10:00", "10:01", "10:02"]


def test_merge_sorted_preserves_all_records():
    streams = [[_r(f"2024-01-01T00:00:0{i}")] for i in range(5)]
    result = list(merge_sorted(streams))
    assert len(result) == 5


# ---------------------------------------------------------------------------
# merge_unordered
# ---------------------------------------------------------------------------

def test_merge_unordered_yields_all():
    a = [{"x": 1}, {"x": 2}]
    b = [{"x": 3}]
    result = list(merge_unordered([a, b]))
    assert len(result) == 3
    assert {r["x"] for r in result} == {1, 2, 3}


def test_merge_unordered_empty():
    assert list(merge_unordered([])) == []


# ---------------------------------------------------------------------------
# merge (dispatch)
# ---------------------------------------------------------------------------

def test_merge_with_key_is_sorted():
    a = [_r("2024-01-01T00:00:03")]
    b = [_r("2024-01-01T00:00:01"), _r("2024-01-01T00:00:02")]
    result = list(merge([a, b], key="timestamp"))
    timestamps = [r["timestamp"] for r in result]
    assert timestamps == sorted(timestamps)


def test_merge_without_key_yields_all():
    a = [{"v": 1}]
    b = [{"v": 2}]
    result = list(merge([a, b], key=None))
    assert len(result) == 2
