#!/usr/bin/env python3
"""Public, unauthenticated Volnorez broadcast snapshot -> data/onair.json.
Do not put any account credentials, cookies or tokens in this script.
"""
import json
from pathlib import Path
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

URL = "https://volnorez.com/pyl_dorog-fm?lang=ru"
OUT = Path("data/onair.json")


def extract(html):
    doc = BeautifulSoup(html, "html.parser")
    topic_el = doc.select_one("#desktop_single .channel_BroadcastTheme")
    host_el = doc.select_one("#desktop_single .channel_OnAirList")
    track_el = doc.select_one("#desktop_single .channel_MediaOnAir.active .channel_MediaOnAirText")
    def cleaned(el):
        if not el: return ""
        return " ".join(el.stripped_strings)[:200]
    return {"host": cleaned(host_el), "topic": cleaned(topic_el), "track": cleaned(track_el)}


def main():
    req = Request(URL, headers={"User-Agent": "Mozilla/5.0 (compatible; PylDorogFM-public-metadata/1.0)", "Accept-Language": "ru"})
    with urlopen(req, timeout=18) as r:
        html = r.read(3_000_000).decode("utf-8", errors="replace")
    if 'id="desktop_single"' not in html:
        raise RuntimeError("Не найдена страница радиостанции: данные не обновлены")
    result = extract(html)
    # Publish only public broadcast fields; never store scraped HTML or session information.
    result["updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Информация об эфире обновлена:", {k:v for k,v in result.items() if k!="updated_at"})

if __name__ == "__main__":
    main()
