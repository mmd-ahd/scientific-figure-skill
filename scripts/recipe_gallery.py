"""Gallery images for the README: one panel per recipe, and one figure in every theme.

    python scripts/recipe_gallery.py [outdir]     # -> recipe_gallery.{png,pdf}, themes.png
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


def data(seed=3):
    rng = np.random.default_rng(seed)
    t = np.linspace(-0.5, 1.5, 161)
    curves = [5 + a * np.exp(-((t - 0.3 - 0.1 * i) / 0.15) ** 2) * (t > 0)
              for i, a in enumerate((8, 16, 24))]
    trials = [c[None] + np.array([np.convolve(rng.normal(0, 4, t.size), np.ones(9) / 9, "same")
                                  for _ in range(30)]) for c in curves]
    spikes = [np.sort(rng.uniform(-0.5, 1.5, rng.poisson(8))) if k % 3 else
              np.sort(np.r_[rng.uniform(-0.5, 1.5, 4), rng.normal(0.35, 0.08, 10)]) for k in range(36)]
    nN, nT = 120, 100
    peaks = rng.uniform(0, nT, nN)
    A = np.exp(-((np.arange(nT)[None] - peaks[:, None]) / 7) ** 2) + rng.normal(0, 0.04, (nN, nT))
    lab = np.repeat([0, 1, 2], 6)
    X = rng.normal(0, 1, (18, 25)) + np.eye(3)[lab] @ rng.normal(0, 2, (3, 25))
    D = 1 - np.corrcoef(X)
    ph = np.linspace(0, 3 * np.pi, 120)
    traj = [np.c_[np.cos(ph + k), np.sin(ph + k)] * (1 + 0.2 * k) * np.exp(-ph / 10)[:, None]
            + np.cumsum(rng.normal(0, 0.012, (120, 2)), 0) for k in range(3)]
    th = rng.uniform(0, 2 * np.pi, 1500)
    Z = np.c_[np.cos(th), np.sin(th)] * (1 + rng.normal(0, 0.08, (1500, 1)))
    groups = [rng.normal(m, 0.07, 14) for m in (0.55, 0.63, 0.76)]
    W = rng.normal(0, 1, (16, 16)) * (rng.random((16, 16)) < 0.4)
    W[:, 12:] = -np.abs(W[:, 12:])
    W[:, :12] = np.abs(W[:, :12])
    steps = np.arange(200)
    runs = [1 - np.exp(-steps / s) + rng.normal(0, 0.02, (5, 200)) for s in (30, 60)]
    theta = np.linspace(0, np.pi, 9)
    tune = [4 + 14 * np.exp(np.cos(2 * (theta - p)) * 1.5) / np.exp(1.5) for p in (0.6, 1.9)]
    return dict(t=t, trials=trials, spikes=spikes, A=A, D=D, traj=traj, Z=Z, th=th, groups=groups, W=W,
                steps=steps, runs=runs, theta=theta, tune=tune)


def recipe_gallery(name="recipe_gallery"):
    sp.use("clean", target="web", palette="sp.neuro")
    pal, tc = sp.colors("sp.neuro"), sp.theme_colors()
    d = data()
    mosaic = "ABCD;EFGH;IJKL"
    fig, ax = sp.figure("web", "double", height_mm=165, mosaic=mosaic)

    a = ax["A"]  # schematic
    W_, H_ = S.canvas(a)
    b1 = S.box(a, (2, H_ * 0.55), text="Stimulus", fc=sp.color.lighten(pal[0], 0.82), ec=pal[0],
               text_color=pal[0])
    b2 = S.box(a, (W_ * 0.58, H_ * 0.55), text="RNN", fc=sp.color.lighten(pal[1], 0.82), ec=pal[1],
               text_color=sp.color.darken(pal[1], 0.15))
    S.connect(a, b1, b2, color=tc["muted"])
    S.network(a, [3, 4, 2], xy=(W_ * 0.2, 2), width=W_ * 0.6, height=H_ * 0.42, r=1.4,
              colors=["#FFFFFF", sp.color.lighten(pal[2], 0.6), "#FFFFFF"],
              edge_color=sp.color.mix(tc["bg"], tc["muted"], 0.45), node_ec=tc["fg"])
    a.set_title("schematic.*")

    for k, c in enumerate([tc["context"], pal[0], pal[1]]):
        neuro.mean_ci(ax["B"], d["t"], d["trials"][k], c, label=["low", "mid", "high"][k])
    sp.shade(ax["B"], 0, 0.5)
    sp.label_lines(ax["B"])
    ax["B"].set(xlabel="Time (s)", ylabel="Rate (Hz)", title="mean_ci")

    neuro.raster(ax["C"], d["spikes"], color=tc["fg"])
    sp.event_lines(ax["C"], [0], color=pal[1])
    ax["C"].set(xlabel="Time (s)", ylabel="Trial", title="raster")

    neuro.activity_heatmap(ax["D"], d["A"], sort="peak", scalebar=dict(dx=20, xlabel="1 s", dy=20, ylabel="20 cells"))
    ax["D"].set_title("activity_heatmap")

    neuro.rdm(ax["E"], d["D"], groups=[(0, 6, "faces"), (6, 12, "bodies"), (12, 18, "objects")],
              group_colors=pal[:3])
    ax["E"].set_title("rdm", pad=10)

    for k, X in enumerate(d["traj"]):
        neuro.trajectories(ax["F"], X, color=pal[k])
    ax["F"].set_axis_off()
    neuro.axis_arrows(ax["F"], "PC 1", "PC 2")
    ax["F"].set_title("trajectories")

    neuro.embedding(ax["G"], d["Z"], c=d["th"], cmap="twilight",
                    s=2)
    ax["G"].set_axis_off()
    neuro.axis_arrows(ax["G"], "UMAP 1", "UMAP 2")
    ax["G"].set_title("embedding")

    neuro.connectivity(ax["H"], d["W"], ei_split=12)
    ax["H"].set_title("connectivity")

    cols = [tc["context"], pal[0], pal[1]]
    neuro.dots_and_summary(ax["I"], d["groups"], cols, labels=["Ctrl", "Opto", "Model"])
    sp.sig_bracket(ax["I"], 0, 2, y=0.9, text=0.002)
    ax["I"].set(ylabel="Accuracy", title="dots_and_summary", ylim=(0.35, 0.98))

    neuro.raincloud(ax["J"], d["groups"], cols, labels=["Ctrl", "Opto", "Model"])
    ax["J"].set(ylabel="Accuracy", title="raincloud")

    layers = ["L1", "L2", "L3", "L4", "L5", "L6"]
    neuro.layer_profile(ax["K"], layers, [0.30, 0.41, 0.35, 0.27, 0.2, 0.16], pal[0], label="V1",
                        err=[0.03] * 6, ceiling=(0.52, 0.58))
    neuro.layer_profile(ax["K"], layers, [0.08, 0.15, 0.27, 0.40, 0.47, 0.45], pal[1], label="IT",
                        err=[0.03] * 6)
    ax["K"].set(ylabel="Encoding R²", title="layer_profile")

    for k, r in enumerate(d["runs"]):
        neuro.learning_curves(ax["L"], d["steps"], r, pal[k], label=["Adam", "SGD"][k])
    sp.label_lines(ax["L"])
    ax["L"].set(xlabel="Step", ylabel="Accuracy", title="learning_curves")

    sp.align_labels(fig)
    sp.label_panels(fig, ax)
    return sp.save(fig, OUT / name, formats=("png", "pdf"), target="web", dpi=300)


def themes(name="themes"):
    d = data()
    names = ["clean", "editorial", "soft", "ink", "paper", "dark"]
    pngs = []
    for th in names:
        sp.use(th, target="web")
        pal, tc = sp.colors(sp.styles.THEMES[th]["palette"]), sp.theme_colors()
        fig, ax = sp.figure("web", "single", height_mm=62, mosaic="AB")
        for k in range(3):
            c = tc["context"] if k == 0 else pal[k - 1]
            neuro.mean_ci(ax["A"], d["t"], d["trials"][k], c, label=["low", "mid", "high"][k])
        sp.label_lines(ax["A"])
        ax["A"].set(xlabel="Time (s)", ylabel="Rate (Hz)", title=f"{th}")
        neuro.dots_and_summary(ax["B"], d["groups"], [tc["context"], pal[0], pal[1]],
                               labels=["Ctrl", "Opto", "Model"])
        ax["B"].set(ylabel="Accuracy")
        p = OUT / f"_theme_{th}.png"
        fig.savefig(p, dpi=200, facecolor=fig.get_facecolor())
        plt.close(fig)
        pngs.append(p)
    imgs = [plt.imread(p) for p in pngs]
    h = min(i.shape[0] for i in imgs)
    w = min(i.shape[1] for i in imgs)
    imgs = [i[:h, :w, :3] for i in imgs]
    grid = np.vstack([np.hstack(imgs[r * 3:(r + 1) * 3]) for r in range(2)])
    plt.imsave(OUT / f"{name}.png", grid)
    for p in pngs:
        p.unlink()
    print(f"saved {name}.png")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    recipe_gallery()
    themes()
