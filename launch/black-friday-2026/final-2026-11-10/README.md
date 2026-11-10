# Black Friday 2026 finals (10 Nov 2026)
Offer text in videos: UP TO 30% OFF (live Shopify discount is still the approved automatic 10% until the separate discount task changes it).
- BF_MajorWood_final_v4.mp4, BF_RearAdmiral_final_v4.mp4 (13.5 s, 1080x1920, music from frame 1, sfx on slams, standard end card).
- Slick Willy: not built. Existing clip (character-clips/sw.mp4) is usable only 0.5-1.4 s (arms leave frame, floating fists); needs a new 5 s Leonardo clip (400 credits, Andy's yes). Build with scripts/char2.py (args: name clip product "LINE1|LINE2" tee 610 800), end card via mkend.py.
- scripts/: char2.py (character body), anim3b.py (Major Wood body), sfx_char.py, end_std.py + mkend.py (standard ending, tagline arg), lay11.py (standard end layout generator), wm_new.png (SC mark layer, x700-930 y1018-1248).
- Audio: BF_music_3_rock.wav (Drive 85 Leonardo AI Images) atrim 0.46..13.96 adelay 40 ms + char_sfx.wav (sfx_char.py) + scripts/sfx_endA.wav atrim 10.99..13.49 adelay 11040 ms.

## Update 10 Nov 2026 (final)
Final files: BF_MajorWood_final_v7.mp4, BF_RearAdmiral_final_v7.mp4 (music fades out over the last 1.8 s).
SC mark: original bottom-right, x 820-1050, y 1660-1890 (wm_new.png = wm_layer.png).
One layout for every character (char2.py NAME CLIP MUGPHOTO "LINE" mug 560 1240): UP TO 30% OFF y 280, PRICES DROP. y 400, gold line y 548; figure only, 820 px wide, top y 600; character's standard mug photo 1240 px wide, top y 560, centred x 540; then the standard end card.
Check every full-size frame before showing: product 80 px clear of text, centred, filling the width, same layout in every video, audio 0 s to end.
