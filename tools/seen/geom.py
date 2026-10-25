"""Kufic SEEN, 4 forms, module units, baseline y=0, x=0 = left reference line of the book sketch.
Every polygon is clockwise; vertex = (x, y, bulge of the segment that starts there)."""
import math
import os as _os, importlib.util as _ilu
_sp = _ilu.spec_from_file_location("kufi_spec", _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "kufi", "spec.py"))
S = _ilu.module_from_spec(_sp); _sp.loader.exec_module(S)
PEN = S.H             # band / connector height = horizontal stroke (6/7 pen)
SLOT = S.G            # slot = 1/7 pen
ARM = S.G             # thin arm of the cup = 1/7 pen
CUT = S.CUT           # 60deg pen cut
TOP = 2.5             # top line

# ---------- helpers ----------
def sub(a, b): return (a[0] - b[0], a[1] - b[1])
def add(a, b): return (a[0] + b[0], a[1] + b[1])
def mul(a, k): return (a[0] * k, a[1] * k)
def norm(a):
    l = math.hypot(*a); return (a[0] / l, a[1] / l)
def cross(a, b): return a[0] * b[1] - a[1] * b[0]

def line_x(p, d, y):           # x where line (p, dir d) reaches height y
    return p[0] + (y - p[1]) * d[0] / d[1]

def inter(p, d, q, e):         # intersection of two lines
    t = cross(sub(q, p), e) / cross(d, e)
    return add(p, mul(d, t))

class Arc:
    """circle arc from p0 to p1 with given start tangent t."""
    def __init__(self, p0, p1, t):
        t = norm(t); n = (-t[1], t[0])                       # left normal
        ch = sub(p1, p0)
        k = (ch[0] ** 2 + ch[1] ** 2) / (2 * (ch[0] * n[0] + ch[1] * n[1]))
        self.c = add(p0, mul(n, k)); self.r = abs(k)
        self.ccw = k > 0
        self.p0, self.p1 = p0, p1
    def ang(self, p): return math.atan2(p[1] - self.c[1], p[0] - self.c[0])
    def bulge(self, a, b):                                      # sub-arc a->b
        th = self.ang(b) - self.ang(a)
        if self.ccw:
            while th <= 0: th += 2 * math.pi
        else:
            while th >= 0: th -= 2 * math.pi
        return math.tan(th / 4)
    def hit(self, p, d):                                        # line ∩ circle, point closest to arc
        d = norm(d); f = sub(p, self.c)
        b = f[0] * d[0] + f[1] * d[1]; cc = f[0] ** 2 + f[1] ** 2 - self.r ** 2
        s = math.sqrt(b * b - cc)
        cands = [add(p, mul(d, -b + s)), add(p, mul(d, -b - s))]
        mid = ((self.p0[0] + self.p1[0]) / 2, (self.p0[1] + self.p1[1]) / 2)
        return min(cands, key=lambda q: math.dist(q, mid))

def fillet(a, v, b, r):
    """round corner v between a->v and v->b. returns (t1, bulge, t2)."""
    u1 = norm(sub(a, v)); u2 = norm(sub(b, v))
    phi = math.acos(max(-1, min(1, u1[0] * u2[0] + u1[1] * u2[1])))
    d = r / math.tan(phi / 2)
    t1, t2 = add(v, mul(u1, d)), add(v, mul(u2, d))
    turn = cross(sub(v, a), sub(b, v))                          # >0 left turn
    bl = math.tan((math.pi - phi) / 4)
    return t1, (bl if turn > 0 else -bl), t2

# ---------- shared parts ----------
def cup(M):
    """the cup (كأس): from baseline point M down the thin arm, round bottom, crescent wing.
    returns (outer path from M to Vi incl. bulges, inner-arm line (point, dir))."""
    V = (M[0] - 4.0, -4.5)               # 4 across, 4.5 down
    P = (V[0] - 2.5, V[1] + 2.0)         # 2.5 across, 2 up
    d_arm = norm(sub(M, V))              # 4 : 4.5
    nrm = (-d_arm[1], d_arm[0])          # upper-left normal
    Ip = add(V, mul(nrm, ARM))           # inner arm line passes here
    Vi = (line_x(Ip, d_arm, V[1] + S.W * 0.8333), V[1] + S.W * 0.8333)   # cup bottom = one pen
    t1, bv, t2 = fillet(M, V, P, 0.25)
    wing = Arc(P, Vi, (4, -1))           # wing top: leaves the tip at slope 1:4
    path = [(*M, 0), (*t1, bv), (*t2, 0), (*P, wing.bulge(P, Vi))]
    return path, Vi, (Ip, d_arm), dict(V=V, P=P, Vi=Vi)

# ---------- body A: isol / init (curved top, upright teeth 1:5) ----------
C0 = (0.0, 2.0)
PK = (2.5, 2.5)
RE = (3.0, 0.5)
D15 = (1.0, -5.0)                        # lean 1:5 (going down)
def body_A(pkx=2.5, slots=(1.0, 2.0)):
    PK = (pkx, TOP); RE = (pkx + 0.5, 0.5)
    top = Arc(C0, PK, (1, 0))
    up = (-D15[0], -D15[1])
    pts = [(*C0, None)]
    for x in slots:
        a0 = (x, PEN); a1 = (x + SLOT, PEN)
        pl = top.hit(a0, up); pr = top.hit(a1, up)
        pts += [(*pl, 0), (*a0, 0), (*a1, 0), (*pr, None)]
    pts += [(*PK, 0)]
    # fill top-arc bulges
    out = []
    for i, (x, y, b) in enumerate(pts):
        if b is None:
            nx = pts[i + 1]; out.append((x, y, top.bulge((x, y), (nx[0], nx[1]))))
        else: out.append((x, y, b))
    Q = (line_x(PK, sub(RE, PK), 0.0), 0.0)                 # right edge meets baseline
    t1, bq, t2 = fillet(PK, Q, (-1, 0), 0.5)
    out += [(*t1, bq), (*t2, 0)]
    return out, top

NARROW = dict(pkx=2.0, slots=(0.875, 1.75))
def seen_init(**kw):
    body, top = body_A(**kw)
    Lb = (line_x(C0, D15, PEN), PEN)
    return [(-0.25 - CUT, 0.0, 0), (-0.25, PEN, 0), (*Lb, 0)] + body

def seen_isol(**kw):
    body, top = body_A(**kw)
    M = (1.25, 0.0)
    path, Vi, (Ip, d), info = cup(M)
    X = inter(Ip, d, C0, D15)                               # inner arm meets body left edge
    return body + path + [(*Vi, 0), (*X, 0)], info, M

# ---------- body B: medi / fina (leaning teeth 7:5, stem, beak) ----------
L = (0.0, 1.0)
P3 = (1.75, 2.5)
D75 = (1.25, -1.75)                      # tooth lean, 54.46 deg
XR = 3.5                                 # stem right edge
def body_B():
    top = Arc(L, P3, (2, 1))
    up = (-D75[0], -D75[1])
    pts = [(*L, None)]
    for x in (1.0, 2.0):
        a0 = (x, PEN); a1 = (x + SLOT, PEN)
        pl = top.hit(a0, up); pr = top.hit(a1, up)
        pts += [(*pl, 0), (*a0, 0), (*a1, 0), (*pr, None)]
    pts += [(*P3, 0)]
    out = []
    for i, (x, y, b) in enumerate(pts):
        if b is None:
            nx = pts[i + 1]; out.append((x, y, top.bulge((x, y), (nx[0], nx[1]))))
        else: out.append((x, y, b))
    out += [(3.0, PEN, 0), (3.0, TOP, 0), (XR, 3.0, 0), (XR, 0.0, 0), (XR - 0.5, -0.5, 0), (XR - 1.0, 0.0, 0)]
    return out, top

def seen_medi():
    body, top = body_B()
    Lb = (line_x(L, D75, PEN), PEN)
    return [(-CUT, 0.0, 0), (0.0, PEN, 0), (*Lb, 0)] + body

def seen_fina():
    body, top = body_B()
    M = (1.75, 0.0)
    path, Vi, (Ip, d), info = cup(M)
    X = inter(Ip, d, L, D75)
    return body + path + [(*Vi, 0), (*X, 0)], info, M

def sample(poly, n=24):
    out = []
    for i, (x, y, b) in enumerate(poly):
        q = poly[(i + 1) % len(poly)]
        p = (x, y); qq = (q[0], q[1])
        if abs(b) < 1e-12: out.append(p); continue
        th = 4 * math.atan(b); c = math.dist(p, qq); R = c / (2 * math.sin(th / 2))
        m = ((p[0] + qq[0]) / 2, (p[1] + qq[1]) / 2)
        dx, dy = (qq[0] - p[0]) / c, (qq[1] - p[1]) / c
        h = R * math.cos(th / 2); cx, cy = m[0] - dy * h, m[1] + dx * h
        a0 = math.atan2(p[1] - cy, p[0] - cx)
        out += [(cx + abs(R) * math.cos(a0 + th * k / n), cy + abs(R) * math.sin(a0 + th * k / n)) for k in range(n)]
    return out
