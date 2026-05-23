"""Read and parse JSON log lines from files or stdin."""

import json
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import TextIO


def iter_records(source: TextIO) -> Iterator[tuple[dict, str]]:
    """Yield (parsed_record, raw_line) tuples from a line-delimited JSON stream.
    Malformed lines are skipped with a warning to stderr.
    """
    for lineno, line in enumerate(source, start=1):
        line = line.rstrip("\n")
        if not line:
            continue
        try:
            record = json.loads(line)
            if isinstance(record, dict):
                yield record, line
            else:
                print(f"[warn] line {lineno}: expected JSON object, got {type(record).__name__}", file=sys.stderr)
        except json.JSONDecodeError as exc:
            print(f"[warn] line {lineno}: invalid JSON — {exc.msg}", file=sys.stderr)


def open_source(path: str | None) -> TextIO:
    """Open a file path for reading, or return stdin if path is None or '-'."""
    if path is None or path == "-":
        return sys.stdin
    p = Path(path)
    if not p.exists():
        print(f"[error] file not found: {path}", file=sys.stderr)
        sys.exit(1)
    return p.open("r", encoding="utf-8")


def iter_sources(paths: list[str]) -> Iterator[tuple[dict, str, str]]:
    """Iterate over multiple sources, yielding (record, raw_line, source_name)."""
    if not paths:
        paths = ["-"]
    for path in paths:
        source_name = "<stdin>" if path == "-" else path
        fh = open_source(path)
        try:
            for record, raw in iter_records(fh):
                yield record, raw, source_name
        finally:
            if fh is not sys.stdin:
                fh.close()
