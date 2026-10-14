"""The palette bank.

    from sciplot import palettes as P
    P.get("okabe_ito", 4)                 # list of hex
    P.cmap("cmc.batlow"); P.cmap("ibl.choice")   # Colormap from any source
    P.search(kind="cat", mood="calm", bg="light", cvd_safe=True)
    P.highlight(5, 2, accent="#D1495B")   # one accent, rest grey
    P.semantic("neuro.opto")              # {'control': ..., 'ChR2': ..., 'ArchT': ...}
    P.info("owid.a")                       # metadata incl. source

Every entry: colors, kind ('cat'|'seq'|'div'|'cyc'|'neutral'), family, bg
('light'|'dark'|'any'), mood (tags), best_for, source. CVD safety is *measured*
(min ΔE2000 under deutan/protan/tritan simulation, see check.palette_report) and
cached in data/cvd.json; `cvd_claim` records what the source itself says.

Families: accessible · neuro (exemplar papers + semantic) · editorial ·
design-system · journal · trend · heritage · art · cinema · theme · riso ·
original (designed here with OKLCH, CVD-tuned).
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import numpy as np

from . import color as C

_DATA = Path(__file__).with_name("data")


def _p(colors, kind="cat", family="original", bg="light", mood=(), best_for="", source="",
       **kw):
    return dict(colors=[c.upper() for c in colors], kind=kind, family=family, bg=bg,
                mood=list(mood), best_for=best_for, source=source, **kw)


# =============================================================================
# 1. ACCESSIBLE CLASSICS
# =============================================================================
BANK: dict[str, dict] = {
    "okabe_ito": _p(["#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00",
                     "#CC79A7", "#000000"], family="accessible", bg="light",
                    mood=["classic", "safe", "bright"], best_for="default CVD-safe categorical (≤8)",
                    source="Okabe & Ito 2008; Wong, Nat Methods 8:441 (2011)", cvd_claim=True),
    "okabe_ito_no_yellow": _p(["#0072B2", "#E69F00", "#009E73", "#D55E00", "#56B4E9",
                               "#CC79A7", "#000000"], family="accessible",
                              mood=["classic", "safe"], best_for="lines on white (yellow dropped)",
                              source="Okabe-Ito reordered for thin lines", cvd_claim=True),
}

# =============================================================================
# 2. NEURO — exemplar papers & semantic sets
# =============================================================================
BANK.update({
    # IBL Brain-Wide Map (Nature 2025): one sequential hue family per task variable
    "ibl.stimulus": _p(["#EAF4B3", "#D5E1A0", "#A3C968", "#86AF40", "#517146", "#33492E"], "seq", "neuro",
                       mood=["organic", "green"], best_for="stimulus-encoding maps",
                       source="IBL paper-brain-wide-map bwm_figs.py"),
    "ibl.choice": _p(["#F8E4AA", "#F9D766", "#E8AC22", "#DA4727", "#96371D"], "seq", "neuro",
                     mood=["warm"], best_for="choice-encoding maps", source="IBL bwm_figs.py"),
    "ibl.feedback": _p(["#F1D3D0", "#F5968A", "#E34335", "#A23535", "#842A2A"], "seq", "neuro",
                       mood=["warm", "red"], best_for="reward/feedback maps", source="IBL bwm_figs.py"),
    "ibl.prior": _p(["#D0CDE4", "#998DC3", "#6159A6", "#42328E", "#262054"], "seq", "neuro",
                    mood=["cool", "violet"], best_for="prior/block, speed maps", source="IBL bwm_figs.py"),
    "ibl.movement": _p(["#C1E1EA", "#91D0FA", "#5DA5F1", "#2A71D7", "#0045B1"], "seq", "neuro",
                       mood=["cool", "blue"], best_for="movement maps", source="IBL bwm_figs.py"),
    "ibl.variables": _p(["#86AF40", "#E8AC22", "#E34335", "#6159A6", "#2A71D7"], "cat", "neuro",
                        mood=["semantic"], best_for="one color per task variable (mid-steps of IBL ramps)",
                        source="derived from IBL ramps"),
    "cebra": _p(["#4854E9", "#6235E0", "#A045E8", "#BF1BB9", "#D4164F"], "seq", "neuro", bg="any",
                mood=["vivid", "electric"], best_for="embedding colored by time/position",
                source="CEBRA cebra/integrations/matplotlib.py"),
    "allen.ccf": _p(["#70FF71", "#9AD2BD", "#7ED04B", "#8ADA87", "#98D6F9", "#8599CC", "#FF7080",
                     "#E64438", "#FF64FF", "#FF9B88", "#FF9BCD", "#F0F080"], "cat", "neuro",
                    mood=["atlas"], best_for="region identity (swatches/labels), not values",
                    source="Allen Brain Atlas API structure graph 1",
                    labels=["Isocortex", "OLF", "HPF", "CTXsp", "STR", "PAL", "TH", "HY", "MB",
                            "P", "MY", "CB"]),
    "rsa.classic": _p(["#0000FF", "#00FFFF", "#808080", "#FF0000", "#FFFF00"], "seq", "neuro",
                      mood=["legacy"], best_for="Kriegeskorte-style RDMs (NOT perceptually uniform)",
                      source="rsatoolbox vis/colors.py (RDMcolormap.m)"),
})

# semantic mappings — label -> color. Chosen for CVD separation + conventions.
SEMANTIC: dict[str, dict[str, str]] = {
    "neuro.ei": {"excitatory": "#D1495B", "inhibitory": "#2E6DB4"},
    "neuro.lr": {"left": "#2E6DB4", "right": "#D1495B"},            # IBL: left blue, right red
    "neuro.opto": {"control": "#8A8F98", "ChR2 (473 nm)": "#2F80ED", "ArchT/eNpHR (532-593 nm)": "#E8A317"},
    "neuro.model_data": {"data": "#1F2328", "model": "#E07A3F", "shuffle/null": "#B8BCC2",
                         "alt. model": "#4C78A8"},
    "neuro.split": {"train": "#4C78A8", "validation": "#F2A541", "test": "#D1495B"},
    "neuro.outcome": {"correct": "#2A9D8F", "error": "#D1495B", "miss": "#B8BCC2"},
    "neuro.bands": {"delta": "#3B4CC0", "theta": "#2A9D8F", "alpha": "#8AB17D",
                    "beta": "#E9C46A", "gamma": "#E76F51"},
    "neuro.cortical_layers": {"L1": "#F3E6C9", "L2/3": "#E9B872", "L4": "#C8553D",
                              "L5": "#7A3B69", "L6": "#2D3047"},
    "neuro.cell_class": {"Excitatory": "#3C7DC4", "Pvalb": "#D1495B", "Sst": "#F2A541",
                         "Vip": "#8E6BBF", "Lamp5": "#E58FB0", "Non-neuronal": "#9AA0A6"},
    "neuro.areas_visual": {"VISp": "#1F2328", "VISl": "#D1495B", "VISal": "#2E6DB4",
                           "VISrl": "#2A9D8F", "VISam": "#F2A541", "VISpm": "#8E6BBF"},
    "neuro.species": {"mouse": "#8E6BBF", "macaque": "#E07A3F", "human": "#2A9D8F", "model": "#4C78A8"},
    "sign": {"positive": "#0976B1", "negative": "#EF2F2F", "zero": "#C7C5C3"},   # Datawrapper
    "status": {"danger": "#DA1E28", "serious": "#FF832B", "warning": "#F1C21B", "success": "#198038"},
}

# =============================================================================
# 3. EDITORIAL house styles (newsrooms)
# =============================================================================
BANK.update({
    "ft": _p(["#0F5499", "#990F3D", "#0D7680", "#FF8833", "#593380", "#96CC28", "#00A0DD"],
             family="editorial", bg="light", mood=["editorial", "financial", "warm-paper"],
             best_for="on FT paper #FFF1E5; oxford first, claret second, green last",
             source="FT Origami o-colors _palette.scss", background="#FFF1E5", context="#D9CDC3"),
    "economist": _p(["#E3120B", "#1F2E7A", "#1DC9A4", "#F97A1F", "#475ED1", "#C91D42", "#F9C31F"],
                    family="editorial", mood=["editorial", "bold", "brand-red"],
                    best_for="red accent + navy; extra series as shades not new hues",
                    source="@economist/design-system color.css", background="#F5F4EF",
                    context="#CFD1C3"),
    "economist.chart": _p(["#0E6BA0", "#30C0D2", "#ED1319", "#973D4C", "#005778", "#EF4E33", "#01A9BF"],
                          family="editorial", mood=["editorial", "restrained"],
                          best_for="3-hue brand system (blue/turquoise/red)",
                          source="Datawrapper blog, observed Economist charts", context="#878771"),
    "owid.a": _p(["#4C6A9C", "#883039", "#578145", "#B13507", "#B16214", "#970046", "#D73C50",
                  "#00295B", "#00847E", "#BC8E5A", "#A2559C", "#18470F"], family="editorial",
                 mood=["scholarly", "earthy", "muted"], best_for="many conditions (≤12), atlas feel",
                 source="owid-grapher CustomSchemes.ts (OwidCategoricalA)"),
    "owid.b": _p(["#00847E", "#00295B", "#C15065", "#38AABA", "#8C4569", "#18470F", "#B13507",
                  "#BC8E5A", "#286BBB", "#970046", "#58AC8C", "#9A5129", "#E56E5A"], family="editorial",
                 mood=["scholarly", "cool", "earthy"], source="owid-grapher CustomSchemes.ts (B)"),
    "owid.c": _p(["#6D3E91", "#C05917", "#58AC8C", "#286BBB", "#883039", "#BC8E5A", "#00295B",
                  "#C15065", "#18470F", "#9A5129", "#E56E5A", "#A2559C"], family="editorial",
                 mood=["scholarly", "rich"], source="owid-grapher CustomSchemes.ts (C)"),
    "owid.d": _p(["#C15065", "#18470F", "#BC8E5A", "#8C4569", "#38AABA", "#00875E", "#E56E5A",
                  "#9A5129", "#CF0A66", "#00295B"], family="editorial", mood=["warm", "botanical"],
                 source="owid-grapher CustomSchemes.ts (D)"),
    "owid.lines": _p(["#4C6A9C", "#B13507", "#996D39", "#2C8465", "#6D3E91", "#883039", "#00295B",
                      "#A2559C", "#9A5129", "#008291"], family="editorial", mood=["scholarly", "deep"],
                     best_for="thin lines and text on white", source="owid-grapher (distinct lines)"),
    "reuters": _p(["#FA6400", "#005DA2", "#0099C4", "#621F95", "#A00000", "#387C2B", "#FFA100"],
                  family="editorial", mood=["newswire", "utilitarian", "orange"],
                  source="reuters-graphics graphics-components _tr.scss"),
    "newamerica": _p(["#FF2D44", "#22C8A3", "#4C81DB", "#70689F", "#AC5E05"], family="editorial",
                     mood=["crisp", "cool"], source="Datawrapper blog (New America style guide)"),
    "pew": _p(["#3171A2", "#70773F", "#EA9E2C", "#81AFD3", "#979E56", "#C7DBED", "#D9DEB8"],
              family="editorial", mood=["academic", "olive", "slate"], source="Datawrapper blog (Pew)"),
    "yougov.likert": _p(["#897CD3", "#B8B0E5", "#DDDDDD", "#D59AB2", "#DB4C81"], "div", "editorial",
                        mood=["soft", "modern", "lavender"], best_for="ordinal agree/disagree, ±5 levels",
                        source="Datawrapper blog (YouGov)"),
    "observable10": _p(["#4269D0", "#EFB118", "#FF725C", "#6CC5B0", "#3CA951", "#FF8AB7", "#A463F2",
                        "#97BBF5", "#9C6B4E", "#9498A0"], family="editorial", bg="any",
                       mood=["friendly", "contemporary", "bright"], source="d3-scale-chromatic observable10"),
    "tableau10": _p(["#4E79A7", "#F28E2C", "#E15759", "#76B7B2", "#59A14F", "#EDC949", "#AF7AA1",
                     "#FF9DA7", "#9C755F", "#BAB0AB"], family="editorial",
                    mood=["balanced", "business", "muted"], source="d3-scale-chromatic Tableau10"),
})

# =============================================================================
# 4. DESIGN SYSTEMS (2024–2026)
# =============================================================================
BANK.update({
    "carbon.light": _p(["#6929C4", "#1192E8", "#005D5D", "#9F1853", "#FA4D56", "#520408", "#198038",
                        "#002D9C", "#EE5396", "#B28600", "#009D9A", "#012749", "#8A3800", "#A56EFF"],
                       family="design-system", mood=["corporate", "sophisticated", "high-contrast"],
                       best_for="strict order; neighbor contrast maximised",
                       source="IBM Carbon @carbon/charts styles.css"),
    "carbon.dark": _p(["#8A3FFC", "#33B1FF", "#007D79", "#FF7EB6", "#FA4D56", "#FFF1F1", "#6FDC8C",
                       "#4589FF", "#D02670", "#D2A106", "#08BDBA", "#BAE6FF", "#BA4E00", "#D4BBFF"],
                      family="design-system", bg="dark", mood=["luminous", "dashboard"],
                      source="IBM Carbon (gray-100 theme)", background="#161616"),
    "carbon.blue": _p(["#EDF5FF", "#D0E2FF", "#A6C8FF", "#78A9FF", "#4589FF", "#0F62FE", "#0043CE",
                       "#002D9C", "#001D6C", "#001141"], "seq", "design-system", bg="any",
                      mood=["cool", "clean"], source="IBM Carbon sequential"),
    "carbon.purple": _p(["#F6F2FF", "#E8DAFF", "#D4BBFF", "#BE95FF", "#A56EFF", "#8A3FFC", "#6929C4",
                         "#491D8B", "#31135E", "#1C0F30"], "seq", "design-system", bg="any",
                        mood=["rich", "violet", "neuro"], source="IBM Carbon sequential"),
    "carbon.teal": _p(["#D9FBFB", "#9EF0F0", "#3DDBD9", "#08BDBA", "#009D9A", "#007D79", "#005D5D",
                       "#004144", "#022B30", "#081A1C"], "seq", "design-system", bg="any",
                      mood=["calm", "biological"], source="IBM Carbon sequential"),
    "carbon.cyan": _p(["#E5F6FF", "#BAE6FF", "#82CFFF", "#33B1FF", "#1192E8", "#0072C3", "#00539A",
                       "#003A6D", "#012749", "#1C0F30"], "seq", "design-system", bg="any",
                      mood=["aquatic"], source="IBM Carbon sequential"),
    "carbon.red_cyan": _p(["#750E13", "#A2191F", "#DA1E28", "#FA4D56", "#FF8389", "#FFB3B8", "#FFD7D9",
                           "#FFF1F1", "#E5F6FF", "#BAE6FF", "#82CFFF", "#33B1FF", "#1192E8", "#0072C3",
                           "#00539A", "#003A6D"], "div", "design-system",
                          mood=["classic", "hot-cold"], source="IBM Carbon diverging"),
    "carbon.purple_teal": _p(["#491D8B", "#6929C4", "#8A3FFC", "#A56EFF", "#BE95FF", "#D4BBFF", "#E8DAFF",
                              "#F6F2FF", "#D9FBFB", "#9EF0F0", "#3DDBD9", "#08BDBA", "#009D9A", "#007D79",
                              "#005D5D", "#004144"], "div", "design-system",
                             mood=["modern", "neuro", "non-political"], source="IBM Carbon diverging"),
    "atlassian": _p(["#357DE8", "#82B536", "#BF63F3", "#F68909", "#1558BC", "#964AC0", "#42B2D7",
                     "#BD5B00"], family="design-system", mood=["upbeat", "product"],
                    source="@atlaskit/tokens chart categorical"),
    "primer": _p(["#006EDB", "#EB670F", "#30A147", "#894CEB", "#DF0C24", "#179B9B", "#CE2C85",
                  "#B88700", "#9D615C", "#808FA3"], family="design-system",
                 mood=["developer", "crisp"], source="@primer/primitives data emphasis (light)"),
    "primer.muted": _p(["#D1F0FF", "#FFE7D1", "#CAF7CA", "#F1E5FF", "#FFE2E0", "#BFF8DB", "#FFE5F1",
                        "#F7EEA1", "#F2E9E9", "#E8ECF2"], family="design-system",
                       mood=["pastel", "soft"], best_for="area fills, shaded epochs, table bands",
                       source="@primer/primitives data muted"),
    "spectrum": _p(["#3B63FB", "#C24E00", "#07816D", "#D92361", "#7155FA", "#9E6600", "#0B78B3",
                    "#B539C8", "#408111", "#AA5E38"], family="design-system",
                   mood=["vivid", "creative"], source="@adobe/spectrum-tokens hue-900 (light)"),
    "spectrum.dark": _p(["#5681FF", "#E06400", "#0A9A80", "#FF3377", "#8077FE", "#BA7C00", "#188EDC",
                         "#D549EB", "#4E9A17", "#C07750"], family="design-system", bg="dark",
                        mood=["vivid", "creative"], source="@adobe/spectrum-tokens hue-900 (dark)"),
    "radix": _p(["#3E63DD", "#E54D2E", "#12A594", "#8E4EC6", "#FFC53D", "#D6409F", "#0090FF",
                 "#46A758", "#AD7F58", "#5B5BD6"], family="design-system", bg="any",
                mood=["polished", "ui"], source="radix-ui/colors step 9"),
    "tailwind.500": _p(["#2B7FFF", "#FF6900", "#00BC7D", "#FB2C36", "#8E51FF", "#FE9A00", "#00B8DB",
                        "#F6339A", "#7CCF00", "#615FFF"], family="design-system", bg="any",
                       mood=["saturated", "digital", "saas"],
                       source="Tailwind v4 theme.css (OKLCH→sRGB, approx)"),
    "tailwind.400": _p(["#51A2FF", "#FF8904", "#00D492", "#FF6467", "#A684FF", "#FFB900", "#00D3F2",
                        "#FB64B6", "#9AE600", "#7C86FF"], family="design-system", bg="dark",
                       mood=["neon", "glow"], best_for="lines on dark slides",
                       source="Tailwind v4 theme.css (approx)", background="#09090B"),
    "tailwind.700": _p(["#1447E6", "#CA3500", "#008236", "#C10007", "#7008E7", "#BB4D00", "#00786F",
                        "#C6005C", "#497D00", "#432DD7"], family="design-system",
                       mood=["deep", "inky", "print"], source="Tailwind v4 theme.css (approx)"),
})

# =============================================================================
# 5. TREND & HERITAGE
# =============================================================================
BANK.update({
    "pantone.coty": _p(["#A47864", "#FFBE98", "#F0EEE9"], family="trend",
                       mood=["warm", "soft", "tactile", "calm"],
                       best_for="Cloud Dancer canvas + Mocha context + Peach highlight",
                       source="Pantone COTY 2024 Peach Fuzz / 2025 Mocha Mousse / 2026 Cloud Dancer"),
    "pantone.deliciousness": _p(["#C44766", "#7E212A", "#EC6936", "#FFB080"], family="trend",
                                mood=["warm", "indulgent", "berry"], source="Pantone Mocha Mousse palettes (via Envato)"),
    "pantone.relaxed_elegance": _p(["#E4C7B8", "#BBAA92", "#8B645A", "#56453F"], "seq", "trend",
                                   mood=["quiet-luxury", "earthy"], source="Pantone Mocha Mousse palettes (via Envato)"),
    "pantone.uniquely_balanced": _p(["#9D4B8D", "#CA80B2", "#33BECD", "#D8AE48"], family="trend",
                                    mood=["playful", "retro"], source="Pantone Mocha Mousse palettes (via Envato)"),
    "nippon.ai": _p(["#0F2540", "#0D5661", "#006284", "#005CAF", "#33A6B8", "#66BAB7", "#7DB9DE",
                     "#A5DEE4"], "seq", "heritage", mood=["calm", "indigo", "crafted", "japanese"],
                    source="nipponcolors.com (KON→KAMENOZOKI)"),
    "nippon.warm": _p(["#9F353A", "#D0104C", "#F75C2F", "#E2943B", "#FFB11B", "#F6C555", "#563F2E"],
                      family="heritage", mood=["lacquer", "autumn", "japanese"], source="nipponcolors.com"),
    "nippon.green": _p(["#0F4C3A", "#1B813E", "#24936E", "#268785", "#5DAC81", "#7BA23F"], family="heritage",
                       mood=["moss", "bamboo", "japanese"], source="nipponcolors.com"),
    "nippon.mix": _p(["#0F2540", "#9F353A", "#FFB11B", "#24936E", "#8B81C3", "#33A6B8", "#E2943B",
                      "#66327C"], family="heritage", mood=["refined", "heritage", "editorial", "japanese"],
                     source="nipponcolors.com (selection)", background="#FFFFFB"),
    "nippon.wabi": _p(["#1C1C1C", "#535953", "#787878", "#BC9F77", "#D7B98E", "#DC9FB4", "#FEDFE1"],
                      family="heritage", kind="neutral", mood=["ink", "paper", "quiet"],
                      source="nipponcolors.com"),
    "dracula": _p(["#BD93F9", "#FF79C6", "#8BE9FD", "#50FA7B", "#FFB86C", "#FF5555", "#F1FA8C"],
                  family="theme", bg="dark", mood=["neon", "dark", "playful"],
                  source="dracula-theme spec", background="#282A36", text="#F8F8F2"),
    "solarized": _p(["#268BD2", "#DC322F", "#859900", "#D33682", "#B58900", "#2AA198", "#6C71C4",
                     "#CB4B16"], family="theme", bg="any", mood=["retro", "balanced"],
                    source="Solarized (Ethan Schoonover)", background="#FDF6E3", background_dark="#002B36"),
})

# =============================================================================
# 6. ORIGINALS — designed for figures (OKLCH-balanced, staggered lightness,
#    verified with check.palette_report; see data/cvd.json for measured ΔE)
# =============================================================================
BANK.update({
    "sp.nature": _p(["#2270CA", "#DB7F3F", "#319C7C", "#C8475B", "#7B578E", "#E1B50B", "#57B5D9"],
                    mood=["clean", "journal", "balanced"],
                    best_for="Nature-style default: calm blue lead, warm orange contrast"),
    "sp.neuro": _p(["#2B4C9B", "#E58447", "#4AAC9B", "#B0396A", "#9F59C4", "#E8C64A", "#6E8FA6"],
                   mood=["modern", "neuro", "confident"],
                   best_for="NeuroAI papers: indigo, tangerine, teal, raspberry, lavender"),
    "sp.lab": _p(["#1F2328", "#D1495B", "#125F9B", "#E9A23B", "#2A9D8F", "#936DC3"],
                 mood=["ink", "crisp", "editorial"], best_for="black for data/main, accents for conditions"),
    "sp.aurora": _p(["#3D5A98", "#E26D5A", "#359FA4", "#F2B134", "#A06CE1", "#76C893"], bg="any",
                    mood=["fresh", "modern", "vivid"], best_for="talks and graphical abstracts"),
    "sp.lavender": _p(["#6C5CE7", "#AE9DFA", "#2D3047", "#F49D6E", "#5EACBC", "#E8DFFC"],
                      mood=["digital-lavender", "soft", "trend"], best_for="modern soft look, one warm accent"),
    "sp.mocha": _p(["#5B3A29", "#A47259", "#D99F64", "#819482", "#3E5C76", "#F1DAC2"],
                   mood=["mocha", "earthy", "warm", "trend"], best_for="warm editorial on Cloud Dancer #F0EEE9",
                   background="#F0EEE9"),
    "sp.terracotta": _p(["#CC5A30", "#2F4858", "#E6A157", "#6A8D73", "#9B4454", "#86A8C4"],
                        mood=["earthy", "mediterranean", "warm"], best_for="ecological/behavioral data"),
    "sp.nordic": _p(["#2E4057", "#418CB1", "#A3C4BC", "#E4B363", "#B5525C", "#8D888E"],
                    mood=["scandinavian", "calm", "muted"], best_for="quiet multi-condition plots"),
    "sp.botanical": _p(["#1F3A2F", "#5D7A59", "#9BBE99", "#D98F4E", "#853850", "#FBE1AF"],
                       mood=["solarpunk", "organic", "green"], background="#FAF3E0"),
    "sp.bauhaus": _p(["#1F3A93", "#D7263D", "#F4B400", "#1B1B1B", "#5F8FB4"],
                     mood=["bauhaus", "primary", "graphic"], best_for="bold schematics, posters"),
    "sp.riso": _p(["#0173D4", "#FE62B2", "#0AA767", "#FFB511", "#775891", "#F04241"],
                  mood=["risograph", "playful", "print"], best_for="graphical abstracts, posters",
                  source="official Riso ink hexes (mattdesl/riso-colors)"),
    "sp.riso_duo": _p(["#3255A4", "#FF665E"], mood=["risograph", "duotone"],
                      best_for="two-condition contrast", source="Riso Medium Blue + Red inks"),
    "sp.synthwave": _p(["#FF48B5", "#AC7EF9", "#97CEFA", "#78FFCD", "#FFD36E", "#FC8E8E"], bg="dark",
                       mood=["neon", "retro-futurism", "dark"], best_for="dark talk slides",
                       background="#14111F"),
    "sp.neon": _p(["#0EE4FE", "#FF75C7", "#AEFF7E", "#FBAE02", "#8B79FF", "#FF5A57"], bg="dark",
                  mood=["neon", "glow", "dark"], best_for="dark slides, glow lines", background="#0B0F17"),
    "sp.midnight": _p(["#488EFF", "#F1738D", "#A2D085", "#ECA937", "#AF9DD2", "#9CDCFF"], bg="dark",
                      mood=["dark", "calm", "editor"], best_for="dark-mode figures (Tokyo-Night-like)",
                      background="#16161E"),
    "sp.pastel": _p(["#72A2FE", "#F39E9A", "#94DFC4", "#F7D08A", "#C5B4E0", "#CFE5F0"],
                    mood=["pastel", "soft", "light"], best_for="fills/areas behind dark lines (not thin lines)"),
    "sp.mono_blue": _p(["#0B2545", "#13315C", "#3E5C8A", "#7C9CC6", "#B9CDE8", "#E6EEF8"], "seq",
                       mood=["monochrome", "calm"], best_for="ordered levels of one variable"),
    "sp.mono_warm": _p(["#4A1C1C", "#8C2F39", "#C8553D", "#E9A066", "#F6CFA6", "#FDF0E1"], "seq",
                       mood=["monochrome", "warm"], best_for="ordered levels, warm"),
    "sp.depth": _p(["#F2E5D7", "#E7B98A", "#D98552", "#B9533E", "#86364A", "#4E2A4F", "#24203F"], "seq",
                   mood=["depth", "layers"], best_for="network layer index / cortical depth / time"),
    "sp.icefire": _p(["#2B4C9B", "#4F86C6", "#9CC3E4", "#F2F2F2", "#F2B38B", "#D9654B", "#9E2A2B"], "div",
                     mood=["classic", "balanced"], best_for="signed effects (Δ, z, weights)"),
    "sp.teal_plum": _p(["#0C5C5A", "#2FA59A", "#9ED9CC", "#F4F1EE", "#D8A7C8", "#A6488A", "#5E1F55"], "div",
                       mood=["modern", "neuro"], best_for="signed effects, non-red/blue alternative"),
})

# context neutrals and backgrounds
NEUTRALS = {
    "ink": "#1F2328", "ink_soft": "#3D434B", "muted": "#6B7280", "context": "#B8BCC2",
    "context_light": "#D9DCE1", "grid": "#E6E8EB", "rule": "#C9CDD2",
    "context_warm": "#CFC8BE", "context_ft": "#D9CDC3", "context_economist": "#CFD1C3",
}
BACKGROUNDS = {
    "white": "#FFFFFF", "paper": "#FAFAF7", "cloud_dancer": "#F0EEE9", "ft_paper": "#FFF1E5",
    "economist": "#F5F4EF", "sand": "#F9F9F8", "mist": "#F9FBFB", "gofun": "#FFFFFB",
    "dark": "#0E1117", "dark_slate": "#111113", "nord": "#2E3440", "catppuccin_mocha": "#1E1E2E",
    "rosepine": "#191724", "dracula": "#282A36", "zinc950": "#09090B", "midnight": "#16161E",
}

# =============================================================================
# 7. EXTERNAL COLORMAP CATALOG (names resolvable by cmap())
# =============================================================================
CMAPS = {
    # perceptually uniform sequential
    "viridis": ("seq", ["classic", "safe"]), "cividis": ("seq", ["cvd-optimal"]),
    "magma": ("seq", ["dark-to-light", "fire"]), "inferno": ("seq", ["fire"]),
    "mako": ("seq", ["ocean"]), "rocket": ("seq", ["warm"]),
    "cmc.batlow": ("seq", ["scientific", "safe", "rainbow-alternative"]),
    "cmc.batlowK": ("seq", ["dark-start"]), "cmc.batlowW": ("seq", ["light-end"]),
    "cmc.lajolla": ("seq", ["warm", "fire"]), "cmc.bilbao": ("seq", ["earth", "red"]),
    "cmc.davos": ("seq", ["cool", "blue"]), "cmc.devon": ("seq", ["cool", "lavender"]),
    "cmc.oslo": ("seq", ["cool", "dark"]), "cmc.lapaz": ("seq", ["blue", "cool"]),
    "cmc.acton": ("seq", ["violet", "soft"]), "cmc.tokyo": ("seq", ["mauve", "soft"]),
    "cmc.imola": ("seq", ["blue-green"]), "cmc.hawaii": ("seq", ["vivid"]),
    "cmc.buda": ("seq", ["magenta-yellow"]), "cmc.nuuk": ("seq", ["steel"]),
    "cmc.turku": ("seq", ["earth", "grey"]), "cmc.glasgow": ("seq", ["earthy"]),
    "cmc.lipari": ("seq", ["dark", "sunset"]), "cmc.navia": ("seq", ["ocean"]),
    "cmc.grayC": ("seq", ["grey"]),
    "cmr.ember": ("seq", ["fire", "dark"]), "cmr.amethyst": ("seq", ["violet", "dark"]),
    "cmr.cosmic": ("seq", ["space", "dark"]), "cmr.rainforest": ("seq", ["green"]),
    "cmr.ocean": ("seq", ["blue"]), "cmr.sunburst": ("seq", ["sunset", "dark"]),
    "cmr.torch": ("seq", ["fire"]), "cmr.lavender": ("seq", ["lavender", "dark"]),
    "cmr.sapphire": ("seq", ["blue", "dark"]), "cmr.jungle": ("seq", ["green", "dark"]),
    "cmr.voltage": ("seq", ["electric", "dark"]), "cmr.arctic": ("seq", ["ice"]),
    "cmr.freeze": ("seq", ["ice", "dark"]), "cmr.flamingo": ("seq", ["pink"]),
    "gray_r": ("seq", ["grey", "raster"]), "Greys": ("seq", ["grey"]),
    # diverging (centered)
    "RdBu_r": ("div", ["classic"]), "cmc.vik": ("div", ["scientific", "blue-red"]),
    "cmc.roma": ("div", ["scientific", "rainbow-alternative"]), "cmc.broc": ("div", ["blue-olive"]),
    "cmc.cork": ("div", ["blue-green"]), "cmc.bam": ("div", ["pink-green"]),
    "cmc.berlin": ("div", ["dark-center", "dark"]), "cmc.managua": ("div", ["dark-center"]),
    "cmc.vanimo": ("div", ["dark-center", "pink-green"]), "cmc.tofino": ("div", ["dark-center"]),
    "cmc.lisbon": ("div", ["dark-center"]),
    "cmr.iceburn": ("div", ["dark-center", "neon"]), "cmr.redshift": ("div", ["dark-center"]),
    "cmr.fusion": ("div", ["light-center"]), "cmr.wildfire": ("div", ["dark-center"]),
    "cmr.waterlily": ("div", ["light-center"]), "cmr.holly": ("div", ["dark-center"]),
    "coolwarm": ("div", ["soft"]), "PuOr_r": ("div", ["cvd-safe"]),
    "icefire": ("div", ["dark-center"]), "vlag": ("div", ["soft"]),
    # cyclic (phase, orientation, direction, time-of-day)
    "twilight": ("cyc", ["phase"]), "twilight_shifted": ("cyc", ["phase"]),
    "cmc.romaO": ("cyc", ["phase", "scientific"]), "cmc.vikO": ("cyc", ["phase"]),
    "cmc.brocO": ("cyc", ["phase"]), "cmc.corkO": ("cyc", ["phase"]), "cmc.bamO": ("cyc", ["phase"]),
    "cmr.infinity": ("cyc", ["phase", "vivid"]), "cmr.seasons": ("cyc", ["phase"]),
    "hsv": ("cyc", ["legacy-avoid"]),
    # multi-sequential / categorical-from-cmap
    "cmc.batlowS": ("cat", ["scientific", "many-categories"]),
    "cmc.hawaiiS": ("cat", ["many-categories"]), "cmc.lipariS": ("cat", ["many-categories"]),
}


# =============================================================================
# loading / API
# =============================================================================

@lru_cache(None)
def _imported() -> dict:
    p = _DATA / "imported.json"
    if not p.exists():
        return {}
    d = json.loads(p.read_text())
    d.pop("_riso_inks", None)
    for v in d.values():
        v.setdefault("bg", "light")
        v.setdefault("mood", [])
        v.setdefault("best_for", "")
    return d


@lru_cache(None)
def riso_inks() -> dict:
    p = _DATA / "imported.json"
    return json.loads(p.read_text()).get("_riso_inks", {}) if p.exists() else {}


@lru_cache(None)
def _cvd() -> dict:
    p = _DATA / "cvd.json"
    return json.loads(p.read_text()) if p.exists() else {}


def all_palettes() -> dict:
    out = dict(_imported())
    out.update(BANK)
    return out


def names(kind=None, family=None) -> list[str]:
    return sorted(k for k, v in all_palettes().items()
                  if (kind is None or v["kind"] == kind) and (family is None or v["family"] == family))


def info(name) -> dict:
    d = dict(all_palettes()[name])
    if name in _cvd():
        d["measured"] = _cvd()[name]
    return d


def get(name, n=None, ordered=True) -> list[str]:
    """Colors of a palette. For 'seq'/'div' with n -> resampled along the ramp.
    For categorical palettes with a curated order (MetBrewer), that order is used."""
    if name in SEMANTIC:
        return list(SEMANTIC[name].values())[:n]
    if name in all_palettes():
        p = all_palettes()[name]
        cols = p["colors"]
        if p["kind"] in ("seq", "div", "cyc") and n is not None and n != len(cols):
            cm = cmap(name)
            return [C.to_hex(cm(x)[:3]) for x in np.linspace(0, 1, n)]
        if ordered and "cat_order" in p and p["kind"] == "cat":
            cols = [cols[i] for i in p["cat_order"]]
        if n is not None and n > len(cols):
            raise ValueError(f"{name} has only {len(cols)} colors; use a larger palette, "
                             "highlight(), or tints()")
        return cols[:n]
    # fall back to a colormap sampled
    cm = cmap(name)
    n = n or 7
    return [C.to_hex(cm(x)[:3]) for x in np.linspace(0.08, 0.92, n)]


def semantic(name) -> dict[str, str]:
    return dict(SEMANTIC[name])


def cmap(name, n=None, reverse=False):
    """Colormap from: bank palettes (smooth OKLab interpolation), 'cmc.*' (cmcrameri),
    'cmr.*' (cmasher), seaborn names, or matplotlib names. `_r` suffix reverses."""
    import matplotlib as mpl
    from matplotlib.colors import LinearSegmentedColormap, ListedColormap
    if name.endswith("_r") and name[:-2] in all_palettes():
        name, reverse = name[:-2], not reverse
    if name in all_palettes():
        p = all_palettes()[name]
        cols = p["colors"]
        if p["kind"] == "cat" and n is None:
            cm = ListedColormap(cols, name=name)
        else:
            # smooth: interpolate in OKLab between anchors
            fine = []
            for a, b in zip(cols[:-1], cols[1:]):
                fine += [C.mix(a, b, t) for t in np.linspace(0, 1, 16, endpoint=False)]
            fine.append(cols[-1])
            cm = LinearSegmentedColormap.from_list(name, fine, N=256)
            if "bad" in p:
                cm.set_bad(p["bad"])
    else:
        if name.startswith("cmc."):
            import cmcrameri.cm  # noqa: F401  registers 'cmc.*'
        elif name.startswith("cmr."):
            import cmasher  # noqa: F401  registers 'cmr.*'
        elif name in ("mako", "rocket", "icefire", "vlag", "crest", "flare"):
            import seaborn  # noqa: F401
        cm = mpl.colormaps[name]
    if reverse:
        cm = cm.reversed()
    if n is not None:
        cm = cm.resampled(n)
    return cm


def register_all(prefix="sp."):
    """Register every bank palette as a matplotlib colormap '<prefix><name>' (idempotent)."""
    import matplotlib as mpl
    for k in all_palettes():
        nm = k if k.startswith(prefix) else prefix + k
        if nm not in mpl.colormaps:
            try:
                mpl.colormaps.register(cmap(k), name=nm)
                mpl.colormaps.register(cmap(k).reversed(), name=nm + "_r")
            except Exception:
                pass


def search(kind=None, mood=None, bg=None, family=None, cvd_safe=None, min_n=None, text=None):
    """Find palettes. mood/text match substrings in mood tags, best_for, name.
    cvd_safe=True uses *measured* data (min ΔE2000 under CVD ≥ 10)."""
    res = []
    moods = [mood] if isinstance(mood, str) else (mood or [])
    for k, v in all_palettes().items():
        if kind and v["kind"] != kind:
            continue
        if family and v["family"] != family:
            continue
        if bg and v.get("bg", "light") not in (bg, "any"):
            continue
        if min_n and len(v["colors"]) < min_n:
            continue
        hay = " ".join([k, " ".join(v.get("mood", [])), v.get("best_for", ""), v["family"]]).lower()
        if moods and not all(m.lower() in hay for m in moods):
            continue
        if text and text.lower() not in hay:
            continue
        if cvd_safe is not None:
            meas = _cvd().get(k)
            if meas is None or meas.get("cvd_safe") != cvd_safe:
                continue
        res.append(k)
    if kind in (None, "seq", "div", "cyc", "cat"):
        for k, (kd, tags) in CMAPS.items():
            if (kind is None or kd == kind) and (not moods or all(
                    any(m.lower() in t for t in tags + [k.lower()]) for m in moods)) and family in (None, "cmap") \
                    and cvd_safe is None and bg is None and not text:
                res.append(k)
    return res


def highlight(n, idx, accent="#D1495B", grey=None, bg="#FFFFFF"):
    """n colors: grey for all, accent for idx (int or list). 'Grey for context, color for signal'."""
    grey = grey or NEUTRALS["context"]
    idx = [idx] if isinstance(idx, int) else list(idx)
    accents = [accent] if isinstance(accent, str) else list(accent)
    out = [grey] * n
    for j, i in enumerate(idx):
        out[i] = accents[j % len(accents)]
    return out


def paired(name, n=None, amount=0.55, bg="#FFFFFF"):
    """[(strong, light), ...] pairs: line + CI band / fill per category."""
    return [(c, C.lighten(c, amount, bg)) for c in get(name, n)]


def shades(color, n=4, spread=0.35):
    """n shades of one hue (Economist rule: more series -> shades, not new hues)."""
    L, Ch, h = C.rgb_to_oklch(C.to_rgb(color))
    Ls = np.linspace(L - spread / 2, L + spread / 2, n)
    return [C.oklch(np.clip(l, 0.2, 0.92), Ch, h) for l in Ls]


def build_categorical(n=6, L=(0.52, 0.78), C_=0.13, h0=255, bg="#FFFFFF", cvd_min=12, seed=0,
                      tries=4000):
    """Generate an n-color categorical palette in OKLCH: hues spread around the wheel,
    lightness staggered (grayscale-separable), maximising min ΔE under CVD."""
    rng = np.random.default_rng(seed)
    best, best_score = None, -1
    from .check import palette_report
    for _ in range(tries):
        hs = (h0 + np.sort(rng.uniform(0, 360, n))) % 360
        Ls = rng.permutation(np.linspace(*L, n))
        cols = [C.oklch(l, C_, h) for l, h in zip(Ls, hs)]
        rep = palette_report(cols, bg=bg, verbose=False)
        score = min(rep["deutan"], rep["protan"], rep["tritan"]) + 0.3 * rep["normal"]
        if score > best_score:
            best, best_score = cols, score
    return best


def to_cycle(name, n=None):
    """Set matplotlib's default color cycle to a palette."""
    import matplotlib as mpl
    from cycler import cycler
    mpl.rcParams["axes.prop_cycle"] = cycler(color=get(name, n))


def swatch(names_=None, path=None, cvd=False):
    """Quick visual of palettes (for Claude to Read). Returns path to PNG."""
    import matplotlib.pyplot as plt
    names_ = names_ or ["okabe_ito", "sp.nature", "sp.neuro"]
    names_ = [names_] if isinstance(names_, str) else names_
    rows = []
    for nm in names_:
        cols = get(nm) if nm in all_palettes() or nm in SEMANTIC else get(nm, 9)
        rows.append((nm, cols))
        if cvd:
            for k in C.CVD_TYPES:
                rows.append((f"  {k}", [C.to_hex(x) for x in C.simulate_cvd(cols, k)]))
    fig, ax = plt.subplots(figsize=(6, 0.28 * len(rows) + 0.3))
    for i, (nm, cols) in enumerate(rows):
        for j, c in enumerate(cols):
            ax.add_patch(plt.Rectangle((j, -i), 0.94, 0.8, fc=c, lw=0))
        ax.text(-0.3, -i + 0.4, nm, ha="right", va="center", fontsize=8)
    ax.set_xlim(-6, max(len(c) for _, c in rows))
    ax.set_ylim(-len(rows) + 0.9, 0.9)
    ax.set_axis_off()
    import os
    import tempfile
    path = path or os.path.join(tempfile.gettempdir(), "sciplot_swatch.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path
