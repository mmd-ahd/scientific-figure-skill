"""Reference figures exercising every part of sciplot (also the visual regression check).

    python demo_figures.py [outdir]        # writes demo_*.pdf/png + lint output
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import sciplot as sp  # noqa: E402
from sciplot import neuro, schematic as S  # noqa: E402

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "examples")
rng = np.random.default_rng(7)


# ---------------------------------------------------------------- synthetic data
def make_data():
    t = np.linspace(-0.5, 1.5, 201)
    conds = 3
    # PSTH-like responses per condition
    resp = []
    for c in range(conds):
        base = 5 + 25 * (c + 1) / conds * np.exp(-((t - 0.25 - 0.1 * c) / 0.18) ** 2) * (t > 0)
        noise = [np.convolve(rng.normal(0, 6, len(t)), np.ones(9) / 9, "same") for _ in range(40)]
        trials = base[None] + np.array(noise)
        resp.append(trials)
    # spikes for raster
    spikes = []
    for c in range(conds):
        for k in range(12):
            rate = np.interp(np.linspace(-0.5, 1.5, 2000), t, resp[c].mean(0))
            s = np.linspace(-0.5, 1.5, 2000)[rng.random(2000) < rate * 0.001]
            spikes.append(s)
    # neural trajectories (rotational dynamics)
    tt = np.linspace(0, 1, 120)
    traj = []
    for c in range(5):
        ang = 2.2 * np.pi * tt * (0.8 + 0.1 * c)
        r = (1 - np.exp(-6 * tt)) * (0.6 + 0.12 * c)
        traj.append(np.c_[r * np.cos(ang + 0.3 * c), r * np.sin(ang + 0.3 * c)] +
                    rng.normal(0, 0.006, (120, 2)))
    # population heatmap (sequence)
    nN, nT = 180, 160
    peaks = rng.uniform(0, nT, nN)
    widths = rng.uniform(6, 16, nN)
    A = np.exp(-((np.arange(nT)[None] - peaks[:, None]) / widths[:, None]) ** 2)
    A += rng.normal(0, 0.03, A.shape)
    # RDM with 3 category blocks
    n = 24
    lab = np.repeat([0, 1, 2], 8)
    X = rng.normal(0, 1, (n, 30)) + np.eye(3)[lab] @ rng.normal(0, 2.2, (3, 30))
    D = 1 - np.corrcoef(X)          # correlation distance
    # layer profile
    layers = ["conv1", "conv2", "conv3", "conv4", "conv5", "fc6", "fc7"]
    v1 = np.array([0.28, 0.41, 0.36, 0.30, 0.24, 0.18, 0.15])
    it = np.array([0.08, 0.13, 0.22, 0.33, 0.44, 0.49, 0.46])
    # group stats
    groups = [rng.normal(0.52, 0.08, 14), rng.normal(0.61, 0.07, 14), rng.normal(0.74, 0.06, 14)]
    return dict(t=t, resp=resp, spikes=spikes, traj=traj, A=A, D=D, layers=layers, v1=v1,
                it=it, groups=groups)


# ---------------------------------------------------------------- figure 1
def figure_main(theme="clean", target="nature", palette="sp.neuro", name="demo_nature",
                width="double", height_mm=118):
    sp.use(theme, target=target, palette=palette)
    d = make_data()
    pal = sp.colors(palette)
    tc = sp.theme_colors()
    fig, ax = sp.figure(target, width, height_mm=height_mm,
                        mosaic=[["a", "a", "b", "c"], ["d", "e", "f", "g"]],
                        width_ratios=[1, 1, 1.05, 1.05], height_ratios=[1, 1.05])

    # a — schematic: task -> model -> readout
    A = ax["a"]
    W, H = S.canvas(A)
    y0 = H * 0.42
    S.box(A, (1, y0), 15, 11, "Stimulus", fc=sp.color.lighten(pal[0], 0.82, tc["bg"]),
          ec=pal[0], text_color=pal[0])
    S.mini_trace(A, (3, y0 - 9), 11, 6, kind="wave", color=pal[0])
    net_x = 24
    S.network(A, [3, 5, 5, 2], xy=(net_x, H * 0.2), width=W * 0.38, height=H * 0.62,
              r=1.25, colors=["#FFFFFF", sp.color.lighten(pal[2], 0.6), sp.color.lighten(pal[2], 0.6), "#FFFFFF"],
              edge_color=sp.color.mix(tc["bg"], tc["muted"], 0.45), node_ec=tc["fg"])
    A.text(net_x + W * 0.19, H * 0.9, "Recurrent network", ha="center", va="center",
           fontsize=plt.rcParams["font.size"], color=tc["fg"], weight="medium")
    S.box(A, (W - 17, y0), 16, 11, "Choice", fc=sp.color.lighten(pal[1], 0.82, tc["bg"]),
          ec=pal[1], text_color=sp.color.darken(pal[1], 0.15))
    S.arrow(A, (16.8, y0 + 5.5), (net_x - 2, y0 + 5.5), color=tc["muted"], lw=0.7)
    S.arrow(A, (net_x + W * 0.38 + 2, y0 + 5.5), (W - 17.8, y0 + 5.5), color=tc["muted"], lw=0.7)
    S.mini_matrix(A, (W - 14, y0 - 10), 7, cmap="cmc.batlow", n=5)
    A.text(W - 5.5, y0 - 6.5, "readout", ha="left", va="center", fontsize=plt.rcParams["xtick.labelsize"],
           color=tc["muted"])

    # b — PSTH with CI + raster inset above
    B = ax["b"]
    cond_cols = pal[:3]
    for c in range(3):
        neuro.mean_ci(B, d["t"], d["resp"][c], cond_cols[c], label=f"{[25, 50, 100][c]}%")
    sp.annotate.shade(B, 0, 0.5, color=sp.color.mix(tc["bg"], tc["muted"], 0.1), label="stim")
    B.set_xlabel("Time from onset (s)")
    B.set_ylabel("Firing rate (Hz)")
    B.set_xlim(-0.5, 1.5)
    sp.max_ticks(B, 4)
    sp.label_lines(B, x=None)

    # c — latent trajectories, colored by condition, start/end markers
    Cx = ax["c"]
    tcols = sp.colors("sp.depth", 5) if theme != "dark" else sp.colors("cmr.ember", 5)
    for i, X in enumerate(d["traj"]):
        neuro.trajectories(Cx, X, color=tcols[i], lw=1.0, fade=True, ms=2.5)
    Cx.set_aspect("equal")
    Cx.set_xticks([]), Cx.set_yticks([])
    for s in Cx.spines.values():
        s.set_visible(False)
    neuro.axis_arrows(Cx, "PC 1", "PC 2", color=tc["muted"])
    Cx.set_title("Population dynamics")

    # d — sequence heatmap, no axes, scale bar
    Dx = ax["d"]
    neuro.activity_heatmap(Dx, d["A"], cmap="gray_r" if theme != "dark" else "magma",
                           scalebar=dict(dx=40, xlabel="1 s", dy=50, ylabel="50 cells",
                                         color=tc["fg"]))
    Dx.set_title("Sequence (sorted by peak)")

    # e — RDM with group bars
    E = ax["e"]
    im = neuro.rdm(E, d["D"], cmap="cmc.lipari" if theme == "dark" else "cmc.batlow",
                   groups=[(0, 8, "faces"), (8, 16, "bodies"), (16, 24, "objects")],
                   group_colors=pal[3:6])
    sp.slim_colorbar(fig, im, E, label="1 − r", ticks=[0, 1, 2], length=0.7)
    E.set_title("Model RDM", pad=7)

    # f — layer-wise alignment (Brain-Score style)
    F = ax["f"]
    neuro.layer_profile(F, d["layers"], d["v1"], pal[0], label="V1", err=0.025)
    neuro.layer_profile(F, d["layers"], d["it"], pal[3], label="IT", err=0.025, ceiling=(0.55, 0.6))
    F.set_ylabel("Encoding $R^2$")
    F.set_xlabel("Model layer")
    F.tick_params(axis="x", rotation=45)
    for lab in F.get_xticklabels():
        lab.set_ha("right")
        lab.set_rotation_mode("anchor")
    F.set_ylim(0, 0.65)
    sp.label_lines(F)

    # g — show-the-data summary + bracket
    G = ax["g"]
    neuro.dots_and_summary(G, d["groups"], [tc["muted"], pal[0], pal[3]],
                           labels=["Ctrl", "Opto", "Model"])
    G.set_ylabel("Decoding accuracy")
    G.set_ylim(0.3, 1.0)
    G.axhline(0.5, color=tc["muted"], lw=0.6, ls=(0, (2, 2)), zorder=0)
    G.text(2.45, 0.5, "chance", ha="right", va="bottom", fontsize=plt.rcParams["xtick.labelsize"],
           color=tc["muted"])
    sp.sig_bracket(G, 0, 1, 0.82, 0.003)
    sp.sig_bracket(G, 0, 2, 0.91, 1e-5)
    sp.max_ticks(G, 4, "y")

    sp.align_labels(fig)
    sp.label_panels(fig, ax)
    return sp.save(fig, OUT / name, formats=("pdf", "png"), target=target)


# ---------------------------------------------------------------- figure 2: ML venue, editorial
def figure_ml(name="demo_neurips_editorial"):
    sp.use("editorial", target="neurips", palette="sp.lab")
    tc = sp.theme_colors()
    fig, ax = sp.figure("neurips", "single", height_mm=52, mosaic="ABC",
                        width_ratios=[1.25, 1, 1])
    # A — learning curves: grey baselines, one highlighted method (Datawrapper rule)
    A = ax["A"]
    steps = np.linspace(1e3, 1e6, 120)
    names_ = ["LSTM", "GRU", "Transformer", "S4", "Ours"]
    cols = sp.highlight(5, 4, accent="#D1495B", grey=tc["context"])
    for i, (nm, c) in enumerate(zip(names_, cols)):
        final = [0.62, 0.66, 0.71, 0.74, 0.83][i]
        runs = [final * (1 - np.exp(-steps / (1.5e5 + 3e4 * i))) + rng.normal(0, 0.008, len(steps))
                for _ in range(4)]
        neuro.learning_curves(A, steps, runs, c, label=nm, show_runs=(i == 4), smooth=5,
                              lw=None if i == 4 else 0.9)
    A.set_xscale("log")
    A.set_xlabel("Training steps")
    A.set_title("Neural predictivity (r)")
    A.set_ylim(0.3, 0.9)
    sp.label_lines(A)
    # B — embedding colored by a behavioral variable
    B = ax["B"]
    th = rng.uniform(0, 2 * np.pi, 4000)
    Z = np.c_[np.cos(th) * (1 + 0.25 * np.sin(3 * th)), np.sin(th)] + rng.normal(0, 0.06, (4000, 2))
    neuro.embedding(B, Z, c=th, cmap="cmc.romaO", s=1.2, alpha=0.6)
    B.set_title("Latent embedding")
    B.set_aspect("equal")
    neuro.axis_arrows(B, "UMAP 1", "UMAP 2", color=tc["muted"])
    # C — raincloud
    C_ = ax["C"]
    g = [rng.normal(0.55, 0.07, 40), rng.normal(0.63, 0.06, 40), rng.normal(0.78, 0.05, 40)]
    neuro.raincloud(C_, g, [tc["context"], "#6C8EA4", "#D1495B"], labels=["Linear", "MLP", "Ours"])
    C_.set_title("Held-out accuracy")
    sp.max_ticks(C_, 4, "y")
    sp.align_labels(fig)
    sp.label_panels(fig, ax)
    return sp.save(fig, OUT / name, formats=("pdf", "png"), target="neurips")


# ---------------------------------------------------------------- figure 3: graphical abstract
def block_rdm(n=9, k=3, noise=0.12, seed=0):
    r = np.random.default_rng(seed)
    lab = np.repeat(np.arange(k), n // k)
    D = 0.85 - 0.6 * (lab[:, None] == lab[None]) + r.normal(0, noise, (n, n))
    D = (D + D.T) / 2
    np.fill_diagonal(D, 0)
    return np.clip(D, 0, 1)


def figure_abstract(name="demo_graphical_abstract"):
    sp.use("clean", target="graphical-abstract", palette="sp.aurora")
    pal = sp.colors("sp.aurora")
    tc = sp.theme_colors()
    fig, ax = sp.figure("graphical-abstract", "single", height_mm=101.6, pad_mm=0)
    W, H = S.canvas(ax)
    fs = plt.rcParams["font.size"]
    ax.text(W / 2, H - 7, "Brain-aligned recurrent models", ha="center", va="center",
            fontsize=fs + 2, weight="bold")
    # row 1: recordings -> model
    y1 = H - 42
    S.gradient_box(ax, (7, y1), 32, 24, pal[0], pal[2])
    ax.text(23, y1 + 18.5, "Neural recordings", ha="center", va="center", color="white",
            fontsize=fs, weight="semibold")
    for k in range(5):                                   # mini raster
        S.mini_trace(ax, (11, y1 + 2.5 + k * 2.6), 24, 2.0, kind="spikes", color="white",
                     lw=0.8, seed=k)
    S.arrow(ax, (41.5, y1 + 12), (50, y1 + 12), color=tc["muted"], lw=1.1, head=3.5)
    for i, c in enumerate([pal[4], pal[1], pal[3]]):
        S.prism(ax, (53 + i * 4, y1 + 2 + i * 3), 26, 15, d=3.2, fc=sp.color.lighten(c, 0.1))
    ax.text(73, y1 - 3, "Recurrent model", ha="center", va="top", fontsize=fs, color=tc["fg"])
    # row 2: representational comparison
    y2 = 13
    sz = 26
    S.mini_matrix(ax, (9, y2), sz, data=block_rdm(seed=1), cmap="sp.mono_blue_r", n=9, lw=0.25)
    S.mini_matrix(ax, (W - 9 - sz, y2), sz, data=block_rdm(seed=2), cmap="sp.mono_blue_r",
                  n=9, lw=0.25)
    ax.text(9 + sz / 2, y2 - 2.5, "Brain RDM", ha="center", va="top", fontsize=fs)
    ax.text(W - 9 - sz / 2, y2 - 2.5, "Model RDM", ha="center", va="top", fontsize=fs)
    S.arrow(ax, (37, y2 + sz / 2), (W - 37, y2 + sz / 2), style="<|-|>", color=tc["muted"],
            lw=1.0, head=3)
    S.pill(ax, (W / 2, y2 + sz / 2), text="r = 0.82", fc=pal[1], weight="bold", anchor="c",
           text_color="white", zorder=4)
    S.arrow(ax, (W / 2, y1 - 3), (W / 2, y2 + sz / 2 + 6), color=tc["muted"], lw=1.1, head=3.5)
    return sp.save(fig, OUT / name, formats=("pdf", "png"), target="graphical-abstract")


# ---------------------------------------------------------------- figure 5: talk slide
def figure_slide(name="demo_slide_dark"):
    """Slides: 2-3 panels max, big text, one message, dark theme."""
    sp.use("dark", target="slide", palette="sp.midnight")
    d = make_data()
    pal = sp.colors("sp.midnight")
    tc = sp.theme_colors()
    fig, ax = sp.figure("slide", "full", height_mm=120, mosaic="ABC", width_ratios=[1.2, 1.1, 1])
    for c in range(3):
        neuro.mean_ci(ax["A"], d["t"], d["resp"][c], pal[c], label=f"{[25, 50, 100][c]}%")
    sp.annotate.shade(ax["A"], 0, 0.5, label="stimulus")
    ax["A"].set(xlabel="Time (s)", ylabel="Firing rate (Hz)", xlim=(-0.5, 1.5))
    sp.max_ticks(ax["A"], 4)
    sp.label_lines(ax["A"])
    neuro.layer_profile(ax["B"], d["layers"], d["v1"], pal[0], label="V1", err=0.025)
    neuro.layer_profile(ax["B"], d["layers"], d["it"], pal[1], label="IT", err=0.025)
    ax["B"].set(ylabel="Encoding $R^2$", ylim=(0, 0.6))
    ax["B"].set_xticks([0, 3, 6], ["early", "middle", "late"])
    ax["B"].set_xlabel("Model layer")
    sp.label_lines(ax["B"])
    neuro.dots_and_summary(ax["C"], d["groups"], [tc["context"], pal[0], pal[1]],
                           labels=["Ctrl", "Opto", "Model"])
    ax["C"].set(ylabel="Decoding accuracy", ylim=(0.3, 1.0))
    sp.sig_bracket(ax["C"], 0, 2, 0.9, 1e-5)
    sp.max_ticks(ax["C"], 4, "y")
    return sp.save(fig, OUT / name, formats=("pdf", "png"), target="slide")


# ---------------------------------------------------------------- figure 4: brain-viz presets
def figure_brain(name="demo_brainviz"):
    sp.use("clean", target="nature")
    try:
        import mne
        from nilearn import datasets, image, plotting
    except ImportError:
        print("skipping demo_brainviz (needs `pip install nilearn mne`)")
        return []
    fig, ax = sp.figure("nature", "double", height_mm=48, mosaic=[["a", "b", "c"]],
                        width_ratios=[2.2, 1, 1])
    tpl = datasets.load_mni152_template(resolution=2)
    ijk = np.indices(tpl.shape).reshape(3, -1).T
    xyz = image.coord_transform(ijk[:, 0], ijk[:, 1], ijk[:, 2], tpl.affine)
    xyz = np.c_[xyz]
    blob = lambda c, s: np.exp(-np.sum((xyz - c) ** 2, 1) / (2 * s ** 2))
    vol = 6 * blob([-40, -70, 5], 8) + 5 * blob([42, -66, 2], 8) - 4 * blob([0, 40, 20], 10)
    stat = image.new_img_like(tpl, vol.reshape(tpl.shape))
    plotting.plot_glass_brain(stat, axes=ax["a"], figure=fig, display_mode="lzr",
                              **neuro.nilearn_kwargs("glass", cmap="cmc.vik", plot_abs=False,
                                                     symmetric_cbar=True, threshold=1.0,
                                                     colorbar=False))
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        mont = mne.channels.make_standard_montage("standard_1005")
    names = [n for n in mont.ch_names if n.rstrip("z").rstrip("0123456789") in
             ("Fp", "AF", "F", "FC", "C", "CP", "P", "PO", "O", "T", "FT", "TP")][:64]
    info = mne.create_info(names, 250, "eeg")
    info.set_montage(mont, on_missing="ignore")
    pos = np.array([info["chs"][i]["loc"][:2] for i in range(len(info.ch_names))])
    for key, (cx, sgn) in zip("bc", [(-0.03, 1), (0.03, -1)]):
        vals = sgn * np.exp(-np.sum((pos - [cx, -0.06]) ** 2, 1) / 0.0012) - 0.3 * np.exp(
            -np.sum((pos - [0, 0.06]) ** 2, 1) / 0.002)
        im, _ = mne.viz.plot_topomap(vals, info, axes=ax[key], show=False,
                                     **neuro.mne_topomap_kwargs(vlim=(-1, 1)))
        ax[key].set_title("P300, left cue" if key == "b" else "P300, right cue")
    sp.slim_colorbar(fig, im, ax["c"], label="z", ticks=[-1, 0, 1])
    neuro.normalize_text(fig)   # nilearn's 12-pt L/R annotations -> style sizes
    sp.label_panels(fig, ax)
    return sp.save(fig, OUT / name, formats=("pdf", "png"), target="nature")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    figure_main()
    figure_slide()
    figure_ml()
    figure_abstract()
    figure_brain()
