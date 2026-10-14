"""Measure every palette (CVD ΔE2000, grayscale, safe prefix length) -> sciplot/data/cvd.json,
and render the visual index -> assets/palette_gallery*.png (+ catalog markdown).

    python palette_gallery.py              # rebuild everything
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import sciplot as sp  # noqa: E402
from sciplot import color as C, palettes as P  # noqa: E402
from sciplot.check import DE_OK, palette_report  # noqa: E402

ASSETS = HERE.parent / "assets"
REFS = HERE.parent / "references"


def measure():
    out = {}
    allp = P.all_palettes()
    for name, p in allp.items():
        cols = p["colors"]
        bg = p.get("background") or ("#0E1117" if p.get("bg") == "dark" else "#FFFFFF")
        if p["kind"] in ("cat", "neutral"):
            if "cat_order" in p:
                cols = [cols[i] for i in p["cat_order"]]
            rep = palette_report(cols, bg=bg, verbose=False)
            # largest prefix that stays CVD-distinct
            safe_n = 1
            for k in range(2, len(cols) + 1):
                r = palette_report(cols[:k], bg=bg, verbose=False)
                if min(r["deutan"], r["protan"], r["tritan"]) >= DE_OK:
                    safe_n = k
                else:
                    break
            rep["safe_n"] = safe_n
        else:
            # ramps: monotone lightness? (perceptual ordering survives CVD/grayscale)
            L = np.array([C.rgb_to_oklab(C.to_rgb(c))[0] for c in cols])
            d = np.diff(L)
            mono = bool(np.all(d > 0) or np.all(d < 0))
            rep = {"lightness_monotonic": mono, "L_range": round(float(L.max() - L.min()), 3),
                   "cvd_safe": mono}
            if p["kind"] == "div":
                i = int(np.argmax(L)) if L[len(L) // 2] > L.mean() else int(np.argmin(L))
                left, right = L[: i + 1], L[i:]
                ok = (np.all(np.diff(left) * np.sign(L[i] - L[0]) >= -0.02) and
                      np.all(np.diff(right) * np.sign(L[-1] - L[i]) >= -0.02) and
                      0.25 < i / (len(L) - 1) < 0.75)
                rep.update(diverging_ok=bool(ok), cvd_safe=bool(ok))
        out[name] = {k: (round(v, 2) if isinstance(v, float) else v) for k, v in rep.items()}
    for name, mapping in P.SEMANTIC.items():
        rep = palette_report(list(mapping.values()), verbose=False)
        out[name] = {k: (round(v, 2) if isinstance(v, float) else v) for k, v in rep.items()}
    (HERE / "sciplot/data/cvd.json").write_text(json.dumps(out, indent=1))
    return out


def _families():
    fam = {}
    for k, v in P.all_palettes().items():
        fam.setdefault(v["family"], []).append(k)
    order = ["original", "accessible", "neuro", "editorial", "design-system", "journal", "trend",
             "heritage", "theme", "art", "cinema", "pop", "ui"]
    return [(f, sorted(fam[f])) for f in order if f in fam] + \
        [(f, sorted(v)) for f, v in fam.items() if f not in order]


def render(meas, cvd_rows=False):
    sp.use("clean", target="web")
    fams = _families()
    blocks = [(f, names) for f, names in fams]
    # one tall PNG per group of families to keep files readable
    pages = {"originals-accessible-neuro": ["original", "accessible", "neuro"],
             "editorial-design": ["editorial", "design-system", "journal", "trend", "heritage",
                                  "theme", "ui", "pop"],
             "art-cinema": ["art", "cinema"]}
    written = []
    for page, fl in pages.items():
        rows = []
        for f, names in blocks:
            if f in fl:
                rows.append(("__h__", f))
                rows += [(n, None) for n in names]
        h = 0.26 * len(rows) + 0.4
        fig = plt.figure(figsize=(8.2, h), layout="none")
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(-11, 17.5)
        ax.set_ylim(-len(rows), 0.8)
        ax.set_axis_off()
        for i, (n, _) in enumerate(rows):
            y = -i
            if n == "__h__":
                ax.text(-10.8, y, _.upper(), fontsize=8, weight="bold", va="center", color="#1F2328")
                continue
            p = P.all_palettes()[n]
            cols = P.get(n) if p["kind"] in ("cat", "neutral") else p["colors"]
            m = meas.get(n, {})
            if p["kind"] in ("seq", "div", "cyc"):
                grad = np.linspace(0, 1, 256)[None]
                ax.imshow(grad, extent=(0, 12, y - 0.36, y + 0.36), aspect="auto",
                          cmap=P.cmap(n), zorder=2)
                if p["kind"] == "div":
                    tag = "✓ symmetric L" if m.get("diverging_ok") else "· check center"
                else:
                    tag = "✓ monotone L" if m.get("lightness_monotonic") else "· non-monotone"
            else:
                wcell = min(12 / max(len(cols), 1), 1.5)
                for j, c in enumerate(cols[:14]):
                    ax.add_patch(plt.Rectangle((j * wcell, y - 0.36), wcell * 0.92, 0.72, fc=c, lw=0))
                worst = min(m.get("deutan", 0), m.get("protan", 0), m.get("tritan", 0))
                tag = (f"CVD ΔE {worst:4.1f}  safe≤{m.get('safe_n', '?')}")
            bgc = p.get("background")
            if bgc:
                ax.add_patch(plt.Rectangle((-0.35, y - 0.4), 0.22, 0.8, fc=bgc, ec="#C9CDD2", lw=0.4))
            ax.text(-0.6, y, n, ha="right", va="center", fontsize=6.5, color="#1F2328")
            ax.text(12.3, y, f"{p['kind']:>4}  {tag}", ha="left", va="center", fontsize=5.5,
                    color="#6B7280", family="monospace")
        path = ASSETS / f"palette_gallery_{page}.png"
        fig.savefig(path, dpi=170, facecolor="white")
        plt.close(fig)
        written.append(path)
    # semantic sets + neutrals/backgrounds
    rows = list(P.SEMANTIC.items())
    fig = plt.figure(figsize=(8.2, 0.34 * (len(rows) + 4)), layout="none")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(-6, 22)
    ax.set_ylim(-(len(rows) + 3), 0.8)
    ax.set_axis_off()
    for i, (n, mp) in enumerate(rows):
        ax.text(-0.3, -i, n, ha="right", va="center", fontsize=6.5)
        for j, (lab, c) in enumerate(mp.items()):
            ax.add_patch(plt.Rectangle((j * 3.3, -i - 0.36), 0.7, 0.72, fc=c, lw=0))
            ax.text(j * 3.3 + 0.85, -i, lab, va="center", fontsize=5.2, color="#3D434B")
    for k, (title, d) in enumerate([("neutrals", P.NEUTRALS), ("backgrounds", P.BACKGROUNDS)]):
        y = -(len(rows) + 1 + k)
        ax.text(-0.3, y, title, ha="right", va="center", fontsize=6.5, weight="bold")
        for j, (lab, c) in enumerate(d.items()):
            ax.add_patch(plt.Rectangle((j * 1.4, y - 0.36), 1.25, 0.72, fc=c, ec="#C9CDD2", lw=0.3))
    path = ASSETS / "palette_gallery_semantic.png"
    fig.savefig(path, dpi=170, facecolor="white")
    plt.close(fig)
    written.append(path)
    return written


def catalog(meas):
    """references/palettes.md — the human-readable index."""
    lines = ["# Palette bank catalog (generated by palette_gallery.py — do not edit by hand)", "",
             "Columns: name · kind · n · bg · measured min CVD ΔE2000 (deutan/protan/tritan) · "
             "safe_n (how many leading colors stay ≥10 ΔE under all CVD types) · mood · source.",
             "Use `sp.palettes.info(name)` for full metadata; images in `assets/palette_gallery_*.png`.",
             ""]
    for f, names in _families():
        lines += [f"## {f}", "", "| name | kind | n | bg | CVD ΔE | safe_n | mood / best for | source |",
                  "|---|---|---|---|---|---|---|---|"]
        for n in names:
            p = P.all_palettes()[n]
            m = meas.get(n, {})
            if p["kind"] in ("cat", "neutral"):
                de = f"{m.get('deutan', 0):.0f}/{m.get('protan', 0):.0f}/{m.get('tritan', 0):.0f}"
                sn = m.get("safe_n", "")
            else:
                de = ("sym L" if m.get("diverging_ok") else "check") if p["kind"] == "div" else \
                    ("mono L" if m.get("lightness_monotonic") else "non-mono")
                sn = ""
            mood = ", ".join(p.get("mood", []))
            bf = p.get("best_for", "")
            desc = "; ".join(x for x in (mood, bf) if x)
            lines.append(f"| `{n}` | {p['kind']} | {len(p['colors'])} | {p.get('bg', 'light')} | {de} | "
                         f"{sn} | {desc} | {p.get('source', '')} |")
        lines.append("")
    lines += ["## semantic mappings (`sp.semantic(name)`)", ""]
    for n, mp in P.SEMANTIC.items():
        lines.append(f"- `{n}`: " + ", ".join(f"{k} `{v}`" for k, v in mp.items()))
    lines += ["", "## external colormaps resolvable by `sp.cmap(name)`", ""]
    for kind in ("seq", "div", "cyc", "cat"):
        ns = [f"`{k}` ({', '.join(t)})" for k, (kd, t) in P.CMAPS.items() if kd == kind]
        lines.append(f"- **{kind}**: " + "; ".join(ns))
    (REFS / "palettes.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    REFS.mkdir(exist_ok=True)
    meas = measure()
    P._cvd.cache_clear()
    for p in render(meas):
        print("wrote", p)
    catalog(meas)
    n_cat = sum(1 for k, v in P.all_palettes().items() if v["kind"] == "cat")
    n_safe = sum(1 for k, v in meas.items() if v.get("cvd_safe") and k in P.all_palettes()
                 and P.all_palettes()[k]["kind"] == "cat")
    print(f"{len(P.all_palettes())} palettes, {len(P.SEMANTIC)} semantic sets; "
          f"{n_safe}/{n_cat} categorical palettes fully CVD-safe")
