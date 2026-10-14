"""Every panel recipe draws without error on a minimal install."""
import numpy as np
import pytest

rng = np.random.default_rng(0)


@pytest.fixture
def ax(sp):
    sp.use("clean", target="nature")
    fig, ax = sp.figure("nature", "single", height_mm=50)
    return ax


def test_time_series(sp, ax):
    from sciplot import neuro
    t = np.linspace(0, 1, 50)
    Y = rng.normal(size=(20, 50))
    for ci in ("sem", "sd", 95):
        neuro.mean_ci(ax, t, Y, "C0", ci=ci, label=str(ci))
    neuro.gradient_line(ax, t, np.sin(t))
    sp.label_lines(ax)
    sp.shade(ax, 0.2, 0.4, label="stim")
    sp.event_lines(ax, [0.5], labels=["go"])


def test_spikes(sp, ax):
    from sciplot import neuro
    spikes = [np.sort(rng.uniform(0, 1, 20)) for _ in range(10)]
    neuro.raster(ax, spikes)
    rate = neuro.psth(spikes, np.linspace(0, 1, 21), smooth_sd=1)
    assert rate.shape[-1] == 20


def test_matrices(sp):
    from sciplot import neuro
    sp.use("clean", target="nature")
    fig, ax = sp.figure("nature", "double", height_mm=50, mosaic="ABC")
    neuro.activity_heatmap(ax["A"], rng.random((30, 40)), zscore=True)
    D = 1 - np.corrcoef(rng.normal(size=(12, 20)))
    neuro.rdm(ax["B"], D, groups=[(0, 6, "faces"), (6, 12, "objects")])
    neuro.connectivity(ax["C"], rng.normal(size=(10, 10)), ei_split=8)


def test_latents(sp):
    from sciplot import neuro
    sp.use("clean", target="nature")
    fig, ax = sp.figure("nature", "double", height_mm=50, mosaic="AB")
    X = np.cumsum(rng.normal(size=(50, 2)), 0)
    neuro.trajectories(ax["A"], X, cmap="viridis")
    neuro.embedding(ax["B"], rng.normal(size=(500, 2)), c=rng.random(500))
    neuro.axis_arrows(ax["B"], "UMAP 1", "UMAP 2")
    fig3 = __import__("matplotlib.pyplot").pyplot.figure()
    a3 = fig3.add_subplot(projection="3d")
    neuro.trajectories(a3, np.cumsum(rng.normal(size=(50, 3)), 0), color="C1", three_d=True)
    neuro.style_3d(a3)


def test_stats(sp):
    from sciplot import neuro
    sp.use("clean", target="nature")
    fig, ax = sp.figure("nature", "double", height_mm=50, mosaic="AB")
    groups = [rng.normal(0, 1, 15), rng.normal(1, 1, 15)]
    neuro.dots_and_summary(ax["A"], groups, ["0.5", "C0"], labels=["a", "b"])
    sp.sig_bracket(ax["A"], 0, 1, y=3, text=0.003)
    neuro.raincloud(ax["B"], groups, ["0.5", "C0"], labels=["a", "b"])
    assert "P" in sp.annotate.fmt_p(0.0001)


def test_model_panels(sp):
    from sciplot import neuro
    sp.use("clean", target="neurips")
    fig, ax = sp.figure("neurips", "single", height_mm=40, mosaic="ABC")
    layers = ["L1", "L2", "L3", "L4"]
    neuro.layer_profile(ax["A"], layers, [0.1, 0.3, 0.4, 0.2], "C0", err=[0.02] * 4, ceiling=(0.5, 0.6))
    neuro.tuning_curve(ax["B"], np.linspace(0, np.pi, 8), rng.random(8), "C1")
    neuro.learning_curves(ax["C"], np.arange(100), rng.random((5, 100)).cumsum(1), "C2", smooth=5)


def test_brainviz_presets_need_no_packages(sp):
    from sciplot import neuro
    assert isinstance(neuro.nilearn_kwargs("stat"), dict)
    assert isinstance(neuro.mne_topomap_kwargs(), dict)
    assert isinstance(neuro.pycortex_quickflat_kwargs(), dict)


def test_schematic(sp):
    from sciplot import schematic as S
    sp.use("clean", target="nature")
    fig, ax = sp.figure("nature", "single", height_mm=50)
    W, H = S.canvas(ax)
    a = S.box(ax, (2, 2), text="Input")
    b = S.box(ax, (40, 2), text="Model")
    S.connect(ax, a, b)
    S.pill(ax, (2, 20), text="loss")
    S.circle(ax, (60, 30), 3, text="z")
    S.arrow(ax, (10, 30), (30, 30), rad=0.2)
    S.pipeline(ax, ["A", "B", "C"], xy=(2, 35))
    S.network(ax, [3, 4, 2], xy=(50, 5), width=30, height=20)
    S.recurrent_unit(ax, (75, 40))
    S.layer_stack(ax, (5, 10), 6, 6)
    S.prism(ax, (20, 10), 6, 6)
    S.mini_trace(ax, (30, 40), 10, 5)
    S.mini_matrix(ax, (45, 40), 6, cmap="cmc.batlow")
    S.gradient_box(ax, (60, 2), 10, 5, "#FFFFFF", "#3366AA")
    S.bracket(ax, 2, 20, 45, text="encoder")
