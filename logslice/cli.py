"""Command-line entry point for logslice."""

from __future__ import annotations

import sys
import argparse
from typing import Sequence

from logslice.formatter import format_record, FORMATS
from logslice.query import parse_query, apply_filters
from logslice.reader import iter_sources


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="logslice",
        description="Stream and filter structured JSON logs.",
    )
    parser.add_argument(
        "sources",
        nargs="*",
        metavar="FILE",
        help="Log files to read (omit or use '-' for stdin).",
    )
    parser.add_argument(
        "-q", "--query",
        default="",
        metavar="QUERY",
        help="Filter expression, e.g. 'level=error status>=500'.",
    )
    parser.add_argument(
        "-f", "--format",
        default="json",
        choices=FORMATS,
        dest="fmt",
        help="Output format (default: json).",
    )
    parser.add_argument(
        "-n", "--limit",
        type=int,
        default=None,
        metavar="N",
        help="Stop after emitting N records.",
    )
    return parser


def run(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    filters = parse_query(args.query)
    sources = args.sources if args.sources else ["-"]

    count = 0
    try:
        for record in iter_sources(sources):
            if not apply_filters(record, filters):
                continue
            print(format_record(record, fmt=args.fmt))
            count += 1
            if args.limit is not None and count >= args.limit:
                break
    except BrokenPipeError:
        pass
    except KeyboardInterrupt:
        pass

    return 0


def main() -> None:
    sys.exit(run())
