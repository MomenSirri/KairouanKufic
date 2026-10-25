"""Pair kerning for the non-joining letters with a tail that hangs left (reh, zain, waw ...): every letter that can
follow is pulled in as far as it goes without coming closer than CLEAR to the tail, the head or the dots.
Measured on the real outlines, for the next letter inside the word and for the first letter after a space."""
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import affinity

def build(glyphs, MARKS, sample, U, letters, tmax_in=1.5, tmax_space=1.0, clear=0.2, step=0.05, space="space", lefts=None):
    def ink(n):
        ps = [Polygon(sample(c, 8)).buffer(0) for c, ccw in glyphs[n][0] if ccw]
        return unary_union(ps) if ps else Polygon()
    if lefts is None: lefts = [n for n in glyphs if n.split(".")[0] in letters and n.split(".")[-1] in ("isol", "fina")]
    firsts = [n for n in glyphs if n not in MARKS and n not in (space, ".notdef")
              and (n.split(".")[-1] in ("isol", "init") or "." not in n or n.endswith((".isol.alt1",)) or ".init.k" in n)]
    INK = {n: ink(n) for n in set(lefts + firsts)}
    INK = {n: g for n, g in INK.items() if not g.is_empty}
    adv = lambda n: glyphs[n][1]
    sp = adv(space)
    def most(T, F, gap, tmax):
        lo, hi = 0.0, tmax
        if T.distance(affinity.translate(F, -(gap), 0)) < clear: return 0.0
        while hi - lo > step:                   # binary search: largest pull-in that keeps the clearance
            m = (lo + hi) / 2
            if T.distance(affinity.translate(F, -(gap - m), 0)) >= clear: lo = m
            else: hi = m
        return round(lo / step) * step
    pair, ctx, stats = {}, {}, []
    for t in lefts:
        if t not in INK: continue
        for f in firsts:
            if f not in INK: continue
            a = most(INK[t], INK[f], adv(f), tmax_in)
            b = most(INK[t], INK[f], sp + adv(f), tmax_space)
            if a > 0: pair.setdefault((t, round(a * U)), []).append(f)
            if b > 0: ctx.setdefault((t, round(b * U)), []).append(f)
            stats.append((t, f, a, b))
    lines = ["feature kern {", "  lookupflag IgnoreMarks;"]
    for (t, v), fs in sorted(pair.items()): lines.append(f"  enum pos {t} [{' '.join(fs)}] <-{v} 0 -{v} 0>;")   # RTL: move the letter and shorten its advance
    lines.append("} kern;")
    sub = ["feature kern {", "  lookupflag IgnoreMarks;"]
    for (t, v), fs in sorted(ctx.items()): sub.append(f"  pos {t} {space}' -{v} [{' '.join(fs)}];")
    sub.append("} kern;")
    return "\n".join(lines) + "\n" + "\n".join(sub), stats
