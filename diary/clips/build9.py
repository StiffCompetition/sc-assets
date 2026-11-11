import subprocess, sys
import build_hanky9 as b
FPS=b.FPS; W,H=b.W,b.H
def enc(name):
    return subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p',name],stdin=subprocess.PIPE)
na=int(FPS*(b.HOLD_END+b.FADE))
p=enc('hk9_segA.mp4')
for i in range(na): p.stdin.write(b.frame(i).tobytes())
p.stdin.close();p.wait()
nb=int(FPS*b.END_TOTAL)
p=enc('hk9_segB.mp4')
for i in range(nb): p.stdin.write(b.endcard(i/FPS).tobytes())
p.stdin.close();p.wait()
print('built',na/FPS,nb/FPS)
