"""SC mug pictures (Andy, 20 Oct 2026): the print wrapped onto Gelato's own blank 15oz mug (renders from Gelato, kept in
Drive SC Image Library/40 Merch/Mugs), lit by the mug's own shading and gloss, on an SC colour backdrop.
  python3 sc_mug_pic.py <blank.png> <blank_cut.png> <wrap.png> <out.jpg> <handle: left|right|back> <backdrop> [size]
     blank.png      Gelato's blank mug on its white studio floor (for the floor shadow)
     blank_cut.png  the same with a clean cut-out (alpha)
     wrap.png       the print file for the whole wrap (transparent where nothing prints)
     handle         where the handle is in this picture: left | right | back (the unprinted strip is centred on the handle)
   Placement (Andy, 20 Oct 2026): Gelato 15oz white mug, 87 mm across, 117 mm tall (Gelato product data); print area
   213 x 103 mm (Gelato support). Gelato does not publish where the band sits, so it is centred: 7 mm clear at the rim
   and at the base, and the 60 mm unprinted strip is centred on the handle. The left half of the file faces you when the
   handle is on the left (as in Gelato's own mockups). Camera geometry checked against Gelato's own 15oz mockups of the
   same blank mugs: the body runs from a straight line at the top (rim) to the base arc."""
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi

BG = {'pink': ((255,110,170),(240,60,130)), 'sky': ((120,205,255),(60,150,240)), 'orange': ((255,170,60),(255,120,20)),
      'aqua': ((90,235,225),(20,180,190)), 'purple': ((170,120,255),(110,60,220))}
CIRC_MM, WRAP_MM = np.pi*87, 213.0  # 15oz mug: 87 mm across; print area 213 mm wide (Gelato)
BODY_MM, BAND_MM = 117.0, 103.0      # mug height; print area height (Gelato)
GAP_MM = (BODY_MM - BAND_MM)/2       # centred: 7 mm clear at the rim and at the base
PRINT_V = (GAP_MM/BODY_MM, (GAP_MM + BAND_MM)/BODY_MM)
K = (CIRC_MM/WRAP_MM)/(2*np.pi)      # share of the wrap per radian round the mug

def grad(W, H, name):
    c1, c2 = BG[name]; yy, xx = np.mgrid[0:H, 0:W].astype(float)
    t = np.clip(np.hypot((xx - W/2)/(W*0.8), (yy - H*0.42)/(H*0.75)), 0, 1)[..., None]
    return np.array(c1)*(1 - t) + np.array(c2)*t

def centre_u(handle):
    # u = 0.5 (middle of the file) is opposite the handle; front of the picture is theta = 0
    th_h = {'left': -np.pi/2, 'right': np.pi/2, 'back': np.pi}[handle]
    d = 0.0 - (th_h + np.pi)
    d = (d + np.pi) % (2*np.pi) - np.pi
    return 0.5 + d*K

def main(blank, cut, wrap, out, handle, bg, size=2000):
    size = int(size); cu = centre_u(handle)
    B = Image.open(blank).convert('RGB').resize((size, size), Image.LANCZOS)
    C = Image.open(cut).convert('RGBA').resize((size, size), Image.LANCZOS)
    b = np.asarray(B).astype(float); a = np.asarray(C)[..., 3].astype(float)/255; H, W = a.shape
    body = a > 0.5
    # body columns per row: the run through the mug's middle (the handle is a separate run)
    cols = np.where(body[int(H*0.55)])[0]
    xmid = int(np.median(cols)) if len(cols) else W//2
    rows = np.where(body.any(1))[0]; y0, y1 = rows.min(), rows.max()
    L = np.full(H, -1); R = np.full(H, -1)
    for y in range(y0, y1 + 1):
        r = body[y]
        if not r[xmid]: continue
        l = xmid
        while l > 0 and r[l - 1]: l -= 1
        rr = xmid
        while rr < W - 1 and r[rr + 1]: rr += 1
        L[y], R[y] = l, rr
    ok = L >= 0
    # handle rows join the body: use the narrowest sensible body edge (median over rows) to cut the handle off
    yy = np.where(ok)[0]
    l_med = np.median(L[yy[len(yy)//5: 4*len(yy)//5]]); r_med = np.median(R[yy[len(yy)//5: 4*len(yy)//5]])
    xl, xr = int(l_med), int(r_med); xc = (xl + xr)/2; Rad = (xr - xl)/2
    # front surface: top and bottom arcs. The base silhouette is the front arc; the top front arc is the same shape shifted up.
    X = np.arange(xl, xr + 1)
    bot = np.array([np.where(body[:, x])[0].max() for x in X]).astype(float)
    top = np.array([np.where(body[:, x])[0].min() for x in X]).astype(float)
    bot = ndi.median_filter(bot, 9)
    n = len(X); edge = list(range(int(n*0.03), int(n*0.07))) + list(range(int(n*0.93), int(n*0.97)))
    Hb = np.median((bot - top)[edge])                            # body height near the sides, where front and back arcs meet
    front_top = np.full_like(bot, np.median(bot[edge]) - Hb)     # the rim: a straight line at the side height (fitted to Gelato's mockups)
    # sampling map
    wr = np.asarray(Image.open(wrap).convert('RGBA')).astype(np.float32); wh, ww = wr.shape[:2]
    mapx = np.full((H, W), -1, np.float32); mapy = np.full((H, W), -1, np.float32)
    for i, x in enumerate(X):
        s = (x - xc)/Rad
        if abs(s) >= 0.999: continue
        th = np.arcsin(s)
        u = cu + th*K
        hh = bot[i] - front_top[i]
        ys = np.arange(int(front_top[i]), int(bot[i]) + 1)
        v = (ys - front_top[i])/hh
        vv = (v - PRINT_V[0])/(PRINT_V[1] - PRINT_V[0])
        m = (vv >= 0) & (vv <= 1) & (u >= 0) & (u <= 1)
        mapx[ys[m], x] = u*(ww - 1); mapy[ys[m], x] = vv[m]*(wh - 1)
    P = np.stack([ndi.map_coordinates(wr[..., k], [mapy, mapx], order=1, mode='constant', cval=0) for k in range(4)], -1)
    pa = (P[..., 3:]/255)*(mapx[..., None] >= 0)*body[..., None]
    # the print is dye under the glaze: it multiplies with the white mug (white in the file = no ink, the bare mug), then the gloss sits on top
    gray = b.mean(axis=2)
    white = np.percentile(gray[body], 98)
    shade = np.clip(b/white, 0, 1.0)
    gloss = np.clip(gray - ndi.gaussian_filter(gray, size/40), 0, None)[..., None]*1.2
    gl = np.minimum(gloss, b)
    printed = (b - gl)*(P[..., :3]/255) + gl
    mug = b*(1 - pa) + np.clip(printed, 0, 255)*pa
    # backdrop with the mug's own floor shadow
    ref = np.median(np.concatenate([gray[:, :30], gray[:, -30:]], axis=1), axis=1)[:, None]
    sh = ndi.gaussian_filter(np.clip(gray/np.maximum(ref, 1), 0.4, 1.0), 2)[..., None]
    G = grad(W, H, bg)*sh
    af = a[..., None]
    outimg = mug*af + G*(1 - af)
    Image.fromarray(np.clip(outimg, 0, 255).astype('uint8')).save(out, quality=94)
    print(f'{out}: body {xl}-{xr}, height {Hb:.0f}px, handle {handle}, centre_u {cu:.3f}')

if __name__ == '__main__':
    main(*sys.argv[1:])
