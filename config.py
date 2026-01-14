import os
from dataclasses import dataclass


@dataclass
class Feed:
    """Represents a calendar feed configuration."""
    name: str
    sources: list[str]
    tokens: set[str]


def _load_numbered_env(prefix: str) -> list[str]:
    """Load numbered environment variables (e.g., PREFIX_0, PREFIX_1, ...)."""
    results = []
    j = 0
    while True:
        value = os.getenv(f"{prefix}_{j}")
        if not value:
            break
        results.append(value.strip())
        j += 1
    return results


def load_feeds() -> dict[str, Feed]:
    """
    Load feed configurations from environment variables.

    Expected format:
        FEED_0_NAME=work
        FEED_0_SOURCE_0=https://calendar.example.com/work.ics
        FEED_0_TOKEN_0=abc123
        FEED_0_TOKEN_1=def456

        FEED_1_NAME=personal
        FEED_1_SOURCE_0=https://cal1.ics
        FEED_1_SOURCE_1=https://cal2.ics
        FEED_1_SOURCE_2=https://cal3.ics
        FEED_1_TOKEN_0=xyz789

    Returns:
        dict mapping feed name to Feed object
    """
    feeds: dict[str, Feed] = {}
    i = 0

    while True:
        name = os.getenv(f"FEED_{i}_NAME")

        # Stop when we hit a gap in the numbering
        if not name:
            break

        sources = _load_numbered_env(f"FEED_{i}_SOURCE")
        tokens = _load_numbered_env(f"FEED_{i}_TOKEN")

        if not sources:
            raise ValueError(f"FEED_{i}_SOURCE_0 is required when FEED_{i}_NAME is set")

        if not tokens:
            raise ValueError(f"FEED_{i}_TOKEN_0 is required when FEED_{i}_NAME is set")

        if name in feeds:
            raise ValueError(f"Duplicate feed name: {name}")

        feeds[name] = Feed(name=name, sources=sources, tokens=set(tokens))
        i += 1

    return feeds


def get_feed_by_token(feeds: dict[str, Feed], feed_name: str, token: str) -> Feed | None:
    """
    Look up a feed by name and validate the token.

    Returns the Feed if found and token is valid, None otherwise.
    """
    feed = feeds.get(feed_name)
    if feed and token in feed.tokens:
        return feed
    return None
