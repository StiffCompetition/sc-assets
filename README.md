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
| SC Content Planner (`S7n6cuyk6EDe5XQH`) | Dashboard planner: creates calendar rows from Andy's selection and runs the concept creator on each. |
| SC Concept Creator (`3hWUnGrQZmI6cAsm`) | Writes each row's brief from approved spreadsheet rows (no AI except Travel); product briefs use the SC Shop Hotline set, the Product Box tab and the seated gestures. |
| SC - Video Generation Pipeline (`hjLFFoSSLwkda0XB`) | Start image (Gemini + checks), Kling animation, sound (ElevenLabs), json2video edit with captions, ticker and Hotline graphics; Roll Call and Travel branches. Calls the Hotline service. |
| SC Kling Collector (`fjPLFR3hCpBIyozZ`) | Collects Kling clips that finished after the pipeline stopped waiting. |
| SC - Calendar API (update) (`4eXYIAKnlJz6aAJ1`) | `sc-calendar-list` / `sc-calendar-update` webhooks used by the dashboard and all content workflows. |
| SC - Content Calendar Dashboard (hosted) (`Fi8KwAgLq266QQ01`) | Serves the dashboard (`dashboard/dashboard.html` in this repo). |
| SC - Publish Scheduler (`cAA12OqK71am3qsV`) | 6am, 7am, Monday 10am, Wed/Fri/Sat 12pm and custom-time slots; hands each approved post to the publish flow. |
| SC - Publish Approved Posts (`ZL9PEe1MnY8nekcE`) | Posts one approved clip to Instagram (Reel), Facebook (Reel) and X. Never runs without Andy's approval of that post. |
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
