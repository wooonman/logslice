"""Tests for logslice.session."""

from logslice.session import flatten_sessions, label_sessions, session_stats


def _group(*keys):
    return [{"req": k, "ts": float(i)} for i, k in enumerate(keys, 1)]


# ---------------------------------------------------------------------------
# label_sessions
# ---------------------------------------------------------------------------

def test_label_sessions_adds_field():
    groups = [_group("a", "a")]
    result = list(label_sessions(groups))
    assert all("session_id" in r for r in result[0])


def test_label_sessions_same_id_within_group():
    groups = [_group("a", "a", "a")]
    result = list(label_sessions(groups))
    ids = {r["session_id"] for r in result[0]}
    assert len(ids) == 1


def test_label_sessions_different_ids_across_groups():
    groups = [_group("a"), _group("b")]
    result = list(label_sessions(groups))
    id0 = result[0][0]["session_id"]
    id1 = result[1][0]["session_id"]
    assert id0 != id1


def test_label_sessions_custom_field_and_prefix():
    groups = [_group("x")]
    result = list(label_sessions(groups, session_field="sid", prefix="run"))
    assert "sid" in result[0][0]
    assert result[0][0]["sid"].startswith("run-")


def test_label_sessions_start_index():
    groups = [_group("a")]
    result = list(label_sessions(groups, start=100))
    assert result[0][0]["session_id"] == "sess-000100"


def test_label_sessions_empty():
    assert list(label_sessions([])) == []


# ---------------------------------------------------------------------------
# flatten_sessions
# ---------------------------------------------------------------------------

def test_flatten_sessions_yields_all_records():
    groups = [_group("a", "b"), _group("c")]
    flat = list(flatten_sessions(groups))
    assert len(flat) == 3


def test_flatten_sessions_preserves_order():
    groups = [[{"n": 1}, {"n": 2}], [{"n": 3}]]
    flat = list(flatten_sessions(groups))
    assert [r["n"] for r in flat] == [1, 2, 3]


def test_flatten_sessions_empty():
    assert list(flatten_sessions([])) == []


# ---------------------------------------------------------------------------
# session_stats
# ---------------------------------------------------------------------------

def test_session_stats_size():
    groups = [_group("a", "a", "a")]
    stats = list(session_stats(groups))
    assert stats[0]["size"] == 3


def test_session_stats_duration():
    group = [{"ts": 1.0}, {"ts": 4.0}]
    stats = list(session_stats([group]))
    assert stats[0]["duration"] == 3.0


def test_session_stats_no_timestamps():
    group = [{"msg": "x"}, {"msg": "y"}]
    stats = list(session_stats([group]))
    assert stats[0]["duration"] is None
    assert stats[0]["first_ts"] is None


def test_session_stats_single_record_no_duration():
    group = [{"ts": 5.0}]
    stats = list(session_stats([group]))
    assert stats[0]["duration"] is None


def test_session_stats_empty():
    assert list(session_stats([])) == []
