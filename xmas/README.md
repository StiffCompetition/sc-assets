Christmas 2026 character clips (6 Nov 2026). 3 s, 480x832, 9:16, silent, waist-up, Santa's workshop at night.
clips/ = the six final clips (trimmed to 3.0 s from the free Wan takes in gifs/clips/2026-11-06-xmas-*).
Method: nano-banana-2.1/edit start picture from stickers/refs standing front, then free HF Wan 2.2 clip on the GitHub runner (gifs/jobs/2026-11-06-xmas-*.json hold the prompts). Drive: SC Image Library > 97 Christmas Clips.

FINAL homepage cut (6 Nov 2026, approved by Andy): final/Xmas_Homepage_Cut_30s_FINAL.mp4, 30 s, 480x832, yuv420p. Order: sleigh, Major Wood, New York, Rear Admiral, London, Hammerin' Hanky, tree, The Grip, chimney, Velvet Python, snowman, Slick Willy, then the real-lights ending (MERRY CHRISTMAS, chrome logo with glow, stiffcompetition.shop). Music: ElevenLabs brass fanfare (fades 26-29 s) + 6 s sleigh-bell jingle on the ending (SC - Music Generator, n8n webhook sc-music). Scene clips: gifs/clips/2026-11-06-xmas-scene*-*.mp4, ending lights gifs/clips/2026-11-06-xmas-endlights-a.mp4. Not live on the shop yet.

## FINAL (6 Nov 2026)
- Homepage cut = xmas/final/Xmas_Homepage_Cut_31s_FINAL.mp4 (v6, 480x832).
- Social cut = xmas/final/Xmas_Social_31s_1080_s.mp4 (1080x1872, 31.5 s, 15 MB; the 23 MB Xmas_Social_31s_1080.mp4 fails Shopify Files upload).
- In SC Content Library as "Christmas ad 2026 (31 s)" (Shopify Files xmas_ad_social_31s_v2.mp4).

## TEASER RUN (6 Nov 2026, approved by Andy)
- Posts at 14:00 London (SC Content Calendar, approved): Sun 8 Major Wood (teaser1), Mon 9 Rear Admiral (teaser2), Tue 10 Slick Willy (teaser3), Wed 11 the full 31 s ad. Files: xmas/teaser/final/teaser1_major_wood.mp4, teaser2_rear_admiral.mp4, teaser3_slick_willy.mp4 (also Shopify Files xmas_teaser1-3).
- Each teaser = the ad's own scene, EMPTY, cold, still (nano-banana-2.1/edit from reference frames in xmas/teaser, job names need an SC Job Budgets row), COMING SOON from 3 s, black end card with logo fade-in, FOLLOW TO SEE OUR / CHRISTMAS TRAILER, stiffcompetition.shop. Brightness MW 0.10, RA 0.08, SW 0.12 (darker was rejected). One teaser at a time, show Andy before the next.
- Build: xmas/teaser/tools/build_teaser.sh (usage: absolute scene.png out.mp4 [brightness]); music = mk3c.py (sleigh bells + piano, wind tail).
- Homepage: hero snippet theme/xmas/sc-xmas-hero.liquid with assets sc-xmas-hero-t1.mp4 + poster. Live theme writes are refused: duplicate current MAIN, wait processing false, upsert, compare md5, Andy publishes. Teaser 1 live 6 Nov. Each launch day the new video takes the hero and the earlier ones go to the Latest Transmission strip. Dashboard Today line "Homepage video" (Mon-Wed) triggers each step.
- Socials: Instagram stiffcompetition_hq, X stiffcomp6969, YouTube @StiffCompetition, Facebook StiffCompetition1994 (from theme settings).
