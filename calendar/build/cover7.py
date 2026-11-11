import sys
from PIL import Image, ImageFilter
src,out,W,H=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4])
SH=round(10*300/25.4)
S=Image.open(src).convert('RGB')
k=max(W/S.width,H/S.height)
B=S.resize((round(S.width*k),round(S.height*k)),Image.LANCZOS)
xo=(B.width-W)//2
base=B.crop((xo,0,xo+W,H))
top=base.crop((0,0,W,SH)).transpose(Image.FLIP_TOP_BOTTOM)
c=Image.new('RGB',(W,H)); c.paste(top,(0,0)); c.paste(base.crop((0,0,W,H-SH)),(0,SH))
# soften the mirror seam slightly
seam=c.crop((0,SH-30,W,SH+30)).filter(ImageFilter.GaussianBlur(6)); c.paste(seam,(0,SH-30))
c.save(out,quality=97,dpi=(300,300)); print(out,c.size)
