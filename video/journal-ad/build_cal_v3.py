import math, subprocess, sys, numpy as np
_a=sys.argv[:]; sys.argv=['x']
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H,FPS=1080,1920,30; T=4.2; N=int(T*FPS)
AB='/tmp/jf/fonts/node_modules/@expo-google-fonts/lilita-one/400Regular/LilitaOne_400Regular.ttf'
PO='/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'
PINK=(255,80,150); WHITE=(255,255,255)
def bg():
    y=np.linspace(0,1,H)[:,None,None]; a=np.array((16,16,36))[None,None,:]*(1-y)+np.array((86,10,60))[None,None,:]*y
    return Image.fromarray(np.broadcast_to(a,(H,W,3)).astype(np.uint8)).convert('RGBA')
BG=bg()
PW=640
def pg(n):
    p=Image.open(f'/tmp/cal/eu-{n:02d}.png').convert('RGBA'); h=int(p.height*PW/p.width); return p.resize((PW,h),Image.LANCZOS)
PGS={k:pg(n) for k,n in dict(cover=1,jan=2,feb=3,apr=5,dec=13).items()}
ALL=[pg(n) for n in range(2,14)]
TOP=735; PX=(W-PW)//2; PIV=(W//2,TOP+14)
def ease_out_back(x):
    x=max(0,min(1,x)); c1=1.9; c3=c1+1; return 1+c3*(x-1)**3+c1*(x-1)**2
def page_layer(p,dt,fall=None):
    # dt: seconds since page entered. fall: seconds since tear began (None if not)
    L=Image.new('RGBA',(W,H),(0,0,0,0))
    y_off=-1500*(1-min(1,max(0,dt/0.45)))**2 if dt<0.45 else 0
    sh=Image.new('RGBA',(PW+80,p.height+80),(0,0,0,0)); ImageDraw.Draw(sh).rectangle((40,60,40+PW,60+p.height),fill=(0,0,0,170)); sh=sh.filter(ImageFilter.GaussianBlur(16))
    sh.alpha_composite(p,(40,40)) if False else None
    L.alpha_composite(sh,(PX-40,TOP-40+int(y_off)+14)); L.alpha_composite(p,(PX,TOP+int(y_off)))
    if fall is None:
        s=dt-0.3; ang=(14*math.exp(-max(s,0)/0.55)*math.cos(9*max(s,0))) if s>0 else 0
        return L.rotate(ang,center=PIV,resample=Image.BICUBIC)
    ang=-55*min(1,fall/0.7)**1.6; ox=-260*fall; oy=2600*fall**2
    L=L.rotate(ang,center=(PX+20,TOP+14),resample=Image.BICUBIC)
    return L.transform((W,H),Image.AFFINE,(1,0,-ox,0,1,-oy),resample=Image.BICUBIC)
def word(txt,font,col,s,rot=0):
    d=ImageDraw.Draw(Image.new('RGBA',(1,1))); w=int(d.textlength(txt,font=font))+40; h=int(font.size*1.35)
    im=Image.new('RGBA',(w,h),(0,0,0,0)); dd=ImageDraw.Draw(im); dd.text((24,14),txt,font=font,fill=(0,0,0,150)); dd.text((20,8),txt,font=font,fill=col,stroke_width=6,stroke_fill=(24,10,40))
    if s!=1: im=im.resize((max(1,int(w*s)),max(1,int(h*s))),Image.LANCZOS)
    return im.rotate(rot,expand=True,resample=Image.BICUBIC) if rot else im
def old_title(im,lines,t,tout=None):
    # lines: [(text,t_start,color,size)]
    y=285
    for txt,t0,col,sz in lines:
        d_=ImageDraw.Draw(Image.new('RGBA',(1,1)))
        while ImageFont.truetype(AB,sz).getlength(txt)>900: sz-=4
        f=ImageFont.truetype(AB,sz); x=t-t0
        if x<0: y+=int(sz*1.25); continue
        s=ease_out_back(x/0.28)*(1.0+0.35*max(0,1-x/0.12)); 
        if tout is not None and t>tout: s=max(0,1-(t-tout)/0.15)
        if s>0.02:
            w=word(txt,f,col,s,rot=0); im.alpha_composite(w,((W-w.width)//2,y+int((sz*1.25-w.height)/2)))
        y+=int(sz*1.25)
def old_bubble(im,t,t0,quote,who):
    x=t-t0
    if x<0: return
    s=ease_out_back(x/0.3)
    f=ImageFont.truetype(PO,50); nf=ImageFont.truetype(AB,38)
    bw,bh=820,250; L=Image.new('RGBA',(bw+60,bh+120),(0,0,0,0)); d=ImageDraw.Draw(L)
    d.rounded_rectangle((30,36,30+bw,36+bh),44,fill=(0,0,0,110)); d.rounded_rectangle((30,20,30+bw,20+bh),44,fill=WHITE)
    d.polygon([(120,20+bh-4),(190,20+bh-4),(110,20+bh+70)],fill=WHITE)
    words=quote.split(); rows=[]; cur=''
    for w_ in words:
        tr=(cur+' '+w_).strip()
        if d.textlength(tr,font=f)>740 and cur: rows.append(cur); cur=w_
        else: cur=tr
    rows.append(cur); yy=48
    for r in rows: d.text((70,yy),r,font=f,fill=(20,20,36)); yy+=64
    d.text((70,yy+10),who,font=nf,fill=PINK)
    L=L.resize((int(L.width*s),int(L.height*s)),Image.LANCZOS) if s!=1 else L
    im.alpha_composite(L,(int(120+(1-s)*200),1290))


import colorsys
def vivid(h,sv,vv): r,g,b=colorsys.hsv_to_rgb(h%1,sv,vv); return (int(r*255),int(g*255),int(b*255))
def dom_hue(p):
    im=p.convert('RGB').crop((0,0,p.width,int(p.height*0.62))).resize((80,80)); a=np.array(im).astype(float)/255
    hs=np.array([colorsys.rgb_to_hsv(*px) for px in a.reshape(-1,3)]); w=hs[:,1]*hs[:,2]; w=np.where(hs[:,1]>0.35,w,0)
    hist=np.zeros(36)
    for hh,ww in zip(hs[:,0],w): hist[int(hh*36)%36]+=ww
    return (np.argmax(hist)+0.5)/36
def key_hue(h):
    k=(h+0.5)%1
    if 0.08<=k<=0.2: k=(k+0.12)%1        # keep clear of yellow
    return k
_bgc={}
def bgfor(h):
    key=round(h*36)
    if key not in _bgc:
        t=vivid(h,0.78,1.0); b=vivid(h+0.04,0.95,0.72); y=np.linspace(0,1,H)[:,None,None]
        a=np.array(t)[None,None,:]*(1-y)+np.array(b)[None,None,:]*y
        _bgc[key]=Image.fromarray(np.broadcast_to(a,(H,W,3)).astype(np.uint8)).convert('RGBA')
    return _bgc[key]
CUR={'h':0.9}
def title(im,lines,t,tout=None):
    y=285; dd=ImageDraw.Draw(im)
    for txt,t0,col,sz in lines:
        sz=int(sz*1.08)
        while ImageFont.truetype(AB,sz).getlength(txt)>900: sz-=4
        f=ImageFont.truetype(AB,sz); bb=dd.textbbox((0,0),txt,font=f); h=bb[3]-bb[1]+28
        x=t-t0
        if x>=0:
            s=ease_out_back(x/0.28)*(1.0+0.35*max(0,1-x/0.12))
            if tout is not None and t>tout: s=max(0,1-(t-tout)/0.15)
            if s>0.02:
                c=vivid(key_hue(CUR['h']),0.9,1.0) if col==PINK else WHITE
                w_=word(txt,f,c,s,rot=0); im.alpha_composite(w_,((W-w_.width)//2,y+int((h-w_.height)/2)))
        y+=h
    return y
def quote(im,t,t0,tout,q,who,y0):
    x=t-t0
    if x<0 or (tout is not None and t>tout): return
    a=min(1,x/0.18); dy=int((1-ease_out_back(x/0.3))*60)
    L=Image.new('RGBA',(W,260),(0,0,0,0)); d=ImageDraw.Draw(L)
    qs=64
    while ImageFont.truetype(PO,qs).getlength(q)>960: qs-=2
    qf=ImageFont.truetype(PO,qs); wf=ImageFont.truetype(AB,54)
    d.text(((W-qf.getlength(q))/2,0),q,font=qf,fill=WHITE,stroke_width=6,stroke_fill=(24,10,40))
    c=vivid(key_hue(CUR['h']),0.9,1.0); d.text(((W-wf.getlength(who))/2,qs+22),who,font=wf,fill=c,stroke_width=6,stroke_fill=(24,10,40))
    L.putalpha(L.split()[3].point(lambda v:int(v*a))); im.alpha_composite(L,(0,y0+dy))

def flash(im,a):
    if a>0: im.alpha_composite(Image.new('RGBA',(W,H),(255,255,255,int(255*a))))
sys.argv=_a
import build_v15 as v15
from build_v15 import endcard15
b14=v15.b14; T_=b14.txt; ease=v15.ease; RED=v15.RED
def endcard_cal(g):
    fr=Image.new('RGB',(W,H),(0,0,0))
    lw=820; lh=int(b14.logo.height*lw/b14.logo.width); lg=b14.logo.resize((lw,lh),Image.LANCZOS)
    t=ease(g/10); lg2=lg.resize((int(lw*(0.92+0.08*t)),int(lh*(0.92+0.08*t))),Image.LANCZOS)
    fr.paste(lg2,((W-lg2.width)//2,290+(lh-lg2.height)//2)); y=290+lh+50
    if g>=6: T_(fr,'THE GIFT THAT STANDS',y,66,alpha=ease((g-6)/6))
    if g>=14: T_(fr,'TALL ALL YEAR.',y+84,66,alpha=ease((g-14)/6))
    if g>=24: T_(fr,'SHOP NOW',y+210,150,fill=RED,stroke=7,alpha=ease((g-24)/5))
    if g>=34: T_(fr,'ALWAYS STANDING TALL',y+400,58,alpha=ease((g-34)/6),stroke=5)
    if g>=42: T_(fr,'stiffcompetition.shop',y+480,72,alpha=ease((g-42)/6),stroke=5)
    return fr
PER=0.5285
ST=[0,4*PER,8*PER,12*PER]                      # cover, jan, feb, apr
FL0=16*PER; FL1=19*PER; DEC0=FL1; END0=DEC0+4*PER   # flick, dec, end
SC=[('cover',[("YOUR WALL",0.0,WHITE,110),("IS BORING.",PER,PINK,132)],None),
    ('jan',[("STANDING TO",0.0,WHITE,100),("ATTENTION",PER,PINK,132)],("Reporting for duty, all year long.","MAJOR WOOD")),
    ('feb',[("BEHIND THE",0.0,WHITE,100),("VELVET ROPE",PER,PINK,112)],("Roses are red. The rope is velvet.","VELVET PYTHON")),
    ('apr',[("EGG-STRA SPECIAL",0.0,WHITE,100),("DELIVERY",PER,PINK,132)],("Delivered fresh, handled with care.","SLICK WILLY")),
    ('dec',[("NAUGHTY LIST:",0.0,WHITE,100),("ALL SIX",PER,PINK,132)],("Santa checked it twice. We're all on it.","ALL SIX"))]
STS=ST+[DEC0]; ENDS=[ST[1],ST[2],ST[3],FL0,END0]
def scene_frame(i,t,im):
    key,lines,bub=SC[i]; CUR['h']=HUE[key]; t0=STS[i]; t1=ENDS[i]-0.15; p=PGS[key]
    dt=t-t0
    if dt<0: return
    if t<t1: im.alpha_composite(page_layer(p,dt))
    elif t<t1+0.9:
        f_=t-t1; subs=[page_layer(p,dt,fall=f_+k*0.012) for k in range(3)]
        im.alpha_composite(Image.fromarray(np.mean([np.array(q).astype(float) for q in subs],axis=0).astype(np.uint8),'RGBA'))
    if t<t1+0.2 and dt>=0:
        yb=title(im,lines,dt,tout=t1-t0)
        if bub: quote(im,dt,0.95+(0.2 if i==4 else 0),t1-t0,bub[0],bub[1],yb+10)
    if abs(t-t0)<0.08 and i>0: flash(im,0.25*(1-abs(t-t0)/0.08))
HUE=dict(cover=0.60,jan=0.53,feb=0.92,apr=0.34,dec=0.99)
ALLH=[(0.55+k*0.083)%1 for k in range(12)]
def frame(f):
    t=f/FPS
    if t>=END0: return endcard_cal(f-int(END0*FPS))
    cur=0
    for i in range(5):
        if STS[i]<=t: cur=i
    hk=HUE[SC[cur][0]]
    if FL0<=t<FL1: hk=ALLH[min(int((t-FL0)/((FL1-FL0)/12)),11)]
    elif t>=DEC0-0.0: hk=HUE['dec']
    im=bgfor(hk).copy()
    CUR['h']=hk
    for i in range(5):
        if i==4 and t<STS[4]-1.2: continue
        if i<4 and t>ENDS[i]+1.0: continue
        if i==4 and t<STS[4]: continue
        scene_frame(i,t,im)
    if FL0<=t<FL1:
        k=int((t-FL0)/((FL1-FL0)/12)); x=(t-FL0)-k*((FL1-FL0)/12)
        p=ALL[min(k,11)]; sc=1.06-0.06*min(1,x/0.07); tilt=(2.2 if k%2 else -2.2)
        L=Image.new('RGBA',(W,H),(0,0,0,0)); q=p.resize((int(PW*sc),int(p.height*sc)),Image.LANCZOS)
        L.alpha_composite(q,((W-q.width)//2,TOP+int((p.height-q.height)/2)))
        im.alpha_composite(L.rotate(tilt,center=PIV,resample=Image.BICUBIC))
        CUR['h']=hk; title(im,[("12 MONTHS.",0.0,WHITE,120),("6 LEGENDS.",0.0,PINK,132)],t-FL0+0.2)
        if x<0.04: flash(im,0.2)
    return im.convert('RGB')
import os
if __name__=='__main__':
    if os.environ.get('STILLS'):
        ts=[1.3,3.4,5.6,7.6,8.9,9.3,11.6,13.5]
        sh=Image.new('RGB',(len(ts)*270+10,500),(20,20,20))
        for i,t in enumerate(ts): sh.paste(frame(int(t*FPS)).resize((260,462),Image.LANCZOS),(10+i*270,10))
        sh.save('cal_full_sheet.png'); sys.exit()
    TT=15.0
    p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i','fan2.mp3','-map','0:v','-map','1:a','-t',str(TT),'-c:v','libx264','-preset','veryfast','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-af',f'afade=t=out:st={TT-0.7}:d=0.7','-movflags','+faststart','SC_calendar_ad_v3.mp4'],stdin=subprocess.PIPE)
    for f in range(int(TT*FPS)): p.stdin.write(frame(f).tobytes())
    p.stdin.close(); p.wait(); print('done')
