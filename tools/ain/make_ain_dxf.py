import sys, math, importlib.util, ezdxf
from ezdxf.enums import TextEntityAlignment as TA
sp = importlib.util.spec_from_file_location("a", "ain/strict.py"); g = importlib.util.module_from_spec(sp); sp.loader.exec_module(g)
U = 196.0
doc = ezdxf.new("R2018", setup=True); doc.header["$INSUNITS"] = 0; doc.header["$LTSCALE"] = 20
msp = doc.modelspace()
for n, c, lt in [("GRID", 8, "Continuous"), ("HALF", 9, "DASHED"), ("BASELINE", 5, "Continuous"), ("AIN", 7, "Continuous"),
                 ("AIN_FILL", 2, "Continuous"), ("POINTS", 1, "Continuous"), ("ARC_CENTRES", 3, "DASHED"), ("NOTES", 7, "Continuous")]:
    doc.layers.add(n, color=c, linetype=lt)
def T(s, p, h=0.18):
    msp.add_text(s, height=h * U, dxfattribs={"layer": "NOTES", "style": "OpenSans"}).set_placement((p[0] * U, p[1] * U), align=TA.MIDDLE_LEFT)
def form(name, poly, ox, x0, x1, y0, y1, centres=()):
    F = lambda x, y: ((ox + x) * U, y * U)
    k = math.floor(x0 * 2) / 2
    while k <= x1 + 1e-9:
        msp.add_line(F(k, y0), F(k, y1), dxfattribs={"layer": "GRID" if abs(k - round(k)) < 1e-9 else "HALF"}); k += .5
    k = math.floor(y0 * 2) / 2
    while k <= y1 + 1e-9:
        msp.add_line(F(x0, k), F(x1, k), dxfattribs={"layer": "GRID" if abs(k - round(k)) < 1e-9 else "HALF"}); k += .5
    msp.add_line(F(x0 - .3, 0), F(x1 + .3, 0), dxfattribs={"layer": "BASELINE"})
    pts = [(*F(x, y), b) for x, y, b in poly]
    msp.add_lwpolyline(pts, format="xyb", close=True, dxfattribs={"layer": "AIN"})
    h = msp.add_hatch(color=2, dxfattribs={"layer": "AIN_FILL"}); h.paths.add_polyline_path(pts, is_closed=True)
    for x, y, b in poly:
        msp.add_circle(F(x, y), 4, dxfattribs={"layer": "POINTS"})
        T(f"({x:.3f}, {y:.3f})", (ox + x + 0.06, y + 0.06), 0.09)
    for c, r in centres:
        if abs(r) < 4.5:
            msp.add_circle(F(*c), 6, dxfattribs={"layer": "ARC_CENTRES"})
            T(f"c({c[0]:.3f},{c[1]:.3f}) r{r:.3f}", (ox + c[0] + 0.06, c[1] - 0.12), 0.09)
    T(name, (ox + x0, y1 + 0.4), 0.3)
tailc = [(g.C_IU, g.R_IU), (g.C_IL, g.R_IL), (g.C_OT, g.R_OT), (g.C_OL, g.R_OL), (g.C_OU, g.R_OU)]
isolc = [((c[0] + g.ISOL_DX, c[1]), r) for c, r in tailc] + [(g.HOOK_C, g.HOOK_R)]
form("AIN  isol", g.ain_isol(), 0, -1.0, 4.0, -4.5, 3.5, isolc)
form("AIN  init", g.ain_init(), -7, -1.0, 3.5, -0.5, 3.5, [(g.HOOK_C, g.HOOK_R)])
form("AIN  medi", g.ain_medi(), -13, -1.0, 3.0, -1.0, 3.0, [(g.FAN_C, g.FAN_R)])
form("AIN  fina", g.ain_fina(), -19, -0.5, 4.0, -4.5, 3.0, tailc + [(g.FAN_C, g.FAN_R)])
for i, s in enumerate(["AIN / GHAIN - strict construction: straight lines + true circular arcs only (LWPOLYLINE bulges). 1 nuqta = 196 u.",
                       "FAN: chord y=1.5 x 0..2.5, apex (1.25,2.5): centre (1.25,0.219) r 1.281.  Sides 45 deg.  Mouth meets band top at x 0.889 / 1.611.",
                       f"HOOK: K(0,1.5) -> T(1,3) slope 3:2; tip cut 1/2 vertical; inner edge parallel; concave arc to the band (centre ({g.HOOK_C[0]:.3f},{g.HOOK_C[1]:.3f}) r {g.HOOK_R:.3f}).",
                       "TAIL: 3 outer + 3 inner arcs, tangent-continuous.  Outer leftmost (0,-2.5), bottom (1.5,-4); inner leftmost (0.35,-1.9), bottom (1.95,-3.5); tip (3.4,-3.55).",
                       "Fina neck: both 45 deg sides meet at (1,0.5), the tail springs from there.  Isol tail = same tail moved 0.567 left, outer edge meets the hook at the band.",
                       "Bands: H high, 60 deg cuts, same as all letters.  Medi W underside: (0.4,0) (0.8,-0.4) (1.25,0.05) (1.7,-0.4) (2.1,0)."]):
    T(s, (-19.5, -5.6 - i * 0.35), 0.16)
doc.set_modelspace_vport(height=12 * U, center=(-8 * U, -1 * U))
doc.saveas(sys.argv[1])
