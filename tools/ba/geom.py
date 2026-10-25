"""BA and MEEM, Kairouan Kufic (book pp. 12-13, heights from the table p. 51). Nuqta units, baseline 0.
BA: built from straight pen strokes on the spec.  MEEM: head traced from the book (p. 12) with potrace,
then every band / connector replaced by the exact spec band (H high, 60 deg cuts) with shapely booleans."""
import os, math, importlib.util
import numpy as np, potrace
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
from shapely import affinity
HERE = os.path.dirname(os.path.abspath(__file__))
def _load(n, rel):
    sp = importlib.util.spec_from_file_location(n, os.path.join(HERE, "..", rel)); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
S = _load("kufi_spec", "kufi/spec.py")
sg = _load("seen_geom", "seen/geom.py")
W, V, H, CUT = S.W, S.V, S.H, S.CUT
C60 = (math.cos(math.radians(60)), math.sin(math.radians(60)))

# ---------------- BA ----------------
SLOPE = 1.39            # tooth edges: 1 across per 1.39 down (~54 deg), measured p. 12
def _tooth(h):
    """tooth leaning right, outer edge ends at the nose (0,H). returns T, Q, inner corner C."""
    T = (-(h - H) / SLOPE, h)
    Q = (T[0] - W * C60[0], T[1] - W * C60[1])           # 60 deg pen-cut top, one pen wide
    C = (Q[0] + (Q[1] - H) / SLOPE, H)
    return T, Q, C

def _ba(h, left, right):
    T, Q, C = _tooth(h)
    if left == "tail":   lp = [(-4.5 - CUT, 0.0, 0), (-4.5, H, 0)]           # isol/fina: long body, may stretch
    else:                lp = [(C[0] - 1.0 - CUT, 0.0, 0), (C[0] - 1.0, H, 0)]  # init/medi: left join, 1 nuqta clear of the tooth
    if right == "nose":  rp = [(0.0, H, 0), (-CUT, 0.0, 0)]
    else:                rp = [(0.0, H, 0), (0.75, H, 0), (0.75 - CUT, 0.0, 0)]  # right join
    return lp + [(*C, 0), (*Q, 0), (*T, 0)] + rp

def ba_isol(): return _ba(2.0, "tail", "nose")
def ba_fina(): return _ba(2.0, "tail", "join")
def ba_init(): return _ba(2.5, "join", "nose")
def ba_medi(): return _ba(2.5, "join", "join")
def ba_medi_after_lam():            # vertical tooth, 45 deg top (p. 12 middle: "يكتب بعد اللام")
    return [(-V - 0.75 - CUT, 0.0, 0), (-V - 0.75, H, 0), (-V, H, 0), (-V, 2.5 - V, 0), (0.0, 2.5, 0),
            (0.0, H, 0), (0.5, H, 0), (0.5 - CUT, 0.0, 0)]

# ---------------- MEEM ----------------
PX0, PY0, PU = 545.0, 542.0, 66.8          # page 12 calibration
def _trace(name):
    m = np.load(os.path.join(HERE, f"{name}_mask.npy"))
    polys = []
    for c in potrace.Bitmap(~m).trace(turdsize=20, alphamax=1.0, opticurve=True, opttolerance=0.3):
        pts = []; cur = c.start_point
        for s in c.segments:
            if s.is_corner: pts += [(cur.x, cur.y), (s.c.x, s.c.y)]
            else:
                p0, c1, c2, p3 = map(np.array, ((cur.x, cur.y), (s.c1.x, s.c1.y), (s.c2.x, s.c2.y), (s.end_point.x, s.end_point.y)))
                pts += [tuple((1-t)**3*p0 + 3*(1-t)**2*t*c1 + 3*(1-t)*t**2*c2 + t**3*p3) for t in np.linspace(0, 1, 14, endpoint=False)]
            cur = s.end_point
        polys.append(Polygon([((x - PX0) / PU, (PY0 - y) / PU) for x, y in pts]).buffer(0))
    return unary_union(polys)

def band(xl, xr):     # spec band: top from xl to xr at H, 60 deg pen cuts at both ends
    return Polygon([(xl - CUT, 0), (xr - CUT, 0), (xr, H), (xl, H)])

def _clean(g):
    g = g.buffer(0.004).buffer(-0.004).simplify(0.006)
    if g.geom_type == "MultiPolygon": g = max(g.geoms, key=lambda p: p.area)
    return g

_MR = _MM = None
def _src():
    global _MR, _MM
    if _MR is None: _MR, _MM = _trace("meem_right"), _trace("meem_mid")
    return _MR, _MM
ABOVE = lambda: box(-50, H, 50, 50)
BELOW = lambda: box(-50, -50, 50, 0)

TAIL_TIP = (4.0, -1.5)                         # book p. 12: tail ends 1/2 + 1 under the baseline
def _with_tip(g):
    low = g.intersection(box(-50, -50, 50, -1.0))
    return unary_union([g, low.union(Polygon([TAIL_TIP, TAIL_TIP, TAIL_TIP]).buffer(0.001)).convex_hull])
def meem_isol():
    mr, _ = _src()
    return _clean(_with_tip(mr))
def meem_fina():
    mr, _ = _src()
    xb = min(x for x, y in mr.intersection(box(-50, H - 0.02, 50, H + 0.02)).exterior.coords) if False else None
    head = mr.intersection(ABOVE()); tail = mr.intersection(BELOW())
    x0, _, x1, _ = mr.intersection(box(-50, 0.05, 50, H)).bounds
    return _clean(_with_tip(unary_union([head, tail, mr.intersection(box(-50, 0, 50, H)), band(x0 + 0.3, x1 + 0.75)])))
def _mid_parts():
    _, mm = _src()
    return mm.intersection(ABOVE()), mm.intersection(BELOW()), mm
def meem_medi():
    head, wedge, mm = _mid_parts()
    x0, _, x1, _ = mm.intersection(box(-50, 0.05, 50, H - 0.05)).bounds
    return _clean(unary_union([head, wedge, band(x0 + CUT * 0.5, x1)]))
def meem_init():
    head, wedge, mm = _mid_parts()
    x0, _, x1, _ = mm.intersection(box(-50, 0.05, 50, H - 0.05)).bounds
    # right side: continue the head's straight right edge down to the baseline (book p. 13, stroke 2)
    hb = head.intersection(box(-50, H, 50, H + 0.6))
    xs = sorted(hb.exterior.coords, key=lambda p: -p[0])
    p_top = max((p for p in head.exterior.coords if p[1] > H + 0.5), key=lambda p: p[0] - 0.3 * p[1])
    p_low = max((p for p in head.exterior.coords if abs(p[1] - H) < 0.05), key=lambda p: p[0])
    dx = (p_low[0] - p_top[0]) / (p_top[1] - p_low[1])
    clip = Polygon([(-50, -50), (p_low[0] + dx * (H + 50), -50), (p_top[0] - dx * (50 - p_top[1]), 50), (-50, 50)])
    return _clean(unary_union([head, wedge, band(x0 + CUT * 0.5, x1)]).intersection(clip))

def to_poly(g):       # shapely -> (outer, holes) in the (x, y, bulge) format
    outer = [(x, y, 0) for x, y in list(g.exterior.coords)[:-1]]
    holes = [[(x, y, 0) for x, y in list(i.coords)[:-1]] for i in g.interiors]
    return outer, holes
sample = sg.sample
