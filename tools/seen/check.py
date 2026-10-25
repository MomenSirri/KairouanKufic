import sys; sys.path.insert(0, "seen")
import importlib, geom; importlib.reload(geom)
from PIL import Image, ImageDraw
def draw(src, box, X0, Y0, U, polys, out, S=1):
    im = Image.open(src).convert("RGB").crop(box)
    big = im.resize((int(im.width*S), int(im.height*S)), Image.LANCZOS); d = ImageDraw.Draw(big)
    P = lambda p: ((X0 + p[0]*U - box[0])*S, (Y0 - p[1]*U - box[1])*S)
    for poly in polys:
        pts = geom.sample(poly)
        d.line([P(p) for p in pts + [pts[0]]], fill=(230, 0, 40), width=3)
        for x, y, b in poly:
            px, py = P((x, y)); d.ellipse([px-5, py-5, px+5, py+5], outline=(230, 0, 40), width=2)
    big.save(out)
isol, info, M = geom.seen_isol()
fina, finfo, fM = geom.seen_fina()
draw("seen/s1.png", (0, 150, 2039, 1457), 1480, 691, 145, [isol], "seen/ck_isol.png", S=0.7)
draw("seen/s1.png", (0, 150, 1100, 1457), 309, 691, 145, [fina], "seen/ck_fina.png", S=0.9)
draw("seen/s2.png", (1250, 150, 1993, 649), 1455, 577, 137, [geom.seen_init()], "seen/ck_init.png", S=1.4)
draw("seen/s2.png", (100, 100, 800, 649), 275, 552, 137, [geom.seen_medi()], "seen/ck_medi.png", S=1.4)
print("isol cup", info, "M", M)
