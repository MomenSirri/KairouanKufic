"""AIN/GHAIN, FA, QAF (book pp. 22-24, 30; ain from the user's sharper scans).
Heads traced with potrace, every band replaced by the exact spec band (H, 60 deg cuts) via tracekit.rebase.
Qaf tail = parametric cup (same family as the seen/sad cup): arm 45 deg, wing 2.5 : 2 (40 deg)."""
import os, math, importlib.util
import numpy as np
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
from shapely import affinity
HERE = os.path.dirname(os.path.abspath(__file__))
def _load(n, rel):
    sp = importlib.util.spec_from_file_location(n, os.path.join(HERE, "..", rel)); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
tk = _load("tracekit", "kufi/tracekit.py")
sg = _load("seen_geom", "seen/geom.py")
S = tk.S; W, H, G, CUT = S.W, S.H, S.G, S.CUT

CAL = {"fa_medi": (386, 651, 66.5), "fa_init": (712, 580, 66.5), "fa_isol": (1022, 651, 66.5),
       "ain_init": (818, 337, 72), "ain_medi": (490, 330, 72), "ain_fina": (150, 316, 70), "ain_isol": (710, 316, 70),
       "qaf_head": (760, 290, 67)}
_c = {}
def src(k):
    if k not in _c:
        x0, y0, u = CAL[k]
        _c[k] = tk.trace(np.load(os.path.join(HERE, f"{k}_mask.npy")), x0, y0, u)
    return _c[k]
R = lambda g: tk.shift_to_right_edge(g)

# ---------------- AIN ----------------
def _jaw_end(g):        # top-right x of the lower jaw (drawn band to the right of the hook)
    return g.intersection(box(-80, 0.25, 80, 0.35)).bounds[2] + (H - 0.3) * CUT / H
def _hook_band(g, left):  # hook (kept as drawn) + one spec band from the left end to the jaw end
    d = max(0.06, tk.band_top(g) - H + 0.04); hl = tk.head_left_above(g, d)
    keep = [g.intersection(box(-80, H + d, 80, 80)), g.intersection(box(-80, -80, 80, 0)),
            g.intersection(box(hl - 0.6, 0, hl + 0.4, H + d))]
    return tk.clean(unary_union(keep + [tk.band(hl - left, _jaw_end(g))]))
def ain_isol(): return R(_hook_band(src("ain_isol"), 0.0))
def ain_fina(): return R(tk.rebase(src("ain_fina"), right=0.75))
def ain_init(): return R(_hook_band(src("ain_init"), 1.0))
def ain_medi(): return R(tk.rebase(src("ain_medi"), left=1.0, right=0.75))

# ---------------- FA ----------------
def fa_init(): return R(tk.rebase(src("fa_init"), left=1.0))
def fa_medi(): return R(tk.rebase(src("fa_medi"), left=1.0, right=0.75))
def _solid(k):   # drop watermark specks inside/along the drawing (closing r=0.12, mitred so corners stay sharp)
    return Polygon(src(k).exterior).buffer(0.12, join_style=2).buffer(-0.12, join_style=2)
def fa_isol():
    g = _solid("fa_isol"); hl = tk.head_left_above(g, 0.06)
    return R(tk.rebase(g, left=hl + 4.5))                 # body 5 long (book), may stretch
def fa_fina():
    g = _solid("fa_isol"); hl = tk.head_left_above(g, 0.06)
    return R(tk.rebase(g, left=hl + 4.5, right=0.75))

# ---------------- QAF ----------------
def cup(M, depth=4.0, wing=(2.5, 2.0), arm=G):
    """arm from baseline point M down-left at 45 deg to the bottom V, rounded r=1/4, wing up-left, crescent top."""
    V = (M[0] - depth, -depth)
    P = (V[0] - wing[0], V[1] + wing[1])
    d = sg.norm(sg.sub(M, V)); n = (-d[1], d[0])
    Ip = sg.add(V, sg.mul(n, arm * math.sqrt(2) / math.sqrt(2)))
    Vi = (sg.line_x(Ip, d, V[1] + W * 0.8333), V[1] + W * 0.8333)
    t1, bv, t2 = sg.fillet(M, V, P, 0.25)
    wingarc = sg.Arc(P, Vi, (4, -1))
    X = (sg.line_x(Ip, d, 0.3), 0.3)
    pts = [(*M, 0), (*t1, bv), (*t2, 0), (*P, wingarc.bulge(P, Vi)), (*Vi, 0), (*X, 0), (M[0], 0.3, 0)]
    return Polygon([(x, y) for x, y in sg.sample(pts, 16)]).buffer(0)

def _qaf_head():
    g = src("qaf_head")
    return g.intersection(box(-80, -0.75, 80, 80))
def qaf_isol():
    head = _qaf_head()
    lo = head.intersection(box(-80, -0.75, 80, -0.55)).bounds     # where the drawn arm leaves the head
    M = ((lo[0] + lo[2]) / 2 + 0.75, 0.0)                         # follow that arm back up to the baseline (45 deg)
    return R(tk.clean(unary_union([head, cup(M)])))
def qaf_fina():
    g = qaf_isol(); hr = tk.head_right_above(g, 0.05)
    return R(tk.clean(unary_union([g, tk.band(hr - 0.8, hr + 0.75)])))
qaf_init, qaf_medi = fa_init, fa_medi

to_poly = tk.to_poly
sample = sg.sample
