import numpy as np, subprocess, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H=1080,1920; FPS=30
F='fonts/x/package/files/anton-latin-400-normal.woff'
font=ImageFont.truetype(F,118)
yy,xx=np.mgrid[0:H,0:W]; r=np.sqrt(((xx-W/2)/W)**2+((yy-H*0.42)/H)**2)
t=np.clip(r/0.75,0,1)[...,None]
BG=Image.fromarray(((1-t)*np.array([34,36,41])+t*np.array([8,8,9])).astype(np.uint8))
front=Image.open('mock/front.png').convert('RGB')
pages=[Image.open(f'pages/out/full/colour_p{p:03d}.png').convert('RGB') for p in (40,400,401,402)]
def shadowed(img,w):
    im=img.resize((w,int(img.height*w/img.width)),Image.LANCZOS)
    pad=60; sh=Image.new('L',(im.width+2*pad,im.height+2*pad),0)
    ImageDraw.Draw(sh).rectangle([pad,pad+18,pad+im.width,pad+im.height+18],fill=170)
    return im, sh.filter(ImageFilter.GaussianBlur(26)), pad
def place(canvas,img,w,cy,sx=1.0,alpha=1.0):
    im,sh,pad=shadowed(img,w)
    if sx<0.999:
        nw=max(2,int(im.width*sx)); im=im.resize((nw,im.height)); sh=sh.resize((max(2,int(sh.width*sx)),sh.height))
    x=(W-im.width)//2; y=int(cy-im.height/2)
    black=Image.new('RGB',sh.size,(0,0,0))
    canvas.paste(black,(x-int(pad*sx),y-pad),sh.point(lambda v:int(v*alpha)))
    if alpha<1: canvas.paste(im,(x,y),Image.new('L',im.size,int(255*alpha)))
    else: canvas.paste(im,(x,y))
def caption(canvas,lines,shown,y0=1560):
    d=ImageDraw.Draw(canvas); k=0
    for i,line in enumerate(lines):
        words=line.split(' '); vis=[]
        for w_ in words:
            if k<shown: vis.append(w_)
            k+=1
        full=d.textbbox((0,0),line,font=font); x0=(W-(full[2]-full[0]))//2
        if vis: d.text((x0,y0+i*132),' '.join(vis),font=font,fill=(255,255,255))
frames=[]
def words_at(f,start,step): return 0 if f<start else 1+(f-start)//step
p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i','ad/cal_audio.m4a','-map','0:v','-map','1:a','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-c:a','copy','-shortest','-movflags','+faststart','ad/SC_journal_preorder_v1.mp4'],stdin=subprocess.PIPE)
for f in range(240):
    if f>=159:
        fr=Image.open(f'ad/endf/e_{f-158:03d}.png').convert('RGB')
    else:
        fr=BG.copy()
        if f<42:
            z=1.0+0.04*f/42; place(fr,front,int(720*z),780)
            caption(fr,['52 WEEKS','OF MISSIONS.'],words_at(f,4,8))
        elif f<108:
            g=f-42; i=min(g//16,3); ph=g%16
            sx=1.0
            if ph>=12 and i<3: sx=max(0.02,1-(ph-11)/4)
            if ph<4 and i>0: sx=max(0.02,(ph+1)/4)
            place(fr,pages[i],700,780,sx)
            caption(fr,['A MISSION','EVERY DAY.'],words_at(g,3,9))
        else:
            g=f-108; z=1.0+0.03*g/51
            a=1.0 if f<150 else max(0.0,1-(f-149)/9)
            place(fr,front,int(720*z),780,alpha=a)
            if f<150: caption(fr,['PRE-ORDER','NOW.'],words_at(g,3,9))
        if f in (30,50,66,90,104,140,155): frames.append(fr.copy())
    p.stdin.write(fr.tobytes())
    if f in (200,):frames.append(fr.copy())
p.stdin.close(); p.wait()
S=Image.new('RGB',(270*len(frames),480))
for i,im in enumerate(frames): S.paste(im.resize((270,480)),(i*270,0))
S.save('ad/adsheet.jpg')
