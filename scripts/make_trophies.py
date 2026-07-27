#!/usr/bin/env python3
"""Self-hosted replacement for github-profile-trophy -> trophies.svg.

Six stat tiles driven by data/contributions.json (so they refresh daily with
the heatmap) plus a row of achievement pills from config.ACHIEVEMENTS.

STATIC=1 emits a frozen frame.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import (  # noqa: E402
    ACCENT, ACCENT_2, ACHIEVEMENTS, BG, BORDER, DIM, FG, HANDLE,
    PUBLIC_REPOS,
)

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "contributions.json"
OUT = ROOT / "trophies.svg"
STATIC = os.environ.get("STATIC") == "1"

MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"
WIDTH = 801           # matches contrib-heatmap.svg so the edges line up
PAD = 18
TITLE_H = 38
TILE_H = 68
GAP = 10
PILL_H = 22
CHAR_W = 6.01         # 10px monospace advance


def main() -> str:
    if not SRC.exists():
        raise SystemExit(f"missing {SRC} — run fetch_contributions.py first")
    st = json.loads(SRC.read_text())["stats"]

    tiles = [
        (f'{st["total"]:,}', "contributions", ACCENT),
        (f'{st["current_streak"]}', "current streak", ACCENT_2),
        (f'{st["longest_streak"]}', "longest streak", ACCENT_2),
        (f'{st["best_day"]["count"]}', "best day", FG),
        (f'{st["days_active"]}', "active days", FG),
        (f"{PUBLIC_REPOS}", "public repos", FG),
    ]

    n = len(tiles)
    grid_w = WIDTH - PAD * 2
    tile_w = (grid_w - GAP * (n - 1)) / n
    grid_y = TITLE_H + PAD
    pills_y = grid_y + TILE_H + 22
    height = pills_y + PILL_H + PAD

    p: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" '
        f'height="{height}" viewBox="0 0 {WIDTH} {height}" role="img" '
        f'aria-label="{escape(HANDLE)} GitHub trophies">'
    ]

    anim = "" if STATIC else """
    .t { opacity: 0; animation: rise .45s ease-out forwards; }
    @keyframes rise {
      from { opacity: 0; transform: translateY(8px); }
      to   { opacity: 1; transform: translateY(0); }
    }
    """
    p.append(
        "<style>"
        f".mono{{font-family:{MONO};}}"
        ".t{transform-box:fill-box;transform-origin:center;}"
        + anim
        + "</style>"
    )

    p.append(
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" '
        f'rx="10" fill="{BG}" stroke="{BORDER}"/>'
    )

    p.append('<g class="mono" font-size="11">')
    for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        p.append(f'<circle cx="{PAD + 4 + i * 15}" cy="19" r="5" fill="{c}"/>')
    p.append(f'<text x="{PAD + 56}" y="23" fill="{DIM}">trophies.sh</text>')
    p.append("</g>")

    for i, (value, label, color) in enumerate(tiles):
        x = PAD + i * (tile_w + GAP)
        cx = x + tile_w / 2
        d = "" if STATIC else f' style="animation-delay:{i * 0.08:.2f}s"'
        p.append(f'<g class="t"{d}>')
        p.append(
            f'<rect x="{x:.1f}" y="{grid_y}" width="{tile_w:.1f}" '
            f'height="{TILE_H}" rx="8" fill="#161b22" stroke="{BORDER}"/>'
        )
        p.append(
            f'<text class="mono" x="{cx:.1f}" y="{grid_y + 32}" fill="{color}" '
            f'font-size="21" text-anchor="middle">{escape(value)}</text>'
        )
        p.append(
            f'<text class="mono" x="{cx:.1f}" y="{grid_y + 52}" fill="{DIM}" '
            f'font-size="10" text-anchor="middle">{escape(label)}</text>'
        )
        p.append("</g>")

    x = PAD
    for i, name in enumerate(ACHIEVEMENTS):
        w = len(name) * CHAR_W + 24
        d = "" if STATIC else f' style="animation-delay:{(len(tiles) + i) * 0.08:.2f}s"'
        p.append(f'<g class="t"{d}>')
        p.append(
            f'<rect x="{x:.1f}" y="{pills_y}" width="{w:.1f}" height="{PILL_H}" '
            f'rx="11" fill="#161b22" stroke="{ACCENT}" stroke-opacity="0.45"/>'
        )
        p.append(
            f'<text class="mono" x="{x + w / 2:.1f}" y="{pills_y + 15}" '
            f'fill="{ACCENT}" font-size="10" text-anchor="middle">'
            f'{escape(name)}</text>'
        )
        p.append("</g>")
        x += w + 8

    d = "" if STATIC else f' style="animation-delay:{(len(tiles) + len(ACHIEVEMENTS)) * 0.08:.2f}s"'
    p.append(
        f'<text class="t mono" x="{WIDTH - PAD}" y="{pills_y + 15}" fill="{DIM}" '
        f'font-size="10" text-anchor="end"{d}>GitHub achievements</text>'
    )

    p.append("</svg>")
    return "".join(p)


if __name__ == "__main__":
    OUT.write_text(main() + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
