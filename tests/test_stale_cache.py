import threading
from datetime import timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest
import requests_cache

import calendar_service

STALE_ICS = (
    "BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//stale-test//EN\r\nEND:VCALENDAR\r\n"
)


class FlakyICSHandler(BaseHTTPRequestHandler):
    fail = False

    def do_GET(self):
        if FlakyICSHandler.fail:
            self.send_response(500)
            self.end_headers()
            return
        body = STALE_ICS.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/calendar")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass


@pytest.fixture
def ics_server():
    FlakyICSHandler.fail = False
    server = ThreadingHTTPServer(("127.0.0.1", 0), FlakyICSHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    requests_cache.get_cache().clear()
    yield f"http://127.0.0.1:{server.server_address[1]}/cal.ics"
    server.shutdown()
    requests_cache.get_cache().clear()


def test_serves_stale_cache_when_upstream_fails(ics_server):
    # Prime the cache while the upstream is healthy
    calendar = calendar_service.fetch_calendar(ics_server)
    assert calendar["PRODID"] == "-//stale-test//EN"

    # Upstream goes down and the cached entry expires
    FlakyICSHandler.fail = True
    requests_cache.get_cache().reset_expiration(timedelta(seconds=-1))

    # The last good copy should still be served
    calendar = calendar_service.fetch_calendar(ics_server)
    assert calendar["PRODID"] == "-//stale-test//EN"
