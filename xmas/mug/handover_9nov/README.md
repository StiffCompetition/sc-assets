# Christmas mugs handover, 9 Nov 2026 (00:45 Bogota)
Everything from the mug build chat. Todoist task "Christmas range 2026 and 2027 calendar" has the full log.

THE MUG LOGO: vectored SC logo (Google Drive > Logo > Logo vectored > SC.png). vec_logo_canvas.png here is the 1258x1217 canvas used for every logo side (logo 893x852 centred at 182,182; S-C notch tip at x 632, y 251).

APPROVED by Andy: logo sides MW holly, Hanky mistletoe, Rear Admiral original rope, Slick Willy original; picture sides MW, Hanky, RA, SW (in ../mw ../hh ../ra ../sw) and Velvet Python picture side v5.
VELVET PYTHON logo side: Andy wants the ORIGINAL bow and holly (from mug/b vp5_side2 design) but placed with thought. Current placement rejected (looks thrown on). Plan he accepted: knot on the outer black outline at the lower-left corner of the S foot, bow rotated to follow the foot's top edge, original size or smaller so the chrome face stays visible, tails hang outside over the white, contact shadow, zoom check.
THE GRIP: picture side and logo side built, not yet shown to Andy.
pieces/vp_original_bow_piece_in_vectored_logo_coordinates.png = bow already warped into vectored-canvas coordinates (current placement); pieces/vp_old_to_vectored_affine_W.npy maps old design coords to vectored coords. Re-place by cropping the bow, rotating about the knot, positioning, shadow (Gaussian sd 4, roll 3 px down, strength 0.5); see scripts/tw.py build().
Picture side build: ../mug_build.py. FADE only below the lowest point of hands and forearms (Andy raised the arm blur about ten times). Usage: FADE=0.075 python3 mug_build.py pic_cut.png logo_cut.png "NAME" "LINE1" "LINE2" prefix 0.0 (trim pic_cut to its bounding box first).
