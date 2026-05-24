"""Tests for logslice.writer."""

import io
from pathlib import Path

import pytest

from logslice.writer import write_lines, append_lines


LINES = ['{"a":1}', '{"b":2}', '{"c":3}']


# --- write_lines to file ---

def test_write_lines_creates_file(tmp_path):
    dest = tmp_path / "out.jsonl"
    write_lines(LINES, dest)
    assert dest.exists()


def test_write_lines_returns_count(tmp_path):
    dest = tmp_path / "out.jsonl"
    n = write_lines(LINES, dest)
    assert n == 3


def test_write_lines_content(tmp_path):
    dest = tmp_path / "out.jsonl"
    write_lines(LINES, dest)
    written = dest.read_text().splitlines()
    assert written == LINES


def test_write_lines_creates_parent_dirs(tmp_path):
    dest = tmp_path / "nested" / "deep" / "out.jsonl"
    write_lines(LINES, dest)
    assert dest.exists()


def test_write_lines_empty(tmp_path):
    dest = tmp_path / "empty.jsonl"
    n = write_lines([], dest)
    assert n == 0
    assert dest.read_text() == ""


# --- write_lines to stdout ---

def test_write_lines_stdout(capsys):
    write_lines(LINES, destination=None)
    captured = capsys.readouterr()
    assert captured.out.strip().splitlines() == LINES


def test_write_lines_stdout_returns_count(capsys):
    n = write_lines(LINES, destination=None)
    assert n == 3


# --- append_lines ---

def test_append_lines_creates_file(tmp_path):
    dest = tmp_path / "log.jsonl"
    append_lines(LINES[:1], dest)
    assert dest.exists()


def test_append_lines_appends(tmp_path):
    dest = tmp_path / "log.jsonl"
    write_lines(LINES[:2], dest)
    append_lines(LINES[2:], dest)
    written = dest.read_text().splitlines()
    assert written == LINES


def test_append_lines_returns_count(tmp_path):
    dest = tmp_path / "log.jsonl"
    n = append_lines(LINES, dest)
    assert n == 3
