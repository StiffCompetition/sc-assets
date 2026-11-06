# SC GIF builder (one GIF, two overlays)

`python3 sc_gif.py SRC.mp4 NAME "CAPTION" HIT_SECONDS [TOP_PX]` makes `NAME_giphy.gif` and `NAME_page.gif`.

Rules (Andy, 6 Nov 2026):
- SOURCE must be the clean video with NO watermark or badge. Never build from an already-overlaid GIF or MP4.
- The overlay is the ONLY branding on the GIF: no website text, no old SC badge, no address.
- Caption text only in the top area. The bottom strip, corners and centre stay clear of everything except the overlay.
- `_giphy.gif` goes to GIPHY. GIPHY stamps its own GIPHY word, the time and the ticks, so we draw none of those. The SC box sits directly above where the GIPHY word appears.
- `_page.gif` goes to the shop page, downloads, Drive, WhatsApp/Telegram and anywhere that is not GIPHY. Same overlay, but the SC box sits in the spot where the GIPHY word appears.
- Overlay: SC box exactly as wide as the word GIPHY (69px at 480px), same left edge, smooth rounded corners (radius 9, supersampled), single solid black line SC. Box, @STIFFCOMP and GIPHY share one off-white (255,250,235) at 65% opacity, measured from WhatsApp.
- @STIFFCOMP: Montserrat ExtraBold 21px (closest to GIPHY's lettering), centred between the GIPHY word and the time, baseline level with GIPHY, clear of the time and ticks.
- 480px wide, 12 fps, 256-colour palette, no dither.
