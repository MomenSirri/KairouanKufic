"""ALIF and LAM, Kairouan Kufic (book pp. 6-9). Nuqta units, baseline 0, right edge of the stem at x=0.
vertex = (x, y, bulge of the segment that starts there)."""
import os, importlib.util
def _load(n, rel):
    sp = importlib.util.spec_from_file_location(n, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", rel))
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
S = _load("kufi_spec", "kufi/spec.py")
sg = _load("seen_geom", "seen/geom.py")          # Arc helper + sampler

V, H, CUT = S.V, S.H, S.CUT
TOP = S.ALIF                                     # 5 nuqta
R_FILLET = 0.5                                   # book: 1/2 x 1/2 fillet stem -> band
JOIN_R = 1.5                                     # band reaches 1.5 nuqta right of the stem (top edge)
JOIN_L = 0.5                                     # left join: band top starts 1/2 left of the stem (as Sad)
DROP = 1.0                                       # lam isol/fina: stem goes 1 nuqta under the baseline
FOOT = 2.0                                       # lam foot length, measured from the stem's right edge

def arc_b(p0, p1, t):  # bulge of the arc p0->p1 leaving p0 along tangent t
    a = sg.Arc(p0, p1, t); return a.bulge(p0, p1)

def _head():  # stem top with the 45 deg pen cut (left edge lower by V)
    return [(-V, TOP - V, 0), (0.0, TOP, 0)]

def _right_join():  # fillet r=1/2 from stem to band, band top to 1.5, 60 deg cut
    a, b = (0.0, H + R_FILLET), (R_FILLET, H)
    return [(*a, arc_b(a, b, (0, -1))), (*b, 0), (JOIN_R, H, 0), (JOIN_R - CUT, 0.0, 0)]

def _left_join_tail():  # from baseline under the stem, out to the left cut, back to the stem
    return [(-V - JOIN_L - CUT, 0.0, 0), (-V - JOIN_L, H, 0), (-V, H, 0)]

def _foot():  # stem down to -1, foot band H high to the left, 60 deg cut, small fillets
    yb = -DROP - H
    c1, c2 = (0.0, yb + 0.25), (-0.25, yb)
    i1, i2 = (-V - 0.25, -DROP), (-V, -DROP + 0.25)
    return [(*c1, arc_b(c1, c2, (0, -1))), (*c2, 0), (-FOOT, yb, 0), (-FOOT + CUT, -DROP, 0),
            (*i1, arc_b(i1, i2, (1, 0))), (*i2, 0)]

def alif_isol():
    a, tip = (0.0, 1.25), (1.0, 0.4)
    b0 = (-V + 0.25, 0.0); c = (-V, 0.25)
    b_tip = -arc_b(b0, tip, (1, 0))              # bottom curve, horizontal at the baseline
    return _head() + [(*a, arc_b(a, tip, (0, -1))), (*tip, b_tip), (*b0, arc_b(b0, c, (-1, 0))), (*c, 0)]

def alif_fina():
    return _head() + _right_join() + [(-V, 0.0, 0)]

def lam_isol():
    return _head() + _foot()

def lam_init():
    return _head() + [(0.0, 0.0, 0)] + _left_join_tail()

def lam_medi():
    return _head() + _right_join() + _left_join_tail()

def lam_fina():
    rj = _right_join()
    return _head() + rj + [(0.0, 0.0, 0)] + _foot()

sample = sg.sample
