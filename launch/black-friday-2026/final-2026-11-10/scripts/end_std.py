import numpy as np,subprocess
from PIL import Image,ImageFilter
src=open('/home/claude/pn/lay11.py').read(); exec(src[:src.index('def make')])
def el(fn):
    out=[]
    for bgc in [(0,0,0),(255,255,255)]:
        o=Image.new('RGBA',(W,H),bgc+(255,)); fn(o); out.append(np.array(o.convert('RGB')).astype(float))
    B,Wt=out; A=np.clip(1-(Wt-B).mean(axis=2)/255,0,1)
    C=np.where(A[...,None]>0.02,B/np.maximum(A[...,None],0.02),0).clip(0,255)
    return A,C
def mk(top,tag,hl):
    return [
     (el(lambda o:slot(o,top,1062,1182,800,120,(230,30,30),(255,255,255),6)),0.95),
     (el(lambda o:slot(o,tag,1196,1270,800,74,(255,255,255),hl=hl)),1.15),
     (el(lambda o:slot(o,'MEET THE GANG. FIND THE FULL STORY AT',1400,1446,800,46,(255,255,255))),1.35),
     (el(lambda o:slot(o,'stiffcompetition.shop',1458,1540,820,82,(255,255,255),(15,15,25),4,glow=True)),1.5)]
E=mk('BLACK FRIDAY','10% OFF ALL MERCH','10% OFF')
bgA=np.array(bg().convert('RGB')).astype(float)
lgl=Image.new('RGBA',(W,H),(0,0,0,0)); lgl.alpha_composite(lg,(45,260))
la=np.array(lgl)[...,3]/255.; lrgb=np.array(lgl)[...,:3].astype(float)
logo=lrgb*la[...,None]
sil=Image.fromarray((la*255).astype('uint8'))
halo=np.array(sil.filter(ImageFilter.GaussianBlur(16))).astype(float)/255*1.6; halo=np.clip(halo,0,1)
def blur(A): return np.clip(np.array(Image.fromarray((A*255).astype('uint8')).filter(ImageFilter.GaussianBlur(10))).astype(float)/255*1.6,0,1)
E=[(A,C,blur(A),s) for (A,C),s in E]
p=subprocess.Popen(['ffmpeg','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','30','-i','-','-c:v','libx264','-crf','14','-preset','veryfast','-pix_fmt','yuv420p','end_std.mp4'],stdin=subprocess.PIPE)
for i in range(74):
    t=i/30
    if t<0.5: fr=np.zeros((H,W,3))
    else:
        q=min(1,(t-0.5)/0.4)
        fr=(bgA+logo*1.0*(1-0)) *q
        fr=bgA*q+ (logo+bgA*(1-la[...,None])*0)*q
        fr=bgA*q*(1-la[...,None])+logo*q
        fr=fr+ (1-q)*255*(la+halo*0.9).clip(0,1)[...,None]
        for A,C,H_,s in E:
            e=min(1,max(0,(t-s)/0.35))
            if e<=0: continue
            a=(A*e)[...,None]
            fr=fr*(1-a)+C*a
            fr=fr+255*H_[...,None]*(1-e)*0.9*(e>0)
    p.stdin.write(np.clip(fr,0,255).astype(np.uint8).tobytes())
p.stdin.close(); p.wait()
