"""SC water bottle pictures (Andy, 20 Oct 2026): the print at true size on Gelato's own blank white 17oz stainless steel
bottle, lit by the bottle's own shading, on an SC colour backdrop.
  python3 sc_bottle_pic.py <blank.png> <blank_cut.png> <print.png> <out.jpg> <turn_deg> <backdrop> [size]
     blank.png      Gelato's blank bottle on its white studio floor (2048 x 2048, from Gelato's own render with the print
                    removed; kept on Cloudinary SCSMAuto/bottles)
     blank_cut.png  the same with a clean cut-out (alpha)
     print.png      the print file (87 x 116 mm, 1027 x 1370 px; transparent where nothing prints)
     turn_deg       0 = print centred to the camera; +/- turns the bottle so the print moves left (-) or right (+)
   Measurements (Gelato): bottle 70 mm across; print area 87 x 116 mm. The print's height on the bottle and the camera's
   view of the top and bottom edges of the print are fitted to Gelato's own render of this bottle (20 Oct 2026):
   print top edge y = 949.2 + 34.8 cos(a), bottom edge y = 1570.3 + 69.7 cos(a) in the 2048 px render, a = angle round
   the bottle from the camera. Across the bottle the print follows the true circle: 1 mm of print = 1 mm of arc (r 35 mm)."""
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi

BG = {'pink': ((255,110,170),(240,60,130)), 'sky': ((120,205,255),(60,150,240)), 'orange': ((255,170,60),(255,120,20)),
      'aqua': ((90,235,225),(20,180,190)), 'purple': ((170,120,255),(110,60,220))}
R_MM, PW_MM = 35.0, 87.0
REF = 2048.0                      # the fit above is in the 2048 px render
TOP = (949.2, 34.8); BOT = (1570.3, 69.7)

def grad(W, H, name):
    c1, c2 = BG[name]; yy, xx = np.mgrid[0:H, 0:W].astype(float)
    t = np.clip(np.hypot((xx - W/2)/(W*0.8), (yy - H*0.42)/(H*0.75)), 0, 1)[..., None]
    return np.array(c1)*(1 - t) + np.array(c2)*t

CROP = (180, 120, 1740)            # square crop round the bottle in the 2048 px render: left, top, side

def main(blank, cut, prn, out, turn, bg, size=2000):
    final = int(size); size = int(round(final*REF/CROP[2])); f = size/REF; th0 = np.radians(float(turn))
    b = np.asarray(Image.open(blank).convert('RGB').resize((size, size), Image.LANCZOS)).astype(float)
    a = np.asarray(Image.open(cut).convert('RGBA').resize((size, size), Image.LANCZOS))[..., 3].astype(float)/255
    H, W = a.shape; body = a > 0.5
    pr = np.asarray(Image.open(prn).convert('RGBA')).astype(np.float32); ph, pw = pr.shape[:2]
    mapx = np.full((H, W), -1, np.float32); mapy = np.full((H, W), -1, np.float32)
    y_lo, y_hi = int((TOP[0] - 5)*f), int((BOT[0] + BOT[1] + 5)*f)
    for y in range(y_lo, y_hi + 1):
        xs = np.where(body[y])[0]
        if len(xs) < 10: continue
        xl, xr = xs.min(), xs.max(); xc, rad = (xl + xr)/2, (xr - xl)/2
        x = np.arange(xl, xr + 1); s = (x - xc)/rad; ok = np.abs(s) < 0.999
        x, s = x[ok], s[ok]; al = np.arcsin(s); c = np.cos(al)
        t = (y/f - TOP[0] - TOP[1]*c)/((BOT[0] - TOP[0]) + (BOT[1] - TOP[1])*c)
        u = 0.5 + (al - th0)*R_MM/PW_MM
        m = (t >= 0) & (t <= 1) & (u >= 0) & (u <= 1)
        mapx[y, x[m]] = u[m]*(pw - 1); mapy[y, x[m]] = t[m]*(ph - 1)
    P = np.stack([ndi.map_coordinates(pr[..., k], [mapy, mapx], order=1, mode='constant', cval=0) for k in range(4)], -1)
    pa = (P[..., 3:]/255)*(mapx[..., None] >= 0)*body[..., None]
    # the print sits in the white coating: it multiplies with the bottle's own shading (white in the file = bare bottle)
    gray = b.mean(axis=2)
    white = np.percentile(gray[body], 98)
    shade = np.clip(b/white, 0, 1.0)
    printed = shade*P[..., :3]
    bottle = b*(1 - pa) + np.clip(printed, 0, 255)*pa
    # backdrop with the bottle's own floor shadow
    ref = np.median(np.concatenate([gray[:, :30], gray[:, -30:]], axis=1), axis=1)[:, None]
    sh = ndi.gaussian_filter(np.clip(gray/np.maximum(ref, 1), 0.4, 1.0), 2)[..., None]
    G = grad(W, H, bg)*sh
    af = a[..., None]
    img = bottle*af + G*(1 - af)
    x0, y0, sd = (int(round(v*f)) for v in CROP)
    im = Image.fromarray(np.clip(img, 0, 255).astype('uint8')).crop((x0, y0, x0 + sd, y0 + sd))
    im.resize((final, final), Image.LANCZOS).save(out, quality=94)
    print(f'{out}: turn {turn} deg, backdrop {bg}')

if __name__ == '__main__':
    main(*sys.argv[1:])
