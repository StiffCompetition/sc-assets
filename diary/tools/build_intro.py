import sys, random, subprocess, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np

W, H, FPS = 1080, 1920, 30
T = float(os.environ.get('T', 3.7))
FD = 0.6 if T > 4 else 0.45
PLACE = sys.argv[1] if len(sys.argv) > 1 else "WALTHAMSTOW"
IMG = sys.argv[2] if len(sys.argv) > 2 else "wthm_C.png"
OUT = sys.argv[3] if len(sys.argv) > 3 else "intro_walthamstow_TEST.mp4"
FONT = "fonts/package/files/special-elite-latin-400-normal.woff"
L1, L2 = "THE STIFF DIARIES", PLACE
TYPE0, TYPE1 = 0.5, 2.7  # typing window (s)
BELL = 2.85

random.seed(7)
bg = Image.open(IMG).convert("RGB")
s = max(W / bg.width, H / bg.height) * 1.08
bg = bg.resize((int(bg.width * s), int(bg.height * s)), Image.LANCZOS)
bg = bg.filter(ImageFilter.GaussianBlur(5))
bg = ImageEnhance.Brightness(bg).enhance(0.8)
# vignette
yy, xx = np.mgrid[0:bg.height, 0:bg.width]
d = np.sqrt(((xx - bg.width / 2) / (bg.width / 2)) ** 2 + ((yy - bg.height / 2) / (bg.height / 2)) ** 2)
v = np.clip(1.15 - 0.45 * d ** 2, 0.45, 1)
arr = (np.asarray(bg).astype(float) * v[..., None]).astype(np.uint8)
bg = Image.fromarray(arr)

f1 = ImageFont.truetype(FONT, 78)
sz = 150
f2 = ImageFont.truetype(FONT, sz)
while sum(f2.getlength(c) for c in L2) > 840:
    sz -= 4
    f2 = ImageFont.truetype(FONT, sz)
chars = [(c, 1) for c in L1] + [(c, 2) for c in L2]
n = len(chars)
times = [TYPE0 + (TYPE1 - TYPE0) * i / (n - 1) + random.uniform(-0.02, 0.02) for i in range(n)]
times.sort()


def line_layout(txt, font, cy):
    w = sum(font.getlength(c) for c in txt)
    x = (W - w) / 2
    pos = []
    for c in txt:
        pos.append(x)
        x += font.getlength(c)
    return pos, cy


p1, y1 = line_layout(L1, f1, 800)
p2, y2 = line_layout(L2, f2, 900)
jit = [random.randint(-2, 2) for _ in range(n)]
CREAM = (246, 238, 216)


ROOM0 = Image.open('room0.png').convert('RGB') if os.environ.get('DISS0') else None


WMO = Image.open('wm_overlay.png').convert('RGBA') if os.environ.get('DISS0') else None


def frame(t):
    z = 1.0 + float(os.environ.get('ZOOM', 0.04)) * (t / T)
    w, h = int(W * z), int(H * z)
    cw, ch = bg.size
    box = ((cw - W / z * 1.0) / 2, (ch - H / z * 1.0) / 2, (cw + W / z) / 2, (ch + H / z) / 2)
    im = bg.crop(tuple(int(b) for b in box)).resize((W, H), Image.BILINEAR)
    dr = ImageDraw.Draw(im, "RGBA")
    k = 0
    for i, (c, ln) in enumerate(chars):
        if times[i] > t:
            break
        if ln == 1:
            x = p1[i]; y = y1; f = f1
        else:
            x = p2[i - len(L1)]; y = y2; f = f2
        y += jit[i]
        dr.text((x + 3, y + 4), c, font=f, fill=(0, 0, 0, 170))
        dr.text((x, y), c, font=f, fill=CREAM)
    # cursor after last typed char until bell
    if t < BELL + 0.3:
        typed = sum(1 for x in times if x <= t)
        if 0 < typed <= n:
            if typed <= len(L1):
                cx = (p1[typed] if typed < len(L1) else p1[-1] + f1.getlength(L1[-1])); cy = y1; ff = f1
            else:
                j = typed - len(L1)
                cx = (p2[j] if j < len(L2) else p2[-1] + f2.getlength(L2[-1])); cy = y2; ff = f2
            if int(t * 6) % 2 == 0:
                dr.rectangle([cx + 4, cy + ff.size * 0.15, cx + 4 + ff.size * 0.08, cy + ff.size * 1.05], fill=CREAM + (200,))
    if WMO is not None:
        im = im.convert('RGBA'); im.alpha_composite(WMO); im = im.convert('RGB')
    # fades
    a = 1.0
    if t < 0.4:
        a = t / 0.4
    if os.environ.get('DISS0'):
        d0 = float(os.environ['DISS0'])
        if t > d0:
            x = (t - d0) / (T - d0); x = x * x * (3 - 2 * x)
            im = Image.blend(im, ROOM0, x)
    elif t > T - FD:
        a = max(0.0, (T - t) / FD)
    if a < 1:
        im = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), im, a)
    return im


cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
       "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-t", str(T), "intro_silent.mp4"]
pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
for i in range(int(T * FPS)):
    pr.stdin.write(frame(i / FPS).tobytes())
pr.stdin.close()
pr.wait()
print("done", OUT)

aud = ("[0:a]asplit=2[a1][a2];[a1]atrim=0.1:2.45,asetpts=PTS-STARTPTS,adelay=450|450[k];"
       "[a2]atrim=3.5:5.7,asetpts=PTS-STARTPTS,volume=0.9,adelay=2850|2850[b];"
       f"[k][b]amix=inputs=2:normalize=0,volume=0.7,afade=t=out:st={T-FD}:d={FD},apad[a]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "tw_pack.mp3", "-filter_complex", aud, "-map", "[a]", "-t", str(T), "intro_audio.wav"], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "intro_silent.mp4", "-i", "intro_audio.wav", "-map", "0:v", "-map", "1:a",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-t", str(T), OUT], check=True)
print("muxed", OUT)
