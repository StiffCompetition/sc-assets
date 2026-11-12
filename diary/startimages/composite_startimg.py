import numpy as np,cv2
from PIL import Image
room=cv2.cvtColor(cv2.imread('room.png'),cv2.COLOR_BGR2RGB).astype(np.float32)
cut=np.array(Image.open('MW_cut.png')).astype(np.float32)
k=0.565
nw,nh=int(2160*k),int(3870*k)
c=cv2.resize(cut,(nw,nh),interpolation=cv2.INTER_AREA)
ox=int(540-1110*k+8); oy=int(269-642*k)
H,W=room.shape[:2]
F=np.zeros((H,W,4),np.float32)
sx0,sy0=max(0,-ox),max(0,-oy)
x0,y0=max(0,ox),max(0,oy)
w=min(W-x0,nw-sx0);h=min(H-y0,nh-sy0)
F[y0:y0+h,x0:x0+w]=c[sy0:sy0+h,sx0:sx0+w]
a=F[:,:,3:4]/255.;fg=F[:,:,:3]
# colour match (partial) in LAB toward room wall mean
lab=cv2.cvtColor(np.clip(fg,0,255).astype(np.uint8),cv2.COLOR_RGB2LAB).astype(np.float32)
rl=cv2.cvtColor(room.astype(np.uint8),cv2.COLOR_RGB2LAB).astype(np.float32)
wall=rl[300:550,100:900].reshape(-1,3).mean(0)
m=a[:,:,0]>0.9
fm=lab[m].mean(0)
lab[:,:,1]+=(wall[1]-128)*0.12; lab[:,:,2]+=(wall[2]-128)*0.18
lab[:,:,0]*=0.97
fg=cv2.cvtColor(np.clip(lab,0,255).astype(np.uint8),cv2.COLOR_LAB2RGB).astype(np.float32)
# directional light: window from right -> brighter right, darker left
xs=np.linspace(0,1,W)[None,:,None]
fg=fg*(0.90+0.16*xs)
# warm tint
fg=fg*np.array([1.03,1.0,0.96])
# light wrap: room colour bleeds on edges
edge=cv2.GaussianBlur(a[:,:,0],(0,0),6)
inner=cv2.erode((a[:,:,0]>0.5).astype(np.uint8),np.ones((3,3)),iterations=6).astype(np.float32)
rim=np.clip(a[:,:,0]-cv2.GaussianBlur(inner,(0,0),5),0,1)[:,:,None]
fg=fg*(1-0.25*rim)+room*0.25*rim
# cast shadow on wall, light from right -> shadow falls left/down
sh=cv2.GaussianBlur(a[:,:,0],(0,0),28)
M=np.float32([[1,0,-55],[0,1,30]])
sh=cv2.warpAffine(sh,M,(W,H))
sh2=cv2.GaussianBlur(a[:,:,0],(0,0),6);sh2=cv2.warpAffine(sh2,np.float32([[1,0,-12],[0,1,8]]),(W,H))
shadow=np.clip(0.40*sh+0.22*sh2,0,0.55)[:,:,None]
base=room*(1-shadow*np.array([0.9,1.0,1.0]))
out=base*(1-a)+fg*a
# grain match
rng=np.random.default_rng(1)
out=out+rng.normal(0,1.6,out.shape)*a
cv2.imwrite('MW_start_comp2.png',cv2.cvtColor(np.clip(out,0,255).astype(np.uint8),cv2.COLOR_RGB2BGR))
