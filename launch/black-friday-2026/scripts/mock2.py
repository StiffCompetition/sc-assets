from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageFile
import numpy as np
from scipy import ndimage
ImageFile.LOAD_TRUNCATED_IMAGES=True
exec(open('mock.py').read().split("mug=Image.open")[0])   # reuse f, ctext, wm, watermark
mug=Image.open('mw_mug.jpg').convert('RGB')
a=np.array(mug).astype(int)
bgm=(a[...,0]-a[...,1]>70)
lab,n=ndimage.label(bgm)
border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
bg=np.isin(lab,list(border))
fg=~bg
fg=ndimage.binary_opening(fg,iterations=2)
fg=fg&~bgm
lab2,n2=ndimage.label(fg); sizes=ndimage.sum(fg,lab2,range(1,n2+1)); fg=lab2==(1+int(np.argmax(sizes)))
al=ndimage.gaussian_filter(fg.astype(float),2.0)
cut=np.dstack([a.astype(np.uint8),(al*255).astype(np.uint8)]); cut=Image.fromarray(cut,'RGBA'); cut=cut.crop(cut.getbbox())
print('cut',cut.size)
RED=(232,38,43); WHITE=(255,255,255); GOLD=(255,196,90)
def stage(color=(0,0,0)):
    return Image.new('RGBA',(W,H),color+(255,))
def glow(im,cx,cy,r,col=GOLD,peak=170):
    yy,xx=np.mgrid[0:H,0:W]; d=np.sqrt((xx-cx)**2+(yy-cy)**2)/r
    al=(np.clip(1-d,0,1)**2*peak).astype(np.uint8)
    g=np.dstack([np.full((H,W),col[0],np.uint8),np.full((H,W),col[1],np.uint8),np.full((H,W),col[2],np.uint8),al])
    im.alpha_composite(Image.fromarray(g,'RGBA'))
def place(im,img,cx,bottom,width):
    s=width/img.width; l=img.resize((width,int(img.height*s)),Image.LANCZOS)
    im.alpha_composite(l,(int(cx-width/2),int(bottom-l.height)))
# Option 1: brand-colour hero (clean flat pink, mug cut-out with soft shadow)
o1=Image.new('RGBA',(W,H),(250,80,150,255))
yy=np.linspace(0,1,H)[:,None]; grad=np.dstack([np.broadcast_to((255*(0.98-0.12*yy)),(H,W)),np.broadcast_to((88*(1-0.25*yy)),(H,W)),np.broadcast_to((158*(1-0.2*yy)),(H,W)),np.full((H,W),255)]).astype(np.uint8)
o1=Image.fromarray(grad,'RGBA')
sh=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(sh).ellipse((170,1560,910,1650),fill=(90,0,40,150)); o1.alpha_composite(sh.filter(ImageFilter.GaussianBlur(30)))
place(o1,cut,W/2,1650,840)
ctext(o1,"10% OFF",270,980,240,WHITE,(60,0,30),10)
ctext(o1,"PRICES DROP.",530,980,72,WHITE,(60,0,30),6)
ctext(o1,"MAJOR WOOD STAYS UP.",612,980,72,WHITE,(60,0,30),6)
watermark(o1); o1.convert('RGB').save('mockA.png')
# Option 2: black stage, gold glow, mug cut-out
o2=stage(); glow(o2,W/2,1250,650)
place(o2,cut,W/2,1620,880)
ctext(o2,"10% OFF",280,980,250,WHITE,(0,0,0),8)
ctext(o2,"ALL MERCH · 27–30 NOV",580,980,68,GOLD,(0,0,0),5)
watermark(o2); o2.convert('RGB').save('mockB.png')
# Option 3: Major Wood with the mug beside him, same black stage as the clip
fr=Image.open('mw_last.png').convert('RGB'); fr=fr.resize((W,int(fr.height*W/fr.width)))
o3=stage(); glow(o3,W/2,1000,800,peak=110)
o3.alpha_composite(fr.convert('RGBA').crop((0,0,W,1250)),(0,520)) if False else None
topfig=fr.crop((0,0,W,1100)).convert('RGBA')
g=Image.new('L',(W,1100)); px=g.load()
for y in range(1100):
    v=255 if y<800 else int(255*(1-(y-800)/300))
    for x in range(W): px[x,y]=v
topfig.putalpha(g); o3.alpha_composite(topfig,(0,560))
place(o3,cut,W*0.70,1700,520)
ctext(o3,"10% OFF",270,980,170,WHITE,(0,0,0),8)
ctext(o3,"PRICES DROP. MAJOR WOOD STAYS UP.",490,980,56,GOLD,(0,0,0),4)
watermark(o3); o3.convert('RGB').save('mockC.png')
sheet=Image.new('RGB',(3*540+40,960),(30,30,30))
for i,p in enumerate(['mockA.png','mockB.png','mockC.png']):
    sheet.paste(Image.open(p).resize((540,960)),(i*560,0))
sheet.save('mock_sheet2.png')
