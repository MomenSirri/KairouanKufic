"""MEEM (p. 12), HAH/JEEM/KHAH (p. 14), LAM-ALIF (p. 10) - strict construction.
Vertices = chosen numbers on the 1/8 nuqta grid; segments = straight lines or true arcs (bulge fitted to the book).
x = 0 at each drawing's right edge (as traced), baseline 0."""
import os, math, importlib.util
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
def _load(n, rel):
    sp = importlib.util.spec_from_file_location(n, os.path.join(HERE, "..", rel)); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
S = _load("kufi_spec", "kufi/spec.py"); sg = _load("seen_geom", "seen/geom.py"); af = _load("arcfit", "kufi/arcfit.py")
W, H, G, CUT = S.W, S.H, S.G, S.CUT
C = lambda k: np.load(os.path.join(HERE, f"{k}.npy"))
def fitted(k, verts, types): return af.fit(C(k), verts, types)[0]
JOIN_L = 1.0

# ---------------- MEEM ----------------
MI = [(-2.25, -1.5), (-2.0, -0.5), (-2.5, 1.0), (-2.0, 1.875), (-1.0, 2.5)]       # tail tip .. apex
def meem_isol():
    return fitted("meem_isol_contour", MI + [(0.0, 0.5), (-0.375, 0.0), (-1.5, 0.0)], ["A", "A", "A", "A", "A", "A", "L", "A"])
def meem_fina():
    xh = -1.0 + (2.5 - H) / 2.0; xr = 0.75
    head = fitted("meem_isol_contour", MI + [(xh, H), (xr, H), (xr - CUT, 0.0), (-1.5, 0.0)], ["A", "A", "A", "A", "L", "L", "L", "L", "A"])
    return head
MB = [(-3.125, H), (-3.25, 1.375), (-2.875, 2.0), (-1.75, 2.5), (-0.875, H)]         # bowl start .. right edge at band
def _meem_left():
    xl = MB[0][0] - JOIN_L; return [(xl - CUT, 0.0), (xl, H)]
def meem_medi():
    W1, WB, W0 = (-0.375, 0.0), (-0.875, -0.5), (-1.375, 0.0); xr = W1[0] + CUT
    v = _meem_left() + MB + [(xr, H), W1, WB, W0]
    return fitted("meem_medi_contour", v, ["L", "L", "A", "A", "A", "A", "L", "L", "L", "L", "L"])
def meem_init():                       # right edge runs straight on below the line (book p. 64, محمد)
    k = 0.6; B = (MB[-1][0] - (H + 0.5) * k, -0.5); W0 = (B[0] - 0.5, 0.0)
    v = _meem_left() + MB + [B, W0]
    return fitted("meem_medi_contour", v, ["L", "L", "A", "A", "A", "A", "L", "L", "L"])

# ---------------- HAH ----------------
D = 1.375 / 2.0                        # head stroke: dx per unit drop (11:16)
def _hah_head(T):
    Q = (T[0] - W * 0.5, T[1] - W * math.sin(math.radians(60)))
    E1 = (T[0] + T[1] * D, 0.0)
    return Q, E1, (E1[0] + 0.125, -0.75), (E1[0], -1.5)
HT = (-2.25, 2.0)
def hah_isol():
    Q, E1, E2, HK = _hah_head(HT)
    No = (Q[0] + (Q[1] - 0.5) * D, 0.5)
    v = [Q, HT, E1, E2, HK, (-1.875, 0.375), (-2.875, -1.875), (-1.5, -3.375), (0.0, -3.5), (-1.625, -4.0),
         (-3.25, -2.375), (-2.5, -0.125), No]
    return fitted("hah_isol_contour", v, ["L", "L", "A", "A", "A", "A", "A", "A", "A", "A", "A", "A", "L"])
def hah_fina():
    Q, E1, E2, HK = _hah_head(HT)
    xh = HT[0] + (HT[1] - H) * D; xb = E1[0] + CUT
    No = (Q[0] + (Q[1] - 0.5) * D, 0.5)
    v = [Q, HT, (xh, H), (xb, H), E1, E2, HK, (-1.875, 0.375), (-2.875, -1.875), (-1.5, -3.375), (0.0, -3.5),
         (-1.625, -4.0), (-3.25, -2.375), (-2.5, -0.125), No]
    return fitted("hah_isol_contour", v, ["L", "L", "L", "L", "A", "A", "A", "A", "A", "A", "A", "A", "A", "A", "L"])
IT = (-1.625, 2.0)
def _hah_init_v(right_band):
    Q, E1, E2, HK = _hah_head(IT)
    xq = Q[0] + (Q[1] - H) * D; xl = xq - JOIN_L
    top = [Q, IT]
    if right_band:
        xh = IT[0] + (IT[1] - H) * D; top += [(xh, H), (E1[0] + CUT, H)]
    v = top + [E1, E2, HK, (-0.875, 0.0), (xl - CUT, 0.0), (xl, H), (xq, H)]
    t = ["L"] * (len(top) - 1) + ["L", "A", "A", "A", "L", "L", "L", "L"]
    return v, t
def hah_init():
    v, t = _hah_init_v(False); return fitted("hah_init_contour", v, t)
def hah_medi():
    v, t = _hah_init_v(True); return fitted("hah_init_contour", v, t)

# ---------------- LAM-ALIF ----------------
def lamalif_isol():
    v = [(-2.75, 0.0), (-1.75, 0.875), (-2.25, 2.0), (-1.75, 3.25), (-2.875, 4.375), (-2.5, 5.0), (-1.375, 3.75),
         (0.0, 5.0), (0.0, 4.875), (-1.25, 3.625), (-0.75, 2.375), (-1.25, 1.125), (-0.375, 0.625), (-0.75, 0.0)]
    t = ["L", "A", "A", "A", "L", "A", "L", "L", "L", "A", "A", "L", "L", "L"]
    return fitted("lamalif_isol_contour", v, t)
def lamalif_isol_hole():
    v = [(-1.5, 1.375), (-1.25, 2.125), (-1.625, 3.125), (-1.875, 2.25)]
    return fitted("lamalif_isol_hole0", v, ["A", "A", "A", "A"])
def lamalif_fina():
    xr = 0.0
    v = [(-3.0, 0.0), (-2.375, 0.875), (-3.125, 2.625), (-2.125, 4.875), (-2.0, 4.75), (-2.625, 3.0), (-2.0, 1.375),
         (-1.625, 2.625), (-2.125, 3.875), (-1.75, 4.5), (-1.125, 2.625), (-1.875, 1.25), (-1.125, H), (xr, H), (xr - CUT, 0.0)]
    t = ["L", "A", "A", "L", "A", "A", "A", "A", "L", "A", "A", "L", "L", "L", "L"]
    return fitted("lamalif_fina_contour", v, t)

sample = sg.sample
