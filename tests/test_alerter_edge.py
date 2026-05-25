"""Edge-case tests for logslice.alerter."""

from logslice.alerter import Alert, make_alert, collect_alerts, watch_alerts


def test_alert_with_no_filters_matches_all_records():
    alert = make_alert("all", "", threshold=2)
    recs = [{"a": 1}, {"b": 2}, {"c": 3}]
    _, fired = collect_alerts(recs, [alert])
    # threshold=2 fires at record 2 and again at record 4 (but only 3 records)
    assert len(fired) == 1


def test_collect_alerts_empty_stream():
    alert = make_alert("err", "level=error", threshold=1)
    all_recs, fired = collect_alerts([], [alert])
    assert all_recs == []
    assert fired == []


def test_collect_alerts_no_alerts():
    recs = [{"level": "error"}]
    all_recs, fired = collect_alerts(recs, [])
    assert all_recs == [{"level": "error"}]
    assert fired == []


def test_alert_threshold_one_fires_every_match():
    alert = make_alert("w", "level=warn", threshold=1)
    recs = [{"level": "warn"}, {"level": "warn"}, {"level": "warn"}]
    _, fired = collect_alerts(recs, [alert])
    assert len(fired) == 3


def test_watch_alerts_is_lazy_generator():
    """watch_alerts should return an iterator, not consume eagerly."""
    import types
    alert = make_alert("x", "level=error", threshold=1)
    result = watch_alerts(iter([{"level": "info"}]), [alert], lambda a, r: None)
    assert isinstance(result, types.GeneratorType)


def test_alert_count_accumulates_across_non_triggering_calls():
    alert = make_alert("e", "level=error", threshold=3)
    alert.check({"level": "error"})
    alert.check({"level": "info"})   # does not increment
    alert.check({"level": "error"})
    assert alert.count == 2
    assert not alert.check({"level": "info"})  # still 2, no fire
    assert alert.check({"level": "error"})     # hits 3, fires
