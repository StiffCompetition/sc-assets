import sys, subprocess
MODE=sys.argv[1] if len(sys.argv)>1 else ""
exec(open('cover6.py').read().split("if __name__")[0])
import build_v14 as b14
FPS=30; END=15.0; N=int(END*FPS)
PER=0.5285; B0=0.25
def bf(k): return round((B0+PER*k)*FPS)
def ease(x): x=max(0,min(1,x)); return x*x*(3-2*x)
# captions: (shot kind, arg, text, key, beats)
S=[('cover',None,"DEAR SANTA,",None,3),
   ('page','01-card',"I'D LIKE\nTO ENLIST","ENLIST",3),
   ('page','02-squad',"SIX FILES.\nONE IS YOU.","ONE IS YOU.",3),
   ('face',5,"THE GRIP CRIES\nAT ANIMAL VIDEOS","AT ANIMAL VIDEOS",3),
   ('face',3,"FIRST MATE:\nA RUBBER DUCK","A RUBBER DUCK",3),
   ('page','03-map',"12 MISSIONS.\nBRIEF. DEBRIEF.","BRIEF. DEBRIEF.",3),
   ('page','08-certificate',"SIGN HERE.\nSTAND TALL.","STAND TALL.",3)]
STARTS=[sum(s[4] for s in S[:i]) for i in range(len(S))]; ENDB=sum(s[4] for s in S)
FONT='archivo-black/400Regular/ArchivoBlack_400Regular.ttf'
def make_sticker(text,key):
    one="\n" not in text
    f,sz=fit(text,FONT,780 if not one else 760,120)
    n=len(text.split("\n")); pw=W-150 if not one else W-190; ph=int(sz*1.12*n)+70
    st=Image.new('RGBA',(pw+80,ph+80),(0,0,0,0)); d=ImageDraw.Draw(st)
    d.rounded_rectangle((40,52,40+pw,52+ph),30,fill=(0,0,0,120)); d.rounded_rectangle((40,40,40+pw,40+ph),30,fill=WHITE); d.rounded_rectangle((58,58,22+pw,22+ph),22,fill=RED)
    if one:
        a,bb_=text.split(" ",1); bbw=d.textbbox((0,0),text,font=f); x=(st.width-(bbw[2]-bbw[0]))//2-bbw[0]
        d.text((x,40+34),a+" ",font=f,fill=WHITE); d.text((x+d.textlength(a+" ",font=f),40+34),bb_,font=f,fill=GOLD)
    else: lines(d,text,key,f,sz,st.width//2,40+30,int(sz*1.12),WHITE,GOLD)
    return st.rotate(-3,resample=Image.BICUBIC,expand=True)
STK=[make_sticker(s[2],s[3]) for s in S]
TOP=[1140,1020,1020,1070,1070,1020,1020]
def base(i,t):
    k,a=S[i][0],S[i][1]
    if k=='cover': return cover6(0.72+0.05*t,272)
    if k=='face': return face4(a,w=int(740+30*t),top=262-int(10*t))
    cw=int(940-70*t); ch=cw*16//9; cy=min(3840-ch//2,1593+90); cx=max(cw//2,min(2160-cw//2,1560 if a!='05-day-tue' else 625))
    return b.b9.imgs[a].crop((cx-cw//2,cy-ch//2,cx+cw//2,cy+ch//2)).resize((W,H),Image.LANCZOS).convert('RGBA')

def endcard15(g):
    fr=Image.new('RGB',(W,H),(0,0,0))
    lw=820; lh=int(b14.logo.height*lw/b14.logo.width); lg=b14.logo.resize((lw,lh),Image.LANCZOS)
    t=ease(g/10); lg2=lg.resize((int(lw*(0.92+0.08*t)),int(lh*(0.92+0.08*t))),Image.LANCZOS)
    fr.paste(lg2,((W-lg2.width)//2,290+(lh-lg2.height)//2))
    y=290+lh+50
    T=b14.txt
    if g>=6: T(fr,'SHOP FOR CHRISTMAS.',y,66,alpha=ease((g-6)/6))
    if g>=14: T(fr,'BUY FOR YOUR BUDDY.',y+84,66,alpha=ease((g-14)/6))
    if g>=24: T(fr,'SHOP NOW',y+210,150,fill=RED,stroke=7,alpha=ease((g-24)/5))
    if g>=34: T(fr,'ALWAYS STANDING TALL',y+400,58,alpha=ease((g-34)/6),stroke=5)
    if g>=42: T(fr,'stiffcompetition.shop',y+480,72,alpha=ease((g-42)/6),stroke=5)
    return fr
_cache={}
def frame(f):
    if f>=bf(ENDB): return endcard15(f-bf(ENDB))
    i=max([k for k in range(len(S)) if f>=bf(STARTS[k])] or [0]); g=max(0,f-bf(STARTS[i])); t=g/max(1,(bf(STARTS[i]+S[i][4])-bf(STARTS[i])))
    if i==0 and f<bf(0): g=0
    im=base(i,t)
    st=STK[i]; p=ease(g/5.0); sc=1+0.14*(1-p)
    s2=st if sc==1 else st.resize((int(st.width*sc),int(st.height*sc)),Image.LANCZOS)
    if p<1:
        a=s2.split()[3].point(lambda v:int(v*max(0.0,p))); s2=s2.copy(); s2.putalpha(a)
    x=(W-s2.width)//2; y=TOP[i]-(s2.height-st.height)//2
    im.alpha_composite(s2,(x,y)); im=im.convert('RGB')
    if g<3 and i>0: im=Image.blend(im,Image.new('RGB',(W,H),(255,255,255)),0.25*(1-g/3))
    return im
if __name__=='__main__':
    if MODE=='frames':
        fs=[bf(STARTS[i])+10 for i in range(len(S))]+[bf(ENDB)+20,bf(ENDB)+70]
        sh=Image.new('RGB',(270*len(fs),480))
        for j,f in enumerate(fs): sh.paste(frame(f).resize((270,480)),(j*270,0))
        sh.save('sheet15.png'); print(fs)
    else:
        p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','30','-i','-','-i','fan2.mp3','-map','0:v','-map','1:a','-c:v','libx264','-preset','veryfast','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-af',f'afade=t=out:st={END-0.7}:d=0.7','-t',str(END),'-movflags','+faststart','SC_journal_preorder_v15.mp4'],stdin=subprocess.PIPE)
        for f in range(N): p.stdin.write(frame(f).tobytes())
        p.stdin.close(); p.wait()
