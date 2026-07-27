"""Single place to edit everything about your profile art."""

# ---------------------------------------------------------------- identity
USERNAME = "DJay2012"

# ------------------------------------------------------------- info card
# Keys are the left column, values the right. Long values wrap automatically.
HANDLE = "DJay"            # used everywhere; no real name anywhere in the art
NAME = ""                  # leave empty to show no name beside the title
CARD_TITLE = f"{HANDLE}@github"

CARD_ROWS = [
    # The badge row in the README covers the stack in detail, so the card
    # keeps one condensed Stack line instead of four.
    ("Role",     "Python backend developer"),
    ("Location", "Mumbai, India · working from home"),
    ("Focus",    "APIs, backend logic, data processing pipelines"),
    ("Stack",    "Python · Django · DRF · MySQL · MongoDB · Neo4j"),
    ("Projects", "DJBot (NLP) · Ad sales prediction · UI components"),
    ("Repos",    "13 public · Pull Shark · Quickdraw · Pair Extraordinaire"),
    ("Links",    "linkedin.com/in/djay4047"),
]

# ------------------------------------------------------------- trophy panel
# Static facts the contribution scrape can't see. Update when they change.
PUBLIC_REPOS = 13
ACHIEVEMENTS = ["Pull Shark", "Quickdraw", "Pair Extraordinaire", "YOLO"]

# --------------------------------------------------------------- palette
FG = "#c9d1d9"          # primary text
DIM = "#8b949e"         # labels / secondary
ACCENT = "#39d353"      # neon green
ACCENT_2 = "#58a6ff"    # blue
BG = "#0d1117"          # panel background
BORDER = "#30363d"      # panel border

# contribution levels: none -> brightest
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

# ---------------------------------------------------------------- layout
# The card is centred under the heatmap. If you later add an ASCII portrait
# beside it, drop CARD_WIDTH back to ~490 and put the two in a <table> row.
CARD_WIDTH = 620
HEATMAP_WIDTH = 860
