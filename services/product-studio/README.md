# SC Product Studio (Railway service sc-product-studio)

The service downloads its code bundle from the CODE_URL variable at start (a .tgz in the shop's Files).

## v24 (6 Nov 2026): Gelato placement on model pictures
Andy, 6 Nov 2026: "There are no guesses in our processes."

**Placement (`sc_mp_tee.py`, `torso_measure`)**
- When a picture spec carries `pa_w_frac` and `pa_top_frac`, the print area is placed from measurements, not from a fixed chest size.
- **Measured on each photo:**
  - the shirt's shoulder seams, where each sleeve joins the body; they give the shirt's width and centre line;
  - the front neckline, found on that centre line.
- **Measured on Gelato's own mock-up** (Classic Unisex Crewneck Gildan 64000, template 53ac8006, the editor/front scene of the live products):
  - the print area is 0.531 of the shirt's body width;
  - its top edge sits 0.138 of the body width below the front neckline, which is 7.9 cm, 3.1 in;
  - it is centred on the shirt.
- **Where the values are stored:** in the SC Model Photos table, `spec` column of each t-shirt base photo. They reach the studio through the Product Runner, so no runner change was needed.

**Go-live gate (`sc_mp_fit.py`, `place_check`)**
- Every finished picture is measured again from scratch: shirt by colour, shoulder seams, centre line and neckline.
- The placed print area must match Gelato's proportions within 2% of the shirt width for:
  - centre;
  - width;
  - top edge.
- Any failure makes the studio job fail. The run then stops as failed and never goes live.

Rollback: set CODE_URL back to sc_studio_code_v23.tgz and restart the service.
