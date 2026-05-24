"""Write exported log lines to a file path or stdout."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable, Optional, Union


def write_lines(
    lines: Iterable[str],
    destination: Optional[Union[str, Path]] = None,
    encoding: str = "utf-8",
) -> int:
    """Write *lines* to *destination* (file path) or stdout if None.

    Returns the number of lines written.
    """
    if destination is None:
        return _write_to_stream(lines, sys.stdout)

    dest = Path(destination)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding=encoding) as fh:
        return _write_to_stream(lines, fh)


def _write_to_stream(lines: Iterable[str], stream) -> int:
    count = 0
    for line in lines:
        stream.write(line)
        stream.write("\n")
        count += 1
    return count


def append_lines(
    lines: Iterable[str],
    destination: Union[str, Path],
    encoding: str = "utf-8",
) -> int:
    """Append *lines* to an existing file (creates it if absent)."""
    dest = Path(destination)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("a", encoding=encoding) as fh:
        return _write_to_stream(lines, fh)
