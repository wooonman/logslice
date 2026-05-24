"""Tests for logslice.watcher."""

from __future__ import annotations

import json
import threading
import time
from unittest.mock import patch

import pytest

from logslice.query import parse_query
from logslice.watcher import watch_file, watch_files_threaded


# ---------------------------------------------------------------------------
# watch_file
# ---------------------------------------------------------------------------

def _write_lines(path, lines: list[str]) -> None:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_watch_file_yields_parsed_records(tmp_path):
    log = tmp_path / "a.log"
    records = [{"level": "info", "msg": "hello"}, {"level": "error", "msg": "boom"}]
    _write_lines(log, [json.dumps(r) for r in records])

    gen = watch_file(str(log), from_start=True, poll_interval=0)
    result = [next(gen), next(gen)]
    assert result == records


def test_watch_file_skips_invalid_json(tmp_path):
    log = tmp_path / "b.log"
    _write_lines(log, ["not-json", '{"ok": true}'])

    gen = watch_file(str(log), from_start=True, poll_interval=0)
    record = next(gen)
    assert record == {"ok": True}


def test_watch_file_skips_non_object_json(tmp_path):
    log = tmp_path / "c.log"
    _write_lines(log, ["[1,2,3]", '{"ok": true}'])

    gen = watch_file(str(log), from_start=True, poll_interval=0)
    record = next(gen)
    assert record == {"ok": True}


def test_watch_file_applies_filters(tmp_path):
    log = tmp_path / "d.log"
    _write_lines(log, [
        json.dumps({"level": "debug", "msg": "skip"}),
        json.dumps({"level": "error", "msg": "keep"}),
    ])

    filters = parse_query("level=error")
    gen = watch_file(str(log), filters=filters, from_start=True, poll_interval=0)
    record = next(gen)
    assert record["level"] == "error"


def test_watch_file_skips_blank_lines(tmp_path):
    log = tmp_path / "e.log"
    log.write_text('\n\n{"x": 1}\n', encoding="utf-8")

    gen = watch_file(str(log), from_start=True, poll_interval=0)
    record = next(gen)
    assert record == {"x": 1}


# ---------------------------------------------------------------------------
# watch_files_threaded
# ---------------------------------------------------------------------------

def test_watch_files_threaded_calls_callback(tmp_path):
    log = tmp_path / "f.log"
    _write_lines(log, [json.dumps({"n": i}) for i in range(3)])

    received: list[dict] = []
    event = threading.Event()

    def cb(record: dict) -> None:
        received.append(record)
        if len(received) >= 3:
            event.set()

    threads = watch_files_threaded(
        [str(log)],
        callback=cb,
        from_start=True,
        poll_interval=0,
    )
    assert len(threads) == 1
    assert threads[0].daemon is True

    event.wait(timeout=3)
    assert len(received) == 3


def test_watch_files_threaded_multiple_files(tmp_path):
    logs = []
    for i in range(2):
        p = tmp_path / f"g{i}.log"
        p.write_text(json.dumps({"src": i}) + "\n", encoding="utf-8")
        logs.append(str(p))

    received: list[dict] = []
    event = threading.Event()

    def cb(record: dict) -> None:
        received.append(record)
        if len(received) >= 2:
            event.set()

    watch_files_threaded(logs, callback=cb, from_start=True, poll_interval=0)
    event.wait(timeout=3)
    assert len(received) == 2
    assert {r["src"] for r in received} == {0, 1}
