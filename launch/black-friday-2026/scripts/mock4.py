exec(open('mock3.py').read().split("o=Image.new('RGBA',(W,H),(0,0,0,255)); glow")[0])
def fade_img(im,top=0,bot=0,side=0):
    g=Image.new('L',im.size,255); px=g.load(); w,h=im.size
    for y in range(h):
        v=255
        if top and y<top: v=int(255*y/top)
        if bot and y>h-bot: v=int(255*(h-y)/bot)
        for x in range(w):
            sv=1.0
            if side: sv=min(1.0,x/side,(w-1-x)/side)
            px[x,y]=int(v*sv)
    im=im.copy(); im.putalpha(g); return im
fr=Image.open('mw_last.png').convert('RGB')
def figure(o,scale_w=800,y=540,x=None,ch=1.25):
    f2=fr.resize((scale_w,int(fr.height*scale_w/fr.width))).crop((0,0,scale_w,int(scale_w*ch))).convert('RGBA')
    f2=fade_img(f2,bot=260,side=140); o.alpha_composite(f2,(((W-scale_w)//2) if x is None else x,y))
def texts(o):
    ctext(o,"10% OFF",225,980,170,WHITE,(0,0,0),8)
    ctext(o,"PRICES DROP. MAJOR WOOD STAYS UP.",405,980,56,GOLD,(0,0,0),4)
# C-mug
o=Image.new('RGBA',(W,H),(0,0,0,255)); glow(o,W/2,1150,750)
figure(o,760,500,ch=0.95)
mw=740; ml=mugc.resize((mw,int(mugc.height*mw/mugc.width)),Image.LANCZOS)
sh=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(sh).ellipse((90,1790,780,1870),fill=(0,0,0,170)); o.alpha_composite(sh.filter(ImageFilter.GaussianBlur(25)))
o.alpha_composite(ml,(80,1840-ml.height))
texts(o); watermark(o); o.convert('RGB').save('mockC_mug.png')
# C-tee: full model photo, big
tee=Image.open('xm_tee_main.jpg').convert('RGB'); sc=W/tee.width; th=int(tee.height*sc); ti=tee.resize((W,th),Image.LANCZOS).convert('RGBA')
top=np.array(tee.crop((0,0,tee.width,12))).reshape(-1,3).mean(axis=0).astype(int)
bgc=tuple(int(v) for v in top)
o=Image.new('RGBA',(W,H),bgc+(255,))
ti=fade_img(ti,top=60); o.alpha_composite(ti,(0,H-th))
ctext(o,"10% OFF",225,980,170,WHITE,(0,40,90),8)
ctext(o,"PRICES DROP. MAJOR WOOD STAYS UP.",405,980,56,WHITE,(0,40,90),5)
watermark(o); o.convert('RGB').save('mockC_tee.png')
sheet=Image.new('RGB',(2*540+20,960),(30,30,30))
for i,p in enumerate(['mockC_mug.png','mockC_tee.png']): sheet.paste(Image.open(p).resize((540,960)),(i*560,0))
sheet.save('mockC_sheet.png'); print('ok')
