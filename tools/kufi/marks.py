"""Dots (i'jam), eyes, hamza, madda and harakat - built on the system.
The book itself is undotted (early Kufic); these are added so the font can write modern Arabic.
  DOT  : rhombus (the book's nuqta shape) with diagonal = pen width W.  Two dots side by side, gap G.
  EYE  : round counter, diameter 1/4 nuqta, at the head's centre (as drawn in the book: meem, fa, qaf, waw, heh, ain).
  HAMZA: the ain hook (strict) at 0.3 scale.   MADDA: thin wave.   HARAKAT: thin pen strokes (book p. 55)."""
import os, math, importlib.util
from shapely.geometry import Polygon, LineString, Point, box
from shapely import affinity
from shapely.ops import unary_union
HERE = os.path.dirname(os.path.abspath(__file__))
def _load(n, rel):
    sp = importlib.util.spec_from_file_location(n, os.path.join(HERE, "..", rel)); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
S = _load("kufi_spec", "kufi/spec.py"); sg = _load("seen_geom", "seen/geom.py"); AS = _load("ain_strict", "ain/strict.py")
W, H, G = S.W, S.H, S.G
D = W                       # dot diagonal
GAP = 0.3                   # clearance letter -> dot
EYE_R = 0.125

def dot(cx, cy):
    h = D / 2; return [(cx, cy - h, 0), (cx + h, cy, 0), (cx, cy + h, 0), (cx - h, cy, 0)]

def dots(n, cx, cy, up=True):
    """n dots centred on (cx, cy) = centre of the bottom row (above) or top row (below)."""
    s = D + G
    if n == 1: return [dot(cx, cy)]
    if n == 2: return [dot(cx - s / 2, cy), dot(cx + s / 2, cy)]
    row2 = cy + (D * 0.75 if up else -D * 0.75)
    return [dot(cx - s / 2, cy), dot(cx + s / 2, cy), dot(cx, row2)] if up else [dot(cx - s / 2, cy), dot(cx + s / 2, cy), dot(cx, row2)]

def eye(cx, cy, r=EYE_R, n=24):     # clockwise hole
    return [(cx + r * math.cos(-2 * math.pi * k / n), cy + r * math.sin(-2 * math.pi * k / n), 0) for k in range(n)]

def poly_of(outer, holes=()):
    return Polygon(sg.sample(outer, 16), [sg.sample(h, 16) for h in holes]).buffer(0)

def head_centroid(P, ymin=None):
    ymin = H + 0.15 if ymin is None else ymin
    part = P.intersection(box(-50, ymin, 50, 50))
    if part.is_empty: return P.centroid.x, P.centroid.y
    if part.geom_type == "MultiPolygon": part = max(part.geoms, key=lambda g: g.area)
    c = part.representative_point() if not part.contains(part.centroid) else part.centroid
    return c.x, c.y

def top_at(P, x, w=0.55):
    g = P.intersection(box(x - w, -50, x + w, 50)); return g.bounds[3] if not g.is_empty else P.bounds[3]
def bottom_at(P, x, w=0.55):
    g = P.intersection(box(x - w, -50, x + w, 50)); return g.bounds[1] if not g.is_empty else P.bounds[1]

def eye_fits(P, x, y, r=EYE_R): return P.buffer(-(r + 0.09)).contains(Point(x, y))

# ---------- shapes as (x, y, bulge) lists ----------
def from_shapely(g):
    if g.geom_type == "MultiPolygon": g = max(g.geoms, key=lambda p: p.area)
    return [(x, y, 0) for x, y in list(g.exterior.coords)[:-1]]

def hamza():
    P = poly_of(AS.ain_init())
    P = P.intersection(box(AS.K2[0] - 0.05, -1, 10, 10))          # hook + jaw, no left join
    P = affinity.scale(P, 0.3, 0.3, origin=(0, 0))
    minx, miny, maxx, maxy = P.bounds
    return from_shapely(affinity.translate(P, -(minx + maxx) / 2, -miny))

def madda():
    pts = [(-0.55 + 1.1 * t / 20, 0.12 * math.sin(math.pi * 2 * t / 20) + 0.12) for t in range(21)]
    return from_shapely(LineString(pts).buffer(0.065, cap_style=2, join_style=2))

def stroke(p, q, t=0.15):
    return from_shapely(LineString([p, q]).buffer(t / 2, cap_style=2, join_style=2))
def fatha(dy=0): return stroke((-0.32, 0.05 + dy), (0.32, 0.4 + dy))
def fathatan(): return fatha(0) + [], fatha(0.38)
def damma():
    WW = _load("waw_g", "waw/geom.py")
    P = poly_of([(p[0], p[1], b) for p, b in WW.POLY])
    P = affinity.scale(P, 0.16, 0.16, origin=(0, 0)); minx, miny, maxx, maxy = P.bounds
    return from_shapely(affinity.translate(P, -(minx + maxx) / 2, -miny))
def sukun():
    ring = Point(0, 0.25).buffer(0.22).difference(Point(0, 0.25).buffer(0.11))
    return [(x, y, 0) for x, y in list(ring.exterior.coords)[:-1]], [[(x, y, 0) for x, y in list(ring.interiors[0].coords)[:-1]]]
def shadda():
    return from_shapely(LineString([(-0.45, 0.42), (-0.32, 0.05), (-0.08, 0.32), (0.06, 0.05), (0.3, 0.32), (0.45, 0.05)]).buffer(0.065, cap_style=2, join_style=2))
