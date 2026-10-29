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
    # 29 Oct 2026 (media move): no Cloudinary upload any more. The transparent PNG is returned as base64 (small); the caller stores it with SC - Store File.
    return {'ok': True, 'png_b64': base64.b64encode(buf.getvalue()).decode(), 'removed_background': round(float(bg.mean()), 3)}

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

def write_video(frames, w, h, put=None):
    # 25 Oct 2026 (media move): h264 via ffmpeg, PUT to a Shopify staged upload address when one is given (the caller then
    # registers it through SC - File Store). Without an address the old Cloudinary upload still runs, so nothing breaks mid-switch.
    path = '/tmp/v_%d.mp4' % int(time.time() * 1000)
    enc = _sp.Popen([_ffmpeg(), '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (w, h), '-r', str(FPS), '-i', '-',
                     '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'veryfast', '-crf', '18', '-movflags', '+faststart', path], stdin=_sp.PIPE)
    for f in frames: enc.stdin.write(np.array(f.convert('RGB')).tobytes())
    enc.stdin.close(); enc.wait()
    data = open(path, 'rb').read()
    try: _os.remove(path)
    except Exception: pass
    if put:
        r = requests.put(put, data=data, headers={'Content-Type': 'video/mp4'}, timeout=300)
        return 'put:%d' % r.status_code if r.status_code < 300 else ''
    # 29 Oct 2026: the old Cloudinary fallback is retired; a caller must give an upload address (SC - Upload Targets).
    return ''

def strip(text_units, h, bg, fg, f, logo=None, star_r=0, gap=36, dur=DUR):
    # one long strip of repeated units, drawn once
    d0 = ImageDraw.Draw(Image.new('RGB', (10, 10)))
    parts = []
    for u in text_units:
        if u == '*': parts.append(('star', star_r * 2 + gap * 2))
        elif u == 'LOGO': parts.append(('logo', logo.width + gap))
        else: parts.append(('text', int(d0.textlength(u, font=f)), u))
    unit_w = sum(p[1] for p in parts)
    reps = int((1080 + 200 * dur) / unit_w) + 3
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
    dur: float = 5.0            # clip length in seconds (Product 5, NFT 8)
    phrase: str = 'IN STOCK NOW'  # top-row text after the name; '*' between parts draws a star (NFT: 'ONE OF ONE*OWN IT NOW')
    box: bool = True            # Product posts need the product box; NFT posts do not
    box_url: str = ''
    box_name: str = ''
    set_url: str = 'https://cdn.shopify.com/s/files/1/0661/7428/7966/files/cl_SCSMAuto_sc_hotline_set_brick_v1.png'
    logo_url: str = 'https://cdn.shopify.com/s/files/1/0661/7428/7966/files/cl_SCSMAuto_sc_ticker_logo_white.png'
    ticker_put: str = ''        # Shopify staged upload addresses (SC - File Store, action targets); empty = old Cloudinary upload
    box_put: str = ''
    box2_url: str = ''          # second product photo: flattened onto white as a 480 x 480 square (the old Cloudinary c_fill,b_white)
    box2_put: str = ''

@app.post('/hotline-gfx')
def hotline_gfx(g: Gfx):
    n = int(FPS * g.dur)
    # ticker: 6 px red rule, royal row (logo + name + stars, white italic), white row (shop address, navy); readable crawl
    fi = font('BarlowCondensed-BoldItalic.ttf', 72); fb = font('BarlowCondensed-Bold.ttf', 48)
    lg = Image.open(io.BytesIO(requests.get(g.logo_url, timeout=60).content)).convert('RGBA')
    capH = fi.getbbox('M')[3] - fi.getbbox('M')[1]; lg = lg.resize((int(lg.width * capH / lg.height), capH))
    units = ['LOGO', g.tick.upper(), '*']
    for part in g.phrase.split('*'):
        if part.strip(): units += [part.strip().upper(), '*']
    top = strip(units, 87, ROYAL, WHITE, fi, logo=lg, star_r=20, dur=g.dur)
    bot = strip(['STIFFCOMPETITION.SHOP', '*'], 80, WHITE, NAVY, fb, star_r=14, dur=g.dur)
    SPEED_TOP, SPEED_BOT = 130.0, 100.0
    tframes = []
    for i in range(n):
        t = i / FPS; fr = Image.new('RGB', (1080, 178), WHITE)
        fr.paste(Image.new('RGB', (1080, 6), RED), (0, 0))
        fr.paste(top.crop((int(SPEED_TOP * t), 0, int(SPEED_TOP * t) + 1080, 87)), (0, 6))
        fr.paste(Image.new('RGB', (1080, 4), NAVY), (0, 93))
        fr.paste(bot.crop((int(SPEED_BOT * t), 0, int(SPEED_BOT * t) + 1080, 80)), (0, 97))
        tframes.append(fr)
    ticker_url = write_video(tframes, 1080, 178, g.ticker_put or None)
    box2 = ''
    if g.box2_url and g.box2_put:
        im2 = ImageOps.exif_transpose(Image.open(io.BytesIO(requests.get(g.box2_url, timeout=60).content))).convert('RGBA')
        im2 = ImageOps.fit(im2, (480, 480), Image.LANCZOS, centering=(0.5, 0.5))
        flat = Image.new('RGBA', (480, 480), (255, 255, 255, 255)); flat.alpha_composite(im2)
        b2 = io.BytesIO(); flat.convert('RGB').save(b2, 'JPEG', quality=90)
        r2 = requests.put(g.box2_put, data=b2.getvalue(), headers={'Content-Type': 'image/jpeg'}, timeout=120)
        box2 = 'put:%d' % r2.status_code if r2.status_code < 300 else ''
    if not g.box:
        return {'ok': bool(ticker_url), 'ticker_url': ticker_url, 'ticker_xywh': [0, 1702, 1080, 178], 'box_url': '', 'box_xywh': None, 'box2': box2}
    # product box over the desk front (Playbook 7.7.2, 8 Oct 2026): one fixed square box, the same size and place on every post;
    # it slides in from the left of the screen and settles on the right.
    # The product photo fills it edge to edge (cover fit); Andy's crop from the dashboard arrives already applied in box_url.
    # No name bar: the ticker carries the name. Slides in (0.5 s), the product slowly pushes in, one light sheen.
    # Square 480 x 480, the same shape as the shop's product photos; it settles on the right of the desk front with
    # equal 47 px gaps under the desk lip (ends at y 1118), above the ticker (y 1702) and to the right edge.
    BW, BH = 480, 480
    BX, BY = 1080 - 47 - 5 - BW, 1118 + 47 + 5
    RX, RY, RW, RH = 0, BY - 24, 1080, BH + 44
    setimg = Image.open(io.BytesIO(requests.get(g.set_url, timeout=60).content)).convert('RGB').resize((1080, 1920))
    bg = setimg.crop((RX, RY, RX + RW, RY + RH))
    prod = None
    if g.box_url:
        prod = Image.open(io.BytesIO(requests.get(g.box_url, timeout=60).content)).convert('RGB')
    def cover(img, w, h):
        s = max(w / img.width, h / img.height)
        r = img.resize((max(w, int(round(img.width * s))), max(h, int(round(img.height * s)))))
        x0 = (r.width - w) // 2; y0 = (r.height - h) // 2
        return r.crop((x0, y0, x0 + w, y0 + h))
    bframes = []
    for i in range(n):
        t = i / FPS
        if prod is not None:
            z = 1.0 + 0.08 * (t / DUR)
            zw, zh = int(BW * z), int(BH * z)
            card = cover(prod, zw, zh).crop(((zw - BW) // 2, (zh - BH) // 2, (zw - BW) // 2 + BW, (zh - BH) // 2 + BH))
        else:
            card = Image.new('RGB', (BW, BH), ROYAL)
        if 0.7 <= t <= 1.8:   # one sheen sweep
            k = (t - 0.7) / 1.1; sx = int(-200 + k * (BW + 400))
            ov = Image.new('RGBA', (BW, BH), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
            for dx in range(-60, 61):
                od.line([(sx + dx + 80, 0), (sx + dx - 80, BH)], fill=(255, 255, 255, int(70 * (1 - abs(dx) / 60))))
            card = Image.alpha_composite(card.convert('RGBA'), ov).convert('RGB')
        framed = Image.new('RGB', (BW + 10, BH + 10), WHITE); framed.paste(card, (5, 5))
        off = 0 if t >= 0.6 else int(-(BX + BW + 40) * (1 - (t / 0.6)) ** 3)   # slides in from off the left edge
        fr = bg.copy()
        shadow = Image.new('L', (RW, RH), 0); ImageDraw.Draw(shadow).rectangle([BX - 5 - RX + off + 8, BY - 5 - RY + 12, BX + BW + 5 - RX + off + 8, BY + BH + 5 - RY + 12], fill=110)
        from PIL import ImageFilter
        shadow = shadow.filter(ImageFilter.GaussianBlur(8))
        fr = Image.composite(Image.new('RGB', (RW, RH), (0, 0, 0)), fr, shadow)
        fr.paste(framed, (BX - 5 - RX + off, BY - 5 - RY))
        bframes.append(fr)
    box_url = write_video(bframes, RW, RH, g.box_put or None)
    return {'ok': bool(ticker_url and box_url), 'ticker_url': ticker_url, 'ticker_xywh': [0, 1702, 1080, 178], 'box_url': box_url, 'box_xywh': [RX, RY, RW, RH], 'box2': box2}

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

# ---------- NFT post: one reusable template clip per character (Playbook: NFT post type) ----------
# Builds the 8 s gallery template: the wall slides only while the character walks (timing measured per character),
# the frame opening is a flat magenta key area, the character is cut out of his green-screen clip and placed in front.
# Per post, json2video lays the NFT under the template (keyframes returned here) and keys out the magenta.
import json as _json, subprocess as _sp, shutil as _sh
from PIL import ImageOps
def _ffmpeg():
    # system ffmpeg if present, otherwise the static build bundled with the imageio-ffmpeg package
    p = _sh.which('ffmpeg')
    if p: return p
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()

class NftTpl(BaseModel):
    wall_url: str                      # gallery wall with this character's busts, frame opening filled flat blue
    clip_url: str                      # character on green, 8 s, already joined (walk in, look, smile, walk on)
    opening: list                      # [x0, y0, x1, y1] frame opening in wall-image pixels
    bust_fracs: list = [0.143, 0.857]  # bust centres as fractions of the wall width
    floor_cut: int = 560               # wall-image row where the floor starts (cut away)
    floor_src: int = 500               # wall rows floor_src..floor_cut are stretched down to replace the floor
    char_xywh: list = [401, 188, 1055, 1876]
    stop_shift: int = 30               # stop the wall this many px further along (frame sits left of him)
    key_extend: int = 10               # key area reaches this many px beyond the opening (covers the bevel)
    bevel: int = 8                     # frame inner edge recoloured dark-to-gold over this many px
    t_full_end: float = 1.0            # walk at full speed until here
    t_stop: float = 1.7                # stopped from here
    t_go: float = 6.7                  # starts walking again here
    t_cruise: float = 7.0              # full speed again from here
    duration: float = 8.0
    fps: int = 25
    name: str = 'nft_template'
    put: str = ''                      # Shopify staged upload address (SC - Upload Targets); required since 29 Oct 2026 (Cloudinary retired)
    enc_preset: str = 'veryfast'       # x264 speed/memory trade-off
    enc_threads: int = 0               # 0 = automatic

def _nft_strip(r):
    CH = 1920; KEY = (255, 0, 255); E = r.key_extend
    wall = Image.open(io.BytesIO(requests.get(r.wall_url, timeout=60).content)).convert('RGB')
    sc = CH / wall.height; full = wall.resize((int(wall.width * sc), CH), Image.LANCZOS)
    cut = int(r.floor_cut * sc)
    strip = Image.new('RGB', full.size); strip.paste(full.crop((0, 0, full.width, cut)), (0, 0))
    strip.paste(full.crop((0, int(r.floor_src * sc), full.width, cut)).resize((full.width, CH - cut), Image.BICUBIC), (0, cut))
    x0, y0, x1, y1 = [int(v * sc) for v in r.opening]
    fcx = (x0 + x1) // 2
    x0, y0, x1, y1 = x0 - E, y0 - E, x1 + E, y1 + E
    strip.paste(Image.new('RGB', (x1 - x0, y1 - y0), KEY), (x0, y0))
    S = np.array(strip).astype(np.float32); RW = r.bevel; DARK = np.array([38, 28, 14], np.float32)
    for d in range(RW):
        a = (d + 1) / (RW + 1)
        for xc, xs in ((x0 - 1 - d, x0 - 1 - RW - 3), (x1 + d, x1 + RW + 3)):
            S[y0 - RW:y1 + RW, xc] = DARK * (1 - a) + S[y0 - RW:y1 + RW, xs] * a
        for yc, ys in ((y0 - 1 - d, y0 - 1 - RW - 3), (y1 + d, y1 + RW + 3)):
            S[yc, x0 - 1 - d:x1 + d + 1] = DARK * (1 - a) + S[ys, x0 - 1 - d:x1 + d + 1] * a
    strip = Image.fromarray(S.clip(0, 255).astype(np.uint8)); del S
    P = 600; FW = full.width; del full
    pad = Image.new('RGB', (strip.width + 2 * P, CH))
    pad.paste(ImageOps.mirror(strip.crop((0, 0, P, CH))), (0, 0)); pad.paste(strip, (P, 0))
    pad.paste(ImageOps.mirror(strip.crop((strip.width - P, 0, strip.width, CH))), (P + strip.width, 0))
    A = np.array(pad); del pad, strip
    fc = fcx + P + r.stop_shift
    bl = int(r.bust_fracs[0] * FW) + P; br = int(r.bust_fracs[1] * FW) + P
    PER = br - bl                                  # wall travel per loop = bust-to-bust spacing (loop lands bust on bust)
    k_in = r.t_full_end + (r.t_stop - r.t_full_end) / 2
    k_out = (r.t_cruise - r.t_go) / 2 + (r.duration - r.t_cruise)
    v = PER / (k_in + k_out)
    endc = int(round(fc - v * k_out)); startc = endc + PER
    F = 90; w = A[:, endc - 540:endc + 540].astype(np.float32)
    a = np.ones(1080, np.float32); a[:F] = np.linspace(0, 1, F); a[-F:] = np.linspace(1, 0, F)
    tgt = A[:, startc - 540:startc + 540].astype(np.float32)
    A[:, startc - 540:startc + 540] = (w * a[None, :, None] + tgt * (1 - a[None, :, None])).clip(0, 255).astype(np.uint8)
    geo = {'fc': fc, 'v': v, 'startc': startc, 'open': [x0 + P, y0, x1 + P, y1]}
    return A, geo

def _nft_centre(r, g, t):
    v, fc, sc0 = g['v'], g['fc'], g['startc']
    a, b, c, d = r.t_full_end, r.t_stop, r.t_go, r.t_cruise
    if t < a: return sc0 - v * t
    if t < b: u = t - a; return sc0 - v * a - (v * u - v * u * u / (2 * (b - a)))
    if t < c: return fc
    if t < d: u = t - c; return fc - v * u * u / (2 * (d - c))
    return fc - v * (d - c) / 2 - v * (t - d)

def _cutout(fr, K3=np.ones((3, 3), np.uint8)):
    # green-screen cut-out: per-row background shade, only his figure kept, solid inside his outline, soft 1 px edge
    f = fr.astype(np.float32); fi0 = fr.astype(np.int16)
    gdm = fi0[..., 1] - np.maximum(fi0[..., 0], fi0[..., 2])
    gm = (gdm > 50).astype(np.float32); cnt = gm.sum(1); sm = (f * gm[..., None]).sum(1); good = cnt > 20
    rowbg = np.zeros((f.shape[0], 3), np.float32); idx = np.arange(f.shape[0])
    for c in range(3): rowbg[:, c] = np.interp(idx, idx[good], sm[good, c] / cnt[good])
    rowbg = cv2.blur(rowbg[None, :, :], (31, 1))[0]
    d = np.sqrt(((f - rowbg[:, None, :]) ** 2).sum(-1)); al = np.clip((d - 45) / 30, 0, 1).astype(np.float32)
    num, lab, st, _ = cv2.connectedComponentsWithStats((al > 0.5).astype(np.uint8))
    big = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA])); fig = (lab == big).astype(np.uint8)
    ff = (1 - fig).astype(np.uint8); h, w = ff.shape; msk = np.zeros((h + 2, w + 2), np.uint8)
    for sx, sy in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        if ff[sy, sx] == 1: cv2.floodFill(ff, msk, (sx, sy), 2)
    solid = ((fig == 1) | ((ff == 1) & (gdm < 30))).astype(np.uint8)
    interior = cv2.erode(solid, K3, iterations=3).astype(np.float32)
    edge_al = al * cv2.dilate(solid, K3).astype(np.float32) * (gdm < 45)
    al2 = np.maximum(cv2.erode(edge_al, K3), interior); al2 = cv2.GaussianBlur(al2, (0, 0), 0.7); al2 = np.maximum(al2, interior)
    edge = (al2 > 0.01) & (al2 < 0.99); lim = np.maximum(f[..., 0], f[..., 2]); f[..., 1] = np.where(edge & (f[..., 1] > lim), lim, f[..., 1])
    holes = int(((interior > 0) & (al2 < 0.99)).sum())
    return f, al2, holes

@app.post('/nft-template')
def nft_template(r: NftTpl):
    A, g = _nft_strip(r)
    clip_path = '/tmp/nft_clip_%d.mp4' % int(time.time() * 1000)
    open(clip_path, 'wb').write(requests.get(r.clip_url, timeout=180).content)
    cap = cv2.VideoCapture(clip_path); sfps = cap.get(cv2.CAP_PROP_FPS) or 24.0; nsrc = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    out_path = '/tmp/nft_tpl_%d.mp4' % int(time.time() * 1000)
    enc = _sp.Popen([_ffmpeg(), '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1080x1920', '-r', str(r.fps), '-i', '-',
                     '-c:v', 'libx264', '-preset', r.enc_preset, '-x264-params', 'rc-lookahead=10', '-threads', str(r.enc_threads), '-crf', '12', '-pix_fmt', 'yuv444p', out_path], stdin=_sp.PIPE)
    X, Y, CW, CHh = r.char_xywh; n_out = int(round(r.duration * r.fps))
    cur_i, cur = -1, None; holes_worst = 0; green_worst = 0
    for n in range(n_out):
        t = n / r.fps; want = min(int(round(t * sfps)), nsrc - 1)
        while cur_i < want:
            ok, fr = cap.read()
            if not ok: break
            cur_i += 1; cur = cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)
        cx = int(round(_nft_centre(r, g, t))) - 540
        out = A[:, cx:cx + 1080].copy()
        f, al, holes = _cutout(cur); holes_worst = max(holes_worst, holes)
        rgb = cv2.resize(f, (CW, CHh), interpolation=cv2.INTER_LANCZOS4); M = cv2.resize(al, (CW, CHh))[..., None]
        hh, ww = min(CHh, 1920 - Y), min(CW, 1080 - X)
        reg = out[Y:Y + hh, X:X + ww].astype(np.float32)
        out[Y:Y + hh, X:X + ww] = (rgb[:hh, :ww] * M[:hh, :ww] + reg * (1 - M[:hh, :ww])).clip(0, 255).astype(np.uint8)
        if n % 10 == 0:
            o = out.astype(np.int16); green_worst = max(green_worst, int(((o[..., 1] - np.maximum(o[..., 0], o[..., 2])) > 40).sum()))
        enc.stdin.write(out.tobytes())
    enc.stdin.close(); enc.wait(); cap.release()
    if not r.put: return {'ok': False, 'reason': 'put (Shopify upload address from SC - Upload Targets) is required; Cloudinary retired 29 Oct 2026'}
    _pr = requests.put(r.put, data=open(out_path, 'rb').read(), headers={'Content-Type': 'video/mp4'}, timeout=300)
    up = {'secure_url': 'put:%d' % _pr.status_code} if _pr.status_code < 300 else {}
    for pth in (clip_path, out_path):
        try: import os; os.remove(pth)
        except Exception: pass
    ox, oy, ox1, oy1 = g['open']; side = ox1 - ox
    # NFT position for every frame while the wall moves (json2video renders 25 fps), plus the stop and the end
    times = sorted(set([round(i / r.fps, 3) for i in range(n_out + 1) if (i / r.fps) <= r.t_stop or (i / r.fps) >= r.t_go]))
    kf = [{'time': t, 'x': int(round(ox - (int(round(_nft_centre(r, g, t))) - 540) - 3))} for t in times]
    return {'ok': bool(up.get('secure_url')) and holes_worst == 0 and green_worst < 500,
            'template_url': up.get('secure_url', ''),
            'checks': {'see_through_pixels_inside_character': holes_worst, 'green_pixels_worst_frame': green_worst},
            'nft': {'y': oy - 3, 'size': side + 6, 'keyframes': kf},
            'chroma_key': {'color': '#FF00FF', 'tolerance': 40}, 'fps': r.fps, 'duration': r.duration}

# ---- Media move test (24 Oct 2026): proves this service can build a slide and a clip and put them straight into Shopify Files
# through the upload addresses that SC - File Store hands out. TEST ONLY: no Cloudinary, no keys, no secrets.
class MediaTest(BaseModel):
    image_put: str = ''   # staged upload address for the PNG (from SC - File Store, action targets)
    video_put: str = ''   # staged upload address for the MP4

def _mt_font(size):
    try:
        return ImageFont.load_default(size=size)
    except Exception:
        return ImageFont.load_default()

def _mt_frame(t, W=1080, H=1920):
    bg = Image.new('RGBA', (W, H), (10, 10, 10, 255))
    ch = Image.new('RGBA', (700, 1100), (0, 0, 0, 0)); cd = ImageDraw.Draw(ch)
    cd.ellipse((50, 50, 650, 1050), fill=(200, 60, 60, 255), outline=(255, 255, 255, 255), width=12)
    bg.alpha_composite(ch, (190, 300 + int(40 * t)))
    bg.alpha_composite(Image.new('RGBA', (W, 260), (255, 214, 0, 230)), (0, 1500))
    ImageDraw.Draw(bg).text((60, 1580), 'TEST - SC MEDIA MOVE', font=_mt_font(90), fill=(0, 0, 0, 255))
    return bg.convert('RGB')

@app.post('/media-test')
def media_test(m: MediaTest):
    out = {'ok': True}
    try:
        buf = io.BytesIO(); _mt_frame(0).save(buf, 'PNG'); png = buf.getvalue()
        out['png_bytes'] = len(png)
        if m.image_put:
            r = requests.put(m.image_put, data=png, headers={'Content-Type': 'image/png'}, timeout=120)
            out['image_put_status'] = r.status_code
        path = '/tmp/mt_%d.mp4' % int(time.time() * 1000)
        enc = _sp.Popen([_ffmpeg(), '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1080x1920', '-r', '25', '-i', '-',
                         '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'veryfast', path], stdin=_sp.PIPE)
        for i in range(125):
            enc.stdin.write(np.array(_mt_frame(i / 25.0)).tobytes())
        enc.stdin.close(); enc.wait()
        mp4 = open(path, 'rb').read(); out['mp4_bytes'] = len(mp4)
        if m.video_put:
            r = requests.put(m.video_put, data=mp4, headers={'Content-Type': 'video/mp4'}, timeout=300)
            out['video_put_status'] = r.status_code
        try:
            import os as _os; _os.remove(path)
        except Exception:
            pass
    except Exception as e:
        out['ok'] = False; out['error'] = str(e)[:300]
    return out

# ---- Bucket test (24 Oct 2026): proves a large clip can be stored in the Railway bucket and fetched by public link.
# TEST ONLY. The bucket keys reach this service as Railway variable references; nothing is written into code.
import hashlib as _hl, hmac as _hm, datetime as _dt, urllib.parse as _up, os as _os
def _s3h(k, m): return _hm.new(k, m.encode(), _hl.sha256).digest()
def _s3enc(s): return _up.quote(s, safe='-_.~')
def s3_presign(method, host, key, access, secret, region, expires, now=None, service='s3'):
    """Query-string SigV4 URL (virtual-host style, path = /key). Returns full https URL."""
    t = now or _dt.datetime.utcnow(); amz = t.strftime('%Y%m%dT%H%M%SZ'); ds = t.strftime('%Y%m%d')
    scope = '%s/%s/%s/aws4_request' % (ds, region, service)
    q = {'X-Amz-Algorithm': 'AWS4-HMAC-SHA256', 'X-Amz-Credential': access + '/' + scope, 'X-Amz-Date': amz, 'X-Amz-Expires': str(expires), 'X-Amz-SignedHeaders': 'host'}
    cq = '&'.join('%s=%s' % (_s3enc(k), _s3enc(v)) for k, v in sorted(q.items()))
    path = '/' + '/'.join(_s3enc(p) for p in key.split('/'))
    creq = '\n'.join([method, path, cq, 'host:' + host + '\n', 'host', 'UNSIGNED-PAYLOAD'])
    sts = '\n'.join(['AWS4-HMAC-SHA256', amz, scope, _hl.sha256(creq.encode()).hexdigest()])
    k = _s3h(_s3h(_s3h(_s3h(('AWS4' + secret).encode(), ds), region), service), 'aws4_request')
    sig = _hm.new(k, sts.encode(), _hl.sha256).hexdigest()
    return 'https://%s%s?%s&X-Amz-Signature=%s' % (host, path, cq, sig)


class BucketTest(BaseModel):
    seconds: int = 25
    mbps: int = 8
    key: str = 'TEST/media_test_25mb.mp4'

@app.post('/bucket-test')
def bucket_test(b: BucketTest):
    out = {'ok': True}
    try:
        ep = _os.environ['BUCKET_ENDPOINT']; bk = _os.environ['BUCKET_NAME']; ak = _os.environ['BUCKET_ACCESS_KEY_ID']; sk = _os.environ['BUCKET_SECRET_ACCESS_KEY']; rg = _os.environ.get('BUCKET_REGION', 'auto')
        host = bk + '.' + _up.urlparse(ep).netloc
        path = '/tmp/bt_%d.mp4' % int(time.time() * 1000)
        r = _sp.run([_ffmpeg(), '-y', '-v', 'error', '-f', 'lavfi', '-i', 'color=c=0x202020:s=1080x1920:r=30', '-t', str(b.seconds), '-vf', 'noise=alls=60:allf=t',
                     '-c:v', 'libx264', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-b:v', '%dM' % b.mbps, '-minrate', '%dM' % b.mbps, '-maxrate', '%dM' % b.mbps, '-bufsize', '%dM' % (b.mbps * 2), '-movflags', '+faststart', path], capture_output=True, text=True)
        if r.returncode != 0:
            out['ok'] = False; out['error'] = r.stderr[:300]; return out
        data = open(path, 'rb').read(); out['mp4_bytes'] = len(data)
        put = requests.put(s3_presign('PUT', host, b.key, ak, sk, rg, 900), data=data, headers={'Content-Type': 'video/mp4'}, timeout=600)
        out['put_status'] = put.status_code
        if put.status_code >= 300:
            out['ok'] = False; out['put_body'] = put.text[:300]
        for label, secs in (('url_7d', 604800), ('url_90d', 7776000)):
            u = s3_presign('GET', host, b.key, ak, sk, rg, secs)
            g = requests.get(u, headers={'Range': 'bytes=0-1023'}, timeout=60)
            out[label] = u
            out[label + '_status'] = g.status_code
            out[label + '_type'] = g.headers.get('Content-Type', '')
            out[label + '_total'] = g.headers.get('Content-Range', '')
        try:
            _os.remove(path)
        except Exception:
            pass
    except Exception as e:
        out['ok'] = False; out['error'] = str(e)[:300]
    return out

# ---- Transform (25 Oct 2026): the picture work Cloudinary used to do on the fly, now done here.
# resize = Cloudinary w_<width> (scale to a width, keep proportions); fill = c_fill,w_,h_,b_white (crop to fill the box,
# white behind any transparency); frame = so_<seconds> (one still frame from a clip). The result is PUT to a staged
# Shopify upload address from SC - File Store (action targets), so no key is held here and no bytes pass through n8n.
class Transform(BaseModel):
    src: str                 # public link of the picture or clip
    op: str                  # resize | fill | frame | crop | silent
    width: int = 1000
    height: int = 0          # fill only; 0 = same as width
    at: float = 0.0          # frame only: seconds into the clip
    x: int = 0               # crop only: left edge in pixels
    y: int = 0               # crop only: top edge in pixels
    w: int = 0               # crop only: width in pixels
    h: int = 0               # crop only: height in pixels
    dur: float = 2.5         # pingpong only: seconds of the clip taken from 'at'
    fmt: str = 'jpg'         # jpg | png
    put: str = ''            # staged upload address; empty = return sizes only (test)

def _tf_fetch(url, timeout=120):
    r = requests.get(url, timeout=timeout, stream=True)
    r.raise_for_status()
    return r.content

def _tf_encode(img, fmt):
    buf = io.BytesIO()
    if fmt == 'png':
        img.save(buf, 'PNG', optimize=True); return buf.getvalue(), 'image/png'
    if img.mode != 'RGB':
        bg = Image.new('RGB', img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
        img = bg
    img.save(buf, 'JPEG', quality=90, optimize=True); return buf.getvalue(), 'image/jpeg'

@app.post('/transform')
def transform(t: Transform):
    out = {'ok': True, 'op': t.op}
    try:
        if t.op == 'silent':
            # 29 Oct 2026: copy of a clip with the sound track removed (replaces Cloudinary's ac_none); video is not re-encoded.
            src = '/tmp/tf_%d_src' % int(time.time() * 1000); dst = src + '_mute.mp4'
            open(src, 'wb').write(_tf_fetch(t.src, 600))
            _sp.run([_ffmpeg(), '-y', '-v', 'error', '-i', src, '-c:v', 'copy', '-an', '-movflags', '+faststart', dst], check=True, timeout=600)
            data = open(dst, 'rb').read(); ctype = 'video/mp4'
            for p_ in (src, dst):
                try: _os.remove(p_)
                except Exception: pass
            out.update({'bytes': len(data), 'content_type': ctype})
            if t.put:
                r = requests.put(t.put, data=data, headers={'Content-Type': ctype}, timeout=600)
                out['put_status'] = r.status_code
            return out
        if t.op == 'pingpong':
            # 29 Oct 2026: forward-then-reversed loop of a clip segment (replaces Cloudinary's fl_splice + e_reverse used by the quiz poster).
            # Result = clip[at .. at+dur] followed by the same segment backwards; silent, re-encoded h264.
            src = '/tmp/tf_%d_src' % int(time.time() * 1000); dst = src + '_pp.mp4'
            open(src, 'wb').write(_tf_fetch(t.src, 600))
            fc = '[0:v]trim=start=%s:duration=%s,setpts=PTS-STARTPTS,split[a][b];[b]reverse[r];[a][r]concat=n=2:v=1:a=0[v]' % (t.at, t.dur)
            _sp.run([_ffmpeg(), '-y', '-v', 'error', '-i', src, '-filter_complex', fc, '-map', '[v]', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'veryfast', '-crf', '18', '-movflags', '+faststart', dst], check=True, timeout=600)
            data = open(dst, 'rb').read(); ctype = 'video/mp4'
            for p_ in (src, dst):
                try: _os.remove(p_)
                except Exception: pass
            out.update({'bytes': len(data), 'content_type': ctype})
            if t.put:
                r = requests.put(t.put, data=data, headers={'Content-Type': ctype}, timeout=600)
                out['put_status'] = r.status_code
            return out
        if t.op == 'frame':
            src = '/tmp/tf_%d_src' % int(time.time() * 1000); dst = src + '.png'
            open(src, 'wb').write(_tf_fetch(t.src, 300))
            _sp.run([_ffmpeg(), '-y', '-v', 'error', '-ss', str(t.at), '-i', src, '-frames:v', '1', dst], check=True, timeout=300)
            img = Image.open(dst).convert('RGB')
            for p in (src, dst):
                try: _os.remove(p)
                except Exception: pass
        else:
            img = Image.open(io.BytesIO(_tf_fetch(t.src)))
            img = ImageOps.exif_transpose(img)
            if t.op == 'resize':
                w = max(1, int(t.width)); h = max(1, round(img.height * w / img.width))
                img = img.convert('RGBA' if img.mode in ('RGBA', 'LA', 'P') else 'RGB').resize((w, h), Image.LANCZOS)
            elif t.op == 'fill':
                w = max(1, int(t.width)); h = max(1, int(t.height or t.width))
                img = img.convert('RGBA'); img = ImageOps.fit(img, (w, h), Image.LANCZOS, centering=(0.5, 0.5))
                bg = Image.new('RGBA', (w, h), (255, 255, 255, 255)); bg.alpha_composite(img); img = bg
            elif t.op == 'crop':
                # 29 Oct 2026: pixel crop (x, y, w, h) of the picture as stored (replaces Cloudinary c_crop).
                if t.w <= 0 or t.h <= 0:
                    return {'ok': False, 'error': 'crop needs w and h'}
                img = img.convert('RGBA' if img.mode in ('RGBA', 'LA', 'P') else 'RGB').crop((t.x, t.y, t.x + t.w, t.y + t.h))
                if t.width and t.width != 1000:
                    img = img.resize((t.width, max(1, round(img.height * t.width / img.width))), Image.LANCZOS)
            else:
                return {'ok': False, 'error': 'op must be resize, fill, frame, crop, silent or pingpong'}
        data, ctype = _tf_encode(img, 'png' if t.fmt == 'png' else 'jpg')
        out.update({'width': img.width, 'height': img.height, 'bytes': len(data), 'content_type': ctype})
        if t.put:
            r = requests.put(t.put, data=data, headers={'Content-Type': ctype}, timeout=300)
            out['put_status'] = r.status_code
    except Exception as e:
        out['ok'] = False; out['error'] = str(e)[:300]
    return out

# ---- Dare to Buy pictures (29 Oct 2026): replaces the pictures Cloudinary used to draw on the fly.
# Fixed art lives in the GitHub repo (sc-assets/dtb); the text font is Anton. kind: s3 (title slide: black canvas, character, three or four text
# lines, GET YOURS bar), s2 (framed photo filling a 1080 x 1350 slide), r (framed photo filling the 1080 x 1920 Reel), x (X image 1080 x 1440:
# hook band on top, framed photo under it). The photo may be a Product boxes crop link (a Cloudinary fetch link): it is worked out here from the
# shop picture itself, nothing is requested from Cloudinary.
import re as _re
_DTB_RAW = 'https://raw.githubusercontent.com/StiffCompetition/sc-assets/main/dtb/'
_ANTON = 'https://raw.githubusercontent.com/google/fonts/main/ofl/anton/Anton-Regular.ttf'

def _dtb_file(name, url):
    path = '/tmp/dtb_' + name
    try:
        open(path, 'rb').close()
    except Exception:
        open(path, 'wb').write(_tf_fetch(url, 120))
    return path

def _dtb_asset(name):
    return Image.open(_dtb_file(name, _DTB_RAW + name))

_CLD_CROP = _re.compile(r'^https://res\.cloudinary\.com/dkapdtxek/image/fetch/c_crop,g_xy_center,x_(-?[0-9.]+),y_(-?[0-9.]+),w_([0-9.]+),h_([0-9.]+),fl_relative/(.+)$')

def _dtb_photo(url):
    m = _CLD_CROP.match(url)
    if not m:
        return ImageOps.exif_transpose(Image.open(io.BytesIO(_tf_fetch(url)))).convert('RGB')
    x, y, w, h = [float(m.group(i)) for i in (1, 2, 3, 4)]
    try:
        src = ImageOps.exif_transpose(Image.open(io.BytesIO(_tf_fetch(_up.unquote(m.group(5)))))).convert('RGB')
    except Exception:
        # 29 Oct 2026: some Product Box framings point at Shopify files that were later replaced; Cloudinary still holds the framed copy.
        return ImageOps.exif_transpose(Image.open(io.BytesIO(_tf_fetch(url)))).convert('RGB')
    cw, ch = max(1, round(w * src.width)), max(1, round(h * src.height))
    left = int(-(-(x * src.width - cw / 2) // 1)); top = int(-(-(y * src.height - ch / 2) // 1))
    left = max(0, min(left, src.width - cw)); top = max(0, min(top, src.height - ch))
    return src.crop((left, top, left + cw, top + ch))

class Dtb(BaseModel):
    kind: str                # s3 | s2 | r | x
    photo: str = ''          # s2, r, x: the framed photo (link)
    char: str = ''           # s3: mw ra hh tg sw vp
    gw: int = 1000           # s3: character width in pixels
    gy: int = 45             # s3: character top
    size: int = 112          # s3: text size
    lines: list = []         # s3: [{t: text, c: 'FFFFFF', y: top of the letters}]
    hook: int = 1            # x: hook band number 1 to 8
    put: str = ''            # staged upload address; empty = return sizes only (test)

@app.post('/dtb')
def dtb(t: Dtb):
    out = {'ok': True, 'kind': t.kind}
    try:
        if t.kind == 's3':
            im = _dtb_asset('canvas_black.jpg').convert('RGB')
            ch = _dtb_asset('char_%s.png' % t.char).convert('RGBA')
            ch = ch.resize((t.gw, max(1, round(ch.height * t.gw / ch.width))), Image.LANCZOS)
            im.paste(ch, ((im.width - ch.width) // 2, t.gy), ch)
            f = ImageFont.truetype(_dtb_file('Anton-Regular.ttf', _ANTON), t.size)
            d = ImageDraw.Draw(im)
            for ln in t.lines:
                l, tp, r, b = f.getbbox(ln['t'])
                col = tuple(int(ln['c'][i:i + 2], 16) for i in (0, 2, 4))
                d.text((540 - (l + r) / 2, ln['y'] - tp), ln['t'], font=f, fill=col)
            im.paste(_dtb_asset('bar.png').convert('RGB'), (60, 1200))
        elif t.kind in ('s2', 'r'):
            im = ImageOps.fit(_dtb_photo(t.photo), (1080, 1350 if t.kind == 's2' else 1920), Image.LANCZOS, centering=(0.5, 0.5))
        elif t.kind == 'x':
            p = _dtb_photo(t.photo)
            sw = max(1, round(p.width * 0.012))
            left = p.crop((0, 0, sw, p.height)).resize((1080, 1050), Image.LANCZOS)
            right = p.crop((p.width - sw, 0, p.width, p.height)).resize((540, 1050), Image.LANCZOS)
            base = left.copy(); base.paste(right, (540, 0)); base.paste(p.resize((1050, 1050), Image.LANCZOS), (15, 0))
            im = Image.new('RGB', (1080, 1440), (10, 10, 10)); im.paste(base, (0, 390))
            band = _dtb_asset('xband_%d.png' % t.hook).convert('RGBA'); im.paste(band, (0, 0), band)
        else:
            return {'ok': False, 'error': 'kind must be s3, s2, r or x'}
        data, ctype = _tf_encode(im, 'jpg')
        out.update({'width': im.width, 'height': im.height, 'bytes': len(data), 'content_type': ctype})
        if t.put:
            r = requests.put(t.put, data=data, headers={'Content-Type': ctype}, timeout=300)
            out['put_status'] = r.status_code
    except Exception as e:
        out['ok'] = False; out['error'] = str(e)[:300]
    return out

# ---- Bucket store (25 Oct 2026): files over Shopify's 20 MB limit live in the Railway bucket.
# bucket-put copies a file from one of our own addresses (Cloudinary account or the shop's CDN) into the bucket;
# bucket-link gives a fresh signed read link (max 90 days) for a key already in the bucket. The bucket keys reach
# this service as Railway variable references only.
_BUCKET_OK_SRC = ('https://res.cloudinary.com/dkapdtxek/', 'https://cdn.shopify.com/s/files/1/0661/7428/7966/')

def _bucket():
    ep = _os.environ['BUCKET_ENDPOINT']; bk = _os.environ['BUCKET_NAME']
    return bk + '.' + _up.urlparse(ep).netloc, _os.environ['BUCKET_ACCESS_KEY_ID'], _os.environ['BUCKET_SECRET_ACCESS_KEY'], _os.environ.get('BUCKET_REGION', 'auto')

class BucketPut(BaseModel):
    src: str                 # public link on one of our own addresses
    key: str                 # bucket path, e.g. media/rollcall_comic_pages_v1.mp4
    content_type: str = 'video/mp4'

class BucketLink(BaseModel):
    key: str
    expires: int = 604800    # seconds; 7 days by default, 90 days at most

@app.post('/bucket-put')
def bucket_put(b: BucketPut):
    out = {'ok': True, 'key': b.key}
    try:
        if not b.src.startswith(_BUCKET_OK_SRC):
            return {'ok': False, 'error': 'source must be one of our own addresses'}
        if not b.key or b.key.startswith('/') or '..' in b.key:
            return {'ok': False, 'error': 'bad key'}
        host, ak, sk, rg = _bucket()
        data = _tf_fetch(b.src, 600); out['bytes'] = len(data)
        put = requests.put(s3_presign('PUT', host, b.key, ak, sk, rg, 900), data=data, headers={'Content-Type': b.content_type}, timeout=900)
        out['put_status'] = put.status_code
        if put.status_code >= 300:
            out['ok'] = False; out['put_body'] = put.text[:300]; return out
        chk = requests.get(s3_presign('GET', host, b.key, ak, sk, rg, 300), headers={'Range': 'bytes=0-0'}, timeout=60)
        out['stored_bytes'] = int((chk.headers.get('Content-Range', '/0').split('/')[-1]) or 0)
        out['ok'] = out['stored_bytes'] == len(data)
    except Exception as e:
        out['ok'] = False; out['error'] = str(e)[:300]
    return out

@app.post('/bucket-link')
def bucket_link(b: BucketLink):
    try:
        if not b.key or b.key.startswith('/') or '..' in b.key:
            return {'ok': False, 'error': 'bad key'}
        host, ak, sk, rg = _bucket()
        secs = max(60, min(int(b.expires), 7776000))
        return {'ok': True, 'key': b.key, 'expires': secs, 'url': s3_presign('GET', host, b.key, ak, sk, rg, secs)}
    except Exception as e:
        return {'ok': False, 'error': str(e)[:300]}

# ---- Media info (25 Oct 2026): duration of a stored sound or clip, which Cloudinary used to report on upload.
class MediaInfo(BaseModel):
    src: str

@app.post('/media-info')
def media_info(m: MediaInfo):
    try:
        path = '/tmp/mi_%d' % int(time.time() * 1000)
        open(path, 'wb').write(_tf_fetch(m.src, 300))
        r = _sp.run([_ffmpeg(), '-hide_banner', '-i', path], capture_output=True, text=True, timeout=120)
        try: _os.remove(path)
        except Exception: pass
        import re as _re
        mm = _re.search(r'Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)', r.stderr)
        if not mm: return {'ok': False, 'error': 'no duration found'}
        d = int(mm.group(1)) * 3600 + int(mm.group(2)) * 60 + float(mm.group(3))
        return {'ok': True, 'duration': round(d, 3)}
    except Exception as e:
        return {'ok': False, 'error': str(e)[:300]}
