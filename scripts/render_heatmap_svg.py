#!/usr/bin/env python3
"""data/contributions.json -> contrib-heatmap.svg (animated, self-contained).

The reveal is a diagonal wave of CSS keyframes that plays once on load and
freezes (animation-fill-mode: forwards). No <script>, no external CSS —
GitHub strips both but happily plays keyframes inside an <img>-embedded SVG.

Set STATIC=1 to emit a frozen frame (handy for local previews).
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import ACCENT, BG, BORDER, DIM, FG, PALETTE, USERNAME  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "contributions.json"
OUT = ROOT / "contrib-heatmap.svg"

STATIC = os.environ.get("STATIC") == "1"

# ------------------------------------------------------------------ layout
CELL = 11          # box size
GAP = 3            # gap between boxes
PITCH = CELL + GAP
PAD_X = 18
PAD_TOP = 44       # title bar + month labels
LABEL_W = 26       # left day labels
FOOTER_H = 46
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DAY_LABELS = {1: "Mon", 3: "Wed", 5: "Fri"}
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"


def load() -> dict:
    if not SRC.exists():
        raise SystemExit(f"missing {SRC} — run fetch_contributions.py first")
    return json.loads(SRC.read_text())


def to_weeks(days: list[dict]) -> list[list[dict | None]]:
    """Bucket days into columns of 7, Sunday-first, padding the first column."""
    weeks: list[list[dict | None]] = []
    col: list[dict | None] = []
    first_dow = datetime.strptime(days[0]["date"], "%Y-%m-%d").weekday()
    col.extend([None] * ((first_dow + 1) % 7))  # Mon=0 -> Sun-first index
    for d in days:
        col.append(d)
        if len(col) == 7:
            weeks.append(col)
            col = []
    if col:
        col.extend([None] * (7 - len(col)))
        weeks.append(col)
    return weeks


def month_ticks(weeks) -> list[tuple[int, str]]:
    ticks, seen = [], set()
    for wi, col in enumerate(weeks):
        first = next((d for d in col if d), None)
        if not first:
            continue
        dt = datetime.strptime(first["date"], "%Y-%m-%d")
        key = (dt.year, dt.month)
        if key not in seen and dt.day <= 14:
            seen.add(key)
            ticks.append((wi, MONTHS[dt.month - 1]))
    return ticks


def build() -> str:
    data = load()
    days, stats = data["days"], data["stats"]
    weeks = to_weeks(days)
    n_weeks = len(weeks)

    grid_w = n_weeks * PITCH - GAP
    grid_h = 7 * PITCH - GAP
    grid_x = PAD_X + LABEL_W
    grid_y = PAD_TOP
    width = grid_x + grid_w + PAD_X
    height = grid_y + grid_h + FOOTER_H

    step = 0.012  # seconds of delay per diagonal step
    parts: list[str] = []

    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
        f'height="{height}" viewBox="0 0 {width} {height}" '
        f'role="img" aria-label="{escape(USERNAME)} contribution graph">'
    )

    anim = "" if STATIC else f"""
    .cell {{ opacity: 0; animation: pop .38s ease-out forwards; }}
    .row  {{ opacity: 0; animation: fade .5s ease-out forwards; }}
    @keyframes pop {{
      from {{ opacity: 0; transform: translateY(-6px) scale(.72); }}
      to   {{ opacity: 1; transform: translateY(0) scale(1); }}
    }}
    @keyframes fade {{ from {{ opacity: 0 }} to {{ opacity: 1 }} }}
    """
    parts.append(
        "<style>"
        f".mono{{font-family:{MONO};}}"
        ".cell{transform-box:fill-box;transform-origin:center;}"
        + anim
        + "</style>"
    )

    # panel
    parts.append(
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" '
        f'fill="{BG}" stroke="{BORDER}"/>'
    )
    # title bar
    parts.append(f'<g class="mono" font-size="11">')
    for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{PAD_X + 4 + i * 15}" cy="19" r="5" fill="{c}"/>')
    parts.append(
        f'<text x="{PAD_X + 56}" y="23" fill="{DIM}">'
        f'{escape(USERNAME)} — contributions.sh</text>'
    )
    parts.append(
        f'<text x="{width - PAD_X}" y="23" fill="{DIM}" text-anchor="end">'
        f'{escape(data["range"]["start"])} → {escape(data["range"]["end"])}</text>'
    )
    parts.append("</g>")

    # month labels
    parts.append(f'<g class="mono" font-size="9" fill="{DIM}">')
    for wi, label in month_ticks(weeks):
        parts.append(f'<text x="{grid_x + wi * PITCH}" y="{grid_y - 6}">{label}</text>')
    for dow, label in DAY_LABELS.items():
        y = grid_y + dow * PITCH + CELL - 2
        parts.append(f'<text x="{PAD_X}" y="{y}">{label}</text>')
    parts.append("</g>")

    # grid
    parts.append("<g>")
    for wi, col in enumerate(weeks):
        for dow, day in enumerate(col):
            if day is None:
                continue
            lvl = max(0, min(len(PALETTE) - 1, int(day["level"])))
            x = grid_x + wi * PITCH
            y = grid_y + dow * PITCH
            delay = "" if STATIC else (
                f' style="animation-delay:{(wi + dow * 2) * step:.3f}s"'
            )
            parts.append(
                f'<rect class="cell" x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                f'rx="2.5" fill="{PALETTE[lvl]}"{delay}>'
                f'<title>{day["count"]} on {day["date"]}</title></rect>'
            )
    parts.append("</g>")

    # footer: stats line + legend
    tail = (n_weeks + 14) * step
    fy = grid_y + grid_h + 22
    d1 = "" if STATIC else f' style="animation-delay:{tail:.2f}s"'
    d2 = "" if STATIC else f' style="animation-delay:{tail + .12:.2f}s"'

    total = f'{stats["total"]:,}'
    summary = (
        f'{total} contributions in the last year   '
        f'·   current streak {stats["current_streak"]}d'
        f'   ·   longest {stats["longest_streak"]}d'
    )
    parts.append(
        f'<g class="row mono" font-size="11"{d1}>'
        f'<text x="{grid_x}" y="{fy}" fill="{ACCENT}">{total}</text>'
        f'<text x="{grid_x + len(total) * 6.7:.0f}" y="{fy}" fill="{FG}">'
        f'{escape(summary[len(total):])}</text></g>'
    )

    lx = width - PAD_X - (len(PALETTE) * PITCH + 74)
    parts.append(f'<g class="row mono" font-size="9" fill="{DIM}"{d2}>')
    parts.append(f'<text x="{lx}" y="{fy}">Less</text>')
    for i, c in enumerate(PALETTE):
        parts.append(
            f'<rect x="{lx + 30 + i * PITCH}" y="{fy - 9}" width="{CELL}" '
            f'height="{CELL}" rx="2.5" fill="{c}"/>'
        )
    parts.append(
        f'<text x="{lx + 36 + len(PALETTE) * PITCH}" y="{fy}">More</text></g>'
    )

    parts.append("</svg>")
    return "".join(parts)


if __name__ == "__main__":
    OUT.write_text(build() + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
