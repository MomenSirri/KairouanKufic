"""Kufic SAD, 4 forms. Module units, baseline y=0, x=0 = left reference line.
Outer contour clockwise, slot (counter) separate counter-clockwise. vertex = (x, y, bulge)."""
import os, importlib.util
_spec = importlib.util.spec_from_file_location("seen_geom", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "seen", "geom.py"))
sg = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(sg)   # shared cup + helpers from the seen

PEN = sg.PEN                                     # 3/4
BODY = 2 * PEN + sg.SLOT                         # two horizontal strokes + one gap
HEAD_TIP = (0.5, BODY + 0.5)                     # head rises 1/2
HEAD_R = (0.75, BODY)                            # head width 3/4
TL = (0.0, BODY)                                 # top-left of head
LEFT_DIR = (0.5, -2.0)                           # left edge 1:4 (75.96 deg, sketch 75)
LENGTH = 4.0                                     # body length after the head (can stretch)
XN = HEAD_R[0] + LENGTH                          # 4.75 nose / right start
NOSE = (XN + 0.5, BODY / 2)                      # nose tip (1/2 out, mid height)
M_CUP = (XN - 3.5, 0.0)                          # 1.25 : arm leaves the baseline 3 1/2 before the nose

def slot():
    t = sg.SLOT; y0, y1 = PEN, PEN + t
    xr = XN - 0.5
    return [(1.0, y0, 0), (xr - t, y0, 0), (xr, y1, 0), (1.0, y1, 0)]   # CCW, 45 deg right end

def _left_conn():
    lb = (sg.line_x(TL, LEFT_DIR, PEN), PEN)
    return [(-0.5 - sg.CUT, 0.0, 0), (-0.5, PEN, 0), (*lb, 0)]

def _top():
    return [(*TL, 0), (*HEAD_TIP, 0), (*HEAD_R, 0), (XN, BODY, 0)]

def _right_nose():
    return [(*NOSE, 0), (XN, 0.0, 0)]

def _right_conn():
    xp = XN + 0.5 * (BODY - PEN) / (BODY - NOSE[1])
    return [(xp, PEN, 0), (XN + 1.25, PEN, 0), (XN + 1.25 - sg.CUT, 0.0, 0)]

def _cup_tail():
    path, Vi, (Ip, d), info = sg.cup(M_CUP)
    X = sg.inter(Ip, d, TL, LEFT_DIR)
    return path + [(*Vi, 0), (*X, 0)], info

def sad_medi(): return _left_conn() + _top() + _right_conn()
def sad_init(): return _left_conn() + _top() + _right_nose()
def sad_isol():
    tail, info = _cup_tail(); return _top() + _right_nose() + tail, info
def sad_fina():
    tail, info = _cup_tail(); return _top() + _right_conn() + tail, info
sample = sg.sample
