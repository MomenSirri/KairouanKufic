import sys, math, ezdxf
from ezdxf.enums import TextEntityAlignment as TA
sys.path.insert(0, sys.argv[3])
import geom as g

OUT, TEMPLATE_IN, _, TEMPLATE_OUT = sys.argv[1:5]
M, BASE = 125.0, 1.5

def fu(p, ox=0.0, oy=0.0):
    return (ox + p[0] * M, oy + (p[1] - BASE) * M)

doc = ezdxf.new("R2018", setup=True)
doc.header["$INSUNITS"] = 0; doc.header["$LTSCALE"] = 12
msp = doc.modelspace()
for n, c, lt, lw in [("MODULE_GRID", 8, "Continuous", 18), ("HALF_GRID", 9, "DASHED", 0),
                     ("BASELINE", 5, "Continuous", 50), ("WAW", 7, "Continuous", 35),
                     ("WAW_FILL", 2, "Continuous", 0), ("WAW_DOT_OPTIONAL", 1, "Continuous", 0),
                     ("CONSTRUCTION", 4, "DASHED", 0), ("POINTS", 1, "Continuous", 0),
                     ("DIMS", 3, "Continuous", 0), ("NOTES", 7, "Continuous", 0)]:
    doc.layers.add(n, color=c, linetype=lt).dxf.lineweight = lw
st = doc.dimstyles.duplicate_entry("EZDXF", "MODULE")
st.dxf.dimtxt = 22; st.dxf.dimasz = 16; st.dxf.dimexe = 10; st.dxf.dimexo = 8; st.dxf.dimgap = 6
st.dxf.dimdec = 2; st.dxf.dimclrd = 3; st.dxf.dimclre = 3; st.dxf.dimclrt = 3

def text(s, p, h=24, layer="NOTES", al=TA.MIDDLE_LEFT):
    msp.add_text(s, height=h, dxfattribs={"layer": layer, "style": "OpenSans"}).set_placement(p, align=al)

# grid: x -0.5..3, y 0..4 (sketch frame), half lines dashed
k = -0.5
while k <= 3.0 + 1e-9:
    lay = "MODULE_GRID" if abs(k - round(k)) < 1e-9 else "HALF_GRID"
    msp.add_line(fu((k, -0.25)), fu((k, 4.25)), dxfattribs={"layer": lay}); k += .5
k = 0.0
while k <= 4.0 + 1e-9:
    lay = "MODULE_GRID" if abs(k - round(k)) < 1e-9 else "HALF_GRID"
    msp.add_line(fu((-0.75, k)), fu((3.25, k)), dxfattribs={"layer": lay}); k += .5
msp.add_line(fu((-1.0, BASE)), fu((3.5, BASE)), dxfattribs={"layer": "BASELINE"})
text("baseline  y=0", fu((3.55, BASE)), 22, "BASELINE")

# the letter: closed polyline with arc segments (bulges)
pts = [(*fu(p), b) for p, b in g.POLY]
msp.add_lwpolyline(pts, format="xyb", close=True, dxfattribs={"layer": "WAW"})
h = msp.add_hatch(color=2, dxfattribs={"layer": "WAW_FILL"})
h.paths.add_polyline_path(pts, is_closed=True)
msp.add_circle(fu(g.DOT), M / 16, dxfattribs={"layer": "WAW_DOT_OPTIONAL"})

# construction: chords of the three arcs + 45deg line L-K1 extended
for a, b in [(g.T, g.J), (g.O1, g.A), (g.K2, g.T)]:
    msp.add_line(fu(a), fu(b), dxfattribs={"layer": "CONSTRUCTION"})

for name, p in [("T", g.T), ("J", g.J), ("O1", g.O1), ("A", g.A), ("L", g.L), ("K1", g.K1), ("K2", g.K2)]:
    x, y = fu(p)
    msp.add_circle((x, y), 5, dxfattribs={"layer": "POINTS"})
    dx = -12 if name in ("L", "K1", "K2") else 12
    al = TA.MIDDLE_RIGHT if dx < 0 else TA.MIDDLE_LEFT
    text(f"{name} ({p[0]:g}, {p[1] - BASE:g})", (x + dx, y + 14), 15, "POINTS", al)

def d(a, b, base, angle=0, txt="<>"):
    msp.add_linear_dim(base=fu(base), p1=fu(a), p2=fu(b), angle=angle, text=txt,
                       dimstyle="MODULE", dxfattribs={"layer": "DIMS"}).render()
d((0, 4), g.A, (0, 4.5), txt="1.5")
d(g.A, (2.5, 4), (0, 4.5), txt="1")
d(g.T, (0, 0), (0, -0.4), txt="1/2")
d((2.5, 4), g.O1, (3.3, 0), 90, txt="2")
d(g.O1, g.J, (3.3, 0), 90, txt="1/2")
d(g.J, (2.5, 0), (3.3, 0), 90, txt="1.5")
d((0, 4), g.L, (-0.6, 0), 90, txt="1.5")
d(g.L, (0, 1.5), (-0.6, 0), 90, txt="1")
d(g.K1, g.K2, (1.8, 0), 90, txt="1/4")

text("WAW  -  Kufic, on the module grid", fu((-0.75, 5.0)), 30)
notes = ["1 module = 125 units.  Baseline (y=0) = join line.  Head top +2.5 module, tail tip -1.5 module.",
         "Straight edges: L-A and L-K1 at 45 deg.  Join face O1-J = 1/2 module (same as Raa).",
         "3 arcs, all with the same rule: arc leaves its chord at atan(1/7) = 8.13 deg  (bulge 0.0711):",
         "   T-J outer tail (chord 2 : 1.5, tangent 45 deg at J)   |   K2-T inner tail (tangent 45 deg at T)",
         "   O1-A right edge, concave (chord 1 : 2, tangent 3 : 1 at A)",
         "Layer WAW_DOT_OPTIONAL = the white dot in the sketch (r = 1/16 module). Turn off if not wanted.",
         "Optional softening like the sketch: FILLET  J r=31,  O1 r=31,  K1/K2 hook r=12."]
for i, s in enumerate(notes):
    text(s, fu((-0.75, -0.9 - i * 0.36)), 22)
doc.set_modelspace_vport(height=1600, center=fu((1.4, 1.5)))
doc.saveas(OUT)

# --- add to the running font template ---
t = ezdxf.readfile(TEMPLATE_IN); tm = t.modelspace()
for e in tm.query("TEXT"):
    if e.dxf.text not in ("waw_isol", "waw_fina"): continue
    cx, cy = e.dxf.align_point.x, e.dxf.align_point.y
    x, yb = cx - 500, cy + 90 + 250
    ox = x + 1000 - 2.5 * M if e.dxf.text == "waw_fina" else x + (1000 - 2.5 * M) / 2
    q = [(ox + p[0] * M, yb + (p[1] - BASE) * M, b) for p, b in g.POLY]
    tm.add_lwpolyline(q, format="xyb", close=True, dxfattribs={"layer": "GLYPHS"})
    print(e.dxf.text, "placed")
t.saveas(TEMPLATE_OUT)
