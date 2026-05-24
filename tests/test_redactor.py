"""Tests for logslice.redactor."""

import pytest
from logslice.redactor import redact_fields, redact_pattern, redact_partial, redact


def _records():
    return [
        {"user": "alice", "password": "s3cr3t", "level": "info"},
        {"user": "bob", "password": "hunter2", "token": "abc123", "level": "debug"},
        {"user": "carol", "level": "warn"},
    ]


# --- redact_fields ---

def test_redact_fields_masks_named_field():
    out = list(redact_fields(_records(), fields=["password"]))
    assert out[0]["password"] == "***"
    assert out[1]["password"] == "***"


def test_redact_fields_missing_field_unchanged():
    out = list(redact_fields(_records(), fields=["password"]))
    assert "password" not in out[2]


def test_redact_fields_other_fields_preserved():
    out = list(redact_fields(_records(), fields=["password"]))
    assert out[0]["user"] == "alice"
    assert out[0]["level"] == "info"


def test_redact_fields_multiple_fields():
    out = list(redact_fields(_records(), fields=["password", "token"]))
    assert out[1]["password"] == "***"
    assert out[1]["token"] == "***"


def test_redact_fields_custom_mask():
    out = list(redact_fields(_records(), fields=["password"], mask="[REDACTED]"))
    assert out[0]["password"] == "[REDACTED]"


def test_redact_fields_empty_fields_list_unchanged():
    out = list(redact_fields(_records(), fields=[]))
    assert out[0]["password"] == "s3cr3t"


def test_redact_fields_does_not_mutate_original():
    originals = _records()
    list(redact_fields(originals, fields=["password"]))
    assert originals[0]["password"] == "s3cr3t"


# --- redact_pattern ---

def test_redact_pattern_replaces_match():
    records = [{"msg": "token=abc123 logged in"}]
    out = list(redact_pattern(records, pattern=r"token=\w+"))
    assert "token=" not in out[0]["msg"]
    assert "***" in out[0]["msg"]


def test_redact_pattern_non_matching_unchanged():
    records = [{"msg": "hello world"}]
    out = list(redact_pattern(records, pattern=r"secret"))
    assert out[0]["msg"] == "hello world"


def test_redact_pattern_non_string_values_unchanged():
    records = [{"count": 42, "active": True}]
    out = list(redact_pattern(records, pattern=r"\d+"))
    assert out[0]["count"] == 42


# --- redact_partial ---

def test_redact_partial_keeps_start():
    records = [{"card": "4111111111111234"}]
    out = list(redact_partial(records, fields=["card"], keep_start=4))
    assert out[0]["card"].startswith("4111")
    assert "***" in out[0]["card"]


def test_redact_partial_keeps_end():
    records = [{"card": "4111111111111234"}]
    out = list(redact_partial(records, fields=["card"], keep_end=4))
    assert out[0]["card"].endswith("1234")


def test_redact_partial_non_string_unchanged():
    records = [{"score": 99}]
    out = list(redact_partial(records, fields=["score"], keep_start=1))
    assert out[0]["score"] == 99


# --- redact convenience wrapper ---

def test_redact_delegates_to_redact_fields():
    out = list(redact(_records(), fields=["password"]))
    assert out[0]["password"] == "***"
