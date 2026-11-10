exec(open('mock.py').read())
GOLD=(255,196,90); WHITE=(255,255,255)
def cutout(path,keyfn,erode=0):
    a=np.array(Image.open(path).convert('RGB')).astype(int)
    bgm=keyfn(a); lab,n=ndimage.label(bgm)
    border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
    bg=np.isin(lab,list(border)); fg=(~bg)&(~bgm)
    fg=ndimage.binary_opening(fg,iterations=2)
    l2,n2=ndimage.label(fg); sz=ndimage.sum(fg,l2,range(1,n2+1)); fg=l2==(1+int(np.argmax(sz)))
    al=ndimage.gaussian_filter(fg.astype(float),1.6)
    im=Image.fromarray(np.dstack([a.astype(np.uint8),(al*255).astype(np.uint8)]),'RGBA'); return im.crop(im.getbbox())
mugc=cutout('xm_mug_left.jpg',lambda a:(a[...,2]-a[...,0])>70)
print('mug',mugc.size)
def glow(im,cx,cy,r,peak=110):
    yy,xx=np.mgrid[0:H,0:W]; d=np.sqrt((xx-cx)**2+(yy-cy)**2)/r
    al=(np.clip(1-d,0,1)**2*peak).astype(np.uint8)
    g=np.dstack([np.full((H,W),GOLD[0],np.uint8),np.full((H,W),GOLD[1],np.uint8),np.full((H,W),GOLD[2],np.uint8),al]); im.alpha_composite(Image.fromarray(g,'RGBA'))
o=Image.new('RGBA',(W,H),(0,0,0,255)); glow(o,W/2,900,800)
# tee close: crop print area, full width
tee=Image.open('xm_tee_close.jpg').convert('RGB'); crop=tee.crop((0,300,1500,1700)); s=W/crop.width
tee_i=crop.resize((W,int(crop.height*s)),Image.LANCZOS).convert('RGBA')   # 1080x1008
g=Image.new('L',tee_i.size); px=g.load()
for y in range(tee_i.height):
    v=int(255*min(1,y/220)) 
    for x in range(W): px[x,y]=v
tee_i.putalpha(g); o.alpha_composite(tee_i,(0,H-tee_i.height))
# figure
fr=Image.open('mw_last.png').convert('RGB'); fr=fr.resize((W,int(fr.height*W/fr.width)))
fig=fr.crop((0,0,W,1000)).convert('RGBA'); g2=Image.new('L',(W,1000)); p2=g2.load()
for y in range(1000):
    v=255 if y<700 else int(255*(1-(y-700)/300))
    for x in range(W): p2[x,y]=v
fig.putalpha(g2); o.alpha_composite(fig,(0,520))
# mug big, bottom-left overlapping tee
mw=680; ml=mugc.resize((mw,int(mugc.height*mw/mugc.width)),Image.LANCZOS)
sh=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(sh).ellipse((30,1760,720,1850),fill=(0,0,0,160)); o.alpha_composite(sh.filter(ImageFilter.GaussianBlur(25)))
o.alpha_composite(ml,(20,1790-ml.height))
ctext(o,"10% OFF",270,980,170,WHITE,(0,0,0),8)
ctext(o,"PRICES DROP. MAJOR WOOD STAYS UP.",470,980,56,GOLD,(0,0,0),4)
watermark(o); o.convert('RGB').save('mockC2.png'); print('ok')
