"""Tests for logslice.highlighter."""

from __future__ import annotations

import pytest

from logslice.highlighter import (
    colourise_level,
    colourise_json,
    highlight_record,
)


# ---------------------------------------------------------------------------
# colourise_level
# ---------------------------------------------------------------------------


def test_colourise_level_known_levels_contain_ansi():
    for level in ("debug", "info", "warn", "warning", "error", "critical", "fatal"):
        result = colourise_level(level)
        assert "\033[" in result, f"expected ANSI code for level {level!r}"


def test_colourise_level_uppercases_text():
    result = colourise_level("info")
    assert "INFO" in result


def test_colourise_level_unknown_level_no_colour():
    result = colourise_level("trace")
    assert result == "TRACE"
    assert "\033[" not in result


def test_colourise_level_case_insensitive():
    lower = colourise_level("error")
    upper = colourise_level("ERROR")
    assert lower == upper


# ---------------------------------------------------------------------------
# colourise_json
# ---------------------------------------------------------------------------


def test_colourise_json_contains_ansi_codes():
    text = '{"level": "info", "msg": "hello"}'
    result = colourise_json(text)
    assert "\033[" in result


def test_colourise_json_preserves_keys():
    text = '{"level": "info"}'
    result = colourise_json(text)
    assert "level" in result
    assert "info" in result


def test_colourise_json_numeric_value():
    text = '{"count": 42}'
    result = colourise_json(text)
    assert "42" in result
    assert "\033[" in result


def test_colourise_json_boolean_value():
    text = '{"ok": true}'
    result = colourise_json(text)
    assert "true" in result


def test_colourise_json_null_value():
    text = '{"field": null}'
    result = colourise_json(text)
    assert "null" in result


# ---------------------------------------------------------------------------
# highlight_record
# ---------------------------------------------------------------------------


def test_highlight_record_with_colour():
    line = '{"level": "error"}'
    result = highlight_record(line, use_colour=True)
    assert "\033[" in result


def test_highlight_record_without_colour_returns_unchanged():
    line = '{"level": "error"}'
    result = highlight_record(line, use_colour=False)
    assert result == line
