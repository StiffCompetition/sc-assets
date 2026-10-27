# extreme close-ups for the back cover: Major Wood's eyes, Rear Admiral's grin (back-panel shape)
from PIL import Image, ImageDraw, ImageFont
src=open('scripts/prep_panels.py').read(); exec(src[src.index('def popbg'):src.index('FACES=')])
AR=1.95
Z={'MW_eyes':('refs/MW_hs_src.png',0.51,0.297,0.427),'RA_mouth':('refs/RA_hs.png',0.515,0.50,0.69)}   # centre x, top y, bottom y (fractions of the figure)
out={}
for k,(f,cx,y0,y1) in Z.items():
    im=Image.open(f).convert('RGBA'); im=im.crop(im.getchannel('A').getbbox()); w,h=im.size
    H=(y1-y0)*h; W=H*AR; box=(int(cx*w-W/2),int(y0*h),int(cx*w+W/2),int(y1*h))
    c=im.crop(box); bg=popbg(c.size,(255,214,0)); bg.paste(c,(0,0),c); c=bg; c.save(f'refs/up_{k}.png'); out[k]=c
if __name__=='__main__':
    F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',26)
    ph=int(700/AR); s=Image.new('RGB',(1460,ph+60),'white'); d=ImageDraw.Draw(s)
    for j,(k,lab) in enumerate([('MW_eyes','Major Wood - eyes'),('RA_mouth','Rear Admiral - mouth')]):
        d.text((10+j*740,10),lab,fill='black',font=F); s.paste(out[k].resize((700,ph),Image.LANCZOS),(10+j*740,50))
    s.save('cover/Back head zoom preview 3.jpg',quality=92); print({k:v.size for k,v in out.items()})
