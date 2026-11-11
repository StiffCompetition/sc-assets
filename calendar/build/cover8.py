import sys
from PIL import Image, ImageFilter
src,out,W,H=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4])
SH=round(10*300/25.4); F=0.975
S=Image.open(src).convert('RGB')
k=max(W/S.width,H/S.height)*F
B=S.resize((round(S.width*k),round(S.height*k)),Image.LANCZOS)
xo=(B.width-W)//2
img=B.crop((xo,0,xo+W,B.height))
c=Image.new('RGB',(W,H))
c.paste(img.crop((0,0,W,SH)).transpose(Image.FLIP_TOP_BOTTOM),(0,0))
c.paste(img,(0,SH))
end=SH+img.height
if end<H:
    gap=H-end; c.paste(img.crop((0,img.height-gap,W,img.height)).transpose(Image.FLIP_TOP_BOTTOM),(0,end))
elif end>H:
    c=c.crop((0,0,W,H))
for y in (SH,end):
    if 0<y<H: c.paste(c.crop((0,y-30,W,y+30)).filter(ImageFilter.GaussianBlur(6)),(0,y-30))
c.save(out,quality=97,dpi=(300,300)); print(out,c.size,'img h',img.height,'end',end)
