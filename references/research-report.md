# Restraint, not ornament, wins neuroscience figures

The best computational-neuroscience and NeuroAI figures of 2022–2026 look beautiful because they hold back. The IBL Brain-Wide Map, Rastermap, CEBRA and MICrONS all put context and non-significant data in grey, give each variable one fixed hue family for the whole paper, use thin despined axes with 5–7 pt sans-serif text, and replace axes with scale bars on image-like panels. That house style lines up closely with the official specs. Nature asks for 89/183 mm widths, 5–7 pt Helvetica/Arial, 0.25–1 pt strokes, editable vector text and the Okabe–Ito palette. Cell, Science, PNAS, PLOS, eLife, JNeurosci and the ML templates mostly differ in the details: panel-letter case, minimum line weight, file format and font embedding. The expert canon (Rougier's ten rules, Crameri's colour-misuse paper, Wong and Krzywinski's *Points of View*, Wilke, Weissgerber, Cumming) turns into a dozen checkable rules. The ones with numbers are: at most about 8 categorical colours, 0.5 pt axes, grids at 15–45% opacity, perceptually uniform colormaps with a colorbar, and every data point shown when n is small. Contemporary design trends (Datawrapper's grey-first emphasis, FT and Economist tinted neutrals, Tailwind v4's OKLCH ramps, IBM Carbon's ordered data-viz palettes, Pantone's 2026 off-white "Cloud Dancer" `#F0EEE9`) can make figures look current. They belong in the accent-and-neutral layer, because journals still require white backgrounds and most trend palettes were never tested for colour-vision deficiency. On the tooling side, matplotlib 3.11 plus seaborn 0.13.2 is enough, but five defaults have to be overridden. Type-3 fonts, outlined SVG text, `bbox_inches='tight'` resizing, DejaVu mathtext and the colour-blind-unsafe `tab10` cycle all work against journal compliance unless a skill fixes them. Together this points to a design for the "scientific-figure" skill: venue presets, a validated palette library, and an automated checker. A mood board would not do the job.

## Four 2022–2026 exemplars share one visual grammar

The most reproducible exemplars are the ones whose labs publish their plotting code, because that code records the design choices as exact values. A caveat up front: the researchers could not view the rendered figure images. Descriptions come from open-access legend text and the labs' plotting source, not from looking at the figures.

**The IBL Brain-Wide Map (Nature, September 2025; over 600,000 neurons across 279 regions in 139 mice)** is the most complete house style available ([Princeton PNI](https://pni.princeton.edu/news/2025/first-brain-wide-map-decision-making-charted-mice)). Its legends follow a strict semantic grammar. Colour shows effect size, and "grey [is] not significant at FDR0.01". Left and right stimuli are always blue and red. Analysis windows are grey. 0%-contrast trials are grey against black for the main condition. Region names are printed *in the region's own colour* so the labels double as a legend across figures ([PMC12408349](https://europepmc.org/article/PMC/PMC12408349)). Brain maps are drawn on Swanson flatmaps and atlas slices with white for empty regions, `silver` for masked regions, 0.1-pt outlines and a horizontal colorbar. Figure widths are set in millimetres (180 mm) ([bwm_figs.py](https://github.com/int-brain-lab/paper-brain-wide-map/blob/main/brainwidemap/meta/bwm_figs.py)). Every task variable gets its own sequential ramp, and that ramp is used for the variable throughout the paper:

| Variable | IBL sequential ramp (light → dark) |
|---|---|
| Stimulus | `#EAF4B3 #D5E1A0 #A3C968 #86AF40 #517146 #33492E` |
| Choice | `#F8E4AA #F9D766 #E8AC22 #DA4727 #96371D` |
| Feedback | `#F1D3D0 #F5968A #E34335 #A23535 #842A2A` |
| Block / prior / wheel | `#D0CDE4 #998DC3 #6159A6 #42328E #262054` |
| Movement | `#c1e1ea #91d0fa #5da5f1 #2a71d7 #0045b1` |

Source: [bwm_figs.py `get_cmap_for_variable`](https://github.com/int-brain-lab/paper-brain-wide-map/blob/main/brainwidemap/meta/bwm_figs.py). The lab's `ibl-style` package gives the rcParams behind this look:
- seaborn `ticks`/`paper` context with top and right spines off
- 7 pt base font, 8 pt titles, 6 pt tick labels
- 0.5 pt axes; ticks 2.5 pt long and 0.5 pt wide; 1 pt lines; 4 pt markers
- `pdf.fonttype 42`, with bundled Helvetica TTFs

([style.py](https://github.com/int-brain-lab/ibl-style/blob/main/src/ibl_style/style.py)). For the Brain-Wide Map figures specifically, the script sets text to 6–7 pt with a 5 pt minimum, turns minor ticks off and caps each axis at four ticks with `MaxNLocator(nbins=4)` ([bwm_figs.py](https://github.com/int-brain-lab/paper-brain-wide-map/blob/main/brainwidemap/meta/bwm_figs.py)).

**Rastermap (Stringer, Pachitariu et al., Nature Neuroscience 2024)** sets the standard for large neural rasters. Rasters use `imshow` with `gray_r` for non-negative activity, or `RdBu_r` with symmetric limits for z-scored data. Axes are switched off and replaced by a black L-shaped scale bar ("500 neurons", "10 sec."). Panel titles are left-aligned and in normal weight, with bold panel letters placed by an offset transform ([fig_utils.py](https://github.com/MouseLand/rastermap/blob/main/paper/fig_utils.py)). Task context sits behind the data as coloured shaded spans and coloured event lines (green lines mark rewards). In spatial panels the selected neurons are coloured while "all neurons in the recording are in gray" ([PMC11706777](https://europepmc.org/article/PMC/PMC11706777)).

**CEBRA (Schneider, Lee & Mathis, Nature 2023)** sets the reference look for latent embeddings. Points are tiny and translucent (`markersize=0.05`, `alpha=0.4`), so they read as a continuous manifold, coloured by a continuous behavioural label. The library registers a branded colormap, `#4854e9 → #6235e0 → #a045e8 → #bf1bb9 → #d4164f` (blue-violet to crimson). A `grey_fig=True` mode greys out ticks, labels and pane edges so one figure works on both white and black backgrounds ([cebra matplotlib.py](https://github.com/AdaptiveMotorControlLab/CEBRA/blob/main/cebra/integrations/matplotlib.py)). Method comparisons draw an orange median line or bar over black dots for individual runs (n = 100), with shuffled controls as dashed lines ([PMC10172131](https://europepmc.org/article/PMC/PMC10172131)). This is a cleaner modern replacement for bar ± SEM.

**MICrONS (Nature, April 2025)** uses the same grammar for connectomics. Anatomy is grey. A few area colours are used ("Black, VISp; red, VISlm; blue, VISal; green, VISrl"). All nucleus detections are light grey underneath the coloured cell types. Connectivity dots are transparent so that density builds up as darker shade. Layer boundaries are dashed grey. A greyscale heatmap sits above a category-coloured heatmap ([PMC11981939](https://europepmc.org/article/PMC/PMC11981939)).

The rule all four share is **grey means context or non-significance; colour means signal**: IBL's silver mask, Rastermap's grey neurons, MICrONS's grey nuclei and CEBRA's grey default embedding. A second shared rule is **a fixed hue per variable or region across the whole paper**, so readers learn the code once and can stop reading legends. For brain regions, the official Allen CCF colours are the identity palette:
- coarse regions: Isocortex `#70FF71`, HPF `#7ED04B`, STR `#98D6F9`, TH `#FF7080`, HY `#E64438`, MB `#FF64FF`, CB `#F0F080`, fiber tracts `#CCCCCC`
- fine regions, for example: MOp `#1F9D5A`, VISp `#08858C`, CA1 `#7ED04B`, LGd `#FF8084`

([Allen Brain Atlas API](https://api.brain-map.org/api/v2/data/query.json?criteria=model::Structure,rma::criteria,[graph_id$eq1],rma::options[num_rows$eqall])). IBL uses those colours for region *identity* (labels and swatches) and switches to per-variable sequential ramps for *values*. That split is worth copying. For representational similarity matrices, rsatoolbox keeps Kriegeskorte's classic map: blue → cyan → grey → red → yellow, with NaNs and the diagonal set to white ([rsatoolbox colors.py](https://github.com/rsagroup/rsatoolbox/blob/main/src/rsatoolbox/vis/colors.py)).

Exemplars sometimes favour telling categories apart over perceptual uniformity. Rastermap's trimmed `gist_ncar` and the classic RDM map are both non-uniform. That is acceptable when colour encodes an *ordering position* and wrong when it encodes *magnitude*. No exemplar uses an off-white background. The coverage has gaps: population-trajectory papers (Churchland, Shenoy, Jazayeri, Sussillo, Linderman, LFADS), Brain-Score alignment plots, and transformer-circuits.pub figures were not analysed. The transformer-circuits page CSS exposed only `#FAFAFA`, `#e5e5e5` and `#1F1F1E` ([Toy Models of Superposition](https://transformer-circuits.pub/2022/toy_model/index.html)). The skill's trajectory and schematic recipes therefore rest on inference, not on documented exemplars.

## Journals agree on 85–90 mm columns and vector RGB, but split on details

Across venues, figures are built to **single-column widths of 85–90 mm and double-column widths of 174–184 mm**, with **sans-serif text of about 5–8 pt at final size**, and supplied as **RGB vector art with live text**. A skill can store each venue as a preset:

| Venue | Widths (1 / 1.5 / 2 col) | Max height | Font, size | Panel label | Min stroke | Final format |
|---|---|---|---|---|---|---|
| *Nature* | 89 / 120–136 / 183 mm | 170 mm (guide) | Helvetica/Arial, 5–7 pt | **8 pt bold lowercase a, b** | 0.25 pt (max 1) | Vector PDF/SVG/PSD; **no JPEG/TIFF/PNG** main figures |
| Nature research journals (Nat Neurosci, NMI, NHB) | 88 / – / 180 mm | ~130–225 mm by caption length | sans, 5–7 pt | lowercase bold | – | Vector; ≥300 dpi bitmaps |
| *Nature Communications* | 88 / – / 180 mm | – | Helvetica-like, same size throughout | lowercase bold, same size as text | **1 pt** | Vector line art; 1,200 dpi if raster |
| Cell Press (Cell, Neuron) | 85 / 114 / 174 mm | ~200 mm | **Arial only**, 6–8 pt | **Capitals A, B** | 0.5 pt (max 1.5) | TIFF/PDF; RGB; ≤20 MB |
| *Science* (revised articles, 2026) | 90 / "1.5" / 184 mm | – | **Myriad** preferred, ≥6 pt | **9 pt bold capitals** | 0.5 pt | PDF/EPS/AI vector |
| *Science Advances* (Apr 2026) | 90 / ≤144 / 184 mm | 199 mm | Myriad, 8 pt default, 6 pt min | 9 pt bold capitals | 0.28 pt | Vector; RGB not CMYK; **no Word/PowerPoint figures** |
| *PNAS* | ~9×6 / 11×11 / 18×22 cm | ~22 cm | 6–12 pt | not specified | – | 600–900 ppi with type; 1,000–1,200 ppi line art |
| *J. Neurosci.* | 85 / 116 / 176 mm | – | not specified | not specified | – | TIFF/EPS; **fonts converted to outlines** |
| *PLOS Comput Biol* | ≥66.8 mm; text col 132 mm; max 190.5 mm | 222 mm | **Arial/Times/Symbol, 8–12 pt** | not specified | ~0.57 pt (recipe) | **TIFF (LZW) or EPS only**; no PDF |
| *eLife* | ≥100 mm; ≥200 mm full width | – | not specified | not specified | – | TIFF/EPS/AI/PDF at ≥300 dpi |
| NeurIPS / ICLR 2026 | 5.5 in (139.7 mm) text width | 9 in | Times 10 pt body; 9 pt captions | – | "dark enough" | Embedded PDF |
| ICML 2026 | 3.25 in column / 6.75 in full | 9 in | Times 10 pt | no in-figure titles | – | PDF with Type-1 fonts |

Sources: [Nature research figure guide](https://research-figure-guide.nature.com/figures/building-and-exporting-figure-panels/), [Nature specs](https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/), [Nature final submission](https://www.nature.com/nature/for-authors/final-submission), [Nature-branded journals artwork guide](https://www.nature.com/documents/NRJs-guide-to-preparing-final-artwork.pdf), [Nat Neurosci formatting](https://www.nature.com/neuro/submission-guidelines/aip-and-formatting), [Nature Communications](https://www.nature.com/ncomms/submit/how-to-submit), [Cell Press figure guidelines](https://www.cell.com/figureguidelines), [Science revised articles](https://www.science.org/content/page/instructions-authors-revised-research-articles), [Science Advances 2026 guide](https://www.science.org/cms/asset/76887697-528f-4a22-afea-cee904504e76/sciadv_guide_to_preparing_figures_2026.pdf), [PNAS](https://www.pnas.org/author-center/submitting-your-manuscript), [JNeurosci](https://www.jneurosci.org/content/information-authors), [PLOS CB](https://journals.plos.org/ploscompbiol/s/figures), [eLife](https://elife-rp.msubmit.net/html/elife-rp_author_instructions.html), [NeurIPS 2026](https://media.neurips.cc/Conferences/NeurIPS2026/Formatting_Instructions_For_NeurIPS_2026.zip), [ICLR template](https://github.com/ICLR/Master-Template), [ICML 2026](https://media.icml.cc/Conferences/ICML2026/Styles/icml2026.zip).

A skill cannot use one global default, because the venues contradict each other on several points:

- **Font embedding.** Nature wants editable text and says so explicitly: "If you are using Python please use … `Matplotlib.rcParams['pdf.fonttype']=42`" ([Nature specs](https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/)). JNeurosci wants all fonts "converted to outlines and saved as EPS files" ([JNeurosci](https://www.jneurosci.org/content/information-authors)). ICML's text literally asks for Type-1 fonts.
- **Minimum stroke.** The floor ranges from 0.25 pt (Nature) through 0.28 pt (Science Advances) and 0.5 pt (Science, Cell) up to **1 pt at Nature Communications** ([NComms](https://www.nature.com/ncomms/submit/how-to-submit)). A 0.5 pt default fails NComms.
- **Greyscale and patterns.** Science Advances says "Avoid using grayscale" ([Sci Adv 2026](https://www.science.org/cms/asset/76887697-528f-4a22-afea-cee904504e76/sciadv_guide_to_preparing_figures_2026.pdf)), while JNeurosci says grayscale "generally provides a more faithful representation" for a single quantity and prefers textures or line types over colour in bar plots ([JNeurosci](https://www.jneurosci.org/content/information-authors)). Nature asks for solid colours rather than patterns in pie sectors ([Nature specs](https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/)).
- **Maximum height.** Nature gives two figures: 170 mm in its figure guide and 247 mm "full depth" on the final-submission page. 170 mm is the safe value because it leaves room for the legend.

Nature's figure guide is the most design-opinionated of the publisher documents. It prints the **Okabe–Ito/Wong palette with hex codes** (`#000000 #E69F00 #56B4E9 #009E73 #F0E442 #0072B2 #D55E00 #CC79A7`). It says to avoid "red/green combinations and rainbow scales". It asks for text contrast above **4.5:1** (WCAG 2.1 AA) and prefers "coloured boxes combined with black text" to coloured text, and it warns that editors "will recolour text to black or white" where colour is unnecessary ([Nature RFG](https://research-figure-guide.nature.com/figures/building-and-exporting-figure-panels/)). This sits uneasily with IBL's coloured region labels, which appeared in Nature itself, and with the newsroom habit of colour-keyed titles. A skill should treat coloured text as allowed only for direct-label identity cues, and only above 4.5:1 contrast.

The other colour rules all target the same failure. Cell: "red and green should not be used together". Science: also avoid dark blue with yellow, and colours close in hue. JNeurosci: convert red/green to magenta/green. eLife: follow Okabe–Ito Colour Universal Design. NComms "strongly encourage[s]" recolouring rainbow pseudo-colour images into colour-safe pairs ([Cell](https://www.cell.com/figureguidelines), [Science](https://www.science.org/content/page/instructions-authors-revised-research-articles), [NComms](https://www.nature.com/ncomms/submit/how-to-submit)). NeurIPS asks that the paper stay legible when printed in black and white ([NeurIPS 2026](https://media.neurips.cc/Conferences/NeurIPS2026/Formatting_Instructions_For_NeurIPS_2026.zip)).

Rules for text inside figures are close to universal, and a linter can enforce them:
- axes labelled with units in parentheses, e.g. "Firing rate (Hz)" ([Nature specs](https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/)); sentence case ([NComms](https://www.nature.com/ncomms/submit/how-to-submit); [Science](https://www.science.org/content/page/instructions-authors-revised-research-articles))
- SI units with a space before the unit ("ms", not "msec"); comma thousands separators for numbers of five digits or more ([NComms](https://www.nature.com/ncomms/submit/how-to-submit))
- leading zeros on decimals; no minor ticks or gridlines; axes that stop at the data range ([Science](https://www.science.org/content/page/instructions-authors-revised-research-articles))
- no titles inside the figure ([Science](https://www.science.org/content/page/instructions-authors-revised-research-articles); [ICML](https://media.icml.cc/Conferences/ICML2026/Styles/icml2026.zip))
- scale bars rather than magnification factors

Statistics rules are equally consistent. Cell requires individual data points alongside mean ± error. Every venue requires legends that define the error bars, n, the test and the P values ([Cell](https://www.cell.com/figureguidelines); [Nat Neurosci](https://www.nature.com/neuro/submission-guidelines/aip-and-formatting); [PNAS](https://www.pnas.org/author-center/submitting-your-manuscript)). JNeurosci adds two rules of its own: remove the top and right borders ("do not box the panels in") and do not publish two-bar graphs at all.

Changes in 2024–2026 have tightened these rules:
- Nature's figure guide now rejects raster main figures, gives a 170 mm maximum height, recommends 450 dpi images, and bans "any sort of generative AI in figures", including Photoshop content-aware tools ([Nature image integrity](https://research-figure-guide.nature.com/figures/image-integrity/)).
- Science Advances' April 2026 guide moved to RGB, Myriad and a 9/14.4/18.4 cm grid, and banned Word/PowerPoint figures and AI-generated artwork.
- PLOS requires uncropped blot and gel originals from 1 April 2026.
- Cell Press forbids generative-AI image creation or alteration.

For Neuron's optional graphical abstract, the spec is an exact **1200 × 1200 px square at 300 dpi** in Arial 8–12 pt, with no data and a clear reading direction ([Neuron checklist, Dec 2025](https://www.cell.com/pb-assets/journals/EM/MasterFFCs/NEURONFFC-1766175479360.pdf); [Cell GA guide](https://www.cell.com/pb/assets/raw/shared/figureguidelines/GA_guide-1537202744020.pdf)).

## Expert canon reduces to a dozen enforceable rules

The design literature is old and stable, and it is unusually precise. **Rougier, Droettboom and Bourne's "Ten Simple Rules for Better Figures" (2014)** gives the workflow ([PLOS CB](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1003833)):
- know the audience and identify the message *before* plotting
- adapt the figure to the medium
- captions are not optional
- do not trust the defaults
- use colour by data type
- do not mislead
- avoid chartjunk
- message trumps beauty
- use the right tool

Rougier's 2021 open-access book turns these into matplotlib practice. Build the figure at final size with the figure font equal to the body text. Use one font family. Put a thin outline stroke on text that sits over images. Prefer direct labels. Use `TwoSlopeNorm` when the centre of diverging data is off-centre. Build gradients in CIELab, not raw sRGB. Keep colour meanings consistent across figures ([typography.rst](https://github.com/rougier/scientific-visualization-book/blob/master/rst/typography.rst); [colors.rst](https://github.com/rougier/scientific-visualization-book/blob/master/rst/colors.rst)). In his dpi comparison, "only the 600 dpi output is acceptable" ([anatomy.rst](https://github.com/rougier/scientific-visualization-book/blob/master/rst/anatomy.rst)).

The *Nature Methods* "Points of View" columns provide most of the field's few numerical style rules ([Wong collection PDF](https://static1.squarespace.com/static/587e7412be6594f2dc02480f/t/63e0d7f70f60c8044b65b900/1675679747977/Bang_Wong_Point-of-view_collection.pdf)):

- **Axes and grids** (Krzywinski): "Axis weight should be modest — 0.5 pt is sufficient", and figures should not be boxed on all sides. "No grid may be better than a badly chosen one". If a grid is used, its opacity should be at least 15% and at most 25–45%.
- **Colour coding** (Wong): spiral through hue and saturation while varying lightness so a set survives greyscale. Keep sets to 6–8 colours. Thinner lines need larger hue and lightness differences.
- **Labels and arrows**: one typeface at a fixed size, callouts at fixed 30° or 45° angles, closed arrowheads rather than open "V" heads, and "variety should be informed by data, not formatting".
- **Accessibility**: replace red with magenta. This matters directly for GCaMP/tdTomato-style two-channel overlays.

Wilke's *Fundamentals of Data Visualization* supplies the thresholds:
- **3–5 categorical colours is ideal; above about 8, use direct labels instead** ([Ch. 19](https://clauswilke.com/dataviz/color-pitfalls.html)).
- "Avoid large filled areas of overly saturated colors."
- Bars on a linear scale start at 0, and on a log scale at 1 ([Ch. 17](https://clauswilke.com/dataviz/proportional-ink.html)).
- "Whenever possible, design your figures so they don't need a legend" ([Ch. 20](https://clauswilke.com/dataviz/redundant-coding.html)).
- Small multiples share axes and appear in a logical order ([Ch. 21](https://clauswilke.com/dataviz/multi-panel-figures.html)).
- Titles belong in the caption, not on the plot ([Ch. 22](https://clauswilke.com/dataviz/figure-titles-captions.html)).
- Axis labels are almost always too small, so check a scaled-down version ([Ch. 24](https://clauswilke.com/dataviz/small-axis-labels.html)).

Wilke also corrects Tufte: "Maximize the data–ink ratio, *within reason*". Over-minimal figures leave elements "float[ing] in space", and grid lines perpendicular to the key variable earn their place ([Ch. 23](https://clauswilke.com/dataviz/balance-data-context.html)). Empirical work backs the softer position. Bateman et al. found embellished charts were read just as accurately and remembered better weeks later ([CHI 2010](https://dblp.uni-trier.de/rec/conf/chi/BatemanMGGMB10.html)). Borkin et al. found colour and recognisable objects raise memorability across 2,070 visualisations ([PubMed](https://pubmed.ncbi.nlm.nih.gov/24051797/)). For a paper, accuracy comes first. For a talk or graphical abstract, one accent colour and a clear visual hook are justified.

Perception research sets the encoding priority. **Cleveland and McGill's ranking** runs from position on a common scale, through position on non-aligned scales, length/direction/angle, area, and volume/curvature, down to shading and colour saturation ([JASA 1984](https://math.pku.edu.cn/teachers/xirb/Courses/biostatistics/Biostatistics2016/GraphicalPerception_Jasa1984.pdf)). The comparison that matters most should therefore never rely on colour alone. Banking to 45° argues for wide, short panels for oscillatory traces such as LFP and calcium, and squarer panels for slow trends ([eagereyes](https://eagereyes.org/basics/banking-45-degrees)).

Statistics display is where neuroscience figures most often fall short. Weissgerber et al. reviewed 703 physiology papers. **85.6% used bar graphs**, 77.6% of those showed mean ± SE, and the median minimum group size was **n = 4**. For small studies they recommend univariate scatterplots, which show what bars hide ([PLoS Biol 2015](https://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.1002128)). There are two modern replacements. **Raincloud plots** combine a half violin, jittered raw points and a box plot ([Allen et al. 2019](https://europepmc.org/article/PMC/PMC6480976)). **Estimation plots** (Gardner–Altman for two groups, Cumming plots for more) show every point plus a 5,000-resample BCa bootstrap 95% CI of the effect on an aligned axis ([Ho et al. 2019](https://www.nature.com/articles/s41592-019-0470-3); [DABEST](https://acclab.github.io/DABEST-python/tutorials/01-basics.html)).

Cumming, Fidler and Vaux's error-bar rules are directly relevant to nested neuroscience data ([J Cell Biol 2007](https://europepmc.org/article/PMC/PMC2064100)):
- Always say what the error bars are and what n is.
- Show error bars only for independent replicates. Triplicate cultures repeated four times give n = 4, not 12.
- At n = 3, plot the points rather than error bars.
- For within-subject comparisons, plot differences rather than group SE.

Applied to neuroscience: cells are not animals. A skill should colour points by animal or session and draw per-animal summaries.

## Validated palettes carry the data; trend palettes set the mood

### The CVD-safe categorical core

Colour is where expert consensus is strongest, and where matplotlib's default is weakest. About **8% of men and 0.5% of women** have a colour-vision deficiency (CVD), mostly red–green ([Crameri et al. 2020](https://europepmc.org/article/PMC/PMC7595127); [Wilke](https://clauswilke.com/dataviz/color-pitfalls.html)). Okabe and Ito estimate that a paper with three male reviewers has about a 22% chance of reaching at least one colour-blind reader ([jfly](https://jfly.uni-koeln.de/color/)). Three sources of categorical palettes are well tested:

| Palette | Hex (default order) | Source |
|---|---|---|
| Okabe–Ito | `#000000 #E69F00 #56B4E9 #009E73 #F0E442 #0072B2 #D55E00 #CC79A7` | [jfly](https://jfly.uni-koeln.de/color/) |
| Tol bright | `#4477AA #EE6677 #228833 #CCBB44 #66CCEE #AA3377 #BBBBBB` | [Paul Tol](https://sronpersonalpages.nl/~pault/) |
| Tol muted | `#CC6677 #332288 #DDCC77 #117733 #88CCEE #882255 #44AA99 #999933 #AA4499` (bad data `#DDDDDD`) | [Paul Tol](https://sronpersonalpages.nl/~pault/) |
| Tol high-contrast | `#004488 #DDAA33 #BB5566` (greyscale-safe) | [Paul Tol](https://sronpersonalpages.nl/~pault/) |
| Tol dark (≥4.5:1 on white) | `#4477BB #CC4466 #228833 #2255AA #993366 #006644 #117788 #882288 #BB4488 #775500 #444444` | [Paul Tol](https://sronpersonalpages.nl/~pault/) |
| Tol vibrant | `#EE7733 #0077BB #33BBEE #EE3377 #CC3311 #009988 #BBBBBB` | [Paul Tol](https://sronpersonalpages.nl/~pault/) |
| petroff6 | `#5790FC #F89C20 #E42536 #964A8B #9C9CA1 #7A21DD` | [Petroff 2021](https://arxiv.org/abs/2107.02270); [matplotlib stylelib](https://github.com/matplotlib/matplotlib/tree/main/lib/matplotlib/mpl-data/stylelib) |
| petroff10 | `#3F90DA #FFA90E #BD1F01 #94A4A2 #832DB6 #A96B59 #E76300 #B9AC70 #717581 #92DADD` | same |

Petroff's 2021 paper gives the only explicit published thresholds. For sets of 6, 8 and 10 colours, the minimum CAM02-UCS distance under simulated CVD should be **20, 18 and 16**. Lightness should stay within J′ 40–84, and markers on white should stay below L* ≈ 85 ([Petroff 2021](https://arxiv.org/abs/2107.02270)). Tol's page was updated through August 2026 and has moved to sronpersonalpages.nl. Its new "dark", "pale" and "incandescent" schemes are missing from the stale `tol_colors.py` v2022.10, so a skill should hard-code the hex values from the web page ([Tol](https://sronpersonalpages.nl/~pault/)).

The research team checked these palettes with their own computation: colorspacious Machado-2009 simulation at full severity, plus CIEDE2000 distances. This is not a published result, so the numbers depend on the pipeline. Under protan and deutan simulation, the minimum pairwise ΔE00 was about 11–12 for Okabe–Ito and 14–15 for Tol bright. **matplotlib's default `tab10` fell to 1.3–3.3**: some of its colours become effectively identical for red–green-deficient readers. The same check flagged low contrast against white for Okabe–Ito yellow `#F0E442` (1.32:1), sky blue (2.31:1) and orange (2.25:1). Use blue `#0072B2` (5.19:1) and vermilion `#D55E00` (3.87:1) for thin lines and text. Okabe and Ito give the same advice: "For thin lines and small objects, use darker blue and orange" ([jfly](https://jfly.uni-koeln.de/color/)). WCAG sets the thresholds the checker should test: **4.5:1 for text, 3:1 for graphical objects needed to understand the chart** ([W3C 1.4.11](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html)).

### Colormaps by data class, mapped to neuroscience quantities

Crameri, Shephard and Heron show that jet can distort the reading of data by **more than 7% of the displayed variation**. Its bright yellow band draws attention to the middle of the scale and creates false boundaries. Turbo looks ordered but still fails on uniform lightness ([Crameri 2020](https://europepmc.org/article/PMC/PMC7595127)). Kovesi found flat spots in vendor colormaps that can hide features as large as a tenth of the data range ([arXiv:1509.03700](https://arxiv.org/abs/1509.03700)). The required properties are perceptual uniformity, perceptual order (monotonic lightness), CVD-friendliness and greyscale readability. Crameri adds two rules: never squeeze or cut a scientific colormap, and always include a colorbar, since leaving it out "would be equivalent to not including the axis labels" ([Crameri 2020](https://europepmc.org/article/PMC/PMC7595127)). The SCM v8 anchors below were sampled from the cmcrameri LUTs. Use the repo's `main` branch: `master` still holds v7, and bilbao, lajolla, grayC, acton, bamako, batlowK and tokyo changed between versions ([cmcrameri](https://github.com/callumrollo/cmcrameri/tree/main/cmcrameri/cmaps)).

| Neuro quantity | Class | Recommended map | Anchor hex (low → high) |
|---|---|---|---|
| Firing rate, power, density | Sequential | viridis | `#440154 #3B528B #21918C #5CC863 #FDE725` |
| Same, CVD-optimised | Sequential | cividis | `#00224E #434E6C #7D7C78 #BBAD6D #FEE838` |
| Same, "scientific rainbow" | Sequential | batlow (SCM v8) | `#011959 #226061 #828231 #F19D6B #FACCFA` |
| Same, modern warm | Sequential | lipari | `#031326 #525B7A #A56267 #E99973 #FDF5DA` |
| Same, modern cool | Sequential | navia | `#031327 #1B608F #418A80 #87C269 #FCF4D9` |
| z-scores, t-maps, ΔF/F, correlation (white bg) | Diverging, light centre | vik | `#001261 #116496 #A7C9DA #ECE5E0 #E1B8A0 #B75A26 #590008` |
| Same, Tol print-safe | Diverging | sunset | `#364B9A #6EA6CD #C2E4EF #EAECCC #FEDA8B #F67E4B #A50026` |
| Stat maps on dark backgrounds or slides | Diverging, dark centre | berlin | `#9EB0FF #3280A6 #112732 #190C09 #5F1F0A #CA7B71 #FFADAD` |
| LFP phase, preferred orientation, direction | Cyclic | romaO | `#733957 #AA752F #CBE1B3 #5495C0 #723959` |
| Many unordered classes | Categorical from sequential | batlowS | `#011959 #FACCFA #828231 #226061 #F19D6B #4D734D` |

Sources: [matplotlib _cm_listed.py](https://github.com/matplotlib/matplotlib/blob/main/lib/matplotlib/_cm_listed.py), [cmcrameri](https://github.com/callumrollo/cmcrameri/tree/main/cmcrameri/cmaps), [Tol](https://sronpersonalpages.nl/~pault/), [viridis rationale](https://bids.github.io/colormap/), [cividis paper](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0199239).

Several details matter in practice:
- **matplotlib 3.10 ships `berlin`, `managua` and `vanimo` natively**, so dark-centre diverging maps need no extra dependency ([3.10 what's new](https://github.com/matplotlib/matplotlib/blob/v3.11.0/doc/release/prev_whats_new/whats_new_3.10.0.rst)).
- nilearn 0.14 now defaults stat maps to `RdBu_r` ([nilearn API](https://nilearn.github.io/stable/modules/plotting.html)).
- Tol warns that all diverging schemes fail in greyscale, and that if several are used in one figure, none should have its direction reversed ([Tol](https://sronpersonalpages.nl/~pault/)).
- Crameri recommends separating heatmap tiles with gaps, because tiles that touch shift each other's apparent colour ([Crameri 2020](https://europepmc.org/article/PMC/PMC7595127)).

### What 2024–2026 design culture contributes

Newsrooms and product design systems offer a modern visual layer on top of this foundation.

**Grey first, then one accent.** Datawrapper's Lisa Charlotte Muth puts the method plainly: "Gray is the most important color in data visualization". Grey out every category first, then colour only what matters with one saturated accent, and use a grey tinted toward the background rather than a neutral one ([Datawrapper](https://www.datawrapper.de/blog/emphasize-with-color-in-data-visualizations); [style guides](https://www.datawrapper.de/blog/colors-for-data-vis-style-guides)). This is the IBL and Rastermap grammar again, arrived at from journalism.

**House colour systems.** Editorial palettes use a fixed hue order and add shades of existing hues rather than new hues:
- FT background "paper" `#FFF1E5`, with chart grey `#D9CDC3`, oxford `#0F5499` and claret `#990F3D` ([o-colors](https://unpkg.com/@financial-times/o-colors/src/scss/_palette.scss)).
- The Economist's three-hue system: `#0E6BA0`, `#30C0D2`, red `#ED1319` for lines and `#973D4C` for areas, with tinted greys `#878771`/`#CFD1C3` ([Datawrapper](https://www.datawrapper.de/blog/colors-for-data-vis-style-guides)).
- Our World in Data's earthy "Distinct (lines)" set, tuned for line contrast on white: `#4C6A9C #B13507 #996D39 #2C8465 #6D3E91 #883039 #00295B #A2559C #9A5129 #008291` ([owid-grapher](https://github.com/owid/owid-grapher/blob/master/packages/@ourworldindata/grapher/src/color/CustomSchemes.ts)). OWID's set is the most "scholarly" of the newsroom palettes and suits multi-condition plots.

**Perceptual colour construction.** Design systems have moved to perceptual colour spaces. Tailwind v4 (January 2025) rebuilt its whole palette in **OKLCH**, and v4.2 (February 2026) added tinted neutrals: mauve `#79697B`, olive `#7C7C67`, mist `#67787C` and taupe `#7C6D67` ([Tailwind v4](https://tailwindcss.com/blog/tailwindcss-v4); [changelog](https://github.com/tailwindlabs/tailwindcss/blob/main/CHANGELOG.md)). IBM Carbon ships an ordered 14-colour categorical palette ("applied in sequence strictly") in separate light and dark versions. Its light version starts `#6929C4 #1192E8 #005D5D #9F1853 #FA4D56`. Carbon also ships Purple↔Teal diverging and Purple, Teal and Cyan sequential ramps that fit a "neuro" look ([Carbon](https://carbondesignsystem.com/data-visualization/color-palettes/); [@carbon/charts CSS](https://unpkg.com/@carbon/charts/dist/styles.css)). Evil Martians argue that OKLCH's predictable lightness makes accessible palettes something you can generate by formula ([Evil Martians](https://evilmartians.com/chronicles/oklch-in-css-why-quit-rgb-hsl)). For a figure skill, that means building sequential ramps with monotonic L, categorical sets at matched chroma but *staggered* lightness, and dark-mode variants by raising L. Datawrapper adds a warning: equal-lightness sets look harmonious but become indistinguishable in greyscale ([Datawrapper](https://www.datawrapper.de/blog/beautifulcolors)).

**Trend forecasts.** Forecasts point toward calm canvases with energetic accents. Pantone moved from Peach Fuzz `#FFBE98` (2024) to Mocha Mousse `#A47864` (2025) to **Cloud Dancer `#F0EEE9` (2026), the first white ever chosen** ([Fast Company](https://www.fastcompany.com/91446151/pantones-2026-color-of-the-year-is-visual-tofu); [muz.li](https://colors.muz.li/color/mocha-mousse)). WGSN/Coloro's 2027 colour is "Luminous Blue" (no hex published) ([WGSN](https://www.wgsn.com/en/wgsn/press/press-releases/wgsn-and-coloro-reveal-colour-year-2027-luminous-blue-and-s-s-27-key)). Adobe's 2026 trends pair saturated "high-energy" palettes with organic, editorial layouts ([Adobe Express](https://www.adobe.com/express/learn/blog/design-trends-2026)). Traditional Japanese colours give sourced, low-chroma sets that look designed rather than default, for example indigo KON `#0F2540`, AI `#0D5661`, HANADA `#006284`, ASAGI `#33A6B8` and SUMI `#1C1C1C` ([nipponcolors dump](https://gist.github.com/RobertYim/3061171b1dbfa93d7f71720e94403382)).

**Typography.** The contemporary choice for data and UI is a screen-native neo-grotesque with tabular numerals:
- **Inter v4.1**, **Geist v1.7.2 (June 2026)** and **IBM Plex** are all OFL-licensed and so can be embedded in journal PDFs ([Inter](https://github.com/rsms/inter); [Geist](https://github.com/vercel/geist-font); [Plex](https://github.com/IBM/plex)).
- These fonts fit the "Helvetica or Arial" rules in spirit only. Nature, Nature-family and Cell submissions should stay with Arial/Helvetica (Cell says "only Arial"). Science should use Myriad or Arial. Inter or Geist are better kept for talks, posters, preprints and ML papers.

**The tension a skill must resolve.** Almost none of these trend palettes were published with CVD testing. Datawrapper explicitly flags an "earthy" nine-hue set as problematic for red-blind readers ([Datawrapper](https://www.datawrapper.de/blog/colors-for-data-vis-style-guides)). The editorial off-white canvas also conflicts with journal rules: Science Advances says "Use white backgrounds", and NComms asks for a white background ([Sci Adv 2026](https://www.science.org/cms/asset/76887697-528f-4a22-afea-cee904504e76/sciadv_guide_to_preparing_figures_2026.pdf); [NComms](https://www.nature.com/ncomms/submit/how-to-submit)). The workable split is:
- **Journal figures:** a white background; trend hues allowed only as validated accents (one dominant hue, plus a background-tinted grey for context) and as per-variable sequential ramps generated in OKLCH and checked for monotonic lightness.
- **Talks, posters, lab websites and preprint thumbnails:** off-white canvases (`#F0EEE9`, `#F5F4EF`), dark mode with dark-centre diverging maps, and Inter or Geist type.

## matplotlib 3.11 does it all once five defaults are fixed

The local `neuroai` environment has matplotlib 3.11.2, seaborn 0.13.2, nilearn 0.14.1, MNE 1.13.2, PyVista 0.49.0 and pycortex 1.3.2. The researchers tested this stack directly. It can produce every exemplar style above, but the shipped defaults conflict with journal requirements in five places:

1. **Fonts.** `pdf.fonttype` and `ps.fonttype` default to 3. `pdffonts` showed Type 3 fonts, which Nature rejects. Setting `pdf.fonttype=42` produced embedded CID TrueType subsets ([matplotlib fonts](https://matplotlib.org/stable/users/explain/text/fonts.html)). SVG defaults to `svg.fonttype='path'`, which turns text into outlines; `'none'` writes live `<text>` elements but does not embed the font.
2. **Exact sizes.** `bbox_inches='tight'` changes the output size: an 89 × 60 mm figure saved 3% larger. Exact journal widths need `layout='constrained'` with `savefig.bbox=None`. tueplots does this; SciencePlots does not ([tueplots figsizes.py](https://github.com/pnkraemer/tueplots/blob/main/tueplots/figsizes.py)).
3. **Mathtext.** It keeps rendering in DejaVu even when the text font is changed. A PDF with Inter labels still embedded `DejaVuSans-Oblique` for `$\lambda_i$` until `mathtext.fontset='custom'` was set. In 3.11, `mathtext.default: it` now italicises digits, so set it to `normal` ([mathtext docs](https://matplotlib.org/stable/users/explain/text/mathtext.html); [3.11 what's new](https://github.com/matplotlib/matplotlib/blob/v3.11.0/doc/release/prev_whats_new/whats_new_3.11.0.rst)).
4. **Colour cycle.** The default `tab10` fails the CVD check described in the colour section.
5. **Physical units.** 3.11 accepts `figsize=(w, h, 'cm')` but rejects `'mm'`, so the skill should convert with `MM = 1/25.4`.

A verified baseline preset combines Nature specs, IBL rcParams and these fixes:

```python
MM = 1/25.4
NATURE_RC = {
  "font.family": "sans-serif",
  "font.sans-serif": ["Arial", "Helvetica", "Liberation Sans", "Inter", "DejaVu Sans"],
  "font.size": 7, "axes.labelsize": 7, "axes.titlesize": 7,
  "xtick.labelsize": 6, "ytick.labelsize": 6, "legend.fontsize": 6,
  "axes.linewidth": 0.5, "lines.linewidth": 1.0, "lines.markersize": 3,
  "xtick.major.size": 2.5, "ytick.major.size": 2.5,
  "xtick.major.width": 0.5, "ytick.major.width": 0.5,
  "xtick.minor.visible": False, "ytick.minor.visible": False,
  "axes.spines.top": False, "axes.spines.right": False,
  "axes.titlelocation": "left", "legend.frameon": False,
  "axes.prop_cycle": "cycler(color=['#0072B2','#D55E00','#009E73','#CC79A7','#E69F00','#56B4E9','#000000'])",
  "mathtext.fontset": "custom", "mathtext.rm": "Liberation Sans",
  "mathtext.it": "Liberation Sans:italic", "mathtext.bf": "Liberation Sans:bold",
  "mathtext.default": "normal",
  "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
  "savefig.dpi": 600, "savefig.bbox": None, "savefig.pad_inches": 0.01,
  "figure.constrained_layout.use": True,
}
# fig = plt.figure(figsize=(183*MM, 100*MM)); verify with `pdffonts fig.pdf` (no Type 3 rows)
```

The values come from [ibl-style](https://github.com/int-brain-lab/ibl-style/blob/main/src/ibl_style/style.py), the [Nature specs](https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/) and the [matplotlib 3.11 notes](https://github.com/matplotlib/matplotlib/blob/v3.11.0/doc/release/prev_whats_new/whats_new_3.11.0.rst). The colour cycle reorders Okabe–Ito so the high-contrast colours come first. Arial and Helvetica are **not installed on this machine**. Liberation Sans is metric-compatible with Arial and is the right fallback. Installing `ttf-mscorefonts-installer` would be a system-wide change that needs the user's approval.

**Layout.** `subplot_mosaic` with `width_ratios`, `subfigures`, `fig.align_ylabels` and a shared `fig.colorbar(im, ax=[...])` covers multi-panel composition at exact width. Place panel letters with the official recipe, `ax.transAxes + ScaledTranslation(dx/72, dy/72, fig.dpi_scale_trans)`, so the offset is in points ([matplotlib gallery](https://matplotlib.org/stable/gallery/text_labels_and_annotations/label_subplots.html)). Range frames (`spines['left'].set_bounds`) and outward spine offsets both work on 3.11.2 ([Spines API](https://matplotlib.org/stable/api/spines_api.html)).

**Dense data.** `rasterized=True` on a 20,000-point scatter cut a vector PDF from 312 KB to 31 KB. This is the right treatment for spike rasters and CEBRA-style embeddings. PLOS and JNeurosci need TIFF output: use `pil_kwargs={'compression':'tiff_lzw'}`.

**Text over images.** For labels over heatmaps, brain maps and micrographs, use `path_effects=[pe.withStroke(linewidth=2.5, foreground='w')]`, which is Rougier's outline-stroke fix ([patheffects guide](https://matplotlib.org/stable/users/explain/artists/patheffects_guide.html)).

The third-party ecosystem is uneven under matplotlib 3.11, so a skill should copy design ideas rather than add dependencies:

| Package | Version (Oct 2026) | Status on mpl 3.11 | Use in skill |
|---|---|---|---|
| SciencePlots | 2.2.2 | Imports with deprecation warnings (breaks at 3.13) | Reference only; its default `science` style is serif with LaTeX, a poor fit for neuro journals |
| tueplots | 0.2.4 | Works; **no NeurIPS/ICML/ICLR 2025–26 bundles** | Copy its composable rc-dict design; ML sizes NeurIPS 9/7 pt, ICML 8/6 pt |
| cmcrameri | 1.10 (SCM 8.0) | Works; names `cmc.batlow` etc. | Optional colormap dependency |
| cmasher / colorcet / cmocean | 1.9.2 / 3.2.1 / 4.0.3 | Work (cmasher warns) | Optional |
| colorspacious / coloraide / daltonlens | 1.1.2 / 8.13 / 0.1.5 | Work | CVD simulation, CIEDE2000 and OKLCH for the palette checker |
| statannotations / ptitprince | 0.7.2 / 0.3.1 | Work with seaborn 0.13.2 | Optional; plain seaborn half-violins are enough |
| UltraPlot | 2.7.0 | Runtime error in test (possibly install artifact) | Avoid |
| mplcyberpunk | 0.7.6 | **Fails to import** | Reimplement glow with path effects |

Sources: [SciencePlots](https://github.com/garrettj403/SciencePlots), [tueplots bundles](https://github.com/pnkraemer/tueplots/blob/main/tueplots/bundles.py), [cmcrameri](https://github.com/callumrollo/cmcrameri), [CMasher](https://cmasher.readthedocs.io/), [colorspacious](https://colorspacious.readthedocs.io/en/latest/reference.html), [ColorAide](https://facelessuser.github.io/coloraide/), [DaltonLens](https://github.com/DaltonLens/DaltonLens-Python), [statannotations](https://github.com/trevismd/statannotations), [PtitPrince](https://github.com/pog87/PtitPrince), [mplcyberpunk](https://github.com/dhaitz/mplcyberpunk).

matplotlib now ships `okabe_ito`, `petroff6`, `petroff8` and `petroff10` as colour sequences (3.10/3.11), so the safe palettes need no extra package ([3.11 what's new](https://github.com/matplotlib/matplotlib/blob/v3.11.0/doc/release/prev_whats_new/whats_new_3.11.0.rst)). Code written to last until matplotlib 3.13 should follow these rules:
- Use `tick_labels=`, because `labels=` has been removed.
- Use `orientation=`, because `vert=` is deprecated.
- Build colormaps without `ListedColormap(N=)`.
- Load styles through dotted package paths rather than `style.core` internals.
- Pin seaborn to 0.13.*, the latest release since January 2024.

**Neuro-viz libraries.** Each one has hooks the skill should set explicitly:
- **nilearn:** pass `black_bg=False`, an explicit `cmap` and `axes=`, so stat maps draw into the skill's grid.
- **MNE:** `Brain` defaults to `background='black'`. Override it and use `save_image(mode='rgba')`.
- **PyVista:** render off-screen with `screenshot(transparent_background=True, scale=2–4)`, then `imshow` the PNG into a matplotlib axis so 3D panels share fonts and panel letters with the rest of the figure.
- **pycortex:** `quickflat.make_figure(fig=ax)` embeds flatmaps directly.
- **BrainGlobe:** gives canonical Allen region colours via `rgb_triplet`.

Sources: [nilearn](https://nilearn.github.io/stable/modules/plotting.html), [MNE Brain](https://mne.tools/stable/generated/mne.viz.Brain.html), [PyVista](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter), [pycortex](https://gallantlab.org/pycortex/), [brainglobe-atlasapi](https://github.com/brainglobe/brainglobe-atlasapi).

**Statistics panels.** Dependency-free rainclouds can be built from seaborn alone (`violinplot(split=True, inner=None, cut=0)`, a narrow `boxplot`, a jittered `stripplot`) or with matplotlib's `violinplot(side='high')` ([seaborn violinplot](https://seaborn.pydata.org/generated/seaborn.violinplot.html)).

**Schematics.** Network diagrams and model schematics can stay in matplotlib with `FancyBboxPatch`, `FancyArrowPatch` using closed `-|>` heads (per Wong), `ConnectionPatch` across axes, and gradient fills via `imshow` clipped to a patch. Schematics should use the same 0.5–0.8 pt lines and 6–7 pt text as the data panels ([ArrowStyle API](https://matplotlib.org/stable/api/_as_gen/matplotlib.patches.ArrowStyle.html)).

## Conclusion

The evidence reframes the task. Figures look "beautiful" in high-impact neuroscience mainly through *consistency under constraint*: one semantic colour per variable kept across the whole paper, grey everywhere else, and identical line weights and type sizes in every panel, including schematics and 3D renders pulled in as images. No trend palette produces that on its own. So the skill should be built as a **compliance-and-consistency engine** rather than a theme. It needs three parts:
- **Venue presets** that encode the real disagreements between journals: panel-letter case, 0.25 vs 0.5 vs 1 pt stroke floors, editable vs outlined fonts, PDF vs TIFF output.
- **A semantic colour registry**, mapping variables to hues and ramps, populated only from validated palettes or OKLCH-generated ramps.
- **An automated checker** for problems a human misses: Type-3 fonts, text under 5–6 pt at final size, more than 8 categorical colours, CVD-simulated ΔE below about 10, contrast below 3:1 for marks or 4.5:1 for text, non-monotonic colormap lightness, a missing colorbar, and bar ± SEM drawn without the data points.

Contemporary design then enters through a narrow, controlled channel: one luminous accent, background-tinted context greys, OKLCH-built ramps, and, outside journal pages, off-white canvases and Inter or Geist type.

Three open questions should shape the next round of work:
- No documented exemplar was found for latent-trajectory rendering, NeuroAI learning curves or model-brain alignment plots, even though these are central NeuroAI figure types. Those recipes will be inferred until someone inspects the actual figures.
- The CVD pass thresholds come partly from the team's own calibration. They should be reported together with the simulation pipeline used, not presented as a standard.
- Several specs are snapshots that could be stale: Cell's page is from April 2025, and both Nature's and Science's guides contradict themselves internally. A skill that cites the source and date next to each preset value will age better than one that hard-codes numbers without that context.
