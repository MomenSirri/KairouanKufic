import json, numpy as np
def load(name): return json.load(open(name))
def sample_contour(segs, n=16):
    out = []
    for p0, c1, c2, p3 in segs:
        p0, c1, c2, p3 = map(np.array, (p0, c1, c2, p3))
        for t in np.linspace(0, 1, n, endpoint=False):
            out.append(tuple((1-t)**3*p0 + 3*(1-t)**2*t*c1 + 3*(1-t)*t**2*c2 + t**3*p3))
    return out
