# Third-party sources

`sciplot` contains **colour values** (hex codes) collected from the sources below. Each palette in
`scripts/sciplot/palettes.py` and `scripts/sciplot/data/imported.json` records its `source`.
Individual colour values are generally not copyrightable, but we credit every source and list its license
where it has one. If you redistribute a specific palette, follow its original terms.

## Imported palette collections (`data/imported.json`, built by `scripts/tools/build_imported_palettes.py`)
| Source | License | Link |
|---|---|---|
| Paul Tol's colour schemes (`tol-colors`) | BSD-3-Clause | https://sronpersonalpages.nl/~pault/ |
| MetBrewer (Blake R. Mills) | CC0-1.0 | https://github.com/BlakeRMills/MetBrewer |
| wesanderson (Karthik Ram) | MIT | https://github.com/karthik/wesanderson |
| ggsci (Nan Xiao): journal-inspired palettes | GPL-3.0 (code); colour values only are used here | https://github.com/nanxstats/ggsci |
| Catppuccin | MIT | https://github.com/catppuccin/palette |
| Rosé Pine | MIT | https://github.com/rose-pine/palette |
| Nord | MIT | https://github.com/nordtheme/nord |
| Riso ink colours (mattdesl/riso-colors) | see repository | https://github.com/mattdesl/riso-colors |
| matplotlib colour sequences (Okabe–Ito, Petroff, tab10) | matplotlib license (PSF-based) | https://matplotlib.org |

## Palettes defined in `palettes.py`
- **Okabe & Ito (2008)** / Wong, *Nat Methods* 8:441 (2011): Colour Universal Design.
- **IBL Brain-Wide Map** variable ramps: `int-brain-lab/paper-brain-wide-map` (`bwm_figs.py`); see that repository for its license.
- **CEBRA** colormap: `AdaptiveMotorControlLab/CEBRA`; see that repository for its license.
- **rsatoolbox** RDM colormap: `rsagroup/rsatoolbox`, MIT.
- **Allen Brain Atlas** structure colours: Allen Institute API (structure graph 1); see Allen Institute terms of use.
- **IBM Carbon** data-viz palettes: `carbon-design-system`, Apache-2.0.
- **Our World in Data** grapher schemes: `owid/owid-grapher`, MIT.
- **d3-scale-chromatic** (Tableau10, observable10): ISC.
- **Tailwind CSS v4** colours (approximate sRGB conversions): MIT.
- **Radix UI colors**: MIT. **GitHub Primer primitives**: MIT. **Dracula theme**: MIT. **Solarized** (Ethan Schoonover): MIT.
- **Financial Times Origami** `o-colors`, **The Economist** design-system, **Reuters graphics-components**:
  house colours observed in their public repositories or style guides, credited for reference.
- **Datawrapper blog** style-guide examples (Pew, YouGov, New America, Economist).
- **Pantone** Colors of the Year (2024 Peach Fuzz, 2025 Mocha Mousse, 2026 Cloud Dancer): approximate sRGB values
  of publicly announced colours. PANTONE® is a trademark of Pantone LLC; this project is not affiliated with Pantone.
- **nipponcolors.com**: traditional Japanese colour names.

## Colormaps (not bundled)
Fabio Crameri's *Scientific colour maps* (`cmcrameri`, MIT) and CMasher (BSD-3-Clause) are optional
dependencies, loaded only when installed.

## Fonts (not bundled)
Inter (OFL-1.1), JetBrains Mono (OFL-1.1), IBM Plex Sans (OFL-1.1), Source Sans 3 (OFL-1.1), DM Sans (OFL-1.1) and
Geist (OFL-1.1) are referenced by name. `scripts/install_fonts.py` downloads Inter and JetBrains Mono from their
official releases. Arial and Helvetica are trademarks of their respective owners. Liberation Sans is used as a
metric-compatible substitute.

## Research sources
`references/research-report.md` quotes short passages from publisher author guidelines and from papers,
with links, for commentary.
