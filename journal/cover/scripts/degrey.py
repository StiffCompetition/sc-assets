# swap the grey studio background behind the collage faces for pop-art dots (keeps the figure, edges softened)
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
from scipy import ndimage as ndi
src=open('scripts/prep_panels.py').read(); exec(src[src.index('def popbg'):src.index('FACES=')])
COL={'beard_shout':(0,174,224),'shout':(0,174,224),'sailor':(255,214,0),'masked':(255,214,0),'blonde_beard':(216,38,44),'hardhat':(255,214,0)}
sheet=Image.new('RGB',(6*260,300),'white')
for i,(k,c) in enumerate(COL.items()):
    fn=f'refs/up_{k}.png'; import os
    if not os.path.exists(f'refs/up_{k}_greyorig.png'): Image.open(fn).save(f'refs/up_{k}_greyorig.png')
    im=Image.open(f'refs/up_{k}_greyorig.png').convert('RGB'); a=np.asarray(im).astype(float)
    mx=a.max(2); mn=a.min(2); sat=(mx-mn)/np.maximum(mx,1)
    grey=(sat<0.10)&(mx>70)&(mx<240)
    if k in ('sailor','blonde_beard','shout','hardhat'): grey|=(mx<35)   # old collage divider corners
    grey=ndi.binary_opening(grey,iterations=2)
    lab,n=ndi.label(grey); edge=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
    bgm=np.isin(lab,list(edge)); bgm=ndi.binary_closing(bgm,iterations=3)
    fg=Image.fromarray(((~bgm)*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5))
    out=popbg(im.size,c); out.paste(im,(0,0),fg); out.save(fn)
    t=out.copy(); t.thumbnail((260,300)); sheet.paste(t,(i*260,0))
sheet.save('cover/_dg.png')
