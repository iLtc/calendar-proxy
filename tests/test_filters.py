import icalendar

from filters import filter_all_day_events, version_event_uids

DURATION_ICS = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//test//EN
BEGIN:VEVENT
UID:long-event
DTSTART:20260101T090000Z
DURATION:P3D
SUMMARY:Long event
END:VEVENT
BEGIN:VEVENT
UID:short-event
DTSTART:20260101T090000Z
DURATION:PT1H
SUMMARY:Short event
END:VEVENT
END:VCALENDAR
"""


def test_filters_events_24h_or_longer_expressed_via_duration():
    calendar = icalendar.Calendar.from_ical(DURATION_ICS)

    filtered = filter_all_day_events(calendar)

    summaries = [
        str(item.get("SUMMARY"))
        for item in filtered.subcomponents
        if item.name == "VEVENT"
    ]
    assert summaries == ["Short event"]


def _event_ics(uid, dtstart, dtend):
    return f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//test//EN
BEGIN:VEVENT
UID:{uid}
DTSTART:{dtstart}
DTEND:{dtend}
SUMMARY:Busy
END:VEVENT
END:VCALENDAR
"""


def _uids(calendar):
    return [str(item.get("UID")) for item in calendar.walk("VEVENT")]


def test_event_uid_is_stable_when_times_unchanged():
    first = version_event_uids(icalendar.Calendar.from_ical(
        _event_ics("abc", "20261008T163000Z", "20261008T170000Z")))
    second = version_event_uids(icalendar.Calendar.from_ical(
        _event_ics("abc", "20261008T163000Z", "20261008T170000Z")))

    assert _uids(first) == _uids(second)
    assert _uids(first) != ["abc"]


def test_event_uid_changes_when_event_is_moved():
    before = version_event_uids(icalendar.Calendar.from_ical(
        _event_ics("abc", "20261007T163000Z", "20261007T170000Z")))
    after = version_event_uids(icalendar.Calendar.from_ical(
        _event_ics("abc", "20261008T163000Z", "20261008T170000Z")))

    assert _uids(before) != _uids(after)


def test_event_uid_changes_when_end_time_changes():
    before = version_event_uids(icalendar.Calendar.from_ical(
        _event_ics("abc", "20261008T163000Z", "20261008T170000Z")))
    after = version_event_uids(icalendar.Calendar.from_ical(
        _event_ics("abc", "20261008T163000Z", "20261008T173000Z")))

    assert _uids(before) != _uids(after)


def test_event_uid_ignores_timezone_representation():
    # Same instant expressed in UTC and in a local timezone
    utc = version_event_uids(icalendar.Calendar.from_ical(
        _event_ics("abc", "20261008T163000Z", "20261008T170000Z")))
    local = version_event_uids(icalendar.Calendar.from_ical(
        _event_ics("abc", "20261008T093000", "20261008T100000")
        .replace("DTSTART:", "DTSTART;TZID=America/Los_Angeles:")
        .replace("DTEND:", "DTEND;TZID=America/Los_Angeles:")))

    assert _uids(utc) == _uids(local)


def test_different_events_at_same_time_get_different_uids():
    first = version_event_uids(icalendar.Calendar.from_ical(
        _event_ics("abc", "20261008T163000Z", "20261008T170000Z")))
    second = version_event_uids(icalendar.Calendar.from_ical(
        _event_ics("xyz", "20261008T163000Z", "20261008T170000Z")))

    assert _uids(first) != _uids(second)
