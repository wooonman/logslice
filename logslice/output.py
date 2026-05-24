"""Output pipeline: format a record and optionally highlight it."""

from __future__ import annotations

import sys
from typing import Any, TextIO

from logslice.formatter import format_record
from logslice.highlighter import highlight_record


def _supports_colour(stream: TextIO) -> bool:
    """Return True when *stream* looks like a colour-capable terminal."""
    return hasattr(stream, "isatty") and stream.isatty()


def emit(
    record: dict[str, Any],
    fmt: str = "text",
    colour: bool | None = None,
    stream: TextIO | None = None,
) -> None:
    """Format *record* and write it to *stream* (default: stdout).

    Parameters
    ----------
    record:
        The parsed JSON log record.
    fmt:
        One of ``"text"``, ``"json"``, or ``"pretty"``.
    colour:
        ``True`` to force ANSI colour, ``False`` to disable, ``None`` to
        auto-detect based on whether *stream* is a TTY.
    stream:
        Output stream; defaults to ``sys.stdout``.
    """
    if stream is None:
        stream = sys.stdout

    line = format_record(record, fmt=fmt)

    if colour is None:
        use_colour = _supports_colour(stream) and fmt == "json"
    else:
        use_colour = colour and fmt == "json"

    line = highlight_record(line, use_colour=use_colour)
    stream.write(line + "\n")


def emit_all(
    records: list[dict[str, Any]],
    fmt: str = "text",
    colour: bool | None = None,
    stream: TextIO | None = None,
) -> None:
    """Emit every record in *records*."""
    for record in records:
        emit(record, fmt=fmt, colour=colour, stream=stream)
