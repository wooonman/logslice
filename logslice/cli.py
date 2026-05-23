"""Command-line interface for logslice."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence

from logslice.aggregator import count_by, summarise
from logslice.formatter import format_record
from logslice.query import apply_filters, parse_query
from logslice.reader import iter_sources


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="logslice",
        description="Stream and filter structured JSON logs.",
    )
    p.add_argument("sources", nargs="*", default=["-"], help="Files or '-' for stdin")
    p.add_argument("-q", "--query", default="", help="Filter expression, e.g. 'level=error'")
    p.add_argument("-n", "--limit", type=int, default=0, help="Max records to output (0 = unlimited)")
    p.add_argument(
        "-f", "--format",
        choices=["json", "pretty", "text"],
        default="json",
        help="Output format",
    )

    agg = p.add_argument_group("aggregation (mutually exclusive)")
    agg_ex = agg.add_mutually_exclusive_group()
    agg_ex.add_argument("--count-by", metavar="FIELD", help="Count records grouped by FIELD")
    agg_ex.add_argument("--summarise", metavar="FIELD", help="Numeric summary of FIELD")

    return p


def run(args: argparse.Namespace) -> None:
    filters = parse_query(args.query)
    records = iter_sources(args.sources)
    matched = apply_filters(records, filters)

    # ---- aggregation modes --------------------------------------------------
    if args.count_by:
        result = count_by(matched, args.count_by)
        print(json.dumps(result, indent=2))
        return

    if args.summarise:
        result = summarise(matched, args.summarise)
        print(json.dumps(result, indent=2))
        return

    # ---- streaming output ---------------------------------------------------
    count = 0
    for record in matched:
        print(format_record(record, fmt=args.format))
        count += 1
        if args.limit and count >= args.limit:
            break


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run(args)
    except BrokenPipeError:
        sys.exit(0)
    except KeyboardInterrupt:
        sys.exit(130)
