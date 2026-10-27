import sys, numpy as np, onnxruntime as ort, time
from PIL import Image
src=Image.open(sys.argv[1]).convert('RGB'); out_path=sys.argv[2]
sess=ort.InferenceSession('models/realesrgan_x4plus.onnx',providers=['CPUExecutionProvider'])
x=np.asarray(src).astype(np.float32).transpose(2,0,1)[None]/255
H,W=x.shape[2:]; T=192; P=12; out=np.zeros((3,H*4,W*4),np.float32)
tiles=[(y,xx) for y in range(0,H,T) for xx in range(0,W,T)]; t0=time.time()
for i,(y,xx) in enumerate(tiles):
    y0,x0=max(0,y-P),max(0,xx-P); y1,x1=min(H,y+T+P),min(W,xx+T+P)
    o=sess.run(None,{'input':x[:,:,y0:y1,x0:x1]})[0][0]
    oy,ox=(y-y0)*4,(xx-x0)*4; h,w=min(T,H-y)*4,min(T,W-xx)*4
    out[:,y*4:y*4+h,xx*4:xx*4+w]=o[:,oy:oy+h,ox:ox+w]
    print(f'{i+1}/{len(tiles)} {time.time()-t0:.0f}s',flush=True)
up=Image.fromarray((np.clip(out,0,1).transpose(1,2,0)*255).round().astype(np.uint8)); up.save(out_path)
back=np.asarray(up.resize(src.size,Image.LANCZOS)).astype(float); orig=np.asarray(src).astype(float)
mse=((back-orig)**2).mean(); print('likeness PSNR dB',round(10*np.log10(255**2/mse),1))
