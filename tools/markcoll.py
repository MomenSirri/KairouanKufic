import sys
FP=sys.argv[1]; texts=sys.argv[2].split('|'); feats={f:True for f in (sys.argv[3].split(',') if len(sys.argv)>3 and sys.argv[3] else [])}
sys.argv=['x',FP,'x']
exec(open('coll.py').read().split("words=sys.argv")[0])
from shapely import affinity
gdef=tt['GDEF'].table.GlyphClassDef.classDefs
tot=0
for t in texts:
    b=hb.Buffer(); b.add_str(t); b.guess_segment_properties(); hb.shape(hf,b,feats)
    x=0; it=[]
    for i,p in zip(b.glyph_infos,b.glyph_positions):
        n=hf.glyph_to_string(i.codepoint); it.append((n,gdef.get(n)==3,affinity.translate(shape(n),x+p.x_offset,p.y_offset))); x+=p.x_advance
    bad=[]
    for k,(n,ism,g) in enumerate(it):
        if not ism or g.is_empty: continue
        for j,(m,ism2,h) in enumerate(it):
            if j==k or h.is_empty: continue
            d=g.distance(h)
            if d<8: bad.append((n,m,round(d)))
    tot+=len(bad); print(t,'|',bad)
print('TOTAL',tot)
