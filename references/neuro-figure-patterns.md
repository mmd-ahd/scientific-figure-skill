# Comp-neuro / NeuroAI panel patterns (with sciplot recipes)

Exemplars studied (code + legends): **IBL Brain-Wide Map** (Nature 2025; `ibl-style`, `paper-brain-wide-map`),
**Rastermap** (Stringer et al., Nat Neurosci 2024; `rastermap/paper/fig_utils.py`), **CEBRA** (Schneider et al.,
Nature 2023), **MICrONS** (Nature 2025), **rsatoolbox** (Kriegeskorte lab). Shared traits: grey context + colour signal,
one hue family per variable, thin despined axes (IBL: 7 pt text, 6 pt ticks, 0.5 pt axes, ≤ 4 ticks), scale bars
instead of axes on image-like panels, tiny translucent points for manifolds, direct coloured labels.

| Panel | Recipe | Best practice |
|---|---|---|
| Task / model schematic | `schematic.box/pill/arrow/connect/network/recurrent_unit/prism/layer_stack/mini_trace/mini_matrix/gradient_box` on `schematic.canvas(ax)` (mm units) | Same font & stroke as data panels; palette colours as light tints with darker edge/text; 1 accent per stage; left→right flow; auto-sized boxes (`w=None`). |
| PSTH / trial-averaged traces | `neuro.mean_ci(ax, t, Y, color)` + `annotate.shade` / `event_lines` | Pre-mixed tint bands (SEM or bootstrap CI), events as dashed hairlines labelled on top, direct labels at line ends. |
| Spike raster | `neuro.raster(ax, spikes, colors=...)` | Rasterized line collection; rows grouped/coloured by condition; time scale bar. |
| Neurons × time heatmap | `neuro.activity_heatmap(ax, A, sort="peak", zscore=..., scalebar=dict(dx=…, xlabel="1 s", dy=…, ylabel="50 cells"))` | No axes, `gray_r` or symmetric `RdBu_r`, L-shaped scale bar, sorted (peak time or Rastermap order). |
| Population trajectories | `neuro.trajectories(ax, X, color, fade=True)` or `cmap=` for time; `neuro.axis_arrows(ax, "PC 1", "PC 2")`; 3-D: `neuro.style_3d` | Start = open circle, end = filled; condition hue via `sp.colors("sp.depth", n)` (ordered) or categorical; equal aspect; no ticks. |
| Embedding (UMAP/t-SNE/CEBRA) | `neuro.embedding(ax, Z, c=var, cmap=...)` | Point size ~1, alpha 0.4–0.6, rasterized; cyclic map for angles; grey background population. |
| RDM / similarity | `neuro.rdm(ax, D, groups=[(0,8,"faces"),…], triangle="lower")` + `sp.slim_colorbar` | Perceptual sequential map, category bars + coloured labels, optional white gaps; give the title `pad≈7` with groups. |
| Model–brain alignment by layer | `neuro.layer_profile(ax, layers, scores, color, err=…, ceiling=(lo, hi))` | Noise-ceiling band in light grey, direct labels for areas (V1 / IT), x labels rotated 45° anchor-right or relabelled early/middle/late. |
| Group comparisons | `neuro.dots_and_summary(...)`, `neuro.raincloud(...)`, `sp.sig_bracket(ax, x1, x2, y, p)` | Show every point; summary as thick short line + error; brackets thin; chance level as dashed hairline with text. |
| Learning curves (ML) | `neuro.learning_curves(ax, steps, runs, color, show_runs=True)` + `sp.highlight` | Baselines grey, "ours" accent; seeds as faint lines; log-x for steps. |
| Tuning curves | `neuro.tuning_curve(ax, theta, rates, color, polar=False)` | Markers with white edge; polar for direction with filled tint. |
| Connectivity / weights | `neuro.connectivity(ax, W, ei_split=…)` | Symmetric diverging limits, E/I separator lines. |
| Brain maps | `neuro.nilearn_kwargs("glass"|"stat"|"surf"|"connectome")`, `neuro.mne_topomap_kwargs()`, `neuro.pycortex_quickflat_kwargs()`, `neuro.pyvista_theme()`, then `neuro.normalize_text(fig)` | Draw into sciplot axes (`axes=`, `figure=`), diverging centred maps, no contour clutter, render 3-D off-screen with transparent background and place via `neuro.image_panel`. |
| Atlas regions | `sp.colors("allen.ccf")` (labels in `info("allen.ccf")["labels"]`) | CCF colours for identity only; values with per-variable sequential ramps (`ibl.*`). |

## Composition templates (mosaics)
- **Nature main figure** (183 × 110–170 mm): row 1 = schematic (wide) + 2 data panels; row 2 = 4 small panels.
  `mosaic=[["a","a","b","c"],["d","e","f","g"]]`.
- **Model-vs-brain** story: `[["task","model","model"],["neural","neural","align"],["rdm_b","rdm_m","stats"]]`.
- **ML paper single-row** (139.7 × 45–55 mm): 3 panels, editorial theme, highlight method.
- **Slide**: 2–3 panels, `target="slide"`, one message, dark or clean theme, 16 pt text.
- **Graphical abstract**: 101.6 mm square, no data, 3-step story, gradient boxes / prisms / mini matrices.

## Typical text
"Firing rate (Hz)", "Time from stimulus onset (s)", "Decoding accuracy", "Encoding R²" (`"Encoding $R^2$"`),
"Neural predictivity (r)", "Model layer", "PC 1", "Spearman ρ", "Δ accuracy (%)", "n = 14 mice".
