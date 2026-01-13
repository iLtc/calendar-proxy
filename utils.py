import os
from datetime import date, datetime, timedelta

import icalendar
import requests
import requests_cache

requests_cache.install_cache('calendar_cache', expire_after=900)

def get_tokens() -> list[str]:
    results = []
    i = 0

    while True:
        token_name = f"TOKEN_{i}"
        token = os.getenv(token_name)

        if not token:
            break

        results.append(token)
        i += 1

    return results

def get_calendar() -> icalendar.Calendar:
    calendar_url = os.getenv("CALENDAR_URL")

    response = requests.get(calendar_url)
    response.raise_for_status()

    calendar = icalendar.Calendar.from_ical(response.text)

    return calendar

def filter_events(calendar: icalendar.Calendar) -> icalendar.Calendar:
    items_to_keep = []

    for item in calendar.subcomponents:
        if item.name != "VEVENT":
            items_to_keep.append(item)
            continue

        dtstart = item.get("DTSTART")

        if dtstart and isinstance(dtstart.dt, date) and not isinstance(dtstart.dt, datetime):
            # this is an all day event, skip it
            continue

        dtend = item.get("DTEND")
        event_duration = None

        if dtstart and dtend:
            if isinstance(dtstart.dt, datetime) and isinstance(dtend.dt, datetime):
                event_duration = dtend.dt - dtstart.dt
            elif isinstance(dtstart.dt, date) and isinstance(dtend.dt, date):
                event_duration = dtend.dt - dtstart.dt

        if event_duration and event_duration >= timedelta(days=1):
            # event is longer than 24 hours, skip it
            continue

        items_to_keep.append(item)

    calendar.subcomponents = items_to_keep

    return calendar
