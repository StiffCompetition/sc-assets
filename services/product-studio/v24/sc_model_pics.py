"""SC model pictures: the one shared picture step for the model process and the Products tab (agreed 19 Oct 2026).
Standard: SC Models Playbook, section "Shop pictures: t-shirts and ringers". Method: plain green-screen base (magenta
t-shirt or white ringer) -> recolour to the variant colour -> place the print at its real size -> contrast backdrop -> fit check.
  python3 sc_model_pics.py <spec.json or the JSON itself>
  spec: {"pics": [{"out": "pic_01_main_navy.jpg", "base": "base_1.jpg", "kind": "tee" | "ring_front" | "ring_back",
                   "colour": "31,41,77", "print": "print_front_dark.png", "bg": "pink" (optional, picked by contrast),
                   "chest_cm": 53, "below_in": 2.0, "hood_tip": (hoodie backs: y of the hood tip), "hood_poly": (hoodie backs: outline of the hood, drawn over the print), "print_w_cm": (optional, print px / 300 x 2.54), "close": "pic_02_close.jpg"}]}
Writes report.json: one entry per picture with ok, reasons (fit check), backdrop used and print box."""
import sys, json, colorsys
from PIL import Image
import numpy as np
import sc_mp_tee as T, sc_mp_ring as R, sc_mp_fit as F

ORDER = ['pink', 'sky', 'orange', 'aqua', 'purple']

def pick_bg(rgb, used):
    """Backdrop that contrasts with the shirt: furthest hue (and, for greys, a bright warm or cool) from the shirt colour;
    the next best is used when the best was used on the picture before, so each picture gets its own backdrop."""
    h, l, s = colorsys.rgb_to_hls(*[c/255 for c in rgb])
    def score(name):
        c = [(x + y)/2/255 for x, y in zip(*T.BG[name])]; bh, bl, bs = colorsys.rgb_to_hls(*c)
        dh = min(abs(bh - h), 1 - abs(bh - h)) if s > 0.15 else 0.5
        return dh*2 + abs(bl - l)*0.6
    ranked = sorted(ORDER, key=score, reverse=True)
    return ranked[1] if ranked[0] == used and len(ranked) > 1 else ranked[0]


def finish(cut, bg, out, frac=1.0, garment=None):
    """SC Models Playbook framing (approved by Andy, 19 Oct 2026; finish.py in the build code doc): zoom so the person fills
    95% of the width (at most 1.35x), head 4.5% from the top, bottom cut to 90% of the height, then the backdrop.
    Writes the final picture and its cut-out; returns the scale and offset so the print box can be followed."""
    c = Image.open(cut).convert('RGBA'); W, H = c.size
    al = np.asarray(c)[..., 3] > 128; ys, xs = np.where(al); top, l, r = ys.min(), xs.min(), xs.max()
    # ONE framing rule for every model picture (Andy, 19 Oct 2026, matching the shop t-shirt set): the person, fists included,
    # fills the width with a 3% margin each side and the top of the head sits 3% below the top edge; the photo always reaches
    # the bottom edge. Measured on the cut-out, so it repeats exactly on any base photo.
    SIDE, TOP = 0.03, 0.03
    bot = ys.max()
    if garment == 'none':
        s, x0, y0 = 1.0, 0, 0
    elif isinstance(garment, dict):   # match the master photo: the hood lands at the master's hood size and position (Andy, 19 Oct 2026)
        g = garment; s = g['mw']/(g['r'] - g['l'])
        x0 = int((g['l'] + g['r'])/2*s - g['mcx']); y0 = int(g['top']*s - g['mtop'])
        y0 = min(y0, int(H*s) - H)   # never leave a gap under the photo
    elif garment:   # hoodie backs (Andy, 19 Oct 2026): every hoodie the same size and in the same place. Hood tip to hem is
        tip, hem, gx = garment                    # 52.2% of the picture height and the hood tip sits 56.7% down, centred on the
        s = 0.522*H/(hem - tip)                   # hoodie; set so the three base photos keep at least 3% beside the fists and
        x0 = int(gx*s - W/2); y0 = int(tip*s - 0.567*H)   # above the highest head
    else:
        s = (1 - 2*SIDE)*W/(r - l)
        s = max(s, H*(1 - TOP)/(bot - top + 1))      # never leave a gap under the photo
        x0 = int((l + r)/2*s - W/2); y0 = int(top*s - TOP*H)
    sm = c.resize((int(W*s), int(H*s)), Image.LANCZOS)
    crop = sm.crop((x0, y0, x0 + W, y0 + int(H*frac)))
    a = np.asarray(crop).astype(float); a2 = a[..., 3:4]/255
    comp = a[..., :3]*a2 + T.grad_bg(W, H, bg)[:crop.size[1]]*(1 - a2)
    Image.fromarray(np.clip(comp, 0, 255).astype('uint8')).save(out, quality=93)
    crop.save(cut)
    return s, x0, y0

BAD = []

def main(spec):
    sp = json.loads(spec) if spec.lstrip().startswith('{') else json.load(open(spec))
    report, last = [], None
    for i, p in enumerate(sp['pics']):
        rgb = tuple(int(v) for v in str(p.get('colour', '255,255,255')).split(','))
        bg = p.get('bg') or pick_bg(rgb, last); last = bg
        pr = Image.open(p['print']); w_cm = float(p.get('print_w_cm') or pr.width/300*2.54)
        bb = pr.getbbox() or (0, 0, pr.width, pr.height)
        key = f'p{i:02d}'; kind = p.get('kind', 'tee'); T.LAST.clear()
        if kind == 'tee':
            x0, y0, pw, ph, W = T.build(key, p['base'], rgb, p['print'], bg, p['out'], chest_cm=float(p.get('chest_cm', 53)),
                                        below_in=float(p.get('below_in', 2.0)), print_w_cm=w_cm, collar_px=p.get('collar_px'), hood_tip=p.get('hood_tip'), hood_poly=p.get('hood_poly'), hood_w=p.get('hood_w'), cords=p.get('cords'), pa_w_frac=p.get('pa_w_frac'), pa_top_frac=p.get('pa_top_frac'))
            art_w = pw*(bb[2] - bb[0])/pr.width
        else:
            back = kind == 'ring_back'
            x0, y0, pw, ph, W = R.build(key, p['base'], p['print'], bg, p['out'], emb_cm=31.0 if back else 12.0,
                                        off_cm=0.0 if back else 11.0, top_cm=8.0, chest_cm=float(p.get('chest_cm', 53)), back=back)
            art_w = pw
        s_, ox, oy = 1.0, 0, 0
        if p.get('frame') == 'none':   # the base photo is already framed as wanted: keep it as it is, backdrop only
            p['finish'] = True
        if p.get('finish', True):
            g = (T.LAST['tip'], T.LAST['hem'], T.LAST['cx']) if (kind == 'tee' and p.get('hood_tip') and p.get('frame') not in ('person', 'none')) else None
            if p.get('frame') == 'none': g = 'none'
            if p.get('match'): g = dict(p['match'], mw=900, mtop=385, mcx=900)   # master: blond tight photo, hood 450-1350 wide, top at 385
            s_, ox, oy = finish(p['out'].replace('.jpg', '_cutout.png'), bg, p['out'], float(p.get('keep', 1.0)), g)
            x0, y0, pw, ph = int(x0*s_ - ox), int(y0*s_ - oy), int(pw*s_), int(ph*s_); art_w = art_w*s_
        ok, why = F.fit_check(p['out'].replace('.jpg', '_cutout.png'), art_w/W)
        place = None
        if kind == 'tee' and p.get('pa_w_frac') and not p.get('hood_tip'):
            # go-live gate (Andy, 6 Nov 2026): the finished picture is re-measured and must match Gelato's placement
            pok, pwhy, nums = F.place_check(p['out'], rgb, (x0, y0, pw, ph), float(p['pa_w_frac']), float(p['pa_top_frac']))
            place = nums; print(p['out'], 'placement', 'OK' if pok else 'FAIL', nums, '; '.join(pwhy))
            if not pok: BAD.append(p['out'] + ': ' + '; '.join(pwhy))
        report.append({'out': p['out'], 'ok': ok, 'reasons': why, 'bg': bg, 'box': [x0, y0, pw, ph], 'print_w_frac': round(art_w/W, 3), 'placement': place})
        print(p['out'], 'OK' if ok else 'CHECK: ' + '; '.join(why), 'backdrop', bg)
        if p.get('close'):
            # Close-up (Andy, 19 Oct 2026, "too zoomed in", twice): the whole print always shows with clear garment around it.
            # The print takes at most 60% of the close-up's width and 65% of its height, whatever its shape (tall character or wide logo).
            im = Image.open(p['out']); s = pw/pr.width if kind == 'tee' else 1
            if kind == 'tee':
                ax0, ay0, ax1, ay1 = x0 + bb[0]*s, y0 + bb[1]*s, x0 + bb[2]*s, y0 + bb[3]*s
            else:
                ax0, ay0, ax1, ay1 = x0, y0, x0 + pw, y0 + ph
            aw, ah = ax1 - ax0, ay1 - ay0
            hgt = int(max(ah/0.65, aw/0.60/0.75)); hgt = min(hgt, im.height, int(im.width/0.75)); wid = int(hgt*0.75)
            cx, cy = (ax0 + ax1)/2, (ay0 + ay1)/2
            l = int(max(0, min(cx - wid/2, im.width - wid))); t = int(max(0, min(cy - hgt/2, im.height - hgt)))
            im.crop((l, t, l + wid, t + hgt)).resize((1500, 2000), Image.LANCZOS).save(p['close'], quality=93)
    json.dump(report, open('report.json', 'w'), indent=1)
    if BAD:
        print('PLACEMENT CHECK FAILED - pictures stopped:\n' + '\n'.join(BAD)); sys.exit(1)

if __name__ == '__main__': main(sys.argv[1])
