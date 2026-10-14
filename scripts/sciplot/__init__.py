"""sciplot — publication-grade, modern scientific figures (comp-neuro / NeuroAI).

    import sciplot as sp          # pip install, or sys.path.insert(0, "<skill-dir>/scripts")

    sp.use("clean", target="nature")                       # theme × venue
    fig, ax = sp.figure("nature", "double", height_mm=70, mosaic="AB;CD")
    ...
    sp.label_panels(fig, ax)
    sp.save(fig, "out/fig1", formats=("pdf", "png"))       # lints automatically

Modules: palettes (bank), color (OKLCH/CVD math), styles, layout, annotate,
neuro (panel recipes + brain-viz presets), schematic, check, export.
"""
from . import annotate, check, color, export, layout, neuro, palettes, schematic, styles
from .annotate import (event_lines, label_lines, label_point, scale_bar, shade, sig_bracket,
                       slim_colorbar)
from .export import preview, save
from .layout import (MM, VENUES, align_labels, figsize, figure, label_panels, max_ticks,
                     offset_spines, range_frame, trim_spines)
from .palettes import cmap, get as colors, highlight, paired, search, semantic, shades
from .styles import context, theme_colors, use

__all__ = [
    "annotate", "check", "color", "export", "layout", "neuro", "palettes", "schematic",
    "styles", "use", "context", "theme_colors", "figure", "figsize", "label_panels",
    "align_labels", "offset_spines", "range_frame", "trim_spines", "max_ticks", "save",
    "preview", "colors", "cmap", "highlight", "paired", "search", "semantic", "shades",
    "label_lines", "label_point", "sig_bracket", "scale_bar", "event_lines", "shade",
    "slim_colorbar", "MM", "VENUES",
]
__version__ = "1.0.0"
