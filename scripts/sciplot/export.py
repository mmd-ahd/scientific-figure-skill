"""Export figures for journals: vector PDF/SVG with editable text, raster TIFF/PNG.

Key rules encoded here
- Never use bbox_inches="tight" for journal figures: it silently changes the
  width you designed for. Use constrained layout + exact figsize instead
  (pass tight=True only for slides/web where exact size doesn't matter).
- pdf.fonttype/ps.fonttype = 42 (TrueType, editable in Illustrator/Inkscape);
  svg.fonttype = "none" (text stays text).
- Dense artists (rasters, >5k-point scatters, images) should be created with
  rasterized=True so the PDF stays small; the rest stays vector.
"""
from __future__ import annotations

import os
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt

MM = 1 / 25.4


def save(fig, path, formats=("pdf", "png"), dpi=600, tight=False, transparent=False,
         check=True, target=None, **kw):
    """Save `fig` to every format in `formats` (path extension is replaced).

    dpi: raster resolution for PNG/TIFF and for rasterized artists inside PDFs.
    Journals: 300 dpi photos/halftone, 600 combination, 1000-1200 line art.
    Returns list of written paths. With check=True runs sciplot.check.lint(fig).
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    out = []
    rc = {"pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
          "pdf.compression": 9}
    with mpl.rc_context(rc):
        for fmt in formats:
            p = path.with_suffix("." + fmt)
            extra = dict(kw)
            if tight:
                extra.setdefault("bbox_inches", "tight")
                extra.setdefault("pad_inches", 0.02)
            if fmt in ("tif", "tiff"):
                extra.setdefault("pil_kwargs", {"compression": "tiff_lzw"})
            if fmt in ("png", "tif", "tiff", "jpg"):
                extra.setdefault("dpi", dpi)
            else:
                extra.setdefault("dpi", dpi)  # affects rasterized artists only
            fig.savefig(p, format=fmt if fmt != "tif" else "tiff",
                        transparent=transparent, facecolor=fig.get_facecolor()
                        if not transparent else "none", **extra)
            out.append(str(p))
    if check:
        from .check import lint
        lint(fig, target=target, verbose=True)
    w, h = fig.get_size_inches()
    print(f"saved {', '.join(os.path.basename(o) for o in out)}  "
          f"[{w / MM:.0f} x {h / MM:.0f} mm]")
    return out


def preview(fig, path=None, dpi=200):
    """Write a PNG preview (for Claude to Read/inspect) and return its path."""
    if path is None:
        import tempfile
        path = os.path.join(tempfile.gettempdir(), "sciplot_preview.png")
    fig.savefig(path, dpi=dpi, facecolor=fig.get_facecolor())
    return path


def pdffonts(path):
    """Return `pdffonts` output (poppler) to confirm embedded TrueType fonts."""
    import shutil
    import subprocess
    if not shutil.which("pdffonts"):
        return "pdffonts not installed"
    return subprocess.run(["pdffonts", str(path)], capture_output=True, text=True).stdout


def close(fig=None):
    plt.close(fig if fig is not None else "all")
