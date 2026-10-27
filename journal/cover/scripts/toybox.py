import math
from PIL import Image, ImageDraw, ImageFont
S='/tmp/claude-0/-home-claude/42e45461-9cc6-5cd5-a986-e34bf4d487d7/scratchpad/'
FX=S+'fonts/x/package/files/'
AN=lambda s: ImageFont.truetype(FX+'anton-latin-400-normal.woff',s)
OS=lambda s: ImageFont.truetype(FX+'oswald-latin-700-normal.woff',s)
W,H,SP=600,900,94
RED=(216,38,44); BLUE=(29,71,184); PINK=(220,40,150); BLACK=(14,14,16); WHITE=(255,255,255); YEL=(255,214,0)
col=Image.open(S+'cover/collage.jpg').convert('RGB')
back=col.crop((0,0,748,1121)).resize((W,H)); front=col.crop((857,0,1600,1121)).resize((W,H))
logo=Image.open(S+'mocks/assets/logo_full.png').convert('RGBA')
def lg(w): return logo.resize((w,int(w*logo.height/logo.width)))
def comic(img,xy,t,f,fill=YEL,stroke=BLACK,sw=7,shadow=RED,off=6,center_w=None):
    d=ImageDraw.Draw(img); x,y=xy
    if center_w: x=x+(center_w-d.textlength(t,font=f))/2
    d.text((x+off,y+off),t,font=f,fill=shadow,stroke_width=sw,stroke_fill=stroke)
    d.text((x,y),t,font=f,fill=fill,stroke_width=sw,stroke_fill=stroke)
def burst(c,cx,cy,a,b):
    d=ImageDraw.Draw(c)
    for i in range(80):
        t=i*2*math.pi/80
        d.polygon([(cx,cy),(cx+1500*math.cos(t),cy+1500*math.sin(t)),(cx+1500*math.cos(t+math.pi/80),cy+1500*math.sin(t+math.pi/80))],fill=a if i%2 else b)
# FRONT
f=Image.new('RGB',(W,H),BLUE); burst(f,W/2,H/2,PINK,BLUE)
L=lg(520); f.paste(L,((W-L.width)//2,26),L)
win=front.crop((60,160,560,760)).resize((400,470)); f.paste(win,(100,255))
d=ImageDraw.Draw(f); d.rounded_rectangle((92,247,508,733),radius=18,outline=WHITE,width=8)
d.ellipse((470,205,580,315),fill=RED,outline=WHITE,width=4)
comic(f,(470,222),'SERIES',OS(17),fill=WHITE,sw=0,off=0,center_w=110); comic(f,(470,238),'1',AN(52),fill=WHITE,sw=0,off=0,center_w=110)
comic(f,(0,748),'FIELD JOURNAL',AN(84),sw=8,off=7,center_w=W)
d.ellipse((14,660,84,730),fill=BLACK,outline=WHITE,width=3); comic(f,(14,672),'18+',AN(32),fill=WHITE,sw=0,off=0,center_w=70)
# SPINE
s=Image.new('RGB',(SP,H),BLUE); burst(s,SP/2,H/2,PINK,BLUE)
ImageDraw.Draw(s).rectangle((0,0,3,H),fill=BLACK); ImageDraw.Draw(s).rectangle((SP-4,0,SP,H),fill=BLACK)
d=ImageDraw.Draw(s); d.ellipse((9,22,85,98),fill=RED,outline=WHITE,width=3)
comic(s,(9,32),'SERIES',OS(12),fill=WHITE,sw=0,off=0,center_w=76); comic(s,(9,42),'1',AN(40),fill=WHITE,sw=0,off=0,center_w=76)
r=Image.new('RGBA',(H,SP),(0,0,0,0))
rd=ImageDraw.Draw(r); f1=AN(50); t1='STIFF COMPETITION'; t2='FIELD JOURNAL'
w1=rd.textlength(t1,font=f1); w2=rd.textlength(t2,font=f1); gap=36; x0=(H-(w1+gap+w2))/2+10
comic(r,(x0,8),t1,f1,fill=WHITE,sw=4,off=4); comic(r,(x0+w1+gap,8),t2,f1,sw=4,off=4)
rd.regular_polygon((x0+w1+gap/2,SP/2,9),5,fill=YEL,outline=BLACK)
rr=r.rotate(-90,expand=True); s.paste(rr,(0,0),rr)
d=ImageDraw.Draw(s); d.ellipse((17,812,77,872),fill=BLACK,outline=WHITE,width=3); comic(s,(17,822),'18+',AN(28),fill=WHITE,sw=0,off=0,center_w=60)
# BACK: collage, words inside the starburst panels, barcode over a burst
b=back.copy()
def burstword(img,lines,box,rot,size):
    x0,y0,x1,y1=box; t=Image.new('RGBA',(x1-x0,y1-y0),(0,0,0,0))
    for i,l in enumerate(lines): comic(t,(0,i*int(size*1.15)),l,AN(size),fill=WHITE,sw=5,off=4,center_w=x1-x0)
    t=t.rotate(rot,expand=True,resample=Image.BICUBIC); img.paste(t,(x0,y0),t)
burstword(b,['52 WEEKS!','12 MISSIONS!'],(420,16,565,110),-8,29)
burstword(b,['COLLECT','ALL SIX!'],(470,480,568,570),-8,28)
d=ImageDraw.Draw(b); d.rectangle((25,268,225,388),fill=WHITE,outline=BLACK,width=3)
d.text((62,318),'BARCODE AREA',font=OS(16),fill=(150,150,150))
w=Image.new('RGB',(W*2+SP,H),WHITE); w.paste(b,(0,0)); w.paste(s,(W,0)); w.paste(f,(W+SP,0))
w.save(S+'cover/Toy box cover v2.jpg',quality=88)
th=f.resize((120,180)); sheet=Image.new('RGB',(w.width+40,H+260),(236,233,226)); sheet.paste(w,(20,20)); sheet.paste(th,(20,H+50))
ImageDraw.Draw(sheet).text((160,H+120),'Front at Amazon thumbnail size',font=OS(26),fill=BLACK)
sheet.save(S+'cover/Toy box cover v2 sheet.jpg',quality=85)
