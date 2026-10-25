import sys, math, importlib.util, ezdxf
from ezdxf.enums import TextEntityAlignment as TA
sp = importlib.util.spec_from_file_location("a", "fa/strict.py"); g = importlib.util.module_from_spec(sp); sp.loader.exec_module(g)
U = 196.0
doc = ezdxf.new("R2018", setup=True); doc.header["$INSUNITS"] = 0; doc.header["$LTSCALE"] = 20
msp = doc.modelspace()
for n, c, lt in [("GRID", 8, "Continuous"), ("HALF", 9, "DASHED"), ("BASELINE", 5, "Continuous"), ("FA", 7, "Continuous"),
                 ("FA_FILL", 2, "Continuous"), ("POINTS", 1, "Continuous"), ("ARC_CENTRES", 3, "DASHED"), ("NOTES", 7, "Continuous")]:
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
    msp.add_lwpolyline(pts, format="xyb", close=True, dxfattribs={"layer": "FA"})
    h = msp.add_hatch(color=2, dxfattribs={"layer": "FA_FILL"}); h.paths.add_polyline_path(pts, is_closed=True)
    for x, y, b in poly:
        msp.add_circle(F(x, y), 4, dxfattribs={"layer": "POINTS"})
        T(f"({x:.3f}, {y:.3f})", (ox + x + 0.06, y + 0.06), 0.09)
    for c, r in centres:
        if abs(r) < 4.5:
            msp.add_circle(F(*c), 6, dxfattribs={"layer": "ARC_CENTRES"})
            T(f"c({c[0]:.3f},{c[1]:.3f}) r{r:.3f}", (ox + c[0] + 0.06, c[1] - 0.12), 0.09)
    T(name, (ox + x0, y1 + 0.4), 0.3)
form("FA  isol", g.fa_isol(), 0, -5.5, 1.5, -1.0, 3.5)
form("FA / QAF  init", g.fa_init(), -9, -3.5, 1.0, -1.0, 3.5)
form("FA / QAF  medi", g.fa_medi(), -15, -3.5, 1.0, -1.0, 4.0)
form("FA  fina", g.fa_fina(), -22, -5.5, 1.5, -1.0, 3.5)
for i, s_ in enumerate(["FA - strict construction (book p. 24): straight lines + fillet arcs only. 1 nuqta = 196 u.",
    "MEDI: A(-1,3.5) L(-2.5,1.75) R(0,1.75) r 1/4  N(-1,0.875).  Lower-left edge L->(-1.125,0) and notch edge parallel (11:14). Wedge 45/45 to (-0.625,-0.5).",
    "INIT: L(-2.5,1.875) T(-1,2.875) r 0.1  R(0,1.5) r 1/4  N(-0.9,0.75).  Lower-left edge L->(-1.25,0) and notch edge parallel (2:3); wedge right side same slope, left 45.",
    "ISOL: A(-1,3) L(-2.5,1.5); right edge A->(0.25,0) (5:12) rounded r 1/2 into the baseline; lower-left edge to (-1.25,H). Body band from x=-4.5 (5 long, may stretch).",
    "FA and QAF share init and medi (book: الفاء والقاف الأوليان متماثلان). Bands: H high, 60 deg cuts."]):
    T(s_, (-27.5, -2.0 - i * 0.35), 0.16)
doc.set_modelspace_vport(height=12 * U, center=(-11 * U, 1 * U))
doc.saveas(sys.argv[1])
