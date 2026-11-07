import numpy as np, subprocess, sys, io
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from scipy.signal import find_peaks
import endmock as em

W, H, FPS = 1080, 1920, 30
BF = em.F + 'BebasNeue-Regular.ttf'
TOOLS = '/home/claude/sc-assets/diary/locked/tools/'

# ---------------- text
PARAS = ["Tues. Chocolate bar smaller again.", "Same price. Measured it with my tape.",
         "Two fingers short. Not happy.", "Mine stayed full length all day.", "Long cup of tea sorted me out."]
FSIZE = 40
MAXW = 395
_f = ImageFont.truetype(TOOLS + 'permanent-marker.ttf', FSIZE)
LINES = []
for p_ in PARAS:
    cur = ''
    for w_ in p_.split():
        t_ = (cur + ' ' + w_).strip()
        if _f.getlength(t_) <= MAXW: cur = t_
        else: LINES.append(cur); cur = w_
    LINES.append(cur)
print(LINES)
INK = (60, 60, 66)

# ---------------- timeline (seconds, relative to start of segment 2)
ROOM_END = 3.7      # room fully replaced by desk
XF = 1.1            # soft dissolve length
DESK_IN = ROOM_END - XF
WRITE0 = ROOM_END + 0.5
WRITE1 = WRITE0 + 5.6
HOLD_END = WRITE1 + 0.9
FADE = 1.5
END_START = HOLD_END + FADE + 0.25
P2, OUT = 2.9, 2.1
END_TOTAL = P2 + 0.8 + 3.0
TOTAL = END_START + END_TOTAL

# ---------------- watermark (pipeline spec)
wm = Image.open('/tmp/sc_watermark_logo.png').convert('RGBA').resize((200, 200), Image.LANCZOS)
wa = np.array(wm); wa[..., 3] = (wa[..., 3] * 0.9).astype(np.uint8); wm = Image.fromarray(wa)
LX, LY = W - 50 - 200, H - 50 - 200
plate = Image.new('RGBA', (240, 240), (0, 0, 0, 0))
ImageDraw.Draw(plate).rounded_rectangle((0, 0, 239, 239), 28, fill=(255, 255, 255, 158))
WM = Image.new('RGBA', (W, H), (0, 0, 0, 0)); WM.alpha_composite(plate, (LX - 20, LY - 20)); WM.alpha_composite(wm, (LX, LY))

# ---------------- room
room = Image.open('hanky_room_C.png').convert('RGB')
sc = max(W / room.width, H / room.height)
room = room.resize((int(room.width * sc), int(room.height * sc)), Image.LANCZOS)
RW, RH = room.size
TARGET = (150, 1335)  # notebook on the room desk (in 1080x1920 coords)
Z1 = 2.0


def ease(x):
    x = min(1, max(0, x)); return x * x * (3 - 2 * x)


def room_frame(t):
    e = ease(t / ROOM_END)
    z = 1 + (Z1 - 1) * e
    cx = 540 + (TARGET[0] - 540) * e; cy = 960 + (TARGET[1] - 960) * e
    ww, hh = W / z, H / z
    x0 = min(max(cx - ww / 2, 0), RW - ww); y0 = min(max(cy - hh / 2, 0), RH - hh)
    im = room.crop((int(x0), int(y0), int(x0 + ww), int(y0 + hh))).resize((W, H), Image.BILINEAR)
    return im


# ---------------- desk + page
desk = Image.open('hanky_desk_D.png').convert('RGB').resize((W, H))
blank = Image.open('/home/claude/diary_ref/photos/hanky.png').convert('RGBA')
BOX = (70, 72, 650, 820)
page = blank.crop(BOX)
arr = np.array(page).astype(float)
bg = np.array(blank.convert('RGB').getpixel((20, 20))).astype(float)
dd = np.abs(arr[..., :3] - bg).sum(axis=2)
pm = Image.new('L', page.size, 0); ImageDraw.Draw(pm).rounded_rectangle((12, 10, 520, 742), radius=16, fill=255)
pm = np.array(pm).astype(float)
strip = np.zeros_like(pm); strip[25:735, 515:578] = 1
alpha = np.maximum(pm, np.clip((dd - 22) * 9, 0, 255) * strip)
alpha = Image.fromarray(np.array(Image.fromarray(alpha.astype('uint8')).filter(ImageFilter.GaussianBlur(1.2))))
page.putalpha(alpha)
PW = 880
PS = PW / page.width

# ruled lines for text baselines (blank photo coords)
gx0, gy0, gx1, gy1 = 130, 150, 540, 740
g = np.array(blank.convert('L').crop((gx0, gy0, gx1, gy1))).astype(float)
prof = g[:, 20:-20].mean(axis=1); prof = prof - np.convolve(prof, np.ones(41) / 41, 'same')
pk, _ = find_peaks(-prof, distance=12, prominence=1.2)
ys = [gy0 + int(p) for p in pk]
sp = float(np.median(np.diff(ys)))
kstep = 2
start = next(i for i, y in enumerate(ys) if y > gy0 + FSIZE * 0.9)
base = [ys[start + i * kstep] for i in range(len(LINES)) if start + i * kstep < len(ys)]
assert len(base) == len(LINES), (len(base), len(LINES), sp, kstep, len(ys))
font = ImageFont.truetype(TOOLS + 'permanent-marker.ttf', FSIZE)
ink_layer = Image.new('L', blank.size, 0)
d = ImageDraw.Draw(ink_layer)
widths = []
for i, l in enumerate(LINES):
    d.text((gx0 + 10, base[i] - 3), l, font=font, fill=255, anchor='ls')
    widths.append(font.getlength(l))
ink_layer = ink_layer.filter(ImageFilter.GaussianBlur(0.7))
ink_crop = np.array(ink_layer.crop(BOX)).astype(float) / 255 * 0.88
page_rgb = np.array(page.convert('RGB')).astype(float)
bandy = [(base[i] - 3 - FSIZE - 6 - BOX[1], base[i] - 3 + 12 - BOX[1]) for i in range(len(LINES))]
bandx0 = gx0 + 10 - BOX[0] - 6
tot = sum(widths)
alloc = [w / tot * (WRITE1 - WRITE0) for w in widths]
starts = np.concatenate([[WRITE0], WRITE0 + np.cumsum(alloc)[:-1]])


def reveal_mask(t):
    m = np.zeros(ink_crop.shape)
    for i in range(len(LINES)):
        if t <= starts[i]: continue
        p = min(1, (t - starts[i]) / alloc[i])
        ya, yb = int(bandy[i][0]), int(bandy[i][1])
        xe = int(bandx0 + (widths[i] + 24) * p)
        m[ya:yb, :max(xe, 0)] = 1
    return m


# static shadow
page_big = page.resize((PW, int(page.height * PS)), Image.LANCZOS).rotate(-3, expand=True, resample=Image.BICUBIC)
sh = Image.new('RGBA', page_big.size, (0, 0, 0, 0)); sh.putalpha(page_big.split()[3].point(lambda v: int(v * 0.5)))
sh = sh.filter(ImageFilter.GaussianBlur(20))
CX2, CY2 = 540, 1020
desk_base = desk.convert('RGBA')
desk_base.alpha_composite(sh, (CX2 - page_big.width // 2 + 14, CY2 - page_big.height // 2 + 24))


def desk_frame(t):
    m = reveal_mask(t)
    ink = ink_crop * m
    rgb = page_rgb * (1 - ink[..., None]) + np.array(INK, float) * ink[..., None]
    pg = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).convert('RGBA')
    pg.putalpha(alpha)
    pg = pg.resize((PW, int(pg.height * PS)), Image.LANCZOS).rotate(-3, expand=True, resample=Image.BICUBIC)
    f = desk_base.copy()
    f.alpha_composite(pg, (CX2 - pg.width // 2, CY2 - pg.height // 2))
    return f


# ---------------- end card (from build6, same spec)
def layer(draw_fn):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(im); draw_fn(im, dr); return im
logo = em.logo
def L_logo(im, d): im.alpha_composite(logo, (105, 260))
def red_row(d, txt, cy, s=172):
    f = ImageFont.truetype(BF, s)
    d.text((540, cy), txt, font=f, fill=(209, 43, 29, 255), stroke_width=3, stroke_fill='white', anchor='mm')
def L_want1(im, d): red_row(d, "WANT MORE", 1030)
def L_want2(im, d): red_row(d, "DIARIES?", 1030 + 168)
def L_follow(im, d):
    s = 172; f = ImageFont.truetype(BF, s); h = round(s * 1.05)
    d.text((540, 931 + h / 2 + s * 0.03), "FOLLOW US", font=f, fill=(209, 43, 29, 255), stroke_width=3, stroke_fill='white', anchor='mm')
def L_tag(im, d):
    f = ImageFont.truetype(BF, 60); d.text((540, 1135), "1994 HEROES. 2026 PROBLEMS.", font=f, fill='white', anchor='mm')
def L_meet(im, d):
    f = ImageFont.truetype(em.F + 'Oswald%5Bwght%5D.ttf', 29); f.set_variation_by_axes([600]); em.spaced(d, "MEET THE GANG. FIND THE FULL STORY AT", f, 1265, 'white', 2.5)
def L_link(im, d):
    f = ImageFont.truetype(em.F + 'Oswald%5Bwght%5D.ttf', 56); f.set_variation_by_axes([600]); em.spaced(d, "stiffcompetition.shop", f, 1329, 'white', 4.5)
els = [(layer(L_logo), 0.12, 0.9, None), (layer(L_want1), 0.5, 0.2, OUT), (layer(L_want2), 0.75, 0.2, OUT),
       (layer(L_follow), P2 + 0.0, 0.2, None), (layer(L_tag), P2 + 0.3, 0.2, None),
       (layer(L_meet), P2 + 0.6, 0.2, None), (layer(L_link), P2 + 0.8, 0.2, None)]
def halo(l):
    gl_ = l.filter(ImageFilter.GaussianBlur(26)); a = gl_.split()[3].point(lambda v: min(255, int(v * 2.2)))
    gl = Image.new('RGBA', (W, H), (255, 255, 255, 0)); gl.putalpha(a)
    br = ImageEnhance.Brightness(l).enhance(1.5); gl.alpha_composite(br); return gl
HAL = [halo(e[0]) for e in els]
def endcard(t):
    f = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    for (l, st, fi, out), h in zip(els, HAL):
        if t < st: continue
        a = min(1, (t - st) / fi)
        if out is not None: a *= max(0, min(1, (out + 0.5 - t) / 0.5))
        if a <= 0: continue
        x = l.copy(); x.putalpha(x.split()[3].point(lambda v: int(v * a))); f.alpha_composite(x)
        ht = t - st
        if ht < 1.1:
            ha = min(1, ht / fi) * (1 if ht < 0.4 else max(0, (1.1 - ht) / 0.7))
            if out is not None: ha *= max(0, min(1, (out + 0.5 - t) / 0.5))
            y = h.copy(); y.putalpha(y.split()[3].point(lambda v: int(v * ha))); f.alpha_composite(y)
    return f.convert('RGB')


BLACK = Image.new('RGB', (W, H), (0, 0, 0))


def soften(im, r, br=1.0):
    if r > 0.3: im = im.filter(ImageFilter.GaussianBlur(r))
    if br != 1.0: im = ImageEnhance.Brightness(im).enhance(br)
    return im


HAZE = Image.new('RGB', (W, H), (255, 226, 176))


def dreamy(im, k):
    """Street-intro look: soft-focus glow, lifted blacks, warm haze. k 0..1."""
    im = im.convert('RGB')
    if k <= 0.01: return im
    glow = ImageEnhance.Brightness(im.filter(ImageFilter.GaussianBlur(14 * k + 1))).enhance(1.10)
    out = Image.blend(im.filter(ImageFilter.GaussianBlur(5 * k)), glow, 0.45 * k)
    out = ImageEnhance.Contrast(out).enhance(1 - 0.30 * k)
    out = ImageEnhance.Color(out).enhance(1 - 0.18 * k)
    return Image.blend(out, HAZE, 0.22 * k)


CLEAR = 1.6   # desk haze clears over this long after the dissolve


def wm(im):
    im = im.convert('RGBA'); im.alpha_composite(WM)
    return im.convert('RGB')


def room_k(t):
    return 1.0 - 0.4 * ease(min(t / DESK_IN, 1.0))   # 1.0 -> 0.6, never fully sharp


def frame(i):
    t = i / FPS
    if t >= END_START:
        return endcard(t - END_START)
    if t >= HOLD_END + FADE:
        return BLACK
    if t >= HOLD_END:
        q = ease((t - HOLD_END) / FADE)
        return Image.blend(wm(dreamy(desk_frame(t), q)), BLACK, q)
    if t < DESK_IN:
        im = wm(dreamy(room_frame(t), room_k(t)))
        return Image.blend(BLACK, im, ease(t / 1.0))
    if t < ROOM_END:
        p = ease((t - DESK_IN) / XF)
        r = dreamy(room_frame(t), 0.6 + 0.4 * p)
        dk = dreamy(desk_frame(t), 1.0)
        return wm(Image.blend(r, dk, p))
    q = ease(min((t - ROOM_END) / CLEAR, 1.0))
    return wm(dreamy(desk_frame(t), 1.0 - q))


if __name__ == '__main__':
    N = int(FPS * TOTAL)
    if len(sys.argv) > 1 and sys.argv[1] == 'stills':
        for tt in [0.4, 1.2, 2.2, 3.0, 3.6, 4.3, 5.0, 6.5, END_START + 0.9, END_START + 5.0]:
            frame(int(tt * FPS)).save(f'hk_{tt:.1f}.png')
        print('stills', TOTAL, starts, base, kstep, sp)
        sys.exit()
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', 'hk_seg2_silent.mp4'], stdin=subprocess.PIPE)
    for i in range(N): p.stdin.write(frame(i).tobytes())
    p.stdin.close(); p.wait()
    print('seg2 built', TOTAL)
