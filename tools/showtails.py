import sys
from PIL import Image, ImageDraw, ImageFont
import uharfbuzz as hb
from shapely import affinity
import os
FEAT={f:True for f in os.environ.get("FEAT","").split(",") if f}
texts=sys.argv[1].split('|'); out=sys.argv[2]; fonts=sys.argv[3:]
SC=float(os.environ.get("SC","0.055")); LH=int(2600*SC)
L=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20)
shaped=[]
for fp in fonts:
    sys.argv=['x',fp,'x']; ns={}
    exec(open('coll.py').read().split("words=sys.argv")[0], ns)
    rows=[]
    for t in texts:
        b=hb.Buffer(); b.add_str(t); b.guess_segment_properties(); hb.shape(ns["hf"],b,FEAT)
        x=0; it=[]
        for i,p in zip(b.glyph_infos,b.glyph_positions):
            n=ns['hf'].glyph_to_string(i.codepoint)
            if n!='space': it.append((n,affinity.translate(ns['shape'](n),x+p.x_offset,p.y_offset)))
            x+=p.x_advance
        rows.append((it,x))
    shaped.append((fp,rows))
Wd=int(max(r[1] for _,rows in shaped for r in rows)*SC)+60
im=Image.new('RGB',(Wd*len(fonts)+20*(len(fonts)-1),len(texts)*LH+50),'white'); d=ImageDraw.Draw(im)
for k,(fp,rows) in enumerate(shaped):
    X0=(len(fonts)-1-k)*(Wd+20)
    lab=fp.split('-')[-1].replace('.ttf','')
    d.text((X0+10,8),lab+('  (red = short form chosen automatically)' if k==len(fonts)-1 else ''),font=L,fill='#555')
    for r,(it,tot) in enumerate(rows):
        oy=50+r*LH+int(1350*SC)
        T=lambda pt:(X0+Wd-30-(tot-pt[0])*SC, oy-pt[1]*SC)
        d.text((X0+10,oy-20),f"{tot/196:.1f} nuqta",font=L,fill='#aaa')
        for n,g in it:
            col='#d23a1f' if n.endswith('.alt1') else '#1d1a14'
            for q in ([g] if g.geom_type=='Polygon' else list(g.geoms)):
                if q.is_empty: continue
                d.polygon([T(p) for p in q.exterior.coords],fill=col)
                for h in q.interiors: d.polygon([T(p) for p in h.coords],fill='white')
im.save(out); print(im.size)
