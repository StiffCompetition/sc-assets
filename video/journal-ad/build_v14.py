import sys, math
from build_v9 import *
import build_v9 as b9
END=15.0; N=int(END*FPS)
PER=0.5285; B0=0.25
def bf(k): return round((B0+PER*k)*FPS)
V8='/tmp/jf/v8/'
faces=[Image.open(V8+f'up_{n}.png').convert('RGB') for n in ['beard_shout','shout','masked','sailor','hardhat','blonde_beard']]
faces[2]=Image.open(V8+'masked_fixed.png').convert('RGB').crop((25,0,1200,1186))
# rays background
def rays():
    import numpy as np
    yy,xx=np.mgrid[0:H,0:W]; a=np.arctan2(yy-800,xx-540); s=((a+math.pi)/(2*math.pi)*26).astype(int)%2
    im=np.zeros((H,W,3),np.uint8); im[s==0]=(30,62,190); im[s==1]=(222,40,150)
    return Image.fromarray(im)
RAYS=rays()
def band(fr,text,y,g,color=(227,28,29),size=92):
    d=ImageDraw.Draw(fr); sz=size
    while True:
        f=F(sz); bb=d.textbbox((0,0),text,font=f)
        if bb[2]-bb[0]<=900: break
        sz-=2
    w=bb[2]-bb[0]; h=bb[3]-bb[1]; pad=26
    a=ease(g/2.5)
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); dl=ImageDraw.Draw(lay)
    dl.rectangle((0,y,W,y+h+2*pad),fill=color+(int(255*a),))
    dl.text(((W-w)//2-bb[0],y+pad-bb[1]),text,font=f,fill=(255,255,255,int(255*a)))
    fr.paste(lay,(0,0),lay)
def faceshot(i,t,g):
    im=faces[i]; w=960; h=int(im.height*w/im.width)
    p=im.resize((w,h),Image.LANCZOS); B=18
    pan=Image.new('RGBA',(w+2*B,h+2*B),(255,255,255,255)); pan.paste(p,(B,B))
    lay=Image.new('RGBA',(pan.width+160,pan.height+160),(0,0,0,0))
    sh=Image.new('RGBA',lay.size,(0,0,0,0)); ImageDraw.Draw(sh).rectangle((80,100,80+pan.width,100+pan.height),fill=(0,0,0,170))
    lay.alpha_composite(sh.filter(ImageFilter.GaussianBlur(20))); lay.alpha_composite(pan,(80,80))
    lay=lay.rotate(2.5 if i%2==0 else -2.5,resample=Image.BICUBIC,expand=True)
    fr=RAYS.copy(); fr.paste(lay,((W-lay.width)//2,700-lay.height//2),lay); return fr
TOP=set()
SEQ=[('card',1560),('F',0),('02-squad',1560),('F',1),('03-map',625),('F',2),('05-day-tue',625),('F',3),('06-day-fri',625),('F',4),('08-certificate',1560),('F',5)]
TXT={2:"I'D LIKE TO ENLIST",3:'PLEASE SEND THE SQUAD',8:'AND MY OWN MISSIONS',12:'AND A CERTIFICATE.'}
SEQ[0]=('01-card',1560)
YEL=(255,222,0); NAVY=(16,24,78)
PL_T,PL_B=292,572
CAPS=[("DEAR\nSANTA,","SANTA,"),("I'D LIKE\nTO ENLIST","ENLIST"),("PLEASE SEND\nTHE SQUAD","SQUAD"),("AND MY OWN\nMISSIONS","MISSIONS"),("AND A\nCERTIFICATE.","CERTIFICATE.")]
PLATE=[0]
def plate(fr,text,key,g):
    d0=ImageDraw.Draw(fr); sz=128
    while True:
        f=F(sz); ws=[d0.textbbox((0,0),l,font=f)[2] for l in text.split("\n")]
        if max(ws)<=960: break
        sz-=4
    a=ease(g/5.0)
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    d.rectangle((0,PL_T,W,PL_B),fill=NAVY+(int(255*a),))
    d.rectangle((0,PL_B,W,PL_B+10),fill=YEL+(int(255*a),)); d.rectangle((0,PL_T-10,W,PL_T),fill=YEL+(int(255*a),))
    lines=text.split("\n"); lh=int(sz*1.04); y=PL_T+((PL_B-PL_T)-lh*len(lines))//2
    pop=1+0.10*(1-ease(g/4.0))
    for l in lines:
        bb=d.textbbox((0,0),l,font=f); x=(W-(bb[2]-bb[0]))//2-bb[0]
        d.text((x,y-bb[1]//3),l,font=f,fill=(YEL if key in l else (255,255,255))+(int(255*a),)); y+=lh
    fr.paste(lay,(0,0),lay)
imgs14={}
def pagecrop2(n,cx,t,dy):
    cw=int(940-90*t); ch=cw*16//9; cy=1593-dy; cx=max(cw//2,min(2160-cw//2,cx))
    return b9.imgs[n].crop((cx-cw//2,cy-ch//2,cx+cw//2,cy+ch//2)).resize((W,H),Image.LANCZOS)
def faceshot2(i,t,g):
    im=faces[i]; w=900; h=int(im.height*w/im.width)
    p=im.resize((w,h),Image.LANCZOS); B=16
    pan=Image.new('RGBA',(w+2*B,h+2*B),(255,255,255,255)); pan.paste(p,(B,B))
    lay=Image.new('RGBA',(pan.width+160,pan.height+160),(0,0,0,0))
    sh=Image.new('RGBA',lay.size,(0,0,0,0)); ImageDraw.Draw(sh).rectangle((80,100,80+pan.width,100+pan.height),fill=(0,0,0,170))
    lay.alpha_composite(sh.filter(ImageFilter.GaussianBlur(20))); lay.alpha_composite(pan,(80,80))
    lay=lay.rotate(2.5 if i%2==0 else -2.5,resample=Image.BICUBIC,expand=True)
    sc=1.04-0.04*ease(t)
    if sc!=1: lay=lay.resize((int(lay.width*sc),int(lay.height*sc)),Image.LANCZOS)
    fr=RAYS.copy(); fr.paste(lay,((W-lay.width)//2,PL_B+30-int(80*sc)),lay); return fr
def cover2(img,cx,cy,t,s=0.66):
    full=cover(img,cx,cy,0.0); s=s+0.05*t
    bg=full.crop((0,0,36,H)).resize((W,H),Image.BICUBIC).filter(ImageFilter.GaussianBlur(24))
    fw,fh=int(W*s),int(H*s); fg=full.resize((fw,fh),Image.LANCZOS)
    m=Image.new('L',(fw,fh),0); ImageDraw.Draw(m).rectangle((34,34,fw-34,fh-34),fill=255); m=m.filter(ImageFilter.GaussianBlur(18))
    x=(W-fw)//2; y=PL_B+10-int(fh*0.17)
    bg.paste(fg,(x,y),m); return bg
SHOTS=[('cover',None),('01-card',1560),('F',0),('02-squad',1560),('F',1),('05-day-tue',625),('F',2),('08-certificate',1560),('F',3)]
DY={'01-card':300,'02-squad':250,'05-day-tue':250,'08-certificate':300}
SPAN=[4,2,2,2,2,2,2,2,2]   # beats per shot
STARTS=[sum(SPAN[:i]) for i in range(len(SPAN))]
CAPSTART={0:0,1:1,3:2,5:3,7:4}  # shot index -> caption index
def frame10(f):
    if f>=bf(20): return endcard10(f-bf(20))
    i=max([k for k in range(len(SHOTS)) if f>=bf(STARTS[k])] or [0]); g=max(0,f-bf(STARTS[i])); t=g/(bf(STARTS[i]+SPAN[i])-bf(STARTS[i]))
    kind,arg=SHOTS[i]
    if kind=='cover': fr=cover2(desk,940,800,ease(t))
    elif kind=='F': fr=faceshot2(arg,t,g)
    else: fr=pagecrop2(kind,arg,t,DY[kind])
    ci=max(c for s_,c in CAPSTART.items() if s_<=i)
    cs=[s_ for s_,c in CAPSTART.items() if c==ci][0]
    if i==0: ci=0
    plate(fr,CAPS[ci][0],CAPS[ci][1],max(0,f-bf(STARTS[cs])))
    if g<2 and i>0: fr=Image.blend(fr,Image.new('RGB',(W,H),(255,255,255)),0.25*(1-g/2))
    return fr
def endcard10(g):
    fr=Image.new('RGB',(W,H),(0,0,0))
    lw=820; lh=int(logo.height*lw/logo.width); lg=logo.resize((lw,lh),Image.LANCZOS)
    t=ease(g/10); lg2=lg.resize((int(lw*(0.9+0.1*t)),int(lh*(0.9+0.1*t))),Image.LANCZOS)
    fr.paste(lg2,((W-lg2.width)//2,300+(lh-lg2.height)//2))
    y=300+lh+60
    if g>=4: txt(fr,'THE FIELD JOURNAL',y,92,alpha=ease((g-4)/6))
    if g>=12: txt(fr,'stiffcompetition.shop',y+150,64,fill=RED,stroke=4,alpha=ease((g-12)/6))
    if g>=20: txt(fr,'ALWAYS STANDING TALL',y+290,60,alpha=ease((g-20)/8),stroke=5)
    return fr
if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='frames':
        fs=[10,45,62,80,98,116,134,152,170,190,215,235,265,300,340,390]
        S=Image.new('RGB',(240*len(fs),427))
        for i,f in enumerate(fs): im=frame10(f); S.paste(im.resize((240,427)),(i*240,0)); im.save(f'v13f{f}.png')
        S.save('sheet11.png')
    else:
        p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','30','-i','-','-i','fan2.mp3','-map','0:v','-map','1:a','-c:v','libx264','-preset','veryfast','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-af',f'afade=t=out:st={END-0.7}:d=0.7','-t',str(END),'-movflags','+faststart','SC_journal_preorder_v14.mp4'],stdin=subprocess.PIPE)
        for f in range(N): p.stdin.write(frame10(f).tobytes())
        p.stdin.close(); p.wait()
