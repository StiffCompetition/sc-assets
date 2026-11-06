"""SC print-on-model: puts an approved print file onto a studio photo of a model in a PLAIN shirt,
the way a print-on-demand mock-up does, so the print looks printed into the fabric, not pasted on top.

  python3 sc_print_on_model.py model_plain.jpg print_3600x4800.png out.jpg [--chest-cm 53] [--below-collar-in 2]

Method (same idea as Gelato and Photoshop mock-ups):
  1. Find the shirt: colour region connected to the chest centre.
  2. Real size: the print file (12 x 16 in Gelato print area) is scaled so 12 in = 30.5 cm on a 53 cm wide chest,
     measured across the shirt body below the sleeves. Top of the print area sits a set distance below the collar.
  3. Folds: the print is displaced by the shirt's own light and shade, so it bends with the fabric.
  4. Shading: the shirt's shadows and highlights are multiplied into the print.
  5. Ink: slightly matte and soft (DTG ink on cotton), with the fabric's own grain on top. Never printed on arms or hair.
The print artwork itself is never redrawn: only scaled, gently bent and shaded.
"""
import sys, numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi

def lum(a): return 0.299*a[..., 0] + 0.587*a[..., 1] + 0.114*a[..., 2]

def skin(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return (r > g + 12) & (r > b + 20) & (r > 80) & (r - b < 140)

_SESSION = None
def shirt_mask(img):
    """Shirt = the person (rembg human segmentation, free, runs locally) minus skin, below the neckline later."""
    global _SESSION
    from rembg import remove, new_session
    if _SESSION is None: _SESSION = new_session('u2net_human_seg')
    a = np.asarray(img).astype(float); H, W = a.shape[:2]
    person = np.asarray(remove(img, session=_SESSION, only_mask=True)) > 128
    ab = np.dstack([ndi.gaussian_filter(a[..., c], 2) for c in range(3)])
    m = person & ~skin(ab)
    m = ndi.binary_opening(m, iterations=2); m = ndi.binary_closing(m, iterations=4)
    lab, _ = ndi.label(m); m = ndi.binary_fill_holes(lab == lab[int(H*0.6), W//2])
    col = np.median(a[int(H*0.55):int(H*0.62), int(W*0.45):int(W*0.55)].reshape(-1, 3), axis=0)
    return m, col

def _old_shirt_mask(img):
    a = np.asarray(img).astype(float); H, W = a.shape[:2]
    seed = a[int(H*0.55):int(H*0.62), int(W*0.45):int(W*0.55)].reshape(-1, 3)
    col = np.median(seed, axis=0); spread = np.percentile(np.abs(seed - col).max(axis=1), 95)
    d = np.abs(a - col).max(axis=2)
    bgc = np.median(np.concatenate([a[:60, :60].reshape(-1, 3), a[:60, -60:].reshape(-1, 3)]), axis=0)
    tol = min(max(45, spread*2.5), 0.55*np.abs(bgc - col).max())     # never reach the backdrop (white shirt on light grey)
    m = d <= tol
    m = ndi.binary_closing(m, iterations=6); m = ndi.binary_opening(m, iterations=3)
    lab, _ = ndi.label(m); m = lab == lab[int(H*0.58), W//2]
    m = ndi.binary_fill_holes(m)
    return m, col

def place(model_path, print_path, out_path, chest_cm=53.0, below_collar_in=2.0, print_w_cm=30.48):
    img = Image.open(model_path).convert('RGB'); a = np.asarray(img).astype(float); H, W = a.shape[:2]
    m, col = shirt_mask(img)
    cx = int(np.mean(np.where(m[int(H*0.58)])[0]))
    # front of the neckline: the lowest skin (neck) pixel on the centre line in the upper part of the photo
    strip = a[:int(H*0.6), cx - 20:cx + 20]
    sk = skin(strip).mean(axis=1) > 0.5
    collar = int(np.where(sk)[0].max()) + 1
    m[:collar] = False                                         # nothing above the neckline is shirt (hair, face, backdrop)
    lab, _ = ndi.label(m); m = lab == lab[int(H*0.58), cx]
    bot = np.where(m.any(axis=1))[0].max()
    # chest width: shirt body width in the band below the sleeves
    widths = []
    for y in range(int(collar + (bot - collar)*0.40), int(collar + (bot - collar)*0.75)):
        xs = np.where(m[y])[0]
        if len(xs): widths.append(xs.max() - xs.min())
    chest_px = float(np.percentile(widths, 30))
    px_per_cm = chest_px/chest_cm
    P = Image.open(print_path).convert('RGBA')
    pw = int(print_w_cm*px_per_cm); ph = int(P.height*pw/P.width)   # the print file's real width (its pixels at 300 dpi)
    P = P.resize((pw, ph), Image.LANCZOS)
    x0 = cx - pw//2; y0 = int(collar + below_collar_in*2.54*px_per_cm)
    layer = np.zeros((H, W, 4));
    xa, ya = max(0, x0), max(0, y0); xb, yb = min(W, x0 + pw), min(H, y0 + ph)
    layer[ya:yb, xa:xb] = np.asarray(P).astype(float)[ya - y0:yb - y0, xa - x0:xb - x0]
    # Mock-up industry method (Photoshop / Printful-style templates): a blurred, desaturated copy of the shirt is used
    # (1) as a displacement map so the print bends with the fabric and (2) as soft-light + hard-light shading layers.
    # The shading map is NORMALISED to mid-grey inside the shirt, so a black shirt gives the same gentle folds as a
    # white one (raw dark fabric would muddy the print). No fabric grain is copied in (it reads as dirt); 2% fine noise only.
    L = lum(a); Ld = ndi.gaussian_filter(L, 10)
    lo, mid, hi = np.percentile(Ld[m], [5, 50, 95]); span = max(8.0, hi - lo)
    base = np.clip(0.5 + (Ld - mid)/span*0.5, 0.15, 0.85)                       # 0.5 = no change
    gy, gx = np.gradient(ndi.gaussian_filter(L, 12)); g = np.hypot(gx, gy)
    k = 5.0/max(1e-3, np.percentile(g[m], 99))                                   # at most ~5 px bend at this photo size
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    warped = np.dstack([ndi.map_coordinates(layer[..., c], [yy - gy*k, xx - gx*k], order=1) for c in range(4)])
    rgb, al = warped[..., :3]/255.0, warped[..., 3]/255.0
    B = base[..., None]
    soft = np.where(B < 0.5, rgb - (1 - 2*B)*rgb*(1 - rgb), rgb + (2*B - 1)*(np.sqrt(rgb) - rgb))
    hard = np.where(B < 0.5, 2*rgb*B, 1 - 2*(1 - rgb)*(1 - B))
    rgb = rgb*0.45 + soft*0.40 + hard*0.15                                       # soft light ~40%, hard light ~15%
    gm = rgb.mean(axis=2, keepdims=True); rgb = gm + (rgb - gm)*0.95            # DTG ink: very slightly less saturated
    rgb = np.clip(rgb + np.random.default_rng(1).normal(0, 0.012, (H, W, 1)), 0, 1)*255
    rgb = np.dstack([ndi.gaussian_filter(rgb[..., c], 0.5) for c in range(3)])
    al = ndi.gaussian_filter(al, 0.6)*ndi.gaussian_filter(m.astype(float), 1.0)
    out = a*(1 - al[..., None]) + np.clip(rgb, 0, 255)*al[..., None]
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(out_path, quality=93)
    print(f'chest {chest_px:.0f} px = {chest_cm} cm, print area width {pw} px, collar y {collar}, print top y {y0}')
    return x0, y0, pw, ph

if __name__ == '__main__':
    args = sys.argv[1:]; kw = {}
    if '--chest-cm' in args: i = args.index('--chest-cm'); kw['chest_cm'] = float(args[i+1]); del args[i:i+2]
    if '--below-collar-in' in args: i = args.index('--below-collar-in'); kw['below_collar_in'] = float(args[i+1]); del args[i:i+2]
    place(*args, **kw)
