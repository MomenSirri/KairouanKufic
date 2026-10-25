"""Release: version + names, hinting (ttfautohint, Arabic), WOFF2/WOFF.
usage: python release.py BUILT.ttf 2.100 OUTDIR      -> OUTDIR/ttf/KairouanKufic-Regular.ttf, OUTDIR/webfonts/*.woff2|woff"""
import os, sys
from fontTools.ttLib import TTFont
import ttfautohint
src, ver, out = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(f"{out}/ttf", exist_ok=True); os.makedirs(f"{out}/webfonts", exist_ok=True)
f = TTFont(src)
for rec in f["name"].names:
    if rec.nameID == 5: rec.string = f"Version {ver}"
    if rec.nameID == 3: rec.string = f"{ver};MOMN;KairouanKufic-Regular"
f["head"].fontRevision = float(ver)
tmp = f"{out}/ttf/_unhinted.ttf"; f.save(tmp)
dst = f"{out}/ttf/KairouanKufic-Regular.ttf"
ttfautohint.ttfautohint(in_file=tmp, out_file=dst, default_script="arab", fallback_script="none",
                        hinting_range_min=8, hinting_range_max=50, increase_x_height=0, windows_compatibility=True)
os.remove(tmp)
h = TTFont(dst); assert not [t for t in f.keys() if t not in h.keys()], "hinting dropped a table"
for fl in ("woff2", "woff"):
    w = TTFont(dst); w.flavor = fl; w.save(f"{out}/webfonts/KairouanKufic-Regular.{fl}")
print("release", ver, "->", out)
