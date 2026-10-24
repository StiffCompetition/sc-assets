// CERTIFICATE OF DEPLOYMENT - design approved by Andy 24 Oct 2026: character colour header with
// portrait(s), custody section with the round stamp beside the name, one-row manifest
// (product then design), Stiff Competition logo at the foot.
//
// TEST SWITCH. TEST_ORDER = an order number to send as a TEST. The TEST goes ONLY to TEST_TO
// (never the customer), the subject starts "TEST - ", and it is not linked to the customer's
// account. It sends once per TEST_SINCE value: change TEST_SINCE to send another.
// Set TEST_ORDER to '' when testing is finished.
const TEST_ORDER = '1062';
const TEST_TO = 'andy@stiffcompetitionart.com';
const TEST_SINCE = '2026-10-24T23:25:00Z';
// HOLD_CUSTOMERS = true holds every customer certificate (not sent, not logged).
// Released by Andy 24 Oct 2026: certificates go to customers 24 hours after a paid order.
const HOLD_CUSTOMERS = false;
// RESEND: order number -> time. Sends that order's certificate again to the CUSTOMER, once,
// even if it was sent before or customers are held. Joey (1062) had the broken certificate; Andy approved the resend 24 Oct 2026.
const RESEND = { '1062': '2026-10-24T22:30:00Z' };
const LOGO = 'https://cdn.jsdelivr.net/gh/StiffCompetition/sc-assets/ecards/brand/logo.png';
const CDN = 'https://cdn.shopify.com/s/files/1/0661/7428/7966/files/';
const WORDMARK = CDN + 'sc-cert-wordmark-trim.png';
const MONOGRAM = CDN + 'sc-cert-monogram.png';
const MONOGRAM_TRIM = CDN + 'sc-cert-monogram-trim.png';
const STAMP_IMG = { DEPLOYED: CDN + 'sc-cert-stamp-deployed.png', ISSUED: CDN + 'sc-cert-stamp-issued.png' };
const UNSUB = 'https://n8n-production-afc2.up.railway.app/form/sc-unsubscribe';
const CERT_PAGE = 'https://www.stiffcompetition.shop/pages/certificate';
const STORE = 'https://www.stiffcompetition.shop';
const RED = '#ed1c24';
const STAMP = '#c8102e';
const INK = '#15181c';
const INK2 = '#4a4a46';
const PAPER = '#f4f0e6';
const RULE = '#b9ad8f';
const MONO = "'IBM Plex Mono','Courier New',Courier,monospace";
const DISPLAY = "'Oswald','Arial Narrow','Helvetica Neue',Arial,sans-serif";
const TEXT = "'Helvetica Neue',Helvetica,Arial,sans-serif";
const CHAR_STYLE = {
  'Major Wood': { key: 'MW', color: '#2e3820', handle: 'major-wood' },
  'The Rear Admiral': { key: 'RA', color: '#1d3557', handle: 'the-rear-admiral' },
  "Hammerin' Hanky": { key: 'HH', color: '#6b3f06', handle: 'hammerin-hanky' },
  'Slick Willy': { key: 'SW', color: '#2b2d33', handle: 'slick-willy' },
  'The Velvet Python': { key: 'VP', color: '#1f4a3a', handle: 'the-velvet-python' },
  'The Grip': { key: 'TG', color: '#24478f', handle: 'the-grip' }
};
const DELAY_HOURS = 24;
const INTERNAL = ['andy@stiffcompetitionart.com','rigid@stiffcompetition.shop','hq@stiffcompetition.shop','rigid@stiffcompetitionart.com'];
const CHARACTERS = ['Major Wood','The Rear Admiral',"Hammerin' Hanky",'The Grip','The Velvet Python','Slick Willy'];
const RECORDS_LINE = 'FOR YOUR RECORDS &mdash; Print and save this certificate.<br>HQ recommends a prominent position on the wall.';
const SOCIALS = [
  ['https://www.instagram.com/stiffcompetition_hq/', 'https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/instagram.svg', 'Instagram'],
  ['https://x.com/stiffcomp6969', 'https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/x.svg', 'X'],
  ['https://www.facebook.com/StiffCompetition1994', 'https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/facebook.svg', 'Facebook'],
  ['https://www.youtube.com/@StiffCompetition', 'https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/youtube.svg', 'YouTube'],
  ['https://discord.gg/QCgCu73ucs', 'https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/discord.svg', 'Discord'],
  ['https://opensea.io/StiffCompetition_hq', 'https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/opensea.svg', 'OpenSea'],
  [STORE, LOGO, 'Shop']
];
function esc(s){return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
function token(){ let t=''; for(let i=0;i<40;i++) t+='0123456789abcdef'[Math.floor(Math.random()*16)]; return t; }
function titleCase(s){
  s = String(s || '').trim();
  if (!s) return '';
  const SMALL = ['a','an','and','at','by','for','in','of','on','or','the','to','with'];
  return s.split(/\s+/).map((w, i) => {
    if (/\d/.test(w) && /^[A-Z0-9#.-]+$/.test(w)) return w;
    w = w.toLowerCase();
    if (i > 0 && SMALL.indexOf(w) !== -1) return w;
    return w.replace(/^(['"(]*)(\w)/, (m, p, c) => p + c.toUpperCase());
  }).join(' ');
}
function londonSendDate() {
  const d = new Date(new Date().toLocaleString('en-US', { timeZone: 'Europe/London' }));
  const day = d.getDate();
  const months = ['January','February','March','April','May','June','July','August','September','October','November','December'];
  const s = (day % 10 === 1 && day !== 11) ? 'st' : (day % 10 === 2 && day !== 12) ? 'nd' : (day % 10 === 3 && day !== 13) ? 'rd' : 'th';
  return day + s + ' day of ' + months[d.getMonth()] + ' ' + d.getFullYear();
}
const SEND_DATE = londonSendDate();
const SEND_DATE_PLAIN = SEND_DATE.replace(/^(\d+)\w\w day of /, '$1 ');
function londonShortDate() {
  const d = new Date(new Date().toLocaleString('en-US', { timeZone: 'Europe/London' }));
  const p = (n) => (n < 10 ? '0' : '') + n;
  return p(d.getDate()) + '·' + p(d.getMonth() + 1) + '·' + d.getFullYear();
}
const SEND_DATE_SHORT = londonShortDate();
const catchphrases = {};
for (const it of $('Get Catchphrases').all()) {
  const topic = String(it.json.topic || '');
  const content = String(it.json.content || '');
  const m = topic.match(/^(.+?) - character$/);
  if (!m) continue;
  const cp = content.match(/Catchphrase:\s*'(.*?)'(?![a-zA-Z])/i);
  if (cp) catchphrases[m[1].trim()] = cp[1].trim();
}
const productChar = {};
const productInfo = {};
for (const it of $('Get Order Products').all()) {
  const list = (it.json && it.json.products) ? it.json.products : [];
  for (const p of list) {
    productInfo[String(p.id)] = { title: String(p.title || '').trim(), type: String(p.product_type || '').trim() };
    const tags = String(p.tags || '');
    for (const c of CHARACTERS) {
      if (tags.indexOf(c) !== -1) { productChar[String(p.id)] = c; break; }
    }
  }
}
const alreadySent = new Set();
const resendDone = new Set();
let testDone = false;
for (const it of $('Get Send Log').all()) {
  const j = it.json || {};
  if (!j.order_id) continue;
  if (String(j.email || '').toLowerCase() === TEST_TO.toLowerCase()) {
    if (TEST_ORDER && String(j.order_number || '') === TEST_ORDER && new Date(j.sent_at || 0).getTime() >= new Date(TEST_SINCE).getTime()) testDone = true;
    continue;
  }
  const rs = RESEND[String(j.order_number || '')];
  if (rs && new Date(j.sent_at || 0).getTime() >= new Date(rs).getTime()) resendDone.add(String(j.order_number));
  alreadySent.add(String(j.order_id));
}
const suppressed = new Set(INTERNAL.map(e => e.toLowerCase()));
for (const it of $('Get Suppression List').all()) {
  if (it.json && it.json.email) suppressed.add(String(it.json.email).toLowerCase());
}
const merchResp = $('Get Merch Pool').first().json || {};
let merchRaw = [];
if (merchResp.data && merchResp.data.products && merchResp.data.products.edges) {
  merchRaw = merchResp.data.products.edges.map(e => {
    const nd = e.node || {};
    const v = (nd.variants && nd.variants.edges && nd.variants.edges[0]) ? nd.variants.edges[0].node : null;
    return {
      title: nd.title,
      handle: nd.handle,
      product_type: nd.productType,
      tags: Array.isArray(nd.tags) ? nd.tags.join(',') : String(nd.tags || ''),
      image: nd.featuredImage ? { src: nd.featuredImage.url } : null,
      variants: v ? [{ price: v.price }] : []
    };
  });
} else if (merchResp.products) {
  merchRaw = merchResp.products;
}
const merch = merchRaw.filter(p => {
  const type = String(p.product_type || '').toLowerCase();
  const tags = String(p.tags || '').toLowerCase();
  if (type === 'nft') return false;
  if (tags.indexOf('internal-test') !== -1) return false;
  return !!(p.image && p.image.src);
});
if (merch.length === 0) { console.log('WARNING: merch pool empty - cross-sell row will not render.'); }
function manifestRow(li) {
  const pid = String(li.product_id);
  const info = productInfo[pid] || { title: String(li.title || ''), type: '' };
  const title = info.title || String(li.title || '');
  const chr = productChar[pid] || '';
  let name = '', sub = '';
  let m = title.match(/^[^:]*:\s*([^()]+?)\s*(?:\((.+?)\))?\s*$/);
  if (m) { name = titleCase(m[1]); sub = titleCase(m[2] || ''); }
  else if ((m = title.match(/['‘’"“”]([^'‘’"“”]+)['‘’"“”]/))) { name = chr || 'Stiff Competition'; sub = titleCase(m[1]); }
  else if (chr) { name = chr; sub = title; }
  else { name = titleCase(title); sub = ''; }
  if (chr && name.toLowerCase().indexOf(chr.toLowerCase()) === -1 && !sub) { sub = name; name = chr; }
  let unit = info.type || 'Item';
  if (/^nft$/i.test(unit)) unit = 'NFT';
  let spec = String(li.variant_title || '').trim();
  if (/^default title$/i.test(spec)) spec = '';
  const color = (chr && CHAR_STYLE[chr]) ? CHAR_STYLE[chr].color : INK;
  return { unit, name, sub, spec, qty: Number(li.quantity) || 1, character: chr, color };
}
function manifestHtml(rows, orderNumber) {
  const n2 = (k) => (k < 10 ? '0' : '') + k;
  {
    // Dark header with the order number in a tag, then one row per item: number, product, design.
    let h = '<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:separate;border:1.5px solid ' + INK + ';background:#fbf8f1;overflow:hidden;">' +
      '<tr><td style="background:' + INK + ';padding:5px 8px;">' +
      '<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;table-layout:fixed;"><tr>' +
      '<td align="left" valign="middle" style="vertical-align:middle;font-family:' + DISPLAY + ';font-weight:700;font-size:10px;line-height:18px;letter-spacing:0.8px;text-transform:uppercase;color:#ffffff;">Deployment Manifest</td>' +
      '<td width="70" align="right" valign="middle" style="vertical-align:middle;white-space:nowrap;"><table cellpadding="0" cellspacing="0" align="right" style="border-collapse:separate;"><tr><td style="border:1px solid ' + PAPER + ';padding:0 6px;height:14px;line-height:14px;font-family:' + DISPLAY + ';font-weight:700;font-size:8px;letter-spacing:0.8px;color:' + PAPER + ';white-space:nowrap;">NO. ' + esc(orderNumber) + '</td></tr></table></td>' +
      '</tr></table></td></tr>' +
      '';
    rows.forEach((r, i) => {
      h += '<tr><td style="padding:0 10px;">' +
        '<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;table-layout:fixed;' + (i ? 'border-top:1px dotted ' + RULE + ';' : '') + '"><tr>' +
        '<td width="30" valign="middle" style="padding:8px 0;vertical-align:middle;font-family:' + DISPLAY + ';font-weight:700;font-size:14px;line-height:1;color:' + r.color + ';">' + n2(i + 1) + '</td>' +
        '<td width="36%" valign="middle" style="padding:8px 6px 8px 0;vertical-align:middle;font-family:' + DISPLAY + ';font-weight:700;font-size:11px;line-height:1.2;letter-spacing:0.5px;text-transform:uppercase;color:' + INK + ';word-break:keep-all;">' + esc(r.unit).replace(/-/g, '&#8209;') + (r.qty > 1 ? ' &times; ' + r.qty : '') + '</td>' +
        '<td align="right" valign="middle" style="padding:8px 0;vertical-align:middle;font-family:' + DISPLAY + ';font-weight:700;font-size:10px;line-height:1.2;letter-spacing:0.5px;text-transform:uppercase;color:' + r.color + ';word-break:keep-all;">' + esc(r.name) + '</td>' +
        '</tr></table></td></tr>';
    });
    h += '</table>';
    return h;
  }
}
const ordersResp = $('Get Recent Paid Orders').first().json || {};
const orders = ordersResp.orders || [];
const now = Date.now();
const out = [];
const skipped = [];
for (const o of orders) {
  const orderId = String(o.id);
  const orderNumber = String(o.name || o.order_number || '').replace(/^#/, '');
  const email = String(o.email || '').trim().toLowerCase();
  const customerId = String((o.customer && o.customer.id) || '');
  const isTest = !!(TEST_ORDER && orderNumber === TEST_ORDER);
  const isResend = !isTest && !!RESEND[orderNumber] && !resendDone.has(orderNumber);
  if (isTest && testDone) { skipped.push(orderNumber + ':test-already-sent'); continue; }
  if (!email) { skipped.push(orderNumber + ':no-email'); continue; }
  if (String(o.financial_status) !== 'paid') { skipped.push(orderNumber + ':not-paid'); continue; }
  if (!isTest && !isResend && alreadySent.has(orderId)) { skipped.push(orderNumber + ':already-sent'); continue; }
  if (suppressed.has(email)) { skipped.push(orderNumber + ':suppressed'); continue; }
  const createdMs = new Date(o.created_at).getTime();
  if (!isTest && (!isFinite(createdMs) || (now - createdMs) / 3600000 < DELAY_HOURS)) { skipped.push(orderNumber + ':too-recent'); continue; }
  if (!isTest && !isResend && HOLD_CUSTOMERS) { skipped.push(orderNumber + ':held'); continue; }
  const found = [];
  for (const li of (o.line_items || [])) {
    const c = productChar[String(li.product_id)];
    if (c && found.indexOf(c) === -1) found.push(c);
  }
  if (found.length === 0) {
    const titles = (o.line_items || []).map(li => String(li.title || ''));
    for (const c of CHARACTERS) {
      if (titles.some(t => t.indexOf(c) !== -1) && found.indexOf(c) === -1) found.push(c);
    }
  }
  const rows = (o.line_items || []).map(manifestRow);
  const otherItems = found.length ? rows.filter(r => !r.character || found.indexOf(r.character) === -1).length : Math.max(0, rows.length - 1);
  const firstName = String((o.customer && o.customer.first_name) || '').trim() || 'Collector';
  const displayName = firstName.toUpperCase();
  // Name size from its length, so it always fits on ONE line: sized for the narrowest view
  // (a forwarded email on a small phone) with the text enlarged by the mail app.
  const nameSize = Math.max(12, Math.min(32, Math.floor(130 / (displayName.length * 1.0 + 0.3))));
  const chars = found.map(c => ({ name: c, phrase: catchphrases[c] || '', style: CHAR_STYLE[c] || null }));
  const c1 = (chars.length && chars[0].style) ? chars[0].style.color : INK;
  const mode = chars.length ? 'DEPLOYED' : 'ISSUED';
  let subjectName, stampText, issue = null;
  if (chars.length) {
    subjectName = found.join(' &amp; ');
    stampText = found.join(', ');
  } else {
    const b = rows[0];
    if (b) {
      const main = b.sub ? b.name + ' ' + b.sub : b.name;
      issue = { name: main + (b.unit && main.toLowerCase().indexOf(b.unit.toLowerCase()) === -1 ? ' ' + b.unit : ''), unit: b.unit, line: '' };
    } else {
      issue = { name: 'General Issue', unit: '', line: '' };
    }
    subjectName = issue.name.replace(/&/g, '&amp;');
    stampText = issue.name;
  }
  const subjectMore = otherItems > 0 ? ' + ' + otherItems + ' more' : '';
  const certData = {
    v: 1,
    order_number: orderNumber,
    name: displayName,
    date_long: SEND_DATE,
    date_short: SEND_DATE_SHORT,
    mode,
    characters: chars.map(c => ({ name: c.name, phrase: c.phrase })),
    issue,
    manifest: rows.map(r => ({ unit: r.unit, qty: r.qty, name: r.name, sub: r.sub, spec: r.spec }))
  };
  const picks = [];
  const usedTypes = new Set();
  const charMatches = merch.filter(p => found.some(c => String(p.title).indexOf(c) !== -1));
  const pool = charMatches.concat(merch.filter(p => charMatches.indexOf(p) === -1));
  for (const p of pool) {
    const t = String(p.product_type || 'other').toLowerCase();
    if (usedTypes.has(t)) continue;
    usedTypes.add(t);
    picks.push(p);
    if (picks.length === 3) break;
  }
  const crossSellCells = picks.map(p => {
    const price = (p.variants && p.variants[0] && p.variants[0].price) ? Number(p.variants[0].price).toFixed(2) : '';
    return '<td width="33%" valign="top" align="center" style="padding:0 4px;">' +
      '<a href="' + STORE + '/products/' + p.handle + '" style="text-decoration:none;color:#111;">' +
      '<img src="' + p.image.src + '" width="110" style="width:100%;max-width:110px;display:block;margin:0 auto 4px;background:#fff;" alt="">' +
      '<span style="display:block;font-size:11px;line-height:1.25;color:#111;">' + esc(p.product_type || p.title) + '</span>' +
      (price ? '<span style="display:block;font-size:11px;line-height:1.25;color:#666;">£' + price + '</span>' : '') +
      '</a></td>';
  }).join('');
  const socialCells = SOCIALS.map(s =>
    '<a href="' + s[0] + '" style="margin:0 5px;"><img src="' + s[1] + '" width="19" height="19" alt="' + s[2] + '" style="vertical-align:middle;"></a>'
  ).join('');
  const statusUrl = o.order_status_url || (STORE + '/account');
  const certToken = token();
  const certUrl = CERT_PAGE + '?o=' + encodeURIComponent(orderId) + '&k=' + certToken;
  const crossSellBlock = crossSellCells
    ? '<hr style="border:none;border-top:1px solid #eee;margin:0 0 14px;">' +
      '<div style="text-align:center;font-size:13px;line-height:1.3;color:#111;font-weight:700;padding-bottom:10px;white-space:nowrap;">The rest of the squad</div>' +
      '<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;"><tr>' + crossSellCells + '</tr></table>' +
      '<div style="height:18px;"></div>'
    : '';
  const small = (px, extra) => 'font-family:' + TEXT + ';font-size:' + px + 'px;letter-spacing:1px;text-transform:uppercase;line-height:1.5;' + (extra || '');
  const display = (px, extra) => 'font-family:' + DISPLAY + ';font-weight:700;font-size:' + px + 'px;line-height:1.05;letter-spacing:1px;text-transform:uppercase;' + (extra || '');
  // PORTRAITS: one character = large portrait with name and catchphrase; several = smaller portraits, three to a row, name under each.
  const one = chars.length === 1;
  const msize = chars.length <= 1 ? 92 : chars.length === 2 ? 60 : 56;
  const ring = msize > 70 ? 4 : 3;
  const portrait = (src, alt) => '<table cellpadding="0" cellspacing="0" align="center" style="border-collapse:separate;margin:0 auto;"><tr><td style="width:' + msize + 'px;height:' + msize + 'px;border-radius:50%;background:#ffffff;border:' + ring + 'px solid ' + PAPER + ';overflow:hidden;">' +
    '<img src="' + src + '" alt="' + esc(alt) + '" width="' + msize + '" height="' + msize + '" style="width:' + msize + 'px;height:' + msize + 'px;display:block;border-radius:50%;"></td></tr></table>';
  let heroBlock;
  if (chars.length) {
    const cells = chars.map(c => '<td valign="top" align="center" width="' + (one ? '100%' : '33%') + '" style="padding:0 3px;">' +
      portrait(c.style ? CDN + 'sc-cert-portrait-' + c.style.key + '.png' : MONOGRAM, c.name) +
      '<div style="' + display(one ? 20 : 10, 'color:' + PAPER + ';letter-spacing:' + (one ? 2 : 0.5) + 'px;line-height:1.15;padding-top:' + (one ? 8 : 6) + 'px;') + '">' + esc(c.name) + '</div>' +
      (one && c.phrase ? '<div style="font-family:' + DISPLAY + ';font-size:14px;line-height:1.3;color:' + PAPER + ';padding-top:2px;">&ldquo;' + esc(c.phrase) + '&rdquo;</div>' : '') +
      '</td>');
    const rowsOf3 = [];
    for (let k = 0; k < cells.length; k += 3) rowsOf3.push(cells.slice(k, k + 3));
    heroBlock = rowsOf3.map((r, k) => '<table align="center" cellpadding="0" cellspacing="0" width="' + (one ? '100%' : String(Math.round(100 * r.length / 3)) + '%') + '" style="border-collapse:collapse;table-layout:fixed;margin:' + (k ? '14px' : '0') + ' auto 0;"><tr>' + r.join('') + '</tr></table>').join('');
  } else {
    // No character: the Stiff Competition badge on its own, no ring, with the brand line.
    heroBlock = '<div style="height:6px;line-height:6px;font-size:0;">&nbsp;</div>' +
      '<img src="' + MONOGRAM_TRIM + '" alt="Stiff Competition" width="88" height="84" style="width:88px;height:84px;display:block;margin:0 auto;">' +
      '<div style="' + display(16, 'color:' + PAPER + ';letter-spacing:1px;line-height:1.15;padding-top:12px;text-align:center;') + '">Always Standing Tall</div>';
  }
  const stampSize = 40;
  const stampCol = '44';
  const stampImg = '<img src="' + STAMP_IMG[mode] + '" alt="' + mode + '" width="' + stampSize + '" height="' + stampSize + '" style="width:' + stampSize + 'px;height:' + stampSize + 'px;display:block;margin:0 auto 0 0;">';
  const certificate =
  '<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;background:' + PAPER + ';border:3px solid ' + INK + ';table-layout:fixed;"><tr><td style="padding:4px;">' +
  '<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;border:1px solid ' + INK + ';table-layout:fixed;"><tr><td style="padding:8px;">' +
  // HEADER BAND
  '<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;table-layout:fixed;background:' + c1 + ';"><tr><td style="padding:10px 10px 14px;">' +
  '<div class="sc-l" style="text-align:center;' + display(8, 'color:' + PAPER + ';letter-spacing:0.5px;line-height:1.4;') + '">Stiff&nbsp;Competition &middot; Official&nbsp;Record&nbsp;of&nbsp;Release</div>' +
  '<div style="height:8px;line-height:8px;font-size:0;">&nbsp;</div>' +
  '<div style="text-align:center;' + display(18, 'color:' + PAPER + ';letter-spacing:1px;line-height:1.15;') + '">Certificate<br>of Deployment</div>' +
  '<div style="height:10px;line-height:10px;font-size:0;">&nbsp;</div>' +
  heroBlock +
  '</td></tr></table>' +
  // CUSTODY: the main part of the certificate, with the stamp beside the name.
  '<div style="height:18px;line-height:18px;font-size:0;">&nbsp;</div>' +
  '<div style="text-align:center;' + small(10, 'color:' + INK + ';letter-spacing:0.5px;line-height:1.6;') + '" class="sc-t">Released from storage ' + SEND_DATE_PLAIN.replace(/ /g, '&nbsp;') + '<br>Deployed to the custody of</div>' +
  '<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;table-layout:fixed;"><tr>' +
  '<td width="' + stampCol + '" style="font-size:0;line-height:0;">&nbsp;</td>' +
  '<td align="center" valign="middle" style="vertical-align:middle;text-align:center;' + display(nameSize, 'color:' + INK + ';letter-spacing:1px;padding:6px 0 4px;white-space:nowrap;word-wrap:normal;word-break:keep-all;') + '">' + esc(displayName) + '</td>' +
  '<td width="' + stampCol + '" align="left" valign="middle" style="vertical-align:middle;">' + stampImg + '</td>' +
  '</tr></table>' +
  '<div style="text-align:center;' + small(9, 'color:' + INK + ';letter-spacing:0;') + '" class="sc-s">Thirty-two&nbsp;years&nbsp;sealed &middot; Nothing&nbsp;has&nbsp;softened</div>' +
  '<div style="height:18px;line-height:18px;font-size:0;">&nbsp;</div>' +
  // MANIFEST
  manifestHtml(rows, orderNumber) +
  '<div style="height:10px;line-height:10px;font-size:0;">&nbsp;</div>' +
  // SIGN-OFF: the Stiff Competition logo on its own, centred.
  '<div style="height:16px;line-height:16px;font-size:0;">&nbsp;</div>' +
  '<img src="' + WORDMARK + '" alt="Stiff Competition" width="118" height="52" style="width:118px;height:52px;display:block;margin:0 auto;">' +
  '<div style="height:8px;line-height:8px;font-size:0;">&nbsp;</div>' +
  '</td></tr></table></td></tr></table>';
  const btn = (href, label) => '<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;"><tr><td align="center" style="border:1.5px solid #111;border-radius:22px;padding:10px 18px;">' +
    '<a href="' + href + '" style="color:#111;text-decoration:none;font-weight:600;font-size:14px;display:block;">' + label + '</a></td></tr></table>';
  const html = '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>@import url("https://fonts.googleapis.com/css2?family=Oswald:wght@400;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap");@media only screen and (min-width:350px){.sc-l{font-size:9px !important}.sc-t{font-size:11px !important}.sc-s{font-size:10px !important}}</style></head><body style="margin:0;padding:0;background:#e8e5df;-webkit-text-size-adjust:100%;text-size-adjust:100%;">' +
  '<div style="max-width:480px;margin:0 auto;background:#ffffff;padding:10px;font-family:Arial,Helvetica,sans-serif;">' +
  certificate +
  '<div style="height:12px;"></div>' +
  '<div style="text-align:center;font-family:' + MONO + ';font-size:9px;line-height:1.5;color:' + INK2 + ';">' + RECORDS_LINE + '</div>' +
  '<div style="height:14px;"></div>' +
  btn(certUrl, 'Print your certificate') +
  '<div style="height:10px;"></div>' +
  btn(statusUrl, 'Check your order status') +
  '<div style="height:18px;"></div>' +
  crossSellBlock +
  '<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;"><tr><td align="center" style="padding-bottom:3px;">' +
  '<a href="' + STORE + '" style="font-weight:800;font-size:15px;letter-spacing:0.5px;color:#111;text-decoration:none;">STIFF COMPETITION</a>' +
  '</td></tr></table>' +
  '<div style="font-size:11px;line-height:1.3;color:#999;text-align:center;">Digitally restored prototype characters from the cancelled 1994 &#39;Stiff Competition&#39; line. Ultra-rigid PVC digital collectibles built for heavy-duty power and maximum extension. Always standing tall!</div>' +
  '<div style="height:16px;"></div>' +
  '<hr style="border:none;border-top:1px solid #eee;margin:0 0 14px;">' +
  '<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;">' +
  '<tr><td align="center" style="padding-bottom:12px;">' + socialCells + '</td></tr>' +
  '<tr><td align="center" style="font-size:11px;color:#777;line-height:1.4;padding-bottom:8px;">You are receiving this because you ordered from us.<br>' +
  '<a href="' + UNSUB + '" style="color:' + RED + ';font-weight:700;text-decoration:underline;">Don&#39;t want more emails from us?</a></td></tr>' +
  '<tr><td align="center" style="font-size:9px;color:#bbb;line-height:1.3;">Stiff Competition Ltd, 20 Wenlock Road, London N1 7GU, United Kingdom</td></tr>' +
  '</table>' +
  '</div></body></html>';
  out.push({ json: {
    orderId, orderNumber,
    email: isTest ? TEST_TO : email,
    customerId: isTest ? '' : customerId,
    customerEmail: email,
    isTest,
    financialStatus: String(o.financial_status),
    character: found.join(', ') || 'general issue',
    productsShown: picks.length,
    subject: (isTest ? 'TEST — ' : '') + 'Certificate of Deployment — ' + subjectName.replace(/&amp;/g, '&') + subjectMore,
    html, unsubUrl: UNSUB,
    certToken, certUrl,
    certificateHtml: certificate,
    certData: JSON.stringify(certData),
    stampText,
    manifestText: rows.map(r => (r.qty > 1 ? r.qty + ' x ' : '') + r.unit + ' - ' + r.name + (r.sub ? ' - ' + r.sub : '') + (r.spec ? ' - ' + r.spec : '')).join(' | '),
    issuedAt: new Date().toISOString(),
    missingCatchphrase: (found.length === 1 && !catchphrases[found[0]])
  } });
}
if (out.length === 0 && skipped.length) { console.log('Skipped: ' + JSON.stringify(skipped)); }
return out;