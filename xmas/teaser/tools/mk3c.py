import numpy as np, wave
sr=44100; T=12.4; n=int(sr*T); t=np.arange(n)/sr; C=8.0
rng=np.random.default_rng(5)
def env(a,b): return np.clip((t-a)/(b-a),0,1)
def lp(x,k): return np.convolve(x,np.ones(k)/k,mode='same')
gate=lp(np.where(t<C,1.0,0.0),300)
def thump(x,at,f,amp,d):
    i=int(at*sr); L=int(0.8*sr); x[i:i+L]+=np.sin(2*np.pi*f*np.arange(L)/sr)*np.exp(-np.arange(L)/sr*d)*amp
notes=[(0.8,440),(1.9,523.3),(3.0,659.3),(4.1,587.3),(5.2,523.3),(6.3,493.9),(7.2,440)]
p=np.zeros(n)
for s,f in notes:
    i=int(s*sr); L=min(int(2.4*sr),n-i); tau=np.arange(L)/sr
    p[i:i+L]+=(np.sin(2*np.pi*f*tau)+0.5*np.sin(2*np.pi*2*f*tau)+0.25*np.sin(2*np.pi*3*f*tau))*np.exp(-tau*2.0)*(0.35+0.4*s/C)
sb=np.zeros(n)
for s in np.arange(0.4,C,0.19):
    i=int(s*sr); L=int(0.12*sr)
    sb[i:i+L]+=(rng.standard_normal(L)-lp(rng.standard_normal(L),6))*np.exp(-np.arange(L)/sr*35)*rng.uniform(0.3,1)*(0.15+0.85*env(0,C)[i])
pad=(np.sin(2*np.pi*55*t)+0.5*np.sin(2*np.pi*82.4*t))*0.35*env(0,C)
# rooftop wind under whole piece, rising, and lingering as the 'shhh' after the cut
w=lp(rng.standard_normal(n),12)-lp(rng.standard_normal(n),80)
wind=w*(0.10+0.25*env(0,C)+0.25*env(C,C+0.4)*(1-env(C+1.5,T)))*(1-0.0)
music=(p+sb*0.5+pad)*gate
thump(music,C,40,1.0,5)
x=music+wind*0.9
x=x/np.max(np.abs(x))*0.85
x*= (1-env(T-1.2,T))
w_=wave.open('3c.wav','wb'); w_.setnchannels(1); w_.setsampwidth(2); w_.setframerate(sr); w_.writeframes((x*32767).astype(np.int16).tobytes()); w_.close()
