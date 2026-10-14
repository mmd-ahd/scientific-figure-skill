"""Programmatic schematics that match the data panels (same fonts, strokes, palette).

Coordinate system: `canvas(ax)` turns an axes into a mm-based drawing board
(0..width_mm x 0..height_mm, origin bottom-left, equal aspect, no axes), so
positions in the code correspond to physical size on the page.

    ax = fig.add_subplot(...); S = schematic.canvas(ax)
    a = schematic.box(ax, (5, 10), 18, 8, "Stimulus", fc=pal[0])
    b = schematic.box(ax, (35, 10), 18, 8, "RNN", fc=pal[1])
    schematic.connect(ax, a, b)
"""
from __future__ import annotations

import numpy as np
from matplotlib.patches import (Circle, FancyArrowPatch, FancyBboxPatch, Polygon,
                                 Rectangle)

from . import color as C
from .palettes import cmap as _cmap


def canvas(ax, width_mm=None, height_mm=None):
    """Make `ax` a mm-scaled blank canvas sized to its physical extent."""
    fig = ax.figure
    fig.canvas.draw_idle()
    bb = ax.get_position()
    fw, fh = fig.get_size_inches()
    w = width_mm or bb.width * fw * 25.4
    h = height_mm or bb.height * fh * 25.4
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.set_aspect("equal", adjustable="box")
    ax.set_axis_off()
    return w, h


def _pt(ax):
    """1 typographic point in mm (canvas units)."""
    return 25.4 / 72


def text_size_mm(ax, text, fontsize=None, weight="medium"):
    """(width, height) of a text string in canvas mm units."""
    import matplotlib as mpl
    from matplotlib.textpath import TextPath
    from matplotlib.font_manager import FontProperties
    fs = fontsize or mpl.rcParams["font.size"]
    fp = FontProperties(family=mpl.rcParams["font.sans-serif"][0], weight=weight, size=fs)
    lines = str(text).split("\n")
    ws = [TextPath((0, 0), ln or " ", prop=fp).get_extents().width for ln in lines]
    pt = 25.4 / 72
    return max(ws) * pt, len(lines) * fs * 1.25 * pt


def box(ax, xy, w=None, h=None, text=None, fc="#E8EEF7", ec=None, lw=None, radius=1.2,
        text_color=None, fontsize=None, weight="medium", alpha=1.0, ls="-",
        shadow=False, zorder=2, pad_mm=(2.4, 1.6), anchor="ll", **textkw):
    """Rounded box with centered label. ec=None -> darker shade of fc.
    w/h=None -> sized to the text (+pad_mm), so boxes stay right at any font size.
    anchor: 'll' = xy is lower-left corner, 'c' = xy is the center.
    Returns the patch (pass it to connect())."""
    if (w is None or h is None) and text:
        tw, th_ = text_size_mm(ax, text, fontsize, weight)
        w = w if w is not None else tw + 2 * pad_mm[0]
        h = h if h is not None else th_ + 2 * pad_mm[1]
    x, y = xy
    if anchor == "c":
        x, y = x - w / 2, y - h / 2
    ec = ec if ec is not None else C.darken(fc, 0.25) if fc not in (None, "none") else "0.2"
    lw = lw if lw is not None else 0.6
    if shadow:
        sh = FancyBboxPatch((x + 0.5, y - 0.5), w, h, boxstyle=f"round,pad=0,rounding_size={radius}",
                            fc="0", ec="none", alpha=0.08, zorder=zorder - 0.1)
        ax.add_patch(sh)
    p = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={radius}",
                       fc=fc, ec=ec, lw=lw, alpha=alpha, ls=ls, zorder=zorder)
    ax.add_patch(p)
    if text:
        tc = text_color or (C.ink_on(fc) if fc not in (None, "none") else "0.1")
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", color=tc,
                fontsize=fontsize, weight=weight, zorder=zorder + 0.1, **textkw)
    return p


def pill(ax, xy, w=None, h=None, text=None, **kw):
    """Fully rounded tag/badge (auto-sized to text when w/h are None)."""
    if (w is None or h is None) and text:
        tw, th_ = text_size_mm(ax, text, kw.get("fontsize"), kw.get("weight", "medium"))
        pad = kw.pop("pad_mm", (2.4, 1.2))
        w = w if w is not None else tw + 2 * pad[0] + th_ * 0.4
        h = h if h is not None else th_ + 2 * pad[1]
    return box(ax, xy, w, h, text, radius=h / 2, **kw)


def circle(ax, xy, r, fc="#FFFFFF", ec="0.2", lw=0.6, text=None, fontsize=None, zorder=3, **kw):
    """Circle (node) of radius `r` mm at `xy`, with optional centred label."""
    p = Circle(xy, r, fc=fc, ec=ec, lw=lw, zorder=zorder, **kw)
    ax.add_patch(p)
    if text:
        ax.text(*xy, text, ha="center", va="center", fontsize=fontsize,
                color=C.ink_on(fc), zorder=zorder + 0.1)
    return p


def arrow(ax, p1, p2, color="0.25", lw=0.8, rad=0.0, style="-|>", head=3.0, shrink=0.0,
          ls="-", zorder=1.5, **kw):
    """Arrow between two points (mm). rad != 0 gives a curved arc (try ±0.3).
    style: '-|>' filled head (default), '->' open, '-' line, '<|-|>' double."""
    a = FancyArrowPatch(p1, p2, arrowstyle=f"{style},head_length={head * 0.9},head_width={head * 0.55}"
                        if "|>" in style or ">" in style else style,
                        connectionstyle=f"arc3,rad={rad}", color=color, lw=lw, ls=ls,
                        shrinkA=shrink, shrinkB=shrink, mutation_scale=1, zorder=zorder,
                        capstyle="round", joinstyle="round", **kw)
    ax.add_patch(a)
    return a


def connect(ax, a, b, side_a="right", side_b="left", gap=0.8, **kw):
    """Arrow from patch `a` to patch `b` attached at given sides
    ('left','right','top','bottom')."""
    def anchor(p, side):
        bb = p.get_bbox() if hasattr(p, "get_bbox") else None
        if isinstance(p, Circle):
            (cx, cy), r = p.center, p.radius
            return {"left": (cx - r, cy), "right": (cx + r, cy),
                    "top": (cx, cy + r), "bottom": (cx, cy - r)}[side]
        x0, y0, x1, y1 = bb.x0, bb.y0, bb.x1, bb.y1
        return {"left": (x0, (y0 + y1) / 2), "right": (x1, (y0 + y1) / 2),
                "top": ((x0 + x1) / 2, y1), "bottom": ((x0 + x1) / 2, y0)}[side]
    p1, p2 = np.array(anchor(a, side_a)), np.array(anchor(b, side_b))
    d = p2 - p1
    n = d / (np.linalg.norm(d) + 1e-9)
    return arrow(ax, tuple(p1 + n * gap), tuple(p2 - n * gap), **kw)


def pipeline(ax, steps, xy=(2, 2), w=16, h=8, gap=6, colors=None, vertical=False, **kw):
    """Chain of boxes connected by arrows. Returns list of patches."""
    colors = colors or ["#EEF1F6"] * len(steps)
    patches = []
    x, y = xy
    for i, s in enumerate(steps):
        p = box(ax, (x, y), w, h, s, fc=colors[i % len(colors)], **kw)
        if patches:
            connect(ax, patches[-1], p, "bottom" if vertical else "right",
                    "top" if vertical else "left")
        patches.append(p)
        if vertical:
            y -= h + gap
        else:
            x += w + gap
    return patches


def network(ax, layers, xy=(5, 5), width=40, height=25, r=1.4, colors=None,
            edge_color="0.75", edge_lw=0.35, node_ec="0.25", node_lw=0.5, dense=True):
    """Feed-forward network glyph: `layers` = list of node counts per layer."""
    colors = colors or ["#FFFFFF"] * len(layers)
    x0, y0 = xy
    xs = np.linspace(x0, x0 + width, len(layers))
    pos = []
    for i, n in enumerate(layers):
        ys = np.linspace(y0, y0 + height, n + 2)[1:-1] if n > 1 else [y0 + height / 2]
        pos.append([(xs[i], yy) for yy in ys])
    if dense:
        for la, lb in zip(pos[:-1], pos[1:]):
            for pa in la:
                for pb in lb:
                    ax.plot([pa[0], pb[0]], [pa[1], pb[1]], color=edge_color, lw=edge_lw,
                            zorder=1, solid_capstyle="round")
    for i, la in enumerate(pos):
        for p in la:
            circle(ax, p, r, fc=colors[i % len(colors)], ec=node_ec, lw=node_lw)
    return pos


def recurrent_unit(ax, xy, r=5, fc="#FFFFFF", text="RNN", loop_color="0.3", **kw):
    """Node with a self-loop arrow on top (recurrence)."""
    c = circle(ax, xy, r, fc=fc, text=text, **kw)
    x, y = xy
    arrow(ax, (x - r * 0.45, y + r * 0.9), (x + r * 0.45, y + r * 0.9), rad=-1.6,
          color=loop_color, lw=0.7)
    return c


def layer_stack(ax, xy, w, h, n=4, depth=(1.6, 1.2), fc="#DCE6F2", ec=None, lw=0.5,
                label=None, fontsize=None):
    """Isometric stack of feature maps (CNN layer glyph)."""
    ec = ec or C.darken(fc, 0.3)
    x, y = xy
    dx, dy = depth
    for i in range(n)[::-1]:
        ox, oy = x + i * dx, y + i * dy
        ax.add_patch(Rectangle((ox, oy), w, h, fc=C.mix(fc, "#FFFFFF", 0.12 * i), ec=ec,
                               lw=lw, zorder=2 + (n - i) * 0.01))
    if label:
        ax.text(x + (w + (n - 1) * dx) / 2, y - 1.5, label, ha="center", va="top", fontsize=fontsize)


def prism(ax, xy, w, h, d=4, fc="#DCE6F2", ec=None, lw=0.5, label=None, fontsize=None):
    """3-D block (transformer/encoder block glyph) with lit top and shaded side."""
    ec = ec or C.darken(fc, 0.3)
    x, y = xy
    front = Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw, zorder=3)
    top = Polygon([(x, y + h), (x + d, y + h + d * 0.6), (x + w + d, y + h + d * 0.6), (x + w, y + h)],
                  fc=C.lighten(fc, 0.35), ec=ec, lw=lw, zorder=3)
    side = Polygon([(x + w, y), (x + w + d, y + d * 0.6), (x + w + d, y + h + d * 0.6), (x + w, y + h)],
                   fc=C.darken(fc, 0.12), ec=ec, lw=lw, zorder=3)
    for p in (front, top, side):
        ax.add_patch(p)
    if label:
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=fontsize,
                color=C.ink_on(fc), zorder=4)
    return front


def mini_trace(ax, xy, w, h, kind="spikes", color="0.2", lw=0.6, seed=0):
    """Tiny signal icon inside a schematic: 'spikes', 'wave', 'noise', 'psth'."""
    rng = np.random.default_rng(seed)
    x0, y0 = xy
    t = np.linspace(0, 1, 200)
    if kind == "wave":
        s = 0.5 + 0.4 * np.sin(2 * np.pi * 2.5 * t)
    elif kind == "noise":
        s = 0.5 + 0.25 * np.convolve(rng.standard_normal(200), np.ones(7) / 7, "same")
    elif kind == "psth":
        s = 0.1 + 0.8 * np.exp(-((t - 0.4) / 0.12) ** 2)
    else:
        s = np.full_like(t, 0.15)
        for k in rng.choice(np.arange(10, 190), 9, replace=False):
            s[k] = 0.95
    ax.plot(x0 + t * w, y0 + s * h, color=color, lw=lw, solid_joinstyle="round", zorder=4)


def mini_matrix(ax, xy, size, data=None, cmap="viridis", n=6, ec="white", lw=0.3, seed=0):
    """Tiny heatmap glyph (weights / RDM / attention icon)."""
    rng = np.random.default_rng(seed)
    data = rng.random((n, n)) if data is None else np.asarray(data)
    cm = _cmap(cmap) if isinstance(cmap, str) else cmap
    n = data.shape[0]
    c = size / n
    for i in range(n):
        for j in range(data.shape[1]):
            ax.add_patch(Rectangle((xy[0] + j * c, xy[1] + (n - 1 - i) * c), c, c,
                                   fc=cm(float(data[i, j])), ec=ec, lw=lw, zorder=3))


def gradient_box(ax, xy, w, h, c1, c2, radius=1.2, horizontal=True, zorder=2, text=None,
                 text_color="white", fontsize=None, weight="semibold"):
    """Rounded box filled with a smooth OKLab gradient (graphical abstracts, slides)."""
    from matplotlib.colors import LinearSegmentedColormap
    cm = LinearSegmentedColormap.from_list("g", [C.mix(c1, c2, t) for t in np.linspace(0, 1, 16)])
    x, y = xy
    grad = np.linspace(0, 1, 256)[None, :] if horizontal else np.linspace(0, 1, 256)[:, None]
    im = ax.imshow(grad, extent=(x, x + w, y, y + h), cmap=cm, aspect="auto", zorder=zorder,
                   origin="lower")
    clip = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={radius}",
                          fc="none", ec="none", transform=ax.transData)
    ax.add_patch(clip)
    im.set_clip_path(clip)
    if text:
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", color=text_color,
                fontsize=fontsize, weight=weight, zorder=zorder + 0.1)
    return clip


def bracket(ax, x0, x1, y, text=None, h=1.2, color="0.35", lw=0.6, fontsize=None, below=False):
    """Curly-free square bracket grouping items in a schematic."""
    s = -1 if below else 1
    ax.plot([x0, x0, x1, x1], [y, y + s * h, y + s * h, y], color=color, lw=lw)
    if text:
        ax.text((x0 + x1) / 2, y + s * (h + 0.8), text, ha="center",
                va="bottom" if not below else "top", color=color, fontsize=fontsize)
