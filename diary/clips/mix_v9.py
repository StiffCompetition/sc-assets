import numpy as np, subprocess, wave
from scipy.signal import butter, sosfilt, fftconvolve
SR=44100; OFF=5.0; TOT=24.13
rng=np.random.default_rng(11)
def load(p, ss=0, t=None):
    c=['ffmpeg','-v','error','-ss',str(ss)]+(['-t',str(t)] if t else [])+['-i',p,'-ac','1','-ar',str(SR),'-f','f32le','-']
    return np.frombuffer(subprocess.run(c,capture_output=True).stdout,dtype=np.float32).astype(np.float64)
N=int(TOT*SR)
def place(buf,x,t,g=1.0):
    i=int(t*SR); 
    if i<0: x=x[-i:]; i=0
    j=min(N,i+len(x)); 
    if j>i: buf[i:j]+=x[:j-i]*g
def env_fade(x,fi=0,fo=0):
    x=x.copy()
    if fi: n=int(fi*SR); x[:n]*=np.linspace(0,1,n)
    if fo: n=int(fo*SR); x[-n:]*=np.linspace(1,0,n)
    return x
def lp(x,f,o=2): return sosfilt(butter(o,f,'low',fs=SR,output='sos'),x)
def bp(x,a,b): return sosfilt(butter(2,[a,b],'band',fs=SR,output='sos'),x)
def gain_curve(pts):
    t=np.arange(N)/SR; return 10**(np.interp(t,[p[0] for p in pts],[p[1] for p in pts])/20)

# ---- street bed (rain+bus etc), loops, indoor muffle after the dissolve
st=load('walthamstow_12s.mp3'); st=st/np.sqrt((st**2).mean())
bed=np.zeros(N)
for k in range(3): place(bed,env_fade(st,.3,.3) if k else st,k*11.6)
bed_in=bed; bed_mu=lp(bed,1100,3)
t=np.arange(N)/SR; m=np.clip((t-(OFF-1.2))/1.6,0,1)  # muffled as we enter the room
bed=bed_in*(1-m)+bed_mu*m
bed*=gain_curve([(0,-50),(0.8,-30),(3.8,-30),(6.5,-37),(OFF+10.7,-37),(OFF+12.2,-48),(OFF+12.45,-60),(TOT,-60)])
# gain curve is dB re rms 1.0 -> treat as dBFS rms
E0_=OFF+12.45
# ---- theme tune (Lyria), two layers: opening+scene, end-card
import sys
TUNE=sys.argv[1] if len(sys.argv)>1 else 'C'
OFFS={'A':0.0,'B':0.0,'C':0.8}[TUNE]
th=load(f'theme/{TUNE}.wav'); th=th/np.sqrt((th**2).mean())
m1=np.zeros(N); place(m1,env_fade(th[:int(17*SR)],1.0,0.3),OFFS,1.0)
m1*=gain_curve([(0,-24),(OFFS+3.0+(0.8 if TUNE=='C' else 0),-24),(OFF+1.5,-24),(OFF+3.0,-30),(OFF+3.6,-33),(OFF+10.6,-33),(OFF+11.3,-48),(OFF+12.0,-70),(TOT,-70)])
m2=np.zeros(N); place(m2,env_fade(th[int(15*SR):int(15*SR)+int((TOT-E0_)*SR)],0.04,1.0),E0_,1.0)
m2*=gain_curve([(0,-90),(E0_-0.01,-90),(E0_,-22),(E0_+0.6,-22),(E0_+0.75,-31),(E0_+2.8,-31),(E0_+3.3,-22),(TOT,-24)])
mus=m1+m2
# ---- typewriter title keys + bell (from existing pack)
tw='/home/claude/sc-assets/diary/intro/typewriter_keys_then_bell.mp3'
keys=load(tw,0.1,2.35); keys2=load(tw,0.2,0.75); bell=load(tw,3.5,2.2)
sfx=np.zeros(N)
place(sfx,keys,0.4,0.9); place(sfx,keys2,2.55,0.9); place(sfx,bell,3.3,0.8)
# ---- pen scratch
starts=[4.2,4.9,5.41,5.8,6.39,6.66,7.31,7.66,8.23,8.75,9.3]; alloc=[.7,.51,.39,.59,.27,.65,.35,.57,.52,.55,.5]
pen=np.zeros(N)
for s,a in zip(starts,alloc):
    t0=OFF+s; n=int(a*SR); nz=rng.standard_normal(n)
    x=bp(nz,1800,7500)
    e=np.zeros(n); k=0
    while k<n:
        L=int(rng.uniform(.035,.09)*SR); sh=np.hanning(L)*rng.uniform(.5,1); e[k:k+L]=np.maximum(e[k:k+L],sh[:max(0,min(L,n-k))]); k+=int(L*rng.uniform(.55,.9))
    x=x*e*np.hanning(n)**.3
    x+=0.25*lp(rng.standard_normal(n),600)*e   # paper body
    place(pen,x,t0,1.0)
pen=pen/ (np.sqrt((pen[pen!=0]**2).mean())+1e-9)*0.05*0+pen
pr=np.sqrt((pen[int((OFF+4.2)*SR):int((OFF+9.8)*SR)]**2).mean()); pen=pen/pr*10**(-29/20)
# ---- tea cup set on saucer, after last line
def tone(f,d,dec): tt=np.arange(int(d*SR))/SR; return np.sin(2*np.pi*f*tt)*np.exp(-tt/dec)
cl=tone(2870,1.2,.22)+.6*tone(4210,1.2,.16)+.35*tone(5830,1.2,.1)+.4*tone(1930,1.2,.3)
cl[:int(.004*SR)]+=rng.standard_normal(int(.004*SR))*.8
cup=cl/np.abs(cl).max()
thump=lp(rng.standard_normal(int(.12*SR)),220)*np.exp(-np.arange(int(.12*SR))/SR/.03)
fx=np.zeros(N); place(fx,cup,OFF+10.05,10**(-24/20)*3.2); place(fx,thump/np.abs(thump).max(),OFF+10.04,10**(-24/20)*1.2)
place(fx,cup*.6,OFF+10.55,10**(-30/20)*3.2)   # second small clink (spoon)
# ---- end card dings
place(sfx,bell,OFF+12.45+0.12,0.6); place(sfx,bell,OFF+12.45+3.8,0.7)
sfx*=10**(-20/20)/np.sqrt((sfx[sfx!=0]**2).mean())*0 + 1

# ---- OOMPH: riser, impacts, announcer line
E0=OFF+12.45
def boom(d=1.4,f0=120,f1=38,tau=.45):
    n=int(d*SR); tt=np.arange(n)/SR
    f=f1+(f0-f1)*np.exp(-tt/.06); ph=2*np.pi*np.cumsum(f)/SR
    x=np.sin(ph)*np.exp(-tt/tau)
    cr=lp(rng.standard_normal(n),3500)*np.exp(-tt/.22)*.5
    x+=cr; x[:int(.003*SR)]+=rng.standard_normal(int(.003*SR))*.8
    return x/np.abs(x).max()
def riser(d):
    n=int(d*SR); tt=np.arange(n)/SR; r=tt/d
    nz=bp(rng.standard_normal(n),700,6500)*r**2.2
    f=150+900*r**2; tone=np.sin(2*np.pi*np.cumsum(f)/SR)*r**2*.5
    return (nz+tone)/np.abs(nz+tone).max()
oom=np.zeros(N)
place(oom,riser(1.9),E0-1.9+0.05,10**(-25/20)*1.0)
place(oom,boom(1.1),E0+0.12,10**(-14/20))            # logo slam
place(oom,boom(.8,90,45,.2),E0+0.5,10**(-32/20))  # WANT MORE
place(oom,boom(.5,90,45,.15),E0+0.75,10**(-34/20)) # DIARIES?
place(oom,boom(1.1,110,40,.3),E0+2.9,10**(-19/20))# FOLLOW US
place(oom,boom(.5,80,50,.12),OFF+3.35,10**(-26/20))  # weight on the title bell
vo=load('brand_vo.wav'); vo=vo/np.sqrt((vo**2).mean())*10**(-17/20)
voice=np.zeros(N); place(voice,vo,E0+0.75,1.0)
tot=bed+mus+pen+fx
# normalise full mix using sfx at fixed relative level
sfx_n=sfx; mix=bed+mus+pen+fx+sfx_n*0.5+oom+voice

def w(p,x):
    x=np.clip(x,-1,1); w_=wave.open(p,'wb'); w_.setnchannels(1); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes((x*32767).astype(np.int16).tobytes()); w_.close()
w(f'/tmp/mix_raw_{TUNE}.wav',mix/ max(1e-9,np.abs(mix).max())*0.5)
for nme,x in [('bed',bed),('mus',mus),('pen',pen),('fx',fx),('sfx',sfx_n*.5)]: w(f'/tmp/stem_{TUNE}_{nme}.wav',np.clip(x,-1,1))
