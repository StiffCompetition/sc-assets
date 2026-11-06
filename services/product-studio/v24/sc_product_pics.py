"""SC product pictures: puts a product's approved print files onto the SC model photos (plain garments, no print).
  python3 sc_product_pics.py <spec.json or the JSON itself>
  spec: {"pics": [{"out": "pic_01_main_navy.jpg", "plain": "plain_1.jpg", "print": "print_front_dark.png",
                   "chest_cm": 53, "below_in": 2.0, "close": "pic_02_close_navy.jpg"}, ...]}
Each print file is the template's whole print area at 300 dpi, so its real width is its pixels / 300 inches; it is placed at
that real size on the garment (sc_print_on_model.place: bends with the fabric, takes its light and shade, never redrawn).
"close" also writes a close-up cropped from that picture, from the collar to just below the print."""
import sys, json
from PIL import Image
import sc_print_on_model as M

def main(spec):
    sp = json.loads(spec) if spec.lstrip().startswith('{') else json.load(open(spec))
    for p in sp['pics']:
        pr = Image.open(p['print']); w_cm = pr.width/300*2.54
        bb = pr.getbbox() or (0, 0, pr.width, pr.height)
        info = M.place(p['plain'], p['print'], p['out'], chest_cm=float(p.get('chest_cm', 53)), below_collar_in=float(p.get('below_in', 2.0)), print_w_cm=w_cm)
        print(f"{p['out']}: print {w_cm:.1f} cm wide on a {p.get('chest_cm', 53)} cm chest")
        if p.get('close'):
            im = Image.open(p['out']); x0, y0, pw, ph = info; s = pw/pr.width
            top = max(0, y0 + int(bb[1]*s) - int(0.10*pw)); bot = min(im.height, y0 + int(bb[3]*s) + int(0.06*pw))
            hgt = bot - top; wid = int(hgt*0.75); cx = x0 + pw//2
            im.crop((cx - wid//2, top, cx + wid//2, bot)).resize((1500, 2000), Image.LANCZOS).save(p['close'], quality=93)
            print(f"{p['close']}: close-up")

if __name__ == '__main__': main(sys.argv[1])
