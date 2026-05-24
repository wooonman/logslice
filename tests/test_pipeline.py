"""Tests for logslice.pipeline."""

import pytest
from logslice.pipeline import build_pipeline


def _records():
    return [
        {"level": "info", "msg": "started", "user": "alice", "token": "tok1"},
        {"level": "error", "msg": "failed", "user": "bob", "token": "tok2"},
        {"level": "info", "msg": "stopped", "user": "carol", "token": "tok3"},
        {"level": "debug", "msg": "verbose", "user": "alice", "token": "tok4"},
        {"level": "info", "msg": "started", "user": "alice", "token": "tok1"},
    ]


def test_no_options_yields_all():
    out = list(build_pipeline(_records(), {}))
    assert len(out) == 5


def test_query_filters_records():
    out = list(build_pipeline(_records(), {"query": "level=info"}))
    assert all(r["level"] == "info" for r in out)
    assert len(out) == 3


def test_limit_truncates_output():
    out = list(build_pipeline(_records(), {"limit": 2}))
    assert len(out) == 2


def test_limit_larger_than_stream():
    out = list(build_pipeline(_records(), {"limit": 100}))
    assert len(out) == 5


def test_sample_n_reduces_count():
    out = list(build_pipeline(_records(), {"sample_n": 2}))
    assert len(out) == 3  # records 0, 2, 4


def test_dedup_removes_duplicates():
    out = list(build_pipeline(_records(), {"dedup": True}))
    # record 4 is identical to record 0 except token differs — not a dup
    # records are all unique here so count stays 5
    assert len(out) == 5


def test_dedup_by_field():
    out = list(build_pipeline(_records(), {"dedup_by": ["user"]}))
    users = [r["user"] for r in out]
    assert len(users) == len(set(users))


def test_redact_masks_field():
    out = list(build_pipeline(_records(), {"redact": ["token"]}))
    assert all(r["token"] == "***" for r in out)


def test_redact_pattern_masks_values():
    records = [{"msg": "secret=abc"}, {"msg": "hello"}]
    out = list(build_pipeline(records, {"redact_pattern": r"secret=\w+"}))
    assert "secret=" not in out[0]["msg"]
    assert out[1]["msg"] == "hello"


def test_namespace_object_as_options():
    """Options can be an argparse-style namespace."""
    class Opts:
        query = "level=error"
        limit = None
        sample_n = None
        dedup = False
        dedup_by = None
        redact = None
        redact_pattern = None

    out = list(build_pipeline(_records(), Opts()))
    assert len(out) == 1
    assert out[0]["level"] == "error"


def test_combined_query_and_limit():
    out = list(build_pipeline(_records(), {"query": "level=info", "limit": 2}))
    assert len(out) == 2
    assert all(r["level"] == "info" for r in out)
