# SC Hotline Compose service

**What it is:** a small Python (FastAPI) image and video service used by the Stiff Competition content pipeline.
It does the picture work n8n cannot do itself.

**Where it runs:** Railway, project `satisfied-generosity` (the n8n project), service `sc-hotline-compose`
(`https://sc-hotline-compose-production.up.railway.app`). Health check: `GET /health`.

**Source of truth for the code:** this folder (`services/hotline-compose/main.py`).
The service downloads this folder's `main.py` from GitHub (main branch) every time it starts (see `startCommand` in the service settings), so the copy here is the one that runs. To deploy a change: upload the new `main.py` here, then redeploy the service in Railway (any variable change also redeploys it). If GitHub cannot be reached at start-up, it falls back to the older copy in the Railway variable `APP_CODE_B64`.
The service's start command installs its packages; it must include `imageio-ffmpeg` (a bundled ffmpeg used by `/nft-template` to encode).

## Endpoints

| Endpoint | Called by | What it does |
|---|---|---|
| `POST /compose` | n8n "SC - Video Generation Pipeline" → node **Hotline: Compose** | Takes the locked SC Shop Hotline set and Gemini's picture of the presenter seated in it. Checks the set was not moved, that there is one presenter of the right size at the desk with nothing else added, then places the presenter onto the exact set pixels with his head top on a fixed line. Returns `{ok, reason, png_b64}`; a failed check returns `ok:false` and the pipeline retries (up to 8 tries). |
| `POST /cutout` | n8n "SC Concept Creator" (product briefs) | Removes a product photo's background (the area connected to the photo's edges) and uploads a transparent PNG to Cloudinary for the on-screen product box. |
| `POST /hotline-gfx` | n8n "SC - Video Generation Pipeline" → node **Hotline Graphics**; NFT posts | Renders the two-row ticker (readable crawl, drawn stars, white SC mark at capital height) and the product box: one fixed square box (480 × 480 px, the same shape as the shop's product photos, on the right of the desk front with equal gaps under the desk lip, above the ticker and to the right edge, the same on every post; it slides in from the left of the screen) that the product photo fills edge to edge, with no name bar because the ticker carries the name (slide-in, slow push-in, one sheen). `box_url` is the product's photo, or Andy's framing of it from the dashboard's Product boxes tool (a Cloudinary fetch-crop URL) as 25 fps MP4 clips, uploads them to Cloudinary and returns their URLs and placement. json2video overlays them; HTML animation is not used because json2video does not capture it smoothly. Optional fields: `dur` (seconds, default 5; NFT posts send 8), `phrase` (top-row text after the name, default `IN STOCK NOW`; `*` between parts draws a star, NFT posts send `ONE OF ONE*OWN IT NOW`), `box` (default true; NFT posts send false, ticker only). |
| `POST /nft-template` | NFT post type, once per character | Builds the character's reusable 8 s gallery template: the wall (with his busts) slides only while he walks, using his measured timing (`t_full_end`, `t_stop`, `t_go`, `t_cruise`); the frame opening becomes a flat magenta key area with a dark-to-gold inner bevel; he is cut out of his green-screen clip (solid inside his outline, no green left) and placed in front; the loop lands bust on bust so start and end match. Encodes full-colour (4:4:4) H.264 at 25 fps, uploads to Cloudinary and returns `template_url`, `checks` (see-through and green pixel counts), and `nft` (`y`, `size`, and an x keyframe for every frame while the wall moves) for the per-post json2video render, which lays the NFT under the template and keys `#FF00FF` at tolerance 40. Takes about 40 s. |
| `POST /travel-merge` | n8n "SC - Video Generation Pipeline" → node **Travel: Keep Original Art** | Travel the World: Gemini only paints the 9:16 extension; the original NFT artwork is laid back over the middle pixel for pixel (faces exactly as sold), and any duplicated corner logos in the painted areas are removed. |

## Fixed assets (Cloudinary, never regenerated)

- Locked Hotline set (brick wall, 8 Oct 2026): `https://res.cloudinary.com/dkapdtxek/image/upload/v1791472129/SCSMAuto/sc_hotline_set_brick_v1.png` (previous blue set: `https://res.cloudinary.com/dkapdtxek/image/upload/v1790557122/SCSMAuto/sc_hotline_set_locked_v2.png`)
- Ticker mark (white, ™ removed): `https://res.cloudinary.com/dkapdtxek/image/upload/v1790460791/SCSMAuto/sc_ticker_logo_white.png`
- SC style plate (style reference for all other posts): `https://res.cloudinary.com/dkapdtxek/image/upload/v1790385659/SCSMAuto/sc_style_plate_v1.jpg`

Layout constants used by `/compose` and `/hotline-gfx` (1080×1920 frame): head top 470, desk top 1085, desk front 1135,
product box 560×420 at (56, 1229), ticker 1080×178 at y 1742, ON AIR light 336×132 at (372, 102).

Playbook reference: SC Content Playbook v30, sections 7.7.2 (SC Shop Hotline), 7.7.3 (Travel the World), 7.9 and 7.10.

## Hotline set v2 (28 Sep 2026)
The service uses `sc_hotline_set_locked_v2.png` (Cloudinary `SCSMAuto`), which is set v1 with 40px of plain black removed under the ON AIR sign and 40px of desk added at the bottom. All placement numbers in `/compose` are set for v2: desk top 1045, desk front 1095, head top on line 430, head window 300 to 720, protected SC-sign and palm regions shifted up 40px. The "extra object beside presenter" check accepts up to 4,500 dark colourless pixels (a clean image with a black belt measured 3,064; an image with a chair back measured 6,156). The pipeline's node **Hotline: Build Request** must send the same set URL that `/compose` receives; change both together.
