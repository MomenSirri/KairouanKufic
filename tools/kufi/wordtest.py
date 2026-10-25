"""compose words from glyph forms: right glyph's left-join top meets left glyph's right-join top (both at y=H)."""
import os, importlib.util
from PIL import Image, ImageDraw
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(n, rel):
    sp = importlib.util.spec_from_file_location(n, os.path.join(ROOT, rel)); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
S = load("spec", "kufi/spec.py"); H = S.H
sg = load("seen", "seen/geom.py")
def pts_at_H(poly): return [x for x, y, b in poly if abs(y - H) < 0.01]
CUT = S.CUT
def entry_x(poly):   # right-join top: band top-right, or a stem standing on the baseline (seen/sad body B)
    top = max(pts_at_H(poly)); base = max([x for x, y, b in poly if abs(y) < 0.01] or [top])
    return base if base > top + 0.05 else top
def render(words, out, U=60, gap=1.2):
    """words: list of words; word = list of (outer, holes, kind) right->left, kind in isol/init/medi/fina"""
    lines = []
    for w in words:
        placed = []; x = 0.0; prev = None
        for outer, holes, kind in w:
            samp = sg.sample(outer)
            if prev is None:
                ox = -max(p[0] for p in samp)
            elif prev[1] in ("init", "medi") and kind in ("medi", "fina"):
                exit_x = min(pts_at_H(prev[0])) + prev[2]          # previous glyph's left-join top (absolute)
                ox = exit_x - entry_x(outer)
            else:
                ox = prev[3] - gap - max(p[0] for p in samp)
            placed.append((outer, holes, ox)); xmin = ox + min(p[0] for p in samp)
            prev = (outer, kind, ox, xmin)
        lines.append((placed, prev[3]))
    Wd = int(max(-l[1] for l in lines) * U + 80); Ht = int(len(words) * 9.5 * U + 40)
    img = Image.new("RGB", (Wd, Ht), "white"); d = ImageDraw.Draw(img)
    for i, (placed, _) in enumerate(lines):
        base = 40 + (i * 9.5 + 6) * U
        d.line([(0, base), (Wd, base)], fill=(150, 180, 235))
        for outer, holes, ox in placed:
            P = lambda p: (Wd - 40 + (ox + p[0]) * U, base - p[1] * U)
            d.polygon([P(p) for p in sg.sample(outer)], fill="black")
            for h in holes: d.polygon([P(p) for p in sg.sample(h)], fill="white")
    img.save(out)
