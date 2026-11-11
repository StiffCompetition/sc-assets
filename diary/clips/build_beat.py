import subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont
import build_hanky9 as b
W,H,FPS=1080,1920,30
SS,DUR=0.15,4.2
raw=subprocess.run(['ffmpeg','-v','error','-ss',str(SS),'-t',str(DUR),'-i','beat/beat1080.mp4','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout
fr=np.frombuffer(raw,dtype=np.uint8).reshape(-1,H,W,3); N=len(fr); print(N)
def red(d,txt,cy,s,a):
    f=ImageFont.truetype(b.BF,s)
    d.text((540,cy),txt,font=f,fill=(209,43,29,int(255*a)),stroke_width=4,stroke_fill=(255,255,255,int(255*a)),anchor='mm')
def cap(t):
    im=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    a=lambda st:min(1,max(0,(t-st)/0.2))
    red(d,"WHAT'S SHRUNK",1150,150,a(0.7)); red(d,"ON YOU?",1290,170,a(1.0))
    f=ImageFont.truetype(b.BF,70)
    d.text((540,1410),"COMMENT BELOW. HANKY'S READING.",font=f,fill=(255,255,255,int(255*a(1.7))),stroke_width=3,stroke_fill=(0,0,0,int(255*a(1.7))),anchor='mm')
    return im
p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','30','-i','-','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','hk9_segBeat.mp4'],stdin=subprocess.PIPE)
for i in range(N):
    t=i/FPS
    im=Image.fromarray(fr[i]).convert('RGBA'); im.alpha_composite(cap(t)); im=b.wm(im)
    k=min(1,t/0.35)*min(1,(DUR-t)/0.35)
    if k<1: im=Image.blend(Image.new('RGB',(W,H),(0,0,0)),im,max(0,k))
    p.stdin.write(im.tobytes())
p.stdin.close();p.wait()
Image.fromarray(fr[int(2.6*30)]).convert('RGBA'); 
