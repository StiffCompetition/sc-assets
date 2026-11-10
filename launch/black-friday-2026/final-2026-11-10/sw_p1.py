import subprocess,numpy as np
from PIL import Image
W,H=1080,1920; FPS=30; N=151
fr=Image.open('sw_still.png').convert('RGB'); wm=Image.open('wm_new.png').convert('RGBA')
def eio(x): x=min(max(x,0),1); return x*x*(3-2*x)
p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','30','-i','-','-c:v','libx264','-crf','16','-pix_fmt','yuv420p','sw_p1.mp4'],stdin=subprocess.PIPE)
for i in range(N):
    u=eio(i/(N-1)); s=(0.84+(0.93-0.84)*u)*W/fr.width
    w=int(fr.width*s); h=int(fr.height*s)
    im=fr.resize((w,h),Image.LANCZOS).convert('RGBA')
    a=np.ones((h,w)); fs=12
    yy=np.arange(h)[:,None]; xx=np.arange(w)[None,:]
    a=np.clip(np.minimum(np.minimum(xx,w-1-xx),np.minimum(yy,h-1-yy))/fs,0,1)
    arr=np.array(im); L=(arr[...,0]*.299+arr[...,1]*.587+arr[...,2]*.114); ed=np.minimum(np.minimum(np.arange(arr.shape[1])[None,:],arr.shape[1]-1-np.arange(arr.shape[1])[None,:]),np.arange(arr.shape[0])[:,None]); wgt=np.clip(ed/(0.17*arr.shape[1]),0,1); a=a*(np.clip((L-34)/30,0,1)*(1-wgt)+wgt); arr[...,3]=(a*255).astype(np.uint8)
    o=Image.new('RGBA',(W,H),(0,0,0,255)); o.alpha_composite(Image.fromarray(arr,'RGBA'),((W-w)//2,(H-h)//2)); o.alpha_composite(wm)
    p.stdin.write(o.convert('RGB').tobytes())
p.stdin.close(); p.wait()
