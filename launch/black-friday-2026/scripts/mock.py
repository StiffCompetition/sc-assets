from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageFile
import numpy as np
from scipy import ndimage
ImageFile.LOAD_TRUNCATED_IMAGES=True
W,H=1080,1920
FB="/usr/share/fonts/opentype/inter/Inter-Black.otf"
def f(s): return ImageFont.truetype(FB,s)
def ctext(im,t,y,maxw,start,fill,stroke=(0,0,0),sw=0,x=None):
    d=ImageDraw.Draw(im); s=start
    while d.textlength(t,font=f(s))>maxw: s-=4
    w=d.textlength(t,font=f(s)); X=(W-w)/2 if x is None else x
    d.text((X,y),t,font=f(s),fill=fill,stroke_width=sw,stroke_fill=stroke); return s
src=np.array(Image.open('wm_old.png').convert('RGBA'))
m=src[...,3]>20; lab,n=ndimage.label(m); sz=ndimage.sum(m,lab,range(1,n+1))
for i,v in enumerate(sz):
    if v<400: src[...,3][lab==i+1]=0
wm=Image.fromarray(src); wm=wm.crop(wm.getbbox())
def watermark(im,size=190):
    plate=Image.new('RGBA',(size+40,size+40),(0,0,0,0))
    ImageDraw.Draw(plate).rounded_rectangle((0,0,size+39,size+39),radius=28,fill=(255,255,255,158))
    l=wm.resize((size,int(size*wm.height/wm.width)),Image.LANCZOS)
    a=np.array(l).astype(float); a[...,:3]=20; a[...,3]*=0.9; l=Image.fromarray(a.astype(np.uint8))
    plate.alpha_composite(l,(20,20+(size-l.height)//2))
    im.alpha_composite(plate,(W-30-plate.width,H-30-plate.height))
mug=Image.open('mw_mug.jpg').convert('RGB')
