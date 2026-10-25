"""Shared tools: trace a yellow letter from a book page, convert to nuqta units, merge with exact spec bands."""
import os, math, importlib.util
import numpy as np, potrace
from PIL import Image
from scipy import ndimage as ndi
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
HERE = os.path.dirname(os.path.abspath(__file__))
_sp = importlib.util.spec_from_file_location("kufi_spec", os.path.join(HERE, "spec.py")); S = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(S)
H, CUT = S.H, S.CUT
PAGES = os.path.join(HERE, "..", "video", "pages")

def mask(page, x0, x1, y0, y1, fill_small=400, loose=False):
    path = page if page.endswith(".png") else os.path.join(PAGES, page + ".png")
    im = np.array(Image.open(path).convert("RGB")).astype(int)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    yel = (r > 170) & (g > 130) & (b < 130) & (r - b > 60)
    if loose: yel = (r > 110) & (g > 90) & (b < 110) & (r - b > 40) & ~((r > 140) & (g < 110))
    ink = im.max(2) < 120
    Y = np.zeros_like(yel); Y[y0:y1, x0:x1] = yel[y0:y1, x0:x1]
    m = Y | (ink & ndi.binary_dilation(Y, iterations=3))
    win = np.zeros_like(m); win[y0:y1, x0:x1] = True; m &= win
    m = ndi.binary_closing(m, iterations=1)
    lab, n = ndi.label(m); k = np.bincount(lab.ravel())[1:].argmax() + 1; m = lab == k
    holes = ndi.binary_fill_holes(m) & ~m; hl, hn = ndi.label(holes)
    for i in range(1, hn + 1):
        if (hl == i).sum() < fill_small: m |= hl == i
    return m

def trace(m, px0, py0, pu):
    polys = []
    for c in potrace.Bitmap(~m).trace(turdsize=20, alphamax=1.0, opticurve=True, opttolerance=0.3):
        pts = []; cur = c.start_point
        for s in c.segments:
            if s.is_corner: pts += [(cur.x, cur.y), (s.c.x, s.c.y)]
            else:
                p0, c1, c2, p3 = map(np.array, ((cur.x, cur.y), (s.c1.x, s.c1.y), (s.c2.x, s.c2.y), (s.end_point.x, s.end_point.y)))
                pts += [tuple((1-t)**3*p0 + 3*(1-t)**2*t*c1 + 3*(1-t)*t**2*c2 + t**3*p3) for t in np.linspace(0, 1, 14, endpoint=False)]
            cur = s.end_point
        polys.append(Polygon([((x - px0) / pu, (py0 - y) / pu) for x, y in pts]).buffer(0))
    polys.sort(key=lambda p: -p.area)
    g = polys[0]
    for p in polys[1:]:
        g = g.difference(p) if g.contains(p) else g.union(p)
    return g

def band(xl, xr):            # spec band: top xl..xr at H, 60 deg pen cuts
    return Polygon([(xl - CUT, 0), (xr - CUT, 0), (xr, H), (xl, H)])
ABOVE = lambda: box(-80, H, 80, 80)
BELOW = lambda: box(-80, -80, 80, 0)
STRIP = lambda: box(-80, 0, 80, H)

def clean(g):
    g = g.buffer(0.004).buffer(-0.004).simplify(0.006)
    if g.geom_type == "MultiPolygon": g = max(g.geoms, key=lambda p: p.area)
    return g

def shift_to_right_edge(g):
    from shapely import affinity
    return affinity.translate(g, -g.bounds[2], 0)

def head_left_above(g, d=0.08):
    d = max(d, 0.0)    # x of the head's left edge just above the band
    return g.intersection(box(-80, H + d, 80, H + 0.3)).bounds[0]
def head_right_above(g, d=0.08):
    return g.intersection(box(-80, H + d, 80, H + 0.3)).bounds[2]
def band_top(g, y0=0.3):
    from shapely.geometry import LineString
    w = lambda y: g.intersection(LineString([(-80, y), (80, y)])).length
    w0 = w(y0); y = y0
    while y < 1.5:
        if w(y) < 0.6 * w0: return y
        y += 0.01
    return H
def rebase(g, left=None, right=None, d=None):
    if d is None: d = max(0.06, band_top(g) - H + 0.04)
    """replace the drawn bands with spec bands. left/right = band length beyond the head (None = no band there)."""
    hl, hr = head_left_above(g, d), head_right_above(g, d)
    keep = unary_union([g.intersection(box(-80, H + d, 80, 80)), g.intersection(box(-80, -80, 80, 0)),
                        g.intersection(box(hl - 0.02 if left is not None else -80, 0,
                                           hr + 0.02 if right is not None else 80, H + d))])
    parts = [keep]
    if left is not None: parts.append(band(hl - left, hl + 0.6))
    if right is not None: parts.append(band(hr - 0.6, hr + right))
    return clean(unary_union(parts))

def to_poly(g):
    outer = [(x, y, 0) for x, y in list(g.exterior.coords)[:-1]]
    holes = [[(x, y, 0) for x, y in list(i.coords)[:-1]] for i in g.interiors]
    return outer, holes
