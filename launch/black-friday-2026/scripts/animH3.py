import sys,subprocess
exec(open('mock3.py').read().split("o=Image.new('RGBA',(W,H),(0,0,0,255)); glow")[0])
FPS=30; TOT=9.04
fr_all=[]
# decode clip frames
raw=subprocess.run(['ffmpeg','-loglevel','error','-i','hh.mp4','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout
cw,ch_=496,864; n=len(raw)//(cw*ch_*3)
src=[Image.frombytes('RGB',(cw,ch_),raw[i*cw*ch_*3:(i+1)*cw*ch_*3]) for i in range(n)]
LW=960; LH=int(ch_*LW/cw); LX=60; LY=448
ft,fs=140,110
yy=np.arange(LH)[:,None]; xx=np.arange(LW)[None,:]
MASK=np.clip(yy/ft,0,1)*np.clip(np.minimum(xx,LW-1-xx)/fs,0,1)
def eo3(x): x=min(max(x,0),1); return 1-(1-x)**3
def eob(x,k=1.9):
    x=min(max(x,0),1); return 1+(k+1)*(x-1)**3+k*(x-1)**2
bg=Image.new('RGBA',(W,H),(0,0,0,255)); glow(bg,W/2,1250,800,peak=90)
def figframe(i):
    im=src[min(i,n-1)].resize((LW,LH),Image.LANCZOS).convert('RGBA'); a=np.array(im); a[...,3]=(MASK*255).astype(np.uint8)
    o=bg.copy(); o.alpha_composite(Image.fromarray(a,'RGBA'),(LX,LY)); return o
def tl(t,size,fill,stroke=(0,0,0),sw=8):
    d=ImageDraw.Draw(Image.new('RGBA',(10,10))); fnt=f(size); w=int(d.textlength(t,font=fnt))+2*sw+10
    im=Image.new('RGBA',(w,size+2*sw+60),(0,0,0,0))
    ImageDraw.Draw(im).text((sw+5,sw),t,font=fnt,fill=fill,stroke_width=sw,stroke_fill=stroke); return im.crop(im.getbbox())
def fit(t,size,fill,sw,maxw=980):
    while True:
        im=tl(t,size,fill,sw=sw)
        if im.width<=maxw: return im
        size-=4
A=tl("10% OFF",214,(255,255,255),sw=12); B=tl("PRICES DROP.",118,(255,255,255),sw=9)
ims=[fit(x,74,(255,196,90),8) for x in ["HANKY HAMMERS","PRICES DOWN."]]
C=Image.new('RGBA',(max(i.width for i in ims),sum(i.height for i in ims)+10),(0,0,0,0)); y_=0
for i in ims: C.alpha_composite(i,((C.width-i.width)//2,y_)); y_+=i.height+10
YA,YB,YC=45,250,382
def place(im,layer,cx,y,scale=1.0,alpha=1.0):
    if scale!=1.0: layer=layer.resize((max(1,int(layer.width*scale)),max(1,int(layer.height*scale))),Image.LANCZOS)
    if alpha<1.0:
        a=layer.getchannel('A').point(lambda v:int(v*alpha)); layer=layer.copy(); layer.putalpha(a)
    im.alpha_composite(layer,(int(cx-layer.width/2),int(y)))
# sign text (last frame geometry)
sc_=LW/cw; sx=lambda v:LX+v*sc_; sy=lambda v:LY+v*sc_
SCX=(sx(38)+sx(466))/2-40; SCY=(sy(470)+sy(760))/2
S1=tl("BLACK FRIDAY",100,(20,20,20),stroke=(20,20,20),sw=0); k_=620/S1.width; S1=S1.resize((int(S1.width*k_),int(S1.height*k_)),Image.LANCZOS)
S2=tl("27 - 30 NOV",100,(200,30,30),stroke=(200,30,30),sw=0); k2=S1.width*0.7/S2.width; S2=S2.resize((int(S2.width*k2),int(S2.height*k2)),Image.LANCZOS)
# tee slide: whole photo with face
pj=Image.open('hh_tee.jpg').convert('RGB'); th=int(pj.height*W/pj.width); pi=pj.resize((W,th),Image.LANCZOS)
edge=np.array(pi.crop((0,0,W,6))).reshape(-1,3).mean(axis=0).astype(int)
pa=np.array(pi); band=np.repeat(pa[:1],H-th,axis=0); slide=Image.fromarray(np.vstack([band,pa]))
T_SIGN,T_TEE=5.5,7.0
last=figframe(n-1)
p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','30','-i','-','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','hh_body.mp4'],stdin=subprocess.PIPE)
for i in range(int(TOT*FPS)):
    t=i/FPS
    base=figframe(int(t*24)) if t<5.04 else last.copy()
    base.alpha_composite(wm)
    if T_SIGN<=t<T_TEE:
        u=(t-T_SIGN)/0.25; scl=1+0.35*(1-eob(u,1.4)) if u<1 else 1
        place(base,S1,SCX,SCY-S1.height-6-(S1.height*scl-S1.height)/2+14,scl,alpha=min(1,u*3)); place(base,S2,SCX,SCY+30,scl,alpha=min(1,u*3))
    if t>=T_TEE:
        off=int((1-eo3((t-T_TEE)/0.45))*H); b=base.convert('RGB'); b.paste(slide,(0,off)); base=b.convert('RGBA')
    if t>=0.5:
        u=(t-0.5)/0.25; sc=1+0.3*(1-eob(u,1.2)) if u<1 else 1
        place(base,A,W/2,YA-(A.height*sc-A.height)/2,sc,alpha=min(1,u*3))
    if t>=1.0:
        u=(t-1.0)/0.3; x=W/2-(1-eo3(u))*1200; dy=14*eob((t-1.3)/0.2,2.5) if t>1.3 else 0
        place(base,B,x,YB+dy)
    if t>=1.5:
        u=(t-1.5)/0.3; x=W/2-(1-eo3(u))*1200; dy=-14*eob((t-1.8)/0.2,2.5) if t>1.8 else 0
        place(base,C,x,YC+dy)
    p.stdin.write(base.convert('RGB').tobytes())
p.stdin.close(); p.wait(); print('body done',n)
