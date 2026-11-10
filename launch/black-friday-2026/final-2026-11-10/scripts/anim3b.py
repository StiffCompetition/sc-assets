exec(open('mock3.py').read().split("o=Image.new('RGBA',(W,H),(0,0,0,255)); glow")[0])
import subprocess
FPS=30
fr=Image.open('mw_last.png').convert('RGB')
def lerp(a,b,k): return a+(b-a)*k
def eo3(x): x=min(max(x,0),1); return 1-(1-x)**3
def eob(x,k=1.9):
    x=min(max(x,0),1); return 1+(k+1)*(x-1)**3+k*(x-1)**2
def eio(x): x=min(max(x,0),1); return x*x*(3-2*x)
# backgrounds
bgG=Image.new('RGBA',(W,H),(0,0,0,255)); glow(bgG,W/2,1150,750)
bgK=Image.new('RGBA',(W,H),(0,0,0,255))
FINAL=dict(s=700/fr.width,x=50,y=620,ch=1.0*700)
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
MW_=400; ml=mugc.resize((MW_,int(mugc.height*MW_/mugc.width)),Image.LANCZOS)
MX=265; MBOT=1420
def mug_on(o,rise):
    # rise 0..1 -> y offset
    off=(1-rise)*(ml.height+260)
    sh=Image.new('RGBA',(W,H),(0,0,0,0)); by=MBOT+off
    ImageDraw.Draw(sh).ellipse((MX+20,by-40,MX+MW_-40,by+30),fill=(0,0,0,170)); o.alpha_composite(sh.filter(ImageFilter.GaussianBlur(25)))
    o.alpha_composite(ml,(MX,int(by-ml.height)))
def tl(t,size,fill,stroke=(0,0,0),sw=8):
    d=ImageDraw.Draw(Image.new('RGBA',(10,10))); fnt=f(size); w=int(d.textlength(t,font=fnt))+2*sw+10
    im=Image.new('RGBA',(w,size+2*sw+60),(0,0,0,0))
    ImageDraw.Draw(im).text((sw+5,sw),t,font=fnt,fill=fill,stroke_width=sw,stroke_fill=stroke); return im.crop(im.getbbox())
A=None
for _s in range(190,60,-2):
    A=tl("UP TO 30% OFF",_s,(255,255,255),sw=10)
    if A.width<=980: break
print('A size',_s,A.size); B=tl("PRICES DROP.",100,(255,255,255),sw=7); C=tl("MAJOR WOOD STAYS UP.",66,(255,196,90),sw=5)
YA,YB,YC=280,400,530
def place(im,layer,cx,y,scale=1.0,alpha=1.0):
    if scale!=1.0: layer=layer.resize((max(1,int(layer.width*scale)),max(1,int(layer.height*scale))),Image.LANCZOS)
    if alpha<1.0:
        a=layer.getchannel('A').point(lambda v:int(v*alpha)); layer=layer.copy(); layer.putalpha(a)
    im.alpha_composite(layer,(int(cx-layer.width/2),int(y)))
_pj=Image.open('xm_tee_main.jpg').convert('RGB'); _PW=800; _PY=560; _ph=int(_pj.height*_PW/_pj.width); _pa=np.array(_pj.resize((_PW,_ph),Image.LANCZOS)).astype(float)
_edge=np.concatenate([_pa[:6].reshape(-1,3),_pa[-6:].reshape(-1,3),_pa[:,:6].reshape(-1,3),_pa[:,-6:].reshape(-1,3)]).mean(axis=0)
_fe=110; _yy=np.arange(_ph)[:,None]; _xx=np.arange(_PW)[None,:]
_m=np.clip(np.minimum(np.minimum(_yy/_fe,(_ph-1-_yy)/_fe),np.minimum(_xx/_fe,(_PW-1-_xx)/_fe)),0,1)[...,None]
_sl=np.zeros((H,W,3)); _sl[:]=_edge; _x0=(W-_PW)//2; _bl=_pa*_m+_edge*(1-_m); _sl[_PY:_PY+_ph,_x0:_x0+_PW]=_bl[:min(_ph,H-_PY)]
tee=Image.fromarray(_sl.astype(np.uint8))
wm=Image.open('wm_new.png')
def mugframe(k,rise):
    o=Image.blend(bgK,bgG,k)
    fg,x,y=figure(k); o.alpha_composite(fg,(x,y))
    if rise>0: mug_on(o,rise)
    return o
final_mug=mugframe(1,1).convert('RGB'); final_mug.save('base_mug2.png')
DUR=6.0; TG=0.5; TR0=0.12
p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','30','-i','-','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','mw_prod.mp4'],stdin=subprocess.PIPE)
for i in range(int(DUR*FPS)):
    t=i/FPS
    if t<TG+0.001:
        k=eio(t/TG); rise=eob((t-TR0)/0.5,1.4) if t>TR0 else 0
        base=mugframe(k,rise)
    else:
        base=final_mug.convert('RGBA')
    if t>3.3:
        off=int((1-eo3((t-3.3)/0.55))*H); base=base.convert('RGB'); base.paste(tee,(0,off)); base=base.convert('RGBA')
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
p.stdin.close(); p.wait(); print('done')
