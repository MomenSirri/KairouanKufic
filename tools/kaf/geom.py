"""Kufic KAF (book page labelled كاف). Module units, baseline 0, x=0 = left reference line.
One clockwise contour; the slot is open to the left (a notch, not a hole). vertex = (x, y, bulge)."""
import os, math, importlib.util
_spec = importlib.util.spec_from_file_location("seen_geom", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "seen", "geom.py"))
sg = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(sg)

PEN = sg.PEN                                   # 3/4
BODY = 2 * PEN + sg.SLOT                       # same as the Sad
K = 5 / 6                                      # left edge: dx/dy = 5:6 (50.2 deg), passes (0,1) and (2.5,4)
def L(y): return K * (y - 1.0)
HW = (sg.S.W / 4) / math.sin(math.atan2(6, 5)) # stem = 1/4 pen thick
def R(y): return L(y) + HW
NECK_L, NECK_R = 2.5, 3.0                      # vertical neck, 1/2 wide
NECK_Y = 4.0                                   # left edge turns vertical at (2.5, 4)
CUT = (NECK_L, 5.0)                            # 45 deg tip cut
TIP = (NECK_R, 5.5)
YR = 1.0 + (NECK_R - HW) / K                   # right neck edge meets the stem's right edge
XN = 4.75                                      # body right corner (same as the Sad)
T = sg.SLOT                                    # slot 1/7 pen
Y0, Y1 = PEN, PEN + T
SLOT_R = XN - 0.5

CUT_K = 2 / 3                                  # Sad connector cut: 1/2 across per 3/4 up
CONN_BL = (-1.5, 0.0)                          # left join point on the baseline
CONN_TL = (CONN_BL[0] + sg.CUT, Y0)            # lower bar continues left, 60deg pen cut

def _left_wedge(): return [(L(0), 0.0, 0), (L(Y0), Y0, 0)]
def _left_conn():  return [(*CONN_BL, 0), (*CONN_TL, 0)]
def _rest():
    return [(SLOT_R - T, Y0, 0), (SLOT_R, Y1, 0), (L(Y1), Y1, 0),
            (NECK_L, NECK_Y, 0), (*CUT, 0), (*TIP, 0), (NECK_R, YR, 0), (R(BODY), BODY, 0), (XN, BODY, 0)]
def _nose():   return [(XN + 0.5, BODY / 2, 0), (XN, 0.0, 0)]
def _conn_r():
    xp = XN + 0.5 * (BODY - PEN) / (BODY / 2)
    return [(xp, PEN, 0), (XN + 1.25, PEN, 0), (XN + 1.25 - sg.CUT, 0.0, 0)]   # = Sad

def kaf_isol(): return _left_wedge() + _rest() + _nose()
def kaf_init(): return _left_conn() + _rest() + _nose()
def kaf_medi(): return _left_conn() + _rest() + _conn_r()
def kaf_fina(): return _left_wedge() + _rest() + _conn_r()
sample = sg.sample
