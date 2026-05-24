"""Tests for logslice.pipeline."""

from __future__ import annotations

import pytest

from logslice.pipeline import build_pipeline


def _records(n: int = 10, level: str = "info") -> list[dict]:
    return [{"i": i, "level": level, "msg": f"msg {i}"} for i in range(1, n + 1)]


def test_no_options_yields_all():
    records = _records(5)
    assert list(build_pipeline(records)) == records


def test_query_filters_records():
    records = [
        {"level": "info", "msg": "ok"},
        {"level": "error", "msg": "bad"},
        {"level": "info", "msg": "also ok"},
    ]
    result = list(build_pipeline(records, query="level=error"))
    assert len(result) == 1
    assert result[0]["level"] == "error"


def test_limit_truncates_output():
    result = list(build_pipeline(_records(20), limit=5))
    assert len(result) == 5


def test_limit_larger_than_stream():
    result = list(build_pipeline(_records(3), limit=100))
    assert len(result) == 3


def test_every_n_sampling():
    result = list(build_pipeline(_records(10), every_n=2))
    assert [r["i"] for r in result] == [2, 4, 6, 8, 10]


def test_rate_one_keeps_all():
    records = _records(10)
    result = list(build_pipeline(records, rate=1.0))
    assert result == records


def test_query_then_limit():
    records = [
        {"level": "error", "i": i} for i in range(10)
    ] + [
        {"level": "info", "i": i} for i in range(10)
    ]
    result = list(build_pipeline(records, query="level=error", limit=3))
    assert len(result) == 3
    assert all(r["level"] == "error" for r in result)


def test_empty_query_string_no_filter():
    records = _records(4)
    assert list(build_pipeline(records, query="")) == records


def test_sampling_and_limit_combined():
    # every_n=2 on 20 records → 10; limit=4 → 4
    result = list(build_pipeline(_records(20), every_n=2, limit=4))
    assert len(result) == 4


def test_both_every_n_and_rate_raises():
    with pytest.raises(ValueError):
        list(build_pipeline(_records(), every_n=2, rate=0.5))
