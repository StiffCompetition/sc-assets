"""SC model pictures, t-shirt step: the model chat's build2.py (updated 19 Oct 2026, from the build code doc); job-folder paths and sizes are parameters."""
import sys, re, numpy as np
from PIL import Image
from scipy import ndimage as ndi
import sc_print_on_model as sp


BG = {'pink': ((255,110,170),(240,60,130)), 'sky': ((120,205,255),(60,150,240)),
      'orange': ((255,170,60),(255,120,20)), 'aqua': ((90,235,225),(20,180,190)),
      'purple': ((170,120,255),(110,60,220))}


def lum(a): return 0.299*a[...,0] + 0.587*a[...,1] + 0.114*a[...,2]


def grad_bg(W, H, name):
    c1, c2 = BG[name]
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    d = np.hypot((xx - W/2)/(W*0.8), (yy - H*0.42)/(H*0.75)); t = np.clip(d, 0, 1)[..., None]
    return np.array(c1)*(1 - t) + np.array(c2)*t


def torso_measure(m, collar):
    """The shirt on this photo, measured at the same points Gelato's mock-up is measured: the shoulder seams (where each
    sleeve joins the body) give the shirt's width and centre line. Each side's seam is the outermost column of the shoulder
    whose shirt runs down to the hem; beyond it only the sleeve and arm remain. Returns centre, width, hem row."""
    rows = np.where(m.any(axis=1))[0]; hem = int(rows.max())
    W = m.shape[1]
    reach = np.array([(np.where(m[:, x])[0].max() if m[:, x].any() else 0) for x in range(W)])
    tops = np.array([(np.where(m[:, x])[0].min() if m[:, x].any() else 10**6) for x in range(W)])
    body = (reach >= hem - 0.12*(hem - collar)) & (tops < collar + 0.25*(hem - collar))
    xs = np.where(body)[0]
    runs = np.split(xs, np.where(np.diff(xs) > 1)[0] + 1); big = max(runs, key=len)
    return (big[0] + big[-1])/2.0, float(big[-1] - big[0] + 1), hem

LAST = {}

def build(key, base, target, printfile, bg, out, chest_cm=53.0, below_in=2.0, print_w_cm=30.48, work='.', collar_px=None, hood_tip=None, hood_poly=None, hood_w=None, cords=None, pa_w_frac=None, pa_top_frac=None):
    img = Image.open(base).convert('RGB'); a = np.asarray(img).astype(float); H, W = a.shape[:2]
    # despill: remove green light bounced onto the subject (skin and hair never have green above red and blue)
    a[..., 1] = np.minimum(a[..., 1], np.maximum(a[..., 0], a[..., 2]))
    # edge band: next to the green screen, pull green down to the red/blue average (removes the olive halo on hair)
    _gs0 = img_raw_gs = (np.asarray(img).astype(float)[..., 1] - np.maximum(np.asarray(img).astype(float)[..., 0], np.asarray(img).astype(float)[..., 2]))
    _bg0 = _gs0 > 0.5*np.median(_gs0[:150, :150])
    _band = ndi.binary_dilation(_bg0, iterations=14) & ~_bg0
    a[..., 1] = np.where(_band, np.minimum(a[..., 1], 0.82*(a[..., 0] + a[..., 2])/2), a[..., 1])
    bgcol = np.median(np.asarray(img).astype(float)[:150, :150].reshape(-1, 3), axis=0)
    ab = np.dstack([ndi.gaussian_filter(a[..., c], 1.2) for c in range(3)])
    r, g, b = ab[..., 0], ab[..., 1], ab[..., 2]
    mg = (r + b)/2 - g
    cand = (mg > 60) & (r > g + 50) & (b > g + 50)
    PAD = 16
    cp = np.pad(cand, PAD, mode='edge')
    cp = ndi.binary_opening(cp, iterations=2); cp = ndi.binary_closing(cp, iterations=6)
    cand = cp[PAD:-PAD, PAD:-PAD]
    lab, n = ndi.label(cand)
    cx0 = W//2
    lbl = lab[int(H*0.62), cx0]
    if lbl == 0: raise SystemExit('no shirt at chest centre')
    m = ndi.binary_fill_holes(lab == lbl)
    _cols = m[:, W//2-12:W//2+13]; collar0 = int(np.median([int(np.argmax(_cols[:, i])) for i in range(_cols.shape[1]) if _cols[:, i].any()]))
    neck = np.zeros((H, W), bool); neck[:collar0 + 70, W//2 - 320:W//2 + 320] = True
    loose = (mg > 25) & (r > g + 15) & (b > g + 15) & ~neck
    loose = ndi.binary_closing(np.pad(loose, PAD, mode='edge'), iterations=3)[PAD:-PAD, PAD:-PAD]
    ll, ln = ndi.label(loose)
    keep = np.unique(ll[ndi.binary_dilation(m, iterations=3) & (ll > 0)])
    m = ndi.binary_fill_holes(m | np.isin(ll, keep[keep > 0]))
    st = (mg > 35) & (r > g + 30) & (b > g + 20) & ~neck
    sl, sn = ndi.label(st)
    sk = np.unique(sl[ndi.binary_dilation(m, iterations=4) & (sl > 0)])
    m = ndi.binary_fill_holes(m | np.isin(sl, sk[sk > 0]))
    m = m | ((mg > 45) & (r > g + 40) & (b > g + 30) & ~neck & ndi.binary_dilation(m, iterations=150))
    # shade and shadow on the shirt (dark or deep magenta): skin and hair never have blue above green
    _extra = ((b > g + 6) & (r > g + 12)) | ((r > g*1.3 + 2) & (b > g*1.0) & (lum(ab) < 120))
    _el, _en = ndi.label(_extra)
    _ek = np.unique(_el[ndi.binary_dilation(m, iterations=3) & (_el > 0)])
    m = ndi.binary_fill_holes(m | np.isin(_el, _ek[_ek > 0]))
    nz3 = np.zeros((H, W), bool); nz3[:collar0 + 40, W//2 - 260:W//2 + 260] = True
    # shirt edge: any remaining magenta/pink spill next to the shirt (skin never has blue above green)
    spill = (b > g + 5) & (r > g + 5)
    fringe = ndi.binary_dilation(m, iterations=5) & spill
    mfull = m | fringe
    if collar_px or hood_tip:   # back view (hood): the head sits above the garment, so nothing above the garment's top edge is fabric
        strict = (mg > 60) & (r > g + 50) & (b > g + 50)
        band = strict[:, W//2 - 40:W//2 + 41].mean(axis=1) > 0.5
        top = int(np.argmax(band)) if band.any() else 0
        top = max(0, top - 25); m[:top] = False; mfull[:top] = False; nz3[:top + 40, :] = True
    # recolour keeping the fabric's own light and shade
    L = lum(a); mu = np.median(L[m])
    ratio = np.clip(L/mu, 0.30, 1.85); ratio = (1 + (ratio - 1)*0.65)[..., None]
    tgt = np.array(target, float)[None, None, :]
    rr = ratio
    rec = np.where(rr <= 1, tgt*rr, tgt + (255 - tgt)*np.clip((rr - 1)*0.6, 0, 1))
    rec = np.clip(rec, 0, 255)
    soft = ndi.gaussian_filter(mfull.astype(float), 0.7)[..., None]
    a2 = a*(1 - soft) + rec*soft
    near60 = ndi.binary_dilation(mfull, iterations=20) & ~ndi.binary_dilation(mfull, iterations=1)
    bounce = near60 & (b > g + 2) & (r > b + 10)
    a2[..., 2] = np.where(bounce, np.minimum(a2[..., 2], g - 4), a2[..., 2])
    near90 = ndi.binary_dilation(mfull, iterations=20) & ~ndi.binary_dilation(mfull, iterations=1)
    redtint = near90 & (b >= g - 6) & (r > g + 22) & (r > b + 12) & (L < 135) & (g < 0.5*r)
    a2[..., 0] = np.where(redtint, g + (r - g)*0.5, a2[..., 0]); a2[..., 2] = np.where(redtint, np.minimum(a2[..., 2], g - 8), a2[..., 2])
    near150 = ndi.binary_dilation(mfull, iterations=45) & ~ndi.binary_dilation(mfull, iterations=1)
    pinkskin = near150 & (b > g + 2) & (r > g + 8)
    a2[..., 2] = np.where(pinkskin, np.minimum(a2[..., 2], g - 4), a2[..., 2])
    near40 = ndi.binary_dilation(mfull, iterations=40) & ~ndi.binary_dilation(mfull, iterations=1)
    pk2 = near150 & False
    a2[..., 2] = np.where(pk2, np.minimum(a2[..., 2], g - 20), a2[..., 2])
    a2[..., 0] = np.where(pk2, g + (r - g)*0.7, a2[..., 0])
    darkmg = ndi.binary_dilation(mfull, iterations=90) & ~mfull & ((r - g) > 0.6*(r + 1)) & (r > 40) & ~nz3 & (b > g + 2)
    sh = np.clip(L/mu*2.2, 0.35, 0.75)[..., None]
    for c in range(3): a2[..., c] = np.where(darkmg, (tgt[0, 0, c]*sh[..., 0]), a2[..., c])
    base2 = f'{work}/{key}_base.jpg'
    Image.fromarray(np.clip(a2, 0, 255).astype('uint8')).save(base2, quality=96)
    # collar = front neckline: first shirt pixel down the centre line
    cx = int(np.mean(np.where(m[int(H*0.62)])[0]))
    cols = m[:, cx-12:cx+13]
    firsts = [int(np.argmax(cols[:, i])) for i in range(cols.shape[1]) if cols[:, i].any()]
    collar = int(np.median(firsts))
    if collar_px: collar = int(collar_px)
    TORSO = None; GEL = None
    if pa_w_frac and pa_top_frac and not (hood_tip or collar_px):
        # Gelato placement (Andy, 6 Nov 2026: no guesses). Measured on this photo: the shirt's centre line and body width in the
        # band below the sleeves (55% to 92% of collar to hem), then the collar on that centre line. The print area is placed
        # with the proportions measured on Gelato's own mock-up of this template: width = pa_w_frac x body width, top edge
        # pa_top_frac x body width below the front neckline, centred on the shirt.
        tc, tw, hem = torso_measure(m, collar)
        cols = m[:, int(tc) - 12:int(tc) + 13]
        firsts = [int(np.argmax(cols[:, i])) for i in range(cols.shape[1]) if cols[:, i].any()]
        collar = int(np.median(firsts))
        tc, tw, hem = torso_measure(m, collar)
        TORSO = (tc, tw); GEL = (float(pa_w_frac), float(pa_top_frac))
        LAST['torso'] = (tc, tw, collar, hem)
        print(key, 'torso centre', round(tc, 1), 'body width', round(tw, 1), 'collar', collar, 'hem', hem)
    pw_override = None
    if hood_tip and hood_w:   # hem off the picture: the same Gelato proportions expressed on the hood's width
        collar = int(int(hood_tip) - 0.145*float(hood_w)); below_in = 0.0; pw_override = int(0.98*float(hood_w))
        LAST['tip'] = int(hood_tip); LAST['hem'] = H; LAST['cx'] = W//2
        print(key, 'hood tip', hood_tip, 'hood width', hood_w, 'print area top', collar, 'width', pw_override)
    elif hood_tip:   # Gelato's own hoodie back mock-up (measured 19 Oct 2026): with D = hem minus hood tip, the 340 x 453 mm print
        # area is 0.537 D wide and its top edge sits 0.0796 D above the hood tip; the hood lies over the top of the print
        cxm = W//2; colm = m[:, cxm - 40:cxm + 41].mean(axis=1) > 0.5
        hem = int(np.where(colm)[0].max()); D = hem - int(hood_tip)
        collar = int(int(hood_tip) - 0.0796*D); below_in = 0.0; pw_override = int(0.537*D)
        print(key, 'hem', hem, 'hood tip', hood_tip, 'print area top', collar, 'width', pw_override)
        LAST['hem'] = hem; LAST['tip'] = int(hood_tip); LAST['cx'] = int(np.mean(np.where(m[(hem + int(hood_tip))//2])[0]))
    # print placement through the playbook script (collar and shirt shape supplied from the exact colour mask)
    src = open(sp.__file__).read()
    src = src.replace("    strip = a[:int(H*0.6), cx - 20:cx + 20]\n    sk = skin(strip).mean(axis=1) > 0.5\n    collar = int(np.where(sk)[0].max()) + 1",
                      "    collar = COLLAR_OVERRIDE")
    assert 'COLLAR_OVERRIDE' in src
    src = src.replace("    pw = int(print_w_cm*px_per_cm);", "    pw = (int(round(GEL[0]*TORSO[1])) if GEL else (PW_OVERRIDE or int(print_w_cm*px_per_cm)));")
    assert 'PW_OVERRIDE' in src
    src = src.replace("    cx = int(np.mean(np.where(m[int(H*0.58)])[0]))", "    cx = int(round(TORSO[0])) if TORSO else int(np.mean(np.where(m[int(H*0.58)])[0]))")
    assert 'TORSO[0]' in src
    src = src.replace("    x0 = cx - pw//2; y0 = int(collar + below_collar_in*2.54*px_per_cm)",
                      "    x0 = cx - pw//2; y0 = int(collar + below_collar_in*2.54*px_per_cm)\n    if GEL: x0 = int(round(TORSO[0] - pw/2)); y0 = int(round(collar + GEL[1]*TORSO[1]))")
    assert 'GEL[1]' in src
    ns = {'__name__': 'spx', 'COLLAR_OVERRIDE': collar, 'PW_OVERRIDE': pw_override, 'TORSO': TORSO, 'GEL': GEL}
    exec(compile(src, 'spx', 'exec'), ns)
    ns['shirt_mask'] = lambda im: (m.copy(), np.median(a2[int(H*0.55):int(H*0.62), int(W*0.45):int(W*0.55)].reshape(-1, 3), axis=0))
    grey = f'{work}/{key}_placed_grey.jpg'
    x0, y0, pw, ph = ns['place'](base2, printfile, grey, chest_cm=chest_cm, below_collar_in=below_in, print_w_cm=print_w_cm)
    print(key, 'collar', collar, 'print box', x0, y0, pw, ph)
    # chroma key on the green backdrop
    placed = Image.open(grey).convert('RGB'); pa = np.asarray(placed).astype(float)
    if hood_poly:   # the hood lies over the top of the print, as on the real garment (Gelato's mock-up)
        from PIL import ImageDraw
        hm = Image.new('L', (W, H), 0); ImageDraw.Draw(hm).polygon([tuple(v) for v in hood_poly], fill=255)
        hm = ndi.gaussian_filter(np.asarray(hm).astype(float)/255, 1.5)[..., None]
        pa = pa*(1 - hm) + np.asarray(Image.open(base2).convert('RGB')).astype(float)*hm
        Image.fromarray(np.clip(pa, 0, 255).astype('uint8')).save(grey, quality=96)
    if cords:   # hoodie fronts: the drawstrings hang over the print, as on the real garment (Andy, 19 Oct 2026)
        from PIL import ImageDraw
        cmk = Image.new('L', (W, H), 0); dr = ImageDraw.Draw(cmk)
        for c in cords:
            pts = [tuple(v) for v in c['pts']]; w = int(c.get('w', 16))
            dr.line(pts, fill=255, width=w, joint='curve')
            for p0 in pts: dr.ellipse((p0[0] - w/2, p0[1] - w/2, p0[0] + w/2, p0[1] + w/2), fill=255)
        cmf = ndi.gaussian_filter(np.asarray(cmk).astype(float)/255, 1.0)[..., None]
        pa = pa*(1 - cmf) + np.asarray(Image.open(base2).convert('RGB')).astype(float)*cmf
        Image.fromarray(np.clip(pa, 0, 255).astype('uint8')).save(grey, quality=96)
    raw = np.asarray(Image.open(base).convert('RGB')).astype(float)
    # the key is read from the original (un-despilled) colours so green is still green; the placed picture carries the print
    gk = np.dstack([ndi.gaussian_filter(raw[..., c], 0.8) for c in range(3)])
    gscore = gk[..., 1] - np.maximum(gk[..., 0], gk[..., 2])
    ref = np.median(gscore[:150, :150]); lo = ref*0.12; hi = ref*0.50
    keyalpha = 1 - np.clip((gscore - lo)/(hi - lo), 0, 1)
    protect = ndi.binary_dilation(mfull, iterations=2)
    protect[max(0, y0-20):y0+ph+20, max(0, x0-20):x0+pw+20] = True
    prot_shirt = ndi.binary_dilation(mfull, iterations=2) & (gscore < ref*0.5)
    protect[:] = False; protect[max(0, y0-20):y0+ph+20, max(0, x0-20):x0+pw+20] = True
    al2 = np.where(protect | prot_shirt, 1.0, keyalpha)
    al2 = ndi.gaussian_filter(al2, 0.5)
    # edge pixels: take the colour of the nearest solid subject pixel (no green or backdrop fringe)
    al2 = np.clip((al2 - 0.45)/0.45, 0, 1)
    er = ndi.gaussian_filter(ndi.binary_erosion(al2 > 0.5, iterations=3).astype(float), 0.8)
    al2 = np.minimum(al2, er)
    solid = ndi.binary_erosion(al2 > 0.97, iterations=5)
    # head and hair (above the collar): take edge colours from well inside, so no green-screen tint survives
    _head = np.zeros((H, W), bool); _head[:collar + 20] = True
    _solid_deep = ndi.binary_erosion(al2 > 0.97, iterations=9)
    solid = np.where(_head, _solid_deep, solid)
    idx = ndi.distance_transform_edt(~solid, return_distances=False, return_indices=True)
    nearest = pa[idx[0], idx[1]]
    _edgezone = _head & ndi.binary_dilation(al2 < 0.97, iterations=9) & ~ndi.binary_erosion(mfull, iterations=1)
    _w = _solid_deep.astype(float)
    _den = ndi.gaussian_filter(_w, 5)[..., None]
    _num = np.dstack([ndi.gaussian_filter(pa[..., c]*_w, 5) for c in range(3)])
    _smooth = np.where(_den > 0.03, _num/np.maximum(_den, 1e-3), nearest)
    _fill = np.where(_head[..., None], _smooth, nearest)
    fg = np.where(((al2 < 0.97) | _edgezone)[..., None], _fill, pa)
    # no green above the red/blue level on the head (hair, skin, beard never are green); NOT on the shirt, it turns the shirt teal
    _g = np.minimum(fg[..., 1], 0.92*np.maximum(fg[..., 0], fg[..., 2]))
    fg[..., 1] = np.where(_head & ~ndi.binary_dilation(mfull, iterations=4), _g, fg[..., 1])
    comp = fg*al2[..., None] + grad_bg(W, H, bg)*(1 - al2[..., None])
    Image.fromarray(np.clip(comp, 0, 255).astype('uint8')).save(out, quality=93)
    Image.fromarray(np.dstack([np.clip(fg, 0, 255), al2*255]).astype('uint8'), 'RGBA').save(out.replace('.jpg', '_cutout.png'))
    # integrity: print area must be unchanged
    ia = pa[y0:y0+ph, x0:x0+pw]; ib = np.asarray(Image.open(out).convert('RGB')).astype(float)[y0:y0+ph, x0:x0+pw]
    print(key, 'print-area max diff', float(np.abs(ia - ib).max()), 'mean', round(float(np.abs(ia - ib).mean()), 2))
    return x0, y0, pw, ph, W


if __name__ == '__main__':
    key, base, target, printfile, bg, out = sys.argv[1:7]
    build(key, base, tuple(int(v) for v in target.split(',')), printfile, bg, out)
