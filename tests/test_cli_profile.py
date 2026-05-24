"""Tests for the 'profile' CLI sub-command."""

import json
from argparse import Namespace
from io import StringIO
from unittest.mock import patch

import pytest

from logslice.cli_profile import run_profile, _print_stat


FAKE_RECORDS = [
    {"level": "info", "latency": 10},
    {"level": "warn", "latency": 20},
    {"level": "info", "latency": 30},
]


def _args(sources=None, fields=None, as_json=False):
    return Namespace(
        sources=sources or ["-"],
        fields=fields,
        as_json=as_json,
    )


def test_run_profile_json_output(capsys):
    with patch("logslice.cli_profile.iter_sources", return_value=FAKE_RECORDS):
        run_profile(_args(as_json=True))
    out = capsys.readouterr().out
    lines = [l for l in out.strip().splitlines() if l]
    assert len(lines) >= 1
    parsed = json.loads(lines[0])
    assert "field" in parsed
    assert "present" in parsed


def test_run_profile_text_output_contains_field(capsys):
    with patch("logslice.cli_profile.iter_sources", return_value=FAKE_RECORDS):
        run_profile(_args())
    out = capsys.readouterr().out
    assert "level" in out
    assert "latency" in out


def test_run_profile_specific_fields(capsys):
    with patch("logslice.cli_profile.iter_sources", return_value=FAKE_RECORDS):
        run_profile(_args(fields=["level"]))
    out = capsys.readouterr().out
    assert "level" in out
    assert "latency" not in out


def test_run_profile_numeric_section_present(capsys):
    with patch("logslice.cli_profile.iter_sources", return_value=FAKE_RECORDS):
        run_profile(_args(fields=["latency"]))
    out = capsys.readouterr().out
    assert "numeric" in out or "mean" in out


def test_run_profile_empty_stream(capsys):
    with patch("logslice.cli_profile.iter_sources", return_value=[]):
        run_profile(_args())
    out = capsys.readouterr().out
    assert out == ""


def test_print_stat_shows_field_name(capsys):
    stat = {"field": "foo", "total": 3, "present": 3, "missing": 0,
            "types": {"str": 3}, "top_values": ["a", "b"]}
    _print_stat(stat)
    out = capsys.readouterr().out
    assert "foo" in out


def test_print_stat_numeric_shown_when_present(capsys):
    stat = {
        "field": "latency", "total": 2, "present": 2, "missing": 0,
        "types": {"int": 2}, "top_values": ["10", "20"],
        "numeric": {"count": 2, "min": 10.0, "max": 20.0,
                    "mean": 15.0, "stddev": 5.0, "median": 15.0},
    }
    _print_stat(stat)
    out = capsys.readouterr().out
    assert "mean" in out
    assert "stddev" in out
