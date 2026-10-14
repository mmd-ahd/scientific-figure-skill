---
name: scientific-figure
description: Build publication-grade, modern, beautiful scientific figures with matplotlib/seaborn — journal-exact multi-panel layouts (Nature, Nature Neuroscience, Neuron/Cell, Science, eLife, PNAS, JNeurosci, PLOS, NeurIPS/ICLR/ICML), a 200-palette CVD-measured color bank, style themes (clean, editorial, soft, ink, paper, dark), comp-neuro/NeuroAI panel recipes (rasters, PSTHs, trajectories, RDMs, embeddings, layer-wise model–brain alignment, rainclouds), schematics/model diagrams, graphical abstracts, posters, talk slides, and nilearn/MNE/pycortex/PyVista brain-viz presets, with automatic linting (fonts, strokes, sizes, color-blind safety). Use whenever the user wants a figure, plot, chart, panel, schematic, graphical abstract, poster/slide figure, color palette or colormap for a paper, preprint, thesis or talk — or asks to make an existing figure prettier, journal-compliant or colorblind-safe.
---

# Scientific figures (sciplot)

`sciplot` is a pure-matplotlib library that ships with this skill in `scripts/sciplot` (paths below are relative
to the directory containing this SKILL.md, called `<skill-dir>`).

## Setup (once per session)
1. Pick the user's Python (their project venv/conda env if there is one, else `python3`) and check:
   `python -c "import sciplot, matplotlib, numpy"`.
2. If `sciplot` is missing, either `pip install <skill-dir>` (adds `import sciplot` everywhere) or put
   `sys.path.insert(0, "<skill-dir>/scripts")` at the top of the script. Needs only numpy + matplotlib ≥ 3.7.
3. Optional extras, used automatically when present: `cmcrameri cmasher colorspacious` (Crameri/CMasher maps;
   without them `cmc.*`/`cmr.*` names fall back to viridis/RdBu_r/twilight with a warning), `scipy`, `seaborn`,
   `nilearn mne` (brain-viz). Install them only if the user agrees or the env already has them.
4. Fonts: Inter is preferred; it is optional. `python <skill-dir>/scripts/install_fonts.py --list` shows what
   matplotlib sees; `install_fonts.py` (no flag) installs Inter + JetBrains Mono for the user. Otherwise the stack
   falls back (Helvetica → Arial → Liberation Sans → DejaVu Sans) and `lint` reports the font actually used —
   mention it in the deliverable.

## Workflow (follow every time)
1. **Message & venue.** Write the one-sentence message of the figure and of each panel. Identify the target
   (`nature`, `nature-research`, `ncomms`, `cell`/`neuron`, `science`, `elife`, `pnas`, `jneurosci`, `plos`,
   `neurips`/`iclr`, `icml`, `slide`, `poster`, `graphical-abstract`, `web`) and width (`single`, `1.5`, `double`, or mm).
   If unknown and it matters, ask; otherwise default to `nature` double column.
2. **Layout** at final size: `fig, ax = sp.figure(target, width, height_mm=..., mosaic=...)`. Order panels as a story
   (schematic → data → model → summary). See templates in `references/neuro-figure-patterns.md`.
3. **Style & colour.** `sp.use(theme, target=..., palette=...)`. Choose colours by data type
   (`references/color-science.md`): grey context + one accent; one fixed colour per condition across all panels;
   perceptual sequential/diverging/cyclic maps; never jet. Find palettes with
   `sp.search(kind="cat", mood="calm", cvd_safe=True, min_n=4)`; check `sp.palettes.info(name)["measured"]["safe_n"]`.
4. **Build panels** with the recipes (`sp.neuro.*`, `sp.schematic.*`, `sp.annotate.*`) or plain matplotlib/seaborn
   (call seaborn functions with `ax=`; never call `sns.set_theme()` after `sp.use`, it overwrites the style).
   Direct-label lines (`sp.label_lines`), show data points, define stats.
5. **Finish:** `sp.align_labels(fig)`, `sp.label_panels(fig, ax)` (last, after all content), then
   `sp.save(fig, path, formats=(...), target=target)` — it prints the size in mm and runs `sp.check.lint`.
   Fix every lint warning or consciously justify it.
6. **Look at it.** Render the PNG and Read it. Check: overlaps, clipped text, letter alignment, colorbar placement,
   legibility at 100%, colour consistency, empty space balance. Iterate until it looks like a figure from a top
   journal — this visual review step is mandatory, the linter can't judge aesthetics.
7. Deliver PDF/SVG (vector, editable text) + PNG preview; state font, palette, size and any caveats
   (e.g. "Cell requires Arial: Liberation Sans used, metric-identical").

## Quickstart
```python
import numpy as np
import sciplot as sp                      # or: sys.path.insert(0, "<skill-dir>/scripts")
from sciplot import neuro

rng = np.random.default_rng(0)            # toy data — replace with the user's
t = np.linspace(-0.5, 1.5, 200)
Y_ctrl = 5 + rng.normal(0, 1, (30, 200))
Y_opto = Y_ctrl + 8 * np.exp(-((t - 0.3) / 0.15) ** 2)
D = 1 - np.corrcoef(rng.normal(size=(16, 40)) + np.repeat(np.eye(2), 8, 0) @ rng.normal(0, 2, (2, 40)))
a, b = rng.normal(0.55, 0.08, 12), rng.normal(0.70, 0.08, 12)

sp.use("clean", target="nature", palette="sp.neuro")
pal, tc = sp.colors("sp.neuro"), sp.theme_colors()
fig, ax = sp.figure("nature", "double", height_mm=60, mosaic="ABC", width_ratios=[1.2, 1, 1])
neuro.mean_ci(ax["A"], t, Y_ctrl, tc["context"], label="Control")
neuro.mean_ci(ax["A"], t, Y_opto, pal[0], label="Opto")
sp.shade(ax["A"], 0, 0.5, label="stim"); sp.label_lines(ax["A"])
ax["A"].set(xlabel="Time from onset (s)", ylabel="Firing rate (Hz)")
neuro.rdm(ax["B"], D, groups=[(0, 8, "faces"), (8, 16, "objects")])
neuro.dots_and_summary(ax["C"], [a, b], [tc["context"], pal[0]], labels=["Ctrl", "Opto"])
sp.sig_bracket(ax["C"], 0, 1, y=0.9, text=0.004)
ax["C"].set_ylabel("Decoding accuracy")
sp.align_labels(fig); sp.label_panels(fig, ax)
sp.save(fig, "figures/fig2", formats=("pdf", "svg", "png"), target="nature")
```
Full worked examples: `scripts/demo_figures.py` (Nature 7-panel, NeurIPS editorial, dark slide, graphical abstract,
nilearn+MNE brain panel) and `scripts/recipe_gallery.py` (one panel per recipe, all themes); rendered outputs in
`examples/` — Read `examples/recipe_gallery.png` to see what each recipe looks like.

## API cheat-sheet
| Need | Call |
|---|---|
| Theme × venue | `sp.use(theme, target, font="auto"/"inter"/"geist"/"plex"/"source"/"arial", palette=, bg=, scale=, grid=)`; temporary: `with sp.context(...)` |
| Themes | `clean` (journal default) · `editorial` (FT/Economist: y-hairlines, no y-spine, bold titles) · `soft` (pale panel + white grid) · `ink` (monochrome + accent) · `paper` (Cloud Dancer bg; web/posters) · `dark` (slides) |
| Figure/layout | `sp.figure(target, width, height_mm, mosaic=, width_ratios=, height_ratios=, hspace=, wspace=)`, `sp.figsize`, `sp.layout.VENUES` |
| Axes polish | `sp.max_ticks(ax, 4)`, `sp.offset_spines(ax, 3)`, `sp.trim_spines(ax)`, `sp.range_frame(ax, x, y)`, `sp.layout.inset(ax, bounds)` |
| Panel letters | `sp.label_panels(fig, ax_dict_or_list)` — venue case/size, row-aligned, nudges left titles |
| Colours | `sp.colors(name, n)`, `sp.cmap(name)`, `sp.highlight(n, idx, accent)`, `sp.shades(c, n)`, `sp.paired(name)`, `sp.semantic("neuro.ei")`, `sp.theme_colors()`, `sp.palettes.NEUTRALS/BACKGROUNDS`, `sp.palettes.swatch([...], cvd=True)` (PNG to Read) |
| Colour math | `sp.color.oklch(L,C,h)`, `lighten/darken/mix/tints/desaturate`, `ensure_contrast`, `contrast_ratio`, `delta_e`, `simulate_cvd`, `sp.palettes.build_categorical(n)` |
| Annotations | `sp.label_lines`, `sp.label_point`, `sp.sig_bracket` (p → stars) / `sp.annotate.fmt_p`, `sp.scale_bar`, `sp.event_lines`, `sp.shade`, `sp.slim_colorbar`, `sp.annotate.halo`, `sp.annotate.value_labels` |
| Neuro recipes | `neuro.mean_ci, raster, psth, activity_heatmap, rdm, trajectories, style_3d, gradient_line, embedding, axis_arrows, dots_and_summary, raincloud, half_violin, layer_profile, tuning_curve, connectivity, learning_curves, image_panel` |
| Brain-viz | `neuro.nilearn_kwargs(kind)`, `neuro.mne_topomap_kwargs()`, `neuro.pycortex_quickflat_kwargs()`, `neuro.pyvista_theme(dark)`, `neuro.normalize_text(fig)` |
| Schematics (mm canvas) | `S.canvas(ax)`, `S.box(ax, xy, w=None, h=None, text, fc, anchor="ll"/"c")` (auto-size), `S.pill`, `S.circle`, `S.arrow(p1, p2, rad, style)`, `S.connect(a, b, sides)`, `S.pipeline`, `S.network(layers)`, `S.recurrent_unit`, `S.layer_stack`, `S.prism`, `S.mini_trace`, `S.mini_matrix`, `S.gradient_box`, `S.bracket` |
| Export & QA | `sp.save(fig, path, formats, dpi=600, target)`, `sp.preview(fig)`, `sp.export.pdffonts(pdf)`, `sp.check.lint(fig, target)`, `sp.check.font_in_use()`, `sp.check.palette_report(colors)` |
| No-package use | `plt.style.use("<skill-dir>/styles/<theme>-<target>.mplstyle")` |

## Decision rules (defaults Claude should apply without asking)
- **Background white** for journals; `paper`/`dark` only for web, posters, slides.
- **Font**: Inter by default; Arial (or its clone Liberation Sans) automatically for `cell`/`neuron`/`plos`; report
  the font `lint` printed.
- **Sizes**: Nature family 5–7 pt (base 7, ticks 6, letters 8 bold lowercase); Cell 6–8 pt capitals; slides ≥ 14 pt.
- **Strokes**: axes 0.6 pt, data 1.0 pt in print (NComms ≥ 1 pt); markers ~3.5 pt.
- **Colours per panel ≤ 5**; more → highlight + grey, shades of a hue, or small multiples.
- **Every continuous map has a colorbar**; diverging maps centred on zero with symmetric limits.
- **Statistics**: dots + summary, not bars ± SEM, for n < 30; define error bars; exact P preferred (stars only if defined).
- **No titles inside journal figures** (short panel headers OK); no 3-D unless the data are 3-D; no rainbow/jet; no red/green.
- **Rasterize** dense artists (`rasterized=True`: rasters, >5k points, images) to keep PDFs small; text stays vector.
- **Never `bbox_inches="tight"`** for journal output (changes the width); `sp.save(..., tight=True)` only for slides/web.
- For **seaborn**: `sns.<plot>(..., ax=ax, palette=sp.colors(name, k))`; set `linewidth`, `edgecolor` explicitly if needed.
- For **existing user figures**: apply `sp.use` before their code, re-run, lint, then fix specific issues.

## References (load as needed)
- `references/journal-specs.md` — per-venue widths, fonts, strokes, formats, labels, stats rules.
- `references/design-principles.md` — the rules behind beautiful, honest figures + self-review checklist.
- `references/color-science.md` — choosing colormaps by data, CVD thresholds, building OKLCH palettes, neuro conventions.
- `references/neuro-figure-patterns.md` — panel types × recipes × exemplar conventions; composition templates.
- `references/trends-2026.md` — editorial/design-system/Pantone/heritage trends and where each is appropriate.
- `references/palettes.md` — generated catalog of all palettes with measured CVD ΔE and `safe_n`.
- `references/research-report.md` — full sourced research report (journals, exemplars, guidelines, tooling).
- `assets/palette_gallery_*.png` — visual index (Read the PNG to browse palettes).

## Maintenance
- Rebuild palette measurements/gallery/catalog after editing palettes: `python scripts/palette_gallery.py`.
- Re-import upstream palettes: `python scripts/tools/build_imported_palettes.py <downloads-dir>` (sources in its docstring).
- Regenerate `.mplstyle` files: `python -c "import sciplot.styles as s; s.write_mplstyles()"` (from `scripts/`).
- Regenerate `docs/api.md` after changing signatures/docstrings: `python scripts/tools/gen_api_docs.py`.
- Build the claude.ai upload zip: `bash scripts/tools/build_skill_zip.sh dist`.
- Regression check: `pytest` and `python scripts/demo_figures.py <tmpdir>` → all lints OK, then view the PNGs.
