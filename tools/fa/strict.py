"""FA (and the shared FA/QAF initial + medial) - strict construction from book p. 24.
Only straight lines and true arcs (fillets). Nuqta units, baseline 0, x = 0 on the book's right reference line.

 MEDI  head: apex A(-1, 3.5), left L(-2.5, 1.75), right R(0, 1.75) rounded r 1/4, notch N(-1, 0.875)   (book 1.75 + 1.75)
             lower-left edge L -> W0(-1.125, 0)  and  notch edge from N are parallel (slope 11:14)
             wedge W0 -> (-0.625, -0.5) -> (-0.125, 0), both sides 45 deg
 INIT  head: rotated: L(-2.5, 1.875), T(-1, 2.875) r 0.1, R(0, 1.5) r 1/4, N(-0.9, 0.75)
             lower-left edge L -> W0(-1.25, 0) and notch edge parallel (2:3); right side of the wedge on the same slope
 ISOL  head: triangle A(-1, 3), L(-2.5, 1.5); right edge A -> C(1/4, 0) (5:12) rounded r 1/2 into the baseline;
             lower-left edge L -> (-1.25, H).  Body: band top from x = -4.5 (book: 5 long, may stretch).
 Bands: spec H, 60 deg cuts.
"""
import os, math, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
def _load(n, rel):
    sp = importlib.util.spec_from_file_location(n, os.path.join(HERE, "..", rel)); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
S = _load("kufi_spec", "kufi/spec.py"); sg = _load("seen_geom", "seen/geom.py")
H, CUT = S.H, S.CUT
JOIN_L = 1.0                                   # left join length beyond the head (all letters)

def at_y(p, q, y):                             # x on line p-q at height y
    return p[0] + (y - p[1]) * (q[0] - p[0]) / (q[1] - p[1])

def fil(a, v, b, r):
    t1, bl, t2 = sg.fillet(a, v, b, r); return [(*t1, bl), (*t2, 0)]

# ---------------- MEDI ----------------
MA, ML, MR, MN = (-1.0, 3.5), (-2.5, 1.75), (0.0, 1.75), (-1.0, 0.875)
MW0, MWB, MW1 = (-1.125, 0.0), (-0.625, -0.5), (-0.125, 0.0)
def fa_medi():
    k = (MW0[0] - ML[0]) / (ML[1] - MW0[1])            # 11/14 : dx per unit drop
    xll = at_y(ML, MW0, H)                              # head's lower-left edge at band top
    xn = MN[0] + (MN[1] - H) * k                        # notch edge at band top (parallel)
    xl = xll - JOIN_L; xr = MW1[0] + CUT                # right band end sits on the wedge's right foot
    return ([(xl - CUT, 0.0, 0), (xl, H, 0), (xll, H, 0), (*ML, 0), (*MA, 0)] + fil(MA, MR, MN, 0.25) +
            [(*MN, 0), (xn, H, 0), (xr, H, 0), (*MW1, 0), (*MWB, 0), (*MW0, 0)])

# ---------------- INIT ----------------
IL, IT, IR, IN = (-2.5, 1.875), (-1.0, 2.875), (0.0, 1.5), (-0.9, 0.75)
IW0 = (-1.25, 0.0)
def fa_init():
    k = (IW0[0] - IL[0]) / (IL[1] - IW0[1])            # 2/3
    xll = at_y(IL, IW0, H); xn = IN[0] + (IN[1] - H) * k
    xr = 0.0
    B = (xr - (H + 0.5) * k, -0.5)                      # wedge bottom: right side keeps the same slope
    W0 = (B[0] - 0.5, 0.0)                              # left side 45 deg
    xl = xll - JOIN_L
    return ([(xl - CUT, 0.0, 0), (xl, H, 0), (xll, H, 0), (*IL, 0)] + fil(IL, IT, IR, 0.1) + fil(IT, IR, IN, 0.25) +
            [(*IN, 0), (xn, H, 0), (xr, H, 0), (*B, 0), (*W0, 0)])

# ---------------- ISOL / FINA ----------------
SA, SL, SC = (-1.0, 3.0), (-2.5, 1.5), (0.25, 0.0)
BODY_L = -4.5
def _isol_left():
    return [(BODY_L - CUT, 0.0, 0), (BODY_L, H, 0), (-1.25, H, 0), (*SL, 0), (*SA, 0)]
def fa_isol():
    return _isol_left() + fil(SA, SC, (BODY_L, 0.0), 0.5)
def fa_fina():
    xh = at_y(SA, SC, H); xr = xh + 0.75
    return _isol_left() + [(xh, H, 0), (xr, H, 0), (xr - CUT, 0.0, 0)]

sample = sg.sample
