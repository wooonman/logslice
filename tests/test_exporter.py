"""Tests for logslice.exporter."""

import json
import pytest

from logslice.exporter import export, to_jsonl, to_csv


RECORDS = [
    {"level": "info", "msg": "started", "svc": "api"},
    {"level": "error", "msg": "failed", "svc": "db"},
    {"level": "info", "msg": "stopped", "svc": "api"},
]


# --- to_jsonl ---

def test_to_jsonl_count():
    lines = list(to_jsonl(RECORDS))
    assert len(lines) == 3


def test_to_jsonl_valid_json():
    for line in to_jsonl(RECORDS):
        parsed = json.loads(line)
        assert isinstance(parsed, dict)


def test_to_jsonl_single_line_each():
    for line in to_jsonl(RECORDS):
        assert "\n" not in line


def test_to_jsonl_empty():
    assert list(to_jsonl([])) == []


# --- to_csv ---

def test_to_csv_header_first():
    rows = list(to_csv(RECORDS, fields=["level", "msg"]))
    assert rows[0] == "level,msg"


def test_to_csv_row_count():
    rows = list(to_csv(RECORDS, fields=["level", "msg"]))
    # header + 3 data rows
    assert len(rows) == 4


def test_to_csv_values():
    rows = list(to_csv(RECORDS, fields=["level", "svc"]))
    assert "info,api" in rows[1]


def test_to_csv_missing_field_uses_empty():
    rows = list(to_csv(RECORDS, fields=["level", "nonexistent"]))
    assert rows[1].endswith(",")


def test_to_csv_missing_field_custom_placeholder():
    rows = list(to_csv(RECORDS, fields=["level", "nonexistent"], missing="N/A"))
    assert "N/A" in rows[1]


def test_to_tsv_delimiter():
    rows = list(to_csv(RECORDS, fields=["level", "msg"], delimiter="\t"))
    assert "\t" in rows[0]


# --- export dispatcher ---

def test_export_jsonl():
    lines = list(export(RECORDS, fmt="jsonl"))
    assert len(lines) == 3


def test_export_csv_requires_fields():
    with pytest.raises(ValueError, match="fields"):
        list(export(RECORDS, fmt="csv"))


def test_export_tsv():
    rows = list(export(RECORDS, fmt="tsv", fields=["level", "svc"]))
    assert rows[0] == "level\tsvc"


def test_export_unknown_format_raises():
    with pytest.raises(ValueError, match="unsupported"):
        list(export(RECORDS, fmt="xml"))


def test_export_dotted_field():
    nested = [{"http": {"status": 200}, "msg": "ok"}]
    rows = list(to_csv(nested, fields=["http.status", "msg"]))
    assert "200" in rows[1]
