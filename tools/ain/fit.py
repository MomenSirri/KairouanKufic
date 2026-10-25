import numpy as np
from scipy.optimize import minimize
P=np.load("ain/isol_contour.npy")
def bez(p0,c1,c2,p3,n=60):
    t=np.linspace(0,1,n)[:,None]
    return (1-t)**3*p0+3*(1-t)**2*t*c1+3*(1-t)*t**2*c2+t**3*p3
def chain(anchors,tans,lens):
    pts=[]
    for i in range(len(anchors)-1):
        p0,p3=np.array(anchors[i]),np.array(anchors[i+1])
        c1=p0+np.array(tans[i])*lens[2*i]; c2=p3-np.array(tans[i+1])*lens[2*i+1]
        pts.append(bez(p0,c1,c2,p3))
    return np.vstack(pts)
def err(curve,data):
    d=np.sqrt(((data[:,None,:]-curve[None,:,:])**2).sum(-1)).min(1); return d
def fit(anchors,tans,data):
    f=lambda L: (err(chain(anchors,tans,np.abs(L)),data)**2).mean()
    r=minimize(f,np.ones(2*(len(anchors)-1))*0.5,method="Nelder-Mead",options=dict(maxiter=4000,xatol=1e-4,fatol=1e-8))
    L=np.abs(r.x); e=err(chain(anchors,tans,L),data); return L,e
def nrm(v): v=np.array(v,float); return v/np.linalg.norm(v)
# split contour into outer / inner tail portions (below y=0.45, left part of letter)
sel=P[(P[:,1]<0.45)&(P[:,0]<2.6)]
# outer: points that are left/below of the inner; classify by distance to a rough midline: use angle around centre (0.9,-2.0)
c=np.array([0.9,-2.0]); 
outer=[];inner=[]
for q in sel:
    r=np.linalg.norm(q-c)
    (outer if r>1.95 else inner).append(q)
outer=np.array(outer); inner=np.array(inner)
outer=outer[(outer[:,1]>-3.99)&~((outer[:,0]>2.3))]; inner=inner[~(inner[:,0]>2.3)&(inner[:,1]<-0.05)]
print("outer",len(outer),"inner",len(inner))
import itertools
best=None
for Ly in [-2.0,-2.25,-2.5]:
  for Bx in [1.0,1.25,1.5]:
    A=(0.25,0.5); Lp=(-0.75,Ly); Bt=(Bx,-4.0); TP=(2.75,-3.5)
    tans=[nrm((-0.4,-0.5)),(0,-1),(1,0),nrm((0.9,0.42))]
    L,e=fit([A,Lp,Bt,TP],tans,outer)
    if best is None or e.mean()<best[0]: best=(e.mean(),e.max(),Ly,Bx,L,tans)
print("OUTER best mean %.3f max %.3f Ly %.2f Bx %.2f"%best[:4], np.round(best[4],3))
bi=None
for ILx in [-0.375,-0.4375,-0.5]:
  for ILy in [-1.5,-1.625,-1.75]:
    TP=(2.75,-3.5); IL=(ILx,ILy); B=(0.0,0.0)
    tans=[nrm((-1,0.05)),(0,1),nrm((0.45,0.9))]
    L,e=fit([TP,IL,B],tans,inner)
    if bi is None or e.mean()<bi[0]: bi=(e.mean(),e.max(),ILx,ILy,L,tans)
print("INNER best mean %.3f max %.3f IL (%.3f,%.3f)"%bi[:4], np.round(bi[4],3))
np.save("ain/fit_out.npy",np.array([best[2],best[3],*best[4]])); np.save("ain/fit_in.npy",np.array([bi[2],bi[3],*bi[4]]))
