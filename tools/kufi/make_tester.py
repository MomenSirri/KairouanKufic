"""tester HTML = template + font (base64) + alternates table. usage: make_tester.py FONT.ttf OUT.html"""
import sys, os, json, base64
HERE = os.path.dirname(os.path.abspath(__file__))
font, out = sys.argv[1], sys.argv[2]
CH = {"yeh": "ي", "alefMaksura": "ى", "yehHamza": "ئ"}
src = open(os.path.join(HERE, "..", "kufi", "build_font.py")).read()
import re
for name, uni in re.findall(r'\("(\w+)", 0x([0-9A-F]{4})', src): CH[name] = chr(int(uni, 16))
alts = {}
p = font + ".alts.json"
if os.path.exists(p):
    for g in json.load(open(p)):
        name, form = g.split(".")
        alts.setdefault(CH[name], []).append(form)
html = open(os.path.join(HERE, "tester_template.html")).read()
from fontTools.ttLib import TTFont
import io
_f = TTFont(font); _f.flavor = "woff2"; _b = io.BytesIO(); _f.save(_b)
html = html.replace("__FONT__", base64.b64encode(_b.getvalue()).decode()).replace("__ALTS__", json.dumps(alts, ensure_ascii=False))
open(out, "w").write(html); print(out, alts)
