#!/usr/bin/env python3
"""Rebuild all 24 GIFs with the two overlays. Usage: python3 rebuild_all.py SRC_DIR OUT_DIR
SRC_DIR holds the clean sources: gifs/src/*.mp4 (12 character clips) and gifs/giphy-v2/*.gif (12 Stiff Moves, footer band cropped off)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sc_gif
# name: (source, caption, hit seconds, top px, end seconds or None)
CH = {
 'admiral_hugs': ('r3_RA.mp4', 'HUGS!', 2.33, 0, None), 'admiral_waitwhat': ('RA.mp4', 'WAIT, WHAT?!', 1.0, 100, None),
 'grip_highfive': ('r3_TG.mp4', 'HIGH FIVE!', 1.67, 0, 31 / 12), 'grip_letsgo': ('TG.mp4', "LET'S GO!", 1.0, 0, None),
 'hanky_no': ('r3_HH.mp4', 'NO.', 0.75, 130, None), 'hanky_seriously': ('HH.mp4', 'SERIOUSLY?', 0.0, 125, 29 / 12),
 'python_letsparty': ('r3_VP.mp4', "LET'S PARTY", 1.0, 40, None), 'python_whatever': ('VP.mp4', 'WHATEVER', 1.0, 110, 34 / 12),
 'willy_isawthat': ('w1.mp4', 'I SAW THAT', 2.17, 120, None), 'willy_ugh': ('r3_willy2.mp4', 'UGH!', 0.92, 135, None),
 'wood_micdrop': ('MW.mp4', 'MIC DROP', 1.92, 90, None), 'wood_thankyou': ('r3_MW.mp4', 'THANK YOU', 1.5, 110, None),
}
src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
for n, (f, text, hit, top, end) in CH.items():
    print(n, sc_gif.make(f'{src}/src/{f}', f'{out}/{n}', text, hit, top, end=end), flush=True)
for f in sorted(os.listdir(f'{src}/giphy-v2')):
    n = f[:-4]   # Stiff Moves: crop 440x440 from (20,0) to drop the old footer band, no caption, no hold
    print(n, sc_gif.make(f'{src}/giphy-v2/{f}', f'{out}/{n}', None, 0, box=(20, 0, 440, 440), hold=0), flush=True)
