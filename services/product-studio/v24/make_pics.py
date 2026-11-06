"""Builds every model picture for one character from the shared plain-shirt photos. python3 make_pics.py XX [slot ...]
Extra Gelato colours use the white-shirt photos recoloured by sc_recolour_shirt.py (made once, kept in pom/)."""
import sys, os
from PIL import Image
import sc_print_on_model as M
import sc_recolour_shirt as R
k = sys.argv[1]; d = f'{k}' if os.path.exists(f'{k}/{k}_lightink_for_dark_shirt.png') else f'{k}/precheck'
L, D = f'{d}/{k}_lightink_for_dark_shirt.png', f'{d}/{k}_darkink_for_light_shirt.png'
SLOTS = [  # (product ink, slot, plain photo, print)
 ('light', '1_main_black', 'plain_blond_black_main', L), ('light', '3_second_black', 'plain_female_black_second', L),
 ('light', '4_royal', 'plain_brunette_royal_main', L), ('light', '5_purple', 'plain_female_purple_main', L),
 ('dark', '1_main_white', 'plain_female_white_main', D), ('dark', '3_second_white', 'plain_brunette_white_second', D),
 ('dark', '4_lightblue', 'plain_blond_lightblue_main', D),
 ('light', '6_red', 'plain_brunette_red', L), ('light', '7_militarygreen', 'plain_female_military-green', L),
 ('light', '8_irishgreen', 'plain_brunette_irish-green', L), ('dark', '5_daisy', 'plain_female_daisy', D)]
RECOLOURED = {'plain_brunette_red': ('plain_brunette_white_second', 'red'), 'plain_female_military-green': ('plain_female_white_main', 'military-green'),
              'plain_brunette_irish-green': ('plain_brunette_white_second', 'irish-green'), 'plain_female_daisy': ('plain_female_white_main', 'daisy')}
NO_DAISY = {'HH', 'TG'}   # yellow parts of these characters vanish on Daisy (checked on mock-up, Andy agreed 18 Oct 2026)
only = set(sys.argv[2:])
os.makedirs(f'{k}/pics2', exist_ok=True)
_orig_mask = M.shirt_mask
for ink, slot, plain, pr in SLOTS:
    if only and slot not in only: continue
    if slot == '5_daisy' and k in NO_DAISY: continue
    out = f'{k}/pics2/{k}_{ink}_{slot}.jpg'
    if plain in RECOLOURED:          # place the print by the white photo's own shirt outline, shade by the recoloured photo
        src, col = RECOLOURED[plain]
        if not os.path.exists(f'pom/{plain}.jpg'): R.recolour(f'pom/{src}.jpg', col, f'pom/{plain}.jpg')
        wm = _orig_mask(Image.open(f'pom/{src}.jpg').convert('RGB')); M.shirt_mask = lambda im, wm=wm: wm
    else: M.shirt_mask = _orig_mask
    info = M.place(f'pom/{plain}.jpg', pr, out, chest_cm=47.0 if 'female' in plain else 53.0)   # women's shirts are cut narrower; the print stays its real size
    if slot.startswith('1_main'):   # close-up: crop of the main picture, collar to below the lockup
        im = Image.open(out); x0, y0, pw, ph = info
        top = max(0, y0 - int(0.10*pw)); bot = min(im.height, y0 + int(ph*0.97)); hgt = bot - top; wid = int(hgt*0.75)
        cx = x0 + pw//2; im.crop((cx - wid//2, top, cx + wid//2, bot)).resize((1500, 2000), Image.LANCZOS).save(
            f'{k}/pics2/{k}_{ink}_2_close.jpg', quality=93)
print('done', k)
