#!/usr/bin/env python3
"""Collect mechanical engineering postings around Lexington / Georgetown, KY.

LinkedIn guest search endpoint, no auth. One location query saturates at
roughly 40 cards, so the same location is looped over keyword buckets and
start=0/10/20, then deduped by job id and filtered against a city whitelist
(the endpoint ignores distance=25 and returns towns two hours away).

Output: jobs.json in the project root, one object per posting:
  {title, company, date, url, id, location, posted}
"""
import html
import json
import re
import time
import urllib.parse
import urllib.request

UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0 Safari/537.36"
)

LOCATIONS = [
    "Lexington, KY, United States",
    "Georgetown, KY, United States",
]

KEYWORDS = [
    "mechanical engineer",
    "mechanical design engineer",
    "mechanical engineering",
    "design engineer",
    "manufacturing engineer",
    "product engineer",
    "project engineer",
    "process engineer",
    "tooling engineer",
    "hvac engineer",
    "thermal engineer",
    "test engineer",
    "quality engineer",
    "applications engineer",
    "reliability engineer",
    "packaging engineer",
    "automation engineer",
    "plant engineer",
    "solidworks",
    "cad designer",
    "mechanical engineer entry level",
    "mechanical engineering internship",
]

STARTS = [0, 10, 20]

# ~45 minutes of Lexington: the Bluegrass counties plus Frankfort and the
# I-75 / I-64 towns that show up in the same commute.
CITIES = [
    "lexington", "georgetown", "nicholasville", "versailles", "frankfort",
    "winchester", "paris", "richmond", "wilmore", "midway", "lawrenceburg",
    "mount sterling", "mt sterling", "berea", "danville", "cynthiana",
    "harrodsburg", "stanford", "shelbyville", "stamping ground", "sadieville",
    "north middletown", "jeffersonville", "clays ferry", "keene",
]

TOKEN = "urn:li:jobPosting:"
CARD_HREF = re.compile(r'class="base-card__full-link[^"]*"\s+href="([^"]+)"')
CARD_TITLE = re.compile(r'class="sr-only"[^>]*>\s*(.*?)\s*</span>', re.S)
CARD_COMPANY = re.compile(r'class="base-search-card__subtitle"[^>]*>\s*(?:<a[^>]*>)?\s*(.*?)\s*</(?:a|h4)>', re.S)
CARD_LOCATION = re.compile(r'class="job-search-card__location"[^>]*>\s*(.*?)\s*</span>', re.S)
CARD_DATE = re.compile(r'<time[^>]*datetime="([^"]+)"', re.S)


def fetch(url, tries=4):
    last = None
    for attempt in range(tries):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as exc:  # 429 in bursts, gateway hiccups
            last = exc
            time.sleep(3 + attempt * 3)
    print(f"  ! gave up on {url[:110]}: {last}")
    return ""


def clean(text):
    text = re.sub(r"<[^>]+>", " ", text)
    return html.unescape(re.sub(r"\s+", " ", text)).strip()


def parse_cards(body):
    cards = []
    for chunk in body.split(f"{TOKEN}")[1:]:
        job_id = re.match(r"(\d+)", chunk)
        if not job_id:
            continue
        title = CARD_TITLE.search(chunk)
        company = CARD_COMPANY.search(chunk)
        location = CARD_LOCATION.search(chunk)
        date = CARD_DATE.search(chunk)
        href = CARD_HREF.search(chunk)
        if not (title and company and location):
            continue
        cards.append(
            {
                "id": job_id.group(1),
                "title": clean(title.group(1)),
                "company": clean(company.group(1)),
                "location": clean(location.group(1)),
                "date": date.group(1) if date else "",
                "url": html.unescape(href.group(1)) if href else "",
            }
        )
    return cards


def city_of(location):
    """First whitelisted town in the location string, city-cased for display."""
    low = location.lower()
    for city in CITIES:
        if city in low:
            return city.title().replace("Mt Sterling", "Mt. Sterling")
    return None


def main():
    seen = {}
    for location in LOCATIONS:
        for kw in KEYWORDS:
            for start in STARTS:
                q = urllib.parse.urlencode(
                    {"keywords": kw, "location": location, "start": start}
                )
                url = (
                    "https://www.linkedin.com/jobs-guest/jobs/api/"
                    f"seeMoreJobPostings/search?{q}"
                )
                body = fetch(url)
                cards = parse_cards(body)
                print(f"{location.split(',')[0]:12} {kw:34} {start:>3} -> {len(cards)}")
                for card in cards:
                    seen.setdefault(card["id"], card)
                if not cards:
                    time.sleep(2)
                else:
                    time.sleep(1.1)

    kept, dropped = [], {}
    for card in seen.values():
        town = city_of(card["location"])
        if not town:
            dropped[card["location"]] = dropped.get(card["location"], 0) + 1
            continue
        card["location"] = town
        card["posted"] = card["date"]
        kept.append(card)

    kept.sort(key=lambda c: (c["date"], c["title"]), reverse=True)
    with open("jobs.json", "w") as fh:
        json.dump(kept, fh, indent=1)
        fh.write("\n")

    print(f"\n{len(seen)} unique postings, {len(kept)} in the whitelist")
    print("dropped by location:")
    for loc, n in sorted(dropped.items(), key=lambda kv: -kv[1]):
        print(f"  {n:3}  {loc}")


if __name__ == "__main__":
    main()
