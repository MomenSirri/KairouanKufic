"""Read glyphs back from the user's edited master (DWG -> JSON via libredwg). One cell = one glyph form.
Every closed LWPOLYLINE inside a cell (any layer except the template layers) becomes a contour.
  - top-level shapes (not inside another shape) are glyph copies; shapes inside a copy are its holes
  - congruent copies (same size and outline, e.g. the ba cell drawn three times for different dots) are ONE glyph
  - a copy with a different outline is an ALTERNATE: the rightmost shape is the default (key "ya_fina"),
    the next one to its left "ya_fina.alt1", then ".alt2" ...
Units -> nuqta, y relative to the cell's baseline, x relative to the cell's right edge."""
import json, math
from shapely.geometry import Polygon
U = 196.0
TEMPLATE = {"CELL", "SPEC", "NA", "GLYPH_FILL", "SPEC_FILL", "GRID_NUQTA", "GRID_HALF", "BASELINE", "GUIDE_ALIF", "GUIDE_STROKE", "LABELS"}
KEYMAP = {"jeem": "hah", "lam-alif": "lamalif"}

def _sample(vs):
    pts = []; n = len(vs)
    for i in range(n):
        x0, y0, b = vs[i]; x1, y1, _ = vs[(i + 1) % n]
        if abs(b) < 1e-9: pts.append((x0, y0)); continue
        th = 4 * math.atan(b); ch = math.dist((x0, y0), (x1, y1))
        if ch == 0: continue
        R = ch / (2 * math.sin(th / 2)); mx, my = (x0 + x1) / 2, (y0 + y1) / 2; dx, dy = (x1 - x0) / ch, (y1 - y0) / ch
        h = R * math.cos(th / 2); cx, cy = mx - dy * h, my + dx * h; a0 = math.atan2(y0 - cy, x0 - cx)
        pts += [(cx + abs(R) * math.cos(a0 + th * k / 12), cy + abs(R) * math.sin(a0 + th * k / 12)) for k in range(12)]
    return pts

def cells_of(ents):
    cells = []
    for e in ents:
        if e["type"] == "LWPOLYLINE" and e["layer"] == "CELL":
            xs = [v["x"] for v in e["vertices"]]; ys = [v["y"] for v in e["vertices"]]
            cells.append([min(xs), min(ys), max(xs), max(ys), None])
    for e in ents:
        if e["type"] == "TEXT" and e["layer"] == "LABELS":
            p = e.get("startPoint") or {}
            for c in cells:
                if c[0] <= p.get("x", 1e9) <= c[2] and c[1] <= p.get("y", 1e9) <= c[3]: c[4] = e["text"]
    # a drawn cell without a label: the first one is the Allah ligature (الله), any further ones are reported
    k = 0
    for c in cells:
        if c[4]: continue
        has = any(e["type"] == "LWPOLYLINE" and e["layer"] not in TEMPLATE and
                  c[0] <= e["vertices"][0]["x"] <= c[2] and c[1] <= e["vertices"][0]["y"] <= c[3] for e in ents)
        if has:
            c[4] = "allah_isol" if k == 0 else f"unlabelled{k}_isol"; k += 1
    return cells

def _chains(ents):
    """closed outlines drawn as loose LINE/ARC pieces (exploded polylines) -> vertex lists (x, y, bulge), drawing units."""
    segs = []
    for e in ents:
        if e["layer"] in TEMPLATE: continue
        if e["type"] == "LINE":
            a, b = e["startPoint"], e["endPoint"]
            if math.dist((a["x"], a["y"]), (b["x"], b["y"])) > 0.5: segs.append([(a["x"], a["y"]), (b["x"], b["y"]), 0.0])
        elif e["type"] == "ARC":
            c, r, a0, a1 = e["center"], e["radius"], e["startAngle"], e["endAngle"]
            th = (a1 - a0) % (2 * math.pi)
            segs.append([(c["x"] + r * math.cos(a0), c["y"] + r * math.sin(a0)), (c["x"] + r * math.cos(a1), c["y"] + r * math.sin(a1)), math.tan(th / 4)])
    out, used = [], [False] * len(segs)
    for i in range(len(segs)):
        if used[i]: continue
        used[i] = True; chain = [segs[i]]
        while math.dist(chain[-1][1], chain[0][0]) > 0.5:
            end = chain[-1][1]
            j = next((j for j in range(len(segs)) if not used[j] and (math.dist(segs[j][0], end) < 0.5 or math.dist(segs[j][1], end) < 0.5)), None)
            if j is None: break
            used[j] = True; a, b, bu = segs[j]
            chain.append([a, b, bu] if math.dist(a, end) < 0.5 else [b, a, -bu])
        if len(chain) >= 3 and math.dist(chain[-1][1], chain[0][0]) < 0.5:
            out.append([(a[0], a[1], bu) for a, b, bu in chain])
    return out

def contours_by_label(ents, cells):
    """label -> list of contours (cell-local nuqta vertices)."""
    out = {}
    for vs in _chains(ents):
        rp = Polygon(_sample(vs)).buffer(0).representative_point()
        cell = next((c for c in cells if c[0] <= rp.x <= c[2] and c[1] <= rp.y <= c[3] and c[4]), None)
        if cell:
            base = cell[1] + 5 * U
            out.setdefault(cell[4], []).append([((x - cell[2]) / U, (y - base) / U, b) for x, y, b in vs])
    for e in ents:
        if e["type"] != "LWPOLYLINE" or e["layer"] in TEMPLATE or len(e["vertices"]) < 3: continue
        v0, v1 = e["vertices"][0], e["vertices"][-1]
        ends_meet = math.dist((v0["x"], v0["y"]), (v1["x"], v1["y"])) < 0.5
        if not (e["flag"] & 512 or e["flag"] & 1 or ends_meet): continue     # drawn closed even if the Closed flag is off
        raw = [(v["x"], v["y"], v.get("bulge", 0) or 0) for v in e["vertices"]]
        clean = []                                          # drop repeated vertices
        for v in raw:
            if clean and math.dist(v[:2], clean[-1][:2]) < 0.5: continue
            clean.append(v)
        if math.dist(clean[0][:2], clean[-1][:2]) < 0.5: clean.pop()
        if len(clean) < 2: continue
        rp = Polygon(_sample(clean)).buffer(0).representative_point()
        cell = next((c for c in cells if c[0] <= rp.x <= c[2] and c[1] <= rp.y <= c[3] and c[4]), None)
        if not cell: continue
        base = cell[1] + 5 * U
        out.setdefault(cell[4], []).append([((x - cell[2]) / U, (y - base) / U, b) for x, y, b in clean])
    return out

def _same(p, q, tol=0.06):
    """congruent up to a shift: same area, same box size, and the outlines overlap once boxes are aligned."""
    from shapely import affinity
    if abs(p.area - q.area) > 0.02 * max(p.area, q.area): return False
    (a0, b0, a1, b1), (c0, d0, c1, d1) = p.bounds, q.bounds
    if abs((a1 - a0) - (c1 - c0)) > tol or abs((b1 - b0) - (d1 - d0)) > tol: return False
    q2 = affinity.translate(q, a0 - c0, b0 - d0)
    return p.symmetric_difference(q2).area < 0.03 * p.area

def shape_groups(contours):
    """-> (polys, groups). groups: list of lists of copy indices, rightmost group first; each group's own copies
    rightmost first. Holes are found later by containment."""
    polys = [Polygon(_sample(c)).buffer(0) for c in contours]
    top = [i for i, p in enumerate(polys)
           if not any(j != i and polys[j].area > p.area and polys[j].contains(p.representative_point()) for j in range(len(polys)))]
    top.sort(key=lambda i: -polys[i].bounds[2])
    groups = []
    for i in top:
        g = next((g for g in groups if _same(polys[g[0]], polys[i])), None)
        (g.append(i) if g else groups.append([i]))
    return polys, groups

def suffix(k): return "" if k == 0 else f".alt{k}"

def alt_shift(polys, groups, k):
    """an alternate drawn floating above the line (to fit in the cell) is dropped back onto the baseline."""
    y0 = polys[groups[k][0]].bounds[1]
    return -y0 if k > 0 and y0 > 0.3 else 0.0
FLOATED = []
MULTI_NAMES = {"allah"}
MULTI = {}

def load(path):
    ents = json.load(open(path))["entities"]
    cells = cells_of(ents)
    glyphs = {}
    for label, contours in contours_by_label(ents, cells).items():
        name, form = label.rsplit("_", 1); key = f"{KEYMAP.get(name, name)}_{form}"
        if name in MULTI_NAMES:            # one glyph made of several separate shapes (الله): keep them all
            polys, groups = shape_groups(contours)
            tops = [i for g in groups for i in g]            # every piece, also identical ones (" « :)
            MULTI[name] = [(contours[i], polys[i].bounds) for i in tops], \
                          [contours[j] for j in range(len(contours)) if j not in tops and any(polys[i].contains(polys[j].representative_point()) for i in tops)]
            continue
        polys, groups = shape_groups(contours)
        for k, g in enumerate(groups):
            i0 = g[0]
            holes = [contours[j] for j in range(len(contours))
                     if j != i0 and polys[j].area < polys[i0].area and polys[i0].contains(polys[j].representative_point())]
            dy = alt_shift(polys, groups, k)
            if dy: FLOATED.append((key + suffix(k), round(-dy, 2)))
            mv = lambda c: [(x, y + dy, b) for x, y, b in c]
            glyphs[key + suffix(k)] = (mv(contours[i0]), [mv(h) for h in holes], form)
    return glyphs
