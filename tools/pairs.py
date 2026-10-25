import sys
FP=sys.argv[1]
sys.argv=[sys.argv[0], FP,'x']
exec(open('coll.py').read().split("words=sys.argv")[0])
from shapely import affinity
names=tt.getGlyphOrder()
L=[n for n in names if n.endswith('.init') or n.endswith('.medi')]          # joins to the left
R=[n for n in names if n.endswith('.medi') or n.endswith('.fina') or n.endswith('.fina.alt1')]  # joins to the right
base=lambda n:n.split('.')[0]
seen_shape={}
gaps, colls = {}, {}
for a in L:
    A=shape(a)
    for c in R:
        advC=tt['hmtx'][c][0]
        C=affinity.translate(shape(c),-advC,0)           # C sits left of A, A starts at x=0
        win=box(-260,12,260,108)
        u=A.union(C).intersection(win)
        n=1 if u.geom_type=='Polygon' else len(u.geoms)
        if n>1: gaps.setdefault((a,c),round(A.intersection(box(-1e6,12,1e6,108)).distance(C.intersection(box(-1e6,12,1e6,108)))))
        ov=A.intersection(C)
        bad=ov.intersection(box(-1e6,H+15,1e6,1e6)).area+ov.intersection(box(-1e6,-1e6,1e6,-15)).area
        if bad>50: colls[(a,c)]=round(bad)
print("pairs",len(L)*len(R))
from collections import defaultdict
def summ(d,label):
    g=defaultdict(list)
    for (a,c),v in d.items(): g[a.split('.',1)[1]+'|'+base(a)].append((c,v))
    print(label,len(d))
    byR=defaultdict(int); byL=defaultdict(int)
    for (a,c) in d: byR[c]+=1; byL[a]+=1
    print("  by right-side glyph (the one before):",sorted(byL.items(),key=lambda t:-t[1])[:15])
    print("  by left-side glyph (the one after):",sorted(byR.items(),key=lambda t:-t[1])[:15])
summ(gaps,"GAPS"); summ(colls,"COLLISIONS")
import json; json.dump({"gaps":[[a,c,v] for (a,c),v in gaps.items()],"colls":[[a,c,v] for (a,c),v in colls.items()]},open(FP+'.pairs.json','w'))
