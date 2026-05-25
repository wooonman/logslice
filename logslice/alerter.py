"""Alert when log records match a condition a threshold number of times."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable, Iterator

from logslice.query import Filter, apply_filters, parse_query


@dataclass
class Alert:
    name: str
    filters: list[Filter]
    threshold: int = 1
    window: int = 0  # 0 means no windowing, just a running count
    _count: int = field(default=0, init=False, repr=False)

    def check(self, record: dict) -> bool:
        """Return True if this record triggers the alert."""
        if apply_filters(record, self.filters):
            self._count += 1
        return self._count >= self.threshold

    def reset(self) -> None:
        self._count = 0

    @property
    def count(self) -> int:
        return self._count


def make_alert(name: str, query: str, threshold: int = 1) -> Alert:
    """Build an Alert from a query string."""
    filters = parse_query(query) if query else []
    return Alert(name=name, filters=filters, threshold=threshold)


def watch_alerts(
    records: Iterable[dict],
    alerts: list[Alert],
    on_alert: Callable[[Alert, dict], None],
) -> Iterator[dict]:
    """Pass records through, calling on_alert whenever an alert fires.

    Each record is yielded regardless of whether it triggered an alert.
    on_alert is called with the alert and the triggering record.
    """
    for record in records:
        for alert in alerts:
            if alert.check(record):
                on_alert(alert, record)
                alert.reset()
        yield record


def collect_alerts(
    records: Iterable[dict],
    alerts: list[Alert],
) -> tuple[list[dict], list[tuple[str, dict]]]:
    """Consume records and return (all_records, fired_events).

    fired_events is a list of (alert_name, record) pairs.
    """
    fired: list[tuple[str, dict]] = []

    def _on_alert(alert: Alert, record: dict) -> None:
        fired.append((alert.name, record))

    all_records = list(watch_alerts(records, alerts, _on_alert))
    return all_records, fired
