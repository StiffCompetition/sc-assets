import sys
from build_v8 import *
AD='/tmp/jf/ad/'
shots=[('01-card',1560),('02-squad',1560),('03-map',625),('04-wood-file',625),('05-day-tue',625),('05-day-tue',1560),('06-day-fri',625),('06-day-fri',1560),('07-sunday',625),('07-sunday',1560),('04-wood-file',1560),('08-certificate',1560)]
imgs={n:Image.open(AD+n+'.png').convert('RGB') for n in set(a for a,_ in shots)}
def pagecrop(n,cx,t):
    cw=int(940-110*t); ch=cw*16//9; cy=1593; cx=max(cw//2,min(2160-cw//2,cx))
    return imgs[n].crop((cx-cw//2,cy-ch//2,cx+cw//2,cy+ch//2)).resize((W,H),Image.LANCZOS)
def cap(fr,text,g,y,color=WHITE):
    txt(fr,text,y,88 if len(text)>12 else 104,fill=color,stroke=8,alpha=ease(g/3))
def endcard9(g):
    fr=Image.new('RGB',(W,H),(0,0,0))
    lw=820; lh=int(logo.height*lw/logo.width); lg=logo.resize((lw,lh),Image.LANCZOS)
    t=ease(g/10); lg2=lg.resize((int(lw*(0.9+0.1*t)),int(lh*(0.9+0.1*t))),Image.LANCZOS)
    fr.paste(lg2,((W-lg2.width)//2,300+(lh-lg2.height)//2))
    y=300+lh+50
    if g>=4: txt(fr,'THE FIELD JOURNAL',y,92,alpha=ease((g-4)/6))
    if g>=10: txt(fr,'STIFF GIFTS FOR EVERYONE',y+130,84,fill=RED,stroke=8,alpha=ease((g-10)/6))
    if g>=22: txt(fr,'stiffcompetition.shop',y+290,56,alpha=ease((g-22)/8),stroke=4)
    return fr
def frame9(f):
    if f>=bf(15): return endcard9(f-bf(15))
    k=max(0,min(14,int((f/FPS-B0)//PER))); g=f-bf(k)
    if k<2:
        t=(f-bf(0))/(bf(2)-bf(0)); fr=cover(desk,940,930,ease(t)); caption(fr,'THE GIFT THAT STANDS TALL',f-bf(0))
    elif k<14:
        n,cx=shots[k-2]
        t=g/(bf(k+1)-bf(k)); fr=pagecrop(n,cx,t)
        cap(fr,'52 WEEKS OF MISSIONS' if k<5 else 'SIX HEROES. ONE PAGE A DAY.',9 if k not in (2,5) else g,1160)
        if g<2: fr=Image.blend(fr,Image.new('RGB',(W,H),(255,255,255)),0.35*(1-g/2))
    else:
        t=(f-bf(14))/(bf(15)-bf(14)); fr=cover(flat,975,930,ease(t)); caption(fr,'ORDER NOW',g,RED)
    return fr
if len(sys.argv)>1 and sys.argv[1]=='frames':
    fs=[10,45,75,100,130,160,190,220,245,265,300,340]
    S=Image.new('RGB',(270*len(fs),480))
    for i,f in enumerate(fs): S.paste(frame9(f).resize((270,480)),(i*270,0)); frame9(f).save(f'v9f{f}.png')
    S.save('sheet9.png')
elif __name__=='__main__':
    p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','30','-i','-','-i','fan1.mp3','-map','0:v','-map','1:a','-c:v','libx264','-preset','veryfast','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-af',f'afade=t=out:st={END-0.7}:d=0.7','-t',str(END),'-movflags','+faststart','SC_journal_preorder_v9.mp4'],stdin=subprocess.PIPE)
    for f in range(N): p.stdin.write(frame9(f).tobytes())
    p.stdin.close(); p.wait()
