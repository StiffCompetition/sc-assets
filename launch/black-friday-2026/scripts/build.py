from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES=True
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import subprocess
F="/usr/share/fonts/opentype/inter/Inter-Black.otf"
RED=(232,38,43); WHITE=(255,255,255); BLUE=(47,109,181)
W,H=1080,1920
def font(sz): return ImageFont.truetype(F,sz)
def fit(draw,text,maxw,start):
    s=start
    while draw.textlength(text,font=font(s))>maxw: s-=4
    return s
def centered(img,text,y,maxw,start,fill,stroke,sw):
    d=ImageDraw.Draw(img); s=fit(d,text,maxw,start); f=font(s)
    w=d.textlength(text,font=f)
    d.text(((W-w)/2,y),text,font=f,fill=fill,stroke_width=sw,stroke_fill=stroke)
    return s
logo=Image.open('logo_cut.png')
def paste_logo(img,h,y):
    l=logo.resize((int(logo.width*h/logo.height),h),Image.LANCZOS)
    img.alpha_composite(l,((W-l.width)//2,y))

def top_text():
    im=Image.new('RGBA',(W,H),(0,0,0,0))
    centered(im,"BLACK FRIDAY",290,980,150,WHITE,(0,0,0),6)
    centered(im,"10% OFF ALL MERCH",450,980,86,RED,WHITE,5)
    return im
def gradient():
    g=Image.new('RGBA',(W,H),(0,0,0,0)); px=g.load()
    for y in range(430,670):
        a=int(255*(1-(y-430)/240))
        for x in range(W): px[x,y]=(0,0,0,a)
    return g

def endcard(prod,kind,status):
    p=Image.open(prod).convert('RGB')
    bg=p.copy(); bg=bg.resize((W,H*W//W) if False else (int(bg.width*H/bg.height),H)); 
    l=(bg.width-W)//2; bg=bg.crop((l,0,l+W,H)).filter(ImageFilter.GaussianBlur(40))
    bg=ImageEnhance.Brightness(bg).enhance(0.35)
    im=bg.convert('RGBA')
    if kind=='mug':
        pp=p.resize((W,W),Image.LANCZOS); im.alpha_composite(pp.convert('RGBA'),(0,H-W))
    else:
        crop=p.crop((0,800,p.width,p.height)); s=W/crop.width
        pp=crop.resize((W,int(crop.height*s)),Image.LANCZOS); im.alpha_composite(pp.convert('RGBA'),(0,H-pp.height))
    paste_logo(im,200,290)
    centered(im,"10% OFF",520,980,230,RED,WHITE,8)
    centered(im,status,770,980,72,WHITE,(0,0,0),5)
    return im.convert('RGB')

clips=[("mw","mw_mug.jpg","mug","STARTS FRIDAY 27 NOV"),
       ("sw","sw_tee.jpg","tee","LIVE NOW · 27–30 NOV"),
       ("hh","hh_tee.jpg","tee","STILL ON · ENDS MON 30 NOV"),
       ("po","ra_mug.jpg","mug","LAST CALL · ENDS TONIGHT")]
top_text().save('build/top.png'); gradient().save('build/grad.png')
for n,prod,kind,status in clips:
    endcard(prod,kind,status).save(f'build/end_{n}.png')
    cmd=["ffmpeg","-loglevel","error","-y",
      "-f","lavfi","-i",f"color=c=black:s={W}x{H}:r=30:d=5.04",
      "-i",f"{n}.mp4","-loop","1","-t","5.04","-i","build/grad.png","-loop","1","-t","5.04","-i","build/top.png",
      "-loop","1","-t","3.5","-i",f"build/end_{n}.png",
      "-filter_complex",
      f"[1:v]scale=-2:1881,crop=1080:1881,setsar=1,fps=30[p];"
      f"[0:v][p]overlay=0:430:shortest=1[a];[a][2:v]overlay=0:0:format=auto[b];"
      f"[3:v]format=rgba,fade=t=in:st=0.2:d=0.3:alpha=1[t];[b][t]overlay=0:0:format=auto[c];"
      f"[4:v]format=yuv420p,fps=30,setsar=1[e];[c]format=yuv420p[c2];"
      f"[c2][e]xfade=transition=fade:duration=0.4:offset=4.6[v]",
      "-map","[v]","-c:v","libx264","-preset","veryfast","-crf","18","-pix_fmt","yuv420p",f"build/BF_{n}.mp4"]
    subprocess.run(cmd,check=True)
for n,*_ in clips:
    subprocess.run(["ffmpeg","-loglevel","error","-y","-i",f"build/BF_{n}.mp4","-vf","select='eq(n,20)+eq(n,120)+eq(n,170)+eq(n,200)',scale=270:-1,tile=4x1","-frames:v","1",f"build/chk_{n}.png"])
