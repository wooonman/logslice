"""Tests for logslice.correlator."""

from logslice.correlator import correlate, correlate_exact


def _r(key, ts, **extra):
    return {"req": key, "ts": ts, **extra}


# ---------------------------------------------------------------------------
# correlate (time-window)
# ---------------------------------------------------------------------------

def test_correlate_groups_same_key():
    records = [
        _r("a", 1.0, msg="start"),
        _r("a", 1.5, msg="middle"),
        _r("a", 2.0, msg="end"),
    ]
    groups = list(correlate(records, "req", window=5.0))
    assert len(groups) == 1
    assert len(groups[0]) == 3


def test_correlate_flushes_expired_group():
    records = [
        _r("a", 1.0),
        _r("b", 8.0),  # ts - start_a > 5 → flush a
        _r("b", 9.0),
    ]
    groups = list(correlate(records, "req", window=5.0))
    keys = [[r["req"] for r in g] for g in groups]
    assert ["a"] in keys
    assert any(all(r == "b" for r in g) for g in keys)


def test_correlate_skips_records_missing_field():
    records = [
        {"ts": 1.0, "msg": "no key"},
        _r("a", 2.0),
    ]
    groups = list(correlate(records, "req", window=5.0))
    assert len(groups) == 1
    assert groups[0][0]["req"] == "a"


def test_correlate_empty_stream():
    assert list(correlate([], "req")) == []


def test_correlate_single_record():
    groups = list(correlate([_r("x", 1.0)], "req", window=5.0))
    assert len(groups) == 1
    assert groups[0][0]["req"] == "x"


def test_correlate_custom_timestamp_field():
    records = [
        {"id": "a", "time": 1.0},
        {"id": "a", "time": 2.0},
    ]
    groups = list(correlate(records, "id", timestamp_field="time", window=5.0))
    assert len(groups) == 1
    assert len(groups[0]) == 2


# ---------------------------------------------------------------------------
# correlate_exact
# ---------------------------------------------------------------------------

def test_correlate_exact_yields_when_count_reached():
    records = [_r("a", i) for i in range(3)]
    groups = list(correlate_exact(records, "req", expected=3))
    assert len(groups) == 1
    assert len(groups[0]) == 3


def test_correlate_exact_multiple_keys():
    records = [
        _r("a", 1), _r("b", 2),
        _r("a", 3), _r("b", 4),
    ]
    groups = list(correlate_exact(records, "req", expected=2))
    assert len(groups) == 2


def test_correlate_exact_incomplete_group_flushed_at_end():
    records = [_r("a", 1), _r("a", 2), _r("a", 3)]
    groups = list(correlate_exact(records, "req", expected=5))
    assert len(groups) == 1
    assert len(groups[0]) == 3


def test_correlate_exact_skips_missing_field():
    records = [{"ts": 1}, _r("a", 2), _r("a", 3)]
    groups = list(correlate_exact(records, "req", expected=2))
    assert len(groups) == 1
    assert all(r["req"] == "a" for r in groups[0])


def test_correlate_exact_empty_stream():
    assert list(correlate_exact([], "req", expected=2)) == []
