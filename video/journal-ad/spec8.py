exec(open('spec5.py').read().split("beats=[")[0])
import numpy as np
def face4(i,w=740,top=262):
    im=b.faces[i]; h=int(im.height*w/im.width)
    p=im.resize((w,h),Image.LANCZOS); B=14
    pan=Image.new('RGBA',(w+2*B,h+2*B),(255,255,255,255)); pan.paste(p,(B,B))
    lay=Image.new('RGBA',(pan.width+160,pan.height+160),(0,0,0,0))
    sh=Image.new('RGBA',lay.size,(0,0,0,0)); ImageDraw.Draw(sh).rectangle((80,100,80+pan.width,100+pan.height),fill=(0,0,0,170))
    lay.alpha_composite(sh.filter(ImageFilter.GaussianBlur(20))); lay.alpha_composite(pan,(80,80))
    lay=lay.rotate(2.5 if i%2==0 else -2.5,resample=Image.BICUBIC,expand=True)
    fr=b.RAYS.copy().convert('RGBA'); fr.alpha_composite(lay,((W-lay.width)//2,top-80)); return fr
def cover5(s=0.62,top=272):
    full=b.cover(b.desk,940,800,0.0)
    bg=full.crop((0,0,36,H)).resize((W,H),Image.BICUBIC).filter(ImageFilter.GaussianBlur(24))
    fw,fh=int(W*s),int(H*s); fg=full.resize((fw,fh),Image.LANCZOS)
    m=Image.new('L',(fw,fh),0); ImageDraw.Draw(m).rectangle((30,30,fw-30,fh-30),fill=255); m=m.filter(ImageFilter.GaussianBlur(14))
    x=540-int(506*s); y=top-int(302*s); bg.paste(fg,(x,y),m); return bg.convert('RGBA')
def stick1(im,parts,top=1120):
    f,sz=fit("DEAR SANTA,",'archivo-black/400Regular/ArchivoBlack_400Regular.ttf',760,120)
    pw,ph=W-190,int(sz*1.12)+70
    st=Image.new('RGBA',(pw+80,ph+80),(0,0,0,0)); d=ImageDraw.Draw(st)
    d.rounded_rectangle((40,52,40+pw,52+ph),30,fill=(0,0,0,120)); d.rounded_rectangle((40,40,40+pw,40+ph),30,fill=WHITE); d.rounded_rectangle((58,58,22+pw,22+ph),22,fill=RED)
    bbw=d.textbbox((0,0),"DEAR SANTA,",font=f); x=(st.width-(bbw[2]-bbw[0]))//2-bbw[0]
    d.text((x,40+34),"DEAR ",font=f,fill=WHITE); wd=d.textlength("DEAR ",font=f); d.text((x+wd,40+34),"SANTA,",font=f,fill=GOLD)
    st=st.rotate(-3,resample=Image.BICUBIC,expand=True); im=im.convert('RGBA'); im.alpha_composite(st,((W-st.width)//2,top)); return im
UPP=90
beats=[('cover',stick1(cover5(),None)),
('card',stick_at(page('01-card',1560,UPP),"I'D LIKE\nTO ENLIST","ENLIST",top=1020)),
('squad',stick_at(page('02-squad',1560,UPP),"SIX FILES.\nONE IS YOU.","ONE IS YOU.",top=1020)),
('grip',stick_at(face4(5),"THE GRIP CRIES\nAT ANIMAL VIDEOS","AT ANIMAL VIDEOS",top=1070)),
('admiral',stick_at(face4(3),"FIRST MATE:\nA RUBBER DUCK","A RUBBER DUCK",top=1070)),
('missions',stick_at(page('03-map',1560,UPP),"12 MISSIONS.\nBRIEF. DEBRIEF.","BRIEF. DEBRIEF.",top=1020)),
('cert',stick_at(page('08-certificate',1560,UPP),"SIGN HERE.\nSTAND TALL.","STAND TALL.",top=1020))]
def guides(im):
    o=im.convert('RGB').copy(); d=ImageDraw.Draw(o)
    for y in (272,1246): d.line((0,y,W,y),fill=(0,255,255),width=3)
    return o
sheet=Image.new('RGB',(4*540+50,2*960+30),(20,20,20)); sheet2=sheet.copy()
for i,(n,im) in enumerate(beats):
    im=im.convert('RGB'); im.save(f'spec8_{i}.png')
    sheet.paste(im.resize((540,960),Image.LANCZOS),(10+(i%4)*550,10+(i//4)*970))
    sheet2.paste(guides(im).resize((540,960),Image.LANCZOS),(10+(i%4)*550,10+(i//4)*970))
sheet.save('sheet_E5.png'); sheet2.save('sheet_E5_guides.png'); print('ok')
