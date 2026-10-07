import os

import requests_cache

# Feed config must be in place before main.py loads feeds at import time.
# Port 1 on localhost refuses connections immediately.
os.environ["FEED_0_NAME"] = "test"
os.environ["FEED_0_SOURCE_0"] = "http://127.0.0.1:1/down.ics"
os.environ["FEED_0_TOKEN_0"] = "tok"

from fastapi.testclient import TestClient

import main

client = TestClient(main.app, raise_server_exceptions=False)


def test_returns_502_when_upstream_down_and_cache_cold():
    requests_cache.get_cache().clear()

    response = client.get("/test/tok.ics")

    assert response.status_code == 502
