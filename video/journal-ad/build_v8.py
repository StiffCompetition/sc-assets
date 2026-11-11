import numpy as np, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H=1080,1920; FPS=30; N=240
SAFE_TOP,SAFE_BOT=272,1246
FONT='node_modules/@fontsource/inter/files/inter-latin-900-normal.woff'
def F(sz): return ImageFont.truetype(FONT,sz)
RED=(227,28,29); WHITE=(255,255,255)
logo=Image.open('logo.png').convert('RGB')
PH=1400; Y0=236; E=150
fy=np.ones(PH,np.float32); fy[:E]=np.linspace(0,1,E)**1.3; fy[-E:]=np.linspace(1,0,E)**1.3
FADE=Image.fromarray((np.tile(fy[:,None],(1,W))*255).astype(np.uint8))
def ease(t): t=max(0,min(1,t)); return t*t*(3-2*t)
def shot(img,cx,cy,cw,alpha=1.0):
    ch=cw*PH/W
    box=(int(cx-cw/2),int(cy-ch/2),int(cx+cw/2),int(cy+ch/2))
    crop=img.crop(box).resize((W,PH),Image.LANCZOS)
    fr=Image.new('RGB',(W,H),(0,0,0))
    m=FADE if alpha>=1 else FADE.point(lambda v:int(v*alpha))
    fr.paste(crop,(0,Y0),m); return fr
def txt(fr,text,y,size,fill=WHITE,stroke=7,scale=1.0,alpha=1.0):
    """centred text, top at y; stays inside safe area (asserted)"""
    sz=int(size*scale); lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    while True:
        f=F(sz); bb=d.textbbox((0,0),text,font=f,stroke_width=stroke)
        if bb[2]-bb[0]<=940: break
        sz-=2
    w=bb[2]-bb[0]; x=(W-w)//2-bb[0]; yy=y-bb[1]
    assert x+bb[0]>=65 and x+bb[2]<=W-65,(text,x+bb[0],x+bb[2])
    d.text((x,yy),text,font=f,fill=fill+(int(255*alpha),),stroke_width=stroke,stroke_fill=(0,0,0,int(255*alpha)))
    fr.paste(lay,(0,0),lay)
def words(fr,text,y,size,shown,**k):
    ws=text.split(' ')
    if shown<=0: return
    txt(fr,' '.join(ws[:shown]),y,size,**k)
def wa(g,s,st,n): return min(n,0 if g<s else 1+(g-s)//st)
def endcard(g):
    fr=Image.new('RGB',(W,H),(0,0,0))
    lw=820; lh=int(logo.height*lw/logo.width); lg=logo.resize((lw,lh),Image.LANCZOS)
    t=ease(g/10); lg2=lg.resize((int(lw*(0.9+0.1*t)),int(lh*(0.9+0.1*t))),Image.LANCZOS)
    fr.paste(lg2,((W-lg2.width)//2,300+(lh-lg2.height)//2))
    y=300+lh+50
    if g>=4: txt(fr,'THE FIELD JOURNAL',y,92,alpha=ease((g-4)/6))
    if g>=10:
        s=0.85+0.15*ease((g-10)/6); txt(fr,'ORDER NOW',y+120,138,fill=RED,stroke=8,scale=s,alpha=ease((g-10)/5))
    if g>=18: txt(fr,'ALWAYS STANDING TALL',y+300,60,alpha=ease((g-18)/8),stroke=5)
    if g>=24: txt(fr,'stiffcompetition.shop',y+385,52,alpha=ease((g-24)/8),stroke=4)
    return fr

import cv2
V8='/tmp/jf/v8/'
PER=0.6006; B0=0.07
def bf(k): return round((B0+PER*k)*FPS)
END=13.4; N=int(END*FPS)
desk=Image.open(V8+'desk_cover.png').convert('RGB'); flat=Image.open(V8+'flat_cover.png').convert('RGB')
bd=Image.open(V8+'bright_desk.png').convert('RGB')
bg=bd.crop((436,0,1444,1792)).resize((W,H),Image.LANCZOS).filter(ImageFilter.GaussianBlur(28))
bg=Image.blend(bg,Image.new('RGB',(W,H),(255,236,190)),0.35)
names=['card','squad','map','woodprofile','day_hammer','day_thrust','sunday1','day_hammer2','sunday2','mission1','debrief','cert']
pages={n:Image.open(V8+f'pg_{n}.png').convert('RGB') for n in names}
def cover(img,cx,cy,t):
    cw=1008-int(60*t); ch=cw*16//9
    box=(int(cx-cw/2),int(cy-ch/2),int(cx+cw/2),int(cy+ch/2))
    box=(max(0,min(box[0],img.width-cw)),max(0,min(box[1],img.height-ch)),0,0)
    box=(box[0],box[1],box[0]+cw,box[1]+ch)
    return img.crop(box).resize((W,H),Image.LANCZOS)
PHT=840
def page(n,t,tilt):
    pg=pages[n]; hh=int(PHT*(1+0.05*t)); ww=int(hh*pg.width/pg.height)
    p=pg.resize((ww,hh),Image.LANCZOS)
    lay=Image.new('RGBA',(ww+160,hh+160),(0,0,0,0))
    sh=Image.new('RGBA',lay.size,(0,0,0,0)); ImageDraw.Draw(sh).rectangle((80,100,80+ww,100+hh),fill=(0,0,0,150))
    sh=sh.filter(ImageFilter.GaussianBlur(24)); lay.alpha_composite(sh)
    lay.paste(p,(80,80))
    lay=lay.rotate(tilt,resample=Image.BICUBIC,expand=True)
    fr=bg.copy(); fr.paste(lay,((W-lay.width)//2,818-lay.height//2),lay); return fr
def caption(fr,text,g,color=WHITE):
    txt(fr,text,SAFE_TOP+14,88 if len(text)>10 else 104,fill=color,stroke=8,alpha=ease(g/3))
shots=[('cov',desk,0,2),]
seq=[('c',0,2)]+[('p',n,2+i,3+i) for i,n in enumerate(names)]+[('c',1,14,15)]
def frame(f):
    if f>=bf(15): return endcard(f-bf(15))
    k=max(0,min(14,int((f/FPS-B0)//PER)))
    g=f-bf(k)
    if k<2:
        t=(f-bf(0))/(bf(2)-bf(0)); fr=cover(desk,940,930,ease(t)); cap=('52 WEEKS OF MISSIONS',f-bf(0),WHITE)
    elif k<14:
        n=names[k-2]; t=g/(bf(k+1)-bf(k)); fr=page(n,t,(-2.2 if k%2 else 2.2)); 
        cap=('52 WEEKS OF MISSIONS',g,WHITE) if k<4 else ('A PAGE FOR EVERY DAY',g if k==4 else 9,WHITE)
        if k==2 or k==3: cap=('52 WEEKS OF MISSIONS',9,WHITE)
    else:
        t=(f-bf(14))/(bf(15)-bf(14)); fr=cover(flat,975,930,ease(t)); cap=('ORDER NOW',g,RED)
    caption(fr,*cap)
    if k<14 and g<2 and k>0: fr=Image.blend(fr,Image.new('RGB',(W,H),(255,255,255)),0.35*(1-g/2))
    return fr
if __name__=='__main__':
    import sys
    if len(sys.argv)>1:
        for f in map(int,sys.argv[1:]): frame(f).save(f'/tmp/jf/work/v8f{f}.png')
        sys.exit()
    p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','30','-i','-','-i','fan1.mp3','-map','0:v','-map','1:a','-c:v','libx264','-preset','veryfast','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-af',f'afade=t=out:st={END-0.7}:d=0.7','-t',str(END),'-movflags','+faststart','SC_journal_preorder_v8.mp4'],stdin=subprocess.PIPE)
    for f in range(N): p.stdin.write(frame(f).tobytes())
    p.stdin.close(); p.wait()
