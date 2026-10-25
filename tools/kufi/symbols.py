"""Digits and punctuation on the Kairouan-Kufic system (nuqta units, baseline 0, glyph starts at x = 0).
Strokes: horizontal bars H thick, vertical bars V wide, free ends cut at 60 deg (like the joins), dots = the user's
round dot (r 1/4). Arabic zero = the book's rhombic nuqta. Height of figures D = 3 nuqta (between ba tooth and fa head).
Every symbol can be redrawn in the master: a cell labelled '<label>_isol' replaces the generated shape."""
import math
from shapely.geometry import Polygon, Point, LineString, box
from shapely.ops import unary_union
from shapely import affinity

def make(S, dot_r=0.25):
    V, H, CUT = S.V, S.H, S.CUT
    D = 3.0
    TC = V * math.tan(math.radians(30))          # 60-deg cut on a vertical stroke end
    def vbar(x, y0, y1, top_cut=False, bot_cut=False):
        return Polygon([(x, y0 + (TC if bot_cut else 0)), (x + V, y0), (x + V, y1 - (TC if top_cut else 0)), (x, y1)])
    def hbar(x0, x1, y, lcut=False, rcut=False):  # band H thick, bottom at y; cut ends lean like the joins
        return Polygon([(x0 - (CUT if lcut else 0), y), (x1 - (CUT if rcut else 0), y), (x1, y + H), (x0, y + H)])
    def dot(x, y): return Point(x, y).buffer(dot_r, 64)
    def ring(x0, y0, x1, y1, r):                  # rounded box with a rounded counter (strokes V / H)
        o = box(x0 + r, y0 + r, x1 - r, y1 - r).buffer(r, 64)
        ri = max(0.05, r - min(V, H))
        i = box(x0 + V + ri, y0 + H + ri, x1 - V - ri, y1 - H - ri).buffer(ri, 64)
        return o.difference(i)
    def rhomb(cx, cy, h): return Polygon([(cx, cy - h), (cx + h, cy), (cx, cy + h), (cx - h, cy)])
    def stroke(pts, w): return LineString(pts).buffer(w / 2, cap_style=2, join_style=2, mitre_limit=4)
    U_ = unary_union
    out = []                                      # (name, [unicodes], label, geometry)
    def add(name, unis, geom, label=None): out.append((name, unis, label or name.replace(".", "-"), geom))

    # ---------- Arabic-Indic digits ٠-٩ ----------
    add("zero.ar", [0x0660], rhomb(0.5, 1.3, 0.5))
    add("one.ar", [0x0661], vbar(0, 0, D, top_cut=True))
    st2, y2 = 2.4, 1.79
    add("two.ar", [0x0662], U_([vbar(0, 0, st2 + 0.01, top_cut=True), hbar(0, 1.35, y2 - 0.01), vbar(1.35 - V, y2, D, top_cut=True)]))
    add("three.ar", [0x0663], U_([vbar(0, 0, st2 + 0.01, top_cut=True), hbar(0, 2.1, y2 - 0.01),
                                  vbar(1.05 - V / 2, y2, D - 0.3, top_cut=True), vbar(2.1 - V, y2, D, top_cut=True)]))
    add("four.ar", [0x0664], U_([vbar(0, 0, D), hbar(0, 1.4, D - H, rcut=True), hbar(0, 1.05, 1.25, rcut=True), hbar(0, 1.4, 0)]))
    add("five.ar", [0x0665], ring(0, 0, 1.55, 2.1, 0.6))
    add("six.ar", [0x0666], U_([vbar(1.3 - V, 0, D), hbar(0, 1.3, D - H, lcut=True)]))
    w7, s7 = 0.62, 1.85                            # ٧ : two leaning strokes meeting on the baseline
    left = Polygon([(0, D), (w7, D), ((s7 + w7) / 2, 0), ((s7 - w7) / 2, 0)])
    right = Polygon([(s7 - w7, D), (s7, D), ((s7 + w7) / 2, 0), ((s7 - w7) / 2, 0)])
    add("seven.ar", [0x0667], U_([left, right]))
    add("eight.ar", [0x0668], affinity.scale(U_([left, right]), 1, -1, origin=(0, D / 2)))
    add("nine.ar", [0x0669], U_([ring(0, 1.25, 1.4, D, 0.45), vbar(1.4 - V, 0, D)]))

    # ---------- Western digits 0-9 (bar construction, same strokes) ----------
    Wd = 1.7; M = (D - H) / 2
    seg = {"a": hbar(0, Wd, D - H), "g": hbar(0, Wd, M), "d": hbar(0, Wd, 0),
           "f": vbar(0, D / 2, D), "e": vbar(0, 0, D / 2 + 0.01), "b": vbar(Wd - V, D / 2, D), "c": vbar(Wd - V, 0, D / 2 + 0.01)}
    digs = {"zero": "abcdef", "two": "abged", "three": "abgcd", "four": "fgbc", "five": "afgcd",
            "six": "afgedc", "seven": "abc", "eight": "abcdefg", "nine": "abcdfg"}
    for i, n in enumerate(["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]):
        if n == "one":
            g = U_([vbar(0.55, 0, D), Polygon([(0, D - 0.7), (0.55, D - 0.2), (0.55 + V, D), (0.55, D), (0.0, D - 0.7 + 0.45)])])
        else:
            g = U_([seg[k] for k in digs[n]])
        add(n, [0x30 + i], g)

    # ---------- punctuation ----------
    comma_ar = U_([dot(0.3, 0.3), Polygon([(0.08, 0.42), (0.52, 0.42), (0.85, 1.15), (0.55, 1.15)])])   # inverted comma
    add("comma.ar", [0x060C, 0x066B], comma_ar)
    add("comma", [0x2C], affinity.rotate(comma_ar, 180, origin=(0.45, 0.55)))
    add("semicolon.ar", [0x061B], U_([affinity.translate(comma_ar, 0, 1.2), dot(0.3, 0.3)]))
    add("semicolon", [0x3B], U_([affinity.rotate(comma_ar, 180, origin=(0.45, 0.55)), dot(0.6, 1.9)]))
    add("colon", [0x3A], U_([dot(0.3, 0.3), dot(0.3, 1.9)]))
    add("exclam", [0x21], U_([vbar(0, 1.0, D, top_cut=True), dot(V / 2, 0.3)]))
    qx = 0.75                                      # ؟ = mirrored question mark: the hook comes down on the left
    q_ar = U_([hbar(0, 1.45, D - H, rcut=True), vbar(0, 1.85, D), hbar(0, qx + V / 2, 1.6),
               vbar(qx - V / 2, 0.95, 1.6 + H), dot(qx, 0.3)])
    add("question.ar", [0x061F], q_ar)
    add("question", [0x3F], affinity.scale(q_ar, -1, 1, origin=(0.725, 0)))
    pl = U_([vbar(0, -0.8, 3.8), hbar(0, 0.95, 3.8 - H, rcut=True), hbar(0, 0.95, -0.8, rcut=True)])
    add("parenleft", [0x28], pl)
    add("parenright", [0x29], affinity.scale(pl, -1, 1, origin=(0.475, 0)))
    chev = stroke([(0.85, 2.15), (0.1, 1.35), (0.85, 0.55)], 0.42)
    gl = U_([chev, affinity.translate(chev, 0.65, 0)])
    add("guillemetleft", [0xAB], gl)
    add("guillemetright", [0xBB], affinity.scale(gl, -1, 1, origin=(0.75, 0)))
    add("hyphen", [0x2D, 0x2010, 0x2011], hbar(0, 1.25, 1.05, lcut=True, rcut=True))
    add("endash", [0x2013], hbar(0, 2.0, 1.05, lcut=True, rcut=True))
    add("emdash", [0x2014], hbar(0, 3.2, 1.05, lcut=True, rcut=True))
    add("slash", [0x2F], Polygon([(0, -0.5), (V * 1.15, -0.5), (1.45 + V * 1.15, 3.5), (1.45, 3.5)]))
    add("percent.ar", [0x066A], U_([rhomb(0.35, 2.55, 0.35), rhomb(1.35, 0.45, 0.35),
                                    Polygon([(0.05, -0.1), (0.05 + V, -0.1), (1.65, 3.1), (1.65 - V, 3.1)])]))
    add("percent", [0x25], U_([ring(0, 1.75, 0.95, 3.0, 0.3), ring(1.05, 0, 2.0, 1.25, 0.3),
                               Polygon([(0.1, -0.1), (0.1 + V, -0.1), (1.95, 3.1), (1.95 - V, 3.1)])]))
    add("periodcentered", [0xB7, 0x2022], dot(dot_r, 1.3))
    cm_lat = affinity.rotate(comma_ar, 180, origin=(0.45, 0.55))
    qr = affinity.translate(cm_lat, 0, 2.35); ql = affinity.translate(comma_ar, 0, 1.9)
    add("quoteright", [0x2019], qr); add("quoteleft", [0x2018], ql)
    add("quotedblright", [0x201D], U_([qr, affinity.translate(qr, 0.6, 0)]))
    add("quotedblleft", [0x201C], U_([ql, affinity.translate(ql, 0.6, 0)]))
    add("quotesingle", [0x27], vbar(0, 2.2, 3.4, top_cut=True))
    add("quotedbl", [0x22], U_([vbar(0, 2.2, 3.4, top_cut=True), vbar(0.75, 2.2, 3.4, top_cut=True)]))
    add("plus", [0x2B], U_([hbar(0, 1.7, 1.05), vbar(0.85 - V / 2, 0.45, 2.25)]))
    add("equal", [0x3D], U_([hbar(0, 1.7, 0.55), hbar(0, 1.7, 1.55)]))
    return out

def contours(geom):
    """shapely -> [(verts, is_outer)] with (x, y, 0) vertices."""
    gs = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)
    out = []
    for g in gs:
        g = g.simplify(0.002)
        out.append(([(x, y, 0) for x, y in list(g.exterior.coords)[:-1]], True))
        for i in g.interiors: out.append(([(x, y, 0) for x, y in list(i.coords)[:-1]], False))
    return out
