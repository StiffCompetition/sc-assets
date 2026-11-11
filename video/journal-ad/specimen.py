import sys; sys.argv=['x']
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import build_v14 as b
W,H=1080,1920
FD='/tmp/jf/fonts/node_modules/@expo-google-fonts/'
def F(p,s): return ImageFont.truetype(FD+p,s)
bg0=b.pagecrop2('01-card',1560,0.0,300).convert('RGBA')
RED=(190,24,38); GOLD=(255,206,64); CREAM=(255,246,226); GREEN=(18,92,52); WHITE=(255,255,255)
TXT=("PLEASE SEND\nTHE SQUAD","SQUAD")
def fit(text,fp,maxw,start=150):
    d=ImageDraw.Draw(Image.new('RGBA',(10,10))); sz=start
    while True:
        f=F(fp,sz); ws=[d.textbbox((0,0),l,font=f)[2] for l in text.split("\n")]
        if max(ws)<=maxw: return f,sz
        sz-=4
def lines(d,text,key,f,sz,cx,y,lh,fill,keyfill,stroke=0,sfill=None,shadow=None):
    for l in text.split("\n"):
        bb=d.textbbox((0,0),l,font=f); x=cx-(bb[2]-bb[0])//2-bb[0]
        fl=keyfill if key in l else fill
        if shadow: d.text((x+shadow[0],y+shadow[1]),l,font=f,fill=shadow[2],stroke_width=stroke,stroke_fill=shadow[2])
        d.text((x,y),l,font=f,fill=fl,stroke_width=stroke,stroke_fill=sfill)
        y+=lh
def A():  # outlined classic
    im=bg0.copy(); d=ImageDraw.Draw(im); f,sz=fit(TXT[0],'bebas-neue/400Regular/BebasNeue_400Regular.ttf',900,230)
    lines(d,*TXT,f,sz,540,1246-int(sz*2.0)-10,int(sz*1.0),WHITE,GOLD,stroke=10,sfill=(10,10,10),shadow=(0,10,(0,0,0))); return im
def B():  # red rounded plate
    im=bg0.copy(); f,sz=fit(TXT[0],'lilita-one/400Regular/LilitaOne_400Regular.ttf',820,150)
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay); h=int(sz*2.05)+60; y0=1246-h-6
    d.rounded_rectangle((90,y0+10,W-90,y0+h+10),50,fill=(0,0,0,110)); d.rounded_rectangle((70,y0,W-70,y0+h),50,fill=RED+(255,),outline=WHITE+(255,),width=8)
    im.alpha_composite(lay); d=ImageDraw.Draw(im)
    lines(d,*TXT,f,sz,540,y0+30,int(sz*1.02),WHITE,GOLD); return im
def C():  # premium serif on gradient
    im=bg0.copy(); g=Image.new('RGBA',(W,H),(0,0,0,0)); gd=ImageDraw.Draw(g)
    for y in range(760,1260): gd.line((0,y,W,y),fill=(12,6,10,int(235*min(1,(y-760)/260))))
    im.alpha_composite(g); d=ImageDraw.Draw(im); f,sz=fit(TXT[0],'playfair-display/900Black_Italic/PlayfairDisplay_900Black_Italic.ttf',860,150)
    lines(d,*TXT,f,sz,540,1246-int(sz*2.15),int(sz*1.08),CREAM,GOLD,shadow=(0,6,(0,0,0))); return im
def D():  # festive hand-drawn
    im=bg0.copy(); d=ImageDraw.Draw(im); f,sz=fit(TXT[0],'mountains-of-christmas/700Bold/MountainsofChristmas_700Bold.ttf',900,260)
    lines(d,*TXT,f,sz,540,1246-int(sz*2.05)-10,int(sz*1.0),WHITE,GOLD,stroke=12,sfill=GREEN,shadow=(0,10,(0,30,10))); return im
def E():  # tilted red sticker, white border
    im=bg0.copy(); f,sz=fit(TXT[0],'archivo-black/400Regular/ArchivoBlack_400Regular.ttf',780,120)
    pw,ph=W-150,int(sz*2.2)+70; st=Image.new('RGBA',(pw+80,ph+80),(0,0,0,0)); d=ImageDraw.Draw(st)
    d.rounded_rectangle((40,52,40+pw,52+ph),30,fill=(0,0,0,120)); d.rounded_rectangle((40,40,40+pw,40+ph),30,fill=WHITE); d.rounded_rectangle((58,58,22+pw,22+ph),22,fill=RED)
    lines(d,*TXT,f,sz,st.width//2,40+36,int(sz*1.12),WHITE,GOLD)
    st=st.rotate(-3,resample=Image.BICUBIC,expand=True); im.alpha_composite(st,((W-st.width)//2,1246-st.height+20)); return im
def G():  # cream gift tag
    im=bg0.copy(); f,sz=fit(TXT[0],'alfa-slab-one/400Regular/AlfaSlabOne_400Regular.ttf',700,120)
    tw,th=W-200,int(sz*2.2)+90; tg=Image.new('RGBA',(tw+80,th+80),(0,0,0,0)); d=ImageDraw.Draw(tg)
    pts=[(40+60,40),(40+tw,40),(40+tw,40+th),(40+60,40+th),(40,40+th//2)]
    d.polygon([(x+6,y+12) for x,y in pts],fill=(0,0,0,120)); d.polygon(pts,fill=CREAM,outline=(150,100,50)); d.line(pts+[pts[0]],fill=(150,100,50),width=4)
    d.ellipse((40+38,40+th//2-14,40+66,40+th//2+14),fill=(60,60,60,0),outline=(150,100,50),width=5)
    lines(d,*TXT,f,sz,40+tw//2+30,40+34,int(sz*1.12),RED,GREEN)
    tg=tg.rotate(2.5,resample=Image.BICUBIC,expand=True); im.alpha_composite(tg,((W-tg.width)//2,1246-tg.height+20)); return im
opts=[('A  Bebas outline',A),('B  Lilita red plate',B),('C  Playfair italic',C),('D  Festive hand-drawn',D),('E  Archivo sticker',E),('G  Gift tag',G)]
sheet=Image.new('RGB',(3*540+40,2*960+90),(20,20,20)); sd=ImageDraw.Draw(sheet); lf=ImageFont.truetype('/tmp/jf/work/node_modules/@fontsource/inter/files/inter-latin-800-normal.woff2' if False else '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf',30)
for i,(n,fn) in enumerate(opts):
    im=fn().convert('RGB'); im.save(f'/tmp/jf/work/spec_{n[0]}.png')
    t=im.resize((540,960),Image.LANCZOS); x=10+(i%3)*550; y=10+(i//3)*1010
    sheet.paste(t,(x,y+40)); sd.text((x,y),n,font=lf,fill=(255,255,255))
sheet.save('/tmp/jf/work/fonts_sheet.png'); print('ok')
