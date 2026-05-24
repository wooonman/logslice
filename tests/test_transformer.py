"""Tests for logslice.transformer."""

from __future__ import annotations

import pytest

from logslice.transformer import (
    add_field,
    drop_fields,
    flatten,
    keep_fields,
    map_field,
    rename_fields,
)


def _records():
    return [
        {"level": "info", "msg": "hello", "ts": 1},
        {"level": "error", "msg": "boom", "ts": 2},
        {"level": "debug", "msg": "trace", "ts": 3},
    ]


# --- rename_fields ---

def test_rename_fields_basic():
    out = list(rename_fields(_records(), {"level": "severity", "msg": "message"}))
    assert out[0] == {"severity": "info", "message": "hello", "ts": 1}


def test_rename_fields_unknown_key_kept():
    out = list(rename_fields([{"a": 1, "b": 2}], {"a": "alpha"}))
    assert out[0] == {"alpha": 1, "b": 2}


def test_rename_fields_empty_mapping_unchanged():
    recs = _records()
    out = list(rename_fields(recs, {}))
    assert out == recs


# --- drop_fields ---

def test_drop_fields_removes_listed():
    out = list(drop_fields(_records(), ["ts", "msg"]))
    assert all("ts" not in r and "msg" not in r for r in out)


def test_drop_fields_unknown_field_safe():
    out = list(drop_fields(_records(), ["nonexistent"]))
    assert out == _records()


# --- keep_fields ---

def test_keep_fields_only_listed_remain():
    out = list(keep_fields(_records(), ["level"]))
    assert out == [{"level": "info"}, {"level": "error"}, {"level": "debug"}]


def test_keep_fields_empty_list_yields_empty_dicts():
    out = list(keep_fields(_records(), []))
    assert all(r == {} for r in out)


# --- add_field ---

def test_add_field_constant():
    out = list(add_field(_records(), "app", lambda r: "myapp"))
    assert all(r["app"] == "myapp" for r in out)


def test_add_field_derived():
    out = list(add_field(_records(), "upper_level", lambda r: r["level"].upper()))
    assert out[0]["upper_level"] == "INFO"


# --- map_field ---

def test_map_field_transforms_value():
    out = list(map_field(_records(), "level", str.upper))
    assert [r["level"] for r in out] == ["INFO", "ERROR", "DEBUG"]


def test_map_field_missing_ok_yields_unchanged():
    recs = [{"msg": "hi"}]
    out = list(map_field(recs, "level", str.upper, missing_ok=True))
    assert out == [{"msg": "hi"}]


def test_map_field_missing_raises_when_not_ok():
    with pytest.raises(KeyError):
        list(map_field([{"msg": "hi"}], "level", str.upper, missing_ok=False))


# --- flatten ---

def test_flatten_hoists_nested_keys():
    recs = [{"meta": {"host": "srv1", "env": "prod"}, "msg": "ok"}]
    out = list(flatten(recs, "meta"))
    assert out[0] == {"msg": "ok", "meta_host": "srv1", "meta_env": "prod"}


def test_flatten_custom_prefix():
    recs = [{"ctx": {"user": "alice"}, "level": "info"}]
    out = list(flatten(recs, "ctx", prefix="context."))
    assert "context.user" in out[0]


def test_flatten_missing_nested_field_safe():
    recs = [{"level": "info"}]
    out = list(flatten(recs, "meta"))
    assert out == [{"level": "info"}]
