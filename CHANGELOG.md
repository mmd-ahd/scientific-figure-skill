# Changelog

## 1.0.0 — 2026-10-14
First public release.

- `sciplot` library: venue presets (Nature family, Cell Press, Science, eLife, PNAS, JNeurosci, PLOS,
  NeurIPS/ICLR, ICML, slides, posters, graphical abstracts, web), six themes, 197-palette CVD-measured colour
  bank, semantic neuro palettes, OKLCH colour math.
- Panel recipes for comp-neuro/NeuroAI (`sciplot.neuro`) and mm-precise schematics (`sciplot.schematic`).
- Brain-viz presets for nilearn, MNE, pycortex and PyVista.
- `sp.save` exports editable vector PDF/SVG and runs the figure linter (sizes, strokes, widths, contrast,
  CVD separation, rainbow colormaps, font actually rendered).
- Works on a minimal install (numpy + matplotlib). Optional packages (cmcrameri, cmasher, colorspacious,
  scipy, seaborn, nilearn, mne) are used when present, with graceful fallbacks.
- `scripts/install_fonts.py` for Inter / JetBrains Mono, 42 portable `.mplstyle` files, pytest suite, CI,
  release zip for claude.ai.
