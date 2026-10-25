import math
# Waw geometry in MODULE units. origin = left grid line, y=0 = bottom line, baseline = y 1.5
ALPHA = math.atan(1/7)            # tangent-to-chord angle of every curve (= 45 - 36.87 = 71.57 - 63.43 deg)
B = math.tan(ALPHA/2)             # DXF bulge for that arc (~0.0711)
T  = (0.5, 0.0)    # tail tip
J  = (2.5, 1.5)    # join point (outer, on baseline)
O1 = (2.5, 1.5 + 30/49)   # top of join face = horizontal stroke (unified)
A  = (1.5, 4.0)    # apex
L  = (0.0, 2.5)    # left point of the head
K1 = (1.5, 1.0)    # where the 45deg lower-left edge meets x=1.5
K2 = (1.5, 0.75)   # bottom of the hook
DOT = (1.25, 2.5)  # optional eye dot, r = 1/16 module
# vertices with bulge on the segment that starts at that vertex
POLY = [(T, +B), (J, 0), (O1, -B), (A, 0), (L, 0), (K1, 0), (K2, +B)]

def sample(poly, n=40):
    out = []
    for i, (p, b) in enumerate(poly):
        q = poly[(i + 1) % len(poly)][0]
        if b == 0: out += [p]; continue
        theta = 4 * math.atan(b); c = math.dist(p, q); R = c / (2 * math.sin(theta / 2))
        mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
        dx, dy = (q[0] - p[0]) / c, (q[1] - p[1]) / c
        h = R * math.cos(theta / 2)                       # signed: centre LEFT of p->q for b>0
        cx, cy = mx - dy * h, my + dx * h
        a0 = math.atan2(p[1] - cy, p[0] - cx)
        for k in range(n):
            a = a0 + theta * k / n
            out.append((cx + abs(R) * math.cos(a), cy + abs(R) * math.sin(a)))
    return out
