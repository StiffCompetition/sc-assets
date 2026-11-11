import sys,cv2,numpy as np
gen=cv2.imread(sys.argv[1]);crop=cv2.imread(sys.argv[2]);out=sys.argv[3]
H,W=gen.shape[:2]
g=cv2.cvtColor(gen,cv2.COLOR_BGR2GRAY);c=cv2.cvtColor(crop,cv2.COLOR_BGR2GRAY)
s=cv2.SIFT_create(4000);k1,d1=s.detectAndCompute(c,None);k2,d2=s.detectAndCompute(g,None)
m=[a for a,b in cv2.BFMatcher().knnMatch(d1,d2,k=2) if a.distance<0.7*b.distance]
src=np.float32([k1[x.queryIdx].pt for x in m]);dst=np.float32([k2[x.trainIdx].pt for x in m])
Hm,inl=cv2.findHomography(src,dst,cv2.RANSAC,4);print(len(m),int(inl.sum()))
warp=cv2.warpPerspective(crop,Hm,(W,H),borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0))
cov=cv2.warpPerspective(np.full(crop.shape[:2],255,np.uint8),Hm,(W,H))>0
d=cv2.absdiff(cv2.GaussianBlur(gen,(0,0),3),cv2.GaussianBlur(warp,(0,0),3)).max(axis=2)
mk=((d>30)&cov).astype(np.uint8)*255
mk=cv2.morphologyEx(mk,cv2.MORPH_CLOSE,np.ones((21,21),np.uint8))
n,lab,st,_=cv2.connectedComponentsWithStats(mk)
big=1+np.argmax(st[1:,4]);mk=((lab==big)*255).astype(np.uint8)
ff=mk.copy();h2=np.zeros((H+2,W+2),np.uint8);cv2.floodFill(ff,h2,(0,0),255);mk=mk|cv2.bitwise_not(ff)
mk=cv2.dilate(mk,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(17,17)))
a=cv2.GaussianBlur(mk,(0,0),4).astype(np.float32)/255
a=np.where(cov,a,1.0)[...,None]
res=(gen*a+warp*(1-a)).astype(np.uint8);cv2.imwrite(out,res)
