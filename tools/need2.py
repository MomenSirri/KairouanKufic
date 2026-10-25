import sys
FP=sys.argv[1]; sys.argv=['x',FP,'x']
exec(open('pairs2.py').read().split("names=tt.getGlyphOrder()")[0])
names=tt.getGlyphOrder()
L=[n for n in names if (n.endswith('.init') or n.endswith('.medi'))]
R=[n for n in names if n.endswith('.medi') or n.endswith('.fina')]
top=box(-1e6,H+15,1e6,1e6)
def need(a,c):
    Ab=parts(a)[0].intersection(top); Cb0=parts(c)[0].intersection(top)
    for s in range(0,300,4):
        if Ab.distance(affinity.translate(Cb0,-tt['hmtx'][c][0]-s,0))>=0.1*196: return s
    return 300
for side,glyph in [("right of","ain.medi"),("right of","ain.fina"),("left of","ain.medi"),("left of","kaf.init"),("left of","kaf.medi")]:
    if side=="right of": res=[(need(a,glyph),a) for a in L if not a.startswith(('teh','theh','noon','yeh','alefM','yehH','khah','jeem','sheen','dad','zah','ghain','feh'))]
    else: res=[(need(glyph,c),c) for c in R if not c.startswith(('teh','theh','noon','yeh','alefM','yehH','khah','jeem','sheen','dad','zah','ghain','feh','thal','zain','wawH','tehM','lamalefH','lamalefM'))]
    res.sort(reverse=True); print(side,glyph,"max", round(res[0][0]/196,2),"nuqta  worst:",[(round(s/196,2),n) for s,n in res[:4] if s>0])
