# SC Hotline Compose service

**What it is:** a small Python (FastAPI) image and video service used by the Stiff Competition content pipeline.
It does the picture work n8n cannot do itself.

**Where it runs:** Railway, project `satisfied-generosity` (the n8n project), service `sc-hotline-compose`
(`https://sc-hotline-compose-production.up.railway.app`). Health check: `GET /health`.

**Source of truth for the code:** this folder (`services/hotline-compose/main.py`).
The running copy is the Railway variable `APP_CODE_B64` (base64 of `main.py`); the service installs its packages and
starts from that variable (see `startCommand` in the service settings). To deploy a change: edit `main.py` here,
then set `APP_CODE_B64` to `base64 -w0 main.py`. Railway redeploys automatically.

## Endpoints

| Endpoint | Called by | What it does |
|---|---|---|
| `POST /compose` | n8n "SC - Video Generation Pipeline" → node **Hotline: Compose** | Takes the locked SC Shop Hotline set and Gemini's picture of the presenter seated in it. Checks the set was not moved, that there is one presenter of the right size at the desk with nothing else added, then places the presenter onto the exact set pixels with his head top on a fixed line. Returns `{ok, reason, png_b64}`; a failed check returns `ok:false` and the pipeline retries (up to 8 tries). |
| `POST /cutout` | n8n "SC Concept Creator" (product briefs) | Removes a product photo's background (the area connected to the photo's edges) and uploads a transparent PNG to Cloudinary for the on-screen product box. |
| `POST /hotline-gfx` | n8n "SC - Video Generation Pipeline" → node **Hotline Graphics** | Renders the two-row ticker (readable crawl, drawn stars, white SC mark at capital height) and the product box (slide-in, slow push-in, one sheen) as 25 fps MP4 clips, uploads them to Cloudinary and returns their URLs and placement. json2video overlays them; HTML animation is not used because json2video does not capture it smoothly. |
| `POST /travel-merge` | n8n "SC - Video Generation Pipeline" → node **Travel: Keep Original Art** | Travel the World: Gemini only paints the 9:16 extension; the original NFT artwork is laid back over the middle pixel for pixel (faces exactly as sold), and any duplicated corner logos in the painted areas are removed. |

## Fixed assets (Cloudinary, never regenerated)

- Locked Hotline set: `https://res.cloudinary.com/dkapdtxek/image/upload/v1790454966/SCSMAuto/sc_hotline_set_locked_v1.png`
- Ticker mark (white, ™ removed): `https://res.cloudinary.com/dkapdtxek/image/upload/v1790460791/SCSMAuto/sc_ticker_logo_white.png`
- SC style plate (style reference for all other posts): `https://res.cloudinary.com/dkapdtxek/image/upload/v1790385659/SCSMAuto/sc_style_plate_v1.jpg`

Layout constants used by `/compose` and `/hotline-gfx` (1080×1920 frame): head top 470, desk top 1085, desk front 1135,
product box 560×420 at (56, 1229), ticker 1080×178 at y 1742, ON AIR light 336×132 at (372, 102).

Playbook reference: SC Content Playbook v30, sections 7.7.2 (SC Shop Hotline), 7.7.3 (Travel the World), 7.9 and 7.10.
