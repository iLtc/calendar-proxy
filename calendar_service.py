import icalendar
import requests
import requests_cache

# Cache calendar fetches for 5 minutes
requests_cache.install_cache('calendar_cache', expire_after=300)


def fetch_calendar(url: str) -> icalendar.Calendar:
    """
    Fetch a calendar from a URL.

    Args:
        url: The URL of the ICS file

    Returns:
        Parsed calendar object
    """
    response = requests.get(url)
    response.raise_for_status()
    return icalendar.Calendar.from_ical(response.text)


def merge_calendars(calendars: list[icalendar.Calendar]) -> icalendar.Calendar:
    """
    Merge multiple calendars into one.

    Uses the first calendar as the base and appends components from the rest.

    Args:
        calendars: List of calendars to merge

    Returns:
        A single merged calendar
    """
    if not calendars:
        raise ValueError("At least one calendar is required")

    if len(calendars) == 1:
        return calendars[0]

    # Use first calendar as base, append components from the rest
    base = calendars[0]
    for cal in calendars[1:]:
        base.subcomponents.extend(cal.subcomponents)

    return base


def get_calendar_for_sources(sources: list[str]) -> icalendar.Calendar:
    """
    Fetch and merge calendars from multiple sources.

    Args:
        sources: List of calendar URLs

    Returns:
        Merged calendar (or single calendar if only one source)
    """
    calendars = [fetch_calendar(url) for url in sources]
    return merge_calendars(calendars)
