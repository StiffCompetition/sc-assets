import sys,subprocess,numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageFile,ImageChops
ImageFile.LOAD_TRUNCATED_IMAGES=True
NAME,CLIP,PROD,LINES,MODE,PY,PW=sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4].split('|'),sys.argv[5],int(sys.argv[6]),int(sys.argv[7])
W,H=1080,1920; FPS=30; DUR=6.0
FB="/usr/share/fonts/opentype/inter/Inter-Black.otf"
def f(s): return ImageFont.truetype(FB,s)
def lerp(a,b,k): return a+(b-a)*k
def eo3(x): x=min(max(x,0),1); return 1-(1-x)**3
def eio(x): x=min(max(x,0),1); return x*x*(3-2*x)
def eob(x,k=1.9):
    x=min(max(x,0),1); return 1+(k+1)*(x-1)**3+k*(x-1)**2
raw=subprocess.run(['ffmpeg','-loglevel','error','-i',CLIP,'-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout
cw,ch_=496,864; n=len(raw)//(cw*ch_*3)
fr=Image.frombytes('RGB',(cw,ch_),raw[(n-1)*cw*ch_*3:n*cw*ch_*3])
def glow(im,cx,cy,r,peak=90):
    yy2,xx2=np.mgrid[0:H,0:W]; d=np.sqrt((xx2-cx)**2+(yy2-cy)**2)/r
    al=(np.clip(1-d,0,1)**2*peak).astype(np.uint8)
    g=np.dstack([np.full((H,W),255,np.uint8),np.full((H,W),196,np.uint8),np.full((H,W),90,np.uint8),al]); im.alpha_composite(Image.fromarray(g,'RGBA'))
bgG=Image.new('RGBA',(W,H),(0,0,0,255)); glow(bgG,W/2,1000,750)
bgK=Image.new('RGBA',(W,H),(0,0,0,255))
FW=820; FINAL=dict(s=FW/fr.width,x=(W-FW)//2,y=600,ch=1.08*FW)
def figure(k):
    s=lerp(1920/fr.height,FINAL['s'],k); x=lerp(-(fr.width*1920/fr.height-W)/2,FINAL['x'],k); y=lerp(0,FINAL['y'],k)
    w=int(fr.width*s); h=int(fr.height*s)
    im=fr.resize((w,h),Image.LANCZOS).convert('RGBA')
    ch=int(lerp(h,FINAL['ch'],k)); im=im.crop((0,0,w,min(ch,h)))
    a=np.ones((im.height,im.width)); fb=260*k; fs=140*k
    yy=np.arange(im.height)[:,None]; xx=np.arange(im.width)[None,:]
    if fb>1: a=a*np.clip((im.height-yy)/fb,0,1)
    if fs>1: a=a*np.clip(np.minimum(xx,im.width-1-xx)/fs,0,1)
    arr=np.array(im); arr[...,3]=(a*255).astype(np.uint8); return Image.fromarray(arr,'RGBA'),int(x),int(y)
def tl(t,size,fill,stroke=(0,0,0),sw=8):
    d=ImageDraw.Draw(Image.new('RGBA',(10,10))); fnt=f(size); w=int(d.textlength(t,font=fnt))+2*sw+10
    im=Image.new('RGBA',(w,size+2*sw+60),(0,0,0,0))
    ImageDraw.Draw(im).text((sw+5,sw),t,font=fnt,fill=fill,stroke_width=sw,stroke_fill=stroke); return im.crop(im.getbbox())
def fit(t,size,fill,sw,maxw=960):
    while True:
        im=tl(t,size,fill,sw=sw)
        if im.width<=maxw: return im
        size-=2
A=fit("UP TO 30% OFF",190,(255,255,255),9); B=fit("PRICES DROP.",100,(255,255,255),7)
ims=[fit(x,66,(255,196,90),6) for x in LINES]
C=Image.new('RGBA',(max(i.width for i in ims),sum(i.height for i in ims)+10*(len(ims)-1)),(0,0,0,0)); y_=0
for i in ims: C.alpha_composite(i,((C.width-i.width)//2,y_)); y_+=i.height+10
YA,YB,YC=280,400,548
def place(im,layer,cx,y,scale=1.0,alpha=1.0):
    if scale!=1.0: layer=layer.resize((max(1,int(layer.width*scale)),max(1,int(layer.height*scale))),Image.LANCZOS)
    if alpha<1.0:
        a=layer.getchannel('A').point(lambda v:int(v*alpha)); layer=layer.copy(); layer.putalpha(a)
    im.alpha_composite(layer,(int(cx-layer.width/2),int(y)))
# product photo composite: PW px wide, top at PY, feathered into its own average edge colour
pj=Image.open(PROD).convert('RGB'); ph=int(pj.height*PW/pj.width); pi=pj.resize((PW,ph),Image.LANCZOS)
pa=np.array(pi).astype(float)
edge=np.concatenate([pa[:6].reshape(-1,3),pa[-6:].reshape(-1,3),pa[:,:6].reshape(-1,3),pa[:,-6:].reshape(-1,3)]).mean(axis=0)
fe=110; yy=np.arange(ph)[:,None]; xx=np.arange(PW)[None,:]
m=np.clip(np.minimum(np.minimum(yy/fe,(ph-1-yy)/fe),np.minimum(xx/fe,(PW-1-xx)/fe)),0,1)[...,None]
blend=pa*m+edge*(1-m)
slide=np.zeros((H,W,3)); slide[:]=edge
x0=int(W/2-0.575*PW)
sl=max(0,-x0); sr=min(PW,W-x0)
slide[PY:PY+min(ph,H-PY),x0+sl:x0+sr]=blend[:min(ph,H-PY),sl:sr]
slide=Image.fromarray(slide.astype(np.uint8))
wm=Image.open('wm_new.png').convert('RGBA')
def mugframe(k): 
    o=Image.blend(bgK,bgG,k); fg,x,y=figure(k); o.alpha_composite(fg,(x,y)); return o
final=mugframe(1.0)
p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','30','-i','-','-c:v','libx264','-crf','16','-pix_fmt','yuv420p',f'{NAME}_prod.mp4'],stdin=subprocess.PIPE)
TG=0.5
for i in range(int(DUR*FPS)):
    t=i/FPS
    base=mugframe(eio(t/TG)) if t<TG+0.001 else final.copy()
    if t>3.3:
        off=int((1-eo3((t-3.3)/0.55))*H); b=base.convert('RGB'); b.paste(slide,(0,off)); base=b.convert('RGBA')
    if t>=0.45:
        u=(t-0.45)/0.3; sc=1+0.3*(1-eob(u,1.2)) if u<1 else 1
        place(base,A,W/2,YA-(A.height*sc-A.height)/2,sc,alpha=min(1,u*3))
    if t>=0.8:
        u=(t-0.8)/0.35; x=W/2-(1-eo3(u))*1200; dy=14*eob((t-1.15)/0.2,2.5) if t>1.15 else 0
        place(base,B,x,YB+dy)
    if t>=1.4:
        u=(t-1.4)/0.35; x=W/2-(1-eo3(u))*1200; dy=-14*eob((t-1.75)/0.2,2.5) if t>1.75 else 0
        place(base,C,x,YC+dy)
    base.alpha_composite(wm)
    p.stdin.write(base.convert('RGB').tobytes())
p.stdin.close(); p.wait(); print('prod done','A',A.size,'B',B.size,'C',C.size,'photo',ph)
