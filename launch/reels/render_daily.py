import subprocess, sys, math
exec(open('frames5.py').read().split('out = []')[0])  # helpers, fonts, colours, pieces
FPS = 30; DUR = 15
def ease(t): return 1 - (1 - t) ** 3
def clamp(t): return max(0.0, min(1.0, t))
BG = grid_bg(1.0)
BLACK = Image.new('RGBA', (W, H), (4, 4, 6, 255))
# layers for scene 1
full = Image.open('/home/claude/sc-assets/brand/logos/SC_full_logo_chrome_transparent.png').convert('RGBA'); full.thumbnail((W - 2 * M, 700), Image.LANCZOS)
glow1 = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(glow1).ellipse((W // 2 - 480, 860 - 260, W // 2 + 480, 860 + 260), fill=(255, 255, 255, 70)); glow1 = glow1.filter(ImageFilter.GaussianBlur(120))
seal = Image.new('RGBA', (W, H), (0, 0, 0, 0)); text_c(seal, 1260, 'ARCHIVE SEALED 1994', 72, RED, sp=8)
# scene 2 layers
vign = grid_bg(0.0)
dt = Image.new('RGBA', (W, H), (0, 0, 0, 0)); text_c(dt, 1700, 'DRAFTING TABLE 03', 56, CYAN, sp=8)
# scene 3
six = Image.new('RGBA', (W, H), (0, 0, 0, 0)); text_c(six, 820, 'SIX HEROES', 150, WHITE, sp=8, glow=CYAN + (140,)); rule(six, 1010)
six2 = Image.new('RGBA', (W, H), (0, 0, 0, 0)); text_c(six2, 1050, 'ONE FILE EACH', 64, CYAN, sp=10)
cards = [Image.open('c%d.png' % i).convert('RGBA') for i in range(6)]
# scene 10/11
top = Image.new('RGBA', (W, H), (0, 0, 0, 0)); text_c(top, 430, 'THE BLUEPRINT', 150, WHITE, sp=6, glow=CYAN + (140,)); rule(top, 650)
lower10 = Image.new('RGBA', (W, H), (0, 0, 0, 0)); text_c(lower10, 1230, 'ONE-OF-ONE PIECES', 86, CYAN, sp=10); text_c(lower10, 1500, 'PICK YOUR PIECE', 72, WHITE, sp=8)
LABEL = sys.argv[1]; LINE2 = sys.argv[2]; OUT = sys.argv[3]
lower11 = Image.new('RGBA', (W, H), (0, 0, 0, 0))
text_c(lower11, 730, LABEL, 170, RED, sp=10, glow=RED + (150,)); text_c(lower11, 960, 'OPENSEA', 110, CYAN, sp=14); text_c(lower11, 1100, LINE2, 64, WHITE, sp=6)
text_c(lower11, 1250, 'PAY BY CARD OR POL', 60, WHITE, sp=6); text_c(lower11, 1400, 'LINK IN BIO', 86, RED, sp=10)
lg = Image.open(LOGO).convert('RGBA'); lg.thumbnail((260, 260), Image.LANCZOS)
logo11 = Image.new('RGBA', (W, H), (0, 0, 0, 0)); logo11.alpha_composite(lg, ((W - lg.width) // 2, 1580))
numcache = {}
def number(n):
    if n not in numcache:
        l = Image.new('RGBA', (W, H), (0, 0, 0, 0)); text_c(l, 760, str(n), 360, WHITE, sp=12, glow=CYAN + (120,)); numcache[n] = l
    return numcache[n]
def with_alpha(layer, a):
    if a >= 1: return layer
    l = layer.copy(); l.putalpha(l.getchannel('A').point(lambda v: int(v * a))); return l
def zoomed(img, z):
    if z == 1: return img
    nw, nh = int(W * z), int(H * z); big = img.resize((nw, nh), Image.BILINEAR); x = (nw - W) // 2; y = (nh - H) // 2
    return big.crop((x, y, x + W, y + H))
def scaled_layer(layer, s, cy=960):
    nw, nh = int(W * s), int(H * s); big = layer.resize((nw, nh), Image.BILINEAR)
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0)); out.alpha_composite(big, ((W - nw) // 2, int(cy - (cy - 0) * s)))
    return out
def frame(t):
    if t < 1.5:
        im = BLACK.copy()
        if t >= 0.3:
            k = ease(clamp((t - 0.3) / 0.25)); im.alpha_composite(with_alpha(glow1, k))
            s = 1.25 - 0.25 * k; lw = int(full.width * s); lh = int(full.height * s)
            im.alpha_composite(with_alpha(full.resize((lw, lh), Image.BILINEAR), k), ((W - lw) // 2, 860 - lh // 2))
            if t < 0.45: im.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(200 * (1 - (t - 0.3) / 0.15)))))
        if t >= 0.9: im.alpha_composite(with_alpha(seal, clamp((t - 0.9) / 0.2)))
        if t > 1.3: im.alpha_composite(Image.new('RGBA', (W, H), (4, 4, 6, int(255 * (t - 1.3) / 0.2))))
        return im
    if t < 3.0:
        p = clamp((t - 1.5) / 1.1); im = grid_bg(p, lamp=int(200 + 680 * clamp((t - 1.5) / 1.4)))
        if t >= 2.2: im.alpha_composite(with_alpha(dt, clamp((t - 2.2) / 0.2)))
        return im
    if t < 4.0:
        im = BG.copy(); k = ease(clamp((t - 3.0) / 0.3)); s = 1.3 - 0.3 * k
        im.alpha_composite(with_alpha(scaled_layer(six, s, 900), k))
        if t >= 3.35: im.alpha_composite(with_alpha(six2, clamp((t - 3.35) / 0.2)))
        return im
    if t < 10.0:
        i = min(5, int(t - 4.0)); u = t - 4.0 - i; k = ease(clamp(u / 0.15))
        z = (1.12 - 0.12 * k) if u < 0.15 else 1.0 + 0.04 * (u - 0.15) / 0.85
        im = zoomed(cards[i], z)
        if u < 0.1: im.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(120 * (1 - u / 0.1)))))
        return im
    if t < 12.0:
        im = BG.copy(); u = t - 10.0
        if u < 0.2: im.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(255 * (1 - u / 0.2)))))
        k = ease(clamp(u / 0.35)); im.alpha_composite(with_alpha(scaled_layer(top, 1.2 - 0.2 * k, 500), k))
        if u >= 0.3:
            r = ease(clamp((u - 0.3) / 1.1)); n = int(round(339 * r)); im.alpha_composite(number(n))
        if u >= 0.5: im.alpha_composite(with_alpha(lower10, clamp((u - 0.5) / 0.3)))
        return im
    im = BG.copy(); im.alpha_composite(top); u = t - 12.0
    if u < 0.35:
        a = 1 - u / 0.35; im.alpha_composite(with_alpha(number(339), a)); im.alpha_composite(with_alpha(lower10, a))
    else:
        k = ease(clamp((u - 0.35) / 0.35)); im.alpha_composite(with_alpha(lower11, k))
    if u >= 0.9: im.alpha_composite(with_alpha(logo11, clamp((u - 0.9) / 0.4)))
    return im
if __name__ == '__main__':
    N = FPS * DUR
    p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H), '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', OUT], stdin=subprocess.PIPE)
    for f in range(N):
        im = frame(f / FPS); p.stdin.write(im.convert('RGB').tobytes())
        if f % 60 == 0: print(f, flush=True)
    p.stdin.close(); p.wait(); print('video ok')
