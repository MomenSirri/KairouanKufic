"""Short (tail-less) forms for the letters with a long descending tail, and the automatic choice between long and short.

Short forms (only made when the master has no hand-drawn alternate for that cell):
  nun  isol/fina  = the ba  isol/fina shape (the early-Kufic flat nun; the dot makes it a nun)
  qaf  isol/fina  = the fa  isol/fina shape (the early-Kufic flat qaf; the two dots make it a qaf)
  seen, sad isol/fina = the drawn head, tail removed at the baseline, band continued EXT to the left and
                        closed with the ba's upturned end
  ya   isol       = the drawn head and its lower band, tail removed
Automatic choice (calt): a long tail goes under the next word; if it would touch any of the next word's first
three letters (with a clearance), the short form is used instead. Checked on the real outlines."""
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
from shapely import affinity

EXT = 1.25          # band continued left of the head (nuqta)
CAP = 0.75          # width of the ba's upturned end taken as the cap
CLEAR = 0.15        # clearance tail <-> next word (nuqta)
ZONE = 0.3          # a tail may not enter the hull of anything the next word hangs below the line (+ this margin)
DEEP = -0.25        # "below the line" starts here (dots under ba/ya sit higher than any tail passes)

def _poly(vs, sample): return Polygon(sample(vs, 8)).buffer(0)
def _verts(g):
    if g.geom_type == "MultiPolygon": g = max(g.geoms, key=lambda p: p.area)
    g = g.simplify(0.002)
    return [(x, y, 0) for x, y in list(g.exterior.coords)[:-1]]

def _headless_tail(GS, key, H, sample, cap_src):
    outer, holes, form = GS[key]
    P = _poly(outer, sample)
    body = P.intersection(box(-50, 0, 50, 50))
    if body.geom_type == "MultiPolygon": body = max(body.geoms, key=lambda p: p.area)
    xl = body.intersection(box(-50, 0, 50, H)).bounds[0]
    C = _poly(GS[cap_src][0], sample); cx0 = C.bounds[0]
    cap = affinity.translate(C.intersection(box(cx0 - 1, -1, cx0 + CAP, 50)), (xl - EXT) - (cx0 + CAP), 0)
    band = box(xl - EXT - 0.05, 0, xl + 0.3, H)
    return _verts(unary_union([body, band, cap])), [h for h in holes if _poly(h, sample).centroid.y > 0], form

def _ya_isol(GS, key, sample):
    outer, holes, form = GS[key]
    P = _poly(outer, sample).intersection(box(-50, -0.75, 50, 50))
    return _verts(P), holes, form

def make(GS, EYES, H, sample, log=print):
    made = []
    def put(key, val, eyes_from=None):
        if f"{key}.alt1" in GS or key not in GS: return
        GS[f"{key}.alt1"] = val; made.append(key)
        if eyes_from and eyes_from in EYES: EYES[f"{key}.alt1"] = EYES[eyes_from]
    for f in ("isol", "fina"):
        if f"ba_{f}" in GS: put(f"nun_{f}", (GS[f"ba_{f}"][0], GS[f"ba_{f}"][1], f), f"ba_{f}")
        if f"fa_{f}" in GS: put(f"qaf_{f}", (GS[f"fa_{f}"][0], GS[f"fa_{f}"][1], f), f"fa_{f}")
        for b in ("seen", "sad"):
            if f"{b}_{f}" in GS: put(f"{b}_{f}", _headless_tail(GS, f"{b}_{f}", H, sample, "ba_isol"), f"{b}_{f}")
    if "ya_isol" in GS: put("ya_isol", _ya_isol(GS, "ya_isol", sample), "ya_isol")
    log(f"short forms made: {made}")
    return made

def calt(glyphs, ALTS, MARKS, sample, space="space"):
    """-> feature text. glyphs: name -> (contours [(verts, ccw)], advance) in nuqta, x from the glyph origin."""
    def ink(n):
        cs = glyphs[n][0]
        ps = [Polygon(sample(c, 8)).buffer(0) for c, ccw in cs if ccw]
        return unary_union(ps) if ps else Polygon()
    base = [n for n in glyphs if n not in MARKS and n not in (space, ".notdef") and not n.endswith(".alt1")]
    first = [n for n in base if n.endswith((".isol", ".init")) or "." not in n]
    letters = [n for n in base if n.split(".")[-1] in ("isol", "init", "medi", "fina")]
    INK = {n: ink(n) for n in base + [a for v in ALTS.values() for a in v]}
    def keep(g):     # the next word's no-go area: its ink + clearance, and the hull of what hangs below the line
        low = g.intersection(box(-50, -50, 50, DEEP))
        return g.buffer(CLEAR).union(low.convex_hull.buffer(ZONE)) if not low.is_empty else g.buffer(CLEAR)
    KEEP = {n: keep(INK[n]) for n in INK}
    adv = lambda n: glyphs[n][1]
    sp = adv(space)
    minA = min(adv(n) for n in letters if adv(n) > 0.3)
    rules = []
    tails = [t for t in ALTS if t.split(".")[-1] in ("isol", "fina")]
    for t in tails:
        T = INK[t]
        hit = lambda n, off: T.intersects(affinity.translate(KEEP[n], off, 0))
        p1 = [n for n in first if hit(n, -(sp + adv(n)))]
        p2 = [n for n in letters if hit(n, -(sp + minA + adv(n)))]
        p3 = [n for n in letters if hit(n, -(sp + 2 * minA + adv(n)))]
        alt = ALTS[t][0]
        if p1: rules.append(f"  sub {t}' {space} [{' '.join(p1)}] by {alt};")
        if p2: rules.append(f"  sub {t}' {space} @ANY [{' '.join(p2)}] by {alt};")
        if p3: rules.append(f"  sub {t}' {space} @ANY @ANY [{' '.join(p3)}] by {alt};")
    if not rules: return ""
    return (f"@ANY = [{' '.join(base)}];\nfeature calt {{\n  lookupflag IgnoreMarks;\n" + "\n".join(rules) + "\n} calt;")
