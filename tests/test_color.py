"""Palette bank, colour math and CVD checks."""
import warnings

import numpy as np
import pytest


def test_every_palette_loads(sp):
    names = sp.palettes.names()
    assert len(names) >= 150
    for n in names:
        cols = sp.colors(n)
        assert len(cols) >= 2, n
        assert all(isinstance(c, str) and c.startswith("#") for c in cols), n


def test_palette_measurements(sp):
    info = sp.palettes.info("sp.neuro")
    assert info["measured"]["safe_n"] >= 3


def test_search(sp):
    hits = sp.search(kind="cat", cvd_safe=True, min_n=4)
    assert hits and all(sp.palettes.info(h)["kind"] == "cat" for h in hits)


@pytest.mark.parametrize("name", ["sp.neuro", "viridis", "cmc.batlow", "cmc.vik", "cmr.ember", "mako"])
def test_cmap_resolves_with_or_without_optional_packages(sp, name):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        cm = sp.cmap(name)
    rgba = cm(0.5)
    assert len(rgba) == 4


def test_external_cmap_names_work_in_plain_matplotlib(sp):
    import matplotlib.pyplot as plt
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        sp.use("clean", target="nature")
    fig, ax = plt.subplots()
    ax.imshow(np.eye(3), cmap="cmc.batlow")  # aliased if cmcrameri is absent


def test_oklch_roundtrip(sp):
    C = sp.color
    for hexc in ["#1f77b4", "#D1495B", "#00A087", "#777777"]:
        back = C.oklch(*C.rgb_to_oklch(C.to_rgb(hexc)))
        assert C.delta_e(hexc, back) < 0.5


def test_contrast_and_cvd(sp):
    C = sp.color
    assert C.contrast_ratio("#000000", "#FFFFFF") == pytest.approx(21, rel=1e-3)
    sim = C.simulate_cvd(["#FF0000", "#00FF00"], "deutan")
    assert sim.shape == (2, 3) and np.all((sim >= 0) & (sim <= 1))


def test_palette_report_flags_red_green(sp):
    r = sp.check.palette_report(["#E41A1C", "#4DAF4A"], verbose=False)
    assert r["deutan"] < r["normal"]


def test_helpers(sp):
    assert len(sp.highlight(5, 2)) == 5
    assert len(sp.shades("#3366AA", 4)) == 4
    assert len(sp.palettes.build_categorical(5)) == 5
