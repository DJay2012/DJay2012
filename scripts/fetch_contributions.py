#!/usr/bin/env python3
"""Scrape the public contribution calendar -> data/contributions.json.

No token, no GraphQL. GitHub serves the same calendar fragment the profile
page uses at https://github.com/users/<username>/contributions
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import USERNAME  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "contributions.json"
URL = f"https://github.com/users/{USERNAME}/contributions"
HEADERS = {
    "User-Agent": "profile-art/1.0 (+https://github.com/%s)" % USERNAME,
    "Accept": "text/html",
    "X-Requested-With": "XMLHttpRequest",
}

_NUM = re.compile(r"([\d,]+)\s+contribution")


def fetch_html() -> str:
    r = requests.get(URL, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text


def count_from_text(text: str) -> int:
    """'No contributions on ...' -> 0 ; '12 contributions on ...' -> 12"""
    if not text:
        return 0
    low = text.strip().lower()
    if low.startswith("no contribution"):
        return 0
    m = _NUM.search(low)
    return int(m.group(1).replace(",", "")) if m else 0


def parse(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")

    # counts live in <tool-tip for="<cell id>">N contributions on ...</tool-tip>
    tips: dict[str, int] = {}
    for tip in soup.find_all("tool-tip"):
        target = tip.get("for")
        if target:
            tips[target] = count_from_text(tip.get_text())

    cells = soup.select("td.ContributionCalendar-day[data-date]")
    if not cells:  # markup drift fallback
        cells = soup.select("[data-date][data-level]")
    if not cells:
        raise SystemExit(
            "Could not find any day cells. GitHub's markup may have changed, "
            f"or the profile {USERNAME!r} has no public contributions."
        )

    days = []
    for c in cells:
        d = c.get("data-date")
        if not d:
            continue
        level = int(c.get("data-level") or 0)
        if c.get("data-count") is not None:
            count = int(c["data-count"])
        elif c.get("id") in tips:
            count = tips[c["id"]]
        else:
            count = count_from_text(c.get("aria-label") or c.get_text())
        days.append({"date": d, "count": count, "level": level})

    days.sort(key=lambda x: x["date"])
    # de-dupe (the fragment occasionally repeats an edge day)
    seen, unique = set(), []
    for day in days:
        if day["date"] not in seen:
            seen.add(day["date"])
            unique.append(day)
    return unique


def derive(days: list[dict]) -> dict:
    total = sum(d["count"] for d in days)

    by_month = defaultdict(int)
    for d in days:
        by_month[d["date"][:7]] += 1 * d["count"]

    best = max(days, key=lambda d: d["count"]) if days else {"date": "", "count": 0}

    # streaks (only count days up to today; future cells in the grid are 0)
    today = date.today()
    past = [d for d in days if datetime.strptime(d["date"], "%Y-%m-%d").date() <= today]

    longest = run = 0
    prev: date | None = None
    for d in past:
        cur = datetime.strptime(d["date"], "%Y-%m-%d").date()
        if d["count"] > 0:
            run = run + 1 if prev and cur - prev == timedelta(days=1) else 1
            longest = max(longest, run)
        else:
            run = 0
        prev = cur

    rev = list(reversed(past))
    if rev and rev[0]["count"] == 0:
        rev = rev[1:]  # an empty today doesn't break yesterday's streak
    current = 0
    for d in rev:
        if d["count"] == 0:
            break
        current += 1

    return {
        "total": total,
        "days_active": sum(1 for d in past if d["count"] > 0),
        "current_streak": current,
        "longest_streak": longest,
        "best_day": {"date": best["date"], "count": best["count"]},
        "by_month": dict(sorted(by_month.items())),
    }


def main() -> None:
    days = parse(fetch_html())
    payload = {
        "username": USERNAME,
        "generated_at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "range": {"start": days[0]["date"], "end": days[-1]["date"]},
        "stats": derive(days),
        "days": days,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=1) + "\n")
    print(
        f"wrote {OUT.relative_to(ROOT)} — {len(days)} days, "
        f"{payload['stats']['total']:,} contributions"
    )


if __name__ == "__main__":
    if os.environ.get("SAMPLE"):  # offline preview data
        import random

        random.seed(7)
        end = date.today()
        start = end - timedelta(days=364)
        start -= timedelta(days=(start.weekday() + 1) % 7)  # back to a Sunday
        days = []
        d = start
        while d <= end:
            n = 0 if random.random() < 0.28 else random.randint(1, 22)
            lvl = 0 if n == 0 else min(5, 1 + n // 5)
            days.append({"date": d.isoformat(), "count": n, "level": lvl})
            d += timedelta(days=1)
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(
            json.dumps(
                {
                    "username": USERNAME,
                    "generated_at": datetime.utcnow().isoformat() + "Z",
                    "range": {"start": days[0]["date"], "end": days[-1]["date"]},
                    "stats": derive(days),
                    "days": days,
                    "sample": True,
                },
                indent=1,
            )
            + "\n"
        )
        print(f"wrote SAMPLE data to {OUT.relative_to(ROOT)}")
    else:
        main()
