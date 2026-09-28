# SC Hotline Compose: places a presenter (seated by Gemini in the locked SC Shop Hotline set) onto the exact set pixels.
# Checks every result before accepting it; the set, SC sign and palm are never altered. Playbook 7.8 / 7.9.
import base64, io, time, random
import numpy as np, cv2, requests
from PIL import Image
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
_cache = {}

def load_set(url):
    if url not in _cache:
        img = Image.open(io.BytesIO(requests.get(url, timeout=60).content)).convert('RGB').resize((1080, 1920), Image.LANCZOS)
        _cache.clear(); _cache[url] = np.array(img).astype(np.float32)
    return _cache[url]

def isblue(p):
    return (p[..., 2] > p[..., 0] + 35) & (p[..., 2] > p[..., 1] + 10)

class Req(BaseModel):
    set_url: str
    seat_b64: str
    head_y: int = 430
    desk_top: int = 1045
    front: int = 1095

@app.get('/health')
def health():
    return {'ok': True}

@app.post('/compose')
def compose(r: Req):
    PA = load_set(r.set_url)
    DT, FR, HY = r.desk_top, r.front, r.head_y
    O = np.array(Image.open(io.BytesIO(base64.b64decode(r.seat_b64))).convert('RGB').resize((1080, 1920), Image.LANCZOS)).astype(np.float32)
    side = np.zeros((1920, 1080), bool); side[300:DT - 10, 0:30] = True; side[FR + 40:1700, :] = True
    O += (PA[side].mean(axis=0) - O[side].mean(axis=0)); np.clip(O, 0, 255, out=O)
    diff = np.sqrt(((O - PA) ** 2).sum(axis=2))
    sd = float(diff[side].mean())
    if sd > 14:
        return {'ok': False, 'reason': f'set moved ({sd:.1f})'}
    m = (diff > 38).astype(np.uint8) * 255
    m[:290] = 0; m[FR + 30:] = 0; m[:, :100] = 0; m[:, 980:] = 0
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)); m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    if n < 2:
        return {'ok': False, 'reason': 'no presenter found'}
    m = np.where(lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA]), 255, 0).astype(np.uint8)
    cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE); mf = np.zeros_like(m); cv2.drawContours(mf, cnts, -1, 255, -1)
    ys, xs = np.nonzero(mf); top = int(ys.min())
    if not (300 <= top <= 720): return {'ok': False, 'reason': f'head out of range ({top})'}
    if ys.max() < DT - 40: return {'ok': False, 'reason': 'not seated at the desk'}
    if len(ys) < 60000: return {'ok': False, 'reason': 'presenter too small'}
    if xs.min() < 110 or xs.max() > 970: return {'ok': False, 'reason': 'presenter too wide'}
    # extra objects (e.g. a chair back): dark, colourless areas inside the presenter shape, beside the torso
    lum = O.mean(axis=2); chroma = O.max(axis=2) - O.min(axis=2)
    cx = int(xs.mean()); band = np.zeros_like(mf, bool); band[DT - 320:DT, :] = True; band[:, cx - 130:cx + 130] = False
    extra = int(((mf > 0) & band & (lum < 60) & (chroma < 22)).sum())
    if extra > 4500: return {'ok': False, 'reason': f'extra object beside presenter ({extra}px)'}
    # scale so the head top always lands on the same line, anchored on the desk
    s = (DT - HY) / max(1, (DT - top)); M = np.float32([[s, 0, 540 * (1 - s)], [0, s, DT * (1 - s)]])
    L = cv2.warpAffine(O, M, (1080, 1920), flags=cv2.INTER_LANCZOS4)
    A = cv2.GaussianBlur(cv2.warpAffine(mf.astype(np.float32), M, (1080, 1920)), (5, 5), 0) / 255
    # the SC sign and the palm always stay exactly as in the set
    # Palm-protection removed 29 Sep 2026 (Andy: character must be in front of the plant, not behind it). Only the
    # SC sign (left, x0:360) is still protected from being altered; the palm (right, x640:1080) now composites
    # normally, so wherever the character's generated pose genuinely covers it, he shows in front as required.
    prot = np.zeros((1920, 1080), np.uint8)
    prot[340:680, 0:360] = (~isblue(PA[340:680, 0:360])).astype(np.uint8) * 255
    prot = cv2.dilate(prot, np.ones((9, 9), np.uint8)).astype(np.float32) / 255
    A = A * (1 - prot)
    comp = PA * (1 - A[..., None]) + L * A[..., None]; comp[FR:] = PA[FR:]
    buf = io.BytesIO(); Image.fromarray(comp.clip(0, 255).astype(np.uint8)).save(buf, 'PNG')
    return {'ok': True, 'reason': 'ok', 'scale': round(float(s), 3), 'png_b64': base64.b64encode(buf.getvalue()).decode()}

class Cut(BaseModel):
    url: str

@app.post('/cutout')
def cutout(c: Cut):
    # product photo for the on-screen box: background (connected to the photo edges) removed, uploaded as a transparent PNG
    im = Image.open(io.BytesIO(requests.get(c.url, timeout=60).content)).convert('RGB'); im.thumbnail((1200, 1200))
    a = np.array(im); h, w = a.shape[:2]
    m = np.zeros((h + 2, w + 2), np.uint8); ff = a.copy()
    for pt in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        cv2.floodFill(ff, m, pt, (255, 0, 255), (40, 40, 40), (40, 40, 40), flags=cv2.FLOODFILL_FIXED_RANGE | 4)
    bg = m[1:-1, 1:-1] > 0
    alpha = np.where(bg, 0, 255).astype(np.uint8); alpha = cv2.GaussianBlur(alpha, (3, 3), 0)
    ys, xs = np.nonzero(alpha > 10)
    if len(ys) == 0: return {'ok': False, 'reason': 'nothing left after cut-out'}
    rgba = np.dstack([a, alpha])[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    buf = io.BytesIO(); Image.fromarray(rgba, 'RGBA').save(buf, 'PNG')
    r = requests.post('https://api.cloudinary.com/v1_1/dkapdtxek/image/upload', data={'upload_preset': 'SCSMAuto', 'asset_folder': 'SCSMAuto', 'public_id': 'box_%d_%d' % (int(time.time() * 1000), random.randint(0, 99999))}, files={'file': ('box.png', buf.getvalue())}, timeout=120).json()
    return {'ok': bool(r.get('secure_url')), 'url': r.get('secure_url'), 'removed_background': round(float(bg.mean()), 3)}

# ---------- SC Shop Hotline graphics rendered as real video (smooth motion at 25 fps) ----------
from PIL import ImageDraw, ImageFont
_fonts = {}
def font(name, size):
    key = (name, size)
    if key not in _fonts:
        path = '/tmp/' + name
        try:
            open(path, 'rb').close()
        except Exception:
            data = requests.get('https://github.com/google/fonts/raw/main/ofl/barlowcondensed/' + name, timeout=60).content
            open(path, 'wb').write(data)
        _fonts[key] = ImageFont.truetype(path, size)
    return _fonts[key]

ROYAL, NAVY, RED, WHITE = (30, 79, 194), (20, 40, 107), (208, 2, 27), (255, 255, 255)
FPS, DUR = 25, 5.0

def star(d, cx, cy, r, fill):
    import math
    pts = []
    for i in range(10):
        a = math.pi / 2 + i * math.pi / 5; rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(a), cy - rr * math.sin(a)))
    d.polygon(pts, fill=fill)

def write_video(frames, w, h):
    path = '/tmp/v_%d.mp4' % int(time.time() * 1000)
    vw = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*'mp4v'), FPS, (w, h))
    for f in frames: vw.write(cv2.cvtColor(np.array(f), cv2.COLOR_RGB2BGR))
    vw.release()
    r = requests.post('https://api.cloudinary.com/v1_1/dkapdtxek/video/upload', data={'upload_preset': 'SCSMAuto', 'asset_folder': 'SCSMAuto', 'public_id': 'hotline_gfx_%d_%d' % (int(time.time() * 1000), random.randint(0, 99999))}, files={'file': ('g.mp4', open(path, 'rb').read())}, timeout=180).json()
    u = r.get('secure_url', '')
    return u.replace('/video/upload/', '/video/upload/vc_h264,q_auto:best/') if u else ''

def strip(text_units, h, bg, fg, f, logo=None, star_r=0, gap=36):
    # one long strip of repeated units, drawn once
    d0 = ImageDraw.Draw(Image.new('RGB', (10, 10)))
    parts = []
    for u in text_units:
        if u == '*': parts.append(('star', star_r * 2 + gap * 2))
        elif u == 'LOGO': parts.append(('logo', logo.width + gap))
        else: parts.append(('text', int(d0.textlength(u, font=f)), u))
    unit_w = sum(p[1] for p in parts)
    reps = int((1080 + 200 * DUR) / unit_w) + 3
    im = Image.new('RGB', (unit_w * reps, h), bg); d = ImageDraw.Draw(im)
    cap = f.getbbox('M'); x = 0
    for _ in range(reps):
        for p in parts:
            if p[0] == 'text':
                d.text((x, h // 2 - (cap[1] + cap[3]) // 2), p[2], font=f, fill=fg); x += p[1]
            elif p[0] == 'star':
                star(d, x + p[1] // 2, h // 2, star_r, fg); x += p[1]
            else:
                im.paste(logo, (x + gap // 2, h // 2 - logo.height // 2), logo); x += p[1]
    return im

class Gfx(BaseModel):
    tick: str
    box_url: str = ''
    box_name: str = ''
    set_url: str = 'https://res.cloudinary.com/dkapdtxek/image/upload/v1790557122/SCSMAuto/sc_hotline_set_locked_v2.png'

@app.post('/hotline-gfx')
def hotline_gfx(g: Gfx):
    n = int(FPS * DUR)
    # ticker: 6 px red rule, royal row (logo + name + stars, white italic), white row (shop address, navy); readable crawl
    fi = font('BarlowCondensed-BoldItalic.ttf', 72); fb = font('BarlowCondensed-Bold.ttf', 48)
    lg = Image.open(io.BytesIO(requests.get('https://res.cloudinary.com/dkapdtxek/image/upload/v1790460791/SCSMAuto/sc_ticker_logo_white.png', timeout=60).content)).convert('RGBA')
    capH = fi.getbbox('M')[3] - fi.getbbox('M')[1]; lg = lg.resize((int(lg.width * capH / lg.height), capH))
    top = strip(['LOGO', g.tick.upper(), '*', 'IN STOCK NOW', '*'], 87, ROYAL, WHITE, fi, logo=lg, star_r=20)
    bot = strip(['STIFFCOMPETITION.SHOP', '*'], 80, WHITE, NAVY, fb, star_r=14)
    SPEED_TOP, SPEED_BOT = 130.0, 100.0
    tframes = []
    for i in range(n):
        t = i / FPS; fr = Image.new('RGB', (1080, 178), WHITE)
        fr.paste(Image.new('RGB', (1080, 6), RED), (0, 0))
        fr.paste(top.crop((int(SPEED_TOP * t), 0, int(SPEED_TOP * t) + 1080, 87)), (0, 6))
        fr.paste(Image.new('RGB', (1080, 4), NAVY), (0, 93))
        fr.paste(bot.crop((int(SPEED_BOT * t), 0, int(SPEED_BOT * t) + 1080, 80)), (0, 97))
        tframes.append(fr)
    ticker_url = write_video(tframes, 1080, 178)
    # product box over the desk front: slides in (0.5 s), the product slowly pushes in, one light sheen
    RX, RY, RW, RH = 0, 1170, 660, 470
    setimg = Image.open(io.BytesIO(requests.get(g.set_url, timeout=60).content)).convert('RGB').resize((1080, 1920))
    bg = setimg.crop((RX, RY, RX + RW, RY + RH))
    BW, BH, BX, BY = 560, 420, 56, 1189
    prod = None
    if g.box_url:
        prod = Image.open(io.BytesIO(requests.get(g.box_url, timeout=60).content)).convert('RGBA')
    grad = Image.new('RGB', (BW, BH - 78))
    gd = ImageDraw.Draw(grad)
    for yy in range(BH - 78):
        k = yy / (BH - 78); gd.line([(0, yy), (BW, yy)], fill=tuple(int(ROYAL[c] * (1 - k) + NAVY[c] * k) for c in range(3)))
    nf = font('BarlowCondensed-Bold.ttf', 46)
    name = (g.box_name or g.tick).upper()
    while nf.getlength(name) > BW - 30 and nf.size > 30: nf = font('BarlowCondensed-Bold.ttf', nf.size - 2)
    bframes = []
    for i in range(n):
        t = i / FPS
        card = Image.new('RGB', (BW, BH), WHITE); card.paste(grad, (0, 0))
        if prod is not None:
            z = 1.0 + 0.08 * (t / DUR); p = prod.copy(); p.thumbnail((int(470 * z), int(292 * z)))
            sh = Image.new('RGBA', (BW, BH - 78), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
            sd.ellipse([BW // 2 - 180, 290, BW // 2 + 180, 322], fill=(0, 0, 0, 120))
            card.paste(Image.alpha_composite(Image.new('RGBA', sh.size, (0, 0, 0, 0)), sh).convert('RGB'), (0, 0), sh.split()[3].point(lambda v: v // 2))
            card.paste(p, ((BW - p.width) // 2, int((BH - 78) * 0.48) - p.height // 2), p)
        cd = ImageDraw.Draw(card)
        cd.rectangle([0, BH - 78, BW, BH], fill=ROYAL); cd.rectangle([0, BH - 78, BW, BH - 72], fill=RED)
        nb = cd.textbbox((0, 0), name, font=nf); cd.text(((BW - (nb[2] - nb[0])) // 2 - nb[0], BH - 39 - (nb[1] + nb[3]) // 2), name, font=nf, fill=WHITE)
        if 0.7 <= t <= 1.8:   # one sheen sweep
            k = (t - 0.7) / 1.1; sx = int(-200 + k * (BW + 400))
            ov = Image.new('RGBA', (BW, BH), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
            for dx in range(-60, 61):
                od.line([(sx + dx + 80, 0), (sx + dx - 80, BH)], fill=(255, 255, 255, int(70 * (1 - abs(dx) / 60))))
            card = Image.alpha_composite(card.convert('RGBA'), ov).convert('RGB')
        framed = Image.new('RGB', (BW + 10, BH + 10), WHITE); framed.paste(card, (5, 5))
        off = 0 if t >= 0.5 else int(-(BW + 80) * (1 - (t / 0.5)) ** 3)
        fr = bg.copy()
        shadow = Image.new('L', (RW, RH), 0); ImageDraw.Draw(shadow).rectangle([BX - 5 - RX + off + 8, BY - 5 - RY + 12, BX + BW + 5 - RX + off + 8, BY + BH + 5 - RY + 12], fill=110)
        from PIL import ImageFilter
        shadow = shadow.filter(ImageFilter.GaussianBlur(8))
        fr = Image.composite(Image.new('RGB', (RW, RH), (0, 0, 0)), fr, shadow)
        fr.paste(framed, (BX - 5 - RX + off, BY - 5 - RY))
        bframes.append(fr)
    box_url = write_video(bframes, RW, RH)
    return {'ok': bool(ticker_url and box_url), 'ticker_url': ticker_url, 'ticker_xywh': [0, 1702, 1080, 178], 'box_url': box_url, 'box_xywh': [RX, RY, RW, RH]}

# ---------- Travel the World: keep the original NFT artwork pixel for pixel inside the 9:16 extension ----------
class Merge(BaseModel):
    extended_b64: str
    original_url: str

@app.post('/travel-merge')
def travel_merge(m: Merge):
    ext = Image.open(io.BytesIO(base64.b64decode(m.extended_b64))).convert('RGB').resize((1080, 1920), Image.LANCZOS)
    org = Image.open(io.BytesIO(requests.get(m.original_url, timeout=60).content)).convert('RGB')
    ow = 1080; oh = int(org.height * ow / org.width); org = org.resize((ow, oh), Image.LANCZOS)
    # find where the extension placed the artwork (best vertical match), then lay the original back exactly there
    E = cv2.cvtColor(np.array(ext), cv2.COLOR_RGB2GRAY).astype(np.float32)
    O = cv2.cvtColor(np.array(org), cv2.COLOR_RGB2GRAY).astype(np.float32)
    small = 4
    Es = cv2.resize(E, (1080 // small, 1920 // small)); Os = cv2.resize(O, (ow // small, oh // small))
    res = cv2.matchTemplate(Es, Os, cv2.TM_CCOEFF_NORMED); _, score, _, loc = cv2.minMaxLoc(res)
    y = int(loc[1] * small)
    y = max(0, min(1920 - oh, y))
    mask = Image.new('L', (ow, oh), 255)
    fe = 28
    md = np.array(mask).astype(np.float32)
    for k in range(fe):
        a = 255 * (k + 1) / fe
        md[k, :] = np.minimum(md[k, :], a); md[oh - 1 - k, :] = np.minimum(md[oh - 1 - k, :], a)
    # the artwork's own corner logo must not be repeated in the painted areas above or below it
    A = np.array(ext)
    corner = np.array(org)[int(oh * 0.84):, int(ow * 0.84):]
    cg = cv2.cvtColor(corner, cv2.COLOR_RGB2GRAY)
    removed = 0
    for (y0, y1) in [(0, y), (y + oh, 1920)]:
        if y1 - y0 < cg.shape[0] + 4: continue
        band = cv2.cvtColor(A[y0:y1], cv2.COLOR_RGB2GRAY)
        for _ in range(3):
            best = None
            for sc in (0.8, 0.9, 1.0, 1.1, 1.25):
                t = cv2.resize(cg, (max(8, int(cg.shape[1] * sc)), max(8, int(cg.shape[0] * sc))))
                if t.shape[0] >= band.shape[0] or t.shape[1] >= band.shape[1]: continue
                r = cv2.matchTemplate(band, t, cv2.TM_CCOEFF_NORMED); _, v, _, l = cv2.minMaxLoc(r)
                if best is None or v > best[0]: best = (v, l, t.shape)
            if not best or best[0] < 0.55: break
            v, (lx, ly), (th, tw) = best
            mk = np.zeros(A.shape[:2], np.uint8); mk[y0 + ly - 6:y0 + ly + th + 6, max(0, lx - 6):lx + tw + 6] = 255
            A = cv2.inpaint(A, mk, 9, cv2.INPAINT_TELEA); band = cv2.cvtColor(A[y0:y1], cv2.COLOR_RGB2GRAY); removed += 1
    ext = Image.fromarray(A)
    ext.paste(org, (0, y), Image.fromarray(md.astype(np.uint8)))
    buf = io.BytesIO(); ext.save(buf, 'PNG')
    return {'ok': True, 'y': y, 'match': round(float(score), 3), 'logos_removed': removed, 'png_b64': base64.b64encode(buf.getvalue()).decode()}
