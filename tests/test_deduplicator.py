"""Tests for logslice.deduplicator."""

import pytest

from logslice.deduplicator import dedup_by, dedup_exact


def _records(*dicts):
    return list(dicts)


# ---------------------------------------------------------------------------
# dedup_by
# ---------------------------------------------------------------------------

def test_dedup_by_removes_duplicates():
    records = [
        {"level": "info", "msg": "hello"},
        {"level": "info", "msg": "hello"},
        {"level": "error", "msg": "boom"},
    ]
    result = list(dedup_by(records, fields=["level", "msg"]))
    assert result == [
        {"level": "info", "msg": "hello"},
        {"level": "error", "msg": "boom"},
    ]


def test_dedup_by_single_field():
    records = [
        {"svc": "a", "val": 1},
        {"svc": "a", "val": 2},
        {"svc": "b", "val": 3},
    ]
    result = list(dedup_by(records, fields=["svc"]))
    assert len(result) == 2
    assert result[0]["svc"] == "a"
    assert result[1]["svc"] == "b"


def test_dedup_by_missing_field_treated_as_none():
    records = [
        {"a": 1},
        {"a": 1},          # duplicate — same key (1, None)
        {"a": 1, "b": 2},  # different key (1, 2)
    ]
    result = list(dedup_by(records, fields=["a", "b"]))
    assert len(result) == 2


def test_dedup_by_empty_stream():
    assert list(dedup_by([], fields=["x"])) == []


def test_dedup_by_empty_fields_raises():
    with pytest.raises(ValueError, match="fields must not be empty"):
        list(dedup_by([{"a": 1}], fields=[]))


def test_dedup_by_window_evicts_old_keys():
    # With window=2, after seeing A B C the key A should be forgotten
    records = [
        {"k": "A"},
        {"k": "B"},
        {"k": "C"},
        {"k": "A"},  # A was evicted, so this should pass through
    ]
    result = list(dedup_by(records, fields=["k"], window=2))
    assert len(result) == 4


def test_dedup_by_invalid_window_raises():
    with pytest.raises(ValueError, match="positive integer"):
        list(dedup_by([], fields=["k"], window=0))


# ---------------------------------------------------------------------------
# dedup_exact
# ---------------------------------------------------------------------------

def test_dedup_exact_removes_identical_records():
    records = [
        {"level": "info", "msg": "hi"},
        {"level": "info", "msg": "hi"},
        {"level": "warn", "msg": "uh"},
    ]
    result = list(dedup_exact(records))
    assert len(result) == 2


def test_dedup_exact_empty_stream():
    assert list(dedup_exact([])) == []
