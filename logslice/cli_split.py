"""CLI sub-command: split a JSONL file into per-bucket output files."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from logslice.reader import iter_sources
from logslice.splitter import split_by_value, split_by_query
from logslice.writer import write_lines


def build_split_parser(parent: "argparse._SubParsersAction | None" = None) -> argparse.ArgumentParser:
    kwargs = dict(
        description="Split a JSONL stream into separate files by field value or query."
    )
    if parent is not None:
        parser = parent.add_parser("split", **kwargs)
    else:
        parser = argparse.ArgumentParser(**kwargs)

    parser.add_argument("sources", nargs="*", default=["-"], help="Input files (default: stdin)")
    parser.add_argument("--field", "-f", help="Field whose value determines the bucket")
    parser.add_argument(
        "--query",
        "-q",
        nargs=2,
        metavar=("BUCKET", "QUERY"),
        action="append",
        dest="queries",
        help="Named query bucket (repeatable): --query errors 'level=error'",
    )
    parser.add_argument("--outdir", "-o", default=".", help="Directory for output files")
    parser.add_argument("--default", default=None, help="Catch-all bucket name (query mode)")
    parser.add_argument("--dry-run", action="store_true", help="Print bucket sizes without writing")
    return parser


def run_split(args: argparse.Namespace) -> None:
    records = list(iter_sources(args.sources))

    if args.queries:
        queries = {name: q for name, q in args.queries}
        buckets = split_by_query(records, queries, default_bucket=args.default)
    elif args.field:
        buckets = split_by_value(records, args.field)
    else:
        print("error: provide --field or at least one --query", file=sys.stderr)
        sys.exit(1)

    outdir = Path(args.outdir)

    for bucket_name, recs in sorted(buckets.items()):
        lines = [json.dumps(r) for r in recs]
        if args.dry_run:
            print(f"{bucket_name}: {len(lines)} record(s)")
        else:
            dest = outdir / f"{bucket_name}.jsonl"
            count = write_lines(dest, lines)
            print(f"wrote {count} record(s) -> {dest}")


def main() -> None:  # pragma: no cover
    parser = build_split_parser()
    run_split(parser.parse_args())


if __name__ == "__main__":  # pragma: no cover
    main()
