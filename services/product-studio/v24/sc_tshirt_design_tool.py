"""SC t-shirt character design tool (Hammerin' Hanky standard).

Steps for one character (see README):
  1. upscale  : enlarge the approved character picture 4x with Real-ESRGAN, saved at 2x  (gets the picture past 300 dpi)
  2. lift     : remove side shadow on the face by lifting the darker side to match the lit side (brightness only)
  3. build    : cut to Hanky's height, place on Hanky's lines, set the phrase, add the lockup, save both ink versions
  4. check    : measure the design against Hanky; every check must pass before Andy sees it

Usage:
  python3 sc_tshirt_design_tool.py upscale <in.jpg> <out.png> <x0,y0,x1,y1>
  python3 sc_tshirt_design_tool.py lift    <in.png> <out.png> <face_centre_x> <x0,x1,y0,y1> <k>
  python3 sc_tshirt_design_tool.py make    <character.json>          (build + check; prints PASS/FAIL per check)

Assets in the same folder as this file: lockup.png (lockup, 1-bit, print size), alfa.ttf (Alfa Slab One),
RealESRGAN_x4plus.pth (only for upscale). Needs: pillow, numpy, scipy; torch + spandrel for upscale.
"""
import sys, os, json, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, 'alfa.ttf')
LOCKUP = os.path.join(HERE, 'lockup.png')
W, H = 3600, 4800                     # Gelato front print file, 12 x 16 in at 300 dpi

# Hammerin' Hanky: measured from his approved print. The standard every character is built to.
HH = dict(char_w=2597, char_top=344, char_h=2876, text_top=3412, lock_top=4100,
          eye_gap=283, eye_mouth=254, gap_text=192, line_gap=62, gap_lock=142, lock_frac=0.50,
          light_bands=dict(brow=30.6, cheek=35.0, jaw=45.0))   # measured on Hanky's 18 Oct 2026 print
INK_DARK_SHIRT, INK_LIGHT_SHIRT, LOCK_LIGHT_SHIRT = 242, 17, 0

# Set layout (Andy, 18 Oct 2026): picture, character NAME line, two-line phrase, lockup. Every shirt in the set uses
# the same lines. Text is never spread out: each phrase line is sized to fill the character width with normal letter
# spacing; if the two lines are taller than the phrase area, both shrink by the same factor and are centred.
_k = 2820/2876                                   # picture made 2% smaller than Hanky's first print to make room for the name
HH.update(char_top=300, char_h=2820, char_w=round(2597*_k), eye_gap=283*_k, eye_mouth=254*_k)
LAY = dict(gap_text=120, name_h=150, name_gap=60, line_gap=62, gap_lock=100, lock_frac=0.45, bottom=300, track=0.06)

def lum(a): return 0.299*a[..., 0] + 0.587*a[..., 1] + 0.114*a[..., 2]
def skin_mask(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return (r > g + 15) & (g > b) & (r > 90) & (a[..., :3].min(axis=2) < 235)
def hsv_sat(a):
    mx, mn = a[..., :3].max(axis=2), a[..., :3].min(axis=2)
    return np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)

# ---------- 1. upscale ----------
def upscale(src, out, box, keep=2):
    import torch
    from spandrel import ModelLoader
    m = ModelLoader().load_from_file(os.path.join(HERE, 'RealESRGAN_x4plus.pth')).eval()
    im = np.asarray(Image.open(src).convert('RGB').crop(box)).astype(np.float32) / 255
    h, w, _ = im.shape; S, T, O = 4, 256, 16
    res = np.zeros((h*S, w*S, 3), np.float32)
    for y in range(0, h, T):
        for x in range(0, w, T):
            y0, x0, y1, x1 = max(y-O, 0), max(x-O, 0), min(y+T+O, h), min(x+T+O, w)
            t = torch.from_numpy(im[y0:y1, x0:x1]).permute(2, 0, 1)[None]
            with torch.no_grad(): r = m(t)[0].permute(1, 2, 0).clamp(0, 1).numpy()
            hh, ww = (min(y+T, h)-y)*S, (min(x+T, w)-x)*S
            res[y*S:y*S+hh, x*S:x*S+ww] = r[(y-y0)*S:(y-y0)*S+hh, (x-x0)*S:(x-x0)*S+ww]
        print(f'row {y//T+1}/{(h+T-1)//T}', flush=True)
    x4 = Image.fromarray((res*255 + 0.5).astype(np.uint8))
    x2 = x4 if keep == 4 else x4.resize((x4.width*keep//4, x4.height*keep//4), Image.LANCZOS); x2.save(out)   # keep 3 for broad characters (wider on the shirt, needs more pixels for 300 dpi)
    orig = np.asarray(Image.open(src).convert('RGB').crop(box)).astype(float)
    back = np.asarray(x2.resize((orig.shape[1], orig.shape[0]), Image.LANCZOS)).astype(float)
    print('likeness check: PSNR %.1f dB (35+ = nothing redrawn)' % (10*np.log10(255**2/((orig-back)**2).mean())))

# ---------- 2. face lighting ----------
def lift(A, cx, box, k=1.0):
    LA = lum(A); low = ndi.gaussian_filter(LA, 35*k)
    x0, x1, y0, y1 = box; reg = low[y0:y1, x0:x1]; Wd = x1 - x0; c = cx - x0
    mir = np.array([reg[:, 2*c-j] if 0 <= 2*c-j < Wd else reg[:, j] for j in range(Wd)]).T
    add = np.zeros_like(LA); add[y0:y1, x0:x1] = np.maximum(reg, mir) - reg
    add = ndi.gaussian_filter(add, 25*k)
    m = np.zeros(LA.shape); e = int(20*k); m[y0+e:y1-e, x0+e:x1-e] = 1; m = ndi.gaussian_filter(m, 30*k)
    add = add * m * ndi.gaussian_filter((A.min(axis=2) < 235).astype(float), 3*k)
    gain = 1 + add/np.maximum(low, 1)   # gain from the smoothed light, so dark details (pupils, brows) brighten only as much as the skin round them (22 Oct 2026: the old per-pixel gain turned a pupil grey)
    return np.clip((A - LA[..., None])*np.sqrt(gain)[..., None] + (LA*gain)[..., None], 0, 255)

# ---------- 3. build ----------
def cutout(im, k=1):
    a = np.asarray(im.convert('RGBA')).astype(float)
    if im.mode == 'RGBA' and a[..., 3].min() < 10:   # picture already cut out (transparent background): defringe only
        _, (iy, ix) = ndi.distance_transform_edt(~(a[..., 3] >= 250), return_indices=True)
        return np.dstack([a[..., :3][iy, ix], a[..., 3]])
    # background colour read from the corners (pure white, or plain grey for white-costume characters such as a white cap)
    bg = np.median(np.concatenate([a[:20, :20, :3].reshape(-1, 3), a[:20, -20:, :3].reshape(-1, 3)]), axis=0)
    cand = (np.abs(a[..., :3] - bg).max(axis=2) <= 30) if bg.min() < 225 else (a[..., :3].min(axis=2) >= 225)
    lab, _ = ndi.label(cand)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    fg = ndi.binary_erosion(~np.isin(lab, list(edge)), iterations=int(4*k))
    alpha = np.asarray(Image.fromarray((fg*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2*k))).astype(float)
    _, (iy, ix) = ndi.distance_transform_edt(~(alpha >= 250), return_indices=True)   # defringe
    return np.dstack([a[..., :3][iy, ix], alpha])

def match_skin(arr, ref_sat):
    rgb = arr[..., :3]; m = skin_mask(rgb) & (arr[..., 3] > 200)
    cur = np.median(hsv_sat(rgb)[m]); k = np.clip(ref_sat/max(cur, 1e-3), 0.9, 1.25)
    L = lum(rgb)[..., None]; sk = ndi.gaussian_filter(m.astype(float), 3)[..., None]
    arr[..., :3] = np.clip(L + (rgb - L)*(1 + (k - 1)*sk), 0, 255)
    return arr, cur, k

def _line(t, sz):
    """One line drawn with normal letter spacing (LAY track x size between letters). Returns the cropped ink image."""
    f = ImageFont.truetype(FONT, sz); ws = [ImageDraw.Draw(Image.new('L', (1, 1))).textlength(x, font=f) for x in t]
    wid = int(sum(ws) + (len(t) - 1)*LAY['track']*sz) + 4
    Lr = Image.new('L', (wid, int(sz*1.6))); dl = ImageDraw.Draw(Lr); x = 0
    for ch_, w_ in zip(t, ws): dl.text((x, int(sz*0.2)), ch_, font=f, fill=255); x += w_ + LAY['track']*sz
    a = np.asarray(Lr); rr = np.where(a.max(axis=1) > 40)[0]; cc = np.where(a.max(axis=0) > 40)[0]
    return Lr.crop((cc.min(), rr.min(), cc.max() + 1, rr.max() + 1))

def _fit(t, width):
    """Largest size at which the line, with normal spacing, fills the width."""
    sz = 1200
    while _line(t, sz).width > width: sz = int(sz*min(0.99, width/_line(t, sz).width + 0.005))
    while _line(t, sz + 1).width <= width: sz += 1
    return sz

def text_layout(lines, name, lock_h):
    """Fixed set lines: name band, phrase area, lockup. Phrase lines fill the width, never stretched."""
    cw = HH['char_w']; y0 = HH['char_top'] + HH['char_h'] + LAY['gap_text']
    lock_top = H - LAY['bottom'] - lock_h
    ph_top = y0 + LAY['name_h'] + LAY['name_gap']; ph_h = lock_top - LAY['gap_lock'] - ph_top
    sizes = [_fit(t, cw) for t in lines]; imgs = [_line(t, z) for t, z in zip(lines, sizes)]
    # never shrunk, never stretched: a phrase whose full-width lines are too tall for the area FAILS the phrase check
    # and is reworded (longer lines) with Andy before any picture is made
    tot = sum(i.height for i in imgs) + LAY['line_gap']*(len(imgs) - 1); scale = 1.0 if tot <= ph_h else ph_h/tot
    ys, y = [], ph_top + max(0, ph_h - tot)//2
    for i in imgs: ys.append(y); y += i.height + LAY['line_gap']
    nsz = None; nimg = None
    if name:
        nsz = 400
        while _line(name, nsz).height > LAY['name_h'] or _line(name, nsz).width > cw: nsz -= 2
        nimg = _line(name, nsz)
    return dict(sizes=sizes, imgs=imgs, ys=ys, name_size=nsz, name_img=nimg, name_y=y0 + (LAY['name_h'] - (nimg.height if nimg else 0))//2,
                ph_top=ph_top, ph_bottom=ph_top + ph_h, lock_top=lock_top, scale=scale, name_top=y0)

def draw_text(C, G, ink):
    for im, y in zip(G['imgs'], G['ys']):
        C.alpha_composite(Image.merge('RGBA', (Image.new('L', im.size, ink),)*3 + (im,)), ((W - im.width)//2, y))
    if G['name_img'] is not None:
        im = G['name_img']; C.alpha_composite(Image.merge('RGBA', (Image.new('L', im.size, ink),)*3 + (im,)), ((W - im.width)//2, G['name_y']))

def build(c, outdir):
    src = Image.open(c['src']); src = src if src.mode == 'RGBA' else src.convert('RGB')
    ref = np.asarray(Image.open(c['skin_ref']).convert('RGB').crop(tuple(c['skin_ref_box']))).astype(float)
    ref_sat = np.median(hsv_sat(ref)[skin_mask(ref)])
    def make(cut):
        arr = cutout(src.crop((0, 0, src.width, cut)), c.get('k', 1))
        arr, sb, k = match_skin(arr, ref_sat)
        ys, xs = np.where(arr[..., 3] > 30); x0, y0 = xs.min(), ys.min()
        arr = arr[y0:ys.max()+1, x0:xs.max()+1]
        # broad characters (fit 'broad'): width out to the safe margin so the face stays Hanky's size; the cut then extends to Hanky's height
        if c.get('fit') == 'face':   # face fit: face at Hanky's size (eye gap), width kept between Hanky's and the safe margin
            eg = c['eyes'][1][0] - c['eyes'][0][0]
            s = min(max(HH['eye_gap']*c.get('face_adjust', 1)/eg, HH['char_w']/arr.shape[1]), (W - 600)/arr.shape[1])   # face_adjust: trim when the mouth sits low (big smile)
        else:
            s = (W - 600)/arr.shape[1] if c.get('fit') == 'broad' else HH['char_w']/arr.shape[1]
        ch = Image.fromarray(arr.astype(np.uint8), 'RGBA').resize((int(arr.shape[1]*s), int(arr.shape[0]*s)), Image.LANCZOS)
        a2 = np.asarray(ch).copy(); fade = int(ch.height*0.07)
        if src.mode != 'RGBA':   # a pre-cut picture already carries its fade
            a2[-fade:, :, 3] = (a2[-fade:, :, 3]*np.linspace(1, 0, fade)[:, None]).astype(np.uint8)
        ch = Image.fromarray(a2); r = np.where(np.asarray(ch.getchannel('A')).max(axis=1) > 40)[0]
        return ch, (x0, y0, s), r.min(), r.max() + 1 - r.min(), sb, k
    cut = c['cut']
    for _ in range(12):            # extend the cut until the figure is Hanky's height
        ch, (x0, y0, s), off, hgt, sb, k = make(cut)
        if abs(hgt - HH['char_h']) <= 4: break
        cut = min(int(cut + (HH['char_h'] - hgt)/s), src.height)
    eyes = [((ex - x0)*s, (ey - y0)*s) for ex, ey in c['eyes']]
    # a picture that cannot reach Hanky's height (a wide character) sits on Hanky's bottom line, so text and lockup stay on his lines
    top, left = HH['char_top'] + max(0, HH['char_h'] - hgt) - off, (W - ch.width)//2
    meta = dict(fit_height=c.get('fit') in ('broad', 'face'), dpi=300/s, cut=cut, eye_gap=eyes[1][0]-eyes[0][0], eye_y=top + np.mean([e[1] for e in eyes]),
                eye_cx=left + np.mean([e[0] for e in eyes]), sat_ref=ref_sat, sat_before=sb, sat_gain=k)
    cw = HH['char_w']
    la = Image.open(LOCKUP).convert('L'); lw = int(cw*LAY['lock_frac'])
    la = la.resize((lw, int(la.height*lw/la.width)), Image.LANCZOS)
    G = text_layout(c['lines'], c.get('name', ''), la.height)
    meta.update(text_sizes=G['sizes'], name_size=G['name_size'], text_scale=G['scale'], track=LAY['track'], has_name=bool(c.get('name')),
                ph_top=G['ph_top'], ph_bottom=G['ph_bottom'], lock_top=G['lock_top'], name_top=G['name_top'], line_w=[i.width for i in G['imgs']])
    out = {}
    for dark, name in ((True, 'lightink_for_dark_shirt'), (False, 'darkink_for_light_shirt')):
        C = Image.new('RGBA', (W, H), (0, 0, 0, 0)); C.alpha_composite(ch, (left, top))
        ink = INK_DARK_SHIRT if dark else INK_LIGHT_SHIRT
        draw_text(C, G, ink)
        lv = INK_DARK_SHIRT if dark else LOCK_LIGHT_SHIRT
        L = Image.merge('RGBA', (Image.new('L', la.size, lv),)*3 + (la,))
        C.alpha_composite(L, ((W - lw)//2, G['lock_top']))
        p = os.path.join(outdir, f"{c['key']}_{name}.png"); C.save(p, dpi=(300, 300)); out[name] = C
    return out, meta

# ---------- 4. check ----------
def bands_on(arr, cx, eye_y, unit):
    res = {}; w = int(unit*0.85)
    for nm, (t, b) in {'brow': (-0.45, -0.1), 'cheek': (0.1, 0.6), 'jaw': (0.6, 1.25)}.items():
        y0, y1 = int(eye_y + t*unit), int(eye_y + b*unit); v = []
        for xa, xb in ((cx - w, cx - int(unit*0.1)), (cx + int(unit*0.1), cx + w)):
            s = arr[y0:y1, int(xa):int(xb)]; m = skin_mask(s)
            v.append(np.percentile(lum(s)[m], 40) if m.mean() >= 0.25 else None)
        # a band mostly covered by costume (a mask, a hat brim) has no skin to compare and is left out
        res[nm] = abs(v[0] - v[1])/max(v)*100 if None not in v else None
    return res

def check(out, meta):
    P = out['lightink_for_dark_shirt']; a = np.asarray(P).astype(float); al = a[..., 3]
    rows = np.where(al.max(axis=1) > 40)[0]; cols = np.where(al.max(axis=0) > 40)[0]
    e = np.diff(np.concatenate([[0], (al.max(axis=1) > 40).astype(int), [0]]))
    blocks = [(s_, t_) for s_, t_ in zip(np.where(e == 1)[0], np.where(e == -1)[0]) if t_ - s_ > 8]
    char_end = blocks[0][1]
    if meta.get('has_name'): nm_, l1, l2, lock = blocks[1], blocks[2], blocks[3], blocks[4]
    else: nm_ = None; l1, l2, lock = blocks[1], blocks[2], blocks[3]
    wh = Image.new('RGBA', P.size, (255, 255, 255, 255)); wh.alpha_composite(P); wa = np.asarray(wh.convert('RGB')).astype(float)
    cx, ey = int(meta['eye_cx']), int(meta['eye_y'])
    reg = wa[ey+40:ey+420, cx-200:cx+200]; rr = np.where((reg.min(axis=2) > 215).sum(axis=1) > 15)[0]
    # closed mouth (a stern face, 22 Oct 2026): no teeth near the mouth line, so the face is sized by the eyes alone;
    # before this the first white below the face (a collar) was taken for teeth and the face read 20% too big
    closed = len(rr) == 0 or 40 + rr.min() > 1.3*HH['eye_mouth']
    unit = HH['eye_mouth']*meta['eye_gap']/HH['eye_gap'] if closed else 40 + (rr.min() + rr.max())/2   # eye line to the middle of the teeth
    lb = bands_on(wa, cx, ey, unit); face = meta['eye_gap']/HH['eye_gap'] if closed else (meta['eye_gap']/HH['eye_gap'] + unit/HH['eye_mouth'])/2
    zone = np.zeros(al.shape, bool); zone[rows.min():int(char_end - 0.08*(char_end - rows.min())), :] = True
    solid = al >= 250; semi = (al > 20) & (al < 230) & zone
    _, (iy, ix) = ndi.distance_transform_edt(~solid, return_indices=True)
    bgc = np.array([22, 22, 27.]); A = (al/255)[..., None]
    rim = np.percentile((lum(A*a[..., :3] + (1-A)*bgc) - lum(A*a[..., :3][iy, ix] + (1-A)*bgc))[semi], 95)
    C = []
    def chk(n, ok, v): C.append((n, bool(ok), v))
    chk('picture at least 300 dpi at print size', meta['dpi'] >= 300, f"{meta['dpi']:.0f} dpi")
    chk('picture top and height = Hanky (±10)', abs(rows.min()-HH['char_top']) <= 10 and abs(char_end-rows.min()-HH['char_h']) <= 10,
        f"top {rows.min()}, height {char_end-rows.min()}")
    chk("character name on the set's name line", (nm_ is not None and nm_[0] >= meta['name_top'] - 4 and nm_[1] <= meta['name_top'] + LAY['name_h'] + 4) if meta.get('has_name') else False,
        f"{nm_[0]}-{nm_[1]}" if nm_ else 'missing')
    chk("phrase inside the set's phrase area", l1[0] >= meta['ph_top'] - 4 and l2[1] <= meta['ph_bottom'] + 4, f"{l1[0]}-{l2[1]}")
    chk("lockup on the set's line (±4)", abs(lock[0] - meta['lock_top']) <= 4, f"{lock[0]}")
    # letters are never spread out: normal spacing always; the widest phrase line fills the width unless the area forced a shrink
    wmax = max(meta['line_w']); full = abs(wmax - HH['char_w']) <= 12
    chk('phrase fills the width with normal letter spacing (never stretched, never shrunk)', meta['track'] <= 0.07 and full and meta['text_scale'] >= 1,
        f"spacing {meta['track']:.2f} em, widest line {wmax} of {HH['char_w']}, scale {meta['text_scale']:.2f}")
    chk('face size within 10% of Hanky', abs(face - 1) <= 0.10, f"{face*100:.0f}%")
    wd = cols.max()-cols.min()
    chk('character width = Hanky (broad characters: at least Hanky, inside the margins)', (abs(wd - HH['char_w']) <= 10) if not meta.get('fit_height') else (HH['char_w'] - 10 <= wd <= W - 600 + 10), f"{wd}")
    chk('line gap = set', abs((l2[0]-l1[1]) - LAY['line_gap']) <= 6, f"{l2[0]-l1[1]}")
    chk('margins at least 300 px', rows.min() >= 300 and H-rows.max() >= 300 and cols.min() >= 300 and W-cols.max() >= 300,
        f"top {rows.min()} bottom {H-rows.max()}")
    chk("skin colour matches own smiling reference", abs(meta['sat_before']*meta['sat_gain'] - meta['sat_ref']) <= 0.04,
        f"{meta['sat_before']*meta['sat_gain']:.2f} vs {meta['sat_ref']:.2f}")
    chk('face lighting no more one-sided than Hanky', all(lb[k] is None or lb[k] <= HH['light_bands'][k] + 2 for k in lb) and sum(v is not None for v in lb.values()) >= 2,
        ', '.join(f"{k} {lb[k]:.0f}%" if lb[k] is not None else f"{k} covered" for k in lb))
    chk('no light rim at edges on a dark shirt', rim <= 8, f"{rim:.1f}")
    return C


# ---------- 5. sheets (only written when every check passes) ----------
def set_lines(meta):
    return {'picture top': HH['char_top'], 'picture bottom': HH['char_top'] + HH['char_h'], 'name top': meta['name_top'],
            'name bottom': meta['name_top'] + LAY['name_h'], 'phrase area top': meta['ph_top'], 'phrase area bottom': meta['ph_bottom'],
            'lockup top': meta['lock_top'], 'bottom margin': H - LAY['bottom']}
def sheets(out, meta, c, outdir):
    def prev(P):
        bg = Image.new('RGBA', P.size, (25, 25, 30, 255)); bg.alpha_composite(P); return bg.convert('RGB')
    hh = Image.open(os.path.join(HERE, 'HH', 'HH_lightink_for_dark_shirt.png'))
    s = 0.25; Wd, Hd = int(W*s), int(H*s)
    sh = Image.new('RGB', (Wd*2 + 20, Hd), (90, 90, 90))
    sh.paste(prev(hh).resize((Wd, Hd)), (0, 0)); sh.paste(prev(out['lightink_for_dark_shirt']).resize((Wd, Hd)), (Wd + 20, 0))
    d = ImageDraw.Draw(sh)
    for n, y in set_lines(meta).items():
        d.line([(0, y*s), (sh.width, y*s)], fill=(0, 220, 255), width=1); d.text((4, y*s - 12), n, fill=(0, 220, 255))
    for x in ((W - HH['char_w'])//2, (W + HH['char_w'])//2):
        for o in (0, Wd + 20): d.line([(o + x*s, 0), (o + x*s, Hd)], fill=(255, 80, 200), width=1)
    sh.save(os.path.join(outdir, 'COMPARISON_' + c['key'] + '.jpg'), quality=90)
    # likeness sheet: the face on the design beside the character's own smiling reference, same size
    P = prev(out['lightink_for_dark_shirt']); cx, ey, g = meta['eye_cx'], meta['eye_y'], meta['eye_gap']
    face = P.crop((int(cx - 2.2*g), int(ey - 1.8*g), int(cx + 2.2*g), int(ey + 2.6*g))).resize((700, 700))
    ref = Image.open(c['skin_ref']).convert('RGB'); ref.thumbnail((700, 700))
    ls = Image.new('RGB', (1420, 700), (90, 90, 90)); ls.paste(face, (0, 0)); ls.paste(ref, (720, 0))
    ls.save(os.path.join(outdir, 'LIKENESS_' + c['key'] + '.jpg'), quality=90)

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'upscale':
        upscale(sys.argv[2], sys.argv[3], tuple(int(v) for v in sys.argv[4].split(',')), int(sys.argv[5]) if len(sys.argv) > 5 else 2)
    elif cmd == 'lift':
        A = np.asarray(Image.open(sys.argv[2]).convert('RGB')).astype(float)
        box = tuple(int(v) for v in sys.argv[5].split(','))
        Image.fromarray(lift(A, int(sys.argv[4]), box, float(sys.argv[6])).astype(np.uint8)).save(sys.argv[3])
    elif cmd == 'phrase':
        # FIRST check, free, before any picture: both lines at full width with normal spacing must fit the phrase area
        lines = sys.argv[2].split('/'); la = Image.open(LOCKUP); lh = int(la.height*int(HH['char_w']*LAY['lock_frac'])/la.width)
        G = text_layout([t.strip() for t in lines], '', lh); tot = sum(i.height for i in G['imgs']) + LAY['line_gap']
        ok = G['scale'] >= 1
        print(('PASS' if ok else 'FAIL') + f" phrase fits at full width — block {tot} px, area {G['ph_bottom'] - G['ph_top']} px, sizes {G['sizes']}")
        if not ok: print('Reword the phrase with Andy (longer lines) before any picture is made.')
        sys.exit(0 if ok else 1)
    elif cmd in ('precheck', 'make'):
        # precheck: run on the generated picture BEFORE any upscale. Every check except resolution must pass,
        #           otherwise the picture is rejected and nothing else is done.
        # make:     run on the upscaled picture. Every check must pass. Only then is the comparison sheet written.
        c = json.load(open(sys.argv[2])); base = os.path.dirname(os.path.abspath(sys.argv[2]))
        if cmd == 'precheck':
            c['src'], c['eyes'], c['k'] = c['raw'], c['raw_eyes'], 1
            if 'raw_cut' in c: c['cut'] = c['raw_cut']
            outdir = os.path.join(base, 'precheck'); os.makedirs(outdir, exist_ok=True)
        else:
            outdir = base
        for k in ('src', 'skin_ref'): c[k] = os.path.join(base, c[k])
        for f in ('COMPARISON_' + c['key'] + '.jpg', 'LIKENESS_' + c['key'] + '.jpg'):
            if os.path.exists(os.path.join(outdir, f)): os.remove(os.path.join(outdir, f))
        out, meta = build(c, outdir)
        res = check(out, meta)
        if cmd == 'precheck':   # forecast the final resolution: raw picture x prep scale (before upscale) x upscale keep factor
            f = c.get('prep_scale', 1) * c.get('keep', 2); d = meta['dpi'] * f
            res = [r for r in res if not r[0].startswith('picture at least 300 dpi')]
            res.insert(0, (f"forecast at least 300 dpi after upscale (prep {c.get('prep_scale', 1)} x keep {c.get('keep', 2)})", d >= 300, f"{d:.0f} dpi"))
        for n, ok, v in res: print(('PASS ' if ok else 'FAIL ') + n + ' — ' + v)
        print('text sizes', meta['text_sizes'], '| cut at', meta['cut'])
        ok_all = all(ok for _, ok, _ in res)
        if ok_all:
            sheets(out, meta, c, outdir)
            print('ALL PASS — comparison and likeness sheets written to', outdir)
        else:
            print('NOT PASSED — stop. Nothing is shown to Andy and no further step runs.')
        sys.exit(0 if ok_all else 1)
