from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H = 1080, 1920
M = 90  # fixed side margin
NAVY = (8, 22, 44); CYAN = (79, 209, 255); WHITE = (245, 247, 250); RED = (212, 31, 42); INK = (10, 14, 22)
ANTON = 'fonts/package/files/anton-latin-400-normal.woff'
LOGO = '/home/claude/sc-assets/brand/logos/SC_square_logo_chrome_transparent.png'
INTER = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'
def font(s): return ImageFont.truetype(ANTON, s)
def width(d, s, f, sp): return d.textlength(s, font=f) + sp * (len(s) - 1)
def fit(d, s, size, sp, maxw=W - 2 * M):
    f = font(size)
    while width(d, s, f, sp) > maxw and size > 40: size -= 4; f = font(size)
    return f
def text_c(img, y, s, size, fill, sp=4, glow=None):
    d = ImageDraw.Draw(img); f = fit(d, s, size, sp); w = width(d, s, f, sp); x = (W - w) / 2
    if glow:
        g = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g); xx = x
        for ch in s: gd.text((xx, y), ch, font=f, fill=glow); xx += d.textlength(ch, font=f) + sp
        g = g.filter(ImageFilter.GaussianBlur(16)); img.alpha_composite(g); img.alpha_composite(g); d = ImageDraw.Draw(img)
    xx = x
    for ch in s: d.text((xx, y), ch, font=f, fill=fill); xx += d.textlength(ch, font=f) + sp
    return f.getbbox('H')[3]
def rule(img, y, w=420, col=CYAN): ImageDraw.Draw(img).rectangle((W // 2 - w // 2, y, W // 2 + w // 2, y + 5), fill=col)
def grid_bg(progress=1.0, lamp=None):
    im = Image.new('RGBA', (W, H), NAVY + (255,))
    v = Image.new('L', (W, H), 0); ImageDraw.Draw(v).ellipse((-200, -100, W + 200, H + 100), fill=255); v = v.filter(ImageFilter.GaussianBlur(260))
    im = Image.composite(im, Image.alpha_composite(im, Image.new('RGBA', (W, H), (0, 0, 0, 150))), v)
    d = ImageDraw.Draw(im); step = 90; n = int((W // step + H // step + 2) * progress); k = 0
    for x in range(0, W + 1, step):
        if k >= n: break
        d.line((x, 0, x, H), fill=CYAN + (38 if x % 270 else 80,), width=1); k += 1
    for y in range(0, H + 1, step):
        if k >= n: break
        d.line((0, y, W, y), fill=CYAN + (38 if y % 270 else 80,), width=1); k += 1
    if lamp is not None:
        l = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(l).polygon([(lamp - 140, 0), (lamp + 140, 0), (lamp + 460, H), (lamp - 460, H)], fill=CYAN + (34,))
        im.alpha_composite(l.filter(ImageFilter.GaussianBlur(70)))
    return im
def framed(piece, size):
    p = Image.open(piece).convert('RGB').resize((size, size), Image.LANCZOS)
    f = Image.new('RGBA', (size + 24, size + 24), (0, 0, 0, 0)); ImageDraw.Draw(f).rectangle((0, 0, size + 23, size + 23), fill=INK + (255,), outline=CYAN + (255,), width=3)
    f.paste(p, (12, 12)); return f
def shadow(im, box, blur=28, a=160):
    s = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(s).rectangle(box, fill=(0, 0, 0, a)); im.alpha_composite(s.filter(ImageFilter.GaussianBlur(blur)))
pieces = [('0004_major_wood.jpg', 'MAJOR WOOD', '#0004'), ('0016_hanky.jpg', "HAMMERIN' HANKY", '#0016'), ('0017_rear_admiral.jpg', 'THE REAR ADMIRAL', '#0017'), ('0011_grip.jpg', 'THE GRIP', '#0011'), ('0013_python.jpg', 'THE VELVET PYTHON', '#0013'), ('0010_willy.jpg', 'SLICK WILLY', '#0010')]
out = []
# 1 opening
im = Image.new('RGBA', (W, H), (4, 4, 6, 255))
full = Image.open('/home/claude/sc-assets/brand/logos/SC_full_logo_chrome_transparent.png').convert('RGBA'); full.thumbnail((W - 2 * M, 700), Image.LANCZOS)
g = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse((W // 2 - 480, 860 - 260, W // 2 + 480, 860 + 260), fill=(255, 255, 255, 70)); im.alpha_composite(g.filter(ImageFilter.GaussianBlur(120)))
im.alpha_composite(full, ((W - full.width) // 2, 860 - full.height // 2))
text_c(im, 1260, 'ARCHIVE SEALED 1994', 72, RED, sp=8)
im.save('g1.png'); out.append(('0-1.5 s  black, bolt thud, logo flashes up', 'g1.png'))
# 2 grid
im = grid_bg(0.55, lamp=420)
text_c(im, 1700, 'DRAFTING TABLE 03', 56, CYAN, sp=8)
im.save('g2.png'); out.append(('1.5-3 s  grid draws itself, lamp sweeps', 'g2.png'))
# 3/4 file cards: picture 900 wide, centred, text block below on a fixed baseline grid
def card(i):
    im = grid_bg(1.0); pc, name, num = pieces[i]; fr = framed(pc, 900); x = (W - fr.width) // 2; y = 250
    shadow(im, (x + 18, y + 28, x + fr.width + 18, y + fr.height + 28)); im.alpha_composite(fr, (x, y))
    text_c(im, 1230, 'FILE %02d' % (i + 1), 64, CYAN, sp=10)
    text_c(im, 1310, name, 130, WHITE, sp=4, glow=CYAN + (110,))
    rule(im, 1480)
    text_c(im, 1515, 'BLUEPRINT ' + num + '  ·  ONE OF ONE', 56, WHITE, sp=5)
    text_c(im, 1735, 'OPENSEA  ·  10 NOVEMBER', 52, CYAN, sp=8)
    return im
im = grid_bg(1.0)
text_c(im, 820, 'SIX HEROES', 150, WHITE, sp=8, glow=CYAN + (140,))
rule(im, 1010)
text_c(im, 1050, 'ONE FILE EACH', 64, CYAN, sp=10)
im.save('g25.png'); out.append(('3-4 s  SIX HEROES title card', 'g25.png'))
for i in range(6):
    card(i).save('c%d.png' % i); out.append(('%d-%d s  FILE %02d snaps in, slow push-in' % (4 + i, 5 + i, i + 1), 'c%d.png' % i))


# 10 title + counter (no logo), 11 end card (logo only here)
lg = Image.open(LOGO).convert('RGBA')
def title_top(im):
    text_c(im, 430, 'THE BLUEPRINT', 150, WHITE, sp=6, glow=CYAN + (140,)); rule(im, 650)
im = grid_bg(1.0); title_top(im)
text_c(im, 760, '339', 360, WHITE, sp=12, glow=CYAN + (120,))
text_c(im, 1230, 'ONE-OF-ONE PIECES', 86, CYAN, sp=10)
text_c(im, 1500, 'PICK YOUR PIECE', 72, WHITE, sp=8)
im.save('g7.png'); out.append(('10-12 s  title lands, counter rolls to 339', 'g7.png'))
im = grid_bg(1.0); title_top(im)
text_c(im, 760, 'OPENSEA', 130, CYAN, sp=14)
text_c(im, 940, '10 NOVEMBER', 96, WHITE, sp=8)
text_c(im, 1065, '16:00 LONDON', 72, WHITE, sp=8)
text_c(im, 1250, 'PAY BY CARD OR POL', 60, WHITE, sp=6)
text_c(im, 1400, 'LINK IN BIO', 86, RED, sp=10)
s2 = lg.copy(); s2.thumbnail((260, 260), Image.LANCZOS); im.alpha_composite(s2, ((W - s2.width) // 2, 1580))
im.save('g8.png'); out.append(('12-15 s  date and link; SC logo signs off', 'g8.png'))
cw, ch, pad, cap, cols = 540, 960, 40, 60, 4
rows = (len(out) + cols - 1) // cols
sheet = Image.new('RGB', (cols * cw + (cols + 1) * pad, rows * (ch + cap) + (rows + 1) * pad + 80), (24, 24, 28)); sd = ImageDraw.Draw(sheet)
sd.text((pad, 24), 'THE BLUEPRINT  ·  countdown Reel storyboard  ·  1080x1920  ·  15 s  ·  %d frames in order' % len(out), font=ImageFont.truetype(INTER, 38), fill=WHITE)
for i, (c, f) in enumerate(out):
    r, ci = divmod(i, cols); x = pad + ci * (cw + pad); y = 80 + pad + r * (ch + cap + pad)
    sheet.paste(Image.open(f).convert('RGB').resize((cw, ch), Image.LANCZOS), (x, y))
    sd.text((x, y + ch + 10), '%d.  %s' % (i + 1, c), font=ImageFont.truetype(INTER, 22), fill=WHITE)
sheet.save('storyboard5.jpg', quality=90); print('ok', len(out))
