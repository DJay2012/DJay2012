#!/usr/bin/env python3
"""Hand-authored neofetch-style info card -> info-card.svg.

Content lives in scripts/config.py. Lines fade + slide in on a stagger so
the panel looks like it's printing. STATIC=1 emits a frozen frame.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import (  # noqa: E402
    ACCENT, ACCENT_2, BG, BORDER, CARD_ROWS, CARD_TITLE, CARD_WIDTH,
    DIM, FG, NAME, PALETTE,
)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "info-card.svg"
STATIC = os.environ.get("STATIC") == "1"

MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"
PAD = 20
TITLE_H = 38
ROW_H = 22
KEY_W = 104
FONT = 12
CHAR_W = FONT * 0.601  # monospace advance width, near enough for wrapping


def wrap(text: str, limit: int) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        cand = f"{cur} {w}".strip()
        if len(cand) <= limit:
            cur = cand
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [""]


def build() -> str:
    value_chars = int((CARD_WIDTH - PAD * 2 - KEY_W - 8) / CHAR_W)

    laid: list[tuple[str, list[str]]] = [
        (key, wrap(val, value_chars)) for key, val in CARD_ROWS
    ]
    body_lines = sum(len(v) for _, v in laid)

    # Layout maths, mirrored exactly by the drawing code below. Keep in sync:
    # header line, divider, body rows, swatch strip, prompt line, bottom pad.
    first_y = TITLE_H + PAD + 14
    rows_y = first_y + ROW_H + (ROW_H - 4)
    swatch_y = rows_y + body_lines * ROW_H + 6
    prompt_y = swatch_y + 30
    height = prompt_y + 18

    p: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CARD_WIDTH}" '
        f'height="{height}" viewBox="0 0 {CARD_WIDTH} {height}" role="img" '
        f'aria-label="{escape(CARD_TITLE)} info card">'
    ]

    anim = "" if STATIC else """
    .ln { opacity: 0; animation: in .42s ease-out forwards; }
    @keyframes in {
      from { opacity: 0; transform: translateX(-10px); }
      to   { opacity: 1; transform: translateX(0); }
    }
    .cur { animation: blink 1.05s steps(1) infinite; }
    @keyframes blink { 0%,49% { opacity:1 } 50%,100% { opacity:0 } }
    """
    p.append(f"<style>.mono{{font-family:{MONO};}}{anim}</style>")

    p.append(
        f'<rect x="0.5" y="0.5" width="{CARD_WIDTH - 1}" height="{height - 1}" '
        f'rx="10" fill="{BG}" stroke="{BORDER}"/>'
    )
    p.append(
        f'<line x1="0" y1="{TITLE_H}" x2="{CARD_WIDTH}" y2="{TITLE_H}" '
        f'stroke="{BORDER}"/>'
    )

    # title bar
    p.append('<g class="mono" font-size="11">')
    for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        p.append(f'<circle cx="{PAD + 4 + i * 15}" cy="19" r="5" fill="{c}"/>')
    p.append(f'<text x="{PAD + 56}" y="23" fill="{DIM}">neofetch</text>')
    p.append("</g>")

    # rows
    y = first_y
    idx = 0
    p.append(f'<g class="mono" font-size="{FONT}">')

    p.append(
        _line(
            idx, PAD, y, [(ACCENT, escape(CARD_TITLE))],
            second=(PAD + (len(CARD_TITLE) + 3) * CHAR_W, DIM, escape(NAME)),
        )
    )
    idx += 1
    y += ROW_H
    p.append(
        _line(idx, PAD, y, [(DIM, "-" * 52)])
    )
    idx += 1
    y += ROW_H - 4

    for key, values in laid:
        for j, val in enumerate(values):
            label = f"{key}:" if j == 0 else ""
            p.append(
                _line(
                    idx, PAD, y,
                    [(ACCENT_2, escape(label))],
                    second=(PAD + KEY_W, FG, escape(val)),
                )
            )
            idx += 1
            y += ROW_H
    p.append("</g>")

    assert y == rows_y + body_lines * ROW_H, "layout drift vs height maths"

    # color swatch strip, like neofetch's palette row
    y = swatch_y
    delay = "" if STATIC else f' style="animation-delay:{idx * 0.07:.2f}s"'
    p.append(f'<g class="ln"{delay}>')
    for i, c in enumerate(PALETTE + ["#58a6ff", "#bc8cff", "#f78166"]):
        p.append(
            f'<rect x="{PAD + i * 20}" y="{y}" width="15" height="10" rx="2" '
            f'fill="{c}"/>'
        )
    p.append("</g>")

    # prompt + cursor
    y = prompt_y
    delay = "" if STATIC else f' style="animation-delay:{(idx + 1) * 0.07:.2f}s"'
    p.append(
        f'<g class="ln mono" font-size="{FONT}"{delay}>'
        f'<text x="{PAD}" y="{y}" fill="{ACCENT}">$</text>'
        f'<rect class="cur" x="{PAD + 14}" y="{y - 10}" width="8" height="13" '
        f'fill="{FG}"/></g>'
    )

    p.append("</svg>")
    return "".join(p)


def _line(idx, x, y, spans, second=None) -> str:
    delay = "" if STATIC else f' style="animation-delay:{idx * 0.07:.2f}s"'
    out = [f'<g class="ln"{delay}>']
    for fill, text in spans:
        out.append(f'<text x="{x}" y="{y}" fill="{fill}">{text}</text>')
    if second:
        sx, sfill, stext = second
        out.append(f'<text x="{sx}" y="{y}" fill="{sfill}">{stext}</text>')
    out.append("</g>")
    return "".join(out)


if __name__ == "__main__":
    OUT.write_text(build() + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
