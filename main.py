from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Response

from utils import get_tokens, get_calendar, filter_events

load_dotenv()

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

@app.get("/")
def read_root():
    return {"status": "ok"}

@app.get("/{token}.ics")
def get_ics(token: str):
    if token not in get_tokens():
        raise HTTPException(status_code=404, detail="Not found")

    calendar = get_calendar()
    filtered_calendar = filter_events(calendar)

    return Response(content=filtered_calendar.to_ical(), media_type="text/calendar")
