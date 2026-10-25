import sys
from PIL import Image, ImageDraw
def overlay(src, box, X0, Y0, U, out, S=2, half=True):
    im = Image.open(src).convert("RGB").crop(box)
    big = im.resize((im.width*S, im.height*S), Image.LANCZOS); d = ImageDraw.Draw(big)
    step = U/2 if half else U
    x0, y0 = (X0-box[0])*S, (Y0-box[1])*S
    k = -40
    while k < 40:
        x = x0 + k*step*S
        if 0 <= x <= big.width: d.line([(x,0),(x,big.height)], fill=(0,150,255) if k%2==0 else (150,210,255), width=1)
        y = y0 - k*step*S
        if 0 <= y <= big.height: d.line([(0,y),(big.width,y)], fill=(0,150,255) if k%2==0 else (150,210,255), width=1)
        k += 1
    big.save(out)
