import sys
from PIL import Image
import numpy as np
src,out,W,H,LB=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),float(sys.argv[5])
S=Image.open(src).convert('RGB')
k=max(W/S.width,H/S.height)
nw,nh=round(S.width*k),round(S.height*k)
B=S.resize((nw,nh),Image.LANCZOS)
xo=(nw-W)//2
base=B.crop((xo,0,xo+W,H))
# logo+tagline boost: region of base (orig y 0..430 of 1500 -> scaled)
u=nh/1500.0
ry=int(430*u)
reg=base.crop((0,0,W,ry))
nw2,nh2=int(W*LB),int(ry*LB)
r2=reg.resize((nw2,nh2),Image.LANCZOS)
x2=(nw2-W)//2
top=int(-12*u*0)  # keep top anchored
r2=r2.crop((x2,0,x2+W,nh2))
fade=int(90*u)
m=np.ones((nh2,W))
m[-fade:,:]=np.linspace(1,0,fade)[:,None]
base.paste(r2,(0,0),Image.fromarray((m*255).astype('uint8')))
base.save(out,quality=97,dpi=(300,300)); print(out,base.size,k)
