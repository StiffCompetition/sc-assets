exec(open('mock.py').read().split("mug=Image.open")[0])
import subprocess, math
FPS=30
def tl(t,size,fill,stroke=(0,0,0),sw=8):
    d=ImageDraw.Draw(Image.new('RGBA',(10,10)))
    fnt=f(size); w=int(d.textlength(t,font=fnt))+2*sw+10
    im=Image.new('RGBA',(w,size+2*sw+60),(0,0,0,0))
    ImageDraw.Draw(im).text((sw+5,sw),t,font=fnt,fill=fill,stroke_width=sw,stroke_fill=stroke)
    return im.crop(im.getbbox())
A=tl("10% OFF",214,(255,255,255),sw=10)
d0=ImageDraw.Draw(Image.new('RGBA',(10,10)))
B=tl("PRICES DROP.",118,(255,255,255),sw=7)
C=tl("MAJOR WOOD STAYS UP.",74,(255,196,90),sw=5)
print(A.size,B.size,C.size)
YA,YB,YC=60,270,418
def eo3(x): x=min(max(x,0),1); return 1-(1-x)**3
def eob(x,k=1.9):
    x=min(max(x,0),1); return 1+(k+1)*(x-1)**3+k*(x-1)**2
T0=0.0
mug=Image.open('base_mug.png').convert('RGB'); tee=Image.open('base_tee.png').convert('RGB')
def place(im,layer,cx,y,scale=1.0,alpha=1.0):
    if scale!=1.0:
        layer=layer.resize((max(1,int(layer.width*scale)),max(1,int(layer.height*scale))),Image.LANCZOS)
    if alpha<1.0:
        a=layer.getchannel('A').point(lambda v:int(v*alpha)); layer=layer.copy(); layer.putalpha(a)
    im.alpha_composite(layer,(int(cx-layer.width/2),int(y-(layer.height-layer.height/scale)/2*0)))
DUR=6.0
p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','30','-i','-','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','prod.mp4'],stdin=subprocess.PIPE)
for i in range(int(DUR*FPS)):
    t=i/FPS
    # base: mug then crossfade to tee 2.9-3.2
    k=min(max((t-2.9)/0.3,0),1)
    base=Image.blend(mug,tee,k).convert('RGBA')
    # 10% OFF punch at 0.15..0.45
    if t>=0.15:
        u=(t-0.15)/0.3; sc=1+0.7*(1-eob(u,1.2)) if u<1 else 1
        h=A.height*sc; place(base,A,W/2,YA-(h-A.height)/2,sc,alpha=min(1,u*3))
    # PRICES DROP slide 0.65..1.0 then sink
    if t>=0.65:
        u=(t-0.65)/0.35; x=W/2-(1-eo3(u))*1200
        dy=0
        if t>1.0: dy=14*eob((t-1.0)/0.2,2.5)
        place(base,B,x,YB+dy)
    # MAJOR WOOD STAYS UP slide 1.25..1.6 then rise
    if t>=1.25:
        u=(t-1.25)/0.35; x=W/2-(1-eo3(u))*1200
        dy=0
        if t>1.6: dy=-14*eob((t-1.6)/0.2,2.5)
        place(base,C,x,YC+dy)
    p.stdin.write(base.convert('RGB').tobytes())
p.stdin.close(); p.wait(); print('done')
