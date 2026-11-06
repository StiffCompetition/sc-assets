"""SC recolour shirt: turns a studio photo of a model in a plain WHITE shirt into the same photo in any Gelato shirt colour.
  python3 sc_recolour_shirt.py pom/plain_female_white_main.jpg daisy pom/plain_female_daisy_main.jpg
Only the shirt changes: the shirt is found by rembg clothes segmentation (u2net_cloth_seg, free, runs locally), the face,
hair, skin and backdrop are left as they are, and the shirt's own folds and shadows are kept by multiplying the new colour by them.
Shirt colours are the Classic Unisex Crewneck (Gildan 64000) colours used in the Gelato template."""
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi
import sc_print_on_model as M
COLOURS = {'daisy': (246, 211, 57), 'red': (190, 30, 45), 'irish-green': (22, 140, 72), 'military-green': (92, 98, 66),
           'white': (250, 250, 250), 'light-blue': (165, 200, 230), 'black': (30, 30, 30), 'royal': (30, 70, 160), 'purple': (70, 40, 110)}
_S = None
def white_shirt_mask(img):
    """Shirt = rembg clothes segmentation (u2net_cloth_seg, free, runs locally; first band = upper-body clothes),
    with its outline smoothed so the low-resolution mask has no stair steps. Face, hair, skin and backdrop are untouched."""
    global _S
    from rembg import remove, new_session
    if _S is None: _S = new_session('u2net_cloth_seg')
    a = np.asarray(img).astype(float); H, W = a.shape[:2]
    cm = np.asarray(remove(img, session=_S, only_mask=True).convert('L')).astype(float)[:H] / 255
    m = ndi.gaussian_filter(cm, 4) > 0.5
    lab, _ = ndi.label(m)
    if lab[int(H*0.6), W//2]: m = lab == lab[int(H*0.6), W//2]
    return ndi.binary_fill_holes(m)
def recolour(src, colour, out):
    img = Image.open(src).convert('RGB'); a = np.asarray(img).astype(float)
    m = white_shirt_mask(img); L = M.lum(a); ref = np.percentile(L[m], 80)
    shade = np.clip(L/ref, 0, 1.1)[..., None]
    rec = np.clip(np.array(COLOURS[colour], float)*shade, 0, 255)
    al = ndi.gaussian_filter(m.astype(float), 1.5)[..., None]
    Image.fromarray((a*(1 - al) + rec*al).astype(np.uint8)).save(out, quality=95)
if __name__ == '__main__': recolour(*sys.argv[1:4])
