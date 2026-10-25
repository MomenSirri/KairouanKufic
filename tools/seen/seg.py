from PIL import Image
import numpy as np
from scipy import ndimage as ndi
from skimage import measure
def masks(f, minarea=5000):
    im=np.array(Image.open(f).convert("RGB")).astype(int)
    r,g,b=im[...,0],im[...,1],im[...,2]
    red=(r>130)&(g<110)&(b<90)&(r-g>50)
    yel=(r>110)&(g>90)&(b<120)&(r-b>45)&~red
    ink=im.max(2)<110
    near=ndi.binary_dilation(yel,iterations=7)
    m=yel|(ink&near)
    m=ndi.binary_closing(m,iterations=1)
    lab,n=ndi.label(yel)
    comps=[]
    for k,sl in enumerate(ndi.find_objects(lab),1):
        a=(lab[sl]==k).sum()
        if a>minarea:
            y,x=sl; comps.append((x.start,x.stop,y.start,y.stop,a))
    return im,yel,m,comps
