exec(open('spec8.py').read().split("UPP=90")[0])
import numpy as np
from scipy import ndimage as ndi
_full=b.cover(b.desk,940,800,0.0)
hsv=np.array(_full.convert('HSV')).astype(int)
m=((hsv[...,1]>90)|(hsv[...,2]<110))
m=ndi.binary_closing(m,structure=np.ones((31,31)),iterations=1)
m=ndi.binary_opening(m,structure=np.ones((71,71)))
lab,nl=ndi.label(m); sizes=ndi.sum(m,lab,range(1,nl+1)); m=lab==(1+int(np.argmax(sizes)))
m=ndi.binary_fill_holes(m)
m=m|np.roll(m,6,0)
BOOK=Image.fromarray((m*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
ys,xs=np.where(m); print('bbox',xs.min(),xs.max(),ys.min(),ys.max())
_bg=_full.crop((0,0,36,H)).resize((W,H),Image.BICUBIC).filter(ImageFilter.GaussianBlur(24))
def cover6(s=0.72,top=272):
    x0,x1,y0,y1=xs.min(),xs.max(),ys.min(),ys.max()
    cxs=(x0+x1)/2
    fw,fh=int(W*s),int(H*s); fg=_full.resize((fw,fh),Image.LANCZOS); mk=BOOK.resize((fw,fh),Image.LANCZOS)
    ox=int(540-cxs*s); oy=int(top-y0*s)
    out=_bg.copy().convert('RGBA')
    # soft shadow under book
    sh=Image.new('RGBA',(W,H),(0,0,0,0)); sd=ImageDraw.Draw(sh); by=oy+int(y1*s)
    sd.ellipse((ox+int(x0*s)+10,by-30,ox+int(x1*s)-10,by+8),fill=(70,50,30,150)); out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)))
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); lay.paste(fg.convert('RGBA'),(ox,oy)); a=Image.new('L',(W,H),0); a.paste(mk,(ox,oy)); lay.putalpha(a)
    out.alpha_composite(lay); return out
if __name__=='__main__':
    c=cover6(0.72,272); c.convert('RGB').resize((540,960)).save('cover6_s.png'); c.convert('RGB').crop((0,200,1080,700)).save('cover6_top.png')
