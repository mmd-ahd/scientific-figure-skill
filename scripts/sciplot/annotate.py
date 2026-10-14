"""Annotation helpers: direct labels, significance brackets, scale bars,
event markers, slim colorbars, text halos.

Design rule: label data directly (text next to the line/cluster, in the
series' own color) instead of a legend box whenever there are <= ~6 series.
"""
from __future__ import annotations

import numpy as np
import matplotlib.patheffects as pe
from matplotlib.transforms import blended_transform_factory

from . import color as C


def _fg():
    import matplotlib as mpl
    return mpl.rcParams["text.color"]


def _muted(t=0.5):
    import matplotlib as mpl
    return C.mix(C.to_hex(C.to_rgb(mpl.rcParams["axes.facecolor"])),
                 C.to_hex(C.to_rgb(mpl.rcParams["text.color"])), t)


def halo(text_artist, width=2.0, color=None):
    """White (or bg-colored) outline so text stays legible on top of data."""
    if color is None:
        color = text_artist.axes.get_facecolor() if text_artist.axes else "white"
    text_artist.set_path_effects([pe.withStroke(linewidth=width, foreground=color)])
    return text_artist


def label_lines(ax, lines=None, labels=None, x=None, offset_pt=4, min_gap_pt=None,
                fontsize=None, weight="medium", side="right", **kw):
    """Put each line's label at its end (or at `x`), in the line's color,
    nudging vertically so labels don't overlap. Replaces ax.legend()."""
    lines = lines or [l for l in ax.get_lines() if not l.get_label().startswith("_")]
    labels = labels or [l.get_label() for l in lines]
    fig = ax.figure
    fig.canvas.draw()  # settle layout so point offsets are right
    fontsize = fontsize or (ax.yaxis.get_label().get_fontsize() * 0.95)
    min_gap_pt = min_gap_pt or fontsize * 1.15
    pts = []
    for ln in lines:
        xd, yd = np.asarray(ln.get_xdata(), float), np.asarray(ln.get_ydata(), float)
        ok = np.isfinite(xd) & np.isfinite(yd)
        xd, yd = xd[ok], yd[ok]
        if x is None:
            i = -1 if side == "right" else 0
            px, py = xd[i], yd[i]
        else:
            px, py = x, np.interp(x, xd, yd)
        pts.append([px, py])
    pts = np.array(pts)
    # convert y to display points, de-overlap, convert back
    disp = ax.transData.transform(pts)
    order = np.argsort(disp[:, 1])
    ys = disp[order, 1].copy()
    gap = min_gap_pt * fig.dpi / 72
    for _ in range(50):
        moved = False
        for i in range(1, len(ys)):
            if ys[i] - ys[i - 1] < gap:
                d = (gap - (ys[i] - ys[i - 1])) / 2
                ys[i - 1] -= d
                ys[i] += d
                moved = True
        if not moved:
            break
    disp[order, 1] = ys
    data_y = ax.transData.inverted().transform(disp)[:, 1]
    out = []
    bg = C.to_hex(ax.get_facecolor()[:3])
    for (px, _), y, ln, lab in zip(pts, data_y, lines, labels):
        t = ax.annotate(lab, (px, y), xytext=(offset_pt if side == "right" else -offset_pt, 0),
                        textcoords="offset points", va="center",
                        ha="left" if side == "right" else "right",
                        color=C.ensure_contrast(C.to_hex(C.to_rgb(ln.get_color())), bg, 3.0),
                        fontsize=fontsize, weight=weight,
                        annotation_clip=False, **kw)
        out.append(t)
    return out


def label_point(ax, x, y, text, dx=6, dy=6, color=None, arrow=False, **kw):
    """Callout label with optional thin leader line."""
    props = dict(arrowstyle="-", lw=0.5, color=color or _muted(0.6), shrinkA=0, shrinkB=2) if arrow else None
    return ax.annotate(text, (x, y), xytext=(dx, dy), textcoords="offset points",
                       color=color, arrowprops=props, **kw)


def stars(p) -> str:
    """P value -> '*' / '**' / '***' / '****' / 'n.s.'."""
    return "****" if p < 1e-4 else "***" if p < 1e-3 else "**" if p < 1e-2 else "*" if p < 0.05 else "n.s."


def fmt_p(p) -> str:
    """Exact p formatting (preferred over stars by Nature/Cell): P = 0.012, P < 0.001."""
    if p < 1e-3:
        e = int(np.floor(np.log10(p)))
        m = p / 10 ** e
        return f"$P = {m:.1f}\\times10^{{{e}}}$"
    return f"P = {p:.2g}" if p >= 0.01 else f"P = {p:.3f}"


def sig_bracket(ax, x1, x2, y, text, h=None, lw=None, color=None, fontsize=None,
                tip=True, pad_pt=1.5):
    """Significance bracket between x1 and x2 at height y (data coords).
    `text` may be a p-value float (formatted as stars) or a string."""
    color = color or _fg()
    if not isinstance(text, str):
        text = stars(text)
    lw = lw or ax.spines["left"].get_linewidth() or 0.6
    h = h if h is not None else 0.02 * np.diff(ax.get_ylim())[0]
    xs = [x1, x1, x2, x2] if tip else [x1, x2]
    ys = [y, y + h, y + h, y] if tip else [y + h, y + h]
    ax.plot(xs, ys, color=color, lw=lw, solid_capstyle="butt", clip_on=False)
    ns = text == "n.s."
    return ax.annotate(text, ((x1 + x2) / 2, y + h), xytext=(0, pad_pt if ns else 0),
                       textcoords="offset points", ha="center", va="bottom",
                       color=color, fontsize=fontsize or ax.xaxis.label.get_fontsize() * (0.9 if ns else 1.0))


def scale_bar(ax, x, y, dx=None, dy=None, xlabel=None, ylabel=None, lw=1.0,
              color=None, fontsize=None, pad_pt=2, hide_axes=True):
    """L-shaped scale bar (time x amplitude) at data coords (x, y) — for traces,
    rasters and images where axes are removed. Common in Neuron/Nature Neuro."""
    fs = fontsize or ax.xaxis.label.get_fontsize() * 0.9
    color = color or _fg()
    if dx:
        ax.plot([x, x + dx], [y, y], color=color, lw=lw, solid_capstyle="butt", clip_on=False)
        if xlabel:
            ax.annotate(xlabel, (x + dx / 2, y), xytext=(0, -pad_pt), textcoords="offset points",
                        ha="center", va="top", fontsize=fs, color=color)
    if dy:
        if ax.yaxis_inverted():
            dy = -abs(dy)          # "up" on screen
        ax.plot([x, x], [y, y + dy], color=color, lw=lw, solid_capstyle="butt", clip_on=False)
        if ylabel:
            ax.annotate(ylabel, (x, y + dy / 2), xytext=(-pad_pt, 0), textcoords="offset points",
                        ha="right", va="center", rotation=90, fontsize=fs, color=color)
    if hide_axes:
        ax.set_axis_off()


def event_lines(ax, xs, labels=None, color=None, ls=(0, (2, 2)), lw=0.6, top=True,
                fontsize=None):
    """Vertical dashed event markers (stimulus on, go cue, reward) labelled above the axes."""
    tr = blended_transform_factory(ax.transData, ax.transAxes)
    fs = fontsize or ax.xaxis.label.get_fontsize() * 0.9
    color = color or _muted(0.55)
    for i, x in enumerate(np.atleast_1d(xs)):
        ax.axvline(x, color=color, ls=ls, lw=lw, zorder=0.5)
        if labels is not None:
            ax.text(x, 1.01 if top else -0.02, labels[i], transform=tr, ha="center",
                    va="bottom" if top else "top", fontsize=fs, color=color)


def shade(ax, x0, x1, color=None, label=None, alpha=1.0, fontsize=None, text_color=None):
    """Background epoch shading (e.g., stimulus period) with optional top label."""
    color = color or _muted(0.08)
    text_color = text_color or _muted(0.6)
    ax.axvspan(x0, x1, color=color, alpha=alpha, lw=0, zorder=0)
    if label:
        tr = blended_transform_factory(ax.transData, ax.transAxes)
        ax.text((x0 + x1) / 2, 1.01, label, transform=tr, ha="center", va="bottom",
                fontsize=fontsize or ax.xaxis.label.get_fontsize() * 0.9, color=text_color)


def slim_colorbar(fig, mappable, ax, label=None, width=0.045, pad=0.04, length=0.7,
                  loc="right", ticks=None, **kw):
    """Thin, short colorbar attached to `ax` as an inset (moves with the axes under
    constrained layout). width/pad/length are fractions of the axes size."""
    if loc == "right":
        bounds = [1 + pad, (1 - length) / 2, width, length]
        orient = "vertical"
    else:  # top
        bounds = [(1 - length) / 2, 1 + pad, length, width]
        orient = "horizontal"
    cax = ax.inset_axes(bounds)
    cb = fig.colorbar(mappable, cax=cax, orientation=orient, ticks=ticks, **kw)
    cb.outline.set_visible(False)
    cax.tick_params(length=1.5, width=0.4, pad=1.5)
    if label:
        cb.set_label(label, labelpad=2)
    if orient == "horizontal":
        cax.xaxis.set_ticks_position("top")
        cax.xaxis.set_label_position("top")
    return cb


def value_labels(ax, bars, fmt="{:.2g}", inside=False, color=None, fontsize=None, pad_pt=2):
    """Write values on bars; inside=True picks white/dark ink by contrast."""
    fs = fontsize or ax.xaxis.label.get_fontsize() * 0.9
    for b in bars:
        h = b.get_height()
        x = b.get_x() + b.get_width() / 2
        if inside:
            ax.annotate(fmt.format(h), (x, h), xytext=(0, -pad_pt), textcoords="offset points",
                        ha="center", va="top", fontsize=fs,
                        color=color or C.ink_on(C.to_hex(b.get_facecolor()[:3])))
        else:
            ax.annotate(fmt.format(h), (x, h), xytext=(0, pad_pt), textcoords="offset points",
                        ha="center", va="bottom", fontsize=fs, color=color or _fg())
