#!/usr/bin/env python3
"""SC animated GIPHY sticker from a clean clip (11 Nov 2026).
python3 make_sticker.py SRC.mp4 OUT.gif "CAPTION"
Cut-out figure (rembg), white outline, yellow caption with black edge at the top, see-through background,
512x512, 12 fps, loops. No overlay, no handle on the picture (stickers carry no overlay, GIF OVERLAY RULES 7).
GIPHY counts a GIF as a sticker when 20% or more of the first frame is transparent."""
import sys, os, subprocess, glob, tempfile
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from rembg import remove, new_session
src, out, cap = sys.argv[1], sys.argv[2], sys.argv[3].upper()
S = 512
tmp = tempfile.mkdtemp()
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-vf', 'fps=12,scale=480:-1:flags=lanczos', f'{tmp}/f%03d.png'], check=True)
files = sorted(glob.glob(f'{tmp}/f*.png'))[:48]
sess = new_session('u2net')
cut = [remove(Image.open(f).convert('RGB'), session=sess) for f in files]
# one crop box for the whole clip so the figure does not jitter
box = None
for c in cut:
    b = c.getchannel('A').point(lambda v: 255 if v > 40 else 0).getbbox()
    if b: box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
bw, bh = box[2] - box[0], box[3] - box[1]
AREA_TOP = 120; AREA_H = S - AREA_TOP - 12; AREA_W = S - 24
sc = min(AREA_W / bw, AREA_H / bh)
font = None
for p in ['/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf', '/usr/share/fonts/opentype/inter/Inter-Black.otf', '/usr/share/fonts/opentype/inter/Inter-Bold.otf']:
    if os.path.exists(p): font = p; break
size = 92
while True:
    ft = ImageFont.truetype(font, size)
    bb = ImageDraw.Draw(Image.new('RGBA', (10, 10))).textbbox((0, 0), cap, font=ft, stroke_width=9)
    if bb[2] - bb[0] <= S - 36 or size < 30: break
    size -= 4
frames = []
for c in cut:
    fig = c.crop(box).resize((max(1, int(bw * sc)), max(1, int(bh * sc))), Image.LANCZOS)
    a = fig.getchannel('A')
    ring = a.filter(ImageFilter.MaxFilter(13)).filter(ImageFilter.GaussianBlur(1.2))
    white = Image.new('RGBA', fig.size, (255, 255, 255, 255)); white.putalpha(ring)
    pad = Image.new('RGBA', (fig.width + 24, fig.height + 24), (0, 0, 0, 0))
    pad.alpha_composite(white, (12, 12)); pad.alpha_composite(fig, (12, 12))
    f = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    f.alpha_composite(pad, ((S - pad.width) // 2, S - pad.height - 4 if pad.height < AREA_H + 24 else AREA_TOP - 12))
    d = ImageDraw.Draw(f)
    tw = d.textlength(cap, font=ft)
    d.text(((S - tw) / 2, 18), cap, font=ft, fill=(255, 205, 0, 255), stroke_width=9, stroke_fill=(0, 0, 0, 255))
    frames.append(f)
def q(im):  # GIF needs a 1-bit alpha: palette with a transparent index
    a = im.getchannel('A'); p = im.convert('RGB').quantize(255, dither=Image.NONE)
    p.paste(255, Image.eval(a, lambda v: 255 if v < 128 else 0)); return p
P = [q(f) for f in frames]
P[0].save(out, save_all=True, append_images=P[1:], duration=83, loop=0, transparency=255, disposal=2, optimize=False)
t = frames[0].getchannel('A').point(lambda v: 255 if v < 128 else 0)
print(out, os.path.getsize(out) // 1024, 'KB', len(P), 'frames', 'first-frame transparent %.0f%%' % (100 * sum(t.getdata()) / 255 / (S * S)))
