"""Single place to edit everything about your profile art."""

# ---------------------------------------------------------------- identity
USERNAME = "DJay2012"

# ------------------------------------------------------------- info card
# Keys are the left column, values the right. Long values wrap automatically.
NAME = "Dhananjay Pathak"
CARD_TITLE = f"dhananjay@{USERNAME}"

CARD_ROWS = [
    ("Role",     "Python backend developer"),
    ("Location", "Mumbai, India · working from home"),
    ("Focus",    "APIs, backend logic, data processing pipelines"),
    ("Backend",  "Python · Django · Django REST Framework"),
    ("Frontend", "JavaScript · HTML5 · CSS"),
    ("Data",     "MySQL · MongoDB · Neo4j · SQLite"),
    ("ML",       "NumPy · pandas · scikit-learn · Keras · Matplotlib"),
    ("Ops",      "Nginx · Gunicorn · Jenkins · Git · GitHub Actions"),
    ("Projects", "DJBot (NLP) · Ad sales prediction · UI components"),
    ("Badges",   "Pull Shark · Quickdraw · Pair Extraordinaire · YOLO"),
    ("Links",    "linkedin.com/in/djay4047"),
]

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
