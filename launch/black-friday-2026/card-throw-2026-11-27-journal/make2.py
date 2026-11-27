import subprocess,numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFile
from scipy.io import wavfile
from scipy.signal import butter,lfilter
ImageFile.LOAD_TRUNCATED_IMAGES=True
W,H=1080,1920; FPS=30
V='/tmp/bfdl/BF_MajorWood_final_v7.mp4'
T1=6.45; SEG=1.5; N=4; PL=6.0; BODY0=4.96; END0=10.96
FB="/usr/share/fonts/opentype/inter/Inter-Black.otf"
def eo3(x): x=min(max(x,0),1); return 1-(1-x)**3
def eob(x,k=1.9):
    x=min(max(x,0),1); return 1+(k+1)*(x-1)**3+k*(x-1)**2
def tl(t,size,fill,sw):
    d=ImageDraw.Draw(Image.new('RGBA',(10,10))); f=ImageFont.truetype(FB,size); w=int(d.textlength(t,font=f))+2*sw+10
    im=Image.new('RGBA',(w,size+2*sw+60),(0,0,0,0))
    ImageDraw.Draw(im).text((sw+5,sw),t,font=f,fill=fill,stroke_width=sw,stroke_fill=(0,0,0)); return im.crop(im.getbbox())
def fit(t,size,fill,sw,maxw=960):
    while True:
        im=tl(t,size,fill,sw)
        if im.width<=maxw: return im
        size-=2
A=fit("UP TO 30% OFF",190,(255,255,255),9); B=fit("PRICES DROP.",100,(255,255,255),7); C=fit("MAJOR WOOD STAYS UP.",66,(255,196,90),6)
def place(im,l,cx,y): im.alpha_composite(l,(int(cx-l.width/2),int(y)))
wm=Image.open('wm_new.png').convert('RGBA')
def frame_at(t):
    raw=subprocess.run(['ffmpeg','-loglevel','error','-ss',str(t),'-i',V,'-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout
    return Image.frombytes('RGB',(W,H),raw)
before=frame_at(T1-1/FPS)
from PIL import ImageFilter,ImageDraw
ORDER=['mug','tee','bottle','poster','jcover','ringer','jpages','xmas']
N=len(ORDER); STEP=0.6; THROW=0.22; FAN=N*STEP; PLEN=6.0
CW,CH,B_=960,1000,18; CX,CY=540,1140
def card(n):
    p=Image.open(f'/tmp/bfpics/{n}.jpg').convert('RGB')
    iw,ih=CW-2*B_,CH-2*B_; r=iw/ih
    if n.endswith('xmas'):
        h=int(p.height*0.89); w=int(h*r); pad=(w-p.width)//2
        p=Image.fromarray(np.pad(np.array(p.crop((0,0,p.width,h))),((0,0),(pad,w-p.width-pad),(0,0)),mode='edge'))
    elif p.width/p.height<r: p=p.crop((0,0,p.width,int(p.width/r)))
    else:
        w=int(p.height*r); x=(p.width-w)//2; p=p.crop((x,0,x+w,p.height))
    col=p.resize((1,1),Image.BOX,box=(0,0,p.width,12)).getpixel((0,0))
    p=p.resize((iw,ih),Image.LANCZOS)
    c=Image.new('RGBA',(CW,CH),(0,0,0,0)); ImageDraw.Draw(c).rounded_rectangle((0,0,CW-1,CH-1),44,fill=(255,255,255,255))
    m=Image.new('L',(iw,ih),0); ImageDraw.Draw(m).rounded_rectangle((0,0,iw-1,ih-1),30,fill=255); c.paste(p,(B_,B_),m)
    return c,col
cards,cols=zip(*[card(n) for n in ORDER])
def put(base,c,cx,cy,ang=0,sc=1.0,shadow=True):
    if sc!=1.0: c=c.resize((int(c.width*sc),int(c.height*sc)),Image.LANCZOS)
    if ang: c=c.rotate(ang,Image.BICUBIC,expand=True)
    x,y=int(cx-c.width/2),int(cy-c.height/2)
    if shadow:
        pad=60; sh=Image.new('RGBA',(c.width+2*pad,c.height+2*pad),(0,0,0,0))
        sh.paste((0,0,0,120),(pad,pad),c.getchannel('A')); sh=sh.filter(ImageFilter.GaussianBlur(22))
        base.paste(sh,(x-pad+8,y-pad+22),sh)
    base.paste(c,(x,y),c)
yy,xx=np.mgrid[0:H,0:W]
light=np.clip(1-np.sqrt((xx-540)**2+(yy-1100)**2)/1400,0,1)[...,None]
def bg(col):
    c=np.array(col,float)
    return Image.fromarray(np.clip(c*(0.30+0.55*light),0,255).astype(np.uint8)).convert('RGBA')
bgs=[bg(c) for c in cols]; bgfan=bg((190,30,50))
TILT=[0,-5,4]
def stack(t):
    k=min(int(t/STEP),N-1); u=t-k*STEP
    q=eo3((u-(STEP-THROW))/THROW) if u>STEP-THROW and k<N-1 else 0
    b=Image.blend(bgs[k],bgs[min(k+1,N-1)],q) if q else bgs[k].copy()
    for d in (2,1):
        if k+d<N: put(b,cards[k+d],CX,CY,TILT[d]*(1-q if d==1 else 1),1-0.035*d+(0.035*q if d==1 else 0))
    if q:
        side=1 if k%2==0 else -1; e=((u-(STEP-THROW))/THROW)**1.6
        put(b,cards[k],CX+side*1350*e,CY-220*e,-side*38*e)
    else: put(b,cards[k],CX,CY)
    return b
SLOTS=[(210,800,-6),(540,775,0),(870,800,6),(360,1140,-3),(720,1140,3),(210,1480,5),(540,1505,0),(870,1480,-5)]
def fan(t):
    q=eo3(t/0.4); b=Image.blend(bgs[-1],bgfan,min(1,q))
    for j,(x,y,a) in enumerate(SLOTS):
        s=1+(0.33-1)*q
        put(b,cards[j],CX+(x-CX)*q,CY+(y-CY)*q,a*q,s)
    return b
def scene(t):
    if t<FAN:
        im=stack(t)
        if t<0.3:
            out=before.convert('RGB'); off=int((1-eo3(t/0.3))*H); out.paste(im.convert('RGB'),(0,off)); im=out.convert('RGBA')
        return im
    return fan(t-FAN)
def prod(i):
    t=i/FPS; u=t%STEP
    moving=(t<FAN and u>STEP-THROW) or (FAN<=t<FAN+0.4)
    if moving:
        s=[np.array(scene(t+d/(FPS*3)).convert('RGB'),float) for d in range(3)]
        base=Image.fromarray((sum(s)/3).astype(np.uint8)).convert('RGBA')
    else: base=scene(t).convert('RGBA')
    bt=T1+t-BODY0
    place(base,A,W/2,280); place(base,B,W/2,400)
    uu=(bt-1.4)/0.35; x=W/2-(1-eo3(uu))*1200; dy=-14*eob((bt-1.75)/0.2,2.5) if bt>1.75 else 0
    place(base,C,x,530+dy)
    base.alpha_composite(wm)
    return base.convert('RGB')
p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','30','-i','-','-c:v','libx264','-crf','16','-pix_fmt','yuv420p','prod.mp4'],stdin=subprocess.PIPE)
for i in range(int(PLEN*FPS)): p.stdin.write(prod(i).tobytes())
p.stdin.close(); p.wait()
# sound: same music and slams as the finals, plus a swoosh on each product change
sr=44100; total=T1+PLEN+(13.46-11.03); E=T1+PLEN
out=np.zeros(int(total*sr)+sr); rng=np.random.default_rng(3)
def thump(t0,amp=1.0,f0=130,f1=48,dur=0.28):
    n=int(dur*sr); t=np.arange(n)/sr; ph=2*np.pi*np.cumsum(f1+(f0-f1)*np.exp(-t*18))/sr
    s=amp*(np.sin(ph)*np.exp(-t*11)+rng.standard_normal(n)*np.exp(-t*90)*0.5); i=int(t0*sr); out[i:i+n]+=s[:len(out)-i]
def whoosh(t0,dur=0.45,amp=0.5):
    n=int(dur*sr); t=np.arange(n)/sr; x=rng.standard_normal(n); k=np.exp(-((t-dur*0.55)/(dur*0.28))**2)
    b,a=butter(2,[400/(sr/2),4000/(sr/2)],'band'); x=lfilter(b,a,x)*k*amp; i=int(t0*sr); out[i:i+n]+=x[:len(out)-i]
for t0,a in [(5.49,1.0),(5.84,0.6),(6.44,0.7),(T1+0.3,0.9),(T1+FAN+0.3,1.0)]: thump(t0,a)
whoosh(5.2,amp=0.4); whoosh(T1-0.1)
for k in range(1,N): whoosh(T1+k*STEP-THROW-0.02,dur=0.24,amp=0.65); thump(T1+k*STEP,0.3)
whoosh(T1+FAN-0.05,dur=0.4,amp=0.7)
wavfile.write('sfx.wav',sr,(np.tanh(out*0.9)*0.8*32767).astype(np.int16))
fc=(f"[0:v]trim=0:{T1},setpts=PTS-STARTPTS,fps=30,format=yuv420p[a];[1:v]fps=30,format=yuv420p[b];"
    f"[0:v]trim=11.03:13.46,setpts=PTS-STARTPTS,fps=30,format=yuv420p[c];[a][b][c]concat=n=3:v=1[v];"
    f"[2:a]atrim=0.46:{0.46+total},asetpts=PTS-STARTPTS,adelay=40|40,afade=t=out:st={total-1.8}:d=1.8[m];"
    f"[3:a]aformat=channel_layouts=stereo[s];[4:a]atrim=10.99:13.49,asetpts=PTS-STARTPTS,aformat=channel_layouts=stereo,adelay={int((E+0.01)*1000)}|{int((E+0.01)*1000)}[e];"
    f"[m][s][e]amix=inputs=3:duration=longest:normalize=0,alimiter=limit=0.95,atrim=0:{total}[au]")
subprocess.run(['ffmpeg','-y','-loglevel','error','-i',V,'-i','prod.mp4','-i','music.wav','-i','sfx.wav','-i','sfx_endA.wav','-filter_complex',fc,'-map','[v]','-map','[au]','-c:v','libx264','-crf','18','-c:a','aac','-b:a','192k','-ar','44100','-movflags','+faststart','BF_MajorWood_cardthrow.mp4'],check=True)
