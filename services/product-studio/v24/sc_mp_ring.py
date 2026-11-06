"""SC model pictures, ringer step: from the model chat's build_ring.py (SC Models Playbook, 19 Oct 2026)."""

import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi

BG = {'pink': ((255,110,170),(240,60,130)), 'sky': ((120,205,255),(60,150,240)),
      'orange': ((255,170,60),(255,120,20)), 'aqua': ((90,235,225),(20,180,190)),
      'purple': ((170,120,255),(110,60,220))}

def lum(a): return 0.299*a[...,0] + 0.587*a[...,1] + 0.114*a[...,2]
def skin(a):
    r, g, b = a[...,0], a[...,1], a[...,2]
    return (r > g + 12) & (r > b + 20) & (r > 80) & (r - b < 140)

def grad_bg(W, H, name):
    c1, c2 = BG[name]
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    d = np.hypot((xx - W/2)/(W*0.8), (yy - H*0.42)/(H*0.75)); t = np.clip(d, 0, 1)[..., None]
    return np.array(c1)*(1 - t) + np.array(c2)*t

def load_art(path):
    P = Image.open(path)
    if P.mode == 'RGBA':
        a = np.asarray(P).astype(float); al = a[..., 3]/255; rgb = a[..., :3]
        bb = P.getchannel('A').getbbox()
    else:
        rgb = np.asarray(P.convert('RGB')).astype(float)
        al = np.ones(rgb.shape[:2]); nw = (rgb.min(2) < 245)
        ys, xs = np.where(nw); bb = (xs.min(), ys.min(), xs.max()+1, ys.max()+1)
    x0, y0, x1, y1 = bb
    eff = rgb[y0:y1, x0:x1]*al[y0:y1, x0:x1, None] + 255*(1 - al[y0:y1, x0:x1, None])
    return eff

def build(key, base, printfile, bg, out, emb_cm=12.0, off_cm=11.0, top_cm=8.0, chest_cm=53.0, back=False):
    a = np.asarray(Image.open(base).convert('RGB')).astype(float); H, W = a.shape[:2]
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    gs = g - np.maximum(r, b)
    border = np.concatenate([gs[:60].ravel(), gs[:, :40].ravel(), gs[:, -40:].ravel()])
    ref = np.percentile(border, 50)
    lo, hi = ref*0.10, ref*0.65
    al = 1 - np.clip((gs - lo)/(hi - lo), 0, 1)
    # despill
    mx = np.maximum(r, b)
    a2 = a.copy(); a2[..., 1] = np.minimum(g, mx + 2)
    solid = ndi.binary_erosion(al > 0.999, iterations=4)
    idx = ndi.distance_transform_edt(~solid, return_distances=False, return_indices=True)
    filled = a2[idx[0], idx[1]]
    edge = ndi.binary_dilation(al < 0.999, iterations=3) & ~solid
    a2 = np.where(edge[..., None], filled, a2)
    band = ndi.binary_dilation(al < 0.999, iterations=14)
    a2[..., 1] = np.where(band, np.minimum(a2[..., 1], (a2[..., 0] + a2[..., 2])/2*0.97), a2[..., 1])
    al = np.clip((al - 0.55)/0.35, 0, 1)
    al = ndi.grey_erosion(al, size=3) if False else al
    al = ndi.gaussian_filter(ndi.binary_erosion(al > 0.5, iterations=2).astype(float)*0 + al, 0.6)
    # geometry on the shirt
    ab = np.dstack([ndi.gaussian_filter(a2[..., c], 2) for c in range(3)])
    person = ndi.binary_fill_holes(al > 0.5)
    L = lum(ab); sat = ab.max(2) - ab.min(2)
    white = person & (L > 135) & (sat < 45) & ~skin(ab)
    white = ndi.binary_opening(white, iterations=2); white = ndi.binary_closing(white, iterations=4)
    cxg = W//2
    lab, _ = ndi.label(white)
    # shirt component = biggest white component whose centroid is near the chest
    cand = lab[int(H*0.62), cxg-60:cxg+60]; cand = cand[cand > 0]
    sh = lab == np.bincount(cand).argmax()
    sh = ndi.binary_fill_holes(sh)
    cx = int(np.mean(np.where(sh[int(H*0.62)])[0]))
    strip = ab[:int(H*0.6), cx-20:cx+20]
    wh = ((lum(strip).mean(axis=1) > 150) & ((strip.max(2) - strip.min(2)).mean(axis=1) < 40))
    if back:
        y0s = int(H*0.30)
        run = np.convolve(wh[y0s:].astype(int), np.ones(60, int), 'valid')
        collar = y0s + int(np.argmax(run >= 60))
    else:
        sk = skin(strip).mean(axis=1) > 0.5
        ylow = int(np.where(sk)[0].max()) + 1
        collar = ylow + int(np.argmax(wh[ylow:]))
    bot = np.where(sh.any(axis=1))[0].max()
    m = sh.copy(); m[:collar] = False
    widths = []
    for y in range(int(collar + (bot - collar)*0.40), int(collar + (bot - collar)*0.75)):
        xs = np.where(m[y])[0]
        if len(xs): widths.append(xs.max() - xs.min())
    chest_px = float(np.percentile(widths, 30)); ppc = chest_px/chest_cm
    # emblem
    art = load_art(printfile)
    pw = int(round(emb_cm*ppc)); ph = int(round(art.shape[0]*pw/art.shape[1]))
    A = np.asarray(Image.fromarray(art.astype('uint8')).resize((pw, ph), Image.LANCZOS)).astype(float)
    xc = cx + int(round(off_cm*ppc)); x0 = xc - pw//2; y0 = int(collar + top_cm*ppc)
    layer = np.full((H, W, 3), 255.0)
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x0+pw), min(H, y0+ph)
    layer[ya:yb, xa:xb] = A[ya-y0:yb-y0, xa-x0:xb-x0]
    # bend with the fabric (max ~5 px), shading multiplied in
    Lraw = lum(a2); gy, gx = np.gradient(ndi.gaussian_filter(Lraw, 12)); gm_ = np.hypot(gx, gy)
    k = 5.0/max(1e-3, np.percentile(gm_[m], 99))
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    layer = np.dstack([ndi.map_coordinates(layer[..., c], [yy - gy*k, xx - gx*k], order=1, mode='nearest') for c in range(3)])
    shirtc = np.dstack([ndi.gaussian_filter(a2[..., c], 1.0) for c in range(3)])
    refc = np.median(shirtc[ya:yb, xa:xb][m[ya:yb, xa:xb]], axis=0)
    shade = np.clip(shirtc/refc, 0, 1.15)
    ink = np.clip(layer/255.0*shade*255*0 + layer*shade, 0, 255)
    # only where the layer is not plain paper: weight by art darkness vs white handled by multiply
    mm = ndi.gaussian_filter(ndi.binary_erosion(m, iterations=3).astype(float), 1.0)[..., None]
    a3 = a2*(1 - mm) + (a2/np.maximum(refc, 1)*0 + shirtc*(layer/255.0)/1.0*0 + np.clip(a2*(layer/255.0), 0, 255))*mm
    # print area outside the emblem box stays untouched (layer is white there -> multiply by 1)
    comp = a3*al[..., None] + grad_bg(W, H, bg)*(1 - al[..., None])
    Image.fromarray(np.clip(comp, 0, 255).astype('uint8')).save(out, quality=93)
    Image.fromarray(np.clip(np.dstack([a3, al*255]), 0, 255).astype('uint8'), 'RGBA').save(out.replace('.jpg', '_cutout.png'))
    print(key, 'collar', collar, 'cx', cx, 'chest px', round(chest_px), 'ppc', round(ppc, 2), 'print box', x0, y0, pw, ph)
    dbg = np.zeros((H, W, 3), 'uint8'); dbg[m] = (255, 255, 255); dbg[..., 1][~m & person] = 90
    Image.fromarray(dbg).resize((W//4, H//4)).save(out.replace('.jpg', '_mask.png'))
    return x0, y0, pw, ph, W

if __name__ == '__main__':
    key, base, printfile, bg, out = sys.argv[1:7] if False else sys.argv[1:6]
    if key.startswith('back'): build(key, base, printfile, bg, out, emb_cm=31.0, off_cm=0.0, top_cm=8.0, back=True)
    else: build(key, base, printfile, bg, out)

