# Panel recipes

![All recipes](../examples/recipe_gallery.png)

Every recipe draws into an `ax` you pass in, takes its colours from arguments or the active theme, and returns the
main artist. Set the style first with `sp.use(theme, target=...)`. The snippets below assume this setup:

```python
import numpy as np
import sciplot as sp
from sciplot import neuro, schematic as S

sp.use("clean", target="nature", palette="sp.neuro")
pal, tc = sp.colors("sp.neuro"), sp.theme_colors()   # tc["context"] is the theme's context grey
```

The conventions come from published exemplars (IBL Brain-Wide Map, Rastermap, CEBRA, MICrONS, rsatoolbox). See
[references/neuro-figure-patterns.md](../references/neuro-figure-patterns.md).

---

## Time series

### `mean_ci(ax, x, Y, color, label=None, ci="sem")`
Mean ± SEM / SD / bootstrap CI band for `Y` of shape `(n_trials, n_time)`.
```python
neuro.mean_ci(ax, t, Y_ctrl, tc["context"], label="Control")      # grey = context
neuro.mean_ci(ax, t, Y_opto, pal[0], label="Opto", ci=95)          # 95% bootstrap CI
sp.shade(ax, 0, 0.5, label="stim")
sp.label_lines(ax)                                                  # labels at line ends, no legend box
```
State in the legend what the band is ("mean ± s.e.m., n = 30 trials").

### `psth(spikes, edges, smooth_sd=None)` → rates
Trial-averaged firing rate in Hz from a list of spike-time arrays. Plot it with `ax.plot` or `mean_ci`.

### `gradient_line(ax, x, y, values=None, cmap="cmr.ember")`
A line coloured by a third variable, e.g. time or speed.

## Spikes and populations

### `raster(ax, spikes, color="0.1")`
One row per trial or neuron, rasterized so PDFs stay small. Add `sp.event_lines(ax, [0], labels=["go"])`.

### `activity_heatmap(ax, A, sort="peak", zscore=False, scalebar=None)`
Neurons × time in Rastermap style. Sorted by peak time, grey ramp by default (or diverging `RdBu_r` with symmetric
limits when `zscore=True`). Axes are replaced by an L-shaped scale bar:
```python
neuro.activity_heatmap(ax, A, t=t, scalebar=dict(dx=1, xlabel="1 s", dy=50, ylabel="50 cells"))
```

## Representations

### `rdm(ax, D, groups=None, group_colors=None, triangle=None, colorbar=False)`
Representational dissimilarity matrix with category blocks marked by coloured bars and labels:
```python
neuro.rdm(ax, D, groups=[(0, 8, "faces"), (8, 16, "bodies"), (16, 24, "objects")], group_colors=pal[:3])
```

### `connectivity(ax, W, ei_split=None)`
Weight matrix with symmetric diverging limits. `ei_split=k` draws a line between excitatory and inhibitory units.

## Latent dynamics

### `trajectories(ax, X, color=None, cmap=None, three_d=False, fade=False)`
Trajectories of shape `(n_time, 2|3)` with start/end markers. Pass `cmap` to colour by time. For 3-D, use
`fig.add_subplot(projection="3d")` and then `neuro.style_3d(ax)`.

### `embedding(ax, Z, c=None, cmap="cmc.batlow", s=1.5, alpha=0.5)`
UMAP / t-SNE / CEBRA scatter in the CEBRA style: tiny translucent points coloured by a behavioural variable. Pair it
with `neuro.axis_arrows(ax, "UMAP 1", "UMAP 2")` and `ax.set_axis_off()`.

## Statistics

### `dots_and_summary(ax, groups, colors, labels=None, summary="mean", err="sem", paired=False)`
Shows every observation as a dot plus a summary tick and error bar. Use it instead of bar ± SEM when n < 30
(`paired=True` connects matched observations).
```python
neuro.dots_and_summary(ax, [ctrl, opto], [tc["context"], pal[0]], labels=["Ctrl", "Opto"])
sp.sig_bracket(ax, 0, 1, y=0.9, text=p)           # number → stars; or text=sp.annotate.fmt_p(p)
```

### `raincloud(ax, groups, colors, labels=None, horizontal=False)` · `half_violin(...)`
Half-violin, thin box and jittered points (Allen et al. 2019). The KDE uses scipy if installed, otherwise numpy.

## NeuroAI

### `layer_profile(ax, layers, scores, color, err=None, ceiling=None)`
Model-to-brain alignment by layer (encoding R², RSA, Brain-Score), with an optional noise-ceiling band:
```python
neuro.layer_profile(ax, layers, r2_v1, pal[0], label="V1", err=sem_v1, ceiling=(0.52, 0.58))
neuro.layer_profile(ax, layers, r2_it, pal[1], label="IT", err=sem_it)
```

### `learning_curves(ax, steps, runs, color, smooth=None, show_runs=True, log_x=False)`
Individual seeds as thin faint lines, with the mean drawn bold on top.

### `tuning_curve(ax, theta, rates, color, err=None, polar=False)`
Orientation or direction tuning on Cartesian or polar axes.

## Brain maps (presets only; install the packages yourself)

| Function | Use with |
|---|---|
| `nilearn_kwargs(kind="stat" \| "glass" \| "surf" \| "connectome", dark=False)` | `nilearn.plotting.plot_stat_map(img, axes=ax, **neuro.nilearn_kwargs())` |
| `mne_topomap_kwargs()` | `mne.viz.plot_topomap(data, info, axes=ax, **neuro.mne_topomap_kwargs())` |
| `pycortex_quickflat_kwargs()` | `cortex.quickflat.make_figure(vol, **neuro.pycortex_quickflat_kwargs())` |
| `pyvista_theme(dark=False)` | sets a PyVista theme that matches the figure; screenshot into `image_panel(ax, img)` |
| `normalize_text(fig)` / `style_mne_figure(fig)` | bring external figures' text sizes back into the venue range |

See `figure_brain()` in [`scripts/demo_figures.py`](../scripts/demo_figures.py) for a complete nilearn + MNE panel.

## Schematics (`sciplot.schematic`)
`S.canvas(ax)` turns an axes into a blank canvas measured in **millimetres**, so boxes and text keep their print size.
```python
W, H = S.canvas(ax["a"])
a = S.box(ax["a"], (2, H/2), text="Stimulus", fc=sp.color.lighten(pal[0], 0.82), ec=pal[0])
b = S.box(ax["a"], (W - 20, H/2), text="Choice")
S.network(ax["a"], [3, 5, 5, 2], xy=(24, 4), width=W*0.4, height=H*0.6)
S.connect(ax["a"], a, b)
```
Other glyphs: `pill`, `circle`, `arrow(rad=0.3)`, `pipeline`, `recurrent_unit`, `layer_stack` (CNN), `prism`
(transformer block), `mini_trace`, `mini_matrix`, `gradient_box`, `bracket`.

## Annotation helpers (`sp.*`)
`label_lines`, `label_point`, `sig_bracket`, `scale_bar`, `event_lines`, `shade`, `slim_colorbar`,
`annotate.halo` (outline for text on images), `annotate.value_labels`. Full signatures are in [api.md](api.md).
