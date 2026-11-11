import numpy as np, subprocess
from PIL import Image, ImageDraw, ImageFont
W,H=1080,1920; FPS=30
font=ImageFont.truetype('fonts/x/package/files/anton-latin-400-normal.woff',118)
sc={k:Image.open(f'm2/out_{k}.jpg').convert('RGB') for k in ['tq','open','hands']}
# vertical fade mask for the photo band
PH=1400
fy=np.ones(PH,np.float32); e=140
fy[:e]=np.linspace(0,1,e); fy[-e:]=np.linspace(1,0,e)
FADE=Image.fromarray((np.tile(fy[:,None],(1,W))*255).astype(np.uint8))
def shot(img,cx,cy,cw,alpha=1.0):
    ch=cw*PH/W
    box=(int(cx-cw/2),int(cy-ch/2),int(cx+cw/2),int(cy+ch/2))
    crop=img.crop(box).resize((W,PH),Image.LANCZOS)
    fr=Image.new('RGB',(W,H),(0,0,0))
    m=FADE if alpha>=1 else FADE.point(lambda v:int(v*alpha))
    fr.paste(crop,(0,110),m); return fr
def caption(fr,lines,shown,y0=1560):
    d=ImageDraw.Draw(fr); k=0
    for i,line in enumerate(lines):
        vis=[]
        for w in line.split(' '):
            if k<shown: vis.append(w)
            k+=1
        bb=d.textbbox((0,0),line,font=font); x0=(W-(bb[2]-bb[0]))//2
        if vis: d.text((x0,y0+i*132),' '.join(vis),font=font,fill=(255,255,255))
def wa(f,s,st): return 0 if f<s else 1+(f-s)//st
def ease(t): return t*t*(3-2*t)
p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','30','-i','-','-i','ad/cal_audio.m4a','-map','0:v','-map','1:a','-c:v','libx264','-preset','veryfast','-crf','17','-pix_fmt','yuv420p','-c:a','copy','-shortest','-movflags','+faststart','ad/SC_journal_preorder_v2.mp4'],stdin=subprocess.PIPE)
keep=[]
for f in range(240):
    if f>=159: fr=Image.open(f'ad/endf/e_{f-158:03d}.png').convert('RGB')
    elif f<44:
        t=ease(f/44); fr=shot(sc['tq'],1060,930,1500-260*t)
        caption(fr,['52 WEEKS','OF MISSIONS.'],wa(f,6,8))
    elif f<108:
        g=f-44; t=ease(g/64); fr=shot(sc['open'],760+620*t,960,1180)
        if g<6: fr=Image.blend(shot(sc['tq'],1060,930,1240),fr,g/6)
        caption(fr,['A MISSION','EVERY DAY.'],wa(g,4,9))
    else:
        g=f-108; t=ease(min(g/42,1)); a=1.0 if f<150 else max(0,1-(f-149)/9)
        fr=shot(sc['hands'],1230,900,1560-220*t,alpha=a)
        if g<6: fr=Image.blend(shot(sc['open'],1380,960,1180),fr,g/6)
        if f<150: caption(fr,['PRE-ORDER','NOW.'],wa(g,4,9))
    if f in (2,30,60,100,130,148,200): keep.append(fr.copy())
    p.stdin.write(fr.tobytes())
p.stdin.close(); p.wait()
S=Image.new('RGB',(270*len(keep),480))
for i,im in enumerate(keep): S.paste(im.resize((270,480)),(i*270,0))
S.save('ad/adsheet2.jpg')
