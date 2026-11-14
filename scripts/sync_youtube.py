#!/usr/bin/env python3
"""Merge the channel's latest videos (public RSS feed) into _data/videos.json."""
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

CHANNEL_ID = "UC4lh3MxdiOPFiP3Pa3oTctQ"
FEED = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
OUT = Path(__file__).resolve().parent.parent / "_data" / "videos.json"
NS = {
    "a": "http://www.w3.org/2005/Atom",
    "yt": "http://www.youtube.com/xml/schemas/2015",
    "media": "http://search.yahoo.com/mrss/",
}
UA = {"User-Agent": "Mozilla/5.0 (site-video-sync)"}


def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return r.read()


def is_short(video_id, link):
    if "/shorts/" in link:
        return True
    # /shorts/<id> answers 200 for a Short and redirects for a regular video
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k):
            return None
    try:
        opener = urllib.request.build_opener(NoRedirect)
        req = urllib.request.Request(f"https://www.youtube.com/shorts/{video_id}", headers=UA, method="HEAD")
        return opener.open(req, timeout=15).status == 200
    except Exception:
        return False


def clean_title(title):
    title = re.sub(r"\s*#\S+", "", title)
    return re.sub(r"\s{2,}", " ", title).strip()


def main():
    existing = json.loads(OUT.read_text()) if OUT.exists() else []
    by_id = {v["id"]: v for v in existing}
    try:
        root = ET.fromstring(fetch(FEED))
    except Exception as e:
        print(f"feed fetch failed, keeping existing data: {e}")
        return 0

    entries = root.findall("a:entry", NS)
    if not entries:
        print("feed returned no videos, keeping existing data")
        return 0

    for e in entries:
        vid = e.find("yt:videoId", NS).text
        link = e.find("a:link", NS).get("href", "")
        raw = e.find("a:title", NS).text or ""
        prev = by_id.get(vid, {})
        by_id[vid] = {
            "id": vid,
            "title": clean_title(raw) or raw,
            "published": e.find("a:published", NS).text,
            "short": prev["short"] if "short" in prev else is_short(vid, link),
        }

    videos = sorted(by_id.values(), key=lambda v: v["published"], reverse=True)
    if videos != existing:
        OUT.parent.mkdir(exist_ok=True)
        OUT.write_text(json.dumps(videos, indent=2, ensure_ascii=False) + "\n")
        print(f"updated {OUT.name}: {len(videos)} videos")
    else:
        print("no changes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
