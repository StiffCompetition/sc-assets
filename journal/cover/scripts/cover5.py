import math, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S='/tmp/claude-0/-home-claude/42e45461-9cc6-5cd5-a986-e34bf4d487d7/scratchpad/'
FX=S+'fonts/x/package/files/'
D=int(sys.argv[1]) if len(sys.argv)>1 else 150
FX_=sys.argv[4] if len(sys.argv)>4 else 'none'      # pixels per inch
LETTER=sys.argv[2] if len(sys.argv)>2 else 'block'
def P(v): return int(round(v*D))
AN=lambda pt: ImageFont.truetype(FX+'anton-latin-400-normal.woff',P(pt/72))
OS=lambda pt: ImageFont.truetype(FX+'oswald-latin-700-normal.woff',P(pt/72))
RED=(216,38,44); DRED=(120,14,20); BLUE=(29,71,184); PINK=(220,40,150); BLACK=(14,14,16); WHITE=(255,255,255); YEL=(255,214,0)
# Lulu cover for 392 pages: 13.193 x 9.25 in, bleed 0.125, spine 0.943
BL=0.125; TW=6.0; TH=9.0; SPW=0.943
CW=BL*2+TW*2+SPW; CH=BL*2+TH
BACK_X=BL; SP_X=BL+TW; FR_X=BL+TW+SPW
SAFE=0.375   # keep text and logos this far inside the trim
col=Image.open(S+'cover/collage.jpg').convert('RGB')
logo=Image.open(S+'cover/SC_full_logo_chrome_transparent.png')
sq=Image.open(S+'cover/SC_square_logo_chrome_transparent.png')
def burst(img,cx,cy,a=PINK,b=BLUE,n=72):
    d=ImageDraw.Draw(img)
    for i in range(n):
        t=i*2*math.pi/n; e=math.pi/n
        d.polygon([(cx,cy),(cx+9000*math.cos(t),cy+9000*math.sin(t)),(cx+9000*math.cos(t+e),cy+9000*math.sin(t+e))],fill=a if i%2==0 else b)
def lg(im,w_in): w=P(w_in); return im.resize((w,int(w*im.height/im.width)),Image.LANCZOS)
# ---------- lettering ----------
def letters(text,font,style=LETTER,face=YEL):
    d=ImageDraw.Draw(Image.new('L',(1,1))); bb=d.textbbox((0,0),text,font=font)
    w,h=bb[2]-bb[0],bb[3]-bb[1]; ow=max(2,P(0.035)); depth=P(0.07); pad=ow*3+depth+4
    im=Image.new('RGBA',(w+pad*2,h+pad*2),(0,0,0,0)); dr=ImageDraw.Draw(im); x,y=pad-bb[0],pad-bb[1]
    if style=='block':        # solid 3D block joined to the letters
        for k in range(depth,0,-1): dr.text((x+k,y+k),text,font=font,fill=DRED,stroke_width=ow,stroke_fill=BLACK)
        dr.text((x,y),text,font=font,fill=face,stroke_width=ow,stroke_fill=BLACK)
    elif style=='toy':        # thick black outline with a white keyline, no shadow
        dr.text((x,y),text,font=font,fill=WHITE,stroke_width=ow*2+P(0.02),stroke_fill=WHITE)
        dr.text((x,y),text,font=font,fill=face,stroke_width=ow*2,stroke_fill=BLACK)
    elif style=='chrome':     # silver face, black outline, yellow keyline: nothing repeats the blue and pink background
        dr.text((x,y),text,font=font,fill=YEL,stroke_width=ow*2+P(0.03),stroke_fill=YEL)
        dr.text((x,y),text,font=font,fill=BLACK,stroke_width=ow*2,stroke_fill=BLACK)
        m=Image.new('L',im.size,0); ImageDraw.Draw(m).text((x,y),text,font=font,fill=255)
        g=Image.new('RGBA',im.size); gd=ImageDraw.Draw(g); top=bb[1]+y; hh=h
        for yy in range(im.height):
            t=min(1,max(0,(yy-top)/max(1,hh)))
            if t<0.5: c=tuple(int(a+(b-a)*t/0.5) for a,b in zip((255,255,255),(170,172,178)))
            elif t<0.54: c=(70,72,78)
            else: c=tuple(int(a+(b-a)*(t-0.54)/0.46) for a,b in zip((120,122,128),(235,236,240)))
            gd.line((0,yy,im.width,yy),fill=c+(255,))
        im.paste(g,(0,0),m)
    return im
def fit_letters(text,max_w_in,max_pt,style=LETTER,face=YEL):
    pt=max_pt
    while True:
        im=letters(text,AN(pt),style,face)
        if im.width<=P(max_w_in) or pt<8: return im.crop(im.getbbox())
        pt-=1
# ---------- clean comic grid ----------
GUT=0.07; SLANT=0.22
LINES=sys.argv[5] if len(sys.argv)>5 else 'comic'   # gutter width and divider lean, identical everywhere
def grid(rows,w_in,row_h_in,src_rects):
    SS=3                                             # draw 3x larger then shrink: clean, even edges
    W,H=P(w_in)*SS,P(row_h_in*len(rows)+GUT*(len(rows)-1))*SS; g=P(GUT)*SS; sl=P(SLANT)*SS; rh=P(row_h_in)*SS
    gut_col=BLACK if LINES=='black' else WHITE
    im=Image.new('RGB',(W,H),gut_col); ol=Image.new('L',(W,H),0); od=ImageDraw.Draw(ol); lw=max(1,int(P(0.022)*SS))
    for r,cells in enumerate(rows):
        y0=r*(rh+g); y1=y0+rh; xs=[0]; acc=0
        for name,frac in cells[:-1]: acc+=frac; xs.append(acc*W)
        xs.append(W)
        for i,(name,frac) in enumerate(cells):
            def ex(x,side,yy):
                if x in (0,W): return x
                off=g/2 if side=='L' else -g/2
                return x+off+sl/2-sl*(yy-y0)/(y1-y0)
            poly=[(ex(xs[i],'L',y0),y0),(ex(xs[i+1],'R',y0),y0),(ex(xs[i+1],'R',y1),y1),(ex(xs[i],'L',y1),y1)]
            bx0=int(min(p[0] for p in poly)); bx1=int(max(p[0] for p in poly)); cw,ch=bx1-bx0,y1-y0
            r_=src_rects[name]
            if len(r_)==2: srcim,(sx0,sy0,sx1,sy1)=r_
            else: srcim=col; sx0,sy0,sx1,sy1=r_
            sw,shh=sx1-sx0,sy1-sy0; s_=max(cw/sw,ch/shh); cw_s,ch_s=cw/s_,ch/s_; cx_=(sx0+sx1)/2; cy_=(sy0+sy1)/2 if name not in FOCUS else min(sy1-ch_s/2,sy0+FOCUS[name]*shh+ch_s/2)
            crop=srcim.crop((int(cx_-cw_s/2),int(cy_-ch_s/2),int(cx_+cw_s/2),int(cy_+ch_s/2))).resize((cw,ch),Image.LANCZOS)
            m=Image.new('L',(cw,ch),0); ImageDraw.Draw(m).polygon([(px-bx0,py-y0) for px,py in poly],fill=255)
            im.paste(crop,(bx0,y0),m)
            if LINES=='comic': od.line(poly+[poly[0]],fill=255,width=lw,joint='curve')
    if LINES=='comic': im.paste(Image.new('RGB',(W,H),BLACK),(0,0),ol)
    else: ImageDraw.Draw(im).rectangle((0,0,W-1,H-1),outline=BLACK,width=g//2)
    return im.resize((W//SS,H//SS),Image.LANCZOS)
def framed(img,rad_in=0.12,border_in=0.06):
    b=P(border_in); r=P(rad_in); w,h=img.size
    out=Image.new('RGBA',(w+2*b,h+2*b),(0,0,0,0)); d=ImageDraw.Draw(out)
    d.rounded_rectangle((0,0,w+2*b-1,h+2*b-1),radius=r+b,fill=WHITE)
    m=Image.new('L',(w,h),0); ImageDraw.Draw(m).rounded_rectangle((0,0,w-1,h-1),radius=r,fill=255)
    out.paste(img,(b,b),m); return out
SHOCK={'shout':(225,8,455,232),'beard_shout':(545,288,742,508),'blonde_beard':(8,552,188,772),'sailor':(272,552,470,772),'masked':(25,808,335,1112),'hardhat':(435,808,742,1112)}
SMILE={'bald':(880,285,1170,505),'grin':(1370,285,1596,505),'mustache':(875,552,1095,772),'army':(1195,552,1385,772),'ring':(935,812,1340,1112),'sailor_smile':(1440,812,1598,1112)}
ROW_H=1.2; WIN_W=3.85
import json as _j
_B=_j.load(open(S+'refs/boxes.json'))
for _k in _B: 
    _im=Image.open(S+f'refs/{_k}_grey.png').convert('RGB'); SHOCK[_k]=(_im,tuple(_B[_k])); SMILE[_k]=(_im,tuple(_B[_k]))
for _k in ['shout','beard_shout','blonde_beard','sailor','masked','hardhat','RA_crotch','TG_biceps','VP_bum']:
    _im=Image.open(S+f'refs/up_{_k}.png').convert('RGB'); SHOCK[_k]=(_im,(0,0,_im.width,_im.height))
for _k in ['bald','army','ring','SW_abs','RA_lats','VP_crotch','RA_hs','SW_hs','HH_hs']:
    _im=Image.open(S+f'refs/up_{_k}.png').convert('RGB'); SMILE[_k]=(_im,(0,0,_im.width,_im.height))
import os as _os
ALL={**SHOCK,**SMILE}
for _k in list(ALL)+['TG_hs','MW_hs','RA_hsw','SW_hsw','MW_hsw','blonde_beard_w','MW_eyes_esr','RA_mouth_esr']:          # always use the sharp, clean-background version when one exists
    if _os.path.exists(S+f'refs/up_{_k}.png'):
        _im=Image.open(S+f'refs/up_{_k}.png').convert('RGB'); ALL[_k]=(_im,(0,0,_im.width,_im.height))
front_rows=[[('beard_shout',1/3),('RA_crotch',1/3),('TG_hs',1/3)],
            [('TG_biceps',1/3),('HH_hs',1/3),('sailor',1/3)],
            [('shout',1/3),('masked',1/3),('VP_bum',1/3)]]
back_rows=[[('bald',1/3),('MW_eyes_esr',1/3),('SW_abs',1/3)],
           [('RA_lats',1/3),('SW_hsw',1/3),('blonde_beard_w',1/3)],
           [('hardhat',1/3),('VP_crotch',1/3),('RA_mouth_esr',1/3)]]
FOCUS={'bald':0.09,'blonde_beard':0.02,'hardhat':0.09,'masked':0.08,'beard_shout':0.0,'sailor':0.04,'shout':0.0}   # where the crop starts (fraction from top) so the whole face shows
# ---------- build ----------
cov=Image.new('RGB',(P(CW),P(CH)),BLUE)
burst(cov,P(FR_X+3.0),P(BL+(1.3 if 'rays' in FX_ else 4.6))); 
back=Image.new('RGB',(P(BL+TW),P(CH)),BLUE); burst(back,P(BL+3.0),P(BL+4.4)); cov.paste(back,(0,0))
def paste(im,x_in,y_in): cov.paste(im,(P(x_in),P(y_in)),im if im.mode=='RGBA' else None)
# FRONT
fx0=FR_X; cx=fx0+3.0
FLASH=sys.argv[3] if len(sys.argv)>3 else 'strap'
G=0.22; FRAME=0.06
L=lg(logo,5.25); logo_top=BL+SAFE; logo_bot=logo_top+L.height/D
title=fit_letters('FIELD JOURNAL',4.6,64)
if FLASH=='strap':     # plain line under the title
    strap=fit_letters('52 WEEKS OF MISSIONS',title.width/D*0.62,22,'toy',WHITE); sg=0.08
elif FLASH=='ribbon':  # red ribbon under the title
    t_=fit_letters('52 WEEKS OF MISSIONS',title.width/D*0.55,20,'toy',WHITE)
    rw,rh=t_.width+P(0.5),t_.height+P(0.16); strap=Image.new('RGBA',(rw,rh),(0,0,0,0)); rd_=ImageDraw.Draw(strap)
    n_=P(0.14); rd_.polygon([(0,0),(rw,0),(rw-n_,rh/2),(rw,rh),(0,rh),(n_,rh/2)],fill=RED,outline=BLACK)
    strap.alpha_composite(t_,((rw-t_.width)//2,(rh-t_.height)//2)); sg=0.08
block_h=title.height/D+sg+strap.height/D
ty=BL+TH-SAFE-block_h
wy=logo_bot+G; wb=ty-G
win_h=wb-wy-2*FRAME
global_row_h=(win_h-GUT*2)/3
win=framed(grid(front_rows,WIN_W,global_row_h,ALL)); paste(win,cx-win.width/D/2,wy)
if 'band' in FX_:       # calm dark header band behind the logo
    bd_=ImageDraw.Draw(cov); bd_.rectangle((P(FR_X),0,P(FR_X+TW+BL),P(logo_bot+0.06)),fill=(10,22,70))
    bd_.rectangle((P(FR_X),P(logo_bot+0.06),P(FR_X+TW+BL),P(logo_bot+0.09)),fill=YEL)
if 'shadow' in FX_:     # soft dark shadow under the logo
    a_=L.getchannel('A'); sh_=Image.new('RGBA',L.size,(0,0,0,0)); sh_.putalpha(a_.point(lambda v:int(v*0.75)))
    pad_=P(0.25); big=Image.new('RGBA',(L.width+2*pad_,L.height+2*pad_),(0,0,0,0)); big.alpha_composite(sh_,(pad_,pad_))
    big=big.filter(ImageFilter.GaussianBlur(P(0.06))); paste(big,cx-L.width/D/2-pad_/D+0.06,logo_top-pad_/D+0.08)
if 'sticker' in FX_:    # white die-cut edge around the logo
    a_=L.getchannel('A'); r_=P(0.07); pad_=r_+2
    ap=Image.new('L',(L.width+2*pad_,L.height+2*pad_),0); ap.paste(a_,(pad_,pad_))
    ap=ap.point(lambda v:255 if v>40 else 0).filter(ImageFilter.MaxFilter(2*(r_//2)+1)).filter(ImageFilter.MaxFilter(2*(r_//2)+1))
    st=Image.new('RGBA',ap.size,WHITE+(255,)); st.putalpha(ap.filter(ImageFilter.GaussianBlur(1)))
    ol=Image.new('RGBA',(ap.width+4,ap.height+4),(0,0,0,0)); apo=Image.new('L',ol.size,0); apo.paste(ap,(2,2)); apo=apo.filter(ImageFilter.MaxFilter(5))
    blk=Image.new('RGBA',ol.size,BLACK+(255,)); blk.putalpha(apo); paste(blk,cx-L.width/D/2-(pad_+2)/D,logo_top-(pad_+2)/D)
    paste(st,cx-L.width/D/2-pad_/D,logo_top-pad_/D)
paste(L,cx-L.width/D/2,logo_top)
paste(title,cx-title.width/D/2,ty)
paste(strap,cx-strap.width/D/2,ty+title.height/D+sg)
print('gaps in',round(wy-logo_bot,3),round(ty-(wy+win.height/D),3))
# SPINE
sx=SP_X; sp=Image.new('RGB',(P(SPW),P(CH)),BLUE); burst(sp,P(SPW/2),P(CH/2)); cov.paste(sp,(P(sx),0))
dd=ImageDraw.Draw(cov); dd.rectangle((P(sx),0,P(sx)+max(1,P(0.012)),P(CH)),fill=BLACK); dd.rectangle((P(sx+SPW)-max(1,P(0.012)),0,P(sx+SPW),P(CH)),fill=BLACK)
# spine: title only, centred, the two parts spaced evenly down the spine
avail=TH-2*SAFE
t1=letters('STIFF COMPETITION',AN(30),LETTER,WHITE); t2=letters('FIELD JOURNAL',AN(30),LETTER,YEL)
t1=t1.crop(t1.getbbox()); t2=t2.crop(t2.getbbox())
h_=max(t1.height,t2.height); sc_=min(1,(SPW-0.3)*D/h_); t1=t1.resize((int(t1.width*sc_),int(t1.height*sc_)),Image.LANCZOS); t2=t2.resize((int(t2.width*sc_),int(t2.height*sc_)),Image.LANCZOS)
free=avail*D-(t1.width+t2.width); g3=free/3          # equal space above, between and below
gap_y=BL+SAFE+(g3+t1.width+g3/2)/D                  # middle of the gap between the two titles
sp=Image.new('RGB',(P(SPW),P(CH)),BLUE); burst(sp,P(SPW/2),P(gap_y)); cov.paste(sp,(P(sx),0))   # burst centred on that gap
dd.rectangle((P(sx),0,P(sx)+max(1,P(0.012)),P(CH)),fill=BLACK); dd.rectangle((P(sx+SPW)-max(1,P(0.012)),0,P(sx+SPW),P(CH)),fill=BLACK)
for t_,y_ in ((t1,g3),(t2,2*g3+t1.width)):
    r_=t_.rotate(-90,expand=True); paste(r_,sx+(SPW-r_.width/D)/2,BL+SAFE+y_/D)
# BACK
bx0=BACK_X; bcx=bx0+3.0
h1=fit_letters('52 WEEKS! 12 MISSIONS!',TW-2*SAFE,60); paste(h1,bcx-h1.width/D/2,BL+SAFE)
bwin=framed(grid(back_rows,h1.width/D-2*FRAME,global_row_h*0.72,ALL)); by=BL+SAFE+h1.height/D+0.16; paste(bwin,bcx-bwin.width/D/2,by)
# banner across the bottom of the picture: what you do with the book
bn_w=bwin.width/D; bn=Image.new('RGBA',(P(bn_w),P(0.5)),(0,0,0,0)); bd=ImageDraw.Draw(bn)
bd.polygon([(0,P(0.06)),(bn.width,0),(bn.width-P(0.05),bn.height),(P(0.04),bn.height-P(0.04))],fill=YEL,outline=BLACK,width=P(0.025))
tx=letters('LOG YOUR MISSIONS. RATE YOUR DAY.',AN(26),'toy',WHITE) if False else None
f=AN(24); t='LOG YOUR MISSIONS.  RATE YOUR DAY.'
while bd.textlength(t,font=f)>bn.width-P(0.3): f=AN(f.size*72/D-1)
bb=bd.textbbox((0,0),t,font=f); bd.text(((bn.width-(bb[2]-bb[0]))/2-bb[0],(bn.height-(bb[3]-bb[1]))/2-bb[1]),t,font=f,fill=BLACK)
bn=bn.rotate(-2,expand=True,resample=Image.BICUBIC); paste(bn,bcx-bn.width/D/2,by+bwin.height/D+0.06)
# what's inside (facts from the Journal Playbook)
iy=by+bwin.height/D+0.06+bn.height/D+0.1
ins=[("364","DAY PAGES"),("12","MISSION BRIEFINGS"),("6","PERSONNEL FILES")]
colw=(TW-2*SAFE)/3
for i,(n_,lab) in enumerate(ins):
    ccx=bx0+SAFE+colw*(i+0.5)
    nimg=letters(n_,AN(40),LETTER,YEL); paste(nimg,ccx-nimg.width/D/2,iy)
    f=OS(14); bb=dd.textbbox((0,0),lab,font=f); dd.text((P(ccx)-(bb[2]-bb[0])/2-bb[0],P(iy)+nimg.height+P(0.04)),lab,font=f,fill=WHITE,stroke_width=max(1,P(0.012)),stroke_fill=BLACK)
# barcode area meets both printers: Lulu 2.5 x 1.7 in (incl. white padding), 0.25 in from every edge;
# KDP own barcode at least 0.76 in from the bottom and 0.25 in from the spine
BW_,BH_=2.5,1.7; bcx1=SP_X-0.30; bcy1=BL+TH-0.80
dd.rectangle((P(bcx1-BW_),P(bcy1-BH_),P(bcx1),P(bcy1)),fill=WHITE,outline=BLACK,width=max(1,P(0.01)))
f=OS(9); lab_='BARCODE AREA (2.5 x 1.7 in)'; dd.text((P(bcx1-BW_/2)-dd.textlength(lab_,font=f)/2,P(bcy1-BH_/2)),lab_,font=f,fill=(140,140,140))
tag=OS(17); bbt=dd.textbbox((0,0),'STIFFCOMPETITION.SHOP',font=tag); dd.text((P(bx0+SAFE),P(bcy1)-(bbt[3]-bbt[1])-bbt[1]),'STIFFCOMPETITION.SHOP',font=tag,fill=WHITE,stroke_width=max(1,P(0.015)),stroke_fill=BLACK)
out=S+f'cover/cover_v13_{LINES}_{D}dpi.jpg'; cov.save(out,quality=90)
# guides copy: trim, spine folds and safe area
g=cov.copy(); gd=ImageDraw.Draw(g)
for x in (BL,SP_X,FR_X,CW-BL): gd.line((P(x),0,P(x),P(CH)),fill=(0,255,255),width=1)
for y in (BL,CH-BL): gd.line((0,P(y),P(CW),P(y)),fill=(0,255,255),width=1)
for x0 in (BACK_X,FR_X): gd.rectangle((P(x0+SAFE),P(BL+SAFE),P(x0+TW-SAFE),P(BL+TH-SAFE)),outline=(0,255,0),width=1)
g.save(out.replace('.jpg','_guides.jpg'),quality=85); print(out, cov.size)
