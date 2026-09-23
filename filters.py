from datetime import date, datetime, timedelta, timezone

import icalendar
import recurring_ical_events

# Only return events within this window around the current time
PAST_WINDOW = timedelta(days=1)
FUTURE_WINDOW = timedelta(days=28)


def filter_time_window(calendar: icalendar.Calendar) -> icalendar.Calendar:
    """
    Keep only events occurring within the time window around now.

    Recurring events are expanded into individual occurrences, each returned
    as a standalone event with its own UID.

    Args:
        calendar: The calendar to filter

    Returns:
        The calendar with events outside the window removed
    """
    # UIDs belonging to recurring series (including their modified instances)
    series_uids = {
        str(item.get("UID"))
        for item in calendar.walk("VEVENT")
        if "RRULE" in item or "RDATE" in item or "RECURRENCE-ID" in item
    }

    now = datetime.now(timezone.utc)
    occurrences = recurring_ical_events.of(calendar).between(now - PAST_WINDOW, now + FUTURE_WINDOW)

    events = []
    for event in occurrences:
        recurrence_id = event.pop("RECURRENCE-ID", None)
        uid = str(event.get("UID"))
        if uid in series_uids and recurrence_id is not None:
            # Give each occurrence a stable, unique UID so clients don't treat
            # it as an exception to a series that is no longer present
            event["UID"] = f"{uid}-{recurrence_id.to_ical().decode()}"
        events.append(event)

    others = [item for item in calendar.subcomponents if item.name != "VEVENT"]
    calendar.subcomponents = others + events
    return calendar


def filter_all_day_events(calendar: icalendar.Calendar) -> icalendar.Calendar:
    """
    Filter out all-day events and events lasting 24 hours or more.

    Args:
        calendar: The calendar to filter

    Returns:
        A new calendar with all-day events removed
    """
    items_to_keep = []

    for item in calendar.subcomponents:
        if item.name != "VEVENT":
            items_to_keep.append(item)
            continue

        dtstart = item.get("DTSTART")

        # Check if this is an all-day event (date without time)
        if dtstart and isinstance(dtstart.dt, date) and not isinstance(dtstart.dt, datetime):
            continue

        # Check if event duration is >= 24 hours
        dtend = item.get("DTEND")
        if dtstart and dtend:
            try:
                if isinstance(dtstart.dt, datetime) and isinstance(dtend.dt, datetime):
                    event_duration = dtend.dt - dtstart.dt
                elif isinstance(dtstart.dt, date) and isinstance(dtend.dt, date):
                    event_duration = dtend.dt - dtstart.dt
                else:
                    event_duration = None

                if event_duration and event_duration >= timedelta(days=1):
                    continue
            except TypeError:
                # If we can't compute duration, keep the event
                pass

        # Events may specify DURATION instead of DTEND
        duration = item.get("DURATION")
        if dtstart and not dtend and duration is not None:
            if isinstance(duration.dt, timedelta) and duration.dt >= timedelta(days=1):
                continue

        items_to_keep.append(item)

    calendar.subcomponents = items_to_keep
    return calendar
