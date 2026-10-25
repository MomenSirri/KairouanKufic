"""HEH, NUN, YA, QAF (isol/fina) - strict construction (book pp. 28, 30, 32).
Every vertex is a chosen number on the 1/8 nuqta grid; segments are straight lines or true circular arcs.
Arc bulges are fitted to the book's contour between the chosen vertices (kufi/arcfit.py).
Shared TAIL (nun, ya, qaf): arm at 45 deg from the corner K down 4 nuqta, cup bottom rounded r 1/4,
wing 2.5 across : 2 up (38.7 deg, book 40), crescent top leaving the tip at 1:4, arm = 1/7 pen."""
import os, math, importlib.util
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
def _load(n, rel):
    sp = importlib.util.spec_from_file_location(n, os.path.join(HERE, "..", rel)); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
S = _load("kufi_spec", "kufi/spec.py"); sg = _load("seen_geom", "seen/geom.py"); af = _load("arcfit", "kufi/arcfit.py")
W, H, G, CUT = S.W, S.H, S.G, S.CUT
SQ2 = math.sqrt(2)
WING_B = -0.125                                # wing-top arc, fitted to the book (p. 32: -0.13 / -0.17)
K_R = {'nun': 0.5}
C = lambda k: np.load(os.path.join(HERE, f"{k}_contour.npy"))

def fitted(k, verts, types):
    poly, rep = af.fit(C(k), verts, types)
    return poly

# ---------------- shared tail ----------------
def tail(K, prev, rk=0.25):
    """vertices from the corner K (rounded r 1/4 from the edge coming from `prev`) down the arm, round the cup,
    up the wing and back along the crescent to Vi.  Returns (vertex list, inner-arm x(y) function)."""
    V = (K[0] - 4.0, K[1] - 4.0); P = (V[0] - 2.5, V[1] + 2.0)
    inner = lambda y: y + (K[0] - K[1]) - G * SQ2
    Vi = (inner(V[1] + W * 0.8333), V[1] + W * 0.8333)
    k1, kb, k2 = sg.fillet(prev, K, V, rk)
    v1, vb, v2 = sg.fillet(K, V, P, 0.25)
    wb = WING_B
    return [(*k1, kb), (*k2, 0), (*v1, vb), (*v2, 0), (*P, wb), (*Vi, 0)], inner

def inter_inner(Lp, d, inner):      # line from Lp along d meets the inner arm line
    t = (inner(Lp[1]) - Lp[0]) / (d[0] + d[1])     # x = Lp.x + d.x t ; y = Lp.y + d.y t ; x = y + c
    # solve Lp.x + dx t = Lp.y + dy t + c  ->  t = (Lp.y + c - Lp.x) / (dx - dy)
    c = inner(0.0)
    t = (Lp[1] + c - Lp[0]) / (d[0] - d[1])
    return (Lp[0] + d[0] * t, Lp[1] + d[1] * t)

# ---------------- NUN ----------------
NT = (-1.5, 2.0)                                       # top tip; right edge 3:4 to K
NK = (0.0, 0.0)
NQ = (NT[0] - W * 0.5, NT[1] - W * math.sin(math.radians(60)))   # 60 deg pen cut, one pen wide
ND = (1.5, -2.0)
def nun_isol():
    tv, inner = tail(NK, NT, 0.5)
    I = inter_inner(NQ, ND, inner)
    return [(*NQ, 0), (*NT, 0)] + tv + [(*I, 0)]
def nun_fina():
    tv, inner = tail(NK, NT)
    I = inter_inner(NQ, ND, inner)
    xh = NT[0] + (NT[1] - H) * 1.5 / 2.0; xr = xh + 0.75
    return [(*NQ, 0), (*NT, 0), (xh, H, 0), (xr, H, 0), (xr - CUT, 0.0, 0)] + tv[1:] + [(*I, 0)] if False else \
           [(*NQ, 0), (*NT, 0), (xh, H, 0), (xr, H, 0), (xr - CUT, 0.0, 0), (NK[0] - 0.0, 0.0, 0)] + _tail_noK(NK) + [(*inter_inner(NQ, ND, _inner(NK)), 0)]

def _inner(K): return lambda y: y + (K[0] - K[1]) - G * SQ2
def _tail_noK(K):                                       # tail without the corner fillet (corner hidden by a band)
    V = (K[0] - 4.0, K[1] - 4.0); P = (V[0] - 2.5, V[1] + 2.0); inner = _inner(K)
    Vi = (inner(V[1] + W * 0.8333), V[1] + W * 0.8333)
    v1, vb, v2 = sg.fillet(K, V, P, 0.25); wb = WING_B
    return [(*v1, vb), (*v2, 0), (*P, wb), (*Vi, 0)]

# ---------------- QAF (isol / fina) ----------------
QA, QL, QK = (-1.0, 3.0), (-2.5, 1.5), (0.0, 0.0)
QD = (5.0, -6.0)                                       # lower-left edge of the head, 5:6
def qaf_isol():
    right = fitted("qaf_head", [QA, (0.0, 0.25)], ["A", "L"])[0][2]     # right edge: slight convex arc A -> K
    tv, inner = tail(QK, (0.0, 0.25))
    I = inter_inner(QL, QD, inner)
    return [(*QL, 0), (*QA, right), (0.0, 0.25, 0)] + tv + [(*I, 0)]
def qaf_fina():
    xh = 0.0 - 0.0; right = fitted("qaf_head", [QA, (0.0, 0.25)], ["A", "L"])[0][2]
    I = inter_inner(QL, QD, _inner(QK))
    return [(*QL, 0), (*QA, right), (0.0, 0.25, 0), (0.0, H, 0), (0.75, H, 0), (0.75 - CUT, 0.0, 0), (0.0, 0.0, 0)] + _tail_noK(QK) + [(*I, 0)]

# ---------------- YA (isol / fina) ----------------
def ya_isol():
    K = (0.0, 0.0); B0 = (-1.875, -H)
    head = [B0, (-3.0, 0.625), (-2.125, 1.625), (-1.0, 0.625), (-0.5, 0.5), (-1.375, 0.125), (-2.375, 0.625), (-1.625, 0.0)]
    hp = fitted("ya_isol", head + [K], ["A", "A", "A", "L", "A", "A", "A", "L", "L"])[:-1]
    tv, inner = tail(K, (-1.625, 0.0))
    J = (inner(-H), -H)
    return hp + tv + [(*J, 0)]
def ya_fina():
    K = (-0.375, 0.0); B0 = (-3.125, -H)
    xr = 0.0; jb = (xr - CUT * (H - G) / H, G)
    head = [B0, (-3.875, 1.0), (-2.5, 2.125), (-1.0, H), (xr, H), jb, (-2.75, G), (-2.75, 0.0)]
    hp = fitted("ya_fina", head + [K], ["A", "A", "A", "L", "L", "L", "L", "L", "L"])[:-1]
    inner = _inner(K)
    return hp + [(*K, 0)] + _tail_noK(K) + [(inner(-H), -H, 0)]

# ---------------- HEH ----------------
def heh_isol():
    v = [(-0.875, 2.5), (0.0, 0.5), (-0.375, 0.0), (-1.625, 0.0), (-2.375, 0.875), (-1.875, 1.625)]
    return fitted("heh_isol", v, ["L", "A", "L", "A", "A", "A"])
def heh_init():
    xl = -2.5 - 1.0
    v = [(xl - CUT, 0.0), (xl, H), (-2.5, H), (-2.5, 1.375), (-1.0, 2.375), (0.0, 0.75), (-0.375, 0.0)]
    return fitted("heh_init", v, ["L", "L", "A", "A", "L", "A", "L"])
def heh_medi():
    xl = -2.5 - 1.0; W1, WB, W0 = (0.125, 0.0), (-0.25, -0.375), (-0.625, 0.0); xr = W1[0] + CUT
    v = [(xl - CUT, 0.0), (xl, H), (-2.5, H), (-2.5, 1.375), (-1.125, 2.375), (-0.125, H), (xr, H), W1, WB, W0]
    return fitted("heh_medi", v, ["L", "L", "A", "A", "A", "L", "L", "L", "L", "L"])
def heh_fina():
    W1, WB, W0 = (-0.25, 0.0), (-0.75, -0.5), (-1.25, 0.0); xr = W1[0] + CUT
    v = [W0, (-2.375, 0.0), (-3.25, 0.75), (-3.125, 1.375), (-1.875, 2.5), (-0.875, H), (xr, H), W1, WB]
    return fitted("heh_fina", v, ["L", "A", "A", "A", "A", "L", "L", "L", "L"])

sample = sg.sample
