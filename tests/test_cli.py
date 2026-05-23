"""Tests for logslice.cli."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from logslice.cli import run, build_parser


LINES = [
    '{"level": "info", "message": "started", "code": 200}',
    '{"level": "error", "message": "boom", "code": 500}',
    '{"level": "info", "message": "done", "code": 201}',
]


def _fake_iter_sources(sources):
    for line in LINES:
        yield json.loads(line)


@patch("logslice.cli.iter_sources", side_effect=_fake_iter_sources)
def test_run_no_filter_prints_all(mock_iter, capsys):
    rc = run(["-"])
    assert rc == 0
    out = capsys.readouterr().out.strip().splitlines()
    assert len(out) == 3


@patch("logslice.cli.iter_sources", side_effect=_fake_iter_sources)
def test_run_with_query_filters(mock_iter, capsys):
    rc = run(["-", "-q", "level=error"])
    assert rc == 0
    out = capsys.readouterr().out.strip().splitlines()
    assert len(out) == 1
    assert json.loads(out[0])["message"] == "boom"


@patch("logslice.cli.iter_sources", side_effect=_fake_iter_sources)
def test_run_limit(mock_iter, capsys):
    rc = run(["-", "-n", "1"])
    assert rc == 0
    out = capsys.readouterr().out.strip().splitlines()
    assert len(out) == 1


@patch("logslice.cli.iter_sources", side_effect=_fake_iter_sources)
def test_run_pretty_format(mock_iter, capsys):
    rc = run(["-", "-f", "pretty"])
    assert rc == 0
    out = capsys.readouterr().out
    # pretty output has newlines inside records
    assert out.count("\n") > 3


@patch("logslice.cli.iter_sources", side_effect=_fake_iter_sources)
def test_run_text_format(mock_iter, capsys):
    rc = run(["-", "-f", "text"])
    assert rc == 0
    out = capsys.readouterr().out.strip().splitlines()
    assert len(out) == 3
    assert "[INFO]" in out[0] or "[ERROR]" in out[1]


def test_build_parser_defaults():
    parser = build_parser()
    args = parser.parse_args([])
    assert args.query == ""
    assert args.fmt == "json"
    assert args.limit is None
