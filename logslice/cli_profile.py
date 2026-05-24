"""CLI sub-command: profile — show field statistics for a log stream."""

from __future__ import annotations

import json
import sys
from argparse import ArgumentParser, Namespace
from typing import List

from logslice.profiler import profile_all
from logslice.reader import iter_sources


def build_profile_parser(sub) -> ArgumentParser:  # type: ignore[type-arg]
    p = sub.add_parser(
        "profile",
        help="Compute field statistics over a log stream.",
    )
    p.add_argument(
        "sources",
        nargs="*",
        default=["-"],
        metavar="FILE",
        help="Log files to read (default: stdin).",
    )
    p.add_argument(
        "--fields",
        nargs="+",
        metavar="FIELD",
        default=None,
        help="Specific fields to profile (default: all).",
    )
    p.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="Emit results as JSON lines instead of human-readable text.",
    )
    return p


def run_profile(args: Namespace) -> None:
    records = list(iter_sources(args.sources))
    results = profile_all(records, fields=args.fields)

    for stat in results:
        if args.as_json:
            sys.stdout.write(json.dumps(stat) + "\n")
        else:
            _print_stat(stat)


def _print_stat(stat: dict) -> None:
    field = stat["field"]
    print(f"\n── {field} ──")
    print(f"  present : {stat['present']} / {stat['total']}")
    print(f"  missing : {stat['missing']}")
    print(f"  types   : {stat['types']}")
    print(f"  top     : {stat['top_values']}")
    if "numeric" in stat:
        n = stat["numeric"]
        print(
            f"  numeric : min={n['min']}  max={n['max']}  "
            f"mean={n['mean']}  stddev={n['stddev']}  median={n['median']}"
        )
