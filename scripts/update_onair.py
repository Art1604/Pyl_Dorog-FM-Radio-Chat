#!/usr/bin/env python3
"""Fetch public on-air metadata without replacing good data on failure."""

import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

URL = "https://volnorez.com/pyl_dorog-fm?lang=ru"
OUT = Path("data/onair.json")


def extract(html):
    doc = BeautifulSoup(html, "html.parser")

    def cleaned(selector):
        item = doc.select_one(selector)
        return " ".join(item.stripped_strings)[:200] if item else ""

    return {
        "host": cleaned("#desktop_single .channel_OnAirList"),
        "topic": cleaned("#desktop_single .channel_BroadcastTheme"),
        "track": cleaned(
            "#desktop_single .channel_MediaOnAir.active .channel_MediaOnAirText"
        ),
    }


def main():
    print("Fetching public radio information...", flush=True)
    req = Request(
        URL,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; PylDorogFM-public-metadata/1.0)",
            "Accept-Language": "ru",
        },
    )
    with urlopen(req, timeout=30) as response:
        html = response.read(3_000_000).decode("utf-8", errors="replace")

    result = extract(html)
    if not any(result.values()):
        raise RuntimeError("No on-air metadata found; keeping previous data")

    result["updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Metadata updated.")


if __name__ == "__main__":
    main()
