from datetime import date, datetime, timedelta

import icalendar


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

        items_to_keep.append(item)

    calendar.subcomponents = items_to_keep
    return calendar
