"""SC water bottle pictures for the product runner (Andy, 20 Oct 2026): the approved print at true size on Gelato's own blank
white 17oz bottle, three views (turned left, front, turned right), on one SC colour backdrop. Method and measurements: sc_bottle_pic.py.
  python3 sc_bottle_pics.py <spec.json or the JSON itself>
  spec: {"print": "print.png", "bg": "sky", "pics": [{"out": "pic_01_front.jpg", "view": "front"}, ...]}"""
import sys, json
import sc_bottle_pic as B, sc_pic_bg as BGS
VIEWS = {'left': -35, 'front': 0, 'right': 35}
def main(spec):
    sp = json.loads(spec) if spec.lstrip().startswith('{') else json.load(open(spec))
    bgs = BGS.per_picture(sp['print'], len(sp['pics']), sp.get('bg') if sp.get('bg') != 'auto' else None, sp.get('shift', 0))   # own colour per picture (20 Oct 2026)
    for p, bg in zip(sp['pics'], bgs):
        B.main('bottle17/blank.png', 'bottle17/cut.png', sp['print'], p['out'], VIEWS[p['view']], p.get('bg', bg), p.get('size', 2000))
if __name__ == '__main__': main(sys.argv[1])
