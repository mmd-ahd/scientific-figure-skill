"""Recipes for common comp-neuro / NeuroAI panel types.

Each function draws into a given `ax` and returns the main artist(s); styling
comes from the active sciplot style. Conventions borrowed from exemplar papers
(IBL brain-wide map, Rastermap, CEBRA, MICrONS, rsatoolbox):
- grey for context, color for signal; one hue family per variable;
- rasters/heatmaps: no axes, L-shaped scale bars, events as thin lines/spans;
- embeddings: tiny semi-transparent points, color = behavioral variable;
- summary panels: every run/subject as a dot + a bold summary mark.
"""
from __future__ import annotations

import numpy as np
import matplotlib as mpl
from matplotlib.collections import LineCollection

from . import color as C
from .annotate import scale_bar


# ------------------------------------------------------------- time series

def mean_ci(ax, x, Y, color, label=None, ci="sem", alpha=0.22, lw=None, band=True,
            z=2, **kw):
    """Mean line + shaded band. Y: (n_trials, n_time). ci: 'sem' | 'sd' | 95 (bootstrap %).
    Band uses a pre-mixed tint (not alpha) so overlaps stay clean in vector output."""
    Y = np.asarray(Y, float)
    m = np.nanmean(Y, 0)
    if ci == "sem":
        e = np.nanstd(Y, 0, ddof=1) / np.sqrt(np.sum(np.isfinite(Y), 0))
        lo, hi = m - e, m + e
    elif ci == "sd":
        e = np.nanstd(Y, 0, ddof=1)
        lo, hi = m - e, m + e
    else:
        rng = np.random.default_rng(0)
        boots = np.array([np.nanmean(Y[rng.integers(0, len(Y), len(Y))], 0) for _ in range(1000)])
        lo, hi = np.nanpercentile(boots, [(100 - ci) / 2, 100 - (100 - ci) / 2], 0)
    if band:
        ax.fill_between(x, lo, hi, color=color, alpha=alpha, lw=0, zorder=z - 0.5)
    (ln,) = ax.plot(x, m, color=color, lw=lw, label=label, zorder=z, **kw)
    return ln


def gradient_line(ax, x, y, values=None, cmap="cmr.ember", lw=1.2, norm=None, **kw):
    """Line whose color encodes a third variable (e.g., time along a trajectory)."""
    pts = np.column_stack([x, y]).reshape(-1, 1, 2)
    segs = np.concatenate([pts[:-1], pts[1:]], 1)
    values = np.linspace(0, 1, len(x)) if values is None else np.asarray(values)
    lc = LineCollection(segs, cmap=_cm(cmap), norm=norm, lw=lw, capstyle="round",
                        joinstyle="round", **kw)
    lc.set_array(values[:-1])
    ax.add_collection(lc)
    ax.autoscale_view()
    return lc


def _lw(lw, k=1.0):
    return lw if lw is not None else mpl.rcParams["lines.linewidth"] * k


def _ms(ms, k=1.0):
    return ms if ms is not None else mpl.rcParams["lines.markersize"] * k


def _cm(cmap):
    if isinstance(cmap, str):
        try:
            return mpl.colormaps[cmap]
        except KeyError:
            from .palettes import cmap as _get
            return _get(cmap)
    return cmap


# ------------------------------------------------------------- spikes

def raster(ax, spikes, color="0.1", lw=0.5, height=0.8, colors=None, t0=None, t1=None,
           rasterized=True):
    """Spike raster. spikes: list of arrays (one per trial/neuron).
    colors: optional per-row colors (e.g., by condition)."""
    segs, cols = [], []
    for i, st in enumerate(spikes):
        st = np.asarray(st)
        segs.extend([[(t, i - height / 2), (t, i + height / 2)] for t in st])
        if colors is not None:
            cols.extend([colors[i]] * len(st))
    lc = LineCollection(segs, colors=cols if colors is not None else color, lw=lw,
                        rasterized=rasterized)
    ax.add_collection(lc)
    ax.set_ylim(-0.5 - (1 - height), len(spikes) - 0.5 + (1 - height))
    if t0 is not None:
        ax.set_xlim(t0, t1)
    else:
        ax.autoscale_view(scaley=False)
    ax.invert_yaxis()
    return lc


def psth(spikes, edges, smooth_sd=None):
    """Trial-averaged firing rate (Hz) from spike times; optional Gaussian smoothing (bins)."""
    counts = np.array([np.histogram(s, edges)[0] for s in spikes], float)
    rate = counts / np.diff(edges)[None]
    if smooth_sd:
        k = np.arange(-4 * smooth_sd, 4 * smooth_sd + 1)
        g = np.exp(-0.5 * (k / smooth_sd) ** 2)
        g /= g.sum()
        rate = np.array([np.convolve(r, g, "same") for r in rate])
    return rate


def activity_heatmap(ax, A, t=None, cmap="gray_r", vmin=None, vmax=None, zscore=False,
                     sort="peak", scalebar=None, rasterized=True, **kw):
    """Neurons x time heatmap (Rastermap / sequence style), no axes.
    sort: 'peak' (by time of max), None, or an index array.
    zscore=True -> diverging RdBu_r with symmetric limits.
    scalebar: dict(dx=..., xlabel='1 s', dy=..., ylabel='100 neurons')."""
    A = np.asarray(A, float)
    if zscore:
        A = (A - A.mean(1, keepdims=True)) / (A.std(1, keepdims=True) + 1e-9)
        cmap = "RdBu_r" if cmap == "gray_r" else cmap
        lim = vmax or np.nanpercentile(np.abs(A), 99)
        vmin, vmax = -lim, lim
    if isinstance(sort, str) and sort == "peak":
        A = A[np.argsort(np.argmax(A, 1))]
    elif sort is not None and not isinstance(sort, str):
        A = A[np.asarray(sort)]
    t = np.arange(A.shape[1]) if t is None else np.asarray(t)
    im = ax.imshow(A, aspect="auto", cmap=_cm(cmap), vmin=vmin, vmax=vmax, interpolation="nearest",
                   extent=(t[0], t[-1], A.shape[0], 0), rasterized=rasterized, **kw)
    if scalebar:
        sb = dict(scalebar)
        span = t[-1] - t[0]
        x0 = sb.pop("x", t[0] - 0.03 * span)
        y0 = sb.pop("y", A.shape[0] * 1.03)
        ax.set_xlim(t[0] - 0.035 * span, t[-1])
        ax.set_ylim(A.shape[0] * 1.04, 0)
        scale_bar(ax, x0, y0, **sb)
    else:
        ax.set_axis_off()
    return im


# ------------------------------------------------------------- representations

def rdm(ax, D, labels=None, cmap="cmc.batlow", vmin=None, vmax=None, groups=None,
        group_colors=None, triangle=None, gap_lw=0.0, colorbar=False, label_fs=None, **kw):
    """Representational dissimilarity matrix.
    groups: list of (start, stop, name) blocks -> colored bars on left/top edges.
    triangle: None | 'lower' | 'upper' to mask the redundant half."""
    D = np.array(D, float)
    if triangle:
        mask = np.triu(np.ones_like(D, bool), 1) if triangle == "lower" else np.tril(np.ones_like(D, bool), -1)
        D = np.ma.array(D, mask=mask)
    im = ax.imshow(D, cmap=_cm(cmap), vmin=vmin, vmax=vmax, interpolation="nearest", **kw)
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    n = D.shape[0]
    if labels is not None and len(labels) <= 30:
        ax.set_xticks(range(n), labels, rotation=90, fontsize=label_fs)
        ax.set_yticks(range(n), labels, fontsize=label_fs)
        ax.tick_params(length=0, pad=1.5)
    if groups:
        gc = group_colors or mpl.rcParams["axes.prop_cycle"].by_key()["color"]
        w = 0.025 * n
        for k, (a, b, name) in enumerate(groups):
            col = gc[k % len(gc)]
            ax.add_patch(mpl.patches.Rectangle((-0.5 - 1.6 * w, a - 0.5), w, b - a, fc=col,
                                               ec="none", clip_on=False))
            ax.add_patch(mpl.patches.Rectangle((a - 0.5, -0.5 - 1.6 * w), b - a, w, fc=col,
                                               ec="none", clip_on=False))
            ax.text(-0.5 - 2.2 * w, (a + b) / 2 - 0.5, name, ha="right", va="center",
                    color=C.ensure_contrast(col, C.to_hex(ax.figure.get_facecolor()[:3]), 3.0),
                    fontsize=label_fs, weight="medium")
            if gap_lw:
                ax.axhline(b - 0.5, color="white", lw=gap_lw)
                ax.axvline(b - 0.5, color="white", lw=gap_lw)
    return im


def trajectories(ax, X, color=None, cmap=None, lw=None, start_marker=True, end_marker=True,
                 ms=None, alpha=1.0, label=None, three_d=False, fade=False):
    """Latent trajectory (n_time, 2|3). color: fixed hue; cmap: color by time.
    fade=True: tint early timepoints toward the background (time without a colorbar).
    Marks start (open circle) and end (filled) — standard in population-dynamics papers."""
    X = np.asarray(X)
    lw, ms = _lw(lw), _ms(ms, 0.85)
    if cmap is not None and not three_d:
        art = gradient_line(ax, X[:, 0], X[:, 1], cmap=cmap, lw=lw, alpha=alpha)
        c_start, c_end = _cm(cmap)(0.0), _cm(cmap)(1.0)
    elif fade and not three_d:
        bg = C.to_hex(ax.get_facecolor()[:3])
        cols = [C.mix(bg, color, t) for t in np.linspace(0.25, 1, 32)]
        art = gradient_line(ax, X[:, 0], X[:, 1], cmap=mpl.colors.ListedColormap(cols), lw=lw)
        c_start, c_end = cols[0], color
    else:
        args = (X[:, 0], X[:, 1], X[:, 2]) if three_d else (X[:, 0], X[:, 1])
        (art,) = ax.plot(*args, color=color, lw=lw, alpha=alpha, label=label,
                         solid_capstyle="round", solid_joinstyle="round")
        c_start = c_end = color
    p0 = X[0] if not three_d else X[0]
    if start_marker:
        ax.plot(*p0[: 3 if three_d else 2], "o", ms=ms, mfc=C.to_hex(ax.get_facecolor()[:3]),
                mec=c_start, mew=0.8, zorder=5)
    if end_marker:
        ax.plot(*X[-1][: 3 if three_d else 2], "o", ms=ms, color=c_end, mec="none", zorder=5)
    return art


def style_3d(ax, pane_color=None, grid=False, elev=22, azim=-55, ticks=False, labels=None):
    """Clean 3D axes for latent spaces: no panes/grid, thin axis lines, set view."""
    for a in (ax.xaxis, ax.yaxis, ax.zaxis):
        a.set_pane_color((1, 1, 1, 0) if pane_color is None else pane_color)
        a.line.set_linewidth(0.5)
        a._axinfo["grid"]["linewidth"] = 0.3
    ax.grid(grid)
    ax.view_init(elev=elev, azim=azim)
    if not ticks:
        ax.set_xticks([]), ax.set_yticks([]), ax.set_zticks([])
    if labels:
        ax.set_xlabel(labels[0], labelpad=-12), ax.set_ylabel(labels[1], labelpad=-12)
        ax.set_zlabel(labels[2], labelpad=-12)


def embedding(ax, Z, c=None, cmap="cmc.batlow", s=1.5, alpha=0.5, grey_bg=None,
              rasterized=True, **kw):
    """2-D embedding scatter (UMAP/t-SNE/CEBRA/PCA). Tiny semi-transparent points.
    grey_bg: optional (N,2) context points drawn first in light grey."""
    if grey_bg is not None:
        ax.scatter(grey_bg[:, 0], grey_bg[:, 1], s=s, c="0.85", lw=0, rasterized=rasterized)
    sc = ax.scatter(Z[:, 0], Z[:, 1], c=c, cmap=_cm(cmap) if c is not None and not isinstance(c, str) else None,
                    s=s, alpha=alpha, lw=0, rasterized=rasterized, **kw)
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    return sc


def axis_arrows(ax, xlabel="Dim 1", ylabel="Dim 2", length=0.16, color=None, lw=0.6,
                fontsize=None):
    """Small L-shaped axis arrows in the lower-left corner (PCA/UMAP panels without axes)."""
    from .annotate import _muted
    color = color or _muted(0.6)
    kw = dict(arrowprops=dict(arrowstyle="-|>,head_length=0.35,head_width=0.18", lw=lw,
                              color=color, shrinkA=0, shrinkB=0), xycoords="axes fraction",
              annotation_clip=False)
    ax.annotate("", (length, 0), (0, 0), **kw)
    ax.annotate("", (0, length), (0, 0), **kw)
    fs = fontsize or ax.xaxis.label.get_fontsize() * 0.85
    ax.annotate(xlabel, (0, 0), xytext=(0, -2), textcoords="offset points",
                xycoords="axes fraction", ha="left", va="top", fontsize=fs, color=color)
    ax.annotate(ylabel, (0, 0), xytext=(-2, 0), textcoords="offset points",
                xycoords="axes fraction", ha="right", va="bottom", rotation=90, fontsize=fs,
                color=color)


# ------------------------------------------------------------- summaries

def dots_and_summary(ax, groups, colors, labels=None, summary="mean", err="sem",
                     jitter=0.08, s=None, alpha=0.65, bar_w=0.32, lw=None, paired=False,
                     pair_color="0.82", seed=0):
    """'Show the data' plot: every observation as a dot + mean/median tick and error.
    paired=True links observations across groups (same subject) with thin grey lines."""
    rng = np.random.default_rng(seed)
    lw = _lw(lw, 1.1)
    s = s if s is not None else _ms(None) ** 2 * 0.5
    xs_all = []
    for i, (g, col) in enumerate(zip(groups, colors)):
        g = np.asarray(g, float)
        xs = i + rng.uniform(-jitter, jitter, len(g)) if not paired else np.full(len(g), i, float)
        xs_all.append(xs)
        ax.scatter(xs, g, s=s, color=C.lighten(col, 0.25), alpha=alpha, lw=0, zorder=3)
        m = np.nanmedian(g) if summary == "median" else np.nanmean(g)
        if err == "sem":
            e = np.nanstd(g, ddof=1) / np.sqrt(np.sum(np.isfinite(g)))
        elif err == "sd":
            e = np.nanstd(g, ddof=1)
        else:
            e = 0
        ax.plot([i - bar_w / 2, i + bar_w / 2], [m, m], color=C.darken(col, 0.15), lw=lw * 1.4,
                solid_capstyle="round", zorder=4)
        if e:
            ax.plot([i, i], [m - e, m + e], color=C.darken(col, 0.15), lw=lw, zorder=4,
                    solid_capstyle="round")
    if paired:
        G = np.array(groups, float)
        for j in range(G.shape[1]):
            ax.plot(range(len(groups)), G[:, j], color=pair_color, lw=0.4, zorder=2)
    ax.set_xticks(range(len(groups)), labels if labels is not None else [""] * len(groups))
    ax.set_xlim(-0.6, len(groups) - 0.4)
    return xs_all


def _kde(d, ys, bw=None):
    """Gaussian KDE (scipy.stats.gaussian_kde semantics; numpy-only fallback).
    bw: None/'scott' | 'silverman' | scalar factor."""
    try:
        from scipy.stats import gaussian_kde
        return gaussian_kde(d, bw_method=bw)(ys)
    except ImportError:
        n = len(d)
        if bw is None or bw == "scott":
            f = n ** (-1 / 5)
        elif bw == "silverman":
            f = (n * 3 / 4) ** (-1 / 5)
        else:
            f = float(bw)
        h = max(np.std(d, ddof=1) * f, 1e-12)
        return np.exp(-0.5 * ((ys[:, None] - d[None]) / h) ** 2).sum(1)


def half_violin(ax, data, pos, color, width=0.4, side="right", alpha=0.35, lw=0.6, bw=None):
    """One-sided KDE (for raincloud plots: half-violin + jittered dots + box)."""
    d = np.asarray(data, float)
    d = d[np.isfinite(d)]
    ys = np.linspace(d.min(), d.max(), 200)
    v = _kde(d, ys, bw)
    v = v / v.max() * width
    sgn = 1 if side == "right" else -1
    ax.fill_betweenx(ys, pos, pos + sgn * v, color=C.lighten(color, 1 - alpha), lw=0, zorder=2)
    ax.plot(pos + sgn * v, ys, color=color, lw=lw, zorder=2.5)


def raincloud(ax, groups, colors, labels=None, horizontal=False, s=None, seed=0):
    """Raincloud: half violin + box (thin) + jittered points (Allen et al. 2019)."""
    rng = np.random.default_rng(seed)
    s = s if s is not None else _ms(None) ** 2 * 0.35
    for i, (g, col) in enumerate(zip(groups, colors)):
        g = np.asarray(g, float)
        half_violin(ax, g, i + 0.06, col, width=0.38)
        q1, med, q3 = np.nanpercentile(g, [25, 50, 75])
        ax.plot([i, i], [q1, q3], color=C.darken(col, 0.2), lw=2.4, solid_capstyle="round", zorder=4)
        ax.plot(i, med, "o", ms=3, mfc="white", mec=C.darken(col, 0.2), mew=0.8, zorder=5)
        ax.scatter(i - 0.12 - rng.uniform(0, 0.16, len(g)), g, s=s, color=col, alpha=0.6, lw=0, zorder=3)
    ax.set_xticks(range(len(groups)), labels if labels is not None else [""] * len(groups))
    ax.set_xlim(-0.6, len(groups) - 0.3)


def layer_profile(ax, layers, scores, color, label=None, err=None, ceiling=None,
                  ceiling_label="noise ceiling", marker="o", ms=None, lw=None):
    """Model–brain alignment across layers (Brain-Score / encoding R² style).
    ceiling: (lo, hi) or float drawn as a grey band/line."""
    from .annotate import _muted
    lw, ms = _lw(lw, 1.1), _ms(ms)
    x = np.arange(len(layers))
    if ceiling is not None:
        if np.ndim(ceiling):
            ax.axhspan(*ceiling, color=_muted(0.1), lw=0, zorder=0)
        else:
            ax.axhline(ceiling, color=_muted(0.45), ls=(0, (3, 2)), lw=0.7, zorder=0)
        ax.text(len(layers) - 1, np.max(ceiling), ceiling_label, ha="right", va="bottom",
                fontsize=ax.xaxis.label.get_fontsize() * 0.85, color=_muted(0.6))
    if err is not None:
        ax.fill_between(x, np.asarray(scores) - err, np.asarray(scores) + err, color=color,
                        alpha=0.2, lw=0)
    (ln,) = ax.plot(x, scores, marker=marker, ms=ms, color=color, lw=lw, label=label,
                    mec=mpl.rcParams["axes.facecolor"], mew=0.6)
    ax.set_xticks(x, layers)
    return ln


def tuning_curve(ax, theta, rates, color, err=None, polar=False, lw=None, ms=None, label=None):
    """Orientation/direction tuning. polar=True expects a polar axes."""
    lw, ms = _lw(lw, 1.1), _ms(ms, 0.85)
    theta = np.asarray(theta)
    rates = np.asarray(rates)
    if polar:
        th = np.r_[theta, theta[:1]]
        r = np.r_[rates, rates[:1]]
        ax.fill(th, r, color=C.lighten(color, 0.75), lw=0)
        (ln,) = ax.plot(th, r, color=color, lw=lw, label=label)
        return ln
    if err is not None:
        ax.errorbar(theta, rates, yerr=err, fmt="none", ecolor=color, elinewidth=0.7, capsize=0)
    (ln,) = ax.plot(theta, rates, "-o", color=color, lw=lw, ms=ms, mec="white", mew=0.5, label=label)
    return ln


def connectivity(ax, W, cmap="RdBu_r", vmax=None, ei_split=None, **kw):
    """Weight/connectivity matrix with symmetric diverging limits.
    ei_split: index where inhibitory units start -> thin separator lines."""
    W = np.asarray(W, float)
    vmax = vmax or np.nanpercentile(np.abs(W), 99)
    im = ax.imshow(W, cmap=_cm(cmap), vmin=-vmax, vmax=vmax, interpolation="nearest", **kw)
    ax.set_xticks([]), ax.set_yticks([])
    if ei_split:
        for f in (ax.axhline, ax.axvline):
            f(ei_split - 0.5, color="0.2", lw=0.5)
    return im


def learning_curves(ax, steps, runs, color, label=None, smooth=None, show_runs=True,
                    log_x=False, lw=None):
    """Training curves: thin faint individual seeds + bold mean (ML-paper style)."""
    lw = _lw(lw, 1.2)
    R = np.asarray(runs, float)
    if smooth:
        k = np.ones(smooth) / smooth
        R = np.array([np.convolve(r, k, "valid") for r in R])
        steps = np.asarray(steps)[smooth - 1:]
    if show_runs:
        for r in R:
            ax.plot(steps, r, color=C.lighten(color, 0.6, C.to_hex(ax.get_facecolor()[:3])),
                    lw=max(lw * 0.45, 0.5), zorder=1)
    (ln,) = ax.plot(steps, R.mean(0), color=color, lw=lw, label=label, zorder=2)
    if log_x:
        ax.set_xscale("log")
    return ln


# ------------------------------------------------------------- brain-viz presets
# Thin wrappers that apply consistent styling to external neuro libraries.
# Each returns kwargs or acts on an existing object; import is lazy.

def nilearn_kwargs(kind="stat", dark=False, cmap=None, **over):
    """Keyword presets for nilearn.plotting functions.
    kind: 'stat' (plot_stat_map), 'glass' (plot_glass_brain), 'surf' (plot_surf_stat_map),
          'connectome' (plot_connectome)."""
    base = dict(black_bg=dark, annotate=True, draw_cross=False, colorbar=True)
    if kind == "stat":
        base.update(cmap=cmap or "cmc.vik", symmetric_cbar=True, dim=-0.3)
    elif kind == "glass":
        base.update(cmap=cmap or "cmr.ember" if not dark else "cmr.ember", plot_abs=False,
                    alpha=0.6, symmetric_cbar=False)
    elif kind == "surf":
        base = dict(cmap=cmap or "cmc.vik", bg_on_data=True, darkness=0.5, colorbar=True)
    elif kind == "connectome":
        base = dict(node_size=12, edge_cmap=cmap or "cmc.vik", edge_kwargs=dict(linewidth=0.8),
                    black_bg=dark, colorbar=True, annotate=True)
    base.update(over)
    for k, v in list(base.items()):
        if k in ("cmap", "edge_cmap") and isinstance(v, str) and "." in v:
            base[k] = _cm(v)
    return base


def mne_topomap_kwargs(cmap="cmc.vik", **over):
    """Presets for mne.viz.plot_topomap / Evoked.plot_topomap: no contour clutter,
    small sensor dots, image limited to the sensor hull."""
    kw = dict(cmap=_cm(cmap), contours=0, sensors="k.", outlines="head", res=128,
              extrapolate="local", image_interp="cubic")
    kw.update(over)
    return kw


def normalize_text(obj, max_pt=None, min_pt=None, color=None):
    """Clamp text sizes (and optionally recolor) inside figures/axes created by external
    libraries (nilearn 'L'/'R' annotations, MNE titles...) to the active style."""
    max_pt = max_pt or mpl.rcParams["axes.labelsize"]
    min_pt = min_pt or mpl.rcParams["xtick.labelsize"]
    from matplotlib.text import Text
    for t in obj.findobj(Text):
        if getattr(t, "_sciplot_label", False):
            continue
        s = t.get_fontsize()
        if s > max_pt or s < min_pt:
            t.set_fontsize(min(max(s, min_pt), max_pt))
        if color is not None:
            t.set_color(color)
    return obj


def style_mne_figure(fig):
    """Re-apply sciplot rcParams to an MNE-created matplotlib figure (fonts/lines/spines)."""
    for ax in fig.axes:
        for sp in ("top", "right"):
            if sp in ax.spines:
                ax.spines[sp].set_visible(False)
        ax.tick_params(labelsize=mpl.rcParams["xtick.labelsize"])
    return fig


def pycortex_quickflat_kwargs(**over):
    """Presets for cortex.quickflat.make_figure (clean flatmap)."""
    kw = dict(with_curvature=True, curvature_brightness=0.5, curvature_contrast=0.25,
              with_rois=True, with_labels=False, with_sulci=False, with_colorbar=False,
              linewidth=1, linecolor=(1, 1, 1), roifill=(0, 0, 0, 0), dpi=300)
    kw.update(over)
    return kw


def pyvista_theme(dark=False, font="Inter"):
    """Configure a PyVista theme matching sciplot (for brain meshes, brainrender-like scenes).
    Use plotter.screenshot(path, transparent_background=True) and composite in matplotlib."""
    import pyvista as pv
    th = pv.themes.DocumentTheme()
    th.background = "#0E1117" if dark else "white"
    th.font.family = "arial"   # VTK only ships arial/courier/times; label in matplotlib instead
    th.font.color = "#E8E8E8" if dark else "#222222"
    th.smooth_shading = True
    th.lighting = True
    th.show_edges = False
    th.anti_aliasing = "ssaa"
    pv.set_plot_theme(th)
    return th


def image_panel(ax, img, title=None):
    """Place a rendered image (PyVista screenshot, microscopy, nilearn PNG) as a panel."""
    if isinstance(img, str):
        import matplotlib.image as mpimg
        img = mpimg.imread(img)
    ax.imshow(img, interpolation="lanczos")
    ax.set_axis_off()
    if title:
        ax.set_title(title)
    return ax
