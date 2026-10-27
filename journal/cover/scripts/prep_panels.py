import numpy as np, onnxruntime as ort, json, sys
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi
sess=ort.InferenceSession('models/realesrgan_x4plus.onnx',providers=['CPUExecutionProvider'])
def up(img):
    x=np.asarray(img.convert('RGB')).astype(np.float32).transpose(2,0,1)[None]/255
    H,W=x.shape[2:]; T=192; P=12; out=np.zeros((3,H*4,W*4),np.float32)
    for y in range(0,H,T):
        for xx in range(0,W,T):
            y0,x0=max(0,y-P),max(0,xx-P); y1,x1=min(H,y+T+P),min(W,xx+T+P)
            o=sess.run(None,{'input':x[:,:,y0:y1,x0:x1]})[0][0]
            oy,ox=(y-y0)*4,(xx-x0)*4; h,w=min(T,H-y)*4,min(T,W-xx)*4
            out[:,y*4:y*4+h,xx*4:xx*4+w]=o[:,oy:oy+h,ox:ox+w]
    return Image.fromarray((np.clip(out,0,1).transpose(1,2,0)*255).round().astype(np.uint8))
def popbg(size,col):
    w,h=size; bg=Image.new('RGB',size,col); d=ImageDraw.Draw(bg); step=max(14,w//28); r=step*0.22
    dark=tuple(int(c*0.82) for c in col)
    for j,y in enumerate(range(0,h+step,step)):
        for x in range(-step,w+step,step):
            xx=x+(step//2 if j%2 else 0); d.ellipse((xx-r,y-r,xx+r,y+r),fill=dark)
    return bg
FACES={'shout':(225,8,455,232),'beard_shout':(545,277,742,508),'blonde_beard':(8,552,188,772),'sailor':(272,552,470,772),'masked':(25,808,335,1112),'hardhat':(435,808,742,1112),
       'bald':(900,285,1170,505),'grin':(1370,285,1596,505),'mustache':(875,552,1095,772),'army':(1195,552,1385,772),'ring':(935,812,1340,1112),'sailor_smile':(1440,812,1598,1112)}
BODY={'RA_crotch':('RA_front.png',(380,450,710,700),(255,214,0)),'TG_biceps':('TG_front.png',(600,250,890,560),(216,38,44)),'VP_bum':('VP_back.jpg',(250,545,560,790),(0,174,224)),
      'SW_abs':('SW_front.png',(320,400,610,660),(255,214,0)),'RA_lats':('RA_back.jpg',(150,250,620,600),(216,38,44)),'VP_crotch':('VP_front.png',(600,1150,1220,1620),(0,174,224))}
which=sys.argv[1]
col=Image.open('cover/collage.jpg').convert('RGB')
if which=='faces':
    for k,b in FACES.items():
        up(col.crop(b)).save(f'refs/up_{k}.png'); print(k,flush=True)
else:
    for k,(fn,b,c) in BODY.items():
        src=Image.open('refs/'+fn).convert('RGB'); a=np.asarray(src).astype(int)
        m=a.max(axis=2)>38; lab,n=ndi.label(ndi.binary_opening(m,iterations=2)); big=lab==(np.bincount(lab.ravel())[1:].argmax()+1)
        m=ndi.binary_fill_holes(ndi.binary_closing(big,iterations=3)); m=ndi.binary_erosion(m,iterations=3)   # trim the dark rim
        crop=src.crop(b); mk=Image.fromarray((m*255).astype(np.uint8)).crop(b)
        if crop.width<600: crop=up(crop); mk=mk.resize(crop.size,Image.LANCZOS)
        mk=mk.filter(ImageFilter.GaussianBlur(1.2))
        bg=popbg(crop.size,c); bg.paste(crop,(0,0),mk); bg.save(f'refs/up_{k}.png'); print(k,crop.size,flush=True)
