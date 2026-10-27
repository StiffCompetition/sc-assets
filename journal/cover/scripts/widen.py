# wide version of a collage face for the back cells: keep the whole face, extend the dot background either side
import numpy as np
from PIL import Image, ImageDraw
src=open('scripts/prep_panels.py').read(); exec(src[src.index('def popbg'):src.index('FACES=')])
def popbg_step(size,col,step):
    w,h=size; bg=Image.new('RGB',size,col); d=ImageDraw.Draw(bg); r=step*0.22; dark=tuple(int(c*0.82) for c in col)
    for j,y in enumerate(range(0,h+step,step)):
        for x in range(-step,w+step,step):
            xx=x+(step//2 if j%2 else 0); d.ellipse((xx-r,y-r,xx+r,y+r),fill=dark)
    return bg
J={'blonde_beard':((216,38,44),0.0,0.63)}
for k,(c,y0,y1) in J.items():
    im=Image.open(f'refs/up_{k}.png').convert('RGB'); w,h=im.size; im=im.crop((0,int(h*y0),w,int(h*y1))); H=im.height; Wc=int(H*1.95)
    f=int(w*0.10); a=np.ones((H,w)); ramp=np.linspace(0,1,f); a[:,:f]*=ramp; a[:,-f:]*=ramp[::-1]   # soft sides so nothing ends in a hard line
    m=Image.fromarray((a*255).astype(np.uint8))
    step=max(14,w//28)                                   # same dot size and spacing as the panel's own background
    ox=((Wc-w)//2)//(2*step)*(2*step); Wc=w+2*ox
    bg=popbg_step((Wc,H),c,step); bg.paste(im,(ox,0),m); bg.save(f'refs/up_{k}_w.png')
    t=bg.copy(); t.thumbnail((600,300)); t.save('cover/_bw.png')
