import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi
src=Image.open(sys.argv[1]).convert('RGB'); band_px=int(sys.argv[3]) if len(sys.argv)>3 else 10
a=np.asarray(src).astype(np.float32)
lum=0.299*a[...,0]+0.587*a[...,1]+0.114*a[...,2]; mn=a.min(axis=2)
nearwhite=mn>200
lab,_=ndi.label(nearwhite)
edge_labels=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
bg=np.isin(lab,list(edge_labels))
dist=ndi.distance_transform_edt(~bg)          # distance of logo pixels from background
band=(~bg)&(dist<=band_px)
alpha=np.ones(lum.shape,np.float32); alpha[bg]=0
# in the edge band the pixel is a mix of the black outline and white paper: un-mix it
ab=np.clip((235-lum)/(235-30),0,1); alpha[band]=ab[band]
# pixels at the very rim of the background that still carry ink
rim=bg&(ndi.distance_transform_edt(bg)<=2); alpha[rim]=np.clip((235-lum[rim])/(235-30),0,1)
rgb=a.copy(); edge=band|rim; rgb[edge]=[14,14,16]
out=np.dstack([rgb,alpha*255]).round().astype(np.uint8)
im=Image.fromarray(out,'RGBA'); im=im.crop(im.getbbox()); im.save(sys.argv[2]); print(im.size)
