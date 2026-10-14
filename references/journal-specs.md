# Journal & venue figure specifications (verified Oct 2026)

All numbers are at **final print size**. These are encoded in `sciplot.layout.VENUES`;
`sp.check.lint(fig, target)` checks width, font range and stroke minimum against them.
Full sourced notes: `references/research-report.md`.

| Venue (`target`) | Widths 1 / 1.5 / 2 col (mm) | Max h (mm) | Text (pt) | Panel labels | Min stroke | Formats |
|---|---|---|---|---|---|---|
| Nature (`nature`) | 89 / 120–136 / 183 | 170 (page 247) | 5–7, Helvetica/Arial pref. | **8 pt bold lowercase a b c** | 0.25 (max 1) | editable vector PDF/AI/EPS/SVG; **no JPEG/TIFF/PNG for main figs**; images ≥ 450 dpi |
| Nat Neurosci / NMI / NHB (`nature-research`, `nn`, `nmi`) | 88 / – / 180 | ~130–225 (depends on legend) | 5–7 | lowercase bold | 0.25 | vector AI/EPS/PDF, bitmaps ≥ 300 dpi |
| Nat Commun (`ncomms`) | 88 / – / 180 | – | ~same size everywhere | lowercase bold, **same size as text** | **1 pt** | vector; line art 1200 dpi |
| Cell Press: Cell, Neuron, Cell Rep, Curr Biol (`cell`, `neuron`) | 85 / 114 / 174 | ~200 | **6–8, Arial only** | **capitals A B C** | 0.5 (–1.5) | TIFF (LZW)/PDF; 300 dpi colour, 500 B/W, 1000 line art |
| Science / Sci Adv (`science`) | 90 / ≤144 / 184 | 199 rec. | 6–8 (8 default), Myriad pref. | **9 pt bold capitals** | 0.5 (Sci Adv 0.28) | vector PDF/AI/EPS; no Word/PPT figures; **no minor ticks** |
| eLife (`elife`) | ≥100 / – / ≥200 | – | – | – | – | TIFF/PDF/EPS ≥ 300 dpi |
| PNAS (`pnas`) | ~90 / ~114 / ~178 | ~220 | 6–12 | – | – | TIFF/EPS/PDF; 600–900 ppi with type; 1000–1200 line art; **numeric axes start at 0** |
| J Neurosci (`jneurosci`) | 85 / 116 / 176 | – | – | – | – | **TIFF or EPS only**, fonts outlined; **no top/right spines; no two-bar graphs** |
| PLOS CB (`plos`) | 66.8 min / 132 / 190.5 | 222 | **8–12, Arial/Times** | – | – | **TIFF (LZW) or EPS only**, 300–600 dpi |
| NeurIPS / ICLR (`neurips`, `iclr`) | textwidth 139.7 (5.5 in) | 228 | body Times 10, captions 9 → figure text 7–9 | – | – | PDF, Type 42 / Type 1 fonts (no Type 3) |
| ICML (`icml`) | 82.55 / – / 171.45 | 228 | as above | – | – | PDF, no Type 3 fonts; no title inside figure |
| Cell GA (`graphical-abstract`) | 1200 × 1200 px @300 dpi = 101.6 mm square | | Arial 8–12 | – | – | no data; reads top→bottom or left→right |

## Rules shared across venues (encode by default)
- Sentence-case labels, units in parentheses: `Firing rate (Hz)`, `Time from onset (s)`. SI units (`ms`, not `msec`), leading zeros (`0.5`), thousands separators for ≥5 digits.
- No figure titles inside the figure (titles go in the caption); short panel titles are OK for Nature/Cell-style "what is this panel" headers.
- Scale bars (vector, labelled or defined in legend) instead of magnification; scale bars on all microscopy.
- Define error bars (SD / SEM / 95% CI), n, test and exact P in the legend. Show individual data points (Cell explicitly).
- Avoid red/green pairings (all), rainbow/jet (Nature), dark-blue + yellow pairs (Science). Use Okabe–Ito or measured-safe palettes. Text contrast > 4.5:1 (Nature).
- White backgrounds for journal figures (Science, NComms). Off-white/dark themes are for slides, posters, web.
- RGB colour mode (all current guides).
- Generative-AI imagery banned (Nature, Cell Press, Science Advances).
- Image integrity: global adjustments only, applied to controls too; mark splices; keep raw images.

## Export recipe per venue
| Venue | `sp.save(..., formats=)` | Notes |
|---|---|---|
| Nature family, Science, Cell, eLife, ML venues | `("pdf", "svg", "png")` | PDF with Type 42 fonts (editable). PNG only for preview. |
| PLOS CB | `("tiff", "eps")`, `dpi=600` | TIFF LZW is automatic. |
| J Neurosci | `("tiff", "eps")` | They want outlined fonts: open the EPS/PDF in Inkscape → "Object to path", or set `svg.fonttype='path'`. |
| Cell submission | `("pdf", "tiff")`, `dpi=600` | Font must be Arial: `sp.use(..., target="cell")` auto-picks Arial, falling back to Liberation Sans (metric-identical). |

## Fonts
Nature says "preferably Helvetica or Arial", Cell/PLOS require Arial. `font="arial"` uses Arial or Helvetica when
installed and otherwise **Liberation Sans** (Arial-metric clone, common on Linux). Modern alternative for venues that
only *prefer* Helvetica/Arial: **Inter** (default), Geist, IBM Plex Sans, Source Sans 3 (all OFL; install Inter with
`python scripts/install_fonts.py`). Missing fonts fall back down the stack (… → DejaVu Sans); `sp.check.lint` prints
the font actually rendered and warns when an Arial-only venue is not met. Mathtext uses the same font.
