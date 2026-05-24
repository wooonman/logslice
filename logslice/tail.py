"""Tail support: follow a file or stream for new JSON log lines."""

from __future__ import annotations

import io
import time
from typing import Generator, IO


DEFAULT_POLL_INTERVAL = 0.25  # seconds


def tail_file(
    path: str,
    poll_interval: float = DEFAULT_POLL_INTERVAL,
    from_start: bool = False,
) -> Generator[str, None, None]:
    """Yield new lines appended to *path*, blocking between polls.

    Parameters
    ----------
    path:
        Filesystem path to follow.
    poll_interval:
        Seconds to sleep between read attempts when no data is available.
    from_start:
        If True read from the beginning of the file; otherwise seek to the
        end before starting (like ``tail -f``).
    """
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        if not from_start:
            fh.seek(0, io.SEEK_END)
        while True:
            line = fh.readline()
            if line:
                yield line.rstrip("\n")
            else:
                time.sleep(poll_interval)


def tail_stream(
    stream: IO[str],
    poll_interval: float = DEFAULT_POLL_INTERVAL,
) -> Generator[str, None, None]:
    """Yield lines from an already-open text stream, blocking when empty.

    Useful for piped input that trickles in over time.
    """
    while True:
        line = stream.readline()
        if line:
            yield line.rstrip("\n")
        else:
            time.sleep(poll_interval)
