import json,sys
sys.path.insert(0,'.')
from render import *
P=[
 ('mw','MAJOR WOOD','UP AT DAWN, NEVER AT EASE','UP AND STAYING UP'),
 ('hh','HANKY','TOOLS OUT, HARD HAT ON','FULLY EXTENDED'),
 ('tg','GRIP','FIRM HANDS ON, NEVER LETS GO','A FIRM HOLD'),
 ('vp','VELVET PYTHON','FULL LENGTH, NEVER SOFT','THE PYTHON IS HUNGRY'),
 ('sw','SLICK WILLY','SLIPS IN EASY, SLIDES OUT SLOW','SLIPPERY'),
 ('ra','ADMIRAL','HEAVY CARGO, SEEKING PORT','IMMEDIATE BOARDING'),
]
for c,name,ph,pr in P:
    o='out/gg_%s_'%c
    hook(c,name,o+'1.jpg')
    items=[(c+'_tee','tee','THE TEE',ph),(c+'_mug','mug','THE MUG',ph),(c+'_bottle','b','THE BOTTLE',ph),(c+'_print','p','THE MUSEUM PRINT',pr)]
    for i,(s,k,l,line) in enumerate(items): prod(s,k,l,line,i,4,o+'%d.jpg'%(i+2))
    srcs=[(s,k) for s,k,_,_ in items]
    cta(srcs,'FOUR GIFTS.','ONE %s.'%name,o+'6.jpg')
    ximg(srcs,'CHRISTMAS SORTED.','FOR THE %s IN YOUR LIFE.'%name,o+'x.jpg')
# mugs post
o='out/gg_mugs_'
im=Image.new('RGB',(1080,1350),K); d=ImageDraw.Draw(im)
ctext(d,'SECRET SANTA',70,R,110); ctext(d,'SORTED.',200,Y,170)
codes=['mw','hh','tg','vp','sw','ra']
for i,c in enumerate(codes):
    ch=char(c,330); x=[30,375,720][i%3]; y=440+(i//3)*320
    im.paste(ch,(x,y),ch)
d.rectangle((0,1130,1080,1350),fill=K)
ctext(d,'ONE MUG. SIX CHOICES.',1160,W,100)
im.save(o+'1.jpg',quality=90)
names={'mw':('THE MAJOR WOOD MUG','UP AT DAWN, NEVER AT EASE'),'hh':("THE HANKY MUG",'TOOLS OUT, HARD HAT ON'),'tg':('THE GRIP MUG','FIRM HANDS ON, NEVER LETS GO'),'vp':('THE VELVET PYTHON MUG','FULL LENGTH, NEVER SOFT'),'sw':('THE SLICK WILLY MUG','SLIPS IN EASY, SLIDES OUT SLOW'),'ra':('THE ADMIRAL MUG','HEAVY CARGO, SEEKING PORT')}
for i,c in enumerate(codes): prod(c+'_mug','mug',names[c][0],names[c][1],i,6,o+'%d.jpg'%(i+2))
cta([('mw_mug','m'),('hh_mug','m'),('tg_mug','m'),('vp_mug','m')],'SIX MUGS.','PICK YOUR MAN.',o+'8.jpg')
ximg([('mw_mug','m'),('hh_mug','m'),('vp_mug','m'),('ra_mug','m')],'SECRET SANTA SORTED.','ONE MUG. SIX CHOICES.',o+'x.jpg')
print('done')
