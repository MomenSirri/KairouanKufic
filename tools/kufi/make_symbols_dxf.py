"""DXF with every digit / punctuation mark in its own master-style cell (13 x 11 nuqta, label '<label>_isol').
Shapes on GLYPHS (closed LWPOLYLINE), dots as CIRCLE on layer 'later' - the same conventions as the letter master."""
import sys, os, math, importlib.util, ezdxf
from ezdxf.enums import TextEntityAlignment as TA
HERE = os.path.dirname(os.path.abspath(__file__))
sp = importlib.util.spec_from_file_location("spec", os.path.join(HERE, "spec.py")); S = importlib.util.module_from_spec(sp); sp.loader.exec_module(S)
sys.path.insert(0, HERE); import symbols
U = S.DOT; CW, CH = 13.0, 11.0; Y0, Y1 = S.DESC - 0.5, S.ASC + 0.5
OUT = sys.argv[1]; R = 0.25
doc = ezdxf.new("R2018", setup=True); doc.header["$INSUNITS"] = 0; doc.header["$LTSCALE"] = 20
msp = doc.modelspace()
for n, c, lt, lw in [("GRID_NUQTA", 8, "Continuous", 18), ("GRID_HALF", 9, "DASHED", 0), ("BASELINE", 5, "Continuous", 50),
                     ("GUIDE_ALIF", 4, "DASHED", 0), ("GUIDE_STROKE", 30, "DASHED", 0), ("CELL", 8, "Continuous", 35),
                     ("LABELS", 7, "Continuous", 0), ("GLYPHS", 7, "Continuous", 35), ("GLYPH_FILL", 2, "Continuous", 0), ("later", 1, "Continuous", 0), ("NOTES", 8, "Continuous", 0)]:
    doc.layers.add(n, color=c, linetype=lt).dxf.lineweight = lw
def L(a, b, layer): msp.add_line(a, b, dxfattribs={"layer": layer})
syms = symbols.make(S, dot_r=R)
for i, (name, unis, label, g) in enumerate(syms):
    cx = -(i % 8) * (CW + 1.0); cy = -(i // 8) * (CH + 1.0) - 20
    F = lambda x, y: ((cx + x) * U, (cy + y) * U)
    msp.add_lwpolyline([F(-CW, Y0), F(0, Y0), F(0, Y1), F(-CW, Y1)], close=True, dxfattribs={"layer": "CELL"})
    msp.add_text(f"{label}_isol", height=0.3 * U, dxfattribs={"layer": "LABELS"}).set_placement(F(-CW + 0.2, Y1 - 0.4), align=TA.MIDDLE_LEFT)
    msp.add_text(" ".join(chr(u) for u in unis[:2]), height=0.8 * U, dxfattribs={"layer": "NOTES"}).set_placement(F(-1.5, Y1 - 1.2), align=TA.MIDDLE_LEFT)
    k = -CW
    while k < -1e-9: L(F(k, Y0), F(k, Y1), "GRID_NUQTA" if abs(k - round(k)) < 1e-9 else "GRID_HALF"); k += .5
    k = math.ceil(Y0 * 2) / 2
    while k < Y1 - 1e-9: L(F(-CW, k), F(0, k), "GRID_NUQTA" if abs(k - round(k)) < 1e-9 else "GRID_HALF"); k += .5
    L(F(-CW - .4, 0), F(.4, 0), "BASELINE"); L(F(-CW, S.ALIF), F(0, S.ALIF), "GUIDE_ALIF"); L(F(-CW, S.H), F(0, S.H), "GUIDE_STROKE")
    ox = -0.5 - g.bounds[2] - 3.0                     # leave room to the right of the shape
    parts = [g] if g.geom_type == "Polygon" else list(g.geoms)
    for p in parts:
        c = p.centroid; rr = math.sqrt(p.area / math.pi)
        if abs(rr - R) < 0.02 and len(p.interiors) == 0 and p.exterior.hausdorff_distance(c.buffer(R, 64).exterior) < 0.02:
            msp.add_circle(F(ox + c.x, c.y), R * U, dxfattribs={"layer": "later"}); continue
        p = p.simplify(0.002)
        msp.add_lwpolyline([F(ox + x, y) for x, y in list(p.exterior.coords)[:-1]], close=True, dxfattribs={"layer": "GLYPHS"})
        for h in p.interiors:
            msp.add_lwpolyline([F(ox + x, y) for x, y in list(h.coords)[:-1]], close=True, dxfattribs={"layer": "GLYPHS"})
doc.saveas(OUT); print(OUT, len(syms), "cells")
