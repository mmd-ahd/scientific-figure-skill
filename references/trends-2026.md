# Modern design trends (2024–2026) → how they translate to scientific figures

## What's current
- **Editorial data-viz** (FT, Economist, OWID, Reuters, Datawrapper): warm/tinted off-white canvas (FT paper
  `#FFF1E5`, Economist `#F5F4EF`), 1 brand hue + 1–2 supporting hues used in fixed order, extra series as *shades*,
  background-tinted greys for context (`#D9CDC3` FT, `#CFD1C3` Economist), horizontal hairline grids with no y-spine,
  bold left-aligned titles, direct labels, title-as-colour-key.
- **Perceptual colour systems**: Tailwind v4 (Jan 2025) moved to OKLCH; v4.2 (Feb 2026) added tinted neutrals
  *mauve, olive, mist, taupe*. Radix 12-step scales, IBM Carbon ordered data-viz palettes (14-colour categorical, light & dark),
  Adobe Spectrum, GitHub Primer data colours. Lesson: build palettes in OKLCH, stagger lightness, ship explicit dark variants.
- **Colour of the year drift → soft warm neutrals**: Pantone 2024 Peach Fuzz `#FFBE98`, 2025 Mocha Mousse `#A47864`,
  2026 **Cloud Dancer `#F0EEE9`** (first white ever). Counter-current: WGSN/Coloro 2027 **Luminous Blue** (saturated accent),
  Adobe 2026 trends: high-energy saturated palettes, tactile/organic, zine-like editorial layouts.
  → *Calm off-white canvas + one luminous accent* (`sp.use("paper")`, `sp.mocha`, `sp.lavender`).
- **Heritage & art palettes**: nipponcolors (`nippon.*`), MetBrewer (`met.*`, 56 artworks), Wes Anderson (`wes.*`) —
  harmonious, low-chroma sets that look "designed" (check `safe_n` before using for categories).
- **Developer/UI themes for dark slides**: Catppuccin, Rosé Pine, Nord, Dracula, Tokyo-Night-like `sp.midnight`,
  synthwave/neon (`sp.synthwave`, `sp.neon`). Dark bg never pure black; text never pure white.
- **Risograph / Bauhaus / Swiss**: flat spot colours (`sp.riso` from official Riso ink hexes, `sp.bauhaus`), strong
  geometry — great for graphical abstracts and posters.
- **Typography**: screen-native neo-grotesques with tabular figures — Inter (4.1), Geist (1.7–1.8), IBM Plex Sans,
  Source Sans 3, DM Sans; mono: JetBrains Mono, Geist Mono. All OFL and installed locally.

## Where trends are allowed
| Output | Background | Palette freedom | Font |
|---|---|---|---|
| Journal figure | **white** (Science/NComms ask for it) | measured-safe categorical; trend palettes only if `safe_n` ≥ needed | Inter (or Arial/Liberation Sans for Cell/PLOS) |
| bioRxiv / thesis | white or very light paper | any safe palette | Inter / Plex / Source Sans |
| Talk slides | dark (`dark`) or clean | neon / midnight / synthwave / catppuccin | Inter, Geist |
| Poster | white, cloud dancer, light tint | bold (bauhaus, riso, aurora) | Inter Display / Geist for titles |
| Graphical abstract | white | riso, aurora, gradients | Arial for Cell (rule), else Inter |
| Lab website / blog | paper (`#F0EEE9`, `#FFF1E5`) | editorial (ft, economist, owid) | Inter / Plex |

## Stylistic devices (use sparingly, never on data encodings that need precision)
- Gradient fills in schematic blocks (`schematic.gradient_box`), isometric prisms/stacks for model diagrams.
- Pills/badges for key numbers (`schematic.pill`), soft shadows only in schematics (`shadow=True`).
- Slim, short colorbars without outlines; floating (offset) spines; range frames.
- Background epoch shading in a 6–10% tint of the text colour, labelled on top.
- Rounded caps/joins on lines; pre-mixed tints instead of alpha for clean vector output.
