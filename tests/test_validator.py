"""Tests for logslice.validator."""

from __future__ import annotations

import pytest

from logslice.validator import filter_valid, validate_record


SCHEMA = {
    "level": {"type": "str", "required": True},
    "ts": {"type": "float", "required": True},
    "msg": {"type": "str", "required": False},
    "count": {"type": "int", "required": False},
}


# ---------------------------------------------------------------------------
# validate_record
# ---------------------------------------------------------------------------

def test_valid_record_returns_no_errors():
    record = {"level": "info", "ts": 1.0, "msg": "hello"}
    assert validate_record(record, SCHEMA) == []


def test_missing_required_field_is_error():
    record = {"ts": 1.0, "msg": "hi"}
    errors = validate_record(record, SCHEMA)
    assert any("level" in e for e in errors)


def test_missing_optional_field_is_not_error():
    record = {"level": "warn", "ts": 2.0}
    errors = validate_record(record, SCHEMA)
    assert errors == []


def test_wrong_type_is_error():
    record = {"level": 42, "ts": 1.0}
    errors = validate_record(record, SCHEMA)
    assert any("level" in e for e in errors)
    assert any("int" in e for e in errors)


def test_multiple_errors_returned():
    record = {"msg": 99}  # missing level, missing ts, msg wrong type
    errors = validate_record(record, SCHEMA)
    assert len(errors) >= 2


def test_unknown_type_name_produces_error():
    schema = {"x": {"type": "uuid", "required": False}}
    record = {"x": "abc"}
    errors = validate_record(record, schema)
    assert any("unknown type" in e for e in errors)


def test_extra_fields_are_ignored():
    record = {"level": "debug", "ts": 0.5, "extra": "whatever"}
    assert validate_record(record, SCHEMA) == []


# ---------------------------------------------------------------------------
# filter_valid
# ---------------------------------------------------------------------------

def test_filter_valid_drops_invalid_by_default():
    records = [
        {"level": "info", "ts": 1.0},
        {"ts": 2.0},  # missing required level
        {"level": "error", "ts": 3.0},
    ]
    result = list(filter_valid(records, SCHEMA))
    assert len(result) == 2
    assert all("level" in r for r in result)


def test_filter_valid_annotates_when_drop_invalid_false():
    records = [
        {"level": "info", "ts": 1.0},
        {"ts": 2.0},
    ]
    result = list(filter_valid(records, SCHEMA, drop_invalid=False))
    assert len(result) == 2
    invalid = [r for r in result if "_validation_errors" in r]
    assert len(invalid) == 1
    assert isinstance(invalid[0]["_validation_errors"], list)


def test_filter_valid_empty_stream():
    assert list(filter_valid([], SCHEMA)) == []


def test_filter_valid_all_pass():
    records = [{"level": "info", "ts": float(i)} for i in range(5)]
    result = list(filter_valid(records, SCHEMA))
    assert len(result) == 5
