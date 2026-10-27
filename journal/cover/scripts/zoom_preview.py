# preview of zoomed back-cover head panels (same shape as the back panels)
from PIL import Image, ImageDraw, ImageFont
src=open('scripts/prep_panels.py').read(); exec(src[src.index('def popbg'):src.index('FACES=')])
AR=1.95
Z={'MW':('refs/MW_hs_src.png',(255,214,0),0.27,0.725),'RA':('refs/RA_hs.png',(255,214,0),0.20,0.775)}
def zoom(f,c,y0,y1):
    im=Image.open(f).convert('RGBA'); im=im.crop(im.getchannel('A').getbbox()); w,h=im.size
    im=im.crop((0,int(h*y0),w,int(h*y1))); H=im.height; Wc=int(H*AR)
    bg=popbg((max(Wc,w),H),c); bg.paste(im,((bg.width-w)//2,0),im)
    x0=(bg.width-Wc)//2; return bg.crop((x0,0,x0+Wc,H)).resize((700,int(700/AR)),Image.LANCZOS)
F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',26) if __import__('os').path.exists('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf') else ImageFont.load_default()
sheet=Image.new('RGB',(1460,2*(int(700/AR)+60)+20),'white'); d=ImageDraw.Draw(sheet)
for i,(k,(f,c,y0,y1)) in enumerate(Z.items()):
    now=Image.open(f'refs/up_{k}_hsw.png').convert('RGB'); nh=int(now.width/AR); now=now.crop((0,(now.height-nh)//2,now.width,(now.height-nh)//2+nh)).resize((700,int(700/AR)))
    y=i*(int(700/AR)+60)+10
    d.text((10,y),f'{"Major Wood" if k=="MW" else "Rear Admiral"}  -  now',fill='black',font=F); sheet.paste(now,(10,y+40))
    d.text((750,y),'zoomed',fill='black',font=F); sheet.paste(zoom(f,c,y0,y1),(750,y+40))
sheet.save('cover/Back head zoom preview.jpg',quality=92)
