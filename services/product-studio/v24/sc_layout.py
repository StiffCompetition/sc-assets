"""SC layout: fits approved design parts into any Gelato template's print area.
  python3 sc_layout.py design.png out.png <area_w_px> <area_h_px> centre [margin_frac] [background]
      one design, centred (t-shirt fronts, posters, tote bags)
  python3 sc_layout.py sides <spec.json or the JSON itself> out.png <area_w_px> <area_h_px>
      a wraparound print (mugs) with a DIFFERENT layout on each side. spec.json:
        {"sides": [["picture", "name", "phrase"], ["logo"]],      parts on side 1 and on side 2, top to bottom
         "files": {"picture": "picture.png", "name": "name.png", "phrase": "phrase.png", "logo": "logo.png"},
         "side1": "left" | "right",                                which half of the wrap holds side 1
         "margin": 0.07}                                           free space round each side, share of the side
      Parts are stacked in the t-shirt order (picture, name, phrase, logo) with the set gap between them, centred,
      and the stack is scaled to fit its half of the wrap. Each side is centred on its half, so it sits in the middle
      of one face of the mug. Parts are only scaled, never redrawn or stretched, and never enlarged past their own
      pixels (the result prints the effective resolution so the caller can check it).
  python3 sc_layout.py areas <spec.json or the JSON itself>
      one print file per print area (front, back, ...) of a garment template (Andy, 19 Oct 2026). spec:
        {"areas": [{"out": "front_dark.png", "w": 4205, "h": 5606, "top": 0 (optional, share left empty at the top), "files": ["picture.png", "name.png", ...]}, ...],
         "margin": 0.06}
      Each area's files are stacked top to bottom in the order given with the set gap, scaled to fill the area
      (inside the margin, never enlarged past 300 dpi), centred across and set at the top of the area. One file on its own (the approved whole print) is simply centred."""
import sys, json
from PIL import Image

ORDER = ['picture', 'name', 'phrase', 'logo']
GAP = 120   # gap between stacked parts at t-shirt print scale (picture to name line on the set)

def trim(im):
    bb = im.getbbox(); return im.crop(bb) if bb else im

def fit(design, w, h, margin, max_scale=None):
    d = trim(design)
    s = min(w*(1 - 2*margin)/d.width, h*(1 - 2*margin)/d.height)
    if max_scale: s = min(s, max_scale)
    return d.resize((max(1, round(d.width*s)), max(1, round(d.height*s))), Image.LANCZOS), s

def stack(parts):
    parts = [trim(p) for p in parts]
    W = max(p.width for p in parts); H = sum(p.height for p in parts) + GAP*(len(parts) - 1)
    S = Image.new('RGBA', (W, H), (0, 0, 0, 0)); y = 0
    for p in parts: S.alpha_composite(p, ((W - p.width)//2, y)); y += p.height + GAP
    return S

def report(name, s, d):
    print(f'{name}: scaled x{s:.3f} to {d.width}x{d.height}; prints at {300/s:.0f} dpi ({"OK" if s <= 1.5 else "UPSCALED"})')

def centre(src, out, w, h, margin=0.06, bg='none'):
    w, h = int(w), int(h); D = Image.open(src).convert('RGBA')
    C = Image.new('RGBA', (w, h), (0, 0, 0, 0) if bg == 'none' else tuple(int(bg[i:i+2], 16) for i in (0, 2, 4)) + (255,))
    d, s = fit(D, w, h, margin); C.alpha_composite(d, ((w - d.width)//2, (h - d.height)//2))
    C.save(out, dpi=(300, 300)); report(f'layout centre in {w}x{h}', s, d)

def sides(spec_path, out, w, h):
    sp = json.loads(spec_path) if spec_path.lstrip().startswith('{') else json.load(open(spec_path)); w, h = int(w), int(h); half = w//2; m = float(sp.get('margin', 0.07))
    C = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    lefts = (0, half) if sp.get('side1', 'left') == 'left' else (half, 0)
    if sp.get('single'): half, lefts = w, (0, 0)   # one print area, no wrap halves (water bottle, Andy 20 Oct 2026)
    if sp.get('place'):
        # placed by Andy in the Products tab (20 Oct 2026): each image at its own spot and size on its side.
        # x, y = centre as a share of the side's width and height; w = width as a share of the side's width.
        stacked = [int(x) for x in (sp.get('stack') or [])]
        for n, (items, x0) in enumerate(zip(sp['place'], lefts), 1):
            if not items: print(f'side {n}: empty'); continue
            if n in stacked:
                # 'Stack neatly' (Andy, 20 Oct 2026): this character's own images one under the other, top to bottom in the
                # order set in the Products tab, filling 86% of the side, the same rule as the Products tab preview
                items = sorted(items, key=lambda it: float(it['y']))
                ims = [Image.open(it['file']).convert('RGBA') for it in items]
                gap = 120*h/1000; W = max(i.width for i in ims); H = sum(i.height for i in ims) + gap*(len(ims) - 1)
                k = min(0.86*half/W, 0.86*h/H); y = (h - H*k)/2; items = [dict(it) for it in items]
                for it, im in zip(items, ims):
                    it['w'] = im.width*k/half; it['x'] = 0.5; it['y'] = (y + im.height*k/2)/h; y += (im.height + gap)*k
            S = Image.new('RGBA', (half, h), (0, 0, 0, 0))   # the side on its own, so nothing spills onto the other face
            for it in items:
                d0 = Image.open(it['file']).convert('RGBA')   # not trimmed: the Products tab shows the whole image, so the print matches it exactly
                tw = max(1, float(it['w'])*half); s = tw/d0.width
                if s > 1.5: s = 1.5   # never printed below 200 dpi (Gelato: 150 minimum, 300 ideal)
                d = d0.resize((max(1, round(d0.width*s)), max(1, round(d0.height*s))), Image.LANCZOS)
                L = Image.new('RGBA', (half, h), (0, 0, 0, 0))
                L.paste(d, (round(float(it['x'])*half - d.width/2), round(float(it['y'])*h - d.height/2)))   # anything past the edge is cut off
                S = Image.alpha_composite(S, L)
                report(f"side {n}: {it['file']} at {float(it['x']):.2f},{float(it['y']):.2f}", s, d)
            C.alpha_composite(S, (x0, 0))
        C.save(out, dpi=(300, 300)); print(f'wrap {w}x{h} written (placed)'); return
    for n, (names, x0) in enumerate(zip(sp['sides'], lefts), 1):
        names = [p for p in ORDER if p in names]
        if not names: print(f'side {n}: empty'); continue
        S = stack([Image.open(sp['files'][p]).convert('RGBA') for p in names])
        d, s = fit(S, half, h, m, max_scale=1.0)
        C.alpha_composite(d, (x0 + (half - d.width)//2, (h - d.height)//2))
        report(f'side {n} ({", ".join(names)}) on the {"left" if x0 == 0 else "right"} half', s, d)
    C.save(out, dpi=(300, 300)); print(f'wrap {w}x{h} written')

def areas(spec_path):
    sp = json.loads(spec_path) if spec_path.lstrip().startswith('{') else json.load(open(spec_path)); m = float(sp.get('margin', 0.06))
    for A in sp['areas']:
        w, h = int(A['w']), int(A['h'])
        C = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        S = stack([Image.open(f).convert('RGBA') for f in A['files']])
        # fills the print area (Andy, 19 Oct 2026: use the maximum space); enlarged at most 1.5x so it never prints below 200 dpi (Gelato: 150 dpi minimum, 300 ideal)
        # 'top': part of the area left empty at the top (hoodie backs: the hood lies over it, Andy 19 Oct 2026)
        t = float(A.get('top', 0)); ht = int(h*(1 - t))
        d, s = fit(S, w, ht, m, max_scale=1.5); C.alpha_composite(d, ((w - d.width)//2, int(h*t) + round(ht*m)))   # top of the area, as garments are printed
        C.save(A['out'], dpi=(300, 300)); report(f"{A['out']} ({', '.join(A['files'])}) in {w}x{h}", s, d)

if __name__ == '__main__':
    a = sys.argv[1:]
    if a[0] == 'areas': areas(a[1])
    elif a[0] == 'sides': sides(a[1], a[2], a[3], a[4])
    else: centre(a[0], a[1], a[2], a[3], float(a[5]) if len(a) > 5 else 0.06, a[6] if len(a) > 6 else 'none')
