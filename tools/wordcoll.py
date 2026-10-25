import sys
FP=sys.argv[1]; texts=sys.argv[2].split('|'); sys.argv=['x',FP,'x']
exec(open('coll.py').read().split("words=sys.argv")[0])
from shapely import affinity
tot=0
for t in texts:
    b=hb.Buffer(); b.add_str(t); b.guess_segment_properties(); hb.shape(hf,b,{})
    x=0; w=0; items=[]
    for i,p in zip(b.glyph_infos,b.glyph_positions):
        n=hf.glyph_to_string(i.codepoint)
        if n=='space': w+=1
        else: items.append((w,n,affinity.translate(shape(n),x+p.x_offset,p.y_offset)))
        x+=p.x_advance
    bad=[(a[1],c[1]) for i,a in enumerate(items) for c in items[i+1:] if a[0]!=c[0] and a[2].distance(c[2])<10]
    tot+=len(bad); print(t,'| width',x,'| between-word touches:',bad)
print('TOTAL',tot)
