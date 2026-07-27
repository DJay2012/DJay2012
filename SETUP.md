# Setup

## 1. Edit your details

Open `scripts/config.py` and rewrite `CARD_ROWS`. Everything else (colors, sizes,
username) lives there too.

## 2. Push to the magic repo

GitHub renders `README.md` from the repo named exactly after your username at the
top of your profile page.

```bash
cd DJay2012
git init -b main
gh repo create DJay2012 --public --source=. --remote=origin   # or create it in the UI
git add -A && git commit -m "feat: animated profile art"
git push -u origin main
```

If the repo already exists, `git remote add origin git@github.com:DJay2012/DJay2012.git`
and push.

## 3. Generate with real data

The committed SVGs were built from **sample** contribution data so you could see
the layout. Replace them with yours:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r scripts/requirements.txt
python scripts/fetch_contributions.py    # scrapes your public calendar, no token
python scripts/render_heatmap_svg.py
python scripts/make_info_card.py
```

Or just let the Action do it — push, then run **Actions → Update profile art →
Run workflow** once by hand.

## 4. Check it locally

Open `preview.html` in a browser. It embeds the SVGs via `<img>`, exactly the way
GitHub does, so what you see there is what your profile will look like.
`STATIC=1 python scripts/make_info_card.py` emits a frozen frame instead.

## How it stays fresh

`.github/workflows/update-profile-art.yml` runs at ~06:17 UTC daily, re-scrapes
`github.com/users/DJay2012/contributions`, re-renders the heatmap, and commits it
with `[skip ci]` so the bot doesn't retrigger itself. Needs no secrets — the
`contents: write` permission on `GITHUB_TOKEN` is enough.

## Gotchas this repo already works around

- GitHub strips `<script>` and external CSS from READMEs, so all motion lives
  inside the SVG files as CSS keyframes with `animation-fill-mode: forwards`
  (plays once, then freezes — no looping glow).
- Inline `style="margin-top:..."` in a README does nothing. Only `<br>` gives
  vertical space.
- `<h1>`/`<h2>` draw a full-width rule; the README uses `<h3>` for the fake shell
  prompts.
- The heatmap `<img>` has no `width` attribute on purpose — the SVG's natural
  width tracks the number of week columns, so it can never mismatch.

## Adding the ASCII portrait later

Set `CARD_WIDTH = 490` in `scripts/config.py`, regenerate the card, and put the
portrait and card in a `<table>` row (the only reliable way to get two images
side by side on GitHub):

```html
<table><tr>
  <td valign="top"><img src="./ascii.svg" width="370" /></td>
  <td valign="top"><img src="./info-card.svg" width="490" /></td>
</tr></table>
```
