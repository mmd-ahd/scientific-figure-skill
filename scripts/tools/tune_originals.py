"""Nudge 'sp.*' categorical palettes in OKLCH to maximise min ΔE2000 under CVD
while staying perceptually close to the designed seed colors."""
import sys
import numpy as np
sys.path.insert(0, ".")
from sciplot import color as C, palettes as P
from sciplot.check import palette_report

TARGET = 11.0   # min ΔE2000 under each CVD type; stop pushing once reached


def score(cols, seeds, bg, max_drift):
    r = palette_report(cols, bg=bg, verbose=False)
    cvd = min(r["deutan"], r["protan"], r["tritan"])
    drifts = [C.delta_e(a, b) for a, b in zip(cols, seeds)]
    drift = max(drifts)
    pen = max(0, drift - max_drift) * 3 + 0.25 * float(np.mean(drifts))
    return min(cvd, TARGET) * 2 + 0.05 * min(r["normal"], 25) - pen, r, drift

def tune(name, iters=4000, max_drift=8, seed=0):
    p = P.BANK[name]
    seeds = p["colors"]
    bg = p.get("background", "#0E1117" if p["bg"] == "dark" else "#FFFFFF")
    lch = np.array([C.rgb_to_oklch(C.to_rgb(c)) for c in seeds])
    rng = np.random.default_rng(seed)
    best = seeds
    best_s, r0, _ = score(seeds, seeds, bg, max_drift)
    cur = lch.copy()
    for it in range(iters):
        cand = cur.copy()
        i = rng.integers(len(cand))
        cand[i] += rng.normal(0, [0.015, 0.008, 4])
        cand[i, 0] = np.clip(cand[i, 0], 0.25, 0.92)
        cand[i, 1] = np.clip(cand[i, 1], 0, 0.3)
        cols = [C.oklch(*x) for x in cand]
        s, r, d = score(cols, seeds, bg, max_drift)
        if s > best_s:
            best_s, best, cur = s, cols, cand
    s, r, d = score(best, seeds, bg, max_drift)
    print(f'{name:16s} before D/P/T={r0["deutan"]:.1f}/{r0["protan"]:.1f}/{r0["tritan"]:.1f}  '
          f'after {r["deutan"]:.1f}/{r["protan"]:.1f}/{r["tritan"]:.1f} N={r["normal"]:.1f} drift={d:.1f}')
    print('   ', best)
    return best

names = sys.argv[1:] or [k for k, v in P.BANK.items() if k.startswith("sp.") and v["kind"] == "cat"]
for n in names:
    tune(n)
