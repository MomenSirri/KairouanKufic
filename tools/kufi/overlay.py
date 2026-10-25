from PIL import Image, ImageDraw
def overlay(page, S, items, crop, out, sample):
    im = Image.open(page).convert("RGB"); big = im.resize((int(im.width * S), int(im.height * S)), Image.LANCZOS); d = ImageDraw.Draw(big)
    for poly, (x0, y0, u) in items:
        pts = sample(poly, 20); d.line([((x0 + x * u) * S, (y0 - y * u) * S) for x, y in pts + [pts[0]]], fill=(230, 0, 40), width=3)
    big.crop(tuple(int(c * S) for c in crop)).save(out)
