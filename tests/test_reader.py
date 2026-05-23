"""Tests for the log reader utilities."""

import io
import pytest
from logslice.reader import iter_records


def _stream(text: str) -> io.StringIO:
    return io.StringIO(text)


def test_iter_records_basic():
    data = '{"level": "info", "msg": "started"}\n{"level": "error", "msg": "oops"}\n'
    records = list(iter_records(_stream(data)))
    assert len(records) == 2
    assert records[0][0]["level"] == "info"
    assert records[1][0]["msg"] == "oops"


def test_iter_records_skips_blank_lines():
    data = '{"a": 1}\n\n{"b": 2}\n'
    records = list(iter_records(_stream(data)))
    assert len(records) == 2


def test_iter_records_skips_invalid_json(capsys):
    data = 'not json\n{"ok": true}\n'
    records = list(iter_records(_stream(data)))
    assert len(records) == 1
    assert records[0][0]["ok"] is True
    captured = capsys.readouterr()
    assert "[warn]" in captured.err


def test_iter_records_skips_non_object(capsys):
    data = '[1, 2, 3]\n{"valid": 1}\n'
    records = list(iter_records(_stream(data)))
    assert len(records) == 1
    captured = capsys.readouterr()
    assert "[warn]" in captured.err


def test_iter_records_preserves_raw_line():
    line = '{"x": 42}'
    records = list(iter_records(_stream(line + "\n")))
    assert records[0][1] == line


def test_iter_records_empty_stream():
    records = list(iter_records(_stream("")))
    assert records == []
