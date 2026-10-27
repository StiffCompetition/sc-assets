# Journal cover working files (27 Oct 2026)
Run from a folder holding scripts/, refs/, cover/collage.jpg, fonts/ and models/realesrgan_x4plus.onnx:
`python3 scripts/cover5.py 150 block strap sticker+rays comic` (use 300 for print).
- cover5.py: the full wrap (front, spine, back). Panel order in front_rows / back_rows; FOCUS sets where face crops start.
- prep_panels.py: collage faces (ESRGAN) and body close-ups on dot backgrounds.
- make_hs.py, feature_zoom.py, widen.py, degrey.py: head close-ups, Major Wood eyes / Rear Admiral grin, wide Thunder Guts, grey backgrounds swapped for dots.
- previews/journal-cover-wrap-v19.jpg: latest review version (front direction approved; panels and back in review).
