"""Install the open-licensed fonts sciplot prefers (optional).

    python scripts/install_fonts.py            # Inter + Inter Display + JetBrains Mono
    python scripts/install_fonts.py --list     # show what matplotlib currently finds

sciplot works without these: every theme has a fallback stack
(Inter -> Helvetica Neue -> Helvetica -> Arial -> Liberation Sans -> DejaVu Sans), and
venues that require Arial (Cell, Neuron, PLOS) use Arial or its metric clone Liberation Sans.
Installing Inter simply gives the intended look.

Fonts are downloaded from their official GitHub releases (SIL Open Font License 1.1) into the
per-user font directory, and matplotlib's font cache is rebuilt. Other optional families
(IBM Plex Sans, Source Sans 3, DM Sans, Geist) can be installed from https://fonts.google.com
or your OS package manager; sciplot picks them up via font="plex"/"source"/"dm"/"geist".
"""
from __future__ import annotations

import argparse
import io
import os
import platform
import sys
import urllib.request
import zipfile
from pathlib import Path

FONTS = {
    "Inter": ("https://github.com/rsms/inter/releases/download/v4.1/Inter-4.1.zip",
              "extras/ttf/"),
    "JetBrains Mono": ("https://github.com/JetBrains/JetBrainsMono/releases/download/v2.304/"
                       "JetBrainsMono-2.304.zip", "fonts/ttf/"),
}


def font_dir() -> Path:
    system = platform.system()
    if system == "Darwin":
        return Path.home() / "Library" / "Fonts"
    if system == "Windows":
        return Path(os.environ.get("LOCALAPPDATA", Path.home())) / "Microsoft" / "Windows" / "Fonts"
    return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "fonts"


def install(name: str, dest: Path) -> int:
    url, prefix = FONTS[name]
    print(f"downloading {name} ...", flush=True)
    with urllib.request.urlopen(url, timeout=120) as r:
        data = r.read()
    n = 0
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for member in z.namelist():
            if member.startswith(prefix) and member.lower().endswith(".ttf"):
                (dest / Path(member).name).write_bytes(z.read(member))
                n += 1
    print(f"  {n} files -> {dest}")
    return n


def rebuild_cache():
    import matplotlib
    from matplotlib import font_manager as fm
    cache = Path(matplotlib.get_cachedir())
    for f in cache.glob("fontlist*.json"):
        f.unlink()
    fm.fontManager = fm._load_fontmanager(try_read_cache=False)


def listing():
    from matplotlib import font_manager as fm
    have = sorted({f.name for f in fm.fontManager.ttflist})
    want = ["Inter", "Inter Display", "Helvetica", "Arial", "Liberation Sans", "IBM Plex Sans",
            "Source Sans 3", "DM Sans", "Geist", "JetBrains Mono"]
    for w in want:
        print(f"  [{'x' if w in have else ' '}] {w}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--list", action="store_true", help="list preferred fonts matplotlib can see")
    ap.add_argument("--dest", type=Path, default=None, help="font directory (default: per-user)")
    a = ap.parse_args(argv)
    if a.list:
        listing()
        return 0
    dest = a.dest or font_dir()
    dest.mkdir(parents=True, exist_ok=True)
    for name in FONTS:
        try:
            install(name, dest)
        except Exception as e:  # network/proxy errors should not be fatal
            print(f"  failed: {e}", file=sys.stderr)
    rebuild_cache()
    listing()
    return 0


if __name__ == "__main__":
    sys.exit(main())
