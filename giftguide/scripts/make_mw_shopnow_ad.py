from PIL import Image, ImageDraw, ImageFont, ImageFilter
A='/home/claude/sc-assets/giftguide/ads/assets/'
F='/usr/share/fonts/truetype/google-fonts/ofl/anton/Anton-Regular.ttf'
W,H=1080,1350
bg=Image.open(A+'bg_xmas_table.jpg').convert('RGB').resize((1080,1440))
bg=bg.crop((0,60,1080,1410)).resize((W,H))
im=bg.convert('RGBA')
# darken top for text
ov=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
for y in range(0,430):
    d.line([(0,y),(W,y)],fill=(0,0,0,int(170*(1-y/430))))
for y in range(H-380,H):
    d.line([(0,y),(W,y)],fill=(0,0,0,int(200*((y-(H-380))/380))))
im=Image.alpha_composite(im,ov)
def shadow(layer,pos,blur=18,alpha=150):
    s=Image.new('RGBA',im.size,(0,0,0,0))
    a=layer.split()[3].point(lambda v:int(v*alpha/255))
    blk=Image.new('RGBA',layer.size,(0,0,0,255)); blk.putalpha(a)
    s.paste(blk,pos,blk); return s.filter(ImageFilter.GaussianBlur(blur))
fig=Image.open(A+'mw_figure_cut.png').convert('RGBA'); fig=fig.resize((540,int(540*fig.height/fig.width)))
fp=(40,440)
fa=fig.split()[3]; g=Image.new('L',fig.size,255); gd=ImageDraw.Draw(g)
for yy in range(fig.height-170,fig.height): gd.line([(0,yy),(fig.width,yy)],fill=int(255*(1-(yy-(fig.height-170))/170)))
fig.putalpha(Image.composite(fa,Image.new('L',fig.size,0),g).point(lambda v:v) if False else Image.eval(Image.merge('L',(fa,)),lambda v:v))
from PIL import ImageChops
fig.putalpha(ImageChops.multiply(fa,g))
im=Image.alpha_composite(im,shadow(fig,(fp[0]+14,fp[1]+22)))
im.alpha_composite(fig,fp)
mug=Image.open(A+'mw_mug_cut.png').convert('RGBA'); mug=mug.resize((400,int(400*mug.height/mug.width)))
mp=(600,560)
im=Image.alpha_composite(im,shadow(mug,(mp[0]+10,mp[1]+26)))
im.alpha_composite(mug,mp)
d=ImageDraw.Draw(im)
def txt(t,y,size,fill,stroke=0,anchor='mm'):
    f=ImageFont.truetype(F,size)
    d.text((W//2+3,y+4),t,font=f,fill=(0,0,0,180),anchor=anchor)
    d.text((W//2,y),t,font=f,fill=fill,anchor=anchor,stroke_width=stroke,stroke_fill=(0,0,0))
txt('SHOP NOW',120,150,(255,255,255,255))
txt('FOR CHRISTMAS',255,112,(255,204,0,255))
txt('MAJOR WOOD CHRISTMAS TEE, MUG & MORE',1010,42,(255,255,255,255))
# button
bx0,by0,bx1,by1=170,1070,910,1175
d.rounded_rectangle((bx0,by0,bx1,by1),radius=24,fill=(200,16,46,255),outline=(255,255,255,255),width=5)
f=ImageFont.truetype(F,66); d.text((W//2,(by0+by1)//2+2),'STIFFCOMPETITION.SHOP',font=f,fill=(255,255,255,255),anchor='mm')
logo=Image.open(A+'logo_chrome_full.png').convert('RGBA'); logo=logo.resize((330,int(330*logo.height/logo.width)))
im.alpha_composite(logo,((W-330)//2,1190))
out=im.convert('RGB'); out.save('gg_mw_ad_ig.jpg',quality=92)
# X image 16:9-ish 1200x675 crop
x=out.resize((1080,1350)); 
