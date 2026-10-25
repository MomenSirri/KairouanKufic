"""Kufic TAH (also the shape of KAF in this book). Module units, baseline 0, x=0 = left line.
Outer contour clockwise; slot separate, counter-clockwise. vertex = (x, y, bulge)."""
import os, math, importlib.util
_spec = importlib.util.spec_from_file_location("seen_geom", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "seen", "geom.py"))
sg = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(sg)

PEN = sg.PEN                      # 3/4
ARM = sg.SLOT                     # thin stem = 1/7 pen (labelled)
S = ARM * math.sqrt(2)            # horizontal width of the 45deg stem (0.1515)
BODY = 2 * PEN + sg.SLOT          # unified body: two horizontal strokes + gap
TIP = (3.0, 5.0)                  # top tip
W = 0.5                           # top stroke: left edge = right edge shifted 1/2 left
CUT_Y = 4.375                     # tip cut meets the left edge 5/8 below the top (book's horizontal line)
XB = 4.5                          # body top-right corner
NOSE = (5.0, BODY / 2)
NOSE_B = (4.75, 0.0)
SLOT_R = 4.25

def rx(y): return TIP[0] + (TIP[1] - y) / 3          # right edge of top stroke (1:3, 71.6 deg)
def lx(y): return rx(y) - W                           # left edge

IE_Y = (lx(0) + 0) / (1 + 1 / 3)                      # x=y meets left edge
IE = (IE_Y, IE_Y)                                     # inner elbow (3.125, 3.125)
OE_Y = (rx(0) - S) / (1 + 1 / 3)                      # x=y+S meets right edge
OE = (OE_Y + S, OE_Y)                                 # outer elbow (~3.54, 3.39)
Q = (lx(CUT_Y), CUT_Y)                                # tip cut point (2.708, 4.375)
STEM_FOOT = (BODY + S, BODY)                          # stem meets body top

def slot():
    t = sg.SLOT; y0, y1 = PEN, PEN + t
    return [(y0 + S, y0, 0), (SLOT_R, y0, 0), (SLOT_R - t, y1, 0), (y1 + S, y1, 0)]

def _upper():   # from the wedge, up the stem, round the head, down to the body top
    return [(*IE, 0), (*Q, 0), (*TIP, 0), (*OE, 0), (*STEM_FOOT, 0), (XB, BODY, 0)]

def _nose():    return [(*NOSE, 0), (*NOSE_B, 0)]
def _conn_r():  # like the Sad: nose edge down to pen height, band 3/4... cut 1/2 : 3/4
    xp = XB + (BODY - PEN) * (NOSE[0] - XB) / (BODY - NOSE[1])
    return [(xp, PEN, 0), (5.5, PEN, 0), (5.5 - sg.CUT, 0.0, 0)]
def _wedge():   return [(0.0, 0.0, 0)]
def _conn_l():  return [(-sg.CUT, 0.0, 0), (0.0, PEN, 0), (PEN, PEN, 0)]   # band like the Sad, wedge starts at (3/4,3/4)

def tah_isol(): return _wedge() + _upper() + _nose()
def tah_init(): return _conn_l() + _upper() + _nose()
def tah_medi(): return _conn_l() + _upper() + _conn_r()
def tah_fina(): return _wedge() + _upper() + _conn_r()
sample = sg.sample
