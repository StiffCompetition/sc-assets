import cv2,numpy as np
front=cv2.imread('mock/front.png'); spine=cv2.imread('mock/spine.png')
def order(q):
    q=np.array(q,np.float32); s=q.sum(1); d=np.diff(q,axis=1).ravel()
    return np.array([q[np.argmin(s)],q[np.argmin(d)],q[np.argmax(s)],q[np.argmax(d)]],np.float32)
def put(scene,art,q,skin=False,gain=1.0,ref=None,S=2,flat=0.0,smooth=0,clip=None):
    H,W=scene.shape[:2]
    q=order(q)*S; h,w=art.shape[:2]
    M=cv2.getPerspectiveTransform(np.float32([[0,0],[w,0],[w,h],[0,h]]),q)
    wa=cv2.warpPerspective(art,M,(W*S,H*S),flags=cv2.INTER_AREA).astype(np.float32)
    m=cv2.warpPerspective(np.full((h,w),255,np.uint8),M,(W*S,H*S),flags=cv2.INTER_LINEAR).astype(np.float32)/255
    m=cv2.resize(m,(W,H),interpolation=cv2.INTER_AREA); wa=cv2.resize(wa,(W,H),interpolation=cv2.INTER_AREA)
    g=cv2.cvtColor(scene,cv2.COLOR_BGR2GRAY).astype(np.float32)
    if ref is None: ref=np.percentile(g[m>0.95],90)
    if smooth:
        g=cv2.morphologyEx(g,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(smooth,smooth)))
        w=clip if clip is not None else np.ones_like(g)
        g=cv2.GaussianBlur(g*w,(0,0),4)/np.maximum(cv2.GaussianBlur(w,(0,0),4),1e-3)
    shade=(flat+(1-flat)*np.clip(g/ref,0,1.1))*gain
    out=wa*shade[...,None]
    if skin:
        hsv=cv2.cvtColor(scene,cv2.COLOR_BGR2HSV).astype(np.float32)
        sk=((hsv[...,1]>58)&((hsv[...,0]<28)|(hsv[...,0]>165))).astype(np.uint8)
        sk=cv2.morphologyEx(sk,cv2.MORPH_OPEN,np.ones((5,5),np.uint8)); sk=cv2.morphologyEx(sk,cv2.MORPH_CLOSE,np.ones((15,15),np.uint8))
        cov=1-cv2.GaussianBlur(sk.astype(np.float32),(0,0),1.2)
        m=m*cov
    if clip is not None: m=m*clip
    m=m[...,None]
    return np.clip(scene*(1-m)+out*m,0,255).astype(np.uint8), ref
