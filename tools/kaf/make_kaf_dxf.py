import sys, math, importlib.util, ezdxf
from ezdxf.enums import TextEntityAlignment as TA
spec = importlib.util.spec_from_file_location("kaf_geom", sys.argv[3]); g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
OUT, TPL_IN, _, TPL_OUT = sys.argv[1:5]
M = 125.0
doc = ezdxf.new("R2018", setup=True); doc.header["$INSUNITS"] = 0; doc.header["$LTSCALE"] = 12
msp = doc.modelspace()
for n, c, lt, lw in [("MODULE_GRID", 8, "Continuous", 18), ("HALF_GRID", 9, "DASHED", 0), ("BASELINE", 5, "Continuous", 50),
                     ("KAF", 7, "Continuous", 35), ("KAF_FILL", 2, "Continuous", 0), ("POINTS", 1, "Continuous", 0),
                     ("DIMS", 3, "Continuous", 0), ("NOTES", 7, "Continuous", 0)]:
    doc.layers.add(n, color=c, linetype=lt).dxf.lineweight = lw
st = doc.dimstyles.duplicate_entry("EZDXF", "MODULE")
st.dxf.dimtxt = 24; st.dxf.dimasz = 16; st.dxf.dimexe = 10; st.dxf.dimexo = 8; st.dxf.dimgap = 6
st.dxf.dimclrd = 3; st.dxf.dimclre = 3; st.dxf.dimclrt = 3
def T(s, p, h=26):
    msp.add_text(s, height=h, dxfattribs={"layer": "NOTES", "style": "OpenSans"}).set_placement(p, align=TA.MIDDLE_LEFT)
def place(name, poly, ox, x0, x1, dims):
    F = lambda p: (ox + p[0] * M, p[1] * M); y0, y1 = -0.5, 6.0
    k = math.floor(x0 * 2) / 2
    while k <= x1 + 1e-9:
        msp.add_line(F((k, y0)), F((k, y1)), dxfattribs={"layer": "MODULE_GRID" if abs(k - round(k)) < 1e-9 else "HALF_GRID"}); k += .5
    k = y0
    while k <= y1 + 1e-9:
        msp.add_line(F((x0, k)), F((x1, k)), dxfattribs={"layer": "MODULE_GRID" if abs(k - round(k)) < 1e-9 else "HALF_GRID"}); k += .5
    msp.add_line(F((x0 - .3, 0)), F((x1 + .3, 0)), dxfattribs={"layer": "BASELINE"})
    pts = [(*F((x, y)), b) for x, y, b in poly]
    msp.add_lwpolyline(pts, format="xyb", close=True, dxfattribs={"layer": "KAF"})
    h = msp.add_hatch(color=2, dxfattribs={"layer": "KAF_FILL"}); h.paths.add_polyline_path(pts, is_closed=True)
    for x, y, b in pts: msp.add_circle((x, y), 4, dxfattribs={"layer": "POINTS"})
    T(name, F((x0, y1 + .5)), 34)
    for a, b, base, ang, txt in dims:
        msp.add_linear_dim(base=F(base), p1=F(a), p2=F(b), angle=ang, text=txt, dimstyle="MODULE", dxfattribs={"layer": "DIMS"}).render()
COMMON = [((0, 0), (0, 5.5), (-1.4, 0), 90, "5.5"), ((2.5, 5.5), (3.0, 5.5), (0, 5.9), 0, "1/2"),
          ((0, 5.5), (2.5, 5.5), (0, 5.9), 0, "2.5"), ((3.0, 5.5), (3.0, 5.0), (3.5, 0), 90, "1/2"),
          ((2.5, 4.0), (2.5, 0), (3.9, 0), 90, "4"), ((g.L(0), 0), (0, 0), (0, -0.4), 0, "5/6"),
          ((0, 1.0), (0, 0), (-0.6, 0), 90, "1"), ((0, g.BODY), (0, 0), (-1.0, 0), 90, "1.5")]
NOSE = [((g.XN, 0), (g.XN + .5, .75), (0, -0.4), 0, "1/2")]
CONN = [((g.XN, 0), (g.XN + .5, .75), (0, -0.4), 0, "1/2"), ((g.XN + .5, .75), (g.XN + 1.25, .75), (0, -0.4), 0, "3/4")]
CL = [(g.CONN_BL, (g.CONN_TL[0], 0), (0, -0.9), 0, "0.46"), (g.CONN_BL, (g.L(0), 0), (0, -1.3), 0, "2/3")]
place("KAF  isol  (as drawn)", g.kaf_isol(), 0, -1.5, 5.5, COMMON + NOSE)
place("KAF  init  (joins left)", g.kaf_init(), -8.5 * M, -2.0, 5.5, COMMON + NOSE + CL)
place("KAF  medi  (joins both)", g.kaf_medi(), -17.5 * M, -2.0, 6.5, COMMON + CONN + CL)
place("KAF  fina", g.kaf_fina(), -27.0 * M, -1.5, 6.5, COMMON + CONN)
notes = ["1 module = 125 units.  Baseline y=0.  Tip +5.5 (top line).  Body 1.5 (= Sad).",
         "Outer edge: ONE straight line 5:6 (50.2 deg) through (0,1) and (2.5,4): from the tail tip (-5/6, 0) up to the neck.",
         "Stem = 1/4 pen thick (the book: 'not more than 1/4 pen').  Neck: vertical, x 2.5 .. 3.0, tip cut 45 deg from (2.5,5) to (3,5.5).",
         "Slot 1/7 pen on y=0.75, OPEN to the left (a notch, part of the one outline), right end at 4.25 cut 45 deg.",
         "Nose and right connector = identical to the Sad (drawn nose is ~0.1 shorter; the book: body length may vary).",
         "Left join (init/medi): the lower bar continues left under the open slot; its top stays on the slot bottom line,",
         "   end cut like the Sad connector (1/2 across per 3/4 up), join point (-1.5, 0) = 2/3 module beyond the isol tail tip.",
         "Optional: FILLET where the neck's right edge meets the stem (sketch is rounded there).  Dashed 'اختياري' tall curved top not drawn."]
for i, s in enumerate(notes): T(s, (-27 * M - 1.5 * M, -1.3 * M - i * 50), 28)
doc.set_modelspace_vport(height=1700, center=(-11 * M, 2.5 * M))
doc.saveas(OUT)
t = ezdxf.readfile(TPL_IN); tm = t.modelspace()
forms = {"kaf_isol": (g.kaf_isol(), g.XN + .5), "kaf_init": (g.kaf_init(), g.XN + .5),
         "kaf_medi": (g.kaf_medi(), g.XN + 1.25), "kaf_fina": (g.kaf_fina(), g.XN + 1.25)}
for e in tm.query("TEXT"):
    if e.dxf.text not in forms: continue
    poly, xmax = forms[e.dxf.text]; cx, cy = e.dxf.align_point.x, e.dxf.align_point.y
    x, yb = cx - 500, cy + 90 + 250; ox = x + 1000 - xmax * M
    tm.add_lwpolyline([(ox + px * M, yb + py * M, b) for px, py, b in poly], format="xyb", close=True, dxfattribs={"layer": "GLYPHS"})
    print(e.dxf.text, "placed")
t.saveas(TPL_OUT)
