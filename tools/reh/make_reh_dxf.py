import sys, math, ezdxf
from ezdxf.enums import TextEntityAlignment as TA
sys.path.insert(0, sys.argv[3])
import geom

OUT, TEMPLATE = sys.argv[1], sys.argv[2]
M = 125.0                     # 1 module = 125 font units (= 1 grid unit of the font template)
BASE = 1.5                    # sketch line y=1.5 (the elbow line) = writing baseline

def fu(p, ox=0.0, oy=0.0):    # module coords -> font units, baseline at 0
    return (ox + p[0] * M, oy + (p[1] - BASE) * M)

doc = ezdxf.new("R2018", setup=True)
doc.header["$INSUNITS"] = 0
doc.header["$LTSCALE"] = 12
doc.header["$DIMSCALE"] = 1
msp = doc.modelspace()
for n, c, lt, lw in [("MODULE_GRID", 8, "Continuous", 18), ("HALF_GRID", 9, "DASHED", 0),
                     ("BASELINE", 5, "Continuous", 50), ("RAA", 7, "Continuous", 35),
                     ("RAA_FILL", 2, "Continuous", 0), ("CONSTRUCTION", 4, "DASHED", 0),
                     ("POINTS", 1, "Continuous", 0), ("DIMS", 3, "Continuous", 0), ("NOTES", 7, "Continuous", 0)]:
    doc.layers.add(n, color=c, linetype=lt).dxf.lineweight = lw

st = doc.dimstyles.duplicate_entry("EZDXF", "MODULE")
st.dxf.dimtxt = 22; st.dxf.dimasz = 16; st.dxf.dimexe = 10; st.dxf.dimexo = 8; st.dxf.dimgap = 6
st.dxf.dimdec = 2; st.dxf.dimclrd = 3; st.dxf.dimclre = 3; st.dxf.dimclrt = 3

def text(s, p, h=26, layer="NOTES", al=TA.MIDDLE_LEFT):
    msp.add_text(s, height=h, dxfattribs={"layer": layer, "style": "OpenSans"}).set_placement(p, align=al)

def grid(ox, oy):
    x0, x1, y0, y1 = -1.0, 2.0, 0.0, 3.0           # sketch frame in modules
    k = x0
    while k <= x1 + 1e-9:
        lay = "MODULE_GRID" if abs(k - round(k)) < 1e-9 else "HALF_GRID"
        msp.add_line(fu((k, y0 - .25), ox, oy), fu((k, y1 + .25), ox, oy), dxfattribs={"layer": lay})
        k += .5
    k = y0
    while k <= y1 + 1e-9:
        lay = "MODULE_GRID" if abs(k - round(k)) < 1e-9 else "HALF_GRID"
        msp.add_line(fu((x0 - .25, k), ox, oy), fu((x1 + .25, k), ox, oy), dxfattribs={"layer": lay})
        k += .5
    msp.add_line(fu((x0 - .5, BASE), ox, oy), fu((x1 + .5, BASE), ox, oy), dxfattribs={"layer": "BASELINE"})
    text("baseline  y=0", fu((x1 + .55, BASE), ox, oy), 22, "BASELINE")

def shape(pts, ox, oy, fill=True):
    q = [fu(p, ox, oy) for p in pts]
    msp.add_lwpolyline(q, close=True, dxfattribs={"layer": "RAA"})
    if fill:
        h = msp.add_hatch(color=2, dxfattribs={"layer": "RAA_FILL"})
        h.paths.add_polyline_path(q, is_closed=True)
    return q

def dims(ox, oy):
    g = geom
    d = lambda a, b, base, angle=0, txt="<>": msp.add_linear_dim(
        base=fu(base, ox, oy), p1=fu(a, ox, oy), p2=fu(b, ox, oy), angle=angle,
        text=txt, dimstyle="MODULE", dxfattribs={"layer": "DIMS"}).render()
    d((0, 3), g.A, (0, 3.45), txt="1/2")
    d(g.A, (1.5, 3), (0, 3.45), txt="1")
    d((1.5, 3), g.O1, (2.25, 0), 90, txt="1")
    d(g.O1, g.O2, (2.25, 0), 90, txt="1/2")
    d(g.O2, (1.5, 0), (2.25, 0), 90, txt="1.5")
    d(g.T, (0, 0), (0, -0.35), txt="1/2")
    msp.add_angular_dim_3p(base=fu((0.35, 0.28), ox, oy), center=fu(g.T, ox, oy), p1=fu((1.5, 0), ox, oy),
                           p2=fu(g.I, ox, oy), dimstyle="MODULE", dxfattribs={"layer": "DIMS"}).render()
    msp.add_angular_dim_3p(base=fu((0.95, 0.2), ox, oy), center=fu(g.T, ox, oy), p1=fu((1.5, 0), ox, oy),
                           p2=fu(g.O2, ox, oy), dimstyle="MODULE", dxfattribs={"layer": "DIMS"}).render()

def points(pts_named, ox, oy):
    for name, p in pts_named:
        x, y = fu(p, ox, oy)
        msp.add_circle((x, y), 5, dxfattribs={"layer": "POINTS"})
        dy = -16 if name == "O2" else 14
        text(f"{name} ({p[0]:g}, {p[1] - BASE:g})", (x + 10, y + dy), 15, "POINTS")

g = geom
# --- sheet 1: as drawn (solid head) ---
OX1, OY1 = 0, 0
grid(OX1, OY1); shape(g.SOLID, OX1, OY1); dims(OX1, OY1)
msp.add_lwpolyline([fu(g.Hs, OX1, OY1), fu(g.H, OX1, OY1), fu(g.A, OX1, OY1)], dxfattribs={"layer": "CONSTRUCTION"})
points([("T", g.T), ("I", g.I), ("Hs", g.Hs), ("A", g.A), ("O1", g.O1), ("O2", g.O2), ("H", g.H)], OX1, OY1)
text("RAA  -  version A  (head as drawn)", fu((-1, 3.9), OX1, OY1), 30)
# --- sheet 2: optional sharp head (dashed version in the sketch) ---
OX2, OY2 = 900, 0
grid(OX2, OY2); shape(g.SHARP, OX2, OY2); dims(OX2, OY2)
points([("T", g.T), ("I", g.I), ("H", g.H), ("A", g.A), ("O1", g.O1), ("O2", g.O2)], OX2, OY2)
text("RAA  -  version B  (dashed head option)", fu((-1, 3.9), OX2, OY2), 30)

notes = ["1 module = 125 units (= 1 cell of the font template).  Half module = 62.5.",
         "Baseline (y=0) = the elbow line.  Descent = 1.5 module (-187.5).  Top = 1.5 module (+187.5).",
         "Inner tail edge T-I = 45 deg (1.5 : 1.5).  Outer tail edge T-O2 = 36.87 deg (1.5 : 2).  Tail axis ~ 41 deg (sketch says 42).",
         "Top limb: both edges at 45 deg, horizontal width 1 module, true thickness 0.707 module.",
         "Join face (O1-O2) = 1/2 module high, at x=1.5, from baseline up.",
         "Optional softening: FILLET outer corner O2 r=31 (1/4 mod), inner elbow I r=12."]
for i, s in enumerate(notes):
    text(s, (-125, -470 - i * 45), 24)
doc.set_modelspace_vport(height=1500, center=(500, 0))
doc.saveas(OUT)

# --- also drop version A into the font template cells reh_isol / reh_fina ---
t = ezdxf.readfile(TEMPLATE)
tm = t.modelspace()
lab = {e.dxf.text: e for e in tm.query("TEXT") if e.dxf.text in ("reh_isol", "reh_fina")}
for slug, e in lab.items():
    cx, cy = e.dxf.align_point.x, e.dxf.align_point.y
    x, yb = cx - 500, cy + 90 + 250                 # cell left edge, baseline
    if slug == "reh_fina": ox = x + 1000 - 1.5 * M  # join face on the right cell edge
    else: ox = x + (1000 - 2 * M) / 2 + 0.5 * M     # centred
    q = [(ox + p[0] * M, yb + (p[1] - BASE) * M) for p in g.SOLID]
    tm.add_lwpolyline(q, close=True, dxfattribs={"layer": "GLYPHS"})
    print(slug, "placed at", round(ox), round(yb))
t.saveas(sys.argv[4])
