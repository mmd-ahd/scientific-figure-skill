"""Style presets = aesthetic theme × venue target.

    import sciplot as sp
    sp.use("clean", target="nature")            # Nature-sized, modern minimal
    sp.use("editorial", target="neuron", bg="paper")
    sp.use("dark", target="slide")              # talk slides

Themes
  clean      white, thin dark-grey axes, despined, no grid — the journal default
  editorial  FT/Economist look: horizontal hairline grid, no y-spine, muted ticks,
             bold left-aligned titles; optional warm paper background
  soft       modern product look: pale panel fill + white grid, no spines
  ink        monochrome ink + one accent (use with palettes.highlight)
  paper      warm off-white (Pantone 2026 Cloud Dancer) + mocha/earth palette
  dark       dark slides/dark-mode: near-black (not pure black) bg, light text, neon/midnight
Targets: any key of layout.VENUES (nature, nature-research, ncomms, cell, neuron,
science, elife, pnas, jneurosci, plos, neurips, iclr, icml, poster, slide,
graphical-abstract, web).
"""
from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
from cycler import cycler

from . import palettes as P
from .layout import VENUES

FONTS = {
    # name -> fallback stack (first available wins)
    "inter": ["Inter", "Helvetica Neue", "Helvetica", "Arial", "Liberation Sans", "DejaVu Sans"],
    "inter-display": ["Inter Display", "Inter", "Liberation Sans", "DejaVu Sans"],
    "geist": ["Geist", "Inter", "Liberation Sans", "DejaVu Sans"],
    "plex": ["IBM Plex Sans", "Inter", "Liberation Sans", "DejaVu Sans"],
    "source": ["Source Sans 3", "Source Sans Pro", "Inter", "Liberation Sans", "DejaVu Sans"],
    "dm": ["DM Sans", "Inter", "Liberation Sans", "DejaVu Sans"],
    "arial": ["Arial", "Helvetica", "Liberation Sans", "Nimbus Sans", "DejaVu Sans"],
    "helvetica": ["Helvetica", "Nimbus Sans", "Arial", "Liberation Sans", "DejaVu Sans"],
}
MONO = ["JetBrains Mono", "IBM Plex Mono", "Geist Mono", "DejaVu Sans Mono"]

THEMES = {
    "clean": dict(bg="#FFFFFF", fg="#1F2328", axis="#3D434B", tick_label="#3D434B",
                  muted="#6B7280", grid=None, palette="sp.nature", spines=("left", "bottom")),
    "editorial": dict(bg="#FFFFFF", fg="#1F2328", axis="#2B2F36", tick_label="#5B6370",
                      muted="#6B7280", grid=("y", "#E3E1DC"), palette="sp.lab",
                      spines=("bottom",), title_weight="bold"),
    "soft": dict(bg="#FFFFFF", panel="#F4F5F8", fg="#2D3340", axis="#2D3340",
                 tick_label="#5B6370", muted="#7A8290", grid=("both", "#FFFFFF"),
                 palette="sp.aurora", spines=()),
    "ink": dict(bg="#FFFFFF", fg="#111418", axis="#111418", tick_label="#111418",
                muted="#5F6670", grid=None, palette="sp.lab", spines=("left", "bottom")),
    "paper": dict(bg="#F0EEE9", fg="#2B2420", axis="#4A403A", tick_label="#5E544D",
                  muted="#8A7F76", grid=("y", "#E2DDD4"), palette="sp.mocha",
                  spines=("bottom",)),
    "dark": dict(bg="#0E1117", fg="#E6E8EB", axis="#8B95A5", tick_label="#AEB6C2",
                 muted="#7D8796", grid=("y", "#1E2430"), palette="sp.midnight",
                 spines=("left", "bottom")),
}
BACKGROUNDS = P.BACKGROUNDS


def available_font(stack):
    from matplotlib import font_manager as fm
    have = {f.name for f in fm.fontManager.ttflist}
    for f in stack:
        if f in have:
            return f
    return "DejaVu Sans"


def rc(theme="clean", target="nature", font="auto", palette=None, bg=None, scale=1.0,
       grid=None, title_loc="left"):
    """Build an rcParams dict (does not apply it)."""
    th = dict(THEMES[theme])
    v = VENUES[target]
    if bg is not None:
        th["bg"] = BACKGROUNDS.get(bg, bg)
    if font == "auto":
        font = "arial" if v.get("arial_only") else "inter"
    stack = FONTS.get(font, [font] + FONTS["inter"])
    fam = available_font(stack)
    base = v["font_base"] * scale
    tick = v["font_tick"] * scale
    big = target in ("poster", "slide", "graphical-abstract")
    lw_axis = max(v["line_min"], 0.6 if not big else 1.2) * (scale if big else 1)
    lw_data = (1.0 if not big else 2.2) * (scale if big else 1)
    if target == "ncomms":
        lw_axis, lw_data = 1.0, 1.25
    pal = P.get(palette or th["palette"])
    r = {
        # canvas
        "figure.facecolor": th["bg"], "savefig.facecolor": th["bg"],
        "axes.facecolor": th.get("panel", th["bg"]), "figure.dpi": 150,
        "savefig.dpi": 600, "savefig.transparent": False,
        "figure.constrained_layout.use": True,
        "figure.constrained_layout.h_pad": 0.02, "figure.constrained_layout.w_pad": 0.02,
        # typography
        "font.family": "sans-serif", "font.sans-serif": [fam] + [f for f in stack if f != fam],
        "font.monospace": MONO, "font.size": base, "text.color": th["fg"],
        "axes.labelsize": base, "axes.titlesize": min(base + (0.5 if not big else 2), v["font_max"]),
        "axes.titleweight": th.get("title_weight", "medium"), "axes.titlelocation": title_loc,
        "axes.titlepad": 4 * scale, "axes.titlecolor": th["fg"],
        "axes.labelcolor": th["fg"], "axes.labelpad": 2.5 * scale, "axes.labelweight": "normal",
        "xtick.labelsize": tick, "ytick.labelsize": tick,
        "xtick.color": th["axis"], "ytick.color": th["axis"],
        "xtick.labelcolor": th["tick_label"], "ytick.labelcolor": th["tick_label"],
        "legend.fontsize": tick, "legend.title_fontsize": base, "figure.titlesize": base + 2,
        "figure.titleweight": "bold",
        "mathtext.fontset": "custom", "mathtext.rm": fam, "mathtext.it": f"{fam}:italic",
        "mathtext.bf": f"{fam}:bold", "mathtext.sf": fam, "mathtext.default": "regular",
        "axes.formatter.use_mathtext": False, "axes.unicode_minus": True,
        "axes.formatter.limits": (-3, 4),
        # axes & ticks
        "axes.linewidth": lw_axis, "axes.edgecolor": th["axis"],
        "axes.spines.top": "top" in th["spines"], "axes.spines.right": "right" in th["spines"],
        "axes.spines.left": "left" in th["spines"], "axes.spines.bottom": "bottom" in th["spines"],
        "xtick.direction": "out", "ytick.direction": "out",
        "xtick.major.size": 2.5 * (scale if big else 1) * (1.6 if big else 1),
        "ytick.major.size": 2.5 * (scale if big else 1) * (1.6 if big else 1),
        "xtick.major.width": lw_axis, "ytick.major.width": lw_axis,
        "xtick.minor.size": 1.5, "ytick.minor.size": 1.5,
        "xtick.minor.width": lw_axis * 0.8, "ytick.minor.width": lw_axis * 0.8,
        "xtick.major.pad": 2 * scale, "ytick.major.pad": 2 * scale,
        "xtick.minor.visible": False, "ytick.minor.visible": False,
        "axes.xmargin": 0.02, "axes.ymargin": 0.04, "axes.autolimit_mode": "data",
        "axes.axisbelow": True,
        # data marks
        "lines.linewidth": lw_data, "lines.markersize": 3.5 * (scale if big else 1) * (2 if big else 1),
        "lines.markeredgewidth": 0.6, "lines.solid_capstyle": "round",
        "lines.dash_capstyle": "round", "lines.dashed_pattern": (3.2, 1.8),
        "patch.linewidth": lw_axis, "patch.edgecolor": th["fg"], "patch.force_edgecolor": False,
        "hatch.linewidth": lw_axis * 0.8,
        "scatter.edgecolors": "none", "errorbar.capsize": 0,
        "boxplot.flierprops.markersize": 2,
        "image.cmap": "viridis", "image.interpolation": "nearest",
        "axes.prop_cycle": cycler(color=pal),
        # legend: frameless, compact
        "legend.frameon": False, "legend.handlelength": 1.4, "legend.handletextpad": 0.5,
        "legend.borderaxespad": 0.3, "legend.labelspacing": 0.35, "legend.columnspacing": 1.0,
        "legend.markerscale": 1.0, "legend.labelcolor": th["fg"],
        # grid (off unless theme/arg turns it on)
        "axes.grid": False, "grid.linewidth": lw_axis * 0.8, "grid.color": "#E6E8EB",
        "grid.linestyle": "-", "grid.alpha": 1.0,
        # export
        "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
        "path.simplify": True,
    }
    g = grid if grid is not None else th["grid"]
    if g:
        which, col = (g, "#E6E8EB") if isinstance(g, str) else g
        r.update({"axes.grid": True, "axes.grid.axis": which, "grid.color": col})
        if theme in ("editorial", "paper", "dark"):
            r.update({"ytick.major.size": 0, "ytick.major.pad": 3 * scale})
    if v.get("no_minor"):
        r.update({"xtick.minor.visible": False, "ytick.minor.visible": False})
    if theme == "dark":
        r.update({"image.cmap": "magma", "patch.edgecolor": th["fg"]})
    return r


def use(theme="clean", target="nature", **kw):
    """Apply a style globally (and register bank colormaps as 'sp.*'). Returns rc dict."""
    r = rc(theme, target, **kw)
    mpl.rcParams.update(r)
    try:
        import cmcrameri.cm  # noqa: F401  (registers cmc.*)
        if theme != "dark":
            mpl.rcParams["image.cmap"] = "cmc.batlow"
    except ImportError:
        pass
    P.register_all()
    _CURRENT.update(theme=theme, target=target, **{k: v for k, v in kw.items()})
    return r


def context(theme="clean", target="nature", **kw):
    """Temporary style: `with sp.context('dark', 'slide'): ...`"""
    return mpl.rc_context(rc(theme, target, **kw))


_CURRENT: dict = {}


def current() -> dict:
    """Active theme/target (used by helpers to pick colors that match)."""
    return dict(_CURRENT)


def theme_colors(theme=None) -> dict:
    """fg/bg/muted/axis/context colors for the active (or given) theme."""
    t = THEMES[theme or _CURRENT.get("theme", "clean")]
    ctx = {"dark": "#3A4250", "paper": "#CFC8BE", "editorial": "#C9CDD2"}.get(
        theme or _CURRENT.get("theme", "clean"), P.NEUTRALS["context"])
    return dict(bg=t["bg"], fg=t["fg"], axis=t["axis"], muted=t["muted"], context=ctx)


def write_mplstyles(outdir=None):
    """Write styles/<theme>-<target>.mplstyle files for use without the package."""
    outdir = Path(outdir or Path(__file__).resolve().parents[2] / "styles")
    outdir.mkdir(parents=True, exist_ok=True)
    targets = ["nature", "nature-research", "cell", "science", "neurips", "slide", "poster"]
    n = 0
    for th in THEMES:
        for tg in targets:
            r = rc(th, tg)
            lines = [f"# sciplot theme={th} target={tg} (generated; see scripts/sciplot/styles.py)"]
            for k, v in r.items():
                if k == "axes.prop_cycle":
                    cols = ", ".join(f"'{c.lstrip('#')}'" for c in v.by_key()["color"])
                    v = f"cycler('color', [{cols}])"
                elif isinstance(v, (list, tuple)):
                    v = ", ".join(str(x) for x in v)
                elif isinstance(v, str) and v.startswith("#"):
                    v = v.lstrip("#")
                lines.append(f"{k}: {v}")
            (outdir / f"{th}-{tg}.mplstyle").write_text("\n".join(lines) + "\n")
            n += 1
    return n
