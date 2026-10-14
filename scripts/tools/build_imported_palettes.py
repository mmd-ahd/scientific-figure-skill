"""Rebuild sciplot/data/imported.json from upstream palette sources.

Sources are fetched verbatim (no hand-typed hex):
  Paul Tol      — tol-colors 2.2.0 wheel (colors.json), https://pypi.org/project/tol-colors/
  MetBrewer     — https://github.com/BlakeRMills/MetBrewer/blob/main/R/PaletteCode.R
  wesanderson   — https://github.com/karthik/wesanderson/blob/master/R/colors.R
  ggsci         — https://github.com/nanxstats/ggsci/blob/master/R/palettes.R
  Catppuccin    — https://github.com/catppuccin/palette/blob/main/palette.json
  Rosé Pine     — https://github.com/rose-pine/palette/blob/main/palette.json
  Riso inks     — https://github.com/mattdesl/riso-colors (riso-colors.json)
  Nord          — https://github.com/nordtheme/nord/blob/develop/src/nord.css
  matplotlib    — mpl.color_sequences (okabe_ito, petroff6/8/10, tab10)
Usage: python build_imported_palettes.py <dir-with-downloads>
"""
import json
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sciplot.color import rgb_to_oklab, to_rgb  # noqa: E402

src = Path(sys.argv[1])
out = {}


def kind_of(colors):
    L = np.array([rgb_to_oklab(to_rgb(c))[0] for c in colors])
    d = np.diff(L)
    if len(colors) >= 5 and (np.all(d > -0.02) or np.all(d < 0.02)) and abs(L[-1] - L[0]) > 0.3:
        return "seq"
    i = int(np.argmax(L))
    if len(colors) >= 5 and 0 < i < len(L) - 1 and L[i] > 0.85 and \
            np.all(np.diff(L[: i + 1]) > -0.03) and np.all(np.diff(L[i:]) < 0.03):
        return "div"
    return "cat"


def add(name, colors, family, source, kind=None, **meta):
    colors = ["#" + c.lstrip("#").upper() for c in colors]
    out[name] = dict(colors=colors, kind=kind or kind_of(colors), family=family,
                     source=source, **meta)


# --- Paul Tol
tol = json.loads((src / "tolpkg/tol_colors/colors.json").read_text())
TOL = "Paul Tol, tol-colors 2.2.0 (personal.sron.nl/~pault)"
for k, v in tol["colorsets"].items():
    if k == "land_cover":
        continue
    cols = [c for n, c in v.items() if n not in ("white", "black") or k == "high_contrast"]
    cols = [c for c in cols if c.upper() not in ("#FFFFFF",)]
    add(f"tol.{k}", cols, "accessible", TOL, kind="cat", cvd_claim=True)
for k, v in tol["colormaps"].items():
    add(f"tol.{k}", v["colors"], "accessible", TOL, bad=v["bad"],
        kind="div" if k in ("sunset", "nightfall", "BuRd", "PRGn") else "seq", cvd_claim=True)

# --- MetBrewer (colorblind flag from the package)
txt = (src / "metbrewer.R").read_text()
for m in re.finditer(r'^\s*(\w+) = list\(c\(([^)]*)\), c\(([^)]*)\), colorblind=(TRUE|FALSE)\)', txt, re.M):
    name, cols, order, cb = m.groups()
    cols = re.findall(r'"(#[0-9a-fA-F]{6})"', cols)
    order = [int(x) - 1 for x in order.split(",")]
    add(f"met.{name.lower()}", cols, "art", "MetBrewer (Blake R. Mills), Met Museum artworks",
        cat_order=order, cvd_claim=cb == "TRUE")

# --- wesanderson
txt = (src / "wes.R").read_text()
for m in re.finditer(r'^\s*(\w+) = c\(([^)]*)\)', txt, re.M):
    name, cols = m.groups()
    if name in ("Rushmore", "Zissou1Continuous"):
        continue
    add(f"wes.{name.lower()}", re.findall(r'"(#[0-9A-Fa-f]{6})"', cols), "cinema",
        "wesanderson R package (Karthik Ram)")

# --- ggsci (journal / sci-fi inspired)
txt = (src / "ggsci.R").read_text()
keep = {("npg", "nrc"): "journal.npg", ("aaas", "default"): "journal.aaas",
        ("nejm", "default"): "journal.nejm", ("lancet", "lanonc"): "journal.lancet",
        ("jama", "default"): "journal.jama", ("jco", "default"): "journal.jco",
        ("uchicago", "default"): "journal.uchicago", ("frontiers", "default"): "journal.frontiers",
        ("d3", "category10"): "d3.category10", ("tron", "legacy"): "scifi.tron",
        ("startrek", "uniform"): "scifi.startrek", ("futurama", "planetexpress"): "scifi.futurama",
        ("flatui", "default"): "ui.flatui", ("flatui", "aussie"): "ui.flatui_aussie",
        ("cosmic", "hallmarks_light"): "journal.cosmic_light",
        ("cosmic", "hallmarks_dark"): "journal.cosmic_dark"}
for m in re.finditer(r'ggsci_db\$"(\w+)"\$"(\w+)" <- c\((.*?)\)', txt, re.S):
    a, b, body = m.groups()
    if (a, b) in keep:
        fam = "journal" if keep[(a, b)].startswith("journal") else "pop"
        add(keep[(a, b)], re.findall(r'"(#[0-9A-Fa-f]{6})"', body), fam,
            f"ggsci (Nan Xiao) '{a}/{b}' — inspired by the publisher's figures",
            kind="cat", bg="dark" if a == "tron" or b.endswith("dark") else "light")

# --- Catppuccin (latte = light, mocha = dark)
cp = json.loads((src / "catppuccin.json").read_text())
accents = ["red", "peach", "yellow", "green", "teal", "sky", "blue", "mauve", "pink", "lavender"]
for flavor, bg in (("latte", "light"), ("frappe", "dark"), ("mocha", "dark")):
    c = cp[flavor]["colors"]
    add(f"theme.catppuccin_{flavor}", [c[a]["hex"] for a in accents], "theme",
        "Catppuccin palette.json", kind="cat", bg=bg, background=c["base"]["hex"],
        text=c["text"]["hex"])

# --- Rosé Pine
rp = json.loads((src / "rosepine.json").read_text())
for var, bg in (("main", "dark"), ("moon", "dark"), ("dawn", "light")):
    d = {c["role"]: "#" + c["hex"] for c in rp[var]}
    add(f"theme.rosepine_{var}", [d[k] for k in ("love", "gold", "rose", "pine", "foam", "iris")],
        "theme", "Rosé Pine palette.json", kind="cat", bg=bg, background=d["base"], text=d["text"])

# --- Nord
nord = dict(re.findall(r"--(nord\d+):\s*(#[0-9a-fA-F]{6})", (src / "nord.css").read_text()))
add("theme.nord_aurora", [nord[f"nord{i}"] for i in (11, 12, 13, 14, 15)], "theme", "Nord (nordtheme)",
    kind="cat", bg="any", background=nord["nord0"])
add("theme.nord_frost", [nord[f"nord{i}"] for i in (7, 8, 9, 10)], "theme", "Nord (nordtheme)",
    kind="cat", bg="any")
add("theme.nord_full", [nord[f"nord{i}"] for i in (10, 11, 12, 13, 14, 15, 7)], "theme",
    "Nord (nordtheme)", kind="cat", bg="dark", background=nord["nord0"], text=nord["nord6"])

# --- Riso inks
riso = {r["name"]: r["hex"] for r in json.loads((src / "riso.json").read_text())}
out["_riso_inks"] = riso

# --- matplotlib built-in color sequences
import matplotlib as mpl  # noqa: E402
from matplotlib.colors import to_hex  # noqa: E402
for k in ("okabe_ito", "petroff6", "petroff8", "petroff10", "tab10"):
    if k in mpl.color_sequences:
        add(f"mpl.{k}", [to_hex(c) for c in mpl.color_sequences[k]], "accessible",
            "matplotlib color_sequences", kind="cat",
            cvd_claim=k != "tab10")

dst = Path(__file__).resolve().parents[1] / "sciplot/data/imported.json"
dst.write_text(json.dumps(out, indent=1))
print(f"{len(out)} entries -> {dst}")
