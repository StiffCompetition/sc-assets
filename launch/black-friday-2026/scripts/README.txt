Black Friday video build files (9 Nov 2026).
animchar.py / animH2.py / animH3.py: character video builders (animH3 = latest, one pass: clip, sign text, shirt photo, thumps on beat).
endclip.py: the three end clips A, B, C (chrome full logo, BLACK FRIDAY, SHOP AT stiffcompetition.shop).
anim3.py: Major Wood product section (approved v4). mock*.py / bases.py / mock.py: layouts and helpers (need xm_*.jpg, wm_old.png).
sfx_synth.py: makes hh_sfx.wav (thumps on the beat, whoosh).
Final mux (style S in A,B,C): ffmpeg concat body + endS.mp4, music BF_music_3_rock.wav atrim 0.46..11.96 adelay 40 ms, sfx, sfx_endS.wav atrim start 2.0.
Music beat grid: beats at x.46 s of BF_music_3_rock.wav (about 120 bpm); video slams on x.5 s.
