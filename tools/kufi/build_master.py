"""Master DXF: every letter / form in one file, on the nuqta grid, unified spec. 1 nuqta = 196 units (UPM 2048)."""
import sys, os, math, importlib.util, ezdxf
from ezdxf.enums import TextEntityAlignment as TA
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(name, rel):
    sp = importlib.util.spec_from_file_location(name, os.path.join(ROOT, rel)); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
S = load("spec", "kufi/spec.py")
seen, sad, tah, kaf = load("seen", "seen/geom.py"), load("sad", "sad/geom.py"), load("tah", "tah/geom.py"), load("kaf", "kaf/geom.py")
reh, waw = load("reh", "reh/geom.py"), load("waw", "waw/geom.py")
alif, bez = load("alif", "alif/geom.py"), load("bez", "alif/bez.py")
ba = load("ba", "ba/geom.py")
jeem = load("jeem", "jeem/geom.py")
fa = load("fa", "fa/geom.py")
ain = load("ain_strict", "ain/strict.py")
fas = load("fa_strict", "fa/strict.py")
hs = load("heh_strict", "heh/strict.py")
ms = load("mh_strict", "mh/strict.py")
from ezdxf.math import Bezier4P, bezier_to_bspline, Vec3
def BEZ(name): return {"bez": bez.load(os.path.join(ROOT, "alif", name + ".json"))}
U = S.DOT
OUT = sys.argv[1]

def shift(poly, dy): return [(x, y + dy, b) for x, y, b in poly]
RAA = shift([(x, y, 0) for x, y in reh.SOLID], -1.5)
WAW = shift([(p[0], p[1], b) for p, b in waw.POLY], -1.5)
GLYPHS = {   # letter -> {form: (outer, [holes])}  or  {form: ({"bez": contours}, [])}
    "alif  ا": {"isol": (alif.alif_isol(), []), "fina": (alif.alif_fina(), [])},
    "ba / ta / tha  ب ت ث": {f: (getattr(ba, "ba_" + f)(), []) for f in ("isol", "init", "medi", "fina")},
    "meem  م": {f: (getattr(ms, "meem_" + f)(), []) for f in ("isol", "init", "medi", "fina")},
    "jeem / hah / khah  ج ح خ": {f: (getattr(ms, "hah_" + f)(), []) for f in ("isol", "init", "medi", "fina")},
    "dal / thal  د ذ": {"isol": (jeem.dal_isol(), []), "fina": (jeem.dal_fina(), [])},
    "ain / ghain  ع غ": {f: (getattr(ain, "ain_" + f)(), []) for f in ("isol", "init", "medi", "fina")},
    "fa  ف": {f: (getattr(fas, "fa_" + f)(), []) for f in ("isol", "init", "medi", "fina")},
    "qaf  ق": {"isol": (hs.qaf_isol(), []), "fina": (hs.qaf_fina(), []),
               "init": (fas.fa_init(), []), "medi": (fas.fa_medi(), [])},
    "heh  ه": {f: (getattr(hs, "heh_" + f)(), []) for f in ("isol", "init", "medi", "fina")},
    "nun  ن": {"isol": (hs.nun_isol(), []), "fina": (hs.nun_fina(), []), "init": (ba.ba_init(), []), "medi": (ba.ba_medi(), [])},
    "ya  ي": {"isol": (hs.ya_isol(), []), "fina": (hs.ya_fina(), []), "init": (ba.ba_init(), []), "medi": (ba.ba_medi(), [])},
    "lam  ل": {f: (getattr(alif, "lam_" + f)(), []) for f in ("isol", "init", "medi", "fina")},
    "lam-alif  لا": {"isol": (ms.lamalif_isol(), [ms.lamalif_isol_hole()]), "fina": (ms.lamalif_fina(), [])},
    "raa / zay  ر ز": {"isol": (RAA, []), "fina": (RAA, [])},
    "waw  و": {"isol": (WAW, []), "fina": (WAW, [])},
    "seen / sheen  س ش": {"isol": (seen.seen_isol()[0], []), "init": (seen.seen_init(), []),
                          "medi": (seen.seen_medi(), []), "fina": (seen.seen_fina()[0], [])},
    "sad / dad  ص ض": {f: (p, [sad.slot()]) for f, p in [("isol", sad.sad_isol()[0]), ("init", sad.sad_init()),
                                                        ("medi", sad.sad_medi()), ("fina", sad.sad_fina()[0])]},
    "tah / zah  ط ظ": {f: (p, [tah.slot()]) for f, p in [("isol", tah.tah_isol()), ("init", tah.tah_init()),
                                                        ("medi", tah.tah_medi()), ("fina", tah.tah_fina())]},
    "kaf  ك": {f: (p, []) for f, p in [("isol", kaf.kaf_isol()), ("init", kaf.kaf_init()),
                                       ("medi", kaf.kaf_medi()), ("fina", kaf.kaf_fina())]},
}
ROWS = ["alif  ا", "ba / ta / tha  ب ت ث", "jeem / hah / khah  ج ح خ", "dal / thal  د ذ", "raa / zay  ر ز",
        "seen / sheen  س ش", "sad / dad  ص ض", "tah / zah  ط ظ", "ain / ghain  ع غ", "fa  ف", "qaf  ق", "kaf  ك",
        "lam  ل", "meem  م", "nun  ن", "heh  ه", "waw  و", "ya  ي", "lam-alif  لا"]
NONJOIN = {"alif  ا", "dal / thal  د ذ", "raa / zay  ر ز", "waw  و", "lam-alif  لا"}
FORMS = ["isol", "init", "medi", "fina"]          # right -> left
CW, CH = 13.0, 11.0                               # cell size in nuqta
Y0, Y1 = S.DESC - 0.5, S.ASC + 0.5                # cell vertical span

doc = ezdxf.new("R2018", setup=True)
doc.header["$INSUNITS"] = 0; doc.header["$LTSCALE"] = 20
msp = doc.modelspace()
for n, c, lt, lw in [("GRID_NUQTA", 8, "Continuous", 18), ("GRID_HALF", 9, "DASHED", 0), ("BASELINE", 5, "Continuous", 50),
                     ("GUIDE_ALIF", 4, "DASHED", 0), ("GUIDE_STROKE", 30, "DASHED", 0), ("CELL", 8, "Continuous", 35),
                     ("LABELS", 7, "Continuous", 0), ("GLYPHS", 7, "Continuous", 35), ("GLYPH_FILL", 2, "Continuous", 0),
                     ("NA", 253, "Continuous", 0), ("SPEC", 7, "Continuous", 25), ("SPEC_FILL", 2, "Continuous", 0)]:
    doc.layers.add(n, color=c, linetype=lt).dxf.lineweight = lw
def T(s, p, h, layer="LABELS", al=TA.MIDDLE_LEFT):
    msp.add_text(s, height=h, dxfattribs={"layer": layer, "style": "OpenSans"}).set_placement(p, align=al)
def L(a, b, layer): msp.add_line(a, b, dxfattribs={"layer": layer})

def cell(cx, cy, slug, na=False):
    """cx = cell right edge (nuqta), cy = baseline (nuqta)"""
    F = lambda x, y: ((cx + x) * U, (cy + y) * U)
    x0, x1 = -CW, 0.0
    msp.add_lwpolyline([F(x0, Y0), F(x1, Y0), F(x1, Y1), F(x0, Y1)], close=True, dxfattribs={"layer": "CELL"})
    T(slug, F(x0 + 0.2, Y1 - 0.4), 0.3 * U)
    if na:
        h = msp.add_hatch(color=253, dxfattribs={"layer": "NA"}); h.set_pattern_fill("ANSI31", scale=60)
        h.paths.add_polyline_path([F(x0, Y0), F(x1, Y0), F(x1, Y1), F(x0, Y1)], is_closed=True); return
    k = math.ceil(x0 * 2) / 2
    while k < x1 - 1e-9:
        L(F(k, Y0), F(k, Y1), "GRID_NUQTA" if abs(k - round(k)) < 1e-9 else "GRID_HALF"); k += .5
    k = math.ceil(Y0 * 2) / 2
    while k < Y1 - 1e-9:
        L(F(x0, k), F(x1, k), "GRID_NUQTA" if abs(k - round(k)) < 1e-9 else "GRID_HALF"); k += .5
    L(F(x0 - .4, 0), F(x1 + .4, 0), "BASELINE")
    L(F(x0, S.ALIF), F(x1, S.ALIF), "GUIDE_ALIF")
    L(F(x0, S.H), F(x1, S.H), "GUIDE_STROKE")

def place_bez(cx, cy, contours):
    xmax = max(p[0] for c in contours for sg_ in c for p in sg_)
    ox = cx - 0.5 - xmax
    F = lambda p: ((ox + p[0]) * U, (cy + p[1]) * U)
    h = msp.add_hatch(color=2, dxfattribs={"layer": "GLYPH_FILL"})
    for i, c in enumerate(contours):
        curves = [Bezier4P([Vec3(*F(p)) for p in sg_]) for sg_ in c]
        sp = msp.add_spline(dxfattribs={"layer": "GLYPHS"}); sp.apply_construction_tool(bezier_to_bspline(curves)); sp.closed = True
        h.paths.add_polyline_path([F(p) for p in bez.sample_contour(c, 10)], is_closed=True, flags=1 if i == 0 else 16)

def place(cx, cy, outer, holes):
    if isinstance(outer, dict): return place_bez(cx, cy, outer["bez"])
    xmax = max(x for x, y, b in outer)
    ox = cx - 0.5 - xmax
    F = lambda x, y: ((ox + x) * U, (cy + y) * U)
    po = [(*F(x, y), b) for x, y, b in outer]
    msp.add_lwpolyline(po, format="xyb", close=True, dxfattribs={"layer": "GLYPHS"})
    h = msp.add_hatch(color=2, dxfattribs={"layer": "GLYPH_FILL"}); h.paths.add_polyline_path(po, is_closed=True, flags=1)
    for hp in holes:
        ph = [(*F(x, y), b) for x, y, b in hp]
        msp.add_lwpolyline(ph, format="xyb", close=True, dxfattribs={"layer": "GLYPHS"})
        h.paths.add_polyline_path(ph, is_closed=True, flags=16)

# ---- spec sheet (top) ----
SX, SY = 0.0, 9.0
T("KAIROUAN KUFIC  -  unified system (book: قواعد الخط الكوفي القيرواني, pp. 3-6, 51)", ((SX - 4 * CW) * U, (SY + 9) * U), 0.6 * U)
lines = [f"1 nuqta (dot) = grid unit = {U} font units  (UPM {S.UPM}).  The dot is a square whose side is the pen width.",
         f"Pen width  W = 5/7 nuqta = {S.W * U:.0f} u      Vertical stroke  V = 5/7 W = {S.V * U:.0f} u      Horizontal stroke  H = 6/7 W = {S.H * U:.0f} u",
         f"Gap / hairline  G = 1/7 W = {S.G * U:.0f} u  (slots, cup arm, tah stem)      Stroke-end cut = pen edge at 60 deg: {S.CUT * U:.0f} u across, H up",
         f"Alif = 5 nuqta.   Line spacing = 6.5 nuqta.   Body letters (sad / tah / kaf) = 2H + G = {(2 * S.H + S.G) * U:.0f} u.   Joins: band height H on the baseline.",
         "Cells: 13 x 11 nuqta, baseline marked, dashed orange = H, dashed cyan = alif height.  Draw/keep glyphs on layer GLYPHS."]
for i, s in enumerate(lines):
    T(s, ((SX - 4 * CW) * U, (SY + 7.8 - i * 0.75) * U), 0.38 * U)
# pen diagram: dot + three strokes
def poly(pts, fill=True):
    pp = [(x * U, y * U) for x, y in pts]
    msp.add_lwpolyline(pp, close=True, dxfattribs={"layer": "SPEC"})
    if fill:
        h = msp.add_hatch(color=2, dxfattribs={"layer": "SPEC_FILL"}); h.paths.add_polyline_path(pp, is_closed=True)
bx, by = SX - 12, SY + 1.0
poly([(bx, by + .5), (bx + .5, by + 1), (bx + 1, by + .5), (bx + .5, by)])
T("1 nuqta", ((bx - .1) * U, (by - .5) * U), 0.3 * U)
poly([(bx + 2, by), (bx + 2 + S.V, by), (bx + 2 + S.V, by + 2.2), (bx + 2, by + 2.2)])
T("V", ((bx + 2) * U, (by - .5) * U), 0.3 * U)
poly([(bx + 3.4, by), (bx + 6.4, by), (bx + 6.4 + S.CUT, by + S.H), (bx + 3.4 + S.CUT, by + S.H)])
T("H, 60deg ends", ((bx + 3.4) * U, (by - .5) * U), 0.3 * U)
poly([(bx + 7.6, by), (bx + 9.6, by), (bx + 9.6, by + S.G), (bx + 7.6, by + S.G)])
T("G", ((bx + 7.6) * U, (by - .5) * U), 0.3 * U)

# ---- letter rows ----
for r, row in enumerate(ROWS):
    cy = -r * CH
    T(row, (1.0 * U, cy * U + 0.5 * U), 0.55 * U)
    done = GLYPHS.get(row, {})
    T("done" if done else "to do", (1.0 * U, cy * U - 0.4 * U), 0.35 * U)
    for j, f in enumerate(FORMS):
        cx = -j * (CW + 0.6)
        na = row in NONJOIN and f in ("init", "medi")
        cell(cx, cy, f"{row.split()[0]}_{f}", na)
        if f in done: place(cx, cy, *done[f])
doc.set_modelspace_vport(height=40 * U, center=(-25 * U, -5 * U))
doc.saveas(OUT)
print("rows", len(ROWS), "glyph forms", sum(len(v) for v in GLYPHS.values()))
