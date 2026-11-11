import sys
from PIL import Image, ImageFilter
import numpy as np
# args: src out W H logoK figK
src,out,W,H,LK,FK=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),float(sys.argv[5]),float(sys.argv[6])
S=Image.open(src).convert('RGB'); su=S.width/1124.0; u=W/1124.0
Ho=H/u
# background: dark, from top strip of source
strip=np.array(S.crop((0,0,S.width,int(30*su)))).astype(float).mean(axis=0)  # (w,3)
row=Image.fromarray(strip[None,:,:].astype('uint8')).resize((W,1),Image.LANCZOS)
row=row.filter(ImageFilter.GaussianBlur(40)) if False else row
bg=Image.new('RGB',(W,H)); a=np.array(row)[0]
from scipy.ndimage import gaussian_filter1d
a=gaussian_filter1d(a.astype(float),200,axis=0)
bgarr=np.tile(a[None,:,:],(H,1,1))
bg=Image.fromarray(bgarr.astype('uint8'))
def place(y0,y1,k,top_o,fade_top,fade_bot,canvas):
    crop=S.crop((0,int(y0*su),S.width,int(y1*su)))
    nw=int(W*k); nh=int((y1-y0)*u*k)
    crop=crop.resize((nw,nh),Image.LANCZOS)
    xo=(nw-W)//2
    crop=crop.crop((xo,0,xo+W,nh))
    m=np.ones((nh,W),dtype=float)
    ft=int(fade_top*u); fb=int(fade_bot*u)
    if ft>0: m[:ft,:]*=np.linspace(0,1,ft)[:,None]
    if fb>0: m[-fb:,:]*=np.linspace(1,0,fb)[:,None]
    mk=Image.fromarray((m*255).astype('uint8'))
    canvas.paste(crop,(0,int(top_o*u)),mk)
    return canvas
# figures band: orig y 405..1500, bottom pushed down by FDOWN units
FDOWN=float(sys.argv[7]) if len(sys.argv)>7 else 0
fb_h=(1500-405)*FK
ftop=Ho+FDOWN-fb_h
bg=place(405,1500,FK,ftop,70,0,bg)
# logo + tagline: orig y 25..415
LTOP=float(sys.argv[8]) if len(sys.argv)>8 else 30
bg=place(25,415,LK,LTOP,0,40,bg)
bg.save(out,quality=97,dpi=(300,300))
print(out,bg.size,'figtop',ftop,'logo end',LTOP+390*LK)
