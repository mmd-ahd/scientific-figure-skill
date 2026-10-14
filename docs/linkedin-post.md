# LinkedIn announcement (draft)

**Suggested image:** `examples/recipe_gallery.png` (12 panel types in one figure). Alternatives:
`examples/demo_nature.png`, or a carousel of recipe_gallery → themes → demo_brainviz. LinkedIn crops wide images,
so check the preview before posting.

---

Making a figure that's accurate, journal-compliant and nice to look at still takes me longer than it should. Column
widths in mm, 5–7 pt text, minimum stroke weights, colour-blind-safe palettes, editable fonts: every journal has its
own rules, and matplotlib's defaults miss most of them.

So I built **scientific-figure**, an open-source Claude skill and Python library (`sciplot`) for computational
neuroscience and NeuroAI figures:

🧠 Ready-made panels: rasters, PSTHs, RDMs, latent trajectories, embeddings, rainclouds, model–brain layer profiles,
learning curves, connectivity, model schematics, plus presets for nilearn, MNE, pycortex and PyVista
📐 Exact layouts for Nature, Nature Neuroscience, Cell/Neuron, Science, eLife, PNAS, JNeurosci, PLOS, NeurIPS/ICLR,
ICML, slides and posters
🎨 197 palettes, each measured for colour-vision deficiency, and six themes
✅ A built-in linter that checks font sizes, line weights, widths, rainbow colormaps, colour-blind safety and the
font that actually got embedded

You can ask Claude: "Make a Nature Neuroscience figure from results.npz: schematic, PSTHs, trajectories,
decoding per mouse." It lays out the figure, lints it, looks at the rendered result and fixes what it finds.
Or skip Claude and just `pip install` it. It's pure matplotlib, and the output stays editable PDF/SVG.

The defaults draw on open plotting code and guidelines from the IBL Brain-Wide Map, Rastermap, CEBRA, publisher
author guides and the data-viz literature (Crameri, Wilke, Wong, Rougier).

MIT-licensed. Feedback, issues and new recipes are very welcome 👇
🔗 https://github.com/mmd-ahd/scientific-figure-skill

#ComputationalNeuroscience #NeuroAI #Neuroscience #DataVisualization #OpenScience #Python #Matplotlib #Claude #ScientificFigures
