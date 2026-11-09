import math,numpy as np,cv2
from PIL import Image
L=Image.open('vec_logo_canvas.png').convert('RGBA')
def key(src,out):
    im=np.array(Image.open(src).convert('RGB')).astype(np.float32)
    r,g,b=im[...,0],im[...,1],im[...,2]
    gd=g-np.maximum(r,b);gate=np.clip((g-110)/80,0,1);score=gd*gate
    a=1-np.clip((score-20)/90,0,1);a=np.minimum(a,1-np.clip((gd-45)/40,0,1));a=cv2.GaussianBlur(a,(0,0),0.6)
    rgb=im.copy();edge=a<0.98;interior=(a>=0.98).astype(np.uint8)
    d,lab=cv2.distanceTransformWithLabels(1-interior,cv2.DIST_L2,5,labelType=cv2.DIST_LABEL_PIXEL)
    ys,xs=np.nonzero(interior);idx=np.zeros(lab.max()+1,int);idx[lab[ys,xs]]=np.arange(len(ys))
    rgb[edge]=im[ys[idx[lab]],xs[idx[lab]]][edge]
    o=np.dstack([rgb,a*255]).clip(0,255).astype(np.uint8);Image.fromarray(o,'RGBA').save(out)
    ab=np.nonzero(a>0.5);return ab[1].min(),ab[0].min(),ab[1].max()+1,ab[0].max()+1
def build(piece,crop,piv,s,rot,bx,by,name,sd=4,so=3,sa=.5):
    P0=Image.open(piece).crop(crop);pv0=(piv[0]-crop[0],piv[1]-crop[1])
    h=P0.resize((round(P0.width*s),round(P0.height*s)),Image.LANCZOS)
    pv=(pv0[0]*s,pv0[1]*s);W,H=h.size;R=int(math.hypot(W,H))+4
    c=Image.new('RGBA',(2*R,2*R),(0,0,0,0));c.alpha_composite(h,(int(R-pv[0]),int(R-pv[1])))
    c=c.rotate(-rot,resample=Image.BICUBIC,center=(R,R))
    big=Image.new('RGBA',(L.width+4*R,L.height+4*R),(0,0,0,0));big.alpha_composite(c,(int(bx-R)+2*R,int(by-R)+2*R))
    hf=big.crop((2*R,2*R,2*R+L.width,2*R+L.height))
    HA=np.array(hf)[...,3].astype(np.float32)/255
    La=np.array(L).astype(np.float32)
    sh=cv2.GaussianBlur(HA,(0,0),sd);sh=np.roll(sh,so,axis=0)
    La[...,:3]*=(1-sa*sh*(1-HA))[...,None]
    out=Image.fromarray(La.clip(0,255).astype(np.uint8),'RGBA');out.alpha_composite(hf)
    out.save(name+'_rgba.png')
    bg=Image.new('RGBA',out.size,(255,255,255,255));bg.alpha_composite(out);bg=bg.convert('RGB');bg.save(name+'.png')
    bg.crop((430,0,830,380)).resize((1000,950)).save('z_'+name+'.png')
