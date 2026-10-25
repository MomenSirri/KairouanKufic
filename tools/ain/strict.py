"""AIN / GHAIN - strict construction: only straight lines and true circular arcs, every point defined by a number.
Units: nuqta, baseline y = 0.  Measured from the user's sharp scans of the book (pp. 22, 24) and snapped to the system.

  FAN head (medi, fina):  chord y = 1.5 from x = 0 to 2.5, one arc through the apex (1.25, 2.5)  -> width 2.5, rise 1
                          sides go down at 45 deg.
  HOOK head (isol, init): outer edge K(0,1.5) -> T(1,3) (slope 3:2); tip cut vertical 1/2 (T -> T2(1,2.5));
                          inner edge parallel to the outer one, then one concave arc to the band.
  TAIL (isol, fina):      crescent made of 6 tangent-continuous arcs (3 outer, 3 inner), bottom at -4, tip (3.4, -3.55).
  BANDS:                  spec band H high, 60 deg pen cuts (same as every other letter).
"""
import os, math, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
def _load(n, rel):
    sp = importlib.util.spec_from_file_location(n, os.path.join(HERE, "..", rel)); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
S = _load("kufi_spec", "kufi/spec.py"); sg = _load("seen_geom", "seen/geom.py")
H, CUT = S.H, S.CUT

def bulge(p0, p1, c, ccw):
    a0 = math.atan2(p0[1] - c[1], p0[0] - c[0]); a1 = math.atan2(p1[1] - c[1], p1[0] - c[0])
    th = a1 - a0
    if ccw:
        while th <= 0: th += 2 * math.pi
    else:
        while th >= 0: th -= 2 * math.pi
    return math.tan(th / 4)

def circle3(a, b, c):
    ax, ay = a; bx, by = b; cx, cy = c
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    ux = ((ax*ax + ay*ay) * (by - cy) + (bx*bx + by*by) * (cy - ay) + (cx*cx + cy*cy) * (ay - by)) / d
    uy = ((ax*ax + ay*ay) * (cx - bx) + (bx*bx + by*by) * (ax - cx) + (cx*cx + cy*cy) * (bx - ax)) / d
    return (ux, uy), math.hypot(ax - ux, ay - uy)

def x_on_circle(c, r, y, side):          # side -1 = left intersection, +1 = right
    return c[0] + side * math.sqrt(r * r - (y - c[1]) ** 2)

# ---------------- FAN ----------------
L, RC, APEX = (0.0, 1.5), (2.5, 1.5), (1.25, 2.5)
FAN_C, FAN_R = circle3(L, APEX, RC)                     # centre (1.25, 0.21875), r = 1.28125
B_FAN = bulge(L, RC, FAN_C, ccw=False)                  # over the top, clockwise
ML = (1.5 - H, H)                                       # left 45 deg side meets the band top
MR = (2.5 - (1.5 - H), H)                               # right 45 deg side (mouth) meets the band top

# ---------------- TAIL (fina coordinates) ----------------
N = (1.0, 0.5)                                          # neck: both 45 deg lines of the fina head meet here
LI, LM = (0.35, -1.9), (0.0, -2.5)                      # inner / outer leftmost points (vertical tangents)
C_IU = (LI[0] + 0, 0); _r = ((N[0] - LI[0]) ** 2 + (N[1] - LI[1]) ** 2) / (2 * (N[0] - LI[0]))
C_IU, R_IU = (LI[0] + _r, LI[1]), _r                    # inner upper arc: through N, vertical at LI   (r = 4.756)
C_IL, R_IL = (1.95, -1.9), 1.6                          # inner lower arc: LI -> BI
BI = (1.95, -3.5)
TP = (3.4, -3.55)                                       # tail tip
_R = ((TP[0] - BI[0]) ** 2 + (TP[1] - BI[1]) ** 2) / (2 * (BI[1] - TP[1])) if BI[1] != TP[1] else 1e6
C_IT, R_IT = (BI[0], BI[1] - abs(_R)), abs(_R)          # inner flat arc BI -> TP (horizontal at BI)
C_OL, R_OL = (1.5, -2.5), 1.5                           # outer lower arc: LM -> BO
BO = (1.5, -4.0)
_R2 = ((TP[0] - BO[0]) ** 2 + (TP[1] - BO[1]) ** 2) / (2 * (TP[1] - BO[1]))
C_OT, R_OT = (BO[0], BO[1] + _R2), _R2                  # outer flat arc BO -> TP (horizontal at BO)  (r = 4.236)
C_OU = None
def _outer_upper(xtop, ytop):                           # circle with vertical tangent at LM through (xtop, ytop)
    r = ((xtop - LM[0]) ** 2 + (ytop - LM[1]) ** 2) / (2 * (xtop - LM[0]))
    return (LM[0] + r, LM[1]), r

def _tail(dx, inner_start, outer_end):
    """inner_start / outer_end: (x, y) where the tail leaves / rejoins the head (fina coords before dx)."""
    sh = lambda p: (p[0] + dx, p[1])
    c_ou = C_OU
    seg = [(*sh(inner_start), bulge(inner_start, LI, C_IU, True)),
           (*sh(LI), bulge(LI, BI, C_IL, True)),
           (*sh(BI), bulge(BI, TP, C_IT, False)),
           (*sh(TP), bulge(TP, BO, C_OT, False)),
           (*sh(BO), bulge(BO, LM, C_OL, False)),
           (*sh(LM), bulge(LM, outer_end, c_ou, False))]
    return seg, sh(outer_end)

# outer tail edge leaves the fina head's left 45 deg side (x = 1.5 - y): solve with the circle through LM
C_OU, R_OU = _outer_upper(0.555, 0.0)                  # outer upper arc: vertical at LM, through the book point (0.555, 0)
def _solve_outer_on_left_side():                        # where that arc meets the head's left 45 deg side x = 1.5 - y
    lo, hi = 0.0, 1.5
    for _ in range(80):
        y = (lo + hi) / 2
        f = x_on_circle(C_OU, R_OU, y, -1) - (1.5 - y)
        if f > 0: hi = y
        else: lo = y
    return (1.5 - y, y)
O_TOP = _solve_outer_on_left_side()

# ---------------- HOOK ----------------
K, T, T2 = (0.0, 1.5), (1.0, 3.0), (1.0, 2.5)
K2 = (K[0] + (K[1] - H) * 0.36, H)                      # lower-left edge, steep (1 : 2.8), down to the band
C1 = (T2[0] - (T2[1] - 1.8) * 2 / 3, 1.8)               # inner edge (parallel to K-T) ends here
HOOK_C, HOOK_R = circle3(C1, (0.745, 1.12), (1.05, 0.77))   # concave arc through two more book points
C2 = (x_on_circle(HOOK_C, HOOK_R, H, -1), H)
B_HOOK = bulge(C1, C2, HOOK_C, ccw=True)

# ---------------- FORMS ----------------
def ain_medi():
    xl, xr = ML[0] - 1.0, MR[0] + 1.1
    return [(xl - CUT, 0.0, 0), (xl, H, 0), (*ML, 0), (*L, B_FAN), (*RC, 0), (*MR, 0), (xr, H, 0), (xr - CUT, 0.0, 0),
            (2.1, 0.0, 0), (1.7, -0.4, 0), (1.25, 0.05, 0), (0.8, -0.4, 0), (0.4, 0.0, 0)]

def ain_fina():
    J = 2.85
    tail, end = _tail(0.0, N, O_TOP)
    return [(*L, B_FAN), (*RC, 0), (*MR, 0), (J, H, 0), (J - CUT, 0.0, 0), (2.0, -0.5, 0)] + tail + [(*end, 0)]

def ain_init():
    J = 3.0; xl = K2[0] - 0.5
    return [(*T, 0), (*T2, 0), (*C1, B_HOOK), (*C2, 0), (J, H, 0), (J - CUT, 0.0, 0),
            (xl - CUT, 0.0, 0), (xl, H, 0), (*K2, 0), (*K, 0)]

ISOL_DX = K2[0] - x_on_circle(C_OU, R_OU, H, -1)   # tail moved so its outer edge meets K2 on the band top
def ain_isol():
    J = 2.5
    c_iu_x = C_IU[0] + ISOL_DX
    xin = c_iu_x - math.sqrt(R_IU ** 2 - (0 - C_IU[1]) ** 2)      # inner tail edge at the baseline
    p_in = (xin - ISOL_DX, 0.0)                                    # back in fina coords for _tail
    p_out = (x_on_circle(C_OU, R_OU, H, -1), H)
    tail, end = _tail(ISOL_DX, p_in, p_out)
    return [(*T, 0), (*T2, 0), (*C1, B_HOOK), (*C2, 0), (J, H, 0), (J - CUT, 0.0, 0)] + tail + [(*K2, 0), (*K, 0)]

sample = sg.sample
SPEC_TEXT = {
    "fan": "chord y=1.5, x 0..2.5, arc through (1.25,2.5): centre (1.25,0.219) r 1.281",
    "hook": f"K(0,1.5) T(1,3) T2(1,2.5) C1({C1[0]:.3f},1.8) arc centre ({HOOK_C[0]:.3f},{HOOK_C[1]:.3f}) r {HOOK_R:.3f}",
    "tail": f"outer: LM(0,-2.5) BO(1.5,-4) TP(3.4,-3.55); inner: LI(0.35,-1.9) BI(1.95,-3.5); radii {R_IU:.3f}/{R_IL}/{R_IT:.2f} - {R_OT:.3f}/{R_OL}",
}
