import cv2, numpy as np, os, sys
from scipy.signal import medfilt
os.chdir(os.path.dirname(os.path.abspath(__file__)))
P = '../pages/out/full/'
src = cv2.imread('bright.jpg')
# portrait canvas: drop top 140 rows, mirror wood at bottom, upscale to 2160 wide
cut = 140
sc = src[cut:]
sc = np.vstack([sc, sc[-cut:][::-1]])
S = 2160 / sc.shape[1]
scene = cv2.resize(sc, (2160, int(round(sc.shape[0] * S))), interpolation=cv2.INTER_LANCZOS4)[:3840]
cv2.imwrite('bright_portrait_clean.png', scene)
H, W = scene.shape[:2]
hsv = cv2.cvtColor(scene, cv2.COLOR_BGR2HSV)
mask = ((hsv[..., 1] < 22) & (hsv[..., 2] > 170)).astype(np.uint8)
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))

def tx(x): return int(round(x * S))
def ty(y): return int(round((y - cut) * S))
ymid = ty(1300)

def curves(xa, xb, fa, fb):
    xs = np.arange(fa, fb); top = []; bot = []
    for x in xs:
        col = mask[:, x]; y0 = ymid; y1 = ymid
        while y0 > 0 and col[y0 - 1]: y0 -= 1
        while y1 < H - 1 and col[y1 + 1]: y1 += 1
        top.append(y0); bot.append(y1)
    top = medfilt(np.array(top, float), 31); bot = medfilt(np.array(bot, float), 31)
    kt = np.polyfit(xs, top, 3); kb = np.polyfit(xs, bot, 3)
    X = np.arange(xa, xb + 1)
    return X, np.polyval(kt, X), np.polyval(kb, X)

L = curves(tx(200), tx(771), tx(215), tx(740))
R = curves(tx(779), tx(1368), tx(875), tx(1355))

def region(X, T, B):
    m = np.zeros((H, W), np.float32)
    t = np.interp(np.arange(W), X, T, left=np.nan, right=np.nan)
    b = np.interp(np.arange(W), X, B, left=np.nan, right=np.nan)
    Y = np.arange(H)[:, None]
    ins = (Y >= t[None]) & (Y <= b[None])
    return ins, t, b

g0 = cv2.cvtColor(scene, cv2.COLOR_BGR2GRAY).astype(np.float32)
g0 = cv2.morphologyEx(g0, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))

def put(img, art, X, T, B, ref):
    ins, t, b = region(X, T, B)
    h, w = art.shape[:2]
    mid = (T + B) / 2
    d = np.sqrt(1 + np.gradient(mid) ** 2); s = np.cumsum(d); s = (s - s[0]) / (s[-1] - s[0])
    u = np.interp(np.arange(W), X, s, left=np.nan, right=np.nan)
    tw = X[-1] - X[0]; th = np.nanmax(b - t)
    k = min(1.0, 1.6 * max(tw / w, th / h))
    if k < 1: art = cv2.resize(art, (int(w * k), int(h * k)), interpolation=cv2.INTER_AREA); h, w = art.shape[:2]
    Y = np.arange(H, dtype=np.float32)[:, None]
    V = (Y - t[None]) / (b - t)[None]
    mapx = np.where(ins, u[None] * (w - 1), -1).astype(np.float32)
    mapy = np.where(ins, V * (h - 1), -1).astype(np.float32)
    wa = cv2.remap(art, mapx, mapy, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE).astype(np.float32)
    m = cv2.GaussianBlur(ins.astype(np.float32), (0, 0), 0.9)
    wgt = ins.astype(np.float32)
    g = cv2.GaussianBlur(g0 * wgt, (0, 0), 3) / np.maximum(cv2.GaussianBlur(wgt, (0, 0), 3), 1e-3)
    shade = np.clip(g / ref, 0, 1.06)
    out = wa * shade[..., None]
    return np.clip(img * (1 - m[..., None]) + out * m[..., None], 0, 255).astype(np.uint8)

insL, _, _ = region(*L); insR, _, _ = region(*R)
ref = np.percentile(g0[insL | insR], 96)

SHOTS = {'01-card': (2, 5), '02-squad': (8, 3), '03-map': (4, 7), '04-wood-file': (6, 11),
         '05-day-tue': (16, 17), '06-day-fri': (12, 13), '07-sunday': (28, 29), '08-certificate': (404, 407),
         '09-claim': (36, 37)}
os.makedirs('ad', exist_ok=True); os.makedirs('shop', exist_ok=True)
only = sys.argv[1:] or list(SHOTS)
# square crop centred on book
bx0, bx1 = tx(40), tx(1500)
by0 = ty(850); by1 = ty(1890); cy = (by0 + by1) // 2
for name in only:
    a, b = SHOTS[name]
    for ink in (['colour', 'bw'] if name in ('05-day-tue',) else ['colour']):
        img = scene.copy()
        img = put(img, cv2.imread(f'{P}{ink}_p{a:03d}.png'), *L, ref)
        img = put(img, cv2.imread(f'{P}{ink}_p{b:03d}.png'), *R, ref)
        suf = '' if ink == 'colour' else '-bw'
        if ink == 'colour': cv2.imwrite(f'ad/{name}.png', img)
        side = W; y0 = max(0, cy - side // 2)
        sq = cv2.resize(img[y0:y0 + side, 0:side], (2048, 2048), interpolation=cv2.INTER_AREA)
        cv2.imwrite(f'shop/{name}{suf}.jpg', sq, [cv2.IMWRITE_JPEG_QUALITY, 92])
print('done', scene.shape, 'book y%', by0 / H, by1 / H)
