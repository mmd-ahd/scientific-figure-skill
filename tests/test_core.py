"""Core API: import surface, styles, layout, export, lint."""
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
MM = 1 / 25.4


def test_public_api(sp):
    for name in sp.__all__:
        assert hasattr(sp, name), name
    assert sp.__version__


@pytest.mark.parametrize("theme", ["clean", "editorial", "soft", "ink", "paper", "dark"])
@pytest.mark.parametrize("target", ["nature", "nature-research", "ncomms", "cell", "science", "elife",
                                    "pnas", "jneurosci", "plos", "neurips", "icml", "slide", "poster",
                                    "graphical-abstract", "web"])
def test_use_every_theme_and_venue(sp, theme, target):
    sp.use(theme, target=target)
    tc = sp.theme_colors()
    assert {"bg", "fg"} <= set(tc)


@pytest.mark.parametrize("target", ["nature", "cell", "science", "neurips", "icml", "pnas"])
def test_figure_width_matches_venue(sp, target):
    sp.use("clean", target=target)
    for key, w in sp.VENUES[target]["widths_mm"].items():
        fig, _ = sp.figure(target, key, height_mm=50)
        assert abs(fig.get_size_inches()[0] / MM - w) < 0.05


def test_mosaic_and_panel_labels(sp):
    sp.use("clean", target="nature")
    fig, ax = sp.figure("nature", "double", height_mm=60, mosaic="AB;CD")
    for a in ax.values():
        a.plot([0, 1], [0, 1])
    sp.align_labels(fig)
    sp.label_panels(fig, ax)
    texts = {t.get_text() for t in fig.texts}
    assert {"a", "b", "c", "d"} <= texts  # Nature: lowercase letters


def test_save_formats_and_exact_size(sp, tmp_path):
    sp.use("clean", target="nature")
    fig, ax = sp.figure("nature", "single", height_mm=50)
    ax.plot(np.arange(10), np.arange(10) ** 0.5)
    ax.set(xlabel="Time (s)", ylabel="Rate (Hz)")
    out = sp.save(fig, tmp_path / "fig", formats=("pdf", "svg", "png"), target="nature")
    assert len(out) == 3 and all(Path(p).stat().st_size > 0 for p in out)
    pdf = (tmp_path / "fig.pdf").read_bytes()
    assert b"/FontType 3" not in pdf and b"/Subtype /Type3" not in pdf  # editable TrueType text
    svg = (tmp_path / "fig.svg").read_text()
    assert "<text" in svg  # text kept as text, not paths
    from matplotlib import image
    h, w = image.imread(tmp_path / "fig.png").shape[:2]
    assert abs(w / 600 / MM - 89) < 0.5  # no bbox_inches="tight" resizing


def test_lint_passes_good_figure(sp):
    sp.use("clean", target="nature")
    fig, ax = sp.figure("nature", "single", height_mm=50)
    ax.plot([0, 1], [0, 1])
    ax.set_xlabel("x")
    warns = sp.check.lint(fig, "nature", verbose=False)
    assert not [w for w in warns if "font" not in w]  # font availability depends on the machine


def test_lint_flags_bad_figure(sp):
    sp.use("clean", target="nature")
    fig, ax = sp.figure("nature", "single", height_mm=50)
    ax.imshow(np.random.default_rng(0).random((5, 5)), cmap="jet")
    ax.set_title("tiny", fontsize=3)
    ax.plot([0, 1], [0, 1], lw=0.1)
    warns = " ".join(sp.check.lint(fig, "nature", verbose=False))
    assert "below 5 pt" in warns
    assert "rainbow" in warns
    assert "thinner" in warns


def test_lint_flags_wrong_width(sp):
    import matplotlib.pyplot as plt
    sp.use("clean", target="nature")
    fig = plt.figure(figsize=(150 * MM, 50 * MM))
    fig.add_subplot().plot([0, 1])
    assert any("width" in w for w in sp.check.lint(fig, "nature", verbose=False))


def test_mplstyles_are_up_to_date(sp, tmp_path):
    n = sp.styles.write_mplstyles(tmp_path)
    committed = sorted((ROOT / "styles").glob("*.mplstyle"))
    assert n == len(committed)
    for f in committed:
        assert (tmp_path / f.name).read_text() == f.read_text(), (
            f"{f.name} is stale: run `python -c \"import sciplot.styles as s; s.write_mplstyles()\"`")


def test_mplstyle_usable_without_package():
    import matplotlib.pyplot as plt
    with plt.style.context(str(ROOT / "styles" / "clean-nature.mplstyle")):
        fig, ax = plt.subplots()
        ax.plot([0, 1])
        assert plt.rcParams["font.size"] == 7
