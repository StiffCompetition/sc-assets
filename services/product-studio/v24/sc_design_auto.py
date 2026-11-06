"""SC design, automatic (Products tab: new design from reference images).

Runs the SC t-shirt design tool (Hammerin' Hanky standard) without hand settings:
  phrase  <KEY> "<NAME>" "<LINE 1>" "<LINE 2>"
      free check that the two phrase lines fit at full width (nothing is spent before this passes)
  build   <KEY> "<NAME>" "<LINE 1>" "<LINE 2>" <raw.png> <ref.png> [auto | x1,y1,x2,y2 eyes in raw] [full | gentle]
      face light: full (default) lifts the darker side all the way; gentle (Andy, 22 Oct 2026: the full lift flattened the
      Rear Admiral's face) lifts it only as far as needed to pass the lighting check (half, three quarters, then full)
      1. precheck on the generated picture with each fit (face, then broad, then plain); if
         one-sided face lighting fails, the darker side of the face is lifted (brightness only) and the precheck runs again
      2. enlarge the passed picture with Real-ESRGAN (scaled to about 1500 px wide first, keep 2 or 3 for 300 dpi)
      3. make on the enlarged picture: every check must pass, then both print files, the comparison and likeness
         sheets, and the picture-only file for the library (KEY_art.png) are written
Last line printed: RESULT: PASS, RESULT: REJECT_PICTURE (generate a new picture) or RESULT: FAIL (stop, show Andy).
"""
import sys, os, json, io, contextlib, numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import sc_tshirt_design_tool as T

def result(r, code):
    print('RESULT: ' + r, flush=True); sys.exit(code)

def phrase(lines):
    la = Image.open(T.LOCKUP); lh = int(la.height*int(T.HH['char_w']*T.LAY['lock_frac'])/la.width)
    G = T.text_layout(lines, '', lh); return G['scale'] >= 1

def run_checks(c, outdir):
    os.makedirs(outdir, exist_ok=True)
    out, meta = T.build(c, outdir); return out, meta, T.check(out, meta)

def show(res, title):
    print('--', title)
    for n, ok, v in res: print(('PASS ' if ok else 'FAIL ') + n + ' — ' + v)

def art_from(print_png, out_png):
    a = np.asarray(print_png); rowon = a[..., 3].max(axis=1) > 40
    e = np.diff(np.concatenate([[0], rowon.astype(int), [0]]))
    end = [t for s, t in zip(np.where(e == 1)[0], np.where(e == -1)[0]) if t - s > 8][0]
    im = print_png.crop((0, 0, print_png.width, end)); ys, xs = np.where(np.asarray(im)[..., 3] > 10)
    im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)).save(out_png, dpi=(300, 300))

if __name__ == '__main__':
    mode, key, name, l1, l2 = sys.argv[1:6]
    lines = [l1.strip().upper(), l2.strip().upper()]; name = name.strip().upper()
    if not phrase(lines):
        print('The two phrase lines are too short to fill the width without shrinking. Use longer lines.'); result('FAIL_PHRASE', 3)
    if mode == 'phrase': result('PASS', 0)
    raw, ref = sys.argv[6], sys.argv[7]
    if len(sys.argv) < 9 or sys.argv[8] == 'auto':   # find the eyes on the picture (free, MediaPipe face mesh)
        from sc_find_eyes import find_eyes
        e = find_eyes(raw)
        if not e: print('No face found on the picture.'); result('REJECT_PICTURE', 2)
        eyes = [int(e[0][0]), int(e[0][1]), int(e[1][0]), int(e[1][1])]; print('eyes found at', eyes)
    else:
        eyes = [int(float(v)) for v in sys.argv[8].split(',')]
    eyes = [[eyes[0], eyes[1]], [eyes[2], eyes[3]]]
    R = Image.open(raw).convert('RGB'); rf = Image.open(ref).convert('RGB')
    base = dict(key=key, name=name, lines=lines, skin_ref=ref, skin_ref_box=[0, 0, rf.width, rf.height], k=1)
    g = eyes[1][0] - eyes[0][0]; cx = (eyes[0][0] + eyes[1][0])//2; ey = (eyes[0][1] + eyes[1][1])//2
    # 1. precheck: each fit, with the face lighting fix when lighting is the only failure
    light = sys.argv[9] if len(sys.argv) > 9 else 'full'
    strengths = (0.5, 0.75, 1.0) if light == 'gentle' else (1.0,)
    chosen = None; lifted = False; src = raw
    for fit in ('face', 'broad', 'plain'):
        for adj in (1.0, 0.93):
            c = dict(base, src=src, eyes=eyes, cut=int(R.height*0.9), fit=fit, face_adjust=adj)
            with contextlib.redirect_stdout(io.StringIO()): out, meta, res = run_checks(c, 'pre')
            if not lifted and any(n.startswith('face lighting') and not ok for n, ok, _ in res):
                A = np.asarray(R).astype(float)
                box = (max(cx - int(2.1*g), 0), min(cx + int(2.0*g), R.width), max(ey - int(0.8*g), 0), min(ey + int(3.3*g), R.height))
                L = T.lift(A, cx, box, 1.0)
                for st in strengths:   # the smallest lift that passes the lighting check keeps the most face shape
                    Image.fromarray(np.clip(A + st*(L - A), 0, 255).astype(np.uint8)).save('raw_lit.png'); src = 'raw_lit.png'; lifted = st
                    c['src'] = src
                    with contextlib.redirect_stdout(io.StringIO()): out, meta, res = run_checks(c, 'pre')
                    if not any(n.startswith('face lighting') and not ok for n, ok, _ in res): break
                print(f'face lighting fixed on the picture (darker side lifted {int(lifted*100)}%, brightness only), box', box)
            res = [r for r in res if not r[0].startswith('picture at least 300 dpi')]
            if all(ok for _, ok, _ in res): chosen = (c, meta); break
            show(res, f'precheck fit {fit} face {adj}')
        if chosen: break
    if not chosen:
        print('The picture fails the precheck in every fit. A new picture is needed.'); result('REJECT_PICTURE', 2)
    c, meta = chosen; show(res, f"precheck PASSED with fit {c['fit']} face {c['face_adjust']}")
    # 2. enlarge: box around the figure, scaled to about 1500 px wide, keep 2 or 3 for 300 dpi
    a = np.asarray(Image.open(c['src']).convert('RGB')).astype(float)
    fg = a.min(axis=2) < 235 if np.median(a[:20, :20]) >= 225 else np.abs(a - np.median(a[:20, :20].reshape(-1, 3), axis=0)).max(axis=2) > 30
    ys, xs = np.where(fg); pad = 40
    box = (max(xs.min() - pad, 0), 0, min(xs.max() + pad, a.shape[1]), min(meta['cut'] + pad, a.shape[0]))
    prep = min(1.0, 1500/(box[2] - box[0])); keep = 2 if meta['dpi']*prep*2 >= 300 else 3
    if meta['dpi']*prep*keep < 300: keep = 4
    small = Image.open(c['src']).convert('RGB').crop(box); small = small.resize((int(small.width*prep), int(small.height*prep)), Image.LANCZOS)
    small.save('prep.png'); print(f'enlarging: box {box}, prep {prep:.2f}, keep {keep}', flush=True)
    T.upscale('prep.png', 'up.png', (0, 0, small.width, small.height), keep)
    f = prep*keep; up_eyes = [[(x - box[0])*f, (y - box[1])*f] for x, y in c['eyes']]
    # 3. make on the enlarged picture: every check, then files and sheets
    m = dict(c, src=os.path.abspath('up.png'), eyes=up_eyes, cut=int((c.get('cut', meta['cut']) - box[1])*f), k=keep)
    m['cut'] = int((meta['cut'] - box[1])*f)
    os.makedirs('out', exist_ok=True)
    out, meta2 = T.build(m, 'out'); res2 = T.check(out, meta2); show(res2, 'make (enlarged picture)')
    if not all(ok for _, ok, _ in res2):
        print('The enlarged design fails a check. Stopped; nothing is shown as ready.'); result('FAIL', 1)
    T.sheets(out, meta2, m, 'out'); art_from(out['lightink_for_dark_shirt'], f'out/{key}_art.png')
    from sc_parts import cut   # library parts: name and phrase lines in both inks (picture = KEY_art.png)
    for ink, f in (('lightink', 'lightink_for_dark_shirt'), ('darkink', 'darkink_for_light_shirt')):
        parts = cut(f'out/{key}_{f}.png')
        for part in ('name', 'phrase'): parts[part].save(f'out/{key}_{part}_{ink}.png', dpi=(300, 300))
    json.dump(dict(fit=m['fit'], face_adjust=m['face_adjust'], lifted=lifted, prep=prep, keep=keep, dpi=round(meta2['dpi'])), open('out/settings.json', 'w'))
    result('PASS', 0)
