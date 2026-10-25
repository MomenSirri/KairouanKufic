"""Harakat on the pen of the font (nuqta units). Top marks sit on y = 0 (their anchor), bottom marks hang from y = 0.
Strokes ~0.27 nuqta across (was 0.15), ends cut flat like the pen; sukun = the book's rhombic nuqta, hollow.
Also: superscript alef (U+0670), the wasla sign (for U+0671) and the Du'ali red dots (Kairouan manuscripts)."""
from shapely.geometry import Polygon, Point, LineString, box
from shapely.ops import unary_union
from shapely import affinity

T = 0.27                                   # stroke across
def _fatha():                              # leaning stroke, flat (pen) ends, 0.9 wide 0.55 high
    return Polygon([(-0.45, 0.0), (-0.05, 0.0), (0.45, 0.55), (0.05, 0.55)])
def _below(g): return affinity.translate(g, 0, -g.bounds[3])           # hang from y = 0
def _damma():
    head = Point(0.08, 0.36).buffer(0.21, 48).difference(Point(0.08, 0.36).buffer(0.065, 32))
    tail = Polygon([(-0.02, 0.24), (0.27, 0.24), (-0.12, 0.0), (-0.40, 0.0)])
    return unary_union([head, tail])
def _sukun():
    o = Polygon([(0, 0.0), (0.34, 0.34), (0, 0.68), (-0.34, 0.34)])
    i = Polygon([(0, 0.2), (0.14, 0.34), (0, 0.48), (-0.14, 0.34)])
    return o.difference(i)
def _shadda():
    return LineString([(-0.45, 0.45), (-0.3, 0.05), (-0.08, 0.36), (0.06, 0.05), (0.28, 0.36), (0.45, 0.05)]).buffer(
        0.11, cap_style=2, join_style=2, mitre_limit=3).intersection(box(-1, 0, 1, 1))
def _madda():
    import math
    pts = [(-0.55 + 1.1 * t / 24, 0.13 * math.sin(math.pi * 2 * t / 24) + 0.2) for t in range(25)]
    return LineString(pts).buffer(0.11, cap_style=2, join_style=2)
def _superalef():                          # small alif: vertical stroke with the alif's slanted top
    return Polygon([(-0.13, 0.0), (0.13, 0.0), (0.13, 0.62), (-0.13, 0.78)])
def _wasla():                              # the sad-head sign above alef wasla
    loop = Point(0.14, 0.24).buffer(0.21, 48).difference(Point(0.14, 0.24).buffer(0.08, 32))
    tail = Polygon([(-0.42, 0.03), (0.0, 0.03), (0.06, 0.23), (-0.36, 0.23)])
    return unary_union([loop, tail]).intersection(box(-1, 0, 1, 1))

def make():
    """name -> (unicode or None, 'top'/'bottom', shapely geometry)"""
    fa = _fatha(); dm = _damma()
    return {
        "fatha": (0x064E, "top", fa),
        "fathatan": (0x064B, "top", unary_union([fa, affinity.translate(fa, 0, 0.66)])),
        "kasra": (0x0650, "bottom", _below(fa)),
        "kasratan": (0x064D, "bottom", _below(unary_union([fa, affinity.translate(fa, 0, 0.66)]))),
        "damma": (0x064F, "top", dm),
        "dammatan": (0x064C, "top", unary_union([affinity.translate(dm, -0.3, 0), affinity.translate(dm, 0.32, 0)])),
        "sukun": (0x0652, "top", _sukun()),
        "shadda": (0x0651, "top", _shadda()),
        "maddaabove": (0x0653, "top", _madda()),
        "superalef": (0x0670, "top", _superalef()),
        "wasla": (None, "top", _wasla()),
    }

def duali(r=0.22):
    """Du'ali vowel dots (ss03): fatha = dot above, kasra = dot below, damma = dot before the letter (to its left),
    tanween = two dots. Drawn red where the app supports colour fonts (COLR), black elsewhere."""
    d = lambda x, y: Point(x, y).buffer(r, 48)
    return {
        "fatha": d(0, r + 0.05), "kasra": d(0, -r - 0.05), "damma": d(-0.6, r + 0.05),
        "fathatan": unary_union([d(-0.27, r + 0.05), d(0.27, r + 0.05)]),
        "kasratan": unary_union([d(-0.27, -r - 0.05), d(0.27, -r - 0.05)]),
        "dammatan": unary_union([d(-0.6, r + 0.05), d(-1.12, r + 0.05)]),
    }

def contours(geom):
    gs = [geom] if geom.geom_type == "Polygon" else [g for g in geom.geoms if g.geom_type == "Polygon"]
    out = []
    for g in gs:
        g = g.simplify(0.002)
        out.append(([(x, y, 0) for x, y in list(g.exterior.coords)[:-1]], True))
        for i in g.interiors: out.append(([(x, y, 0) for x, y in list(i.coords)[:-1]], False))
    return out
