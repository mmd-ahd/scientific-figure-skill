# Design principles — what makes a figure beautiful *and* honest

Distilled from: Rougier, Droettboom & Bourne (2014) *Ten Simple Rules for Better Figures*; Rougier (2021)
*Scientific Visualization: Python + Matplotlib*; Wong et al. *Points of View* (Nat Methods 2010–2016);
Wilke *Fundamentals of Data Visualization*; Tufte; Cleveland & McGill (1984); Weissgerber et al. (2015);
Allen et al. (2019) raincloud plots; Ho et al. (2019) estimation plots; Datawrapper (Muth 2020–2023);
plus the exemplar papers in `neuro-figure-patterns.md`.

## 1. Message first
1. Write the one-sentence message of the figure (and of each panel) before plotting. Every encoding choice
   should serve it; if a panel has no message, cut it.
2. Know the medium: print figure (small, read closely), slide (big, read in 5 s, 1 message), poster
   (read at 1–2 m), graphical abstract (no data, a story in 3 steps).
3. The caption carries the title and the statistics; the figure carries the evidence.

## 2. Encode with the strongest channel
Cleveland–McGill ranking: **position on a common scale** > position on non-aligned scales > length /
direction / angle > area > volume / curvature > colour saturation / shading.
- Put the key comparison on a shared axis, side by side.
- Use colour for *identity* and *grouping*, not for precise magnitude (use position for that).
- Bank line charts so average slopes are about 45° (choose aspect ratio accordingly).
- Bars must start at 0 (proportional ink); log axes start at a meaningful power of 10.

## 3. Grey first, then one accent ("grey for context, colour for signal")
Used by every exemplar (IBL, Rastermap, MICrONS, CEBRA) and by Datawrapper/FT/Economist:
- Draw everything in a background-tinted grey (`P.NEUTRALS['context']`), then colour only what the message is about
  (`sp.highlight(n, idx, accent)`).
- More series of the same family → **shades of one hue** (`sp.shades(color, n)`), not new hues
  ("a change of colour implies a categorical change").
- ≤ 5 colours per panel is ideal; > 8 → direct labels, small multiples, or grey-out.
- **One fixed colour per variable/condition for the whole paper** (IBL: one hue family per task variable).

## 4. Label directly
- Put the series name at the line end in the series colour (`sp.label_lines(ax)`), region acronyms in the region colour,
  legend-as-title. Legends are a last resort; when used: frameless, ordered like the data.
- Units in parentheses, sentence case, no redundant labels (shared axes label once).
- Panel titles left-aligned, regular/medium weight (Rastermap, editorial style), not bold-centred.

## 5. Declutter (Tufte, "within reason")
- Remove top/right spines, box frames, background fills, 3-D effects, shadows on data, heavy grids.
- Grids: only when reading values matters, one axis, hairline, very light (15–45% opacity equivalent).
- ≤ 4–5 ticks per axis (`sp.max_ticks(ax, 4)`); no minor ticks (Science); outward ticks 2.5 pt.
- Thin strokes: axes 0.5–0.6 pt, data 1.0 pt (print), ≥ 0.25–0.5 pt minimum depending on venue.
- Do not over-minimise: keep axis lines and ticks on quantitative panels (Nature requires them).

## 6. Show the data
- n < ~30 per group: plot every point (`neuro.dots_and_summary`, `neuro.raincloud`), with mean/median + error.
- Prefer estimation (effect size + 95% CI) over p-value stars; when stars are used, define them in the legend and
  prefer exact P (`sp.annotate.fmt_p`). Paired designs: connect points (`paired=True`).
- Never error bars on technical replicates; with n = 3, show points only.
- Individual runs/seeds as faint thin lines, mean as a bold line (`neuro.learning_curves`).

## 7. Layout & typography
- Build at final size (mm). Never rescale a figure afterwards: fonts and strokes would change.
- One font family, 2–3 sizes only: tick labels (6), labels/body (7), panel letters (8 bold) for Nature.
- Align: shared baselines, aligned y-labels (`sp.align_labels`), panel letters on a common row line (`sp.label_panels`).
- Generous but consistent whitespace; group related panels (Gestalt: proximity < similarity < enclosure).
- Reading order: left→right, top→bottom; schematic/task first, then data, then model, then summary.
- Insets and annotations get halos (`sp.annotate.halo`) when on top of data.

## 8. Colormaps (see color-science.md)
- Sequential for magnitude, diverging (centred with `TwoSlopeNorm`/symmetric vmin/vmax) for signed data, cyclic for
  phase/orientation, categorical "S" maps for many classes. Never jet/rainbow/hsv for data.
- Always a colorbar (slim: `sp.slim_colorbar`), never stretch or crop a colormap to fake contrast.

## 9. Accessibility checklist (run `sp.check.lint`)
- Categorical colours ≥ 10 ΔE2000 apart under deutan/protan/tritan simulation, or redundant coding (marker, dash, label).
- Text contrast ≥ 4.5:1 (Nature) / ≥ 3:1 for large text and graphics (WCAG).
- Survives greyscale: vary lightness among categories; monotone-lightness colormaps.

## 10. Common failure modes Claude should catch when reviewing its own render
Overlapping labels, legend covering data, clipped text at figure edge, unequal panel-letter heights, colorbar
detached from its panel, axis tick labels with too many decimals, mismatched fonts (DejaVu in math), y-axes of
compared panels not shared, rainbow maps, red–green pairs, bars without data points, 3-D for 2-D data, titles
inside journal figures, text < venue minimum, inconsistent colours for the same condition across panels.
