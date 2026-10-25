import sys, uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.basePen import BasePen
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
fp=sys.argv[1]; tt=TTFont(fp); gs=tt.getGlyphSet()
class P(BasePen):
    def __init__(s): super().__init__(gs); s.c=[]; s.cur=[]
    def _moveTo(s,p): s.cur=[p]
    def _lineTo(s,p): s.cur.append(p)
    def _curveToOne(s,a,b,c):
        p0=s.cur[-1]
        for t in [i/8 for i in range(1,9)]:
            s.cur.append(tuple((1-t)**3*p0[k]+3*(1-t)**2*t*a[k]+3*(1-t)*t*t*b[k]+t**3*c[k] for k in (0,1)))
    def _qCurveToOne(s,a,b):
        p0=s.cur[-1]
        for t in [i/6 for i in range(1,7)]:
            s.cur.append(tuple((1-t)**2*p0[k]+2*(1-t)*t*a[k]+t*t*b[k] for k in (0,1)))
    def _closePath(s):
        if len(s.cur)>2: s.c.append(s.cur)
        s.cur=[]
cache={}
def shape(g):
    if g not in cache:
        p=P(); gs[g].draw(p)
        polys=[Polygon(c).buffer(0) for c in p.c]
        # even-odd-ish: biggest are outers; subtract contained
        polys.sort(key=lambda q:-q.area); res=None
        for q in polys:
            res=q if res is None else (res.difference(q) if res.contains(q.representative_point()) else res.union(q))
        cache[g]=res if res is not None else Polygon()
    return cache[g]
hf=hb.Font(hb.Face(open(fp,'rb').read()))
H=120
def check(word):
    b=hb.Buffer(); b.add_str(word); b.guess_segment_properties(); hb.shape(hf,b,{})
    x=0; items=[]
    for i,p in zip(b.glyph_infos,b.glyph_positions):
        n=hf.glyph_to_string(i.codepoint)
        from shapely import affinity
        items.append((n,affinity.translate(shape(n),x+p.x_offset,p.y_offset))); x+=p.x_advance
    out=[]
    for k in range(len(items)-1):
        (n1,a),(n2,c)=items[k],items[k+1]
        if n1=='space' or n2=='space': continue
        ov=a.intersection(c)
        bad=ov.intersection(box(-1e6,H+15,1e6,1e6)).area + ov.intersection(box(-1e6,-1e6,1e6,-15)).area
        gap=a.intersection(box(-1e6,H+15,1e6,1e6)).distance(c.intersection(box(-1e6,H+15,1e6,1e6)))
        out.append((n1,n2,round(bad),round(gap)))
    return out
words=sys.argv[2].split()
for w in words:
    r=check(w); print(w, [(a,b,o,g) for a,b,o,g in r if o>0 or g<25])

def render(words, out, scale=0.15):
    from PIL import Image, ImageDraw, ImageFont
    from shapely import affinity
    L=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
    rows=[]
    for w in words:
        b=hb.Buffer(); b.add_str(w); b.guess_segment_properties(); hb.shape(hf,b,{})
        x=0; items=[]
        for i,p in zip(b.glyph_infos,b.glyph_positions):
            n=hf.glyph_to_string(i.codepoint); items.append((n,affinity.translate(shape(n),x+p.x_offset,p.y_offset))); x+=p.x_advance
        rows.append((w,items,x))
    Wd=int(max(r[2] for r in rows)*scale)+80; Hh=len(rows)*int(2300*scale)+20
    im=Image.new('RGB',(Wd,Hh),'white'); d=ImageDraw.Draw(im)
    for ri,(w,items,tot) in enumerate(rows):
        oy=20+ri*int(2300*scale)+int(1300*scale)
        T=lambda pt:(Wd-40-(tot-pt[0])*scale, oy-pt[1]*scale)
        d.line([T((0,0)),T((tot,0))],fill='#ddd')
        cols=['#222','#555']
        def fill(g,col):
            gs_=[g] if g.geom_type=='Polygon' else list(getattr(g,'geoms',[]))
            for q in gs_:
                if q.geom_type!='Polygon' or q.is_empty: continue
                d.polygon([T(p) for p in q.exterior.coords],fill=col)
                for h in q.interiors: d.polygon([T(p) for p in h.coords],fill='white')
        for k,(n,g) in enumerate(items): fill(g,cols[k%2])
        for k in range(len(items)-1):
            ov=items[k][1].intersection(items[k+1][1])
            fill(ov.intersection(box(-1e6,H+15,1e6,1e6)),'#e0301e'); fill(ov.intersection(box(-1e6,-1e6,1e6,-15)),'#e0301e')
    im.save(out)
if len(sys.argv)>3: render(sys.argv[3].split(), sys.argv[4])
