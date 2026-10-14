"""Journal-exact figure sizes, multi-panel layouts and panel letters.

    fig, axd = layout.figure("nature", width="double", height_mm=110,
                             mosaic="AAB;CDE")          # subplot_mosaic string/list
    layout.label_panels(fig, axd)                        # a, b, c ... in venue style
"""
from __future__ import annotations

import string

import matplotlib.pyplot as plt
from matplotlib.transforms import ScaledTranslation

MM = 1 / 25.4  # inches per mm

# Venue specs. widths in mm at final print size; fonts in pt at final size.
# label_case: 'lower' (a, b) | 'upper' (A, B); label_weight: 'bold' | 'normal'.
# Sources: see references/journal-specs.md (each venue's author guidelines).
VENUES: dict[str, dict] = {
    # Nature (main journal): 89 / 120-136 / 183 mm; text 5-7 pt; labels 8 pt bold lowercase;
    # strokes 0.25-1 pt; figure guide max height 170 mm (page depth 247 mm).
    "nature": dict(widths_mm={"single": 89, "1.5": 120, "1.5w": 136, "double": 183},
                   height_max_mm=170, font_min=5, font_max=7, font_base=7, font_tick=6,
                   label_size=8, label_case="lower", label_weight="bold", line_min=0.25,
                   line_max=1.0, gray_ok=True),
    # Nature research journals (Nat Neurosci, Nat Mach Intell, Nat Hum Behav): 88 / 180 mm
    "nature-research": dict(widths_mm={"single": 88, "double": 180}, height_max_mm=225,
                            font_min=5, font_max=7, font_base=7, font_tick=6, label_size=8,
                            label_case="lower", label_weight="bold", line_min=0.25,
                            line_max=1.0),
    # Nature Communications: 88 / 180 mm; labels lowercase bold, SAME size as other text;
    # thinnest line >= 1 pt (!)
    "ncomms": dict(widths_mm={"single": 88, "double": 180}, height_max_mm=225, font_min=5,
                   font_max=7, font_base=7, font_tick=6, label_size=7, label_case="lower",
                   label_weight="bold", line_min=1.0),
    # Cell Press (Cell, Neuron, Cell Reports, Current Biology): 85 / 114 / 174 mm;
    # Arial only, 6-8 pt; capital panel letters; strokes 0.5-1.5 pt; max ~200 mm tall
    "cell": dict(widths_mm={"single": 85, "1.5": 114, "double": 174}, height_max_mm=200,
                 font_min=6, font_max=8, font_base=7, font_tick=6, label_size=9,
                 label_case="upper", label_weight="bold", line_min=0.5, line_max=1.5,
                 arial_only=True),
    # Science / Science Advances (2026): 90 / <=144 / 184 mm; Myriad-like sans, 6-8 pt,
    # labels 9 pt bold capitals; min stroke 0.5 pt (web) / 0.28 (Sci Adv); no minor ticks
    "science": dict(widths_mm={"single": 90, "1.5": 144, "double": 184}, height_max_mm=199,
                    font_min=6, font_max=8, font_base=7, font_tick=6, label_size=9,
                    label_case="upper", label_weight="bold", line_min=0.5, no_minor=True),
    # eLife: >= 100 mm (single), >= 200 mm (full width) at >= 300 dpi
    "elife": dict(widths_mm={"single": 100, "double": 200}, height_max_mm=240, font_min=6,
                  font_max=10, font_base=7, font_tick=6, label_size=9, label_case="upper",
                  label_weight="bold", line_min=0.5),
    # PNAS: small ~90, medium ~110-114, large ~178-180 mm; text 6-12 pt; axes start at 0
    "pnas": dict(widths_mm={"single": 87, "1.5": 114, "double": 178}, height_max_mm=220,
                 font_min=6, font_max=12, font_base=7, font_tick=6, label_size=9,
                 label_case="upper", label_weight="bold", line_min=0.5),
    # J Neurosci: max 85 / 116 / 176 mm; TIFF/EPS; no top/right spines; no two-bar graphs
    "jneurosci": dict(widths_mm={"single": 85, "1.5": 116, "double": 176}, height_max_mm=230,
                      font_min=6, font_max=10, font_base=7, font_tick=6, label_size=9,
                      label_case="upper", label_weight="bold", line_min=0.5),
    # PLOS Comp Biol: 66.8 min, 132 text column, 190.5 max; Arial 8-12 pt; TIFF/EPS only
    "plos": dict(widths_mm={"single": 132, "double": 190.5, "min": 66.8}, height_max_mm=222,
                 font_min=8, font_max=12, font_base=8, font_tick=8, label_size=10,
                 label_case="upper", label_weight="bold", line_min=0.5, arial_only=True),
    # ML venues: NeurIPS/ICLR textwidth 5.5 in; ICML 3.25 / 6.75 in. Body Times 10 pt,
    # captions 9 pt -> figure text 7-9 pt reads as the same size as captions.
    "neurips": dict(widths_mm={"single": 139.7, "half": 67.5, "third": 44.5},
                    height_max_mm=228, font_min=6, font_max=10, font_base=8, font_tick=7,
                    label_size=9, label_case="lower", label_weight="bold", line_min=0.5),
    "icml": dict(widths_mm={"single": 82.55, "double": 171.45}, height_max_mm=228,
                 font_min=6, font_max=10, font_base=8, font_tick=7, label_size=9,
                 label_case="lower", label_weight="bold", line_min=0.5),
    # Non-print targets (canvases; text sizes for legibility at viewing distance)
    "poster": dict(widths_mm={"single": 250, "double": 520}, height_max_mm=600, font_min=18,
                   font_max=60, font_base=24, font_tick=20, label_size=32, label_case="upper",
                   label_weight="bold", line_min=1.5),
    "slide": dict(widths_mm={"full": 300, "two-thirds": 200, "half": 145},
                  height_max_mm=169, font_min=12, font_max=40, font_base=16, font_tick=14,
                  label_size=18, label_case="lower", label_weight="bold", line_min=1.0),
    # Cell Press graphical abstract: 1200 x 1200 px @ 300 dpi = 101.6 mm square, Arial 8-12 pt,
    # no data, reads top->bottom or left->right
    "graphical-abstract": dict(widths_mm={"single": 101.6}, height_max_mm=101.6, font_min=8,
                               font_max=12, font_base=10, font_tick=9, label_size=12,
                               label_case="upper", label_weight="bold", line_min=0.75),
    "web": dict(widths_mm={"single": 160, "double": 240}, height_max_mm=400, font_min=8,
                font_max=16, font_base=10, font_tick=9, label_size=11, label_case="lower",
                label_weight="bold", line_min=0.5),
}
for _alias, _base in {"nature-neuroscience": "nature-research", "nn": "nature-research",
                      "nmi": "nature-research", "nhb": "nature-research",
                      "neuron": "cell", "current-biology": "cell", "cell-reports": "cell",
                      "science-advances": "science", "ploscb": "plos", "iclr": "neurips",
                      "biorxiv": "nature"}.items():
    VENUES[_alias] = VENUES[_base]


def width_mm(target="nature", width="single") -> float:
    if isinstance(width, (int, float)):
        return float(width)
    return VENUES[target]["widths_mm"][width]


def figsize(target="nature", width="single", height_mm=None, aspect=None):
    """(w, h) in inches. Give height_mm, or aspect = height/width (default 0.75)."""
    w = width_mm(target, width)
    h = height_mm if height_mm is not None else w * (aspect if aspect else 0.75)
    return w * MM, h * MM


def figure(target="nature", width="single", height_mm=None, aspect=None, mosaic=None,
           nrows=1, ncols=1, width_ratios=None, height_ratios=None, hspace=None,
           wspace=None, pad_mm=1.0, sharex=False, sharey=False, subplot_kw=None,
           per_subplot_kw=None, **kw):
    """Create a figure at the exact journal width with constrained layout.

    mosaic: subplot_mosaic spec ("AB;CC" or nested lists; '.' = empty) ->
            returns (fig, dict_of_axes). Otherwise returns (fig, axes) like subplots.
    Spacing (hspace/wspace) are fractions as in constrained layout; pad_mm is the
    outer padding.
    """
    fig = plt.figure(figsize=figsize(target, width, height_mm, aspect), layout="constrained",
                     **kw)
    fig._sciplot_target = target
    le = fig.get_layout_engine()
    le.set(w_pad=pad_mm * MM, h_pad=pad_mm * MM,
           hspace=0.04 if hspace is None else hspace, wspace=0.04 if wspace is None else wspace)
    gs_kw = {}
    if width_ratios is not None:
        gs_kw["width_ratios"] = width_ratios
    if height_ratios is not None:
        gs_kw["height_ratios"] = height_ratios
    if mosaic is not None:
        axd = fig.subplot_mosaic(mosaic, gridspec_kw=gs_kw or None, sharex=sharex,
                                 sharey=sharey, subplot_kw=subplot_kw,
                                 per_subplot_kw=per_subplot_kw)
        return fig, axd
    axs = fig.subplots(nrows, ncols, gridspec_kw=gs_kw or None, sharex=sharex,
                       sharey=sharey, subplot_kw=subplot_kw, squeeze=True)
    return fig, axs


def panel_letters(n, case="lower"):
    s = string.ascii_lowercase if case == "lower" else string.ascii_uppercase
    return list(s[:n])


def label_panels(fig, axes, labels=None, target=None, dx_mm=0.0, dy_mm=0.0,
                 size=None, weight=None, case=None, loc="outside", color=None, **kw):
    """Add panel letters at each axes' top-left corner in the venue style.

    axes: dict (from mosaic; keys used as labels if they're single letters) or list.
    loc='outside' puts the letter left of the y-tick labels (aligned across a column
    via the tight bbox); 'inside' puts it at the axes corner.
    Letters are aligned to the axes *tight bbox* left edge so they line up even when
    y-labels differ.
    """
    spec = VENUES.get(target or getattr(fig, "_sciplot_target", "nature"), VENUES["nature"])
    size = size or spec["label_size"]
    weight = weight or spec["label_weight"]
    case = case or spec["label_case"]
    if isinstance(axes, dict):
        keys = list(axes.keys())
        axes_list = [axes[k] for k in keys]
        if labels is None:
            labels = [k if len(str(k)) == 1 else None for k in keys]
            if any(l is None for l in labels):
                labels = panel_letters(len(keys), case)
    else:
        axes_list = list(getattr(axes, "flat", axes))
        labels = labels or panel_letters(len(axes_list), case)
    labels = [l.lower() if case == "lower" else l.upper() for l in labels]
    fig.canvas.draw()  # finalize layout so tight bboxes are right
    r = fig.canvas.get_renderer()
    inv = fig.transFigure.inverted()
    items = [(ax, lab) for ax, lab in zip(axes_list, labels) if lab is not None]
    # row alignment: axes whose tops are within 2 mm share the highest tight-bbox top
    tops = {}
    if loc == "outside":
        fh = fig.get_size_inches()[1]
        for ax, _ in items:
            tops[ax] = inv.transform(ax.get_tightbbox(r).corners()[1])[1]  # (x0, y1)
        def row_key(a):
            try:
                ss = a.get_subplotspec()
                return ("gs", id(ss.get_gridspec()), ss.rowspan.start)
            except AttributeError:
                return ("y", round(a.get_position().y1 * fh * 25.4 / 2))
        for ax, _ in items:
            row = [b for b, _ in items if row_key(b) == row_key(ax)]
            tops[ax] = max(tops[b] for b in row)
    out = []
    for ax, lab in items:
        if loc == "outside":
            # left edge of the panel's tight bbox (includes y-label), top of its row
            tb = ax.get_tightbbox(r)
            x_fig = inv.transform((tb.x0, tb.y1))[0]
            off = ScaledTranslation(dx_mm * MM, dy_mm * MM, fig.dpi_scale_trans)
            t = fig.text(max(x_fig, 0.002), min(tops[ax], 0.998), lab,
                         transform=fig.transFigure + off, ha="left", va="top",
                         fontsize=size, weight=weight, color=color, **kw)
            _clear_title(fig, ax, t, r)
        else:
            off = ScaledTranslation(dx_mm * MM, dy_mm * MM, fig.dpi_scale_trans)
            t = ax.text(0, 1, lab, transform=ax.transAxes + off, ha="right", va="bottom",
                        fontsize=size, weight=weight, color=color, **kw)
        t._sciplot_label = True
        out.append(t)
    return out


def _clear_title(fig, ax, letter, renderer, gap_mm=1.2):
    """If a left-aligned title starts under the panel letter, nudge the title right."""
    title = getattr(ax, "_left_title", None)
    if title is None or not title.get_text():
        return
    lb = letter.get_window_extent(renderer)
    tb = title.get_window_extent(renderer)
    if tb.x0 < lb.x1 and tb.y1 > lb.y0 and tb.y0 < lb.y1:
        shift = (lb.x1 - tb.x0) / fig.dpi + gap_mm * MM
        title.set_transform(title.get_transform() + ScaledTranslation(shift, 0, fig.dpi_scale_trans))


def align_labels(fig):
    """Align x/y axis labels across panels (call before saving)."""
    fig.align_xlabels()
    fig.align_ylabels()
    if hasattr(fig, "align_titles"):
        fig.align_titles()


def offset_spines(ax, pts=3, which=("left", "bottom")):
    """Detach spines from the data (modern 'floating axes' look)."""
    for s in which:
        ax.spines[s].set_position(("outward", pts))


def range_frame(ax, x=None, y=None):
    """Tufte range frame: spines span only the data range (pass data arrays)."""
    import numpy as np
    if x is not None:
        ax.spines["bottom"].set_bounds(np.nanmin(x), np.nanmax(x))
    if y is not None:
        ax.spines["left"].set_bounds(np.nanmin(y), np.nanmax(y))


def trim_spines(ax):
    """Spines end at the first/last major tick (clean, Nature-like)."""
    xt = [t for t in ax.get_xticks() if ax.get_xlim()[0] - 1e-9 <= t <= ax.get_xlim()[1] + 1e-9]
    yt = [t for t in ax.get_yticks() if ax.get_ylim()[0] - 1e-9 <= t <= ax.get_ylim()[1] + 1e-9]
    if len(xt) > 1:
        ax.spines["bottom"].set_bounds(xt[0], xt[-1])
    if len(yt) > 1:
        ax.spines["left"].set_bounds(yt[0], yt[-1])


def max_ticks(ax, n=4, axis="both"):
    from matplotlib.ticker import MaxNLocator
    if axis in ("x", "both"):
        ax.xaxis.set_major_locator(MaxNLocator(n))
    if axis in ("y", "both"):
        ax.yaxis.set_major_locator(MaxNLocator(n))


def no_axes(ax):
    ax.set_axis_off()


def inset(ax, bounds=(0.6, 0.6, 0.38, 0.38), **kw):
    """Inset axes in axes-fraction bounds (x0, y0, w, h)."""
    return ax.inset_axes(bounds, **kw)
