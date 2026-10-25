"""Strict fitting: the designer gives the vertices (snapped numbers) and the type of each segment ('L' line, 'A' arc);
each arc's bulge is fitted to the book contour between its two vertices (1 parameter, true circular arc).
Result = (x, y, bulge) polyline: only lines and arcs, every vertex a chosen number."""
import math, numpy as np
from scipy.optimize import minimize_scalar

def arc_points(p, q, b, n=40):
    if abs(b) < 1e-9: return np.array([p, q])
    th = 4 * math.atan(b); c = math.dist(p, q); R = c / (2 * math.sin(th / 2))
    mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
    dx, dy = (q[0] - p[0]) / c, (q[1] - p[1]) / c
    h = R * math.cos(th / 2); cx, cy = mx - dy * h, my + dx * h
    a0 = math.atan2(p[1] - cy, p[0] - cx)
    return np.array([(cx + abs(R) * math.cos(a0 + th * k / n), cy + abs(R) * math.sin(a0 + th * k / n)) for k in range(n + 1)])

def seg_dist(pts, curve):
    d = np.sqrt(((pts[:, None, :] - curve[None, :, :]) ** 2).sum(-1)); return d.min(1)

def contour_between(C, p, q, ref_dir):
    """contour points from the vertex nearest p to the vertex nearest q, walking in the contour's direction ref_dir (+1/-1)."""
    n = len(C); i = int(np.argmin(((C - p) ** 2).sum(1))); j = int(np.argmin(((C - q) ** 2).sum(1)))
    k = (j - i) % n if ref_dir > 0 else (i - j) % n
    idx = [(i + ref_dir * t) % n for t in range(k + 1)]
    return C[idx]

def fit(C, verts, types, direction=None):
    """C: contour (N,2) in nuqta. verts: [(x,y)], types: 'L'/'A' per segment (closed polyline).
    direction: +1/-1 walking order of C that matches verts order (auto if None)."""
    C = np.asarray(C)
    if direction is None:      # choose the walk that gives the shorter first segment
        a = contour_between(C, np.array(verts[0]), np.array(verts[1]), 1)
        b_ = contour_between(C, np.array(verts[0]), np.array(verts[1]), -1)
        direction = 1 if len(a) <= len(b_) else -1
    out, report = [], []
    for i, p in enumerate(verts):
        q = verts[(i + 1) % len(verts)]
        if types[i] == "L":
            out.append((p[0], p[1], 0.0)); continue
        pts = contour_between(C, np.array(p), np.array(q), direction)
        pts = pts[1:-1] if len(pts) > 4 else pts
        f = lambda b: seg_dist(pts, arc_points(p, q, b)).mean()
        r = minimize_scalar(f, bounds=(-0.95, 0.95), method="bounded")
        out.append((p[0], p[1], float(r.x))); report.append((i, round(float(r.x), 4), round(float(r.fun), 4)))
    return out, report

def max_dev(C, poly, n=30):
    from shapely.geometry import Polygon, Point
    pts = []
    for i, (x, y, b) in enumerate(poly):
        q = poly[(i + 1) % len(poly)]
        pts += list(arc_points((x, y), (q[0], q[1]), b, n)[:-1])
    P = Polygon(pts)
    d = [P.exterior.distance(Point(c)) for c in C[:: max(1, len(C) // 400)]]
    return round(max(d), 3), round(float(np.mean(d)), 3)
