import sys, math, ezdxf
from ezdxf.enums import TextEntityAlignment as TA
sys.path.insert(0, sys.argv[3]); import geom as g
OUT, TPL_IN, _, TPL_OUT = sys.argv[1:5]
M = 125.0

doc = ezdxf.new("R2018", setup=True)
doc.header["$INSUNITS"] = 0; doc.header["$LTSCALE"] = 12
msp = doc.modelspace()
for n, c, lt, lw in [("MODULE_GRID", 8, "Continuous", 18), ("HALF_GRID", 9, "DASHED", 0),
                     ("BASELINE", 5, "Continuous", 50), ("TOPLINE", 4, "DASHED", 0),
                     ("SEEN", 7, "Continuous", 35), ("SEEN_FILL", 2, "Continuous", 0),
                     ("SEEN_NARROW", 7, "Continuous", 35), ("POINTS", 1, "Continuous", 0),
                     ("DIMS", 3, "Continuous", 0), ("NOTES", 7, "Continuous", 0)]:
    doc.layers.add(n, color=c, linetype=lt).dxf.lineweight = lw
st = doc.dimstyles.duplicate_entry("EZDXF", "MODULE")
st.dxf.dimtxt = 24; st.dxf.dimasz = 16; st.dxf.dimexe = 10; st.dxf.dimexo = 8; st.dxf.dimgap = 6
st.dxf.dimclrd = 3; st.dxf.dimclre = 3; st.dxf.dimclrt = 3

def T(s, p, h=26, layer="NOTES", al=TA.MIDDLE_LEFT):
    msp.add_text(s, height=h, dxfattribs={"layer": layer, "style": "OpenSans"}).set_placement(p, align=al)

def place(name, poly, ox, oy, x0, x1, y0, y1, layer="SEEN", dims=None):
    F = lambda p: (ox + p[0] * M, oy + p[1] * M)
    k = math.floor(x0 * 2) / 2
    while k <= x1 + 1e-9:
        lay = "MODULE_GRID" if abs(k - round(k)) < 1e-9 else "HALF_GRID"
        msp.add_line(F((k, y0)), F((k, y1)), dxfattribs={"layer": lay}); k += .5
    k = math.floor(y0 * 2) / 2
    while k <= y1 + 1e-9:
        lay = "MODULE_GRID" if abs(k - round(k)) < 1e-9 else "HALF_GRID"
        msp.add_line(F((x0, k)), F((x1, k)), dxfattribs={"layer": lay}); k += .5
    msp.add_line(F((x0 - .3, 0)), F((x1 + .3, 0)), dxfattribs={"layer": "BASELINE"})
    msp.add_line(F((x0, g.TOP)), F((x1, g.TOP)), dxfattribs={"layer": "TOPLINE"})
    pts = [(*F((x, y)), b) for x, y, b in poly]
    msp.add_lwpolyline(pts, format="xyb", close=True, dxfattribs={"layer": layer})
    h = msp.add_hatch(color=2, dxfattribs={"layer": "SEEN_FILL"}); h.paths.add_polyline_path(pts, is_closed=True)
    for x, y, b in poly:
        msp.add_circle(F((x, y)), 4, dxfattribs={"layer": "POINTS"})
    T(name, F((x0, y1 + .6)), 34)
    for a, b, base, ang, txt in (dims or []):
        msp.add_linear_dim(base=F(base), p1=F(a), p2=F(b), angle=ang, text=txt, dimstyle="MODULE",
                           dxfattribs={"layer": "DIMS"}).render()

isol, cinfo, Mi = g.seen_isol()
fina, finfo, Mf = g.seen_fina()
V, P = cinfo["V"], cinfo["P"]
DIM_A = lambda pkx: [((0, g.TOP), (pkx, g.TOP), (0, 3.1), 0, f"{pkx:g}"),
                     ((pkx, g.TOP), (pkx + .5, g.TOP), (0, 3.1), 0, "0.5"),
                     ((pkx + .5, g.TOP), (pkx + .5, 0), (pkx + 1.1, 0), 90, "2.5"),
                     ((0, g.TOP), g.C0, (-0.6, 0), 90, "1/2"),
                     ((1, g.PEN), (1, 0), (1.2, 0), 90, "3/4")]
place("SEEN  isol  (dims: 2 1/2 + 0.5)", isol, 0, 0, -5.5, 3.5, -4.75, 3.0,
      dims=DIM_A(2.5) + [((Mi[0], 0), (Mi[0], -4.5), (3.6, 0), 90, "4.5"),
                         (V, (Mi[0], -4.5), (0, -5.3), 0, "4"),
                         (P, V, (0, -5.3), 0, "2.5"),
                         (P, (P[0], -4.5), (-5.9, 0), 90, "2")])
place("SEEN  init", g.seen_init(), -10.5 * M, 0, -1.0, 3.5, -0.5, 3.0, dims=DIM_A(2.5))
place("SEEN  medi", g.seen_medi(), -17.0 * M, 0, -1.0, 4.0, -1.0, 3.5,
      dims=[((0, g.TOP), g.L, (-0.6, 0), 90, "1.5"), (g.L, (0, 0), (-0.6, 0), 90, "1"),
            ((g.XR - 1, 0), (g.XR, 0), (0, -1.0), 0, "1"), ((3, 3), (3.5, 3), (0, 3.3), 0, "1/2")])
place("SEEN  fina", fina, -23.5 * M, 0, -5.0, 4.0, -4.75, 3.5,
      dims=[((0, g.TOP), g.L, (-0.6, 0), 90, "1.5"), (g.L, (0, 0), (-0.6, 0), 90, "1"),
            ((g.XR - 1, 0), (g.XR, 0), (0, -1.0), 0, "1")])
# narrow variants (follow the drawn width)
place("VARIANT  isol narrow  (as drawn: 2 + 0.5)", g.seen_isol(**g.NARROW)[0], 0, -10 * M, -5.5, 3.0, -4.75, 3.0,
      layer="SEEN_NARROW", dims=DIM_A(2.0))
place("VARIANT  init narrow", g.seen_init(**g.NARROW), -10.5 * M, -10 * M, -1.0, 3.0, -0.5, 3.0,
      layer="SEEN_NARROW", dims=DIM_A(2.0))

notes = ["1 module = 125 units. Baseline y=0. Top line +2.5. Stem top (medi/fina) +3.0. Cup bottom -4.5.",
         "Pen width = 3/4 module (bottom band, connector, cup bottom).  Slot = 3/16 (1/4 pen).  Thin arm = 1/7 pen.",
         "isol/init teeth lean 1:5.  Top = one arc, horizontal at (0,2), through peak (2.5,2.5).  Slots start at x=1 and x=2.",
         "medi/fina teeth lean 5:7 (54.5 deg).  Top = one arc from (0,1) [slope 1:2] to peak (1.75,2.5). Stem 1/2 wide, top 45 deg.",
         "Beak under the stem: 45 deg triangle, 1 wide, 1/2 deep.  Connector cut (init/medi): 1/2 across, 3/4 up.",
         "Cup: arm 4 across : 4.5 down (48.4 deg, sketch says 45).  Wing 2.5 : 2 (38.7 deg, sketch says 40).",
         "Cup bottom rounded r=1/4.  Wing top = arc leaving the tip at slope 1:4.  Same cup for isol (from x=1.25) and fina (from x=1.75)."]
for i, s in enumerate(notes):
    T(s, (-23.5 * M - 5 * M, -16.5 * M - i * 50), 28)
doc.set_modelspace_vport(height=2800, center=(-11 * M, -5 * M))
doc.saveas(OUT)

# ---------- template ----------
t = ezdxf.readfile(TPL_IN); tm = t.modelspace()
forms = {"seen_isol": (isol, 2.985), "seen_init": (g.seen_init(), 2.985),
         "seen_medi": (g.seen_medi(), 3.5), "seen_fina": (fina, 3.5)}
for e in tm.query("TEXT"):
    if e.dxf.text not in forms: continue
    poly, xmax = forms[e.dxf.text]
    cx, cy = e.dxf.align_point.x, e.dxf.align_point.y
    x, yb = cx - 500, cy + 90 + 250
    ox = x + 1000 - xmax * M
    tm.add_lwpolyline([(ox + px * M, yb + py * M, b) for px, py, b in poly], format="xyb", close=True,
                      dxfattribs={"layer": "GLYPHS"})
    print(e.dxf.text, "placed")
t.saveas(TPL_OUT)
