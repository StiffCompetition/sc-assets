"""SC mug pictures for the product runner (Andy, 20 Oct 2026): the approved wrap print at true size on Gelato's own blank
15oz white mug, three views (handle left, front, handle right), on one SC colour backdrop. Method and measurements: sc_mug_pic.py.
  python3 sc_mug_pics.py <spec.json or the JSON itself>
  spec: {"wrap": "print.png", "bg": "sky", "pics": [{"out": "pic_01_left.jpg", "view": "left"}, ...]}"""
import sys, json
import sc_mug_pic as M, sc_pic_bg as BGS
VIEWS = {'left': ('mug15/blank_6.png', 'mug15/cut_6.png', 'left'), 'front': ('mug15/blank_8.png', 'mug15/cut_8.png', 'back'),
         'right': ('mug15/blank_9.png', 'mug15/cut_9.png', 'right')}
def main(spec):
    sp = json.loads(spec) if spec.lstrip().startswith('{') else json.load(open(spec))
    bgs = BGS.per_picture(sp['wrap'], len(sp['pics']), sp.get('bg') if sp.get('bg') != 'auto' else None, sp.get('shift', 0))   # own colour per picture (20 Oct 2026)
    for p, bg in zip(sp['pics'], bgs):
        b, c, h = VIEWS[p['view']]
        M.main(b, c, sp['wrap'], p['out'], h, p.get('bg', bg), p.get('size', 2000))
if __name__ == '__main__': main(sys.argv[1])
