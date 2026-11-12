import os, sys, subprocess, numpy as np, cv2
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import importlib.util as iu
sp = iu.spec_from_file_location('b', 'build.py'); B = iu.module_from_spec(sp); sp.loader.exec_module(B)
H, W, scene, L, R, ref, g0 = B.H, B.W, B.scene, B.L, B.R, B.ref, B.g0
P = '../pages/out/full/'
OUT = 1080; FPS = 30

def geom(X, T, Bt):
    ins, t, b = B.region(X, T, Bt)
    mid = (T + Bt) / 2
    d = np.sqrt(1 + np.gradient(mid) ** 2); s = np.cumsum(d); s = (s - s[0]) / (s[-1] - s[0])
    u = np.interp(np.arange(W), X, s, left=np.nan, right=np.nan)
    Y = np.arange(H, dtype=np.float32)[:, None]
    V = (Y - t[None]) / (b - t)[None]
    wgt = ins.astype(np.float32)
    g = cv2.GaussianBlur(g0 * wgt, (0, 0), 3) / np.maximum(cv2.GaussianBlur(wgt, (0, 0), 3), 1e-3)
    shade = np.clip(g / ref, 0, 1.06)
    return dict(ins=ins, U=np.broadcast_to(u[None], (H, W)), V=V, shade=shade)

GL = geom(*L); GR = geom(*R)
cache = {}
def art(ink, p):
    k = (ink, p)
    if k not in cache:
        a = cv2.imread(f'{P}{ink}_p{p:03d}.png')
        cache[k] = cv2.resize(a, (int(a.shape[1] * 0.55), int(a.shape[0] * 0.55)), interpolation=cv2.INTER_AREA)
    return cache[k]

def paint(img, a, G, u0, u1, flip=False, dark=0.0):
    """paint art a onto page geometry G where u in [u0,u1]; art spans that band. flip: art x reversed (back of page not used)."""
    if u1 - u0 < 1e-3: return img
    h, w = a.shape[:2]
    U = G['U']; band = G['ins'] & (U >= u0) & (U <= u1)
    au = (U - u0) / (u1 - u0)
    mapx = np.where(band, au * (w - 1), -1).astype(np.float32)
    mapy = np.where(band, G['V'] * (h - 1), -1).astype(np.float32)
    wa = cv2.remap(a, mapx, mapy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE).astype(np.float32)
    sh = G['shade'] * (1 - dark)
    m = cv2.GaussianBlur(band.astype(np.float32), (0, 0), 0.9)[..., None]
    return np.clip(img * (1 - m) + wa * sh[..., None] * m, 0, 255).astype(np.uint8)

def edge_shadow(img, G, ux, side, strength):
    U = G['U']; ins = G['ins']
    dist = (ux - U) if side == 'left' else (U - ux)
    sh = np.where(ins & (dist > 0), np.exp(-np.maximum(dist, 0) / 0.06) * strength, 0).astype(np.float32)
    return np.clip(img * (1 - sh[..., None]), 0, 255).astype(np.uint8)

def frame(img):
    return cv2.resize(img, (OUT, int(OUT * H / W)), interpolation=cv2.INTER_AREA)

SPREADS = [(2, 5), (8, 3), (4, 7), (6, 11), (16, 17), (12, 13), (28, 29), (36, 37), (404, 407)]
HOLD, TURN = int(1.9 * FPS), int(0.7 * FPS)
ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{OUT}x{int(OUT*H/W)}',
                       '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p',
                       '-movflags', '+faststart', 'journal_flip_through.mp4'], stdin=subprocess.PIPE)
def write(img, n=1):
    f = frame(img).tobytes()
    for _ in range(n): ff.stdin.write(f)

def spread(l, r):
    img = paint(scene.copy(), art('colour', l), GL, 0, 1)
    return paint(img, art('colour', r), GR, 0, 1)

ease = lambda x: 0.5 - 0.5 * np.cos(np.pi * x)
for i, (l, r) in enumerate(SPREADS):
    write(spread(l, r), HOLD if i < len(SPREADS) - 1 else int(2.6 * FPS))
    if i == len(SPREADS) - 1: break
    nl, nr = SPREADS[i + 1]
    for k in range(1, TURN):
        x = ease(k / TURN)
        img = paint(scene.copy(), art('colour', l), GL, 0, 1)
        img = paint(img, art('colour', nr), GR, 0, 1)
        if x < 0.5:  # right page folds toward gutter
            s = 1 - 2 * x
            img = edge_shadow(img, GR, s, 'right', 0.35 * (1 - s))
            img = paint(img, art('colour', r), GR, 0, s, dark=0.25 * (1 - s))
        else:  # new left page unfolds from gutter
            s = 2 * x - 1
            img = edge_shadow(img, GL, 1 - s, 'left', 0.35 * (1 - s))
            img = paint(img, art('colour', nl), GL, 1 - s, 1, dark=0.25 * (1 - s))
        write(img)
ff.stdin.close(); ff.wait()
print('ok')
