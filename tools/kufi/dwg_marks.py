"""Dots and eyes drawn by the user in the master (circles). A cell may hold several copies of its glyph, each with its
own dots (e.g. the ba cell: one copy for ب, one for ت, one for ث), and also differently shaped copies = alternates
(see dwg_glyphs). Dots are grouped into clusters, every cluster is tied to the nearest copy, and its offset from that
copy is moved onto the canonical (rightmost) copy of the same shape. Keys use the form string with the alternate
suffix, e.g. ("yeh", "fina.alt1") and "ya_fina.alt1"."""
import json, math, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dwg_glyphs
from shapely.geometry import Point
U = 196.0
DOT_LAYERS_EXCLUDE = {"EYES"}
RAW = {}     # circles in cells that are not letters with dots (digits, punctuation): kept as drawn

ROW_RULES = {   # glyph key -> function(cluster_size, below) -> letter name used in build_font
    "ba": lambda n, below: "beh" if (n == 1 and below) else {2: "teh", 3: "theh"}.get(n),
    "hah": lambda n, below: "jeem" if below else "khah",
    "dal": lambda n, b: "thal", "raa": lambda n, b: "zain", "seen": lambda n, b: "sheen", "sad": lambda n, b: "dad",
    "tah": lambda n, b: "zah", "ain": lambda n, b: "ghain", "fa": lambda n, b: "feh", "qaf": lambda n, b: "qaf",
    "nun": lambda n, b: "noon", "ya": lambda n, b: "yeh", "heh": lambda n, b: "tehMarbuta",
}

def load(path):
    ents = json.load(open(path))["entities"]
    cells = dwg_glyphs.cells_of(ents)
    def cell_of(x, y): return next((c for c in cells if c[4] and c[0] <= x <= c[2] and c[1] <= y <= c[3]), None)
    def local(c, x, y): return ((x - c[2]) / U, (y - c[1] - 5 * U) / U)
    shapes = dwg_glyphs.contours_by_label(ents, cells)
    circles = {}
    for e in ents:
        if e["type"] == "CIRCLE":
            c = cell_of(e["center"]["x"], e["center"]["y"])
            if not c: continue
            x, y = local(c, e["center"]["x"], e["center"]["y"])
            circles.setdefault(c[4], []).append((e["layer"], x, y, e["radius"] / U))
    dots, eyes, report = {}, {}, []
    for label, cl in circles.items():
        name, form = label.rsplit("_", 1); key = dwg_glyphs.KEYMAP.get(name, name)
        if name in dwg_glyphs.MULTI_NAMES and name != "allah":       # symbol cell: every circle is part of the glyph
            RAW.setdefault(label, []).extend([(x, y, r) for lay, x, y, r in cl if lay not in DOT_LAYERS_EXCLUDE])
            continue
        if label not in shapes: report.append((label, "circles but no glyph")); continue
        polys, groups = dwg_glyphs.shape_groups(shapes[label])
        copies = [(polys[i], k, polys[g[0]]) for k, g in enumerate(groups) for i in g]    # (copy, alt index, canonical)
        shift = {k: dwg_glyphs.alt_shift(polys, groups, k) for k in range(len(groups))}
        def copy_for(x, y):
            # a dot above the line never belongs to a shape it sits below (e.g. a short form drawn raised in the cell)
            ok = [t for t in copies if not (y > -0.3 and y < t[0].bounds[1] - 0.05)] or copies
            return min(ok, key=lambda t: t[0].distance(Point(x, y)))
        for lay, x, y, r in cl:                                                          # eyes
            if lay == "EYES":
                cp, k, canon = copy_for(x, y); dx = canon.bounds[2] - cp.bounds[2]
                inside = cp.buffer(-r).contains(Point(x, y))
                margin = cp.exterior.distance(Point(x, y)) - r
                eyes.setdefault(f"{key}_{form}{dwg_glyphs.suffix(k)}", []).append((x + dx, y + shift[k], r))
                if not inside or margin < 0.08: report.append((label, "eye", round(margin * U)))
        ds = [(x, y, r) for lay, x, y, r in cl if lay not in DOT_LAYERS_EXCLUDE]           # dots -> clusters
        clusters = []
        for p in ds:
            g = next((g for g in clusters if any(math.dist(p[:2], q[:2]) < (p[2] + q[2]) * 1.45 for q in g)), None)
            (g.append(p) if g else clusters.append([p]))
        for g in clusters:
            gx = sum(p[0] for p in g) / len(g); gy = sum(p[1] for p in g) / len(g)
            cp, k, canon = copy_for(gx, gy); dx = canon.bounds[2] - cp.bounds[2]
            rule = ROW_RULES.get(key); letter = rule(len(g), gy + shift[k] < 0.3) if rule else None
            if not letter:
                RAW.setdefault(f"{key}_{form}{dwg_glyphs.suffix(k)}", []).extend([(p[0] + dx, p[1] + shift[k], p[2]) for p in g])
                if rule: report.append((label, "unassigned cluster", len(g)))
                continue
            gap = min(cp.distance(Point(p[0], p[1])) - p[2] for p in g)
            if gap < 0.08: report.append((label, letter, "dot gap", round(gap * U)))
            dots.setdefault((letter, form + dwg_glyphs.suffix(k)), []).extend([(p[0] + dx, p[1] + shift[k], p[2]) for p in g])
    return dots, eyes, report

def circle(cx, cy, r):           # exact circle: two half-arcs (bulge 1)
    return [(cx - r, cy, -1.0), (cx + r, cy, -1.0)]
