import sys, math, importlib.util, ezdxf
from ezdxf.enums import TextEntityAlignment as TA
from ezdxf.entities.boundary_paths import BoundaryPathType
spec = importlib.util.spec_from_file_location("sad_geom", sys.argv[3]); g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
OUT, TPL_IN, _, TPL_OUT = sys.argv[1:5]
M = 125.0

doc = ezdxf.new("R2018", setup=True)
doc.header["$INSUNITS"] = 0; doc.header["$LTSCALE"] = 12
msp = doc.modelspace()
for n, c, lt, lw in [("MODULE_GRID", 8, "Continuous", 18), ("HALF_GRID", 9, "DASHED", 0),
                     ("BASELINE", 5, "Continuous", 50), ("SAD", 7, "Continuous", 35),
                     ("SAD_FILL", 2, "Continuous", 0), ("POINTS", 1, "Continuous", 0),
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
        msp.add_lwpolyline(pts, format="xyb", close=True, dxfattribs={"layer": "SAD"})
        for x, y, b in pts: msp.add_circle((x, y), 4, dxfattribs={"layer": "POINTS"})
    h = msp.add_hatch(color=2, dxfattribs={"layer": "SAD_FILL"})
    h.paths.add_polyline_path(outer, is_closed=True, flags=1)
    h.paths.add_polyline_path(hole, is_closed=True, flags=16)
    T(name, F((x0, y1 + .6)), 34)
    for a, b, base, ang, txt in dims:
        msp.add_linear_dim(base=F(base), p1=F(a), p2=F(b), angle=ang, text=txt, dimstyle="MODULE",
                           dxfattribs={"layer": "DIMS"}).render()

XN, B = g.XN, g.BODY
HEAD = [((0, 2), (0.75, 2), (0, 2.5), 0, "3/4"), ((0.75, B), (XN, B), (0, 2.5), 0, "4"),
        ((0, 2), (0, B), (-0.7, 0), 90, "1/2"), ((0, B), (0, 0), (-0.7, 0), 90, "1.5")]
NOSE = [((XN, 0), (XN + .5, .75), (0, -0.8), 0, "1/2")]
CONN_R = [((XN, 0), (XN + .5, .75), (0, -0.8), 0, "1/2"), ((XN + .5, .75), (XN + 1.25, .75), (0, -0.8), 0, "3/4")]
CONN_L = [((-1, 0), (-0.5, .75), (0, -0.8), 0, "1/2")]
isol, info = g.sad_isol(); fina, _ = g.sad_fina()
V, P = info["V"], info["P"]; Mc = g.M_CUP
CUP = [((Mc[0], 0), (XN, 0), (0, -0.8), 0, "3 1/2"), ((Mc[0], 0), (Mc[0], -4.5), (6.0, 0), 90, "4 1/2"),
       (V, (Mc[0], -4.5), (0, -5.3), 0, "4"), (P, V, (0, -5.3), 0, "2 1/2"), (P, (P[0], -4.5), (-5.9, 0), 90, "2")]
place("SAD  isol", isol, 0, 0, -5.5, 5.5, -4.75, 2.5, HEAD + NOSE + CUP)
place("SAD  init", g.sad_init(), -13.0 * M, 0, -1.5, 5.5, -1.0, 2.5, HEAD + NOSE + CONN_L)
place("SAD  medi", g.sad_medi(), -23.0 * M, 0, -1.5, 6.5, -1.0, 2.5, HEAD + CONN_R + CONN_L)
place("SAD  fina", fina, -34.5 * M, 0, -5.5, 6.5, -4.75, 2.5, HEAD + CONN_R + CUP[:1])

notes = ["1 module = 125 units.  Baseline y=0.  Body = 2 pens = 1.5 high.  Head tip +2.0.  Cup bottom -4.5.",
         "Head: 3/4 wide, rises 1/2, tip at x=1/2.  Left edge 1:4 (76 deg, sketch 75), down to -1/2 where the cup arm joins.",
         "Body length after the head = 4 (the book: may be stretched or shortened when needed - move the right part only).",
         "Nose: 1/2 out to the mid height (0.75).  Right connector (medi/fina): 3/4 more, cut 1/2 : 3/4.  Left connector (init/medi): same cut.",
         "Slot (counter) = 1/7 pen thick, centred on y=0.75, from x=1 to x=4.25, right end cut 45 deg.  It is a separate closed polyline (hole).",
         "Cup = identical to the Seen cup (arm 4 : 4.5, wing 2.5 : 2, bottom r=1/4).  The book allows the arm up to 1/4 pen; here 1/7 like the Seen."]
for i, s in enumerate(notes):
    T(s, (-34.5 * M - 5.5 * M, -6.5 * M - i * 50), 28)
doc.set_modelspace_vport(height=2200, center=(-17 * M, -1.5 * M))
doc.saveas(OUT)

t = ezdxf.readfile(TPL_IN); tm = t.modelspace()
forms = {"sad_isol": (isol, XN + .5), "sad_init": (g.sad_init(), XN + .5),
         "sad_medi": (g.sad_medi(), XN + 1.25), "sad_fina": (fina, XN + 1.25)}
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
