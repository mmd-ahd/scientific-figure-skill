# Colour science for figures — choosing, checking, building

## Pick the colour class from the data
| Data | Class | Good defaults (`sp.cmap(name)` / `sp.colors(name)`) |
|---|---|---|
| Unordered categories (conditions, models, areas) | categorical | `sp.neuro`, `sp.nature`, `sp.lab`, `okabe_ito`, `tol.muted`, `mpl.petroff10` |
| Few categories, one matters | accent + grey | `sp.highlight(n, idx, accent)` |
| Ordered levels (contrast %, layer index, time bins) | sequential discrete | `sp.colors("sp.depth", n)`, `ibl.*`, `carbon.purple` |
| Magnitude ≥ 0 (rates, R², density) | sequential | `cmc.batlow`, `viridis`, `cmc.lajolla`, `mako`, `rocket`, `cmr.ember`; rasters `gray_r` |
| Signed (Δ, z-score, weights, correlation) | diverging, centred | `cmc.vik`, `RdBu_r`, `sp.icefire`, `sp.teal_plum`, `carbon.purple_teal`; dark-centre: `cmc.berlin`, `cmc.managua`, `cmr.iceburn` |
| Phase, orientation, direction, time-of-day | cyclic | `cmc.romaO`, `cmc.vikO`, `twilight_shifted`, `cmr.infinity` |
| Many classes (>12, clusters) | categorical-from-map | `cmc.batlowS`, `cmc.hawaiiS`; better: grey-out + highlight |
| Region identity (mouse brain) | atlas | `allen.ccf` (identity only — never for values) |
| Model vs data, E/I, opto, train/test… | semantic | `sp.semantic("neuro.model_data")` etc. |

Rules: always a colorbar for continuous maps; centre diverging maps on the meaningful zero
(`vmin=-vmax` or `matplotlib.colors.TwoSlopeNorm`); never jet/rainbow/hsv (non-uniform lightness creates false
edges: >7% distortion for jet, Crameri 2020); never stretch/crop a map to boost contrast; use the same
colormap + limits for panels that are compared.

## Measured CVD safety (`data/cvd.json`, `references/palettes.md`)
- Simulation: Machado et al. 2009 (severity 100) via colorspacious, in linear sRGB; distances CIEDE2000.
- Thresholds (calibrated on established safe sets, Okabe–Ito ≈ 10.9, Tol muted ≈ 11.5):
  **≥ 10 pass · 6–10 warn · < 6 fail**. Petroff 2021 (matplotlib petroff6/8/10) used stricter CAM02-UCS targets
  of 20/18/16 for 6/8/10 colours.
- `safe_n` = how many *leading* colours of a palette stay ≥ 10 apart; e.g. tab10 is safe only up to 2,
  Tableau10 and Tailwind palettes fail beyond ~4–5, while all `sp.*` originals pass for their full length.
- Prevalence: ~8% of men, 0.5% of women (mostly deuteranomaly). Tritan is rare but our check covers it.
- Lightness: categorical colours should also differ in lightness so they survive greyscale/photocopy
  (`gray` column in reports); colormaps must be monotone in lightness (sequential) or symmetric (diverging).
- Contrast: text ≥ 4.5:1 (WCAG AA; Nature asks for > 4.5), large text & essential graphics ≥ 3:1.
  `sp.color.ensure_contrast(c, bg, 3)` darkens a series colour for its direct label automatically.

## Building new palettes (OKLCH)
OKLCH (Ottosson 2020) is perceptually uniform: equal ΔL looks equal across hues, unlike HSL. The modern design
systems (Tailwind v4, Radix, Huetone) are built in it.
- `sp.color.oklch(L, C, h)` → hex (gamut-mapped by chroma reduction).
- Categorical: spread hues, *stagger* lightness 0.50–0.80, moderate chroma 0.10–0.16, then verify:
  `sp.palettes.build_categorical(n=6)` does this search automatically, maximising CVD ΔE.
- Tune an aesthetic seed palette to pass CVD with minimal drift: `scripts/tools/tune_originals.py` logic
  (cap target ΔE 11, penalise drift).
- Sequential: one hue, L from ~0.25 → 0.95, chroma peaking mid-ramp (`sp.color.tints(c, k)`).
- Diverging: two sequential ramps glued at their light end (Datawrapper) — e.g. `sp.palettes.cmap` on a list
  `[dark1, mid1, light, mid2, dark2]` (interpolated in OKLab).
- Tints for CI bands / fills: `sp.color.lighten(c, 0.6, bg)` (pre-mixed, no alpha → clean vector overlaps).
- Dark backgrounds: raise L of every colour (~0.70–0.85), avoid pure black (`#0E1117`, `#16161E`), never pure white text
  (`#E6E8EB`).
- Natural, harmonious palettes: avoid pure hues (shift 5–10° off primaries), desaturate light colours and saturate
  dark ones, pair warm hues with blue (also CVD-friendly), take inspiration from art (MetBrewer), nature, heritage
  (nipponcolors).

## Neuro-specific colour conventions
- Excitatory red / inhibitory blue; left blue / right red (IBL); opto: ChR2 blue (473 nm), ArchT/eNpHR amber–green.
- Grey = non-significant / context / shuffle; black = data / main condition; colour = model or highlighted effect.
- Rasters: `gray_r` (counts) or `RdBu_r` symmetric (z-scored). Embeddings: colour = behavioural variable with a
  perceptual map (cyclic for angles).
- fMRI stat maps: diverging centred (`cmc.vik`, `RdBu_r`); nilearn's `cold_hot` only for continuity with older work.
- RDMs: sequential perceptual (`cmc.batlow`, `viridis`, `mako`); the Kriegeskorte "classic" map is not uniform.

## Sources
Crameri, Shephard & Heron (2020) Nat Commun 11:5444 · Kovesi (2015) arXiv:1509.03700 · Nuñez et al. (2018) cividis ·
Okabe & Ito (2008) · Tol (2026 web page; tol-colors 2.2.0) · Petroff (2021) arXiv:2107.02270 · Machado et al. (2009) ·
Sharma et al. (2005) CIEDE2000 test data (our implementation matches to 1e-4) · Datawrapper blog (Muth) ·
Ottosson (2020) OKLab.
