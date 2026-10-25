import sys, math, importlib.util, ezdxf
from ezdxf.enums import TextEntityAlignment as TA
from ezdxf.entities.boundary_paths import BoundaryPathType
spec = importlib.util.spec_from_file_location("tah_geom", sys.argv[3]); g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
OUT, TPL_IN, _, TPL_OUT = sys.argv[1:5]
M = 125.0

doc = ezdxf.new("R2018", setup=True)
doc.header["$INSUNITS"] = 0; doc.header["$LTSCALE"] = 12
msp = doc.modelspace()
for n, c, lt, lw in [("MODULE_GRID", 8, "Continuous", 18), ("HALF_GRID", 9, "DASHED", 0),
                     ("BASELINE", 5, "Continuous", 50), ("TAH", 7, "Continuous", 35),
                     ("TAH_FILL", 2, "Continuous", 0), ("POINTS", 1, "Continuous", 0),
                     ("DIMS", 3, "Continuous", 0), ("NOTES", 7, "Continuous", 0)]:
    doc.layers.add(n, color=c, linetype=lt).dxf.lineweight = lw
st = doc.dimstyles.duplicate_entry("EZDXF", "MODULE")
st.dxf.dimtxt = 24; st.dxf.dimasz = 16; st.dxf.dimexe = 10; st.dxf.dimexo = 8; st.dxf.dimgap = 6
st.dxf.dimclrd = 3; st.dxf.dimclre = 3; st.dxf.dimclrt = 3

def T(s, p, h=26, al=TA.MIDDLE_LEFT):
    msp.add_text(s, height=h, dxfattribs={"layer": "NOTES", "style": "OpenSans"}).set_placement(p, align=al)

def place(name, poly, ox, oy, x0, x1, y0, y1, dims=()):
    F = lambda p: (ox + p[0] * M, oy + p[1] * M)
    k = math.floor(x0 * 2) / 2
    while k <= x1 + 1e-9:
        msp.add_line(F((k, y0)), F((k, y1)), dxfattribs={"layer": "MODULE_GRID" if abs(k - round(k)) < 1e-9 else "HALF_GRID"}); k += .5
    k = math.floor(y0 * 2) / 2
    while k <= y1 + 1e-9:
        msp.add_line(F((x0, k)), F((x1, k)), dxfattribs={"layer": "MODULE_GRID" if abs(k - round(k)) < 1e-9 else "HALF_GRID"}); k += .5
    msp.add_line(F((x0 - .3, 0)), F((x1 + .3, 0)), dxfattribs={"layer": "BASELINE"})
    outer = [(*F((x, y)), b) for x, y, b in poly]
    hole = [(*F((x, y)), b) for x, y, b in g.slot()]
    for pts in (outer, hole):
        msp.add_lwpolyline(pts, format="xyb", close=True, dxfattribs={"layer": "TAH"})
        for x, y, b in pts: msp.add_circle((x, y), 4, dxfattribs={"layer": "POINTS"})
    h = msp.add_hatch(color=2, dxfattribs={"layer": "TAH_FILL"})
    h.paths.add_polyline_path(outer, is_closed=True, flags=1)
    h.paths.add_polyline_path(hole, is_closed=True, flags=16)
    T(name, F((x0, y1 + .6)), 34)
    for a, b, base, ang, txt in dims:
        msp.add_linear_dim(base=F(base), p1=F(a), p2=F(b), angle=ang, text=txt, dimstyle="MODULE",
                           dxfattribs={"layer": "DIMS"}).render()

B = g.BODY
UP = [((0, 0), (0, 5), (-0.7, 0), 90, "5"), ((0, 5), (g.TIP[0], 5), (0, 5.5), 0, "3"),
      ((g.TIP[0], 5), (3.5, 5), (0, 5.5), 0, "1/2"), ((3.5, 3.5), (3.5, 0), (6.0, 0), 90, "3.5"),
      ((g.TIP[0], 5), (g.TIP[0], g.CUT_Y), (2.2, 0), 90, "5/8"), ((0, B), (0, 0), (-0.3, 0), 90, "1.25")]
NOSE = [((g.XB, B), (g.NOSE[0], B), (0, 1.7), 0, "1/2"), ((g.NOSE_B[0], 0), (g.NOSE[0], 0.5), (0, -0.7), 0, "1/4"),
        ((g.SLOT_R, 0), (g.XB, 0), (0, -0.7), 0, "1/4")]
CONN_R = [((g.XB, B), (5.5, 0.75), (0, 1.7), 0, "1"), ((5.0, 0), (5.5, 0.75), (0, -0.7), 0, "1/2")]
CONN_L = [((-0.5, 0), (0, 0.75), (0, -0.7), 0, "1/2"), ((0, 0.75), (0.75, 0.75), (0, -0.7), 0, "3/4")]
place("TAH  isol  (= KAF shape)", g.tah_isol(), 0, 0, -0.5, 5.5, -0.5, 5.5, UP + NOSE)
place("TAH  init", g.tah_init(), -8.0 * M, 0, -1.0, 5.5, -0.5, 5.5, UP + NOSE + CONN_L)
place("TAH  medi", g.tah_medi(), -16.0 * M, 0, -1.0, 6.0, -0.5, 5.5, UP + CONN_R + CONN_L)
place("TAH  fina", g.tah_fina(), -23.5 * M, 0, -0.5, 6.0, -0.5, 5.5, UP + CONN_R)
notes = ["1 module = 125 units.  Baseline y=0.  Top tip +5.  Body 1.25 high (as drawn on the diamond grid).",
         "Wedge + stem: one 45 deg line from (0,0) to the inner elbow (3.125, 3.125).  Stem = 1/7 pen thick (labelled), parallel 45 deg.",
         "Head stroke: right edge from tip (3,5) at 1:3 (71.6 deg), meets the 3.5 grid lines at the elbow.  Left edge = right edge moved 1/2 left.",
         "Tip cut from (3,5) to (2.708, 4.375) on the book's 5/8 line (65 deg; sketch says 60).  Outer elbow may be rounded (FILLET) - the book: 'التليين ممكن'.",
         "Nose: body corner (4.5,1.25) -> tip (5,0.5) -> (4.75,0).  Slot 1/7 pen, centred on 0.625, left end parallel to the wedge, right end at 4.25 cut 45 deg.",
         "Connected forms follow the Sad (book: 'as in the Sad when connecting'): left band 3/4 high cut 1/2 : 3/4; right band from the nose edge to x=5.5, cut to (5,0)."]
for i, s_ in enumerate(notes):
    T(s_, (-23.5 * M - 0.5 * M, -1.6 * M - i * 50), 28)
doc.set_modelspace_vport(height=1600, center=(-9 * M, 2.5 * M))
doc.saveas(OUT)

t = ezdxf.readfile(TPL_IN); tm = t.modelspace()
forms = {"tah_isol": (g.tah_isol(), 5.0), "tah_init": (g.tah_init(), 5.0), "tah_medi": (g.tah_medi(), 5.5), "tah_fina": (g.tah_fina(), 5.5)}
for e in tm.query("TEXT"):
    if e.dxf.text not in forms: continue
    poly, xmax = forms[e.dxf.text]
    cx, cy = e.dxf.align_point.x, e.dxf.align_point.y
    x, yb = cx - 500, cy + 90 + 250
    ox = x + 1000 - xmax * M
    for pp in (poly, g.slot()):
        tm.add_lwpolyline([(ox + px * M, yb + py * M, b) for px, py, b in pp], format="xyb", close=True,
                          dxfattribs={"layer": "GLYPHS"})
    print(e.dxf.text, "placed")
t.saveas(TPL_OUT)
