import sys,subprocess,numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES=True
W,H=1080,1920;FPS=30;DUR=2.46;N=int(round(DUR*FPS))
FB="/usr/share/fonts/opentype/inter/Inter-Black.otf"
def F(s):return ImageFont.truetype(FB,s)
logo=Image.open('chrome_full_1200.png').convert('RGBA');logo=logo.crop(logo.getbbox())
def lg(w):return logo.resize((w,int(w*logo.height/logo.width)),Image.LANCZOS)
def ease(x):x=min(max(x,0),1);return 1-(1-x)**3
def txt(im,t,cy,maxw,size,fill,stroke,sw,alpha=1,scale=1):
    s=size
    d=ImageDraw.Draw(im)
    while d.textlength(t,font=F(s))>maxw:s-=4
    s=int(s*scale);fo=F(max(s,4))
    L=Image.new('RGBA',(W,300+s),(0,0,0,0));dl=ImageDraw.Draw(L)
    w=dl.textlength(t,font=fo)
    dl.text(((W-w)/2,100),t,font=fo,fill=fill,stroke_width=sw,stroke_fill=stroke)
    if alpha<1:
        a=np.array(L);a[...,3]=(a[...,3]*alpha).astype(np.uint8);L=Image.fromarray(a)
    im.alpha_composite(L,(0,int(cy-100-s/2)))
def put(im,img,cx,cy,alpha=1):
    if alpha<1:
        a=np.array(img);a[...,3]=(a[...,3]*alpha).astype(np.uint8);img=Image.fromarray(a)
    im.alpha_composite(img,(int(cx-img.width/2),int(cy-img.height/2)))
RED=(235,30,30,255);WHITE=(255,255,255,255);GOLD=(255,196,90,255);BLK=(0,0,0,255)
def frame(style,k):
    t=k/FPS;im=Image.new('RGBA',(W,H),(0,0,0,255));T=0.46
    LY=720
    if style=='A':
        if t>=T:
            u=(t-T)/0.9;halo=max(0,1-u)
            L=lg(960);put(im,L,W/2,LY)
            if halo>0:
                g=Image.new('RGBA',L.size,(255,255,255,0));m=np.array(L)[...,3]
                gl=Image.fromarray(np.dstack([np.full_like(m,255)]*3+[m]))
                big=Image.new('RGBA',(L.width+240,L.height+240),(0,0,0,0));big.paste(gl,(120,120),gl)
                big=big.filter(ImageFilter.GaussianBlur(45))
                a=np.array(big);a[...,3]=np.clip(a[...,3]*1.6*halo,0,255).astype(np.uint8)
                put(im,Image.fromarray(a),W/2,LY)
                # brightness lift
                w=Image.new('RGBA',L.size,(255,255,255,0));wa=np.array(L)[...,3]*0.8*halo
                put(im,Image.fromarray(np.dstack([np.full_like(m,255)]*3+[wa.astype(np.uint8)])),W/2,LY)
            txt(im,"BLACK FRIDAY",400,960,150,RED,WHITE,8,alpha=ease((t-T)/0.25))
            txt(im,"SHOP AT stiffcompetition.shop",1010,960,76,WHITE,BLK,5,alpha=ease((t-T-0.7)/0.35))
    if style=='B':
        if t>=T:
            u=(t-T);sc=1+2*(1-ease(u/0.18));sh=int(18*max(0,1-u/0.45)*np.sin(u*90))
            L=lg(int(960*sc));put(im,L,W/2+sh,LY+70+sh//2)
            if u<0.1:
                im=Image.alpha_composite(im,Image.new('RGBA',(W,H),(255,255,255,int(200*(1-u/0.1)))))
            txt(im,"BLACK FRIDAY",300,960,150,RED,WHITE,8,alpha=ease(u/0.2),scale=1+0.25*(1-ease(u/0.3)))
            txt(im,"10% OFF MERCH",450,960,100,GOLD,BLK,6,alpha=ease((u-0.15)/0.2))
            txt(im,"27 - 30 NOV",1085,900,80,WHITE,BLK,5,alpha=ease((u-0.4)/0.3))
            txt(im,"SHOP AT stiffcompetition.shop",1190,1000,58,GOLD,BLK,4,alpha=ease((u-0.7)/0.35))
    if style=='C':
        if t>=T:
            u=t-T;sc=1+0.9*(1-ease(u/0.15))
            txt(im,"BLACK",470,900,330,WHITE,RED,14,alpha=ease(u/0.1),scale=sc)
            txt(im,"FRIDAY",780,900,330,RED,WHITE,10,alpha=ease((u-0.18)/0.1),scale=1+0.9*(1-ease((u-0.18)/0.15)))
        if t>=T+1.0:
            u=t-T-1.0;sc=1+2*(1-ease(u/0.16));sh=int(16*max(0,1-u/0.4)*np.sin(u*90))
            im=Image.new('RGBA',(W,H),(0,0,0,255))
            txt(im,"BLACK FRIDAY",400,960,150,RED,WHITE,8)
            put(im,lg(int(960*sc)),W/2+sh,LY+sh//2)
            if u<0.1:
                im=Image.alpha_composite(im,Image.new('RGBA',(W,H),(255,255,255,int(200*(1-u/0.1)))))
            txt(im,"SHOP AT stiffcompetition.shop",1010,960,76,WHITE,BLK,5,alpha=ease((u-0.2)/0.3))
    return im.convert('RGB')
def sfx(style):
    sr=44100;n=int(13.49*sr);y=np.zeros(n)
    hits=[11.49] if style!='C' else [11.49,12.49]
    for h in hits:
        t=np.arange(int(.35*sr))/sr;f=120*np.exp(-t*7)+35
        s=np.sin(2*np.pi*np.cumsum(f)/sr)*np.exp(-t*9)*0.8
        i=int(h*sr);y[i:i+len(s)]+=s
    import wave
    w=wave.open(f'sfx_end{style}.wav','wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr)
    w.writeframes((np.clip(y,-1,1)*32767).astype(np.int16).tobytes());w.close()
for style in sys.argv[1:]:
    p=subprocess.Popen(f"ffmpeg -y -loglevel error -f rawvideo -pix_fmt rgb24 -s {W}x{H} -r {FPS} -i - -c:v libx264 -crf 18 -pix_fmt yuv420p end{style}.mp4",shell=True,stdin=subprocess.PIPE)
    for k in range(N):p.stdin.write(frame(style,k).tobytes())
    p.stdin.close();p.wait();sfx(style)
    for tt in (0.3,0.5,0.9,1.5,2.4):
        frame(style,int(tt*FPS)).save(f'e{style}_{tt}.png')
