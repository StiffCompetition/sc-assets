"""Mug wrap builder. python3 mug_build.py pic_cut.png logo_cut.png NAME L1 L2 out_prefix [crop_frac]
Text drawn as whole words with the font's own kerning (raqm), word gaps set by hand: no per-letter placement."""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
pic_f, logo_f, NAME, L1, L2, out = sys.argv[1:7]; crop = float(sys.argv[7]) if len(sys.argv) > 7 else 0.14
WW, HH = 1258, 1217; MAXH = int(HH*0.985); MAXW = 893
F = 'alfa.ttf'
TRACK = 0.035
def word(w, sz):
    f = ImageFont.truetype(F, sz, layout_engine=ImageFont.Layout.RAQM); d = ImageDraw.Draw(Image.new('L', (1, 1)))
    im = Image.new('L', (int(sz*len(w)*1.3)+40, int(sz*1.6)), 0); dr = ImageDraw.Draw(im)
    for i, ch in enumerate(w):
        x = d.textlength(w[:i+1], font=f) - d.textlength(ch, font=f) + i*TRACK*sz
        dr.text((10 + x, int(sz*.2)), ch, font=f, fill=255)
    a = np.asarray(im); c = np.where(a.max(0) > 40)[0]; rr = np.where(a.max(1) > 40)[0]
    # shared baseline: rows fixed by the cap height of 'H' so punctuation never shifts a word
    hi = Image.new('L', im.size, 0); ImageDraw.Draw(hi).text((10, int(sz*.2)), 'H', font=f, fill=255)
    hr = np.where(np.asarray(hi).max(1) > 40)[0]; m = int(.03*sz)
    top = hr.min() - m; bot = max(rr.max()+1, hr.max()+1+m)
    return im.crop((c.min(), top, c.max()+1, bot))
def line(t, sz, gap=0.30):
    ws = [word(w, sz) for w in t.split(' ')]; g = int(gap*sz)
    W = sum(i.width for i in ws) + g*(len(ws)-1); H = max(i.height for i in ws)
    L = Image.new('L', (W, H), 0); x = 0
    for i in ws: L.paste(i, (x, 0)); x += i.width + g   # top-aligned = shared baseline
    return L
def fit(t, W, gap=0.30):
    sz = 400
    while line(t, sz, gap).width > W: sz = int(sz*0.97)
    while line(t, sz+1, gap).width <= W: sz += 1
    return line(t, sz, gap)
# picture: lose the bottom `crop` and refade higher
pic = Image.open(pic_f).convert('RGBA'); a = np.array(pic); h = a.shape[0]; keep = int(h*(1-crop)); a = a[:keep]
import os; fade = int(keep*float(os.environ.get("FADE","0.22"))); a[-fade:, :, 3] = (a[-fade:, :, 3]*np.linspace(1, 0, fade)[:, None]**1.3).astype(np.uint8)
pic = Image.fromarray(a); pa = pic.height/pic.width
def stack(W):
    l1, l2 = fit(L1, W), fit(L2, W); nm = fit(NAME, W)
    nm = nm.resize((W, int(nm.height*0.0 + W*0.075)), Image.LANCZOS) if False else nm
    # name band: height about 4% of W*... use name fit to width but cap height to 0.14 W
    if nm.height > 0.059*W: nm = nm.resize((int(nm.width*0.059*W/nm.height), int(0.059*W)), Image.LANCZOS)
    gp = int(0.047*W); ln = int(0.024*W); tot = int(W*pa) + gp + nm.height + ln + l1.height + ln + l2.height - int(0.04*W)
    return tot, l1, l2, nm, gp, ln
W = MAXW
while stack(W)[0] > MAXH: W -= 4
tot, l1, l2, nm, gp, ln = stack(W)
cv = Image.new('RGBA', (WW, HH), (0, 0, 0, 0)); x0 = (WW - W)//2; y = (HH - tot)//2
p = pic.resize((W, int(W*pa)), Image.LANCZOS); cv.alpha_composite(p, (x0, y)); y += p.height - int(0.04*W) + gp
for im in (nm, l1, l2):
    ink = Image.new('RGBA', im.size, (17, 17, 17, 255)); ink.putalpha(im); cv.alpha_composite(ink, ((WW - im.width)//2, y)); y += im.height + ln
cv.save(out + '_side1.png')
lg = Image.open(logo_f).convert('RGBA'); s = min(MAXW/lg.width, MAXH/lg.height); lg = lg.resize((int(lg.width*s), int(lg.height*s)), Image.LANCZOS)
c2 = Image.new('RGBA', (WW, HH), (0, 0, 0, 0)); c2.alpha_composite(lg, ((WW-lg.width)//2, (HH-lg.height)//2)); c2.save(out + '_side2.png')
wr = Image.new('RGBA', (2*WW, HH), (0, 0, 0, 0)); wr.alpha_composite(cv, (0, 0)); wr.alpha_composite(c2, (WW, 0)); wr.save(out + '_wrap.png')
for n, im in (('side1', cv), ('side2', c2)):
    g = Image.new('RGB', im.size, (222, 226, 232)); g.paste(im, mask=im.split()[3]); g.save(f'{out}_{n}_flat.jpg', quality=92)
print('column mm', round(W/11.82, 1), 'stack', tot, 'of', HH, 'widths', l1.width, l2.width, nm.width, 'logo', lg.size)
