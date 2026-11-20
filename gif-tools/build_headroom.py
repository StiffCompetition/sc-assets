import sys,subprocess,os
sys.path.insert(0,'/home/claude/sc-assets/gif-tools')
import sc_gif
from PIL import Image
def build(clip,name,text,hit,end=None,pad=None):
    # sample backdrop colour from frame 0 corner, pad top (headroom) and sides to a square so the caption sits above the head
    subprocess.run(['ffmpeg','-v','error','-y','-i',clip,'-frames:v','1','f0.png'],check=True)
    im=Image.open('f0.png').convert('RGB'); w,h=im.size
    px=[im.getpixel((x,y)) for x in (4,w-5) for y in (4,10)]
    c=tuple(sum(p[i] for p in px)//len(px) for i in range(3)); hexc='%02x%02x%02x'%c
    P=pad or 70; S=h+P
    subprocess.run(['ffmpeg','-v','error','-y','-i',clip,'-vf',f'pad={S}:{S}:{(S-w)//2}:{P}:color=0x{hexc},fillborders=left={(S-w)//2}:right={S-w-(S-w)//2}:top={P}:bottom=0:mode=smear','-an','padded.mp4'],check=True)
    return sc_gif.make('padded.mp4',name,text,hit,None,0.0,end,0.8,12,30)
if __name__=='__main__':
    a=sys.argv; print(build(a[1],a[2],a[3],float(a[4]),float(a[5]) if len(a)>5 and a[5]!='-' else None,int(a[6]) if len(a)>6 else None))
