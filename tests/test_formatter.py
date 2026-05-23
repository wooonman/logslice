"""Tests for logslice.formatter."""

from __future__ import annotations

import json
import pytest

from logslice.formatter import format_record, FORMATS


SAMPLE = {
    "timestamp": "2024-01-15T10:00:00Z",
    "level": "info",
    "message": "hello world",
    "service": "api",
    "code": 200,
}


def test_format_json_roundtrip():
    out = format_record(SAMPLE, fmt="json")
    assert json.loads(out) == SAMPLE


def test_format_json_is_single_line():
    out = format_record(SAMPLE, fmt="json")
    assert "\n" not in out


def test_format_pretty_is_multiline():
    out = format_record(SAMPLE, fmt="pretty")
    assert "\n" in out
    assert json.loads(out) == SAMPLE


def test_format_text_contains_timestamp():
    out = format_record(SAMPLE, fmt="text")
    assert "2024-01-15T10:00:00Z" in out


def test_format_text_contains_level_uppercased():
    out = format_record(SAMPLE, fmt="text")
    assert "[INFO]" in out


def test_format_text_contains_message():
    out = format_record(SAMPLE, fmt="text")
    assert "hello world" in out


def test_format_text_contains_extra_fields():
    out = format_record(SAMPLE, fmt="text")
    assert "service" in out
    assert "code" in out


def test_format_text_fallback_no_known_fields():
    record = {"foo": "bar", "baz": 1}
    out = format_record(record, fmt="text")
    # Should still produce something sensible
    assert "foo" in out


def test_format_unknown_raises():
    with pytest.raises(ValueError, match="Unknown format"):
        format_record(SAMPLE, fmt="xml")


def test_format_uses_alt_timestamp_key():
    record = {"ts": "2024-06-01", "msg": "hi"}
    out = format_record(record, fmt="text")
    assert "2024-06-01" in out
    assert "hi" in out


def test_formats_constant_contains_all():
    assert set(FORMATS) == {"json", "pretty", "text"}
