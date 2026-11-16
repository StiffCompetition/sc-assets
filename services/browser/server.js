// SC Browser: headless Chromium on Railway with a saved profile (volume at /data),
// a wallet signer for OpenSea sign-in (admin key from ADMIN_PRIVATE_KEY), a secured HTTP API
// and an action log. Started on demand, closed after IDLE_MINUTES of no use to keep RAM low.
const express = require('express');
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const { Wallet, getBytes, isHexString, toUtf8String } = require('ethers');

const SECRET = process.env.BROWSER_SECRET || '';
const KEY = process.env.ADMIN_PRIVATE_KEY || '';
const DATA = process.env.DATA_DIR || '/data';
const PROFILE = path.join(DATA, 'profile');
const LOG = path.join(DATA, 'actions.jsonl');
const IDLE_MS = (Number(process.env.IDLE_MINUTES) || 10) * 60 * 1000;
const PORT = Number(process.env.PORT) || 3000;
const CHAIN_ID = process.env.CHAIN_ID_HEX || '0x89'; // Polygon

if (!SECRET) { console.error('BROWSER_SECRET missing'); process.exit(1); }
fs.mkdirSync(PROFILE, { recursive: true });
const wallet = KEY ? new Wallet(KEY.startsWith('0x') ? KEY : '0x' + KEY) : null;

function log(entry) {
  try { fs.appendFileSync(LOG, JSON.stringify({ t: new Date().toISOString(), ...entry }) + '\n'); } catch (e) {}
}

let ctx = null, page = null, idleTimer = null, starting = null;

async function walletRequest(method, params) {
  if (!wallet) throw new Error('no wallet');
  params = params || [];
  switch (method) {
    case 'eth_requestAccounts':
    case 'eth_accounts': return [wallet.address];
    case 'eth_chainId': return CHAIN_ID;
    case 'net_version': return String(parseInt(CHAIN_ID, 16));
    case 'wallet_switchEthereumChain':
    case 'wallet_addEthereumChain':
    case 'wallet_requestPermissions':
    case 'wallet_revokePermissions': return null;
    case 'personal_sign': {
      const m = params[0];
      const bytes = isHexString(m) ? getBytes(m) : new TextEncoder().encode(String(m));
      return wallet.signMessage(bytes);
    }
    case 'eth_sign': {
      const m = params[1];
      const bytes = isHexString(m) ? getBytes(m) : new TextEncoder().encode(String(m));
      return wallet.signMessage(bytes);
    }
    case 'eth_signTypedData_v4':
    case 'eth_signTypedData': {
      const td = typeof params[1] === 'string' ? JSON.parse(params[1]) : params[1];
      const types = { ...td.types }; delete types.EIP712Domain;
      return wallet.signTypedData(td.domain, types, td.message);
    }
    default: throw new Error('unsupported method ' + method);
  }
}

const INIT = `(() => {
  if (window.__scWalletInstalled) return; window.__scWalletInstalled = true;
  const listeners = {};
  const provider = {
    isMetaMask: true,
    _events: {},
    selectedAddress: null,
    chainId: '${CHAIN_ID}',
    networkVersion: '${parseInt(CHAIN_ID, 16)}',
    isConnected: () => true,
    request: async ({ method, params }) => {
      const r = await window.__scWallet(method, params || []);
      if (method === 'eth_requestAccounts' || method === 'eth_accounts') provider.selectedAddress = r[0];
      return r;
    },
    enable: async () => provider.request({ method: 'eth_requestAccounts' }),
    send: (a, b) => typeof a === 'string' ? provider.request({ method: a, params: b }) : provider.request(a),
    sendAsync: (payload, cb) => provider.request(payload).then(result => cb(null, { id: payload.id, jsonrpc: '2.0', result })).catch(cb),
    on: (e, f) => { (listeners[e] = listeners[e] || []).push(f); return provider; },
    removeListener: (e, f) => { listeners[e] = (listeners[e] || []).filter(x => x !== f); return provider; },
    removeAllListeners: () => provider
  };
  window.ethereum = provider;
  const info = { uuid: '4c3a4b2e-5c6c-4a8e-9a9b-7b0f3c1d2e10', name: 'MetaMask', icon: 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiI+PHJlY3Qgd2lkdGg9IjMyIiBoZWlnaHQ9IjMyIiBmaWxsPSIjZjY4NTFiIi8+PC9zdmc+', rdns: 'io.metamask' };
  const announce = () => window.dispatchEvent(new CustomEvent('eip6963:announceProvider', { detail: Object.freeze({ info, provider }) }));
  window.addEventListener('eip6963:requestProvider', announce);
  announce();
})();`;

async function ensureBrowser() {
  if (ctx) { touch(); return page; }
  if (starting) return starting;
  starting = (async () => {
    ctx = await chromium.launchPersistentContext(PROFILE, {
      headless: true,
      viewport: { width: 1280, height: 900 },
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
      locale: 'en-GB',
      timezoneId: 'Europe/London',
      args: ['--disable-blink-features=AutomationControlled', '--no-sandbox', '--disable-dev-shm-usage', '--js-flags=--max-old-space-size=512']
    });
    await ctx.exposeFunction('__scWallet', (method, params) => walletRequest(method, params));
    await ctx.addInitScript(INIT);
    page = ctx.pages()[0] || await ctx.newPage();
    ctx.on('close', () => { ctx = null; page = null; });
    log({ event: 'browser started' });
    touch();
    return page;
  })();
  try { return await starting; } finally { starting = null; }
}

function touch() {
  clearTimeout(idleTimer);
  idleTimer = setTimeout(closeBrowser, IDLE_MS);
}

async function closeBrowser() {
  clearTimeout(idleTimer);
  if (ctx) { try { await ctx.close(); } catch (e) {} ctx = null; page = null; log({ event: 'browser closed (idle or stop)' }); }
}

async function runStep(p, s) {
  const to = s.timeout || 30000;
  switch (s.op) {
    case 'goto': await p.goto(s.url, { waitUntil: s.waitUntil || 'domcontentloaded', timeout: Math.max(to, 45000) }); return { url: p.url(), title: await p.title() };
    case 'click': if (s.selector) await p.click(s.selector, { timeout: to }); else if (s.text) await p.getByText(s.text, { exact: !!s.exact }).first().click({ timeout: to }); else await p.mouse.click(s.x, s.y); return 'clicked';
    case 'fill': await p.fill(s.selector, s.value, { timeout: to }); return 'filled';
    case 'type': await p.keyboard.type(s.value, { delay: s.delay || 20 }); return 'typed';
    case 'press': await p.keyboard.press(s.key); return 'pressed';
    case 'wait': await p.waitForTimeout(Math.min(s.ms || 1000, 60000)); return 'waited';
    case 'waitFor': await p.waitForSelector(s.selector, { timeout: to }); return 'found';
    case 'text': return (await p.evaluate(sel => (sel ? document.querySelector(sel) : document.body).innerText, s.selector || null)).slice(0, s.max || 20000);
    case 'html': return (await p.content()).slice(0, s.max || 50000);
    case 'eval': return await p.evaluate(s.js);
    case 'url': return { url: p.url(), title: await p.title() };
    case 'upload': await p.setInputFiles(s.selector, s.files); return 'uploaded';
    case 'scroll': await p.mouse.wheel(0, s.dy || 600); return 'scrolled';
    case 'screenshot': { const b = await p.screenshot({ type: 'jpeg', quality: s.quality || 55, fullPage: !!s.full }); return { jpeg_base64: b.toString('base64') }; }
    default: throw new Error('unknown op ' + s.op);
  }
}

const app = express();
app.use(express.json({ limit: '5mb' }));
function auth(req, res, next) {
  const k = req.get('x-browser-secret') || req.query.k || '';
  if (k !== SECRET) return res.status(401).json({ error: 'unauthorized' });
  next();
}

app.get('/health', (req, res) => res.json({ ok: true, browser: !!ctx, wallet: wallet ? wallet.address : null }));

app.post('/run', auth, async (req, res) => {
  const steps = Array.isArray(req.body.steps) ? req.body.steps : [];
  const who = String(req.body.who || 'unknown').slice(0, 80);
  const purpose = String(req.body.purpose || '').slice(0, 200);
  const results = [];
  try {
    const p = await ensureBrowser();
    for (const s of steps) {
      try {
        const r = await runStep(p, s);
        results.push({ op: s.op, ok: true, result: r });
        log({ who, purpose, op: s.op, url: s.url || s.selector || s.text || '', ok: true });
      } catch (e) {
        results.push({ op: s.op, ok: false, error: String(e.message || e).slice(0, 400) });
        log({ who, purpose, op: s.op, ok: false, error: String(e.message || e).slice(0, 200) });
        if (!s.continueOnError) break;
      }
    }
    touch();
    res.json({ results, url: p.url() });
  } catch (e) {
    log({ who, purpose, event: 'run failed', error: String(e.message || e).slice(0, 200) });
    res.status(500).json({ error: String(e.message || e) });
  }
});

app.post('/stop', auth, async (req, res) => { await closeBrowser(); res.json({ ok: true }); });

app.get('/log', auth, (req, res) => {
  try {
    const lines = fs.readFileSync(LOG, 'utf8').trim().split('\n');
    res.type('text/plain').send(lines.slice(-Number(req.query.n || 200)).join('\n'));
  } catch (e) { res.type('text/plain').send(''); }
});

// Live view for a one-time sign-in from a phone: screenshot, tap and type.
app.get('/shot', auth, async (req, res) => {
  try {
    const p = await ensureBrowser();
    const b = await p.screenshot({ type: 'jpeg', quality: 60 });
    res.type('image/jpeg').send(b);
  } catch (e) { res.status(500).send(String(e.message || e)); }
});
app.post('/tap', auth, async (req, res) => {
  try {
    const p = await ensureBrowser();
    if (req.body.url) await p.goto(req.body.url, { waitUntil: 'domcontentloaded' });
    if (typeof req.body.x === 'number') await p.mouse.click(req.body.x, req.body.y);
    if (req.body.text) await p.keyboard.type(req.body.text, { delay: 25 });
    if (req.body.key) await p.keyboard.press(req.body.key);
    log({ who: 'live view', op: 'tap/type', ok: true });
    res.json({ ok: true, url: p.url() });
  } catch (e) { res.status(500).json({ error: String(e.message || e) }); }
});
app.get('/live', auth, (req, res) => {
  const k = encodeURIComponent(req.query.k || '');
  res.type('html').send(`<!doctype html><meta name=viewport content="width=device-width,initial-scale=1"><body style="margin:0;font-family:sans-serif">
<div style="padding:6px"><input id=u placeholder="https://..." style="width:62%"><button onclick="go()">Go</button>
<input id=t placeholder="type text" style="width:50%"><button onclick="typ()">Type</button><button onclick="key('Enter')">Enter</button></div>
<img id=i style="width:100%;display:block" onclick="tap(event)"><script>
const k='${k}';const img=document.getElementById('i');
function ref(){img.src='/shot?k='+k+'&r='+Date.now();}
img.onload=()=>setTimeout(ref,1500);ref();
async function post(b){await fetch('/tap?k='+k,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(b)});}
function tap(e){const r=img.getBoundingClientRect();post({x:Math.round((e.clientX-r.left)*1280/r.width),y:Math.round((e.clientY-r.top)*900/r.height)});}
function go(){post({url:document.getElementById('u').value});}
function typ(){post({text:document.getElementById('t').value});document.getElementById('t').value='';}
function key(x){post({key:x});}
</script></body>`);
});

app.listen(PORT, () => console.log('sc-browser on ' + PORT));
process.on('SIGTERM', async () => { await closeBrowser(); process.exit(0); });
