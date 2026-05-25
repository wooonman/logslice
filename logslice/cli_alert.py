"""CLI entry point for the alert sub-command."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence

from logslice.alerter import make_alert, watch_alerts
from logslice.reader import iter_sources


def build_alert_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # noqa: SLF001
    kwargs = dict(
        description="Stream logs and print a message whenever an alert threshold is reached."
    )
    if parent is not None:
        parser = parent.add_parser("alert", **kwargs)
    else:
        parser = argparse.ArgumentParser(prog="logslice alert", **kwargs)

    parser.add_argument("sources", nargs="*", default=["-"], help="Log files (default: stdin)")
    parser.add_argument("-a", "--alert", action="append", dest="alerts", default=[],
                        metavar="NAME:QUERY:THRESHOLD",
                        help="Alert spec: name:query:threshold (threshold optional, default 1)")
    parser.add_argument("--passthrough", action="store_true",
                        help="Also print every log record to stdout")
    return parser


def _parse_alert_spec(spec: str):
    """Parse 'name:query:threshold' or 'name:query'."""
    parts = spec.split(":", 2)
    if len(parts) < 2:
        raise ValueError(f"Invalid alert spec (need name:query[:threshold]): {spec!r}")
    name = parts[0]
    query = parts[1]
    threshold = int(parts[2]) if len(parts) == 3 else 1
    return make_alert(name, query, threshold)


def run_alert(args: argparse.Namespace, out=sys.stdout, err=sys.stderr) -> int:
    try:
        alerts = [_parse_alert_spec(s) for s in args.alerts]
    except ValueError as exc:
        print(f"error: {exc}", file=err)
        return 1

    if not alerts:
        print("error: at least one --alert spec is required", file=err)
        return 1

    records = iter_sources(args.sources)

    def _on_alert(alert, record):
        msg = json.dumps({"alert": alert.name, "count": alert.count, "record": record})
        print(msg, file=out)

    for record in watch_alerts(records, alerts, _on_alert):
        if args.passthrough:
            print(json.dumps(record), file=out)

    return 0


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_alert_parser()
    args = parser.parse_args(argv)
    sys.exit(run_alert(args))


if __name__ == "__main__":
    main()
