# Stiff Competition automation — index

Read this before building or changing anything. It lists every live piece of the SC automation, what it does, and where
its code lives. Detailed process rules are in the SC Content Playbook (Google Doc v30) and the SC Master Manual.

## Rule for all sessions (Claude included): tag what you build, and say what it belongs to

- Every n8n workflow carries a **description** stating: the SC area it belongs to (Content pipeline, Publishing, Finance,
  Support bots, Press, Backups, Character facts), what it does in one sentence, what calls it and what it calls, and the
  Playbook section it implements.
- Every workflow **name** starts with `SC - ` for live workflows. Temporary or one-off workflows carry `(temporary)` or
  `(one-off)` in the name and are archived when their job is done, in the same session that created them.
- Every version saved to a workflow has a **version name** saying what changed and why.
- Code that runs outside n8n (Railway services, the dashboard, scripts) lives in this repository with a README beside it,
  and the README names the workflows that call it.
- When a session finds work it did not do (a new node, a new endpoint, a changed setting), it reads the description and
  README first and builds on that work rather than duplicating it.

## Content pipeline (SC Content Playbook v30)

| Workflow (n8n id) | Role |
|---|---|
| SC Content Planner (`S7n6cuyk6EDe5XQH`) | Dashboard planner: creates calendar rows from Andy's selection and runs the concept creator on each (NFT rows go to SC - NFT Post Builder, Dare to Buy rows to SC - Dare to Buy Builder). |
| SC Concept Creator (`3hWUnGrQZmI6cAsm`) | Writes each row's brief from approved spreadsheet rows (no AI except Travel); product briefs use the SC Shop Hotline set, the Product Box tab and the seated gestures. |
| SC - NFT Post Builder (`ykDQm3T2fYGHWF5n`) | NFT post type: POST `{row_id}` to `sc-nft-post` (called by SC Content Planner). Picks a never-used, unsold shop NFT (Travel the World excluded), makes its 8 s ticker (Hotline Compose `/hotline-gfx`), renders the character's NFT template (built once per character by Hotline Compose `/nft-template`) with json2video, stores the clip on Cloudinary and writes clip and captions to the calendar row for review. |
| SC - Video Generation Pipeline (`hjLFFoSSLwkda0XB`) | Start image (Gemini + checks), Kling animation, sound (ElevenLabs), json2video edit with captions, ticker and Hotline graphics; Roll Call and Travel branches. Calls the Hotline service. |
| SC Kling Collector (`fjPLFR3hCpBIyozZ`) | Collects Kling clips that finished after the pipeline stopped waiting. |
| SC - Workflow Code Patch (helper) (`4X0Yozi0Ma7F59DB`) | Maintenance helper: POST `{workflowId, nodeName, replacements:[[old,new]]}` to `sc-wf-patch` makes exact-text edits to one Code node through the n8n API; each old text must occur exactly once or nothing is saved. Called by Claude; calls the n8n API. |
| SC - Product Box (`WnmRdLvPHnzwLyOm`) | Product posts: GET `sc-product-box` lists the Product Box tab (photo, box name, saved framing) for the dashboard's Product boxes tool; POST `sc-product-box-save` `{handle, crop}` writes Andy's framing (a Cloudinary fetch-crop URL) to column G. Called by the dashboard; SC Concept Creator reads column G. |
| SC - Render Movie (json2video) (`vaTb07ARFo7AqL2y`) | Content pipeline helper: POST `sc-render-movie` `{requestBody}` submits a finished json2video edit made outside a post run (used for the Roll Call master clip); GET `sc-render-movie-status?project=` checks it. Called by Claude; calls json2video. |
| SC - Sound Effect Generator (`LxpZamDurtbMvjwx`) | Content pipeline helper: POST `sc-sound-effect` `{prompt, duration}` makes one ElevenLabs sound effect and saves it to Cloudinary (`SCSMAuto/sfx_...`), returning its URL (used for the Roll Call logo sound). Called by Claude; calls ElevenLabs, Cloudinary. |
| SC - Dare to Buy Builder (`Jj2P0WJDMgWBoU17`) | Dare to Buy post type (Playbook 7.7.6): POST `{row_id}` to `sc-dare-to-buy` (called by SC Content Planner and the dashboard's "Make the slides again"). Makes the three 1080 × 1350 carousel slides and the X image with Cloudinary (fixed assets `SCSMAuto/dtb_hook_1..8_v1`, `dtb_xband_1..8_v1`, `dtb_bar_v1`, `dtb_canvas_black_v1`, character cut-outs `dtb_char_<mw/ra/hh/tg/sw/vp>_v1`), stores them as `SCSMAuto/dtb_post_...`, writes the captions and saves everything to the calendar row (slide links in its notes). Test without a row: `{handle, character, dry: true}`. Calls the shop, SC - Product Box, Cloudinary, the calendar API. |
| SC - Publish Dare to Buy (carousel) (`HX2qD2wTHB1gSNPl`) | Publishing for Dare to Buy: POST `{row_id, dry}` to `sc-publish-dtb` (called by SC - Publish Approved Posts). Instagram carousel, Facebook multi-photo post, X image post; live only for rows with status approved, and a dry run stops before each platform's publish call. Writes the result to the row. |
| SC - Calendar API (update) (`4eXYIAKnlJz6aAJ1`) | `sc-calendar-list` / `sc-calendar-update` webhooks used by the dashboard and all content workflows. |
| SC - Content Calendar Dashboard (hosted) (`Fi8KwAgLq266QQ01`) | Serves the dashboard (`dashboard/dashboard.html` in this repo). |
| SC - Publish Scheduler (`cAA12OqK71am3qsV`) | 6am, 7am, Monday 10am, Wed/Fri/Sat 12pm and custom-time slots; hands each approved post to the publish flow. |
| SC - Publish Approved Posts (`ZL9PEe1MnY8nekcE`) | Posts one approved clip to Instagram (Reel), Facebook (Reel) and X; hands approved Dare to Buy rows to SC - Publish Dare to Buy (carousel). Never runs without Andy's approval of that post. |
| SC - Post Now (`TI7Lg8CCMdtN48pG`) | Dashboard "Post Now" for one row. |
| SC Claude Call (`S11nkqzMbLjTFfdY`) | Internal helper so code nodes can call Claude; logs usage. |
| SC - Usage Log Write (`jF0xvGdqHtNFr1ph`) / SC - Daily Cost Digest (`QtFfNhdeAhvalH9x`) | Paid-call log and the 23:30 Telegram cost digest with the price book. |
| SC - Product Box API (`K5iUMBHmZOMxLjT8`) | `sc-productbox` webhook: the dashboard's Product image picker. Lists a product's live `.shop` photos and saves the chosen photo to the Product Box tab. |
| Hotline Compose service (Railway `sc-hotline-compose`) | `services/hotline-compose/` — seating check and placement on Hotline set v2, product cut-outs, ticker and box video, Travel artwork merge. Set v2 is `sc_hotline_set_locked_v2.png` in Cloudinary (v1 kept unchanged). |

Voice-over: Product posts carry a spoken line from the Product Box tab (column F) through the Hotline steps of the pipeline (`Hotline: Has VO?` to `Hotline: Add Narration Audio`); a failed voice step leaves the clip silent.

Data: SC Content Calendar table `Lw2b11QdxL1ZJfz5`; SC Coverage Queue table `SyW9U1Jz3yetKxdp`; SC Usage Log table `El5mTKsfKay47RqA`; content spreadsheet
`1h5EmblzL6kWV4WcG-T8B-b-utsNNYSgb55O0fFTWQ60` (tabs: Ideas by post category, Move Definition, SC Shop Hotline Poses,
Promotable Items, Product Box).

Retired: SC Content Automation - Full (`UGXrwQChDqlgVLFP`, the old trend-to-publish flow; still active for its retry
queue, superseded by the pipeline above), SC - Concept Creator (`9UU1LsBXPW9iXOYL`), SC Brief Creator / v2, SC Panel
Reviewer, SC Brief Validator, and the earlier pipeline copies (`I5kNOphPxKYRC8ia`, `89RaWM8ODoVBRdin`).

## Press (WS-Press)
SC - Coverage Stagger (`kEHUF3zLTmuYqwrD`): staggers Facebook, Discord, Instagram and Reddit legs after each Day-0 X post. The press-page leg is not built yet (Todoist `6hfFqXFXRPJQGWp7`).
SC - Coverage Publish (`8yOMWAmkidnYrAl0`): logs a feature and posts the Day-0 X leg.
SC - Coverage List API (`r8j6H4m0QoFMLbSW`): read-only `sc-coverage-list` webhook; feeds the dashboard's Press coverage view and PRESS calendar cards. The Facebook hold date is also set in the stagger workflow; change both together.

## Finance
SC - Bank Statement Ingest, SC - Receipt Capture (Gmail), SC - PayPal Ingest, SC - Amex Ingest, SC - Expense Entry
(Telegram), SC - Renewals Reminder, SC - Monthly Finance Report, SC - Shopify Daily Snapshot.

## Support bots and knowledge base
SC - Shared Brain, SC - Web/Discord Bridge, SC - KB Public Read, SC - Instagram DM Channel, SC - Instagram Comment
Auto-Reply, SC - Facebook Comment Auto-Reply, SC - Messenger Channel, SC - WhatsApp Channel, SC - Telegram Reply Handler,
SC - Escalation Notifier, SC - Sticker Click Tracker.

## Character facts
SC - Character Fact Review (`RDomdwUKvXvk1rLk`) with the SC - Character Facts table.

## Backups
SC - Daily Workflow Backup, SC - Daily Data Table Backup, SC - Claims Backup to Drive.

## Repository layout
- `dashboard/dashboard.html` — the content calendar dashboard.
- `services/hotline-compose/` — the Hotline Compose service (code + README).
- `rollcall/` — Roll Call assets.
- `ecards/` — birthday e-card artwork per character.
