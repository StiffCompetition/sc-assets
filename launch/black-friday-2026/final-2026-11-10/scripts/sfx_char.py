import numpy as np
from scipy.io import wavfile
from scipy.signal import butter,lfilter
sr=44100; T=13.5; out=np.zeros(int(T*sr)); rng=np.random.default_rng(3)
def thump(t0,amp=1.0,f0=130,f1=48,dur=0.28):
    n=int(dur*sr); t=np.arange(n)/sr; fr=f1+(f0-f1)*np.exp(-t*18); ph=2*np.pi*np.cumsum(fr)/sr
    s=np.sin(ph)*np.exp(-t*11); c=rng.standard_normal(n)*np.exp(-t*90)*0.5
    s=amp*(s+c); i=int(t0*sr); out[i:i+n]+=s[:len(out)-i]
def whoosh(t0,dur=0.45,amp=0.5):
    n=int(dur*sr); t=np.arange(n)/sr; x=rng.standard_normal(n); k=np.exp(-((t-dur*0.55)/(dur*0.28))**2)
    b,a=butter(2,[400/(sr/2),4000/(sr/2)],'band'); x=lfilter(b,a,x)*k*amp
    i=int(t0*sr); out[i:i+n]+=x[:len(out)-i]
for t0,a in [(5.49,1.0),(5.84,0.6),(6.44,0.7),(8.9,0.9)]: thump(t0,a)
whoosh(5.2,amp=0.4); whoosh(8.2)
out=np.tanh(out*0.9)*0.8
wavfile.write('char_sfx.wav',sr,(out*32767).astype(np.int16))
