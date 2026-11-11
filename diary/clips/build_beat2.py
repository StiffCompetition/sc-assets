import subprocess, sys, math, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import build_hanky9 as b
W,H,FPS=1080,1920,30
SRC=sys.argv[1] if len(sys.argv)>1 else 'beat/beat1080.mp4'
OUT=sys.argv[2] if len(sys.argv)>2 else 'hk10_segBeat.mp4'
SS,DUR=0.0,5.0
PM='/home/claude/sc-assets/diary/locked/tools/permanent-marker.ttf'
INK=(38,40,52)
raw=subprocess.run(['ffmpeg','-v','error','-ss',str(SS),'-t',str(DUR),'-i',SRC,'-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout
fr=np.frombuffer(raw,dtype=np.uint8).reshape(-1,H,W,3); N=len(fr); print('frames',N)
def ease(x): x=min(1,max(0,x)); return x*x*(3-2*x)
def overshoot(x):
    x=min(1,max(0,x)); c=1.70158; return 1+(c+1)*(x-1)**3+c*(x-1)**2
def grade(a):
    x=a.astype(np.float32)/255
    x=np.where(x>0.68,0.68+(x-0.68)*0.5,x)          # tame plastic highlights
    x=x*0.97+0.025                                    # matt lift
    g=x.mean(axis=2,keepdims=True); x=g+(x-g)*0.94
    return (np.clip(x,0,1)*255).astype(np.uint8)
# ---- cloud
rng=np.random.default_rng(5)
CW,CH=980,470
def make_cloud():
    cx,cy=CW/2,CH/2
    m=Image.new('L',(CW,CH),0); d=ImageDraw.Draw(m)
    d.ellipse((cx-360,cy-140,cx+360,cy+140),fill=255)
    n=18
    for k in range(n):
        a=2*math.pi*k/n; rx,ry=385,150
        r=rng.uniform(78,118); x=cx+rx*math.cos(a); y=cy+ry*math.sin(a)
        d.ellipse((x-r,y-r*0.9,x+r,y+r*0.9),fill=255)
    core=m.filter(ImageFilter.GaussianBlur(4))
    haze=m.filter(ImageFilter.GaussianBlur(30)).point(lambda v:int(v*0.55))
    cl=Image.new('RGBA',(CW,CH),(236,240,250,0)); cl.putalpha(haze)
    body=Image.new('RGBA',(CW,CH),(255,255,255,0)); body.putalpha(core.point(lambda v:int(v*0.93)))
    cl.alpha_composite(body)
    # soft inner shading, hand-inked faint outline wobble
    ol=Image.new('RGBA',(CW,CH),(0,0,0,0)); od=ImageDraw.Draw(ol)
    arr=np.array(core)>128
    edge=np.array(Image.fromarray((arr*255).astype('uint8')).filter(ImageFilter.FIND_EDGES))>0
    ys,xs=np.where(edge); 
    for x,y in zip(xs[::2],ys[::2]): od.point((x,y),fill=(120,130,150,90))
    ol=ol.filter(ImageFilter.GaussianBlur(1.6)); cl.alpha_composite(ol)
    return cl
CLOUD=make_cloud()
BX,BY=540,300     # cloud centre
def puff(r):
    s=int(r*3.4); im=Image.new('RGBA',(s,s),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.ellipse((s/2-r,s/2-r,s/2+r,s/2+r),fill=(255,255,255,235))
    gl=im.filter(ImageFilter.GaussianBlur(r*0.5)); gl=Image.new('RGBA',(s,s),(236,240,250,0)).copy(); 
    h=Image.new('L',(s,s),0); ImageDraw.Draw(h).ellipse((s/2-r,s/2-r,s/2+r,s/2+r),fill=255)
    hz=h.filter(ImageFilter.GaussianBlur(r*0.45)).point(lambda v:int(v*0.5)); gl.putalpha(hz); gl.alpha_composite(im.filter(ImageFilter.GaussianBlur(1.2)))
    return gl
PUFFS=[((690,525),20,0.5),((662,480),30,0.7),((628,438),44,0.9)]
PUFFIM=[puff(r) for _,r,_ in PUFFS]
# ---- text layers (written-on reveal)
def text_layer(txt,size,cx,cy,outline=6):
    f=ImageFont.truetype(PM,size)
    L=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(L)
    d.text((cx,cy),txt,font=f,fill=INK+(255,),anchor='mm',stroke_width=outline,stroke_fill=(255,255,255,0))
    bb=d.textbbox((cx,cy),txt,font=f,anchor='mm'); return L,bb
T1,B1=text_layer("WHAT'S SHRUNK",92,BX,BY-52); T2,B2=text_layer("ON YOU?",106,BX,BY+58)
T3,B3=text_layer("COMMENT BELOW",84,540,1436,0)
def reveal(L,bb,p):
    a=np.array(L); x1=int(bb[0]-10+(bb[2]-bb[0]+20)*p); a[:,x1:,3]=0; return Image.fromarray(a)
# outlined version of comment text for readability on busy background
def outlined(txt,size,cx,cy):
    f=ImageFont.truetype(PM,size); L=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(L)
    d.text((cx,cy),txt,font=f,fill=(255,255,255,255),anchor='mm',stroke_width=12,stroke_fill=(255,255,255,255))
    d.text((cx,cy),txt,font=f,fill=INK+(255,),anchor='mm'); return L,d.textbbox((cx,cy),txt,font=f,anchor='mm')
T3,B3=outlined("COMMENT BELOW",84,540,1436)
# ---- squiggle path
pts=[]
for i in range(260):
    u=i/259; x=70+u*880; y=1500+46*math.sin(u*math.pi*5.5)*(1-0.45*u)+rng.normal(0,0.6)
    pts.append((x,y))
ax,ay=pts[-1]
arrow=[(ax,ay),(ax+30,ay+40),(ax+14,ay+80)]    # curls down: leads to comments
def squiggle(p):
    L=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(L)
    k=int(len(pts)*min(1,p/0.82)); seg=pts[:max(2,k)]
    d.line(seg,fill=(255,255,255,255),width=26,joint='curve')
    d.line(seg,fill=INK+(255,),width=13,joint='curve')
    if p>0.82:
        q=(p-0.82)/0.18; n=max(2,int(q*30)); cc=[]
        for j in range(n):
            u=j/29; cc.append((ax+30*math.sin(u*math.pi*0.5)+14*u*(1-u)*0, ay+80*u))
        d.line([(ax,ay)]+cc,fill=(255,255,255,255),width=26,joint='curve'); d.line([(ax,ay)]+cc,fill=INK+(255,),width=13,joint='curve')
        if q>0.9:
            ex,ey=cc[-1]
            for hx in (-34,34): d.line([(ex,ey),(ex+hx,ey-30)],fill=(255,255,255,255),width=26); d.line([(ex,ey),(ex+hx,ey-30)],fill=INK+(255,),width=13)
    return L
def frame(i):
    t=i/FPS
    im=Image.fromarray(grade(fr[i])).convert('RGBA')
    L=Image.new('RGBA',(W,H),(0,0,0,0))
    # trailing puffs
    for (pos,r,st),pi in zip(PUFFS,PUFFIM):
        s=overshoot((t-st)/0.28)
        if s>0.02:
            w=int(pi.width*s); 
            if w>2: q=pi.resize((w,w),Image.BILINEAR); L.alpha_composite(q,(int(pos[0]-w/2),int(pos[1]-w/2+3*math.sin(t*3+r))))
    # cloud pop + float
    s=overshoot((t-1.05)/0.45)
    if s>0.02:
        fl=1+0.012*math.sin(t*2.6); w=int(CW*s*fl); h=int(CH*s*fl)
        if w>4 and h>4:
            q=CLOUD.resize((w,h),Image.BILINEAR); L.alpha_composite(q,(int(BX-w/2),int(BY-h/2+7*math.sin(t*2.0))))
    im.alpha_composite(L)
    off=int(7*math.sin(t*2.0)) if t>1.5 else 0
    tl=Image.new('RGBA',(W,H),(0,0,0,0))
    p1=ease((t-1.6)/0.8); p2=ease((t-2.4)/0.6)
    if p1>0: tl.alpha_composite(reveal(T1,B1,p1))
    if p2>0: tl.alpha_composite(reveal(T2,B2,p2))
    if off: tl=tl.transform(tl.size,Image.AFFINE,(1,0,0,0,1,-off))
    im.alpha_composite(tl)
    ps=(t-3.2)/0.9
    if ps>0: im.alpha_composite(squiggle(min(1,ps)))
    p3=ease((t-4.0)/0.7)
    if p3>0: im.alpha_composite(reveal(T3,B3,p3))
    im=b.wm(im)
    k=min(1,t/0.35)*min(1,(DUR-t)/0.35)
    if k<1: im=Image.blend(Image.new('RGB',(W,H),(0,0,0)),im,max(0,k))
    return im
p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','30','-i','-','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p',OUT],stdin=subprocess.PIPE)
for i in range(N): p.stdin.write(frame(i).tobytes())
p.stdin.close();p.wait()
for tt in (1.3,2.4,3.6,4.5):
    frame(int(tt*FPS)).save(f'/tmp/b2_{tt}.png')
