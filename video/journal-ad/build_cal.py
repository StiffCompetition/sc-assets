import sys
M=sys.argv[1] if len(sys.argv)>1 else ""
sys.argv=[sys.argv[0]]
import build_v15 as v
from build_v15 import *
PG={'cover':1,'jan':2,'feb':3,'mar':4,'apr':5,'oct':11,'dec':13}
pages={k:Image.open(f'/tmp/cal/eu-{n:02d}.png').convert('RGB') for k,n in PG.items()}
BGS=[((232,54,143),(120,20,140)),((0,170,200),(20,60,150)),((255,130,30),(200,30,90)),((130,40,190),(40,20,120))]
def backdrop(j):
    c1,c2=BGS[j%4]; import numpy as np
    y=np.linspace(0,1,H)[:,None,None]; a=np.array(c1)[None,None,:]*(1-y)+np.array(c2)[None,None,:]*y
    arr=np.broadcast_to(a,(H,W,3)).astype(np.uint8); return Image.fromarray(arr).convert('RGBA')
def wire(w,x0,y):
    lay=Image.new('RGBA',(W,200),(0,0,0,0)); d=ImageDraw.Draw(lay)
    n=22; step=w/n
    for i in range(n):
        x=x0+step*(i+0.5)
        d.rounded_rectangle((x-6,92,x+6,150),6,fill=(40,40,40,255)); d.ellipse((x-17,100,x+17,132),outline=(215,215,225,255),width=7)
    d.line((W//2-70,92,W//2,20),fill=(200,200,210,255),width=7); d.line((W//2+70,92,W//2,20),fill=(200,200,210,255),width=7)
    d.ellipse((W//2-12,4,W//2+12,28),outline=(215,215,225,255),width=7); return lay
SCALE=0.85
def card(key,j,t,tilt):
    pg=pages[key]; w=int(918*(1+0.035*t)); h=int(pg.height*w/pg.width)
    p=pg.resize((w,h),Image.LANCZOS).convert('RGBA')
    sh=Image.new('RGBA',(w+120,h+120),(0,0,0,0)); ImageDraw.Draw(sh).rectangle((60,80,60+w,80+h),fill=(0,0,0,150)); sh=sh.filter(ImageFilter.GaussianBlur(18))
    sh.alpha_composite(p,(60,60)); lay=sh.rotate(tilt,resample=Image.BICUBIC,expand=True)
    fr=backdrop(j); top=TOPC[key]-int(h*0.0)
    fr.alpha_composite(lay,((W-lay.width)//2,top-60-(lay.height-h-120)//2))
    wl=wire(w,(W-w)//2,top); fr.alpha_composite(wl,(0,top-110))
    return fr
TOPC={'cover':210,'jan':272,'feb':272,'mar':272,'apr':272,'oct':272,'dec':272}
CAL=[('cover',"SIX LADS.\nTWELVE MONTHS.","TWELVE MONTHS.",1140),
('jan',"NEVER SITS.\nNEVER SLUMPS.","NEVER SLUMPS.",1020),
('feb',"BEHIND THE\nVELVET ROPE","VELVET ROPE",1020),
('mar',"CRIES AT\nANIMAL VIDEOS","ANIMAL VIDEOS",1020),
('apr',"NOTHING EVER\nSTICKS TO HIM","STICKS TO HIM",1020),
('oct',"FIRST MATE:\nA RUBBER DUCK","A RUBBER DUCK",1020),
('dec',"ALL SIX.\nONE PARTY.","ONE PARTY.",1020)]
CSTK=[make_sticker(c[1],c[2]) for c in CAL]
def frame_cal(i,t=0.3,g=20):
    k,text,key,top=CAL[i]; im=card(k,i,t,(-1.5 if i%2 else 1.5))
    st=CSTK[i]; im.alpha_composite(st,((W-st.width)//2,top)); return im.convert('RGB')
if M=='stills':
    sh=Image.new('RGB',(4*540+50,2*960+30),(20,20,20))
    for i in range(7):
        im=frame_cal(i); im.save(f'cal_still_{i}.png'); sh.paste(im.resize((540,960),Image.LANCZOS),(10+(i%4)*550,10+(i//4)*970))
    sh.save('sheet_cal1.png'); print('ok')
