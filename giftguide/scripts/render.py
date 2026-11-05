import sys
from PIL import Image, ImageDraw, ImageFont, ImageOps
G='/tmp/claude-0/-home-claude/1c72146d-8d83-5791-ac40-334afdb105b7/scratchpad/gg/'
A='/home/claude/sc-assets/dtb/'
F=G+'fonts/Anton-Regular.ttf'
Y=(255,214,0);R=(230,30,40);W=(255,255,255);K=(10,10,10)
def font(s): return ImageFont.truetype(F,s)
def fit_text(d,t,maxw,size):
    while size>20:
        f=font(size); l,tp,r,b=f.getbbox(t)
        if r-l<=maxw: return f
        size-=2
    return font(size)
def ctext(d,t,y,col,size,maxw=980,cx=540):
    f=fit_text(d,t,maxw,size); l,tp,r,b=f.getbbox(t)
    d.text((cx-(l+r)/2,y-tp),t,font=f,fill=col); return y+(b-tp)
def photo(name,kind):
    im=Image.open(G+'src/'+name+'.jpg').convert('RGB')
    if kind=='tee':  # crop the chest so the print is big
        w,h=im.size; s=760; x=(w-s)//2; y=int(h*0.36)
        im=im.crop((x,y,x+s,y+s))
    return ImageOps.fit(im,(1080,1080),Image.LANCZOS)
def char(code,w):
    c=Image.open(A+'char_%s.png'%code).convert('RGBA')
    return c.resize((w,round(c.height*w/c.width)),Image.LANCZOS)
def hook(code,name,out):
    im=Image.new('RGB',(1080,1350),K); d=ImageDraw.Draw(im)
    ctext(d,'CHRISTMAS GIFT GUIDE',70,R,70)
    ctext(d,'SORTED.',160,Y,170)
    c=char(code,900); im.paste(c,((1080-c.width)//2,1350-c.height-300),c)
    d.rectangle((0,1050,1080,1350),fill=K)
    ctext(d,'FOR THE %s'%name,1075,W,120)
    ctext(d,'IN YOUR LIFE.',1210,R,95)
    im.save(out,quality=90)
def prod(src,kind,label,line,n,tot,out):
    im=Image.new('RGB',(1080,1350),K); im.paste(photo(src,kind),(0,0)); d=ImageDraw.Draw(im)
    ctext(d,label,1105,Y,105)
    ctext(d,line,1240,W,62)
    im.save(out,quality=90)
def grid(srcs,box):
    x0,y0,w,h,gap=box; cw=(w-gap)//2; ch=(h-gap)//2; tiles=[]
    for i,(s,k) in enumerate(srcs):
        p=photo(s,k).resize((cw,ch),Image.LANCZOS); tiles.append((p,x0+(i%2)*(cw+gap),y0+(i//2)*(ch+gap)))
    return tiles
def cta(srcs,l1,l2,out):
    im=Image.new('RGB',(1080,1350),K); d=ImageDraw.Draw(im)
    ctext(d,l1,60,Y,120); ctext(d,l2,195,W,90)
    for p,x,y in grid(srcs,(90,330,900,800,16)): im.paste(p,(x,y))
    bar=Image.open(A+'bar.png').convert('RGB'); im.paste(bar,(60,1185))
    im.save(out,quality=90)
def ximg(srcs,l1,l2,out):
    im=Image.new('RGB',(1080,1440),K); d=ImageDraw.Draw(im)
    ctext(d,l1,40,Y,110); ctext(d,l2,170,W,80)
    for p,x,y in grid(srcs,(40,300,1000,1000,16)): im.paste(p,(x,y))
    ctext(d,'STIFFCOMPETITION.SHOP',1335,R,70)
    im.save(out,quality=90)
