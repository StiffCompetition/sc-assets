from PIL import Image, ImageFilter
import numpy as np
from scipy import ndimage as ndi
K=3
import sys
SIG=float(sys.argv[1])
src=Image.open('/home/claude/sc-assets/brand/logos/SC_square_logo_chrome_transparent.png').convert('RGBA')
W,H=src.size
S=np.asarray(src).astype(np.float32)
rgb=S[...,:3];al=S[...,3]/255
mx=rgb.max(2);r,g,b=rgb[...,0],rgb[...,1],rgb[...,2]
opaque=al>0.9
black=(mx<45)&opaque
red=(r-np.maximum(g,b)>80)&opaque
dred=ndi.distance_transform_edt(~red)
blue=(~black)&(~red)&opaque&(dred<58)&(np.sqrt((r-30)**2+(g-90)**2+(b-148)**2)<52)&(b>118)
blue=ndi.binary_closing(blue,iterations=5)&~black&~red&opaque&(dred<52)
blue=ndi.median_filter(blue.astype(np.uint8),size=5).astype(bool)
face=opaque&~black&~red&~blue
lab=np.zeros((H,W),np.int8)   # 0 raster
lab[black]=1;lab[red]=2;lab[blue]=3
# grow cores into unlabeled non-face-ish pixels (transition) up to 5px
un=(lab==0)&opaque
dist,idx=ndi.distance_transform_edt(lab==0,return_indices=True)
near=lab[idx[0],idx[1]]
grow=un&(dist<=5)&((near==1)|(near==2))&(mx<190)
lab2=lab.copy();lab2[grow]=near[grow]
Image.fromarray((lab2*80).astype('uint8')).save('labels.png')
# soft one-hot at K scale
oh=[ndi.gaussian_filter(np.asarray(Image.fromarray(((lab2==c)*255).astype('uint8')).resize((W*K,H*K),Image.BICUBIC)).astype(np.float32)/255,K*SIG) for c in range(4)]
oh=np.stack(oh)
big=src.resize((W*K,H*K),Image.LANCZOS)
out=np.asarray(big.convert('RGB')).astype(np.float32)
cols={1:(4,4,4),2:(214,38,26),3:(30,90,148)}
for c in (1,2,3):
    other=np.max(np.delete(oh,c,axis=0),axis=0)
    t=np.clip((oh[c]-other)/0.25+0.5,0,1);t=t*t*(3-2*t)
    out=out*(1-t[...,None])+np.array(cols[c],np.float32)*t[...,None]
A=np.asarray(big.split()[3]).astype(np.float32)/255
A=np.asarray(Image.fromarray((A*255).astype('uint8')).filter(ImageFilter.GaussianBlur(K*3.0))).astype(np.float32)/255
t=np.clip((A-0.5)/0.12+0.5,0,1);A=t*t*(3-2*t)
res=np.dstack([np.clip(out,0,255),A*255]).astype('uint8')
Image.fromarray(res,'RGBA').save('SC_chrome_vec_x3_s%s.png'%sys.argv[1]+'')
def comp(i):
    bg=Image.new('RGBA',i.size,'white');bg.alpha_composite(i);return bg.convert('RGB')
n=Image.open('SC_chrome_vec_x3_s%s.png'%sys.argv[1]+'');c=comp(n);c.resize((900,859),Image.LANCZOS).save('full.jpg')
ob=comp(big);box=(180*3,540*3,480*3,780*3)
a=ob.crop(box);b2=c.crop(box)
s=Image.new('RGB',(a.width*2+20,a.height),'gray');s.paste(a,(0,0));s.paste(b2,(a.width+20,0));s.save('cmp.jpg')
