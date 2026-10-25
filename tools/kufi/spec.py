"""Unified Kairouan-Kufic system, from 'قواعد الخط الكوفي القيرواني' (Amer Ben Jeddou), pages 3-6 and 51.
All geometry in NUQTA units (1 = one rhombic dot of the grid, نقطة الميزان)."""
# pen: the dot is a square whose side is the pen width, so pen = dot diagonal / sqrt2 ~ 5/7 (the book uses 5/7)
W = 5 / 7            # pen width (عرض القلم)
V = W * 5 / 7        # vertical stroke  (pen at 45deg)  = 25/49 ~ 0.51
H = W * 6 / 7        # horizontal stroke (pen at 60deg) = 30/49 ~ 0.61
G = W / 7            # fixed gap / hairline (1/7 pen)   =  5/49 ~ 0.10
CUT = W / 2          # 60deg pen cut at a stroke end: across = pen/2, up = H
ALIF = 5.0           # alif height (طول الألف = 5 نقاط)
LINE = 6.5           # baseline to baseline (المسافة بين السطرين = 6.5 نقاط)
# font units: UPM 2048, 1 dot = 196  ->  pen 140, V 100, H 120, gap 20 (all integers)
UPM = 2048
DOT = 196
ASC = 5.5            # highest point (kaf tip)
DESC = -4.5          # lowest point (seen/sad cup)
# letter heights / pen angles from the table on page 51 (for the coming letters)
TABLE = {"ba_init": (2.5, 45), "ba_medi": (2.5, 60), "ba_fina": (2, 60), "jeem": (2.5, 60), "dal": (2.5, 60),
         "seen": (2.5, "40/45"), "ain": (2, 60), "waw_reh": (2, 60), "nun": (1.5, 60), "alif_lam": (None, 60)}
