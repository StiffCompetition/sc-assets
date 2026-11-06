import numpy as np
from PIL import Image
def fit_check(cutout_png, print_w_frac):
    """print_w_frac = printed width / picture width, read from the build output.
    Returns (ok, reasons). ok only if no hand/arm touches the left or right edge, the top is clear, and the print is readable."""
    a=np.asarray(Image.open(cutout_png).convert('RGBA'))[...,3]>128
    H,W=a.shape; why=[]
    if a[:,:6].any() or a[:,-6:].any(): why.append('hand or arm touches the side edge')
    if a[:6,:].any(): why.append('head or hand touches the top edge')
    if print_w_frac<0.25: why.append('print too small to read: %.2f of width'%print_w_frac)
    return (not why), why




def place_check(final_jpg, shirt_rgb, box, pa_w_frac, pa_top_frac, tol=0.02):
    """Go-live gate (Andy, 6 Nov 2026: no picture goes live unless it matches Gelato's mock-up). The finished picture is
    measured again from scratch (shirt found by its colour, shoulder seams, centre line, neckline) and the print area that
    was placed (box = x, y, width, height on the finished picture) must sit where Gelato's proportions put it: centred,
    pa_w_frac x shirt width wide, top edge pa_top_frac x shirt width below the neckline, each within tol of the shirt width.
    Returns (ok, reasons, numbers)."""
    from scipy import ndimage as ndi
    a = np.asarray(Image.open(final_jpg).convert('RGB')).astype(float); H, W = a.shape[:2]
    tgt = np.array(shirt_rgb, float); x0, y0, pw, ph = box
    lum = a.mean(axis=2); tl = tgt.mean()
    norm = a/np.maximum(lum, 1)[..., None]*max(tl, 1)
    close = (np.abs(norm - tgt).max(axis=2) < 60) & (np.abs(lum - tl) < 110)
    if tl < 60: close = (a.max(axis=2) < tl + 45)
    close[y0:y0 + ph, max(0, x0):x0 + pw] = True          # the print sits on the shirt
    lab, n = ndi.label(ndi.binary_opening(close, iterations=2))
    seed = lab[min(H - 1, y0 + ph//2), min(W - 1, max(0, x0 + pw//2))]
    if seed == 0: return False, ['shirt not found under the print'], {}
    m = ndi.binary_fill_holes(ndi.binary_closing(lab == seed, iterations=3))
    rows = np.where(m.any(axis=1))[0]; top, hem = int(rows.min()), int(rows.max())
    reach = np.array([(np.where(m[:, x])[0].max() if m[:, x].any() else 0) for x in range(W)])
    tops = np.array([(np.where(m[:, x])[0].min() if m[:, x].any() else 10**6) for x in range(W)])
    xs = np.where((reach >= hem - 0.12*(hem - top)) & (tops < top + 0.25*(hem - top)))[0]
    if not len(xs): return False, ['shirt body not found'], {}
    runs = np.split(xs, np.where(np.diff(xs) > 1)[0] + 1); big = max(runs, key=len)
    tc, tw = (big[0] + big[-1])/2.0, float(big[-1] - big[0] + 1)
    col = m[:, int(tc) - 12:int(tc) + 13]
    collar = int(np.median([int(np.argmax(col[:, i])) for i in range(col.shape[1]) if col[:, i].any()]))
    d_c = ((x0 + pw/2) - tc)/tw; d_w = pw/tw - pa_w_frac; d_t = (y0 - collar)/tw - pa_top_frac
    nums = {'shirt_w': round(tw, 1), 'centre_off': round(d_c, 4), 'width_off': round(d_w, 4), 'top_off': round(d_t, 4), 'collar': collar}
    why = []
    if abs(d_c) > tol: why.append('print off centre by %.1f%% of the shirt width' % (100*d_c))
    if abs(d_w) > tol: why.append('print area %.3f of the shirt width, Gelato %.3f' % (pw/tw, pa_w_frac))
    if abs(d_t) > tol: why.append('print top %.3f of the shirt width below the neckline, Gelato %.3f' % ((y0 - collar)/tw, pa_top_frac))
    return (not why), why, nums
