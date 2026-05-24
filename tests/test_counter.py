"""Tests for logslice.counter."""

from __future__ import annotations

import pytest

from logslice.counter import Counter, count_records, count_stream


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _records():
    return [
        {"level": "info", "msg": "a"},
        {"level": "error", "msg": "b"},
        {"level": "info", "msg": "c"},
        {"level": "warn", "msg": "d"},
    ]


# ---------------------------------------------------------------------------
# Counter unit tests
# ---------------------------------------------------------------------------

def test_counter_starts_at_zero():
    c = Counter()
    assert c.total == 0
    assert dict(c.by_value) == {}


def test_counter_increment_total():
    c = Counter()
    c.increment("info")
    c.increment("error")
    assert c.total == 2


def test_counter_increment_tracks_value():
    c = Counter()
    c.increment("info")
    c.increment("info")
    c.increment("error")
    assert c.by_value["info"] == 2
    assert c.by_value["error"] == 1


def test_counter_none_value_uses_null_key():
    c = Counter()
    c.increment(None)
    assert c.by_value["<null>"] == 1


def test_counter_reset_clears_state():
    c = Counter()
    c.increment("info")
    c.reset()
    assert c.total == 0
    assert dict(c.by_value) == {}


# ---------------------------------------------------------------------------
# count_records
# ---------------------------------------------------------------------------

def test_count_records_total():
    result = count_records(_records())
    assert result.total == 4


def test_count_records_by_field():
    result = count_records(_records(), field="level")
    assert result.by_value["info"] == 2
    assert result.by_value["error"] == 1
    assert result.by_value["warn"] == 1


def test_count_records_empty():
    result = count_records([], field="level")
    assert result.total == 0


def test_count_records_missing_field_uses_null():
    records = [{"msg": "no level"}]
    result = count_records(records, field="level")
    assert result.by_value["<null>"] == 1


# ---------------------------------------------------------------------------
# count_stream
# ---------------------------------------------------------------------------

def test_count_stream_passes_records_through():
    out = list(count_stream(_records()))
    # only original records, no checkpoints
    assert out == _records()


def test_count_stream_checkpoint_injects_summary():
    out = list(count_stream(_records(), checkpoint=2))
    checkpoints = [r for r in out if r.get("_logslice_checkpoint")]
    assert len(checkpoints) == 2
    assert checkpoints[0]["_logslice_count"] == 2
    assert checkpoints[1]["_logslice_count"] == 4


def test_count_stream_checkpoint_zero_no_summaries():
    out = list(count_stream(_records(), checkpoint=0))
    assert all("_logslice_checkpoint" not in r for r in out)


def test_count_stream_invalid_checkpoint_raises():
    with pytest.raises(ValueError):
        list(count_stream(_records(), checkpoint=-1))
