import sys, json
FP=sys.argv[1]; sys.argv=['x',FP,'x']
exec(open('coll.py').read().split("words=sys.argv")[0])
from shapely import affinity
from shapely.ops import unary_union
from collections import defaultdict
def parts(g):
    s=shape(g); comps=[s] if s.geom_type=='Polygon' else list(s.geoms)
    body=[q for q in comps if q.area>12000]; dots=[q for q in comps if q.area<=12000]
    return unary_union(body), unary_union(dots) if dots else Polygon()
names=tt.getGlyphOrder()
L=[n for n in names if n.endswith('.init') or n.endswith('.medi')]
R=[n for n in names if n.endswith('.medi') or n.endswith('.fina') or n.endswith('.fina.alt1')]
fam={'beh':'ba','teh':'ba','theh':'ba','noon':'nun','yeh':'ya','alefMaksura':'ya','yehHamza':'ya','jeem':'hah','khah':'hah','sheen':'seen','dad':'sad','zah':'tah','ghain':'ain','feh':'fa','lamalefHamzaBelow':'lamalef','lamalefHamzaAbove':'lamalef','lamalefMadda':'lamalef','thal':'dal','zain':'reh','tehMarbuta':'heh','wawHamza':'waw'}
F=lambda n:fam.get(n.split('.')[0],n.split('.')[0])+'.'+n.split('.',1)[1]
zone=lambda g:g.intersection(box(-1e6,H+15,1e6,1e6)).area+g.intersection(box(-1e6,-1e6,1e6,-15)).area
body,dot=defaultdict(int),defaultdict(set)
for a in L:
    Ab,Ad=parts(a)
    for c in R:
        Cb,Cd=[affinity.translate(q,-tt['hmtx'][c][0],0) for q in parts(c)]
        bb=zone(Ab.intersection(Cb))
        if bb>300: body[(F(a),F(c))]=max(body[(F(a),F(c))],round(bb))
        if not Ad.is_empty and Ad.intersects(Cb.buffer(10)): dot[(a.split('.')[0]+'.'+a.split('.',1)[1])].add(F(c))
        if not Cd.is_empty and Cd.intersects(Ab.buffer(10)): dot[c].add(F(a)+' (before)')
print("BODY collisions (>300 u2):")
for k,v in sorted(body.items(),key=lambda t:-t[1]): print(" ",k,v)
print("DOTS touching the neighbour:")
for k,v in sorted(dot.items()): print(" ",k,sorted(v))
