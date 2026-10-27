def k(*v): return tuple(int(x*K) for x in v)
def lg(w): w=int(w*K); return logo.resize((w,int(w*logo.height/logo.width)),Image.LANCZOS)
def tw(d,t,f): return d.textlength(t,font=f)
def comic(img,xy,t,f,fill=YEL,sw=4,off=4,cw=None):
    d=ImageDraw.Draw(img); x,y=xy; x*=K; y*=K
    if cw: x=x+(cw*K-tw(d,t,f))/2
    if off: d.text((x+off*K,y+off*K),t,font=f,fill=RED,stroke_width=sw*K,stroke_fill=BLACK)
    d.text((x,y),t,font=f,fill=fill,stroke_width=sw*K,stroke_fill=BLACK)
def burst(c,cx,cy,a=PINK,b=BLUE,n=72):
    d=ImageDraw.Draw(c); cx*=K; cy*=K
    for i in range(n):
        t=i*2*math.pi/n; e=math.pi/n
        d.polygon([(cx,cy),(cx+4000*math.cos(t),cy+4000*math.sin(t)),(cx+4000*math.cos(t+e),cy+4000*math.sin(t+e))],fill=a if i%2==0 else b)
def badge(img,cx,cy,r,top,big):
    d=ImageDraw.Draw(img); d.ellipse(k(cx-r,cy-r,cx+r,cy+r),fill=RED,outline=WHITE,width=3*K)
    comic(img,(cx-r,cy-r*0.62),top,OS(r*0.3),fill=WHITE,sw=0,off=0,cw=2*r); comic(img,(cx-r,cy-r*0.42),big,AN(r*0.9),fill=WHITE,sw=0,off=0,cw=2*r)
def age(img,cx,cy,r=30):
    d=ImageDraw.Draw(img); d.ellipse(k(cx-r,cy-r,cx+r,cy+r),fill=BLACK,outline=WHITE,width=3*K); comic(img,(cx-r,cy-r*0.62),'18+',AN(r*0.9),fill=WHITE,sw=0,off=0,cw=2*r)
def window(img,src,box,rad=16):
    x0,y0,x1,y1=box; w,h=int((x1-x0)*K),int((y1-y0)*K)
    sw_,sh=src.size; r=w/h
    if sw_/sh>r: nw=int(sh*r); src=src.crop(((sw_-nw)//2,0,(sw_-nw)//2+nw,sh))
    else: nh=int(sw_/r); src=src.crop((0,0,sw_,nh))
    p=src.resize((w,h),Image.LANCZOS); m=Image.new('L',(w,h),0); ImageDraw.Draw(m).rounded_rectangle((0,0,w-1,h-1),radius=rad*K,fill=255)
    img.paste(p,(int(x0*K),int(y0*K)),m)
    ImageDraw.Draw(img).rounded_rectangle(k(x0-4,y0-4,x1+4,y1+4),radius=(rad+4)*K,outline=WHITE,width=7*K)
def base(): c=Image.new('RGB',(W,H),BLUE); burst(c,300,450); return c
# FRONT A: toy box, shocked faces in window (all four rows)
def frontA():
    f=base(); L=lg(400); f.paste(L,((W-L.width)//2,int(10*K)),L)
    window(f,shock,(100,186,500,786))
    comic(f,(0,800),'FIELD JOURNAL',AN(64),sw=5,off=5,cw=600); return f
# SPINE
def spine():
    s=Image.new('RGB',(SP,H),BLUE); burst(s,47,450)
    d=ImageDraw.Draw(s); d.rectangle(k(0,0,3,900),fill=BLACK); d.rectangle(k(91,0,94,900),fill=BLACK)
    
    r=Image.new('RGBA',(H,SP),(0,0,0,0)); rd=ImageDraw.Draw(r); f1=AN(46)
    t1,t2='STIFF COMPETITION','FIELD JOURNAL'; g=40*K
    w1,w2=tw(rd,t1,f1),tw(rd,t2,f1); tot=w1+g+w2; x0=(H-tot)/2
    bb=rd.textbbox((0,0),'S',font=f1); th=bb[3]-bb[1]; y=(SP-th)/2-bb[1]-2*K
    for t,x,fl in ((t1,x0,WHITE),(t2,x0+w1+g,YEL)):
        rd.text((x+3*K,y+3*K),t,font=f1,fill=RED,stroke_width=3*K,stroke_fill=BLACK); rd.text((x,y),t,font=f1,fill=fl,stroke_width=3*K,stroke_fill=BLACK)
    rd.regular_polygon((x0+w1+g/2,SP/2,9*K),5,fill=YEL,outline=BLACK,width=2*K)
    rr=r.rotate(-90,expand=True); s.paste(rr,(0,0),rr); return s
def barcode(b,x=388,y=740):
    d=ImageDraw.Draw(b); d.rectangle(k(x,y,x+200,y+120),fill=WHITE,outline=BLACK,width=2*K); comic(b,(x,y+48),'BARCODE',OS(14),fill=(150,150,150),sw=0,off=0,cw=200)
def blurb(b,y,lines):
    for i,l in enumerate(lines): comic(b,(0,y+i*30),l,OS(21),fill=WHITE,sw=3,off=0,cw=600)
# BACK 1: collect all six, character windows
def back1():
    b=base(); comic(b,(0,40),'COLLECT ALL SIX!',AN(64),sw=5,off=5,cw=600)
    for i,(n,fn) in enumerate(chars):
        cx=50+(i%3)*175; cy=150+(i//3)*235; window(b,Image.open(A+fn).convert('RGB'),(cx,cy,cx+150,cy+180),12)
        d=ImageDraw.Draw(b); d.rectangle(k(cx-4,cy+186,cx+154,cy+214),fill=BLACK); comic(b,(cx-4,cy+188),n,OS(15),fill=WHITE,sw=0,off=0,cw=158)
    blurb(b,630,['52 WEEKS. 12 MISSIONS. ONE FIELD JOURNAL.','RATE YOUR DAY. LOG YOUR MISSIONS.']); barcode(b); age(b,60,800); return b
# BACK 2: smiling-faces collage in a window, everything aligned to the box edges (x 70 to 530)
def fit(t,font_fn,width,start=120):
    d=ImageDraw.Draw(Image.new('RGB',(10,10))); z=start
    while tw(d,t,font_fn(z))>width*K: z-=0.5
    return font_fn(z)
def back2():
    b=base(); X0,X1=100,500; BW=X1-X0
    d=ImageDraw.Draw(b)
    def line(t,ffn,top,fill,sw,off,f=None,x0=X0,w=BW):
        f=f or fit(t,ffn,w-off); bb=d.textbbox((0,0),t,font=f); comic(b,(x0,top-bb[1]/K),t,f,fill=fill,sw=sw,off=off,cw=w); return (bb[3]-bb[1])/K
    line('52 WEEKS! 12 MISSIONS!',AN,36,YEL,5,5)
    window(b,smile,(X0,96,X1,696))
    l1,l2='LOG YOUR MISSIONS.','RATE YOUR DAY.'; TW=186
    bf=fit(l1,OS,TW); h=line(l1,OS,724,WHITE,3,0,bf,X0,TW); line(l2,OS,724+h+10,WHITE,3,0,bf,X0,TW)
    barcode(b,X1-200,708); return b
