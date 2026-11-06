#!/usr/bin/env python3
"""Stiff Competition GIF builder. ONE GIF, TWO overlays (Andy's rules, 6 Nov 2026).
Usage: python3 sc_gif.py SRC.mp4 NAME "CAPTION" HIT_SECONDS [TOP_PX]
Writes NAME_giphy.gif (for GIPHY) and NAME_page.gif (for the shop page / direct downloads).
Needs ffmpeg + Pillow + numpy. Geometry is in 480px GIF pixels, measured from WhatsApp's GIPHY stamp."""
import sys, os, subprocess, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
MONT = HERE + '/fonts/montserrat-800.woff'; INTER = HERE + '/fonts/inter-800.woff'
BAND = HERE + '/sc_outline_band.png'
W = 480
GX0, GX1, GTOP, GBASE = 25, 94, 451, 466      # WhatsApp GIPHY stamp: left, right, cap top, baseline
TIME_X = 370                                  # WhatsApp time/tick start (keep clear)
COL, ALPHA = (255, 250, 235), 166             # GIPHY stamp colour and ~65% opacity, measured from WhatsApp
S = 4                                         # supersample for smooth corners

def overlay(mode):
    """mode 'giphy': SC box sits above the GIPHY word spot. mode 'page': SC box sits in the GIPHY word spot."""
    band = np.array(Image.open(BAND)) > 0
    tw = (GX1 - GX0) * S; pad = 4 * S; lw = tw - 2 * pad
    lh = round(band.shape[0] * lw / band.shape[1]); th = lh + 2 * pad     # box exactly as wide as the word GIPHY
    bottom = (GBASE if mode == 'page' else GTOP - 7) * S
    y0, x0 = bottom - th, GX0 * S
    L = Image.new('RGBA', (W * S, W * S), (0, 0, 0, 0))
    tile = Image.new('L', L.size, 0)
    ImageDraw.Draw(tile).rounded_rectangle((x0, y0, x0 + tw - 1, bottom - 1), radius=9 * S, fill=ALPHA)
    white = Image.new('RGBA', L.size, COL + (255,)); white.putalpha(tile); L.alpha_composite(white)
    b = Image.new('L', L.size, 0)
    b.paste(Image.fromarray((band * 255).astype(np.uint8)).resize((lw, lh), Image.LANCZOS), (x0 + pad, y0 + pad))
    dark = Image.new('RGBA', L.size, (15, 15, 15, 255)); dark.putalpha(b.point(lambda v: int(v * .9)))
    L.alpha_composite(dark)
    L = L.resize((W, W), Image.LANCZOS)
    F = ImageFont.truetype(MONT, 21); s = '@STIFFCOMP'
    x = (GX1 + TIME_X) / 2 - ImageDraw.Draw(L).textlength(s, font=F) / 2   # centred between GIPHY and the time
    sh = Image.new('RGBA', (W, W), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((x + 1, GBASE + 1), s, font=F, fill=(0, 0, 0, 90), anchor='ls')
    L.alpha_composite(sh.filter(ImageFilter.GaussianBlur(1.2)))
    ImageDraw.Draw(L).text((x, GBASE), s, font=F, fill=COL + (ALPHA,), anchor='ls')
    return L

def caption(im, text, size, age_frames):
    sc = [1.35, 1.15, 1.0][min(age_frames, 2)]
    ff = ImageFont.truetype(INTER, int(size * sc)); d0 = ImageDraw.Draw(im)
    bb = d0.textbbox((0, 0), text, font=ff, stroke_width=2); tw = bb[2] - bb[0]; th = bb[3] - bb[1]
    x = (W - tw) // 2 - bb[0]; y = int(W * .075) - th // 2 - bb[1]     # text only in the top area
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).text((x + 1, y + 2), text, font=ff, fill=(0, 0, 0, 170))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(2)))
    ImageDraw.Draw(im).text((x, y), text, font=ff, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))

def make(mp4, name, text=None, hit=0.0, top=None, start=0.0, end=None, hold=0.8, fps=12, size=30, boom=False, box=None):
    """box=(x,y,w,h): crop this region of the source before resizing to 480 (default: centred square, top at `top`)."""
    tmp = tempfile.mkdtemp()
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(start)] + (['-to', str(end)] if end else []) +
                   ['-i', mp4, '-vf', f'fps={fps}', f'{tmp}/r%04d.png'], check=True)
    fr = sorted(f for f in os.listdir(tmp) if f.startswith('r')); fr += [fr[-1]] * int(hold * fps)
    if boom: fr = fr + fr[-2:0:-1]
    ov = {m: overlay(m) for m in ('giphy', 'page')}
    for i, n in enumerate(fr):
        im = Image.open(f'{tmp}/{n}').convert('RGB'); w, h = im.size; s = min(w, h)
        t0 = top if top is not None else (h - s) // 2
        im = im.crop((box[0], box[1], box[0] + box[2], box[1] + box[3]) if box else ((w - s) // 2, t0, (w - s) // 2 + s, t0 + s)).resize((W, W), Image.LANCZOS).convert('RGBA')
        t = i / fps
        if text and (t >= hit or boom):
            caption(im, text, size, int((((hit + 1) if boom else t) - hit) * fps))
        for m in ov:
            o = im.copy(); o.alpha_composite(ov[m]); o.convert('RGB').save(f'{tmp}/{m}{i:04d}.png')
    out = {}
    for m in ov:
        p = f'{name}_{m}.gif'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(fps), '-i', f'{tmp}/{m}%04d.png', '-filter_complex',
                        '[0]split[a][b];[a]palettegen=max_colors=256:stats_mode=single[p];[b][p]paletteuse=new=1:dither=none',
                        '-loop', '0', p], check=True)
        out[m] = (p, os.path.getsize(p))
    return out

if __name__ == '__main__':
    a = sys.argv
    print(make(a[1], a[2], a[3] if len(a) > 3 and a[3] != '-' else None, float(a[4]) if len(a) > 4 else 0.0, int(a[5]) if len(a) > 5 else None))
