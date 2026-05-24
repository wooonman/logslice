"""Tests for logslice.tail."""

from __future__ import annotations

import io
import threading
import time
from unittest.mock import patch, mock_open, MagicMock

import pytest

from logslice.tail import tail_file, tail_stream, DEFAULT_POLL_INTERVAL


# ---------------------------------------------------------------------------
# tail_stream helpers
# ---------------------------------------------------------------------------

def _lines_from_stream(lines: list[str], limit: int) -> list[str]:
    """Drive tail_stream with a StringIO that has all lines ready."""
    text = "\n".join(lines) + "\n"
    stream = io.StringIO(text)
    results = []
    # tail_stream blocks forever; we stop after *limit* yields.
    gen = tail_stream(stream, poll_interval=0)
    for _ in range(limit):
        results.append(next(gen))
    return results


def test_tail_stream_yields_lines():
    result = _lines_from_stream(['{"a": 1}', '{"b": 2}'], limit=2)
    assert result == ['{"a": 1}', '{"b": 2}']


def test_tail_stream_strips_newline():
    stream = io.StringIO('{"x": 1}\n')
    gen = tail_stream(stream, poll_interval=0)
    line = next(gen)
    assert line == '{"x": 1}'


def test_tail_stream_blocks_when_empty():
    """Generator should sleep (not raise) when no data is available."""
    stream = io.StringIO("")
    sleep_calls: list[float] = []

    def fake_sleep(n: float) -> None:
        sleep_calls.append(n)
        if len(sleep_calls) >= 3:
            raise StopIteration  # escape the infinite loop in the test

    gen = tail_stream(stream, poll_interval=0.1)
    with patch("logslice.tail.time.sleep", side_effect=fake_sleep):
        with pytest.raises(StopIteration):
            next(gen)

    assert len(sleep_calls) >= 1


# ---------------------------------------------------------------------------
# tail_file helpers
# ---------------------------------------------------------------------------

def test_tail_file_from_start(tmp_path):
    log = tmp_path / "app.log"
    log.write_text('{"level": "info"}\n{"level": "warn"}\n', encoding="utf-8")

    gen = tail_file(str(log), poll_interval=0, from_start=True)
    lines = [next(gen), next(gen)]
    assert lines == ['{"level": "info"}', '{"level": "warn"}']


def test_tail_file_default_seeks_to_end(tmp_path):
    """Without from_start the existing content should be skipped."""
    log = tmp_path / "app.log"
    log.write_text('{"old": true}\n', encoding="utf-8")

    sleep_calls: list[float] = []

    def fake_sleep(n: float) -> None:
        sleep_calls.append(n)
        # append a new line then stop
        with open(str(log), "a", encoding="utf-8") as fh:
            fh.write('{"new": true}\n')
        # prevent infinite sleep loop after the new line is consumed
        if len(sleep_calls) > 5:
            raise RuntimeError("too many sleeps")

    gen = tail_file(str(log), poll_interval=0.05)
    with patch("logslice.tail.time.sleep", side_effect=fake_sleep):
        line = next(gen)

    assert line == '{"new": true}'


def test_default_poll_interval_value():
    assert DEFAULT_POLL_INTERVAL == 0.25
