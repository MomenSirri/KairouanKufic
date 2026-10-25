# any two glyphs that are NOT joined neighbours must keep a distance (inside words too)
import sys
FP=sys.argv[1]; texts=sys.argv[2].split('|'); sys.argv=['x',FP,'x']
exec(open('coll.py').read().split("words=sys.argv")[0])
from shapely import affinity
joinL=lambda n:('.init' in n) or ('.medi' in n)
tot=0
for t in texts:
    b=hb.Buffer(); b.add_str(t); b.guess_segment_properties(); hb.shape(hf,b,{})
    x=0; it=[]
    for i,p in zip(b.glyph_infos,b.glyph_positions):
        n=hf.glyph_to_string(i.codepoint)
        if n!='space': it.append((n,affinity.translate(shape(n),x+p.x_offset,p.y_offset)))
        x+=p.x_advance
    bad=[]
    for i in range(len(it)):
        for j in range(i+1,len(it)):
            a,c=it[i],it[j]
            if j==i+1 and joinL(c[0]): continue   # visual order: c is to the right of a; joined if c joins left
            d=a[1].distance(c[1])
            if d<25: bad.append((c[0],a[0],round(d)))
    tot+=len(bad); print(t,'|',x,'|',bad)
print('TOTAL',tot)
