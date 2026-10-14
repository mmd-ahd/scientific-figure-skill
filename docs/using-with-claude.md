# Using the skill with Claude

## What happens when you ask for a figure
Claude loads `SKILL.md` when a request mentions a figure, plot, panel, schematic, colormap, poster or slide. The skill
gives Claude the `sciplot` library and a fixed workflow:

1. **Message and venue.** Claude writes one sentence for the figure and one per panel, and picks the target (e.g.
   `nature-research`, `cell`, `neurips`) and width. If you don't say, it uses Nature double column and tells you so.
2. **Layout at final size.** It calls `sp.figure(target, width, height_mm, mosaic=...)` and orders panels as a story:
   schematic → data → model → summary.
3. **Style and colour.** It calls `sp.use(theme, target, palette)`. Context is grey with one accent, each condition
   keeps the same colour in every panel, sequential/diverging/cyclic maps are chosen by data type, and jet is never used.
4. **Build panels** with the recipes or plain matplotlib/seaborn, labelling lines directly and showing the data points.
5. **Finish and lint.** It aligns labels, adds panel letters, then runs `sp.save(...)`, which prints the size and the
   lint result.
6. **Look at it.** Claude renders the PNG, reads it, and fixes overlaps, clipped text, colorbar placement and
   balance. This step is required because the linter can't judge aesthetics.
7. **Deliver** vector PDF/SVG plus a PNG preview, and report the font, palette, size and any caveats.

## Prompts that work well
Give the **data** (file path or a description of the arrays), the **venue**, and what each panel should show.
- "Figure 3 for *Neuron*: A, task schematic; B, example raster + PSTH for the 3 coherences; C, choice-decoding
  accuracy over time vs. shuffle; D, per-session decoding at 300 ms as dots + mean. Data in `results/fig3.npz`."
- "Make a 2 × 3 panel of model–brain RSA by layer for 5 vision models, NeurIPS full width, colour-blind safe."
- "Plot this UMAP of hippocampal population activity coloured by position, CEBRA style."
- "Poster version (A0 column) of `fig2.py`, `paper` theme."
- "Find me a calm 5-colour categorical palette that is safe for deuteranopes and works on a dark slide."
- "Here is my figure script. Make it Nature-compliant and prettier without changing the data."

## Fixing an existing figure
Ask Claude to apply the skill to your script. It will add `sp.use(...)` before your plotting code, replace
`plt.figure(figsize=...)` with `sp.figure(target, width, ...)`, re-run, lint, and then fix the specific issues the
linter and its own visual review find. Your data processing stays untouched.

## Without the package installed
Claude checks `python -c "import sciplot"`. If that fails, it either runs `pip install <skill-dir>` or adds
`sys.path.insert(0, "<skill-dir>/scripts")`. It installs optional packages (cmcrameri, nilearn, …) only with your
agreement or when your environment already has them. Without them, colormap names fall back to matplotlib built-ins.

## Where the knowledge lives
Claude reads `references/*.md` only when needed, so they cost no context until then:
- `journal-specs.md`: widths, fonts, strokes and formats per venue, with sources
- `design-principles.md`: rules plus a self-review checklist
- `color-science.md`: choosing colormaps, CVD thresholds, OKLCH palette construction, neuro colour conventions
- `neuro-figure-patterns.md`: panel types × recipes × exemplar conventions, composition templates
- `trends-2026.md`: editorial and design-system trends, and where each is appropriate
- `palettes.md`: the measured palette catalogue
- `research-report.md`: the full sourced research behind the defaults
