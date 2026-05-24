"""Tests for logslice.truncator."""

import pytest

from logslice.truncator import cap_list_field, truncate_field, truncate_fields


def _records(*overrides):
    base = {"msg": "hello world", "level": "info", "tags": ["a", "b", "c"]}
    return [{**base, **ov} for ov in overrides]


# --- truncate_field ---

def test_truncate_field_shortens_long_string():
    recs = [{"msg": "hello world"}]
    result = list(truncate_field(recs, "msg", 5))
    assert result[0]["msg"] == "hello..."


def test_truncate_field_leaves_short_string_unchanged():
    recs = [{"msg": "hi"}]
    result = list(truncate_field(recs, "msg", 10))
    assert result[0]["msg"] == "hi"


def test_truncate_field_exact_length_unchanged():
    recs = [{"msg": "hello"}]
    result = list(truncate_field(recs, "msg", 5))
    assert result[0]["msg"] == "hello"


def test_truncate_field_missing_field_unchanged():
    recs = [{"level": "info"}]
    result = list(truncate_field(recs, "msg", 5))
    assert result[0] == {"level": "info"}


def test_truncate_field_non_string_unchanged():
    recs = [{"count": 12345}]
    result = list(truncate_field(recs, "count", 3))
    assert result[0]["count"] == 12345


def test_truncate_field_custom_placeholder():
    recs = [{"msg": "hello world"}]
    result = list(truncate_field(recs, "msg", 5, placeholder="[cut]"))
    assert result[0]["msg"] == "hello[cut]"


def test_truncate_field_zero_length():
    recs = [{"msg": "hi"}]
    result = list(truncate_field(recs, "msg", 0))
    assert result[0]["msg"] == "..."


def test_truncate_field_negative_raises():
    with pytest.raises(ValueError):
        list(truncate_field([{"msg": "hi"}], "msg", -1))


def test_truncate_field_does_not_mutate_original():
    original = {"msg": "hello world"}
    list(truncate_field([original], "msg", 5))
    assert original["msg"] == "hello world"


# --- truncate_fields ---

def test_truncate_fields_applies_multiple_limits():
    recs = [{"msg": "hello world", "src": "long-source-name"}]
    result = list(truncate_fields(recs, {"msg": 5, "src": 4}))
    assert result[0]["msg"] == "hello..."
    assert result[0]["src"] == "long..."


def test_truncate_fields_negative_limit_raises():
    with pytest.raises(ValueError):
        list(truncate_fields([{"msg": "hi"}], {"msg": -1}))


# --- cap_list_field ---

def test_cap_list_field_trims_long_list():
    recs = [{"tags": ["a", "b", "c", "d"]}]
    result = list(cap_list_field(recs, "tags", 2))
    assert result[0]["tags"] == ["a", "b"]


def test_cap_list_field_short_list_unchanged():
    recs = [{"tags": ["a", "b"]}]
    result = list(cap_list_field(recs, "tags", 5))
    assert result[0]["tags"] == ["a", "b"]


def test_cap_list_field_non_list_unchanged():
    recs = [{"tags": "not-a-list"}]
    result = list(cap_list_field(recs, "tags", 2))
    assert result[0]["tags"] == "not-a-list"


def test_cap_list_field_missing_field_unchanged():
    recs = [{"level": "info"}]
    result = list(cap_list_field(recs, "tags", 2))
    assert result[0] == {"level": "info"}


def test_cap_list_field_zero_items():
    recs = [{"tags": ["a", "b"]}]
    result = list(cap_list_field(recs, "tags", 0))
    assert result[0]["tags"] == []


def test_cap_list_field_negative_raises():
    with pytest.raises(ValueError):
        list(cap_list_field([{"tags": []}], "tags", -1))
