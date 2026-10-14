"""Color math: hex/RGB, OKLab/OKLCH, CIEDE2000, CVD simulation, contrast, tints.

Pure numpy. `colorspacious` is used for CVD simulation when installed (it is in
the neuroai env); otherwise the Machado et al. (2009) severity-1.0 matrices
below are applied in linear sRGB, which is what colorspacious does too.
"""
from __future__ import annotations

import numpy as np

# ----------------------------------------------------------------- conversions

def to_rgb(c) -> np.ndarray:
    """Any matplotlib color spec (hex, name, tuple) -> float RGB array in [0, 1]."""
    if isinstance(c, str) and c.startswith("#") and len(c) in (7, 9):
        return np.array([int(c[i:i + 2], 16) for i in (1, 3, 5)], float) / 255
    from matplotlib.colors import to_rgb as _to_rgb
    return np.asarray(_to_rgb(c), float)


def to_hex(rgb) -> str:
    rgb = np.clip(np.asarray(rgb, float), 0, 1)
    return "#" + "".join(f"{int(round(v * 255)):02X}" for v in rgb[:3])


def _srgb_to_linear(c):
    c = np.asarray(c, float)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def _linear_to_srgb(c):
    c = np.asarray(c, float)
    return np.where(c <= 0.0031308, 12.92 * c, 1.055 * np.abs(c) ** (1 / 2.4) - 0.055)


_M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929],
                [0.2119034982, 0.6806995451, 0.1073969566],
                [0.0883024619, 0.2817188376, 0.6299787005]])
_M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468],
                [1.9779984951, -2.4285922050, 0.4505937099],
                [0.0259040371, 0.7827717662, -0.8086757660]])


def rgb_to_oklab(rgb):
    lms = _srgb_to_linear(rgb) @ _M1.T
    return np.cbrt(lms) @ _M2.T


def oklab_to_rgb(lab, clip=True):
    lms = (np.asarray(lab, float) @ np.linalg.inv(_M2).T) ** 3
    rgb = _linear_to_srgb(lms @ np.linalg.inv(_M1).T)
    return np.clip(rgb, 0, 1) if clip else rgb


def rgb_to_oklch(rgb):
    L, a, b = np.moveaxis(rgb_to_oklab(rgb), -1, 0)
    return np.stack([L, np.hypot(a, b), np.degrees(np.arctan2(b, a)) % 360], -1)


def oklch_to_rgb(lch, clip=True):
    L, C, h = np.moveaxis(np.asarray(lch, float), -1, 0)
    hr = np.radians(h)
    return oklab_to_rgb(np.stack([L, C * np.cos(hr), C * np.sin(hr)], -1), clip=clip)


def in_gamut(lch, eps=1e-4) -> bool:
    rgb = oklch_to_rgb(lch, clip=False)
    return bool(np.all(rgb >= -eps) and np.all(rgb <= 1 + eps))


def oklch(L, C, h) -> str:
    """Hex for an OKLCH color; chroma is reduced until it fits in sRGB."""
    while C > 0 and not in_gamut([L, C, h]):
        C -= 0.002
    return to_hex(oklch_to_rgb([L, max(C, 0), h]))


def rgb_to_lab(rgb):
    """sRGB -> CIELAB (D65)."""
    lin = _srgb_to_linear(rgb)
    M = np.array([[0.4124564, 0.3575761, 0.1804375],
                  [0.2126729, 0.7151522, 0.0721750],
                  [0.0193339, 0.1191920, 0.9503041]])
    xyz = lin @ M.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > (6 / 29) ** 3, np.cbrt(xyz), xyz / (3 * (6 / 29) ** 2) + 4 / 29)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]),
                     200 * (f[..., 1] - f[..., 2])], -1)


def delta_e(c1, c2) -> float:
    """CIEDE2000 color difference between two colors (any matplotlib spec).
    Rough scale: <2 indistinguishable, ~5 just distinct, >=10 clearly distinct
    categories, >=20 comfortably distinct at small mark sizes."""
    return de2000_lab(rgb_to_lab(to_rgb(c1)), rgb_to_lab(to_rgb(c2)))


def de2000_lab(lab1, lab2) -> float:
    L1, a1, b1 = lab1
    L2, a2, b2 = lab2
    C1, C2 = np.hypot(a1, b1), np.hypot(a2, b2)
    Cb = (C1 + C2) / 2
    G = 0.5 * (1 - np.sqrt(Cb ** 7 / (Cb ** 7 + 25 ** 7)))
    a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = np.hypot(a1p, b1), np.hypot(a2p, b2)
    h1p = np.degrees(np.arctan2(b1, a1p)) % 360
    h2p = np.degrees(np.arctan2(b2, a2p)) % 360
    dLp, dCp = L2 - L1, C2p - C1p
    dh = h2p - h1p
    if C1p * C2p == 0:
        dh = 0
    elif dh > 180:
        dh -= 360
    elif dh < -180:
        dh += 360
    dHp = 2 * np.sqrt(C1p * C2p) * np.sin(np.radians(dh / 2))
    Lbp, Cbp = (L1 + L2) / 2, (C1p + C2p) / 2
    if C1p * C2p == 0:
        hbp = h1p + h2p
    elif abs(h1p - h2p) <= 180:
        hbp = (h1p + h2p) / 2
    else:
        hbp = (h1p + h2p + 360) / 2 if h1p + h2p < 360 else (h1p + h2p - 360) / 2
    T = (1 - 0.17 * np.cos(np.radians(hbp - 30)) + 0.24 * np.cos(np.radians(2 * hbp))
         + 0.32 * np.cos(np.radians(3 * hbp + 6)) - 0.20 * np.cos(np.radians(4 * hbp - 63)))
    dtheta = 30 * np.exp(-(((hbp - 275) / 25) ** 2))
    Rc = 2 * np.sqrt(Cbp ** 7 / (Cbp ** 7 + 25 ** 7))
    Sl = 1 + 0.015 * (Lbp - 50) ** 2 / np.sqrt(20 + (Lbp - 50) ** 2)
    Sc, Sh = 1 + 0.045 * Cbp, 1 + 0.015 * Cbp * T
    Rt = -np.sin(np.radians(2 * dtheta)) * Rc
    return float(np.sqrt((dLp / Sl) ** 2 + (dCp / Sc) ** 2 + (dHp / Sh) ** 2
                         + Rt * (dCp / Sc) * (dHp / Sh)))


# ----------------------------------------------------------------- CVD

_MACHADO = {  # severity 1.0, applied to linear sRGB
    "protan": np.array([[0.152286, 1.052583, -0.204868],
                        [0.114503, 0.786281, 0.099216],
                        [-0.003882, -0.048116, 1.051998]]),
    "deutan": np.array([[0.367322, 0.860646, -0.227968],
                        [0.280085, 0.672501, 0.047413],
                        [-0.011820, 0.042940, 0.968881]]),
    "tritan": np.array([[1.255528, -0.076749, -0.178779],
                        [-0.078411, 0.930809, 0.147602],
                        [0.004733, 0.691367, 0.303900]]),
}
CVD_TYPES = ("deutan", "protan", "tritan")


def simulate_cvd(colors, kind="deutan", severity=100):
    """Simulate color-vision deficiency. `colors`: list of specs or (...,3) array.
    Returns an array of the same leading shape, RGB in [0, 1]."""
    if isinstance(colors, str):
        arr = to_rgb(colors)
    elif isinstance(colors, np.ndarray):
        arr = colors.astype(float)
    else:
        arr = np.asarray([to_rgb(c) for c in colors])
    try:
        from colorspacious import cspace_convert
        name = {"deutan": "deuteranomaly", "protan": "protanomaly", "tritan": "tritanomaly"}[kind]
        out = cspace_convert(arr, {"name": "sRGB1+CVD", "cvd_type": name,
                                   "severity": severity}, "sRGB1")
    except ImportError:
        lin = _srgb_to_linear(arr)
        M = _MACHADO[kind] if severity >= 100 else (
            np.eye(3) + (_MACHADO[kind] - np.eye(3)) * severity / 100)
        out = _linear_to_srgb(lin @ M.T)
    return np.clip(out, 0, 1)


def grayscale(colors):
    """Luminance-preserving grayscale (CIELAB L*) of a list of colors -> RGB array."""
    L = rgb_to_lab(np.asarray([to_rgb(c) for c in colors]))[..., 0] / 100
    # invert L* -> sRGB gray
    Y = np.where(L > 0.08, ((L * 100 + 16) / 116) ** 3, L * 100 / 903.3)
    g = _linear_to_srgb(Y)
    return np.repeat(g[:, None], 3, axis=1)


# ----------------------------------------------------------------- contrast

def luminance(c) -> float:
    r, g, b = _srgb_to_linear(to_rgb(c))
    return float(0.2126 * r + 0.7152 * g + 0.0722 * b)


def contrast_ratio(c1, c2) -> float:
    """WCAG 2.x contrast ratio (1..21). Text >= 4.5, large text/graphics >= 3."""
    l1, l2 = sorted([luminance(c1), luminance(c2)], reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def ensure_contrast(c, bg="#FFFFFF", ratio=3.0) -> str:
    """Darken (light bg) or lighten (dark bg) `c` in OKLCH until it reaches `ratio`
    against `bg`, keeping its hue. Use for colored text labels (direct labels)."""
    if contrast_ratio(c, bg) >= ratio:
        return to_hex(to_rgb(c))
    L, Ch, h = rgb_to_oklch(to_rgb(c))
    step = -0.02 if luminance(bg) > 0.4 else 0.02
    for _ in range(40):
        L = float(np.clip(L + step, 0, 1))
        out = oklch(L, Ch, h)
        if contrast_ratio(out, bg) >= ratio:
            return out
    return out


def ink_on(bg, light="#FFFFFF", dark="#1A1A1A") -> str:
    """Pick readable text color for a fill (e.g., labels inside heatmap cells)."""
    return light if contrast_ratio(light, bg) >= contrast_ratio(dark, bg) else dark


# ----------------------------------------------------------------- tints

def mix(c1, c2, t=0.5) -> str:
    """Mix two colors in OKLab (perceptually smooth). t=0 -> c1, t=1 -> c2."""
    a, b = rgb_to_oklab(to_rgb(c1)), rgb_to_oklab(to_rgb(c2))
    return to_hex(oklab_to_rgb(a + (b - a) * t))


def lighten(c, amount=0.5, bg="#FFFFFF") -> str:
    """Tint toward the background (use for CI bands, fills, de-emphasis)."""
    return mix(c, bg, amount)


def darken(c, amount=0.3) -> str:
    L, C, h = rgb_to_oklch(to_rgb(c))
    return oklch(L * (1 - amount), C, h)


def tints(c, k=5, lo=0.15, hi=0.85, bg="#FFFFFF") -> list[str]:
    """k-step tonal ramp of one hue from dark to light (OKLCH lightness ramp)."""
    L0, C0, h = rgb_to_oklch(to_rgb(c))
    Ls = np.linspace(0.30, 0.94, k)
    out = []
    for L in Ls:
        # chroma peaks near the seed lightness, fades toward white/black
        C = C0 * max(0.15, 1 - abs(L - L0) / 0.8)
        out.append(oklch(L, C, h))
    return out


def desaturate(c, amount=0.5) -> str:
    L, C, h = rgb_to_oklch(to_rgb(c))
    return oklch(L, C * (1 - amount), h)


def min_pairwise_de(colors, cvd: str | None = None) -> tuple[float, tuple[int, int]]:
    """Smallest CIEDE2000 between any two colors (optionally after CVD simulation)."""
    rgbs = [to_rgb(c) for c in colors]
    if cvd:
        rgbs = list(simulate_cvd(np.asarray(rgbs), cvd))
    best, pair = np.inf, (0, 0)
    for i in range(len(rgbs)):
        for j in range(i + 1, len(rgbs)):
            d = delta_e(rgbs[i], rgbs[j])
            if d < best:
                best, pair = d, (i, j)
    return float(best), pair
