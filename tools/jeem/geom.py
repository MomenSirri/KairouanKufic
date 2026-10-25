"""JEEM/HAH/KHAH (book p. 14) and DAL/THAL (p. 16). Nuqta units, baseline 0.
HAH: traced from the book (head + crescent), bands replaced by exact spec bands.
DAL: straight pen geometry on the spec."""
import os, math, importlib.util
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
from shapely import affinity
HERE = os.path.dirname(os.path.abspath(__file__))
def _load(n, rel):
    sp = importlib.util.spec_from_file_location(n, os.path.join(HERE, "..", rel)); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
tk = _load("tracekit", "kufi/tracekit.py")
sg = _load("seen_geom", "seen/geom.py")
S = tk.S; W, H, G, CUT = S.W, S.H, S.G, S.CUT

# ---------------- HAH ----------------
PU, PY0 = 68.0, 318.0                     # page 14 calibration (baseline row 318, 68 px per nuqta)
_c = {}
def _src():
    if not _c:
        _c["isol"] = tk.shift_to_right_edge(tk.trace(tk.mask("p_14", 790, 1080, 170, 600), 0, PY0, PU))
        _c["init"] = tk.shift_to_right_edge(tk.trace(tk.mask("p_14", 225, 540, 170, 425), 0, PY0, PU))
    return _c

def _head_right_at_H(g):   # x of the head's right edge at band height
    return g.intersection(box(-80, H - 0.02, 80, H + 0.02)).bounds[2]

def hah_isol():
    return tk.clean(_src()["isol"])

def _hx0(g):   # head stroke's left edge just above the band
    return g.intersection(box(-80, H + 0.08, 80, H + 0.3)).bounds[0]
def _head():
    g = _src()["init"]; hx0 = _hx0(g)
    return tk.clean(unary_union([g.intersection(box(-80, H + 0.08, 80, 80)), g.intersection(tk.BELOW()),
                                 g.intersection(box(hx0 - 0.02, 0, 80, H + 0.08))]))

def hah_init():
    head = _head()
    hx0 = _hx0(head)
    return tk.clean(unary_union([head, tk.band(hx0 - 1.0, hx0 + 0.6)]))

def hah_medi():
    head = _head(); xr = _head_right_at_H(head)
    hx0 = _hx0(head)
    return tk.clean(unary_union([head, tk.band(hx0 - 1.0, hx0 + 0.6), tk.band(xr - 0.6, xr + 0.75)]))

def hah_fina():
    g = _src()["isol"]; xr = _head_right_at_H(g)
    return tk.clean(unary_union([g, tk.band(xr - 0.6, xr + 0.75)]))

# ---------------- DAL ----------------
TAN60 = math.tan(math.radians(60))
T = (-2.0, 2.5)                                    # top tip (height 2.5, table p. 51)
Q = (T[0] - W * 0.5, T[1] - W * math.sin(math.radians(60)))   # 60 deg pen cut, one pen wide
D = (2.0, -(T[1] - H))                             # right edge: tip -> nose (0, H)
def _lx(y): return Q[0] + (y - Q[1]) / TAN60       # left edge, 60 deg, through Q
YS = H - G / 2                                     # slot ends on this horizontal line
def _slot_pts():
    n = (-D[1], D[0]); ln = math.hypot(*n); n = (n[0] / ln, n[1] / ln)   # normal pointing up-right
    # upper slot edge: through Q along D; lower edge: offset by G towards the inside (down-left)
    du = (D[0] / math.hypot(*D), D[1] / math.hypot(*D))
    q2 = (Q[0] - n[0] * G, Q[1] - n[1] * G)
    xu = Q[0] + (YS - Q[1]) * du[0] / du[1]
    xl = q2[0] + (YS - q2[1]) * du[0] / du[1]
    # lower edge meets the left edge
    t = sg.inter(q2, du, Q, (1 / TAN60, 1))
    return (xu, YS), (xl, YS), t

def _dal_body():
    up, lo, L1 = _slot_pts()
    return [(_lx(0), 0.0, 0), (*L1, 0), (*lo, 0), (*up, 0), (*Q, 0), (*T, 0)]

def dal_isol():
    return _dal_body() + [(0.0, H, 0), (-CUT, 0.0, 0)]

DX_FINA = -0.9                                    # fina: body moves 0.9 left, band + 1/2 dip below the line
def dal_fina():
    b = [(x + DX_FINA, y, bl) for x, y, bl in _dal_body()]
    return b + [(DX_FINA, H, 0), (0.0, H, 0), (-CUT, 0.0, 0), (-0.8, -0.5, 0), (-1.25, 0.0, 0)]

to_poly = tk.to_poly
sample = sg.sample
