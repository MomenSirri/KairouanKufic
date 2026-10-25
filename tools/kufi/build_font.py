"""Build the Kairouan Kufic OpenType font (CFF) from the strict glyph geometry.
Units: 1 nuqta = 196 font units, UPM 2048.  Joining: exit (left band top) at x = 0, entry (right band top) at x = advance."""
import os, sys, math, importlib.util
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from shapely.geometry import Polygon, box
from shapely import affinity
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import glyphset, wordtest as wt
def load(n, rel):
    sp = importlib.util.spec_from_file_location(n, os.path.join(HERE, "..", rel)); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
S = load("spec", "kufi/spec.py"); MK = load("marks", "kufi/marks.py"); sg = load("seen", "seen/geom.py")
U = S.DOT; H = S.H; CUT = S.CUT
SB = 0.35                                  # side bearing (nuqta) on non-joining sides
OV = 0.06                                  # joins overlap by 0.06 nuqta so no seam shows
OUT = sys.argv[1]

GS = glyphset.build()
DWG_DOTS, DWG_EYES = {}, {}
if os.environ.get("KUFI_DWG"):
    import dwg_glyphs, dwg_marks, symbols as _symbols_pre
    dwg_glyphs.MULTI_NAMES |= {lab for _n, _u, lab, _g in _symbols_pre.make(S)}     # symbol cells: all pieces = one glyph
    GS.update(dwg_glyphs.load(os.environ["KUFI_DWG"]))
    DWG_DOTS, DWG_EYES, _rep = dwg_marks.load(os.environ["KUFI_DWG"])
    if DWG_DOTS:                       # the user's dot shape: round, diameter from the drawing
        _r = next(iter(DWG_DOTS.values()))[0][2]
        MK.D = 2 * _r
        MK.dot = lambda cx, cy: dwg_marks.circle(cx, cy, _r)
import shorts
TAIL_MODE = os.environ.get("KUFI_TAILS", "auto")     # auto = tails under the next word + short form when it would touch
if TAIL_MODE != "off":
    shorts.make(GS, DWG_EYES, H, sg.sample)
FORMS = ["isol", "init", "medi", "fina"]
LET = [  # name, unicode, base, joining, extra
    ("alef", 0x0627, "alif", "R", None), ("alefHamzaAbove", 0x0623, "alif", "R", ("hamza", "above")),
    ("alefHamzaBelow", 0x0625, "alif", "R", ("hamza", "below")), ("alefMadda", 0x0622, "alif", "R", ("madda", "above")),
    ("beh", 0x0628, "ba", "D", (1, "below")), ("teh", 0x062A, "ba", "D", (2, "above")), ("theh", 0x062B, "ba", "D", (3, "above")),
    ("jeem", 0x062C, "hah", "D", (1, "jeem")), ("hah", 0x062D, "hah", "D", None), ("khah", 0x062E, "hah", "D", (1, "above")),
    ("dal", 0x062F, "dal", "R", None), ("thal", 0x0630, "dal", "R", (1, "above")),
    ("reh", 0x0631, "raa", "R", None), ("zain", 0x0632, "raa", "R", (1, "above")),
    ("seen", 0x0633, "seen", "D", None), ("sheen", 0x0634, "seen", "D", (3, "above")),
    ("sad", 0x0635, "sad", "D", None), ("dad", 0x0636, "sad", "D", (1, "above")),
    ("tah", 0x0637, "tah", "D", None), ("zah", 0x0638, "tah", "D", (1, "body")),
    ("ain", 0x0639, "ain", "D", None), ("ghain", 0x063A, "ain", "D", (1, "above")),
    ("feh", 0x0641, "fa", "D", (1, "above")), ("qaf", 0x0642, "qaf", "D", (2, "above")),
    ("kaf", 0x0643, "kaf", "D", None), ("lam", 0x0644, "lam", "D", None), ("meem", 0x0645, "meem", "D", None),
    ("noon", 0x0646, "nun", "D", (1, "above")), ("heh", 0x0647, "heh", "D", None), ("tehMarbuta", 0x0629, "heh", "R", (2, "above")),
    ("waw", 0x0648, "waw", "R", None), ("wawHamza", 0x0624, "waw", "R", ("hamza", "above")),
    ("alefWasla", 0x0671, "alif", "R", ("wasla", "above")),
    ("yeh", 0x064A, "ya", "D", (2, "below")), ("alefMaksura", 0x0649, "ya", "D", None), ("yehHamza", 0x0626, "ya", "D", ("hamza", "above")),
]
EYES = {"meem": "all", "fa": "all", "qaf": "all", "waw": "all", "heh": "all", "ain": ("medi", "fina")}

import harakat
HK = harakat.make()
def _mark_shape(kind):
    """single-contour (x, y, bulge) list for hamza / madda sitting on y = 0; wasla returns several contours"""
    if kind == "hamza": return MK.hamza()
    if kind == "madda": return harakat.contours(HK["maddaabove"][2])[0][0]
    return [c for c, _ in harakat.contours(HK["wasla"][2])]
def P_of(outer, holes=()): return MK.poly_of(outer, holes)
def free(P, cand, pad=MK.G):
    return all(not P.buffer(pad).intersects(Polygon(sg.sample(d, 8))) for d in cand)

def place_dots(P, n, where, form):
    hx, hy = MK.head_centroid(P)
    if where == "body":
        y = (2 * H + MK.G) + MK.GAP + MK.D / 2; xs = [P.bounds[2] - 1.0 - 0.25 * k for k in range(16)]
        for x in xs:
            c = MK.dots(n, x, y)
            if free(P, c): return c
    if where == "jeem":
        low = P.intersection(box(-50, -50, 50, -0.4))
        if form in ("isol", "fina"):
            hole = low.convex_hull.difference(P)
            if hole.geom_type == "MultiPolygon": hole = max(hole.geoms, key=lambda g: g.area)
            c = hole.centroid; return MK.dots(1, c.x, c.y)
        hx = low.centroid.x; where = "below"
    if where == "above":
        y0 = MK.top_at(P, hx) + MK.GAP + MK.D / 2
    else:
        upper = P.intersection(box(-50, -0.95, 50, 50))
        y0 = MK.bottom_at(upper, hx) - MK.GAP - MK.D / 2
    for dy in [0, 0.25, 0.5, 0.75, 1.0]:
        y = y0 + (dy if where == "above" else -dy)
        for dx in [0, -0.25, 0.25, -0.5, 0.5, -0.75, 0.75, -1.0, -1.25, -1.5]:
            c = MK.dots(n, hx + dx, y, up=(where == "above"))
            if free(P, c): return c
    return MK.dots(n, hx, y0, up=(where == "above"))

def place_mark(P, shape, where, hx=None):
    hx = MK.head_centroid(P)[0] if hx is None else hx
    ys = [b for a, b, c in shape]
    if where == "above":
        y = MK.top_at(P, hx) + 0.25 - min(ys)
    else:
        y = MK.bottom_at(P, hx) - 0.25 - max(ys)
    return [(x + hx, yy + y, b) for x, yy, b in shape]

def area(c):
    pts = sg.sample(c, 8); return 0.5 * sum(pts[i][0] * pts[i - 1][1] - pts[i - 1][0] * pts[i][1] for i in range(len(pts))) * -1
def reverse(c):
    n = len(c); return [(c[j][0], c[j][1], -c[j - 1][2]) for j in range(n - 1, -1, -1)]
def orient(c, ccw):
    a = area(c)
    return c if (a > 0) == ccw else reverse(c)

def compose(base, form, extra, name, alt=""):
    outer, holes, _ = GS[f"{base}_{form}{alt}"]
    key = f"{base}_{form}{alt}"
    P = P_of(outer, holes)
    contours = [(outer, True)] + [(h, False) for h in holes]
    ek = EYES.get(base)
    if DWG_EYES:
        for x, y, r in DWG_EYES.get(key, []): contours.append((dwg_marks.circle(x, y, r), False))
    elif ek and (ek == "all" or form in ek):
        hx, hy = MK.head_centroid(P)
        pts = [(hx, hy)] if not (base == "heh" and form in ("init", "medi")) else [(hx - 0.3, hy + 0.35), (hx + 0.3, hy - 0.35)]
        for x, y in pts:
            if MK.eye_fits(P, x, y): contours.append((MK.eye(x, y), False))
    if extra:
        if isinstance(extra[0], int) and (name, form + alt) in DWG_DOTS:
            for x, y, r in DWG_DOTS[(name, form + alt)]: contours.append((dwg_marks.circle(x, y, r), True))
        elif isinstance(extra[0], int):
            for d in place_dots(P, extra[0], extra[1], form): contours.append((d, True))
        elif extra[0] == "wasla":
            parts = _mark_shape("wasla"); ref = place_mark(P, parts[0], extra[1])
            dx, dy = ref[0][0] - parts[0][0][0], ref[0][1] - parts[0][0][1]
            g = HK["wasla"][2]
            for c, outer_ in harakat.contours(g): contours.append(([(x + dx, y + dy, b) for x, y, b in c], outer_))
        else:
            shape = _mark_shape(extra[0])
            contours.append((place_mark(P, shape, extra[1]), True))
    return outer, contours

def lamalef_variant(form, extra):
    outer, holes, _ = GS[f"lamalif_{form}"]; P = P_of(outer, holes)
    contours = [(outer, True)] + [(h, False) for h in holes]
    if extra:
        shape = _mark_shape(extra[0])
        hx = -0.45 if form == "isol" else -1.55
        if extra[1] == "below": hx = -1.0 if form == "isol" else -0.9
        if form == "fina":                    # follow the drawing: above the top tip on the right, below the middle of the foot
            tips = [v for v in outer if v[1] > 0.8 * max(u[1] for u in outer)]
            foot = [v[0] for v in outer if abs(v[1]) < 1e-6]
            joinx = min(v[0] for v in outer if abs(v[1] - H) < 0.02 and v[0] > min(foot))
            hx = max(t[0] for t in tips) if extra[1] == "above" else (min(foot) + min(joinx, max(foot))) / 2
        contours.append((place_mark(P, shape, extra[1], hx), True))
    return outer, contours

# ------------------------------------------------------------------ glyphs
glyphs = {}           # name -> (contours, advance, lsb shift)
TAIL_LETTERS = {"yeh", "alefMaksura", "yehHamza", "noon", "qaf", "seen", "sheen", "sad", "dad"}
TAIL_Y = float(os.environ.get("KUFI_TAIL_Y", "-1.0"))       # the long-tail letter's box ends at its ink above this height
TAIL_KERN = float(os.environ.get("KUFI_TAIL_KERN", "1.0"))   # chosen: D (1 nuqta closer)    # ... and the next word comes this much closer still
def add(name, outer, contours, form):
    pts_samp = sg.sample(outer, 8)
    xs = [x for c, _ in contours for x, y in sg.sample(c, 8)]
    if form in ("init", "medi"): ox = min(wt.pts_at_H(outer))
    else:
        ox = min(xs) - SB
        if TAIL_MODE != "off":       # descending tails may reach under the next word: box = ink above the tail zone
            tail = name.split(".")[0] in TAIL_LETTERS and ".alt" not in name
            ycut = TAIL_Y if tail else -1.0
            xa = [x for c, _ in contours for x, y in sg.sample(c, 8) if y > ycut]
            ox = max(ox, min(xa) - SB) + (TAIL_KERN if tail else 0.0)
    if form in ("medi", "fina"): adv = wt.entry_x(outer) - ox - OV
    else: adv = max(xs) - ox + SB
    glyphs[name] = ([(orient([(x - ox, y, b) for x, y, b in c], ccw), ccw) for c, ccw in contours], adv)

cmap = {}; forms_of = {}; ALTS = {}
for name, uni, base, jt, extra in LET:
    fl = FORMS if jt == "D" else ["isol", "fina"]
    forms_of[name] = fl
    for f in fl:
        o, cs = compose(base, f, extra, name)
        add(f"{name}.{f}", o, cs, f)
        k = 1
        while f"{base}_{f}.alt{k}" in GS:                 # alternates drawn in the same cell (left of the default)
            o, cs = compose(base, f, extra, name, f".alt{k}")
            add(f"{name}.{f}.alt{k}", o, cs, f); ALTS.setdefault(f"{name}.{f}", []).append(f"{name}.{f}.alt{k}")
            k += 1
    cmap[uni] = f"{name}.isol"
LAMALEF = [("lamalef", None, "alef"), ("lamalefHamzaAbove", ("hamza", "above"), "alefHamzaAbove"),
           ("lamalefHamzaBelow", ("hamza", "below"), "alefHamzaBelow"), ("lamalefMadda", ("madda", "above"), "alefMadda")]
for nm, ex, _ in LAMALEF:
    for f in ("isol", "fina"):
        o, cs = lamalef_variant(f, ex); add(f"{nm}.{f}", o, cs, f)
# Allah ligature, drawn by the user as one cell (alif + لله + eye)
LIGAS = []
if os.environ.get("KUFI_DWG") and "allah" in dwg_glyphs.MULTI:
    _tops, _holes = dwg_glyphs.MULTI["allah"]
    _eyes = [c for k, v in DWG_EYES.items() if k.startswith("allah_isol") for c in v]
    _alif = max(_tops, key=lambda t: t[1][2])                 # the alif is the rightmost shape
    _rest = [t for t in _tops if t is not _alif]
    def _mk(shapes):
        return ([(c, True) for c, _ in shapes] + [(h, False) for h in _holes] +
                [(dwg_marks.circle(x, y, r), False) for x, y, r in _eyes])
    add("allah", _alif[0], _mk(_tops), "isol")
    add("lillah", _rest[0][0], _mk(_rest), "isol")
    _ax0, _ay0, _ax1, _ay1 = _alif[1]                          # ٱللّه: the wasla sign over the alif
    _w = [([(x + (_ax0 + _ax1) / 2, y + _ay1 + 0.25, b) for x, y, b in c], o) for c, o in harakat.contours(HK["wasla"][2])]
    add("allahWasla", _alif[0], _mk(_tops) + _w, "isol")
    LIGAS += ["  sub alef.isol lam.init lam.medi heh.fina by allah;", "  sub alefWasla.isol lam.init lam.medi heh.fina by allahWasla;",
              "  sub lam.init lam.medi heh.fina by lillah;"]
    cmap[0xFDF2] = "allah"                                   # ﷲ  ARABIC LIGATURE ALLAH ISOLATED FORM
# digits and punctuation (symbols.py), each replaceable by a master cell labelled '<label>_isol'
import symbols
SYMBOLS = symbols.make(S, dot_r=(MK.D / 2) if DWG_DOTS else 0.25)
SYM_FROM_DWG = []
for _n, _unis, _lab, _g in SYMBOLS:
    _key = f"{_lab}_isol"
    _multi = dwg_glyphs.MULTI.get(_lab) if os.environ.get("KUFI_DWG") else None
    _dots = dwg_marks.RAW.get(_key, []) if os.environ.get("KUFI_DWG") else []
    if _multi or _dots:
        _tops, _h = _multi or ([], [])
        _cs = [(c, True) for c, _ in _tops] + [(h, False) for h in _h] + [(dwg_marks.circle(x, y, r), True) for x, y, r in _dots]
        _o = _cs[0][0]; SYM_FROM_DWG.append(_n)
    else:
        _cs = symbols.contours(_g); _o = _cs[0][0]
    add(_n, _o, _cs, "isol")
    for _u in _unis: cmap.setdefault(_u, _n)
cmap.setdefault(0xA0, "space")
# dots that touch the next letter move toward their own letter, only in that context
import dotshift
_DOTFEA, _ndot = dotshift.build(glyphs, sg.sample, orient)
# kashida (مد): every joining letter gets versions whose outgoing band is 1, 2, 3 nuqta longer
KASH = [1.0, 2.0, 3.0]
KALTS = {}
for _n in [n for n in list(glyphs) if n.endswith((".init", ".medi"))]:
    _cs, _adv = glyphs[_n]
    for _k, _L in enumerate(KASH, 1):
        _band = orient([(-CUT, 0.0, 0), (_L + 0.1 - CUT, 0.0, 0), (_L + 0.1, H, 0), (0.0, H, 0)], True)
        glyphs[f"{_n}.k{_k}"] = ([(_band, True)] + [([(x + _L, y, b) for x, y, b in c], ccw) for c, ccw in _cs], _adv + _L)
        KALTS.setdefault(_n, []).append(f"{_n}.k{_k}")
# hamza alone, tatweel, space, marks
hz = [(x * 1.5, y * 1.5, b) for x, y, b in MK.hamza()]
add("hamza", hz, [(hz, True)], "isol"); cmap[0x0621] = "hamza"
tat = [(-CUT, 0.0, 0), (0.0, H, 0), (1.0, H, 0), (1.0 - CUT, 0.0, 0)]
glyphs["tatweel"] = ([(orient(tat, True), True)], 1.0 - OV); cmap[0x0640] = "tatweel"
glyphs["space"] = ([], 1.6); cmap[0x20] = "space"
dotp = [(x, y + MK.D / 2, b) for x, y, b in MK.dot(0, 0)]
add("period", dotp, [(dotp, True)], "isol"); cmap[0x2E] = "period"; cmap[0x06D4] = "period"
MARKS = {}
def mark(name, uni, contours, where):
    glyphs[name] = ([(orient(c, ccw), ccw) for c, ccw in contours], 0.0); MARKS[name] = where
    if uni: cmap[uni] = name
for _hn, (_hu, _hw, _hg) in HK.items():
    if _hn == "wasla": continue
    mark(_hn, _hu, harakat.contours(_hg), _hw)
DUALI = {}
for _hn, _hg in harakat.duali().items():
    mark(f"{_hn}.dot", None, harakat.contours(_hg), MARKS[_hn]); DUALI[_hn] = f"{_hn}.dot"
mark("hamzaabove", 0x0654, [(MK.hamza(), True)], "top")
mark("hamzabelow", 0x0655, [([(x, y - 0.9, b) for x, y, b in MK.hamza()], True)], "bottom")

# ------------------------------------------------------------------ anchors for marks
def anchors(name):
    cs, adv = glyphs[name]
    polys = [Polygon(sg.sample(c, 8)) for c, ccw in cs if ccw]
    if not polys: return None
    from shapely.ops import unary_union
    P = unary_union([p.buffer(0) for p in polys])
    hx, _ = MK.head_centroid(P)
    return (hx, MK.top_at(P, hx, 0.45) + 0.2), (hx, MK.bottom_at(P, hx, 0.45) - 0.2)

# ------------------------------------------------------------------ draw
def draw(pen, contours):
    for c, ccw in contours:
        n = len(c)
        pen.moveTo((round(c[0][0] * U), round(c[0][1] * U)))
        for i in range(n):
            x0, y0, b = c[i]; x1, y1, _ = c[(i + 1) % n]
            if abs(b) < 1e-9:
                if i < n - 1: pen.lineTo((round(x1 * U), round(y1 * U)))
                continue
            th = 4 * math.atan(b); ch = math.dist((x0, y0), (x1, y1)); R = ch / (2 * math.sin(th / 2))
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2; dx, dy = (x1 - x0) / ch, (y1 - y0) / ch
            hh = R * math.cos(th / 2); cx, cy = mx - dy * hh, my + dx * hh; r = abs(R)
            a0 = math.atan2(y0 - cy, x0 - cx); k = max(1, math.ceil(abs(th) / (math.pi / 2)))
            step = th / k; t = 4 / 3 * math.tan(step / 4)
            for j in range(k):
                a1 = a0 + step * j; a2 = a1 + step
                p1 = (cx + r * math.cos(a1), cy + r * math.sin(a1)); p2 = (cx + r * math.cos(a2), cy + r * math.sin(a2))
                c1 = (p1[0] - t * r * math.sin(a1), p1[1] + t * r * math.cos(a1))
                c2 = (p2[0] + t * r * math.sin(a2), p2[1] - t * r * math.cos(a2))
                if j == k - 1: p2 = (x1, y1)
                pen.curveTo(*[(round(px * U), round(py * U)) for px, py in (c1, c2, p2)])
        pen.closePath()

# zero-width controls (ZWNJ, ZWJ, LRM, RLM, ALM, word joiner, BOM): present as empty glyphs
glyphs["zerowidth"] = ([], 0.0)
for _u in (0x200B, 0x200C, 0x200D, 0x200E, 0x200F, 0x061C, 0x2060, 0xFEFF): cmap[_u] = "zerowidth"
# Arabic presentation forms (old PDFs / web pages): each code point -> the glyph of that form
_PF = [("hamza", 1), ("alefMadda", 2), ("alefHamzaAbove", 2), ("wawHamza", 2), ("alefHamzaBelow", 2), ("yehHamza", 4),
       ("alef", 2), ("beh", 4), ("tehMarbuta", 2), ("teh", 4), ("theh", 4), ("jeem", 4), ("hah", 4), ("khah", 4),
       ("dal", 2), ("thal", 2), ("reh", 2), ("zain", 2), ("seen", 4), ("sheen", 4), ("sad", 4), ("dad", 4), ("tah", 4),
       ("zah", 4), ("ain", 4), ("ghain", 4), ("feh", 4), ("qaf", 4), ("kaf", 4), ("lam", 4), ("meem", 4), ("noon", 4),
       ("heh", 4), ("waw", 2), ("alefMaksura", 2), ("yeh", 4),
       ("lamalefMadda", 2), ("lamalefHamzaAbove", 2), ("lamalefHamzaBelow", 2), ("lamalef", 2)]
_cp = 0xFE80; PRES = 0
for _nm, _k in _PF:
    for _f in ["isol", "fina", "init", "medi"][:_k]:
        _g = _nm if _k == 1 else f"{_nm}.{_f}"
        if _g in glyphs: cmap[_cp] = _g; PRES += 1
        _cp += 1
assert _cp == 0xFEFD, hex(_cp)
for _cp, _g in [(0xFE70, "fathatan"), (0xFE72, "dammatan"), (0xFE74, "kasratan"), (0xFE76, "fatha"), (0xFE78, "damma"),
                (0xFE7A, "kasra"), (0xFE7C, "shadda"), (0xFE7E, "sukun")]:
    if _g in glyphs: cmap[_cp] = _g; PRES += 1
order = [".notdef"] + list(glyphs)
fb = FontBuilder(1400, isTTF=True)               # TrueType outlines: the most robust format on Windows
fb.setupGlyphOrder(order)
fb.setupCharacterMap(cmap)
ttglyphs, metrics = {}, {}
for g in order:
    adv = 1000 if g == ".notdef" else round(glyphs[g][1] * U)
    tp = TTGlyphPen(None)
    pen = ReverseContourPen(Cu2QuPen(tp, max_err=1.0, reverse_direction=False))   # TrueType wants outer contours clockwise
    if g == ".notdef":
        pen.moveTo((100, 0)); pen.lineTo((900, 0)); pen.lineTo((900, 1000)); pen.lineTo((100, 1000)); pen.closePath()
    else: draw(pen, glyphs[g][0])
    ttglyphs[g] = tp.glyph()
    metrics[g] = (adv, 0)
fb.setupGlyf(ttglyphs)
for g in order:
    gl = fb.font["glyf"][g]; metrics[g] = (metrics[g][0], getattr(gl, "xMin", 0))
fb.setupHorizontalMetrics(metrics)
fb.setupHorizontalHeader(ascent=1250, descent=-900)
fb.setupNameTable({"familyName": {"en": "Kairouan Kufic", "ar": "الكوفي القيرواني"}, "styleName": "Regular",
                   "uniqueFontIdentifier": "2.1;MOMN;KairouanKufic-Regular", "fullName": {"en": "Kairouan Kufic Regular", "ar": "الكوفي القيرواني"},
                   "psName": "KairouanKufic-Regular", "version": "Version 2.100",
                   "copyright": "Copyright 2026 Momen, with Reserved Font Names \"Kairouan Kufic\" and \"الكوفي القيرواني\".",
                   "licenseDescription": "This Font Software is licensed under the SIL Open Font License, Version 1.1. "
                                         "This license is available with a FAQ at: https://openfontlicense.org",
                   "licenseInfoURL": "https://openfontlicense.org",
                   "manufacturer": "Momen", "designer": "Momen",
                   "description": "Kairouan Kufic: an Arabic Kufic typeface drawn on the nuqta grid of the Kairouan school "
                                  "(lines and true arcs, 60-degree pen cuts), after the construction rules of Amer Ben Jeddou (قواعد الخط الكوفي القيرواني). Features: positional forms, lam-alif, Allah ligature, "
                                  "short tails (ss01, automatic), kashida (ss02, jalt), Du'ali red vowel dots (ss03)."}, mac=False)
fb.setupOS2(achVendID="MOMN", usWeightClass=400, usWidthClass=5, fsSelection=0x40 | 0x80, fsType=0, version=4,
            ulUnicodeRange1=(1 << 0) | (1 << 13), ulUnicodeRange2=0, ulCodePageRange1=(1 << 0) | (1 << 6),
            sTypoAscender=1250, sTypoDescender=-900, sTypoLineGap=150, usWinAscent=1300, usWinDescent=950)
fb.setupPost(keepGlyphNames=True)
if DUALI:
    fb.setupCPAL([[(0.78, 0.20, 0.12, 1.0)]])                  # manuscript vermilion
    fb.setupCOLR({g: [(g, 0)] for g in DUALI.values()})
fb.setupMaxp()

# ------------------------------------------------------------------ features
fea = ["languagesystem DFLT dflt;", "languagesystem arab dflt;"]
for f in FORMS:
    lines = [f"  sub {n}.isol by {n}.{f};" for n, *_ in LET if f in forms_of[n] and f != "isol"]
    if lines: fea.append(f"feature {f} {{\n" + "\n".join(lines) + f"\n}} {f};")
lig = []
for nm, ex, al in LAMALEF:
    lig.append(f"  sub lam.init {al}.fina by {nm}.isol;"); lig.append(f"  sub lam.medi {al}.fina by {nm}.fina;")
fea.append("feature rlig {\n" + "\n".join(lig) + "\n} rlig;")
if LIGAS: fea.append("feature liga {\n  lookupflag IgnoreMarks;\n" + "\n".join(LIGAS) + "\n} liga;")
if _DOTFEA: fea.append(_DOTFEA)
if DUALI:   # ss03: Du'ali vowel dots (red in colour-capable apps)
    fea.append("feature ss03 {\n  featureNames { name \"Du'ali vowel dots (Kairouan manuscripts)\"; name 3 1 0x0C01 \"حركات أبي الأسود الدؤلي\"; };\n" +
               "\n".join(f"  sub {k} by {v};" for k, v in DUALI.items()) + "\n} ss03;")
if KALTS:   # jalt = justification alternates (InDesign/Word pick them to justify); ss02 = every join 1 nuqta longer
    fea.append("feature jalt {\n" + "\n".join(f"  sub {g} from [{' '.join(a)}];" for g, a in KALTS.items()) + "\n} jalt;")
    fea.append("feature ss02 {\n  featureNames { name \"Kashida: every join +1 nuqta\"; name 3 1 0x0C01 \"مد كل الوصلات نقطة\"; };\n" +
               "\n".join(f"  sub {g} by {a[0]};" for g, a in KALTS.items()) + "\n} ss02;")
if ALTS:   # alternates: aalt = all (glyph panels), salt = first, ssNN = the N-th alternate of every letter that has one
    fea.append("feature aalt {\n" + "\n".join(f"  sub {g} from [{' '.join(a)}];" for g, a in ALTS.items()) + "\n} aalt;")
    fea.append("feature salt {\n" + "\n".join(f"  sub {g} by {a[0]};" for g, a in ALTS.items()) + "\n} salt;")
    for n in range(1, max(len(a) for a in ALTS.values()) + 1):
        rules = "\n".join(f"  sub {g} by {a[n - 1]};" for g, a in ALTS.items() if len(a) >= n)
        fea.append(f"feature ss{n:02d} {{\n  featureNames {{ name \"{'Short tails' if n == 1 else f'Alternate {n}'}\"; name 3 1 0x0C01 \"{'الأشكال القصيرة' if n == 1 else f'الشكل البديل {n}'}\"; }};\n{rules}\n}} ss{n:02d};")
if TAIL_MODE != "off" and ALTS:
    _c = shorts.calt(glyphs, ALTS, MARKS, sg.sample)
    if _c: fea.append(_c)
KERN_LETTERS = set(filter(None, os.environ.get("KUFI_KERN", "reh,zain,waw,wawHamza,alef,alefHamzaAbove,alefHamzaBelow,alefMadda,dal,thal,tehMarbuta,lamalef,lamalefHamzaAbove,lamalefHamzaBelow,lamalefMadda").split(",")))
if KERN_LETTERS:
    import kern
    _k, KSTATS = kern.build(glyphs, MARKS, sg.sample, U, KERN_LETTERS)
    fea.append(_k)
SHORT_KERN = float(os.environ.get("KUFI_SHORT_KERN", "2.0"))  # chosen: 2 nuqta   # the word after a short (tail-less) form comes closer, up to this
if SHORT_KERN > 0 and ALTS:
    import kern
    _k, _ = kern.build(glyphs, MARKS, sg.sample, U, set(), tmax_in=0.0, tmax_space=SHORT_KERN,
                       lefts=[a for v in ALTS.values() for a in v])
    fea.append(_k)
top = [m for m, w in MARKS.items() if w == "top"]; bot = [m for m, w in MARKS.items() if w == "bottom"]
fea.append(f"markClass [{' '.join(top)}] <anchor 0 0> @TOP;")
fea.append(f"markClass [{' '.join(bot)}] <anchor 0 0> @BOT;")
# mark-to-ligature for الله / لله: one anchor pair per letter (alef, lam, lam, heh), so harakat do not pile up
LIGCOMP = {}
def _lig_anchors(name, with_alif):
    from shapely.ops import unary_union
    cs = glyphs[name][0]
    polys = [Polygon(sg.sample(c, 8)).buffer(0) for c, ccw in cs if ccw]
    P = unary_union(polys)
    big = sorted([p for p in polys if p.area > 0.5], key=lambda p: -p.bounds[2])
    xs = []
    if with_alif:
        alif = big[0]; xs.append((alif.bounds[0] + alif.bounds[2]) / 2); body = unary_union(big[1:])
    else:
        body = unary_union(big)
    tall = body.intersection(box(-50, 2.6, 50, 50))
    stems = sorted(([tall] if tall.geom_type == "Polygon" else list(tall.geoms)), key=lambda p: -p.bounds[2])
    xs += [(p.bounds[0] + p.bounds[2]) / 2 for p in stems[:2]]          # the two lams
    holes = [Polygon(sg.sample(c, 8)) for c, ccw in cs if not ccw]
    xs.append(min(h.centroid.x for h in holes) if holes else body.bounds[0] + 0.8)   # heh: at its eye
    return [((x, MK.top_at(P, x, 0.55) + 0.25), (x, MK.bottom_at(P, x, 0.55) - 0.25)) for x in xs]
for _ln, _wa in (("allah", True), ("allahWasla", True), ("lillah", False)):
    if _ln in glyphs:
        try: LIGCOMP[_ln] = _lig_anchors(_ln, _wa)
        except Exception as _e: print("lig anchors failed", _ln, _e)
mk = []
for _ln, _comps in LIGCOMP.items():
    _parts = [f"<anchor {round(tx * U)} {round(ty * U)}> mark @TOP <anchor {round(bx * U)} {round(by * U)}> mark @BOT" for (tx, ty), (bx, by) in _comps]
    mk.append(f"  pos ligature {_ln} " + " ligComponent ".join(_parts) + ";")
for g in order:
    if g in (".notdef", "space") or g in MARKS or g in LIGCOMP: continue
    a = anchors(g)
    if not a: continue
    (tx, ty), (bx, by) = a
    mk.append(f"  pos base {g} <anchor {round(tx * U)} {round(ty * U)}> mark @TOP <anchor {round(bx * U)} {round(by * U)}> mark @BOT;")
fea.append("feature mark {\n" + "\n".join(mk) + "\n} mark;")
# mark on mark: a vowel over shadda / madda / hamza / small alif, a kasra under hamza-below
def _mtop(n): return max(y for c, ccw in glyphs[n][0] for x, y in sg.sample(c, 8))
def _mbot(n): return min(y for c, ccw in glyphs[n][0] for x, y in sg.sample(c, 8))
_stack_top = [n for n in ("fatha", "fathatan", "damma", "dammatan", "sukun", "superalef", "fatha.dot", "fathatan.dot", "damma.dot", "dammatan.dot") if n in glyphs]
_stack_bot = [n for n in ("kasra", "kasratan", "kasra.dot", "kasratan.dot") if n in glyphs]
fea.append(f"markClass [{' '.join(_stack_top)}] <anchor 0 0> @STACK_T;")
fea.append(f"markClass [{' '.join(_stack_bot)}] <anchor 0 0> @STACK_B;")
_mm = []
for _c in ("shadda", "maddaabove", "hamzaabove", "superalef", "fatha", "fatha.dot"):
    if _c in glyphs: _mm.append(f"  pos mark {_c} <anchor 0 {round((_mtop(_c) + 0.12) * U)}> mark @STACK_T;")
if "hamzabelow" in glyphs: _mm.append(f"  pos mark hamzabelow <anchor 0 {round((_mbot('hamzabelow') - 0.12) * U)}> mark @STACK_B;")
fea.append("feature mkmk {\n" + "\n".join(_mm) + "\n} mkmk;")
fea.append(f"table GDEF {{ GlyphClassDef [{' '.join(g for g in order if g not in MARKS and g not in LIGCOMP and g != '.notdef')}], [{' '.join(LIGCOMP)}], [{' '.join(MARKS)}], ; }} GDEF;")
addOpenTypeFeaturesFromString(fb.font, "\n".join(fea))
fb.save(OUT)
open(OUT + ".fea", "w").write("\n".join(fea))
print("glyphs", len(order), "->", OUT, "presentation forms:", PRES, "alternates:", ALTS)
import json as _j; open(OUT + ".alts.json", "w").write(_j.dumps(ALTS))
