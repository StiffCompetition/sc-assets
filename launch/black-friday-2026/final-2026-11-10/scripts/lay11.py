from PIL import Image,ImageDraw,ImageFont,ImageFilter
import glob,sys
RAJ=glob.glob('/home/claude/bf/fonts/fontsource-rajdhani-5.3.0/package/files/rajdhani-latin-700-normal.woff')[0]
W,H=1080,1920
lg0=Image.open('/home/claude/stiffcompetition/sc-assets/brand/logos/print/SC_chrome_full_print_3472w.png').convert('RGBA')
lw=990; lh=int(lg0.height*lw/lg0.width); lg=lg0.resize((lw,lh),Image.LANCZOS)
def fit(d,t,width):
    lo,hi=10,400
    while lo<hi:
        m=(lo+hi+1)//2; f=ImageFont.truetype(RAJ,m); bb=d.textbbox((0,0),t,font=f)
        if bb[2]-bb[0]<=width: lo=m
        else: hi=m-1
    return lo
def line(o,t,top,width,fill,stroke=None,sw=0,glow=False):
    d=ImageDraw.Draw(o); s=fit(d,t,width); f=ImageFont.truetype(RAJ,s); bb=d.textbbox((0,0),t,font=f)
    x=(W-(bb[2]-bb[0]))/2-bb[0]; y=top-bb[1]
    if glow:
        g=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(g).text((x,y),t,font=f,fill=(255,255,255,255),stroke_width=sw,stroke_fill=(255,255,255,255))
        o.alpha_composite(g.filter(ImageFilter.GaussianBlur(14)))
    d=ImageDraw.Draw(o); d.text((x,y),t,font=f,fill=fill,stroke_width=sw,stroke_fill=stroke or fill)
    return bb[3]-bb[1]


import numpy as np
def bg():
    yy,xx=np.mgrid[0:H,0:W].astype(float)
    def rad(cx,cy,r,col,a):
        d=np.sqrt((xx-cx)**2+(yy-cy)**2)/r; m=np.clip(1-d,0,1)**1.6*a
        return m[...,None]*np.array(col)[None,None,:]
    img=rad(540,1000,900,(150,12,24),0.55)+rad(540,380,700,(30,60,170),0.45)
    return Image.fromarray(np.clip(img,0,255).astype('uint8')).convert('RGBA')
def slot(o,t,y0,y1,width,maxcap,fill,stroke=None,sw=0,glow=False,hl=None):
    d=ImageDraw.Draw(o); sz=fit(d,t,width)
    while True:
        f=ImageFont.truetype(RAJ,sz); bb=d.textbbox((0,0),t,font=f)
        if bb[3]-bb[1]<=maxcap: break
        sz-=2
    top=y0+((y1-y0)-(bb[3]-bb[1]))/2
    if hl and hl in t:
        a=t[:t.index(hl)]; w_a=d.textlength(a,font=f); w_h=d.textlength(hl,font=f); w_all=d.textlength(t,font=f)
        x0=(W-w_all)/2; y=top-bb[1]
        d.text((x0,y),a,font=f,fill=fill)
        d.text((x0+w_a,y),hl,font=f,fill=(230,30,30),stroke_width=3,stroke_fill=(255,255,255))
        rest=t[t.index(hl)+len(hl):]
        d.text((x0+w_a+w_h,y),rest,font=f,fill=fill)
    else:
        line(o,t,top,bb[2]-bb[0],fill,stroke,sw,glow)
def make(top,tag,out,hl=None):
    o=bg(); o.alpha_composite(lg,(45,260))
    slot(o,top,1062,1182,800,120,(230,30,30),(255,255,255),6)
    slot(o,tag,1196,1270,800,74,(255,255,255),hl=hl)
    slot(o,'MEET THE GANG. FIND THE FULL STORY AT',1400,1446,800,46,(255,255,255))
    slot(o,'stiffcompetition.shop',1458,1540,820,82,(255,255,255),(15,15,25),4,glow=True)
    o.convert('RGB').save(out)
V=[('FOLLOW US','ALWAYS STANDING TALL',None),('SHOP NOW','ALWAYS STANDING TALL',None),('BLACK FRIDAY','10% OFF ALL MERCH','10% OFF')]
for i,(a,b,h) in enumerate(V): make(a,b,f't{i}.png',h)
S=Image.new('RGB',(3*540+4*20,960+40),(24,24,28))
for i in range(3): S.paste(Image.open(f't{i}.png').resize((540,960)),(20+i*560,20))
S.save('t_sheet.png')
