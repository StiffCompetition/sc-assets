from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
S='/tmp/claude-0/-home-claude/42e45461-9cc6-5cd5-a986-e34bf4d487d7/scratchpad/'
F='/mnt/skills/examples/canvas-design/canvas-fonts/'
BS=lambda s: ImageFont.truetype(F+'BigShoulders-Bold.ttf',s)
WS=lambda s: ImageFont.truetype(F+'WorkSans-Bold.ttf',s)
W,H,SP=600,900,94
RED=(216,38,44); BLUE=(29,71,184); BLACK=(14,14,16); WHITE=(255,255,255)
col=Image.open(S+'cover/collage.jpg').convert('RGB')
back=col.crop((0,0,748,1121)).resize((W,H)); front=col.crop((857,0,1600,1121)).resize((W,H))
logo=Image.open(S+'mocks/assets/logo_full.png').convert('RGBA')
mw=Image.open(S+'mocks/assets/mw_portrait.jpg').convert('RGB')
def lg(w): return logo.resize((w,int(w*logo.height/logo.width)))
def ctext(d,y,t,f,fill,x0=0,w=W):
    tw=d.textlength(t,font=f); d.text((x0+(w-tw)/2,y),t,font=f,fill=fill)
def spine(bg,fg):
    s=Image.new('RGB',(SP,H),bg); t=Image.new('RGBA',(H,SP),(0,0,0,0)); d=ImageDraw.Draw(t)
    d.text((60,18),'STIFF COMPETITION  ·  FIELD JOURNAL',font=BS(46),fill=fg)
    s.paste(t.rotate(-90,expand=True),(0,0),t.rotate(-90,expand=True)); return s
def backpanel(img,dark=False):
    b=img.copy(); d=ImageDraw.Draw(b,'RGBA')
    d.rectangle((50,560,550,820),fill=(255,255,255,235) if not dark else (14,14,16,235))
    tc=BLACK if not dark else WHITE
    ctext(d,578,'52 WEEKS. 12 MISSIONS. STAND TALL.',BS(36),tc,50,500)
    for i,l in enumerate(['A daily field journal for the year ahead.','Rate your day, log your missions,','collect all six. 18+']):
        ctext(d,630+i*28,l,WS(18),tc,50,500)
    d.rectangle((380,730,540,810),fill=WHITE,outline=(150,150,150)); ctext(d,760,'BARCODE',WS(14),(150,150,150),380,160)
    return b
def wrap(bk,sp,fr):
    w=Image.new('RGB',(W*2+SP,H),WHITE); w.paste(bk,(0,0)); w.paste(sp,(W,0)); w.paste(fr,(W+SP,0)); return w
outs=[]
# 1 collage + title block
f=front.copy(); d=ImageDraw.Draw(f)
d.rectangle((0,310,W,590),fill=BLACK); L=lg(500); f.paste(L,((W-L.width)//2,325),L)
ctext(d,540,'FIELD JOURNAL',BS(38),WHITE)
outs.append(('1  Collage with title block',wrap(backpanel(back),spine(BLACK,WHITE),f)))
# 2 hero
f=Image.new('RGB',(W,H),BLACK); h=mw.resize((W,int(W*mw.height/mw.width))); f.paste(h,(0,H-h.height))
g=Image.new('L',(W,H),0); gd=ImageDraw.Draw(g)
for y in range(0,420): gd.line((0,y,W,y),fill=int(255*max(0,1-y/420)))
f.paste(Image.new('RGB',(W,H),BLACK),(0,0),g); L=lg(500); f.paste(L,((W-L.width)//2,40),L)
d=ImageDraw.Draw(f); ctext(d,265,'FIELD JOURNAL',BS(44),WHITE)
d.rectangle((0,H-70,W,H),fill=RED); ctext(d,H-60,'MAJOR WOOD REPORTS FOR DUTY',BS(40),WHITE)
outs.append(('2  One hero on the front',wrap(backpanel(back),spine(RED,WHITE),f)))
# 3 toy box
f=Image.new('RGB',(W,H),BLUE); d=ImageDraw.Draw(f)
for i in range(-20,40): d.polygon([(W/2,H/2),(W/2+1400*__import__('math').cos(i*0.16),H/2+1400*__import__('math').sin(i*0.16)),(W/2+1400*__import__('math').cos(i*0.16+0.08),H/2+1400*__import__('math').sin(i*0.16+0.08))],fill=(220,40,150) if i%2 else BLUE)
L=lg(500); f.paste(L,((W-L.width)//2,30),L)
win=front.crop((60,160,560,760)).resize((400,480)); f.paste(win,(100,260))
d=ImageDraw.Draw(f); d.rounded_rectangle((92,252,508,748),radius=18,outline=WHITE,width=8)
d.ellipse((470,215,580,325),fill=RED,outline=WHITE,width=4); ctext(d,240,'SERIES',WS(16),WHITE,470,110); ctext(d,258,'1',BS(46),WHITE,470,110)
d.rectangle((24,770,104,830),fill=BLACK); ctext(d,774,'18+',BS(44),WHITE,24,80)
d.rectangle((120,775,480,845),fill=(230,230,230),outline=BLACK,width=3); ctext(d,782,'FIELD JOURNAL',BS(50),BLACK,120,360)
outs.append(('3  Toy-box front',wrap(backpanel(back),spine(BLUE,WHITE),f)))
# 4 dark premium
f=Image.new('RGB',(W,H),BLACK); d=ImageDraw.Draw(f)
L=lg(480); f.paste(L,((W-L.width)//2,170),L)
d.line((150,400,450,400),fill=RED,width=3); ctext(d,420,'FIELD JOURNAL',BS(60),WHITE); ctext(d,495,'52 WEEKS  ·  12 MISSIONS  ·  SERIES 1',WS(16),(190,190,190))
strip=front.crop((0,500,W,900)).resize((W,260)); f.paste(strip,(0,600)); d.rectangle((0,596,W,600),fill=RED); d.rectangle((0,860,W,864),fill=RED)
outs.append(('4  Dark premium',wrap(backpanel(ImageEnhance.Brightness(back).enhance(0.55),dark=True),spine(BLACK,WHITE),f)))
# sheet
sc=0.5; ww,wh=int((W*2+SP)*sc),int(H*sc); pad=40; lab=50
sheet=Image.new('RGB',(ww*2+pad*3,(wh+lab)*2+pad*3+lab+230),(236,233,226)); d=ImageDraw.Draw(sheet)
for i,(t,img) in enumerate(outs):
    x=pad+(i%2)*(ww+pad); y=pad+(i//2)*(wh+lab+pad)
    d.text((x,y),t,font=WS(26),fill=BLACK); sheet.paste(img.resize((ww,wh)),(x,y+lab))
    img.save(S+f'cover/option{i+1}.jpg',quality=88)
y=pad+2*(wh+lab+pad); d.text((pad,y),'Thumbnail test: the front at Amazon search size',font=WS(26),fill=BLACK)
for i,(t,img) in enumerate(outs):
    th=img.crop((W+SP,0,W*2+SP,H)).resize((120,180)); sheet.paste(th,(pad+i*170,y+lab))
    d.text((pad+i*170+50,y+lab+186),str(i+1),font=WS(20),fill=BLACK)
sheet.save(S+'cover/Journal cover options.jpg',quality=85); print(sheet.size)
