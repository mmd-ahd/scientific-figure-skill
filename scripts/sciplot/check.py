"""Quality gates: lint a Figure against a venue spec; audit a palette for CVD safety.

    from sciplot import check
    check.lint(fig, target="nature")        # fonts, strokes, width, colors
    check.palette_report(["#..", ...])      # ΔE2000 normal / deutan / protan / tritan / gray
"""
from __future__ import annotations

import numpy as np
from matplotlib.colors import to_hex
from matplotlib.text import Text

from . import color as C

MM = 1 / 25.4

# Thresholds for categorical palettes (CIEDE2000)
DE_OK = 10.0      # distinct categories under simulated CVD
DE_GOOD = 20.0    # comfortable at small marker sizes

# Non-perceptual rainbow maps that distort data (Crameri et al. 2020, Nat Commun)
RAINBOW_CMAPS = {"jet", "rainbow", "hsv", "gist_rainbow", "gist_ncar", "nipy_spectral",
                 "spectral", "spectral_r", "jet_r", "rainbow_r", "gist_rainbow_r"}
ARIAL_LIKE = {"Arial", "Helvetica", "Liberation Sans", "Nimbus Sans", "Arimo"}


def font_in_use(family=None) -> str:
    """Name of the font matplotlib actually renders for `family` (default: current rc)."""
    import matplotlib as mpl
    from matplotlib import font_manager as fm
    path = fm.findfont(fm.FontProperties(family=family or mpl.rcParams["font.family"]))
    try:
        return fm.get_font(path).family_name
    except Exception:
        return path


def palette_report(colors, bg="#FFFFFF", verbose=True) -> dict:
    """Min pairwise ΔE2000 under normal vision, 3 CVD types and grayscale,
    plus each color's contrast against the background."""
    colors = [to_hex(c) for c in colors]
    rep = {"normal": C.min_pairwise_de(colors)[0]}
    for k in C.CVD_TYPES:
        rep[k] = C.min_pairwise_de(colors, cvd=k)[0]
    g = C.grayscale(colors)
    rep["gray"] = C.min_pairwise_de([C.to_hex(x) for x in g])[0]
    rep["min_bg_contrast"] = min(C.contrast_ratio(c, bg) for c in colors)
    rep["cvd_safe"] = min(rep[k] for k in C.CVD_TYPES) >= DE_OK
    if verbose:
        print("  ".join(f"{k}={v:.1f}" if isinstance(v, float) else f"{k}={v}"
                        for k, v in rep.items()))
    return rep


def _artist_colors(fig):
    """Hues used for data encoding: lines, small scatters, bars. Schematic patches,
    images and colormapped collections are ignored."""
    from matplotlib.container import BarContainer
    cols = set()
    for ax in fig.axes:
        if not ax.axison:
            continue
        for a in ax.get_lines():
            if a.get_visible() and len(a.get_xdata()) > 2:
                cols.add(to_hex(a.get_color()))
        for a in ax.collections:
            if a.get_visible() and a.get_array() is None:
                fc = a.get_facecolor()
                if 0 < len(fc) <= 12:
                    cols.update(to_hex(c) for c in fc if c[3] > 0.3)
        for cont in ax.containers:
            if isinstance(cont, BarContainer):
                cols.update(to_hex(b.get_facecolor()) for b in cont)
    out = []
    for c in cols:
        L, Ch, _ = C.rgb_to_oklch(C.to_rgb(c))
        if Ch > 0.04:
            out.append(c)
    # merge tints/shades of one hue (line + its lighter dots/band = one category)
    uniq = []
    for c in sorted(out, key=lambda c: -C.rgb_to_oklch(C.to_rgb(c))[1]):
        h = C.rgb_to_oklch(C.to_rgb(c))[2]
        if all(min(abs(h - C.rgb_to_oklch(C.to_rgb(u))[2]), 360 - abs(h - C.rgb_to_oklch(C.to_rgb(u))[2])) > 10
               for u in uniq):
            uniq.append(c)
    return sorted(uniq)


def _local_bg(t, fig_bg):
    """Color behind a text item: topmost filled patch under its center; None if it sits
    on an image (can't judge)."""
    ax = t.axes
    if ax is None:
        return to_hex(fig_bg)
    r = t.figure.canvas.get_renderer()
    bb = t.get_window_extent(r)
    cx, cy = (bb.x0 + bb.x1) / 2, (bb.y0 + bb.y1) / 2
    for im in ax.images:
        if im.get_window_extent(r).contains(cx, cy):
            return None
    under = [p for p in ax.patches if p.get_visible() and p.get_facecolor()[3] > 0.5
             and p.contains_point((cx, cy)) and p.get_zorder() <= t.get_zorder()]
    if under:
        return to_hex(max(under, key=lambda p: p.get_zorder()).get_facecolor())
    return to_hex(ax.get_facecolor()) if ax.patch.get_visible() else to_hex(fig_bg)


def lint(fig, target=None, verbose=True) -> list[str]:
    """Return a list of warnings for `fig` (and print them)."""
    from .layout import VENUES
    spec = VENUES.get(target or getattr(fig, "_sciplot_target", None) or "", {})
    fmin = spec.get("font_min", 5)
    fmax = spec.get("font_max", 12)
    lw_min = spec.get("line_min", 0.25)
    warns = []

    # --- figure size
    w_mm, h_mm = (np.array(fig.get_size_inches()) / MM)
    widths = spec.get("widths_mm", {})
    if widths and not any(abs(w_mm - v) < 1.5 for v in widths.values()):
        if w_mm > max(widths.values()) + 1.5:
            warns.append(f"width {w_mm:.0f} mm exceeds max {max(widths.values())} mm")
        else:
            warns.append(f"width {w_mm:.0f} mm is not a standard width {widths}")
    if spec.get("height_max_mm") and h_mm > spec["height_max_mm"] + 1:
        warns.append(f"height {h_mm:.0f} mm > max {spec['height_max_mm']} mm")

    # --- text sizes and contrast
    fig.canvas.draw()
    bg = fig.get_facecolor()
    small, big, lowc = set(), set(), set()
    for t in fig.findobj(Text):
        if not t.get_visible() or not t.get_text().strip():
            continue
        s = t.get_fontsize()
        if s < fmin - 0.05:
            small.add((round(s, 1), t.get_text()[:20]))
        if s > fmax + 0.05 and not getattr(t, "_sciplot_label", False):
            big.add((round(s, 1), t.get_text()[:20]))
        try:
            local = _local_bg(t, bg)
            if local is not None and C.contrast_ratio(to_hex(t.get_color()), local) < 3:
                lowc.add(t.get_text()[:20])
        except Exception:
            pass
    if small:
        warns.append(f"{len(small)} text item(s) below {fmin} pt: {sorted(small)[:4]}")
    if big:
        warns.append(f"{len(big)} text item(s) above {fmax} pt: {sorted(big)[:4]}")
    if lowc:
        warns.append(f"low-contrast text (<3:1 vs background): {sorted(lowc)[:4]}")

    # --- strokes
    thin = 0
    for ax in fig.axes:
        for ln in ax.get_lines():
            if ln.get_visible() and 0 < ln.get_linewidth() < lw_min:
                thin += 1
        for sp in ax.spines.values():
            if sp.get_visible() and 0 < sp.get_linewidth() < lw_min:
                thin += 1
    if thin:
        warns.append(f"{thin} line(s)/spine(s) thinner than {lw_min} pt (may vanish in print)")

    # --- fonts actually rendered (fallbacks are silent in matplotlib)
    fonts = set()
    for t in fig.findobj(Text):
        if t.get_visible() and t.get_text().strip():
            try:
                fonts.add(font_in_use(t.get_fontfamily()))
            except Exception:
                pass
    if spec.get("arial_only") and fonts - ARIAL_LIKE:
        warns.append(f"{target} requires Arial; rendered with {sorted(fonts)} "
                     "(install Arial or Liberation Sans)")
    if "DejaVu Sans" in fonts and len(fonts) > 1:
        warns.append(f"mixed fonts {sorted(fonts)}: a glyph or family fell back to DejaVu Sans")

    # --- colormaps
    bad_maps = set()
    for ax in fig.axes:
        for a in ax.get_children():
            cm = getattr(a, "get_cmap", None)
            if callable(cm) and getattr(a, "get_array", lambda: None)() is not None:
                name = getattr(cm(), "name", "")
                if name.lower() in RAINBOW_CMAPS:
                    bad_maps.add(name)
    if bad_maps:
        warns.append(f"rainbow colormap(s) {sorted(bad_maps)} are not perceptually uniform; "
                     "use viridis/cmc.batlow (sequential) or RdBu_r/cmc.vik (diverging)")

    # --- categorical colors
    cols = _artist_colors(fig)
    if 2 <= len(cols) <= 12:
        worst = min(C.min_pairwise_de(cols, cvd=k)[0] for k in C.CVD_TYPES)
        if worst < DE_OK:
            warns.append(f"categorical colors {cols} only ΔE={worst:.1f} apart under CVD "
                         f"simulation (<{DE_OK}); add redundant coding (marker/dash/label) "
                         "or switch palette")
    if len(cols) > 8:
        warns.append(f"{len(cols)} distinct hues — consider grey-out + highlight, or small multiples")

    if verbose:
        tag = f"[{target}] " if target else ""
        if warns:
            print(f"lint {tag}— {len(warns)} warning(s):")
            for w in warns:
                print("  •", w)
        else:
            print(f"lint {tag}— OK")
        if fonts:
            print(f"  font: {', '.join(sorted(fonts))}")
    return warns
