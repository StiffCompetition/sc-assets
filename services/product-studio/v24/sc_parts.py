"""SC design parts: cuts an approved t-shirt print (Hammerin' Hanky set layout) into its library parts.
Every SC print uses the same set lines (T-Shirt Products Playbook, set layout 18 Oct 2026), so the parts are cut by band:
  picture  above the name line            (no text)
  name     the character name line
  phrase   the two phrase lines, kept together with their set line gap
  logo     the lockup (Always Standing Tall / Stiff Competition / Est. 1994)
  python3 sc_parts.py <print.png> <out_prefix>     -> out_prefix_picture.png, _name.png, _phrase.png, _logo.png
Parts keep the print's pixels and scale (300 dpi at shirt size); nothing is redrawn."""
import sys
import numpy as np
from PIL import Image

BANDS = {'picture': (0, 3180), 'name': (3180, 3420), 'phrase': (3420, 4136), 'logo': (4136, 4800)}

def trim(im):
    a = np.asarray(im)[..., 3]; ys, xs = np.where(a > 10)
    return im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)) if len(xs) else None

def cut(print_path):
    P = Image.open(print_path).convert('RGBA')
    if P.size != (3600, 4800): raise SystemExit('Not an SC t-shirt print (3600 x 4800): ' + str(P.size))
    return {k: trim(P.crop((0, y0, P.width, y1))) for k, (y0, y1) in BANDS.items()}

if __name__ == '__main__':
    parts = cut(sys.argv[1])
    for k, im in parts.items():
        if im is None: print('missing part', k); continue
        im.save(f'{sys.argv[2]}_{k}.png', dpi=(300, 300)); print(k, im.size)
