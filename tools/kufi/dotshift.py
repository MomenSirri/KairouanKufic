"""Dots that touch the next (tall) letter: a variant of the dotted letter with its dots moved toward itself
(right), used only before the letters it would touch (calt). The user's dot placement stays everywhere else."""
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import affinity

def build(glyphs, sample, orient, clear=0.12, step=0.05, max_dx=0.8):
    def is_dot(c): return len(c) == 2 and all(abs(abs(b) - 1) < 1e-6 for _, _, b in c)
    def ink(cs): ps = [Polygon(sample(c, 8)).buffer(0) for c, ccw in cs if ccw]; return unary_union(ps) if ps else Polygon()
    lefts = [n for n in glyphs if n.endswith((".init", ".medi")) and any(is_dot(c) for c, _ in glyphs[n][0])]
    rights = [n for n in glyphs if n.endswith((".medi", ".fina"))]
    BODY = {n: ink([(c, k) for c, k in glyphs[n][0] if not is_dot(c)]) for n in set(lefts + rights)}
    rules, made = {}, {}
    for a in lefts:
        cs = glyphs[a][0]
        dots = unary_union([Polygon(sample(c, 8)).buffer(0) for c, k in cs if is_dot(c)])
        own = BODY[a]
        for f in rights:
            F = affinity.translate(BODY[f], -glyphs[f][1], 0)
            if dots.distance(F) >= clear: continue
            own0 = min(dots.distance(own), 0.08)
            best = None                       # smallest move (right and/or up) that clears the next letter
            for i in range(0, int(max_dx / step) + 1):
                for j in range(0, int(max_dx / step) + 1):
                    dx, dy = i * step, j * step
                    if best and dx * dx + dy * dy >= best[0]: continue
                    m = affinity.translate(dots, dx, dy)
                    if m.distance(F) >= clear and m.distance(own) >= own0 - 1e-6:
                        best = (dx * dx + dy * dy, round(dx, 2), round(dy, 2))
            if not best: continue
            _, dx, dy = best
            name = f"{a}.d{int(round(dx * 100))}u{int(round(dy * 100))}"
            if name not in made:
                made[name] = ([([(x + dx, y + dy, b) for x, y, b in c] if is_dot(c) else c, k) for c, k in cs], glyphs[a][1])
            rules.setdefault((a, name), []).append(f)
    glyphs.update(made)
    if not rules: return "", 0
    lines = ["feature calt {", "  lookupflag IgnoreMarks;"]
    for (a, name), fs in sorted(rules.items()): lines.append(f"  sub {a}' [{' '.join(fs)}] by {name};")
    lines.append("} calt;")
    return "\n".join(lines), len(made)
