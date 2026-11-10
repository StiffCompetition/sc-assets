import sys,subprocess
exec(open('mock3.py').read().split("o=Image.new('RGBA',(W,H),(0,0,0,255)); glow")[0])
name,last,prodjpg,crop_top,gold,out=sys.argv[1:7]; crop_top=int(crop_top)
FPS=30
fr=Image.open(last).convert('RGB')
def lerp(a,b,k): return a+(b-a)*k
def eo3(x): x=min(max(x,0),1); return 1-(1-x)**3
def eob(x,k=1.9):
    x=min(max(x,0),1); return 1+(k+1)*(x-1)**3+k*(x-1)**2
def eio(x): x=min(max(x,0),1); return x*x*(3-2*x)
bgG=Image.new('RGBA',(W,H),(0,0,0,255)); glow(bgG,W/2,1150,750)
bgK=Image.new('RGBA',(W,H),(0,0,0,255))
FINAL=dict(s=760/fr.width,x=160,y=440,ch=1.15*760)
def figure(k):
    s=lerp(1920/fr.height,FINAL['s'],k); x=lerp(-11,FINAL['x'],k); y=lerp(0,FINAL['y'],k)
    w=int(fr.width*s); h=int(fr.height*s)
    im=fr.resize((w,h),Image.LANCZOS).convert('RGBA')
    ch=int(lerp(h,FINAL['ch'],k)); im=im.crop((0,0,w,min(ch,h)))
    a=np.ones((im.height,im.width))
    fb=260*k; fs=140*k
    yy=np.arange(im.height)[:,None]; xx=np.arange(im.width)[None,:]
    if fb>1: a=a*np.clip((im.height-yy)/fb,0,1)
    if fs>1: a=a*np.clip(np.minimum(xx,im.width-1-xx)/fs,0,1)
    arr=np.array(im); arr[...,3]=(a*255).astype(np.uint8); return Image.fromarray(arr,'RGBA'),int(x),int(y)
def tl(t,size,fill,stroke=(0,0,0),sw=8):
    d=ImageDraw.Draw(Image.new('RGBA',(10,10))); fnt=f(size); w=int(d.textlength(t,font=fnt))+2*sw+10
    im=Image.new('RGBA',(w,size+2*sw+60),(0,0,0,0))
    ImageDraw.Draw(im).text((sw+5,sw),t,font=fnt,fill=fill,stroke_width=sw,stroke_fill=stroke); return im.crop(im.getbbox())
def fit_tl(t,size,fill,sw,maxw=980):
    while True:
        im=tl(t,size,fill,sw=sw)
        if im.width<=maxw: return im
        size-=4
A=tl("10% OFF",214,(255,255,255),sw=10); B=tl("PRICES DROP.",118,(255,255,255),sw=7)
def gl(t): return fit_tl(t,74,(255,196,90),5)
parts=gold.split('|'); ims=[gl(x) for x in parts]
C=Image.new('RGBA',(max(i.width for i in ims),sum(i.height for i in ims)+8*(len(ims)-1)),(0,0,0,0)); yy_=0
for i in ims: C.alpha_composite(i,((C.width-i.width)//2,yy_)); yy_+=i.height+8
YA,YB,YC=45,250,382
def place(im,layer,cx,y,scale=1.0,alpha=1.0):
    if scale!=1.0: layer=layer.resize((max(1,int(layer.width*scale)),max(1,int(layer.height*scale))),Image.LANCZOS)
    if alpha<1.0:
        a=layer.getchannel('A').point(lambda v:int(v*alpha)); layer=layer.copy(); layer.putalpha(a)
    im.alpha_composite(layer,(int(cx-layer.width/2),int(y)))
# product photo slide
pj=Image.open(prodjpg).convert('RGB')
if crop_top: pj=pj.crop((0,crop_top,pj.width,pj.height))
th=int(pj.height*W/pj.width); pi=pj.resize((W,th),Image.LANCZOS)
edge=np.array(pi.crop((0,0,W,10))).reshape(-1,3).mean(axis=0).astype(int); bgc=tuple(int(v) for v in edge)
slide=Image.new('RGB',(W,H),bgc)
g=np.ones((th,W)); fh=min(220,th//3); g[:fh]=np.linspace(0,1,fh)[:,None]
pa=np.array(pi.convert('RGBA')); pa[...,3]=(g*255).astype(np.uint8)
sl=slide.convert('RGBA'); sl.alpha_composite(Image.fromarray(pa,'RGBA'),(0,H-th)); gr=np.zeros((H,W,4),np.uint8); gr[:620,:,3]=(np.linspace(0.88,0,620)**1*255).astype(np.uint8)[:,None]; sl.alpha_composite(Image.fromarray(gr,'RGBA')); sl.alpha_composite(wm); slide=sl.convert('RGB')
def frame(k):
    o=Image.blend(bgK,bgG,k); fg,x,y=figure(k); o.alpha_composite(fg,(x,y)); o.alpha_composite(wm); return o
final=frame(1).convert('RGB')
DUR=6.0; TG=0.5
p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','30','-i','-','-c:v','libx264','-crf','18','-pix_fmt','yuv420p',out],stdin=subprocess.PIPE)
for i in range(int(DUR*FPS)):
    t=i/FPS
    base=frame(eio(t/TG)) if t<TG+0.001 else final.convert('RGBA')
    if t>3.3:
        off=int((1-eo3((t-3.3)/0.55))*H); base=base.convert('RGB'); base.paste(slide,(0,off)); base=base.convert('RGBA')
    if t>=0.45:
        u=(t-0.45)/0.3; sc=1+0.3*(1-eob(u,1.2)) if u<1 else 1
        place(base,A,W/2,YA-(A.height*sc-A.height)/2,sc,alpha=min(1,u*3))
    if t>=0.8:
        u=(t-0.8)/0.35; x=W/2-(1-eo3(u))*1200; dy=14*eob((t-1.15)/0.2,2.5) if t>1.15 else 0
        place(base,B,x,YB+dy)
    if t>=1.4:
        u=(t-1.4)/0.35; x=W/2-(1-eo3(u))*1200; dy=-14*eob((t-1.75)/0.2,2.5) if t>1.75 else 0
        place(base,C,x,YC+dy)
    p.stdin.write(base.convert('RGB').tobytes())
p.stdin.close(); p.wait(); print('done',name)
