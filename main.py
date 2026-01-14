from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Response

from config import load_feeds, get_feed_by_token
from calendar_service import get_calendar_for_sources
from filters import filter_all_day_events

load_dotenv()

# Load feed configuration at startup
feeds = load_feeds()

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

@app.get("/")
def read_root():
    return {"status": "ok"}


@app.get("/{feed_name}/{token}.ics")
def get_feed_ics(feed_name: str, token: str):
    """
    Get a filtered calendar for a specific feed.

    URL format: /{feed_name}/{token}.ics
    Example: /work/abc123.ics
    """
    feed = get_feed_by_token(feeds, feed_name, token)

    if not feed:
        raise HTTPException(status_code=404, detail="Not found")

    calendar = get_calendar_for_sources(feed.sources)
    filtered_calendar = filter_all_day_events(calendar)

    return Response(content=filtered_calendar.to_ical(), media_type="text/calendar")
