"""SC colour backdrops for product pictures on a white product (mugs, bottles) (Andy, 20 Oct 2026: different colours, as the
other products have): each picture gets its own SC colour, the ones furthest in hue from the print's main colour first,
the same contrast rule as the t-shirt model pictures (sc_model_pics.pick_bg)."""
import colorsys, numpy as np
from PIL import Image
BG = {'pink': ((255,110,170),(240,60,130)), 'sky': ((120,205,255),(60,150,240)), 'orange': ((255,170,60),(255,120,20)),
      'aqua': ((90,235,225),(20,180,190)), 'purple': ((170,120,255),(110,60,220))}
ORDER = ['pink', 'sky', 'orange', 'aqua', 'purple']

def ranked(print_path):
    a = np.asarray(Image.open(print_path).convert('RGBA').resize((400, 200))).astype(float)/255
    rgb, al = a[..., :3].reshape(-1, 3), a[..., 3].reshape(-1)
    mx, mn = rgb.max(1), rgb.min(1); sat = (mx - mn)/np.maximum(mx, 1e-6)
    keep = (al > 0.5) & (sat > 0.35) & (mx > 0.25)
    if keep.sum() < 50: return ORDER[:]
    hs = np.array([colorsys.rgb_to_hls(*p)[0] for p in rgb[keep][::max(1, keep.sum()//4000)]])
    ang = hs*2*np.pi; h = (np.arctan2(np.sin(ang).mean(), np.cos(ang).mean())/(2*np.pi)) % 1   # main hue of the print
    def score(name):
        c = [(x + y)/2/255 for x, y in zip(*BG[name])]; bh = colorsys.rgb_to_hls(*c)[0]
        return min(abs(bh - h), 1 - abs(bh - h))
    return sorted(ORDER, key=score, reverse=True)

def per_picture(print_path, n, fixed=None, shift=0):
    """n backdrops, one per picture, all different (fixed: one colour Andy chose for every picture). shift turns the best n
    round so products with similar prints still lead with different colours across the range."""
    if fixed and fixed in BG: return [fixed]*n
    top = ranked(print_path)[:max(n, 3)]; k = int(shift) % len(top)
    top = top[k:] + top[:k]; return [top[i % len(top)] for i in range(n)]
