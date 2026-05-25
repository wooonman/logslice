"""Tests for logslice.alerter."""

import pytest

from logslice.alerter import Alert, make_alert, watch_alerts, collect_alerts
from logslice.query import parse_query


def _records(*levels):
    return [{"level": lvl, "msg": f"msg-{lvl}"} for lvl in levels]


# --- Alert.check ---

def test_alert_check_increments_count():
    alert = make_alert("err", "level=error", threshold=3)
    alert.check({"level": "error"})
    assert alert.count == 1


def test_alert_check_non_matching_does_not_increment():
    alert = make_alert("err", "level=error", threshold=3)
    alert.check({"level": "info"})
    assert alert.count == 0


def test_alert_fires_at_threshold():
    alert = make_alert("err", "level=error", threshold=2)
    assert not alert.check({"level": "error"})
    assert alert.check({"level": "error"})


def test_alert_reset_clears_count():
    alert = make_alert("err", "level=error", threshold=1)
    alert.check({"level": "error"})
    alert.reset()
    assert alert.count == 0


# --- make_alert ---

def test_make_alert_empty_query_matches_everything():
    alert = make_alert("any", "", threshold=1)
    assert alert.check({"level": "info"})


def test_make_alert_sets_name_and_threshold():
    alert = make_alert("my-alert", "level=warn", threshold=5)
    assert alert.name == "my-alert"
    assert alert.threshold == 5


# --- watch_alerts ---

def test_watch_alerts_yields_all_records():
    recs = _records("info", "error", "info")
    alert = make_alert("err", "level=error", threshold=1)
    fired = []
    result = list(watch_alerts(recs, [alert], lambda a, r: fired.append(a.name)))
    assert len(result) == 3


def test_watch_alerts_fires_callback_on_match():
    recs = _records("error", "info", "error")
    alert = make_alert("err", "level=error", threshold=1)
    fired = []
    list(watch_alerts(recs, [alert], lambda a, r: fired.append(r["level"])))
    assert fired == ["error", "error"]


def test_watch_alerts_threshold_two():
    recs = _records("error", "error", "error", "error")
    alert = make_alert("err", "level=error", threshold=2)
    fired = []
    list(watch_alerts(recs, [alert], lambda a, r: fired.append(True)))
    assert len(fired) == 2


def test_watch_alerts_multiple_alerts():
    recs = _records("error", "warn", "error")
    a1 = make_alert("errors", "level=error", threshold=1)
    a2 = make_alert("warns", "level=warn", threshold=1)
    fired_names = []
    list(watch_alerts(recs, [a1, a2], lambda a, r: fired_names.append(a.name)))
    assert "errors" in fired_names
    assert "warns" in fired_names


# --- collect_alerts ---

def test_collect_alerts_returns_all_records():
    recs = _records("info", "error")
    alert = make_alert("err", "level=error", threshold=1)
    all_recs, fired = collect_alerts(recs, [alert])
    assert len(all_recs) == 2


def test_collect_alerts_fired_contains_name_and_record():
    recs = _records("error")
    alert = make_alert("err", "level=error", threshold=1)
    _, fired = collect_alerts(recs, [alert])
    assert len(fired) == 1
    name, rec = fired[0]
    assert name == "err"
    assert rec["level"] == "error"


def test_collect_alerts_no_match_empty_fired():
    recs = _records("info", "debug")
    alert = make_alert("err", "level=error", threshold=1)
    _, fired = collect_alerts(recs, [alert])
    assert fired == []
