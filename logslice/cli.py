"""Command-line interface for logslice."""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

from logslice.reader import iter_sources
from logslice.pipeline import build_pipeline
from logslice.formatter import format_record
from logslice.output import emit_all


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="logslice",
        description="Stream and filter structured JSON logs.",
    )
    p.add_argument("sources", nargs="*", default=["-"], help="Files or '-' for stdin")
    p.add_argument("-q", "--query", default=None, help="Filter expression, e.g. level=error")
    p.add_argument("-n", "--limit", type=int, default=None, help="Max records to output")
    p.add_argument("-f", "--format", dest="fmt", choices=["json", "pretty", "text"],
                   default="json", help="Output format")
    p.add_argument("--colour", action="store_true", default=False,
                   help="Force ANSI colour output")
    p.add_argument("--sample", dest="sample_n", type=int, default=None,
                   help="Keep every N-th record")
    p.add_argument("--dedup", action="store_true", default=False,
                   help="Drop exact duplicate records")
    p.add_argument("--dedup-by", dest="dedup_by", nargs="+", default=None,
                   help="Deduplicate by named fields")
    p.add_argument("--redact", nargs="+", default=None,
                   help="Field names whose values should be masked")
    p.add_argument("--redact-pattern", dest="redact_pattern", default=None,
                   help="Regex pattern — matching substrings are masked")
    return p


def run(
    sources: list[str],
    options,
    *,
    _iter_sources=iter_sources,
    _out=None,
) -> None:
    file = _out or sys.stdout
    records = _iter_sources(sources)
    pipeline = build_pipeline(records, options)
    lines = (format_record(r, fmt=options.fmt) for r in pipeline)
    emit_all(lines, colour=options.colour, file=file)


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_parser()
    options = parser.parse_args(argv)
    run(options.sources, options)


if __name__ == "__main__":  # pragma: no cover
    main()
