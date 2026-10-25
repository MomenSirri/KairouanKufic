import numpy as np, potrace, json
U, BASE = 67.0, 518.0
def trace(name):
    m = np.load(f"alif/{name}_mask.npy")
    bm = potrace.Bitmap(~m)
    plist = bm.trace(turdsize=20, alphamax=1.0, opticurve=True, opttolerance=0.3)
    conv = lambda p: ((p.x - 0) / U, (BASE - p.y) / U) if hasattr(p, "x") else ((p[0]) / U, (BASE - p[1]) / U)
    contours = []
    for curve in plist:
        cur = conv(curve.start_point); segs = []
        for s in curve.segments:
            if s.is_corner:
                c, e = conv(s.c), conv(s.end_point)
                segs.append([cur, cur, c, c]); segs.append([c, c, e, e]); cur = e
            else:
                c1, c2, e = conv(s.c1), conv(s.c2), conv(s.end_point)
                segs.append([cur, c1, c2, e]); cur = e
        contours.append(segs)
    xs = [p[0] for c in contours for s in c for p in s]; ys = [p[1] for c in contours for s in c for p in s]
    xr = max(xs)
    snap = lambda p: (round(p[0] - xr, 4), 0.0 if abs(p[1]) < 0.09 else round(p[1], 4))
    contours = [[[snap(p) for p in s] for s in c] for c in contours]
    print(name, "contours", len(contours), "segments", [len(c) for c in contours], "x", round(min(xs) - xr, 2), "y", round(min(ys), 2), round(max(ys), 2))
    json.dump(contours, open(f"alif/{name}.json", "w"))
for n in ["lamalif_isol", "lamalif_fina"]: trace(n)
