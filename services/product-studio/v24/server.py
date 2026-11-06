"""SC Product Studio: runs the heavy image steps of the SC product automation (design tool, print-on-model pictures,
shirt recolouring) away from n8n. Sleeps when idle. Every job: inputs (public URLs) are downloaded into a fresh job folder
next to the tool files, one allowed script runs, chosen outputs go to the Shopify store's Files (Andy, 21 Oct 2026: Cloudinary is full, no longer used) through
SC - File Store, and the job reports its log and links.
  POST /jobs {script, args[], inputs{name:url}, outputs[glob], key}   header X-Studio-Key
  GET  /jobs/{id}
"""
import os, glob, json, uuid, time, shutil, threading, subprocess, requests
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

APP = '/app'; DATA = os.environ.get('DATA_DIR', '/data'); WORK = f'{DATA}/work'; ASSET_DIR = f'{DATA}/assets'
KEY = os.environ.get('STUDIO_KEY', '')
FILE_STORE = 'https://n8n-production-afc2.up.railway.app/webhook/sc-file-store'
FILE_KEY = os.environ.get('FILE_STORE_KEY', '')
MIME = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.json': 'application/json', '.txt': 'text/plain'}
SCRIPTS = {'design': 'sc_tshirt_design_tool.py', 'pics': 'make_pics.py', 'recolour': 'sc_recolour_shirt.py',
           'place': 'sc_print_on_model.py', 'layout': 'sc_layout.py',
           'designauto': 'sc_design_auto.py', 'parts': 'sc_parts.py', 'eyes': 'sc_find_eyes.py', 'productpics': 'sc_product_pics.py', 'modelpics': 'sc_model_pics.py', 'mugpics': 'sc_mug_pics.py', 'bottlepics': 'sc_bottle_pics.py'}
ASSETS = json.load(open(f'{APP}/assets.json'))           # {relative path: public url}
app = FastAPI(); JOBS = {}; LOCK = threading.Semaphore(1)   # one heavy job at a time
# Jobs are kept on the volume (Andy, 20 Oct 2026: bottle pictures were lost when the service slept before the runner
# came back for them), and while a job is queued or running the service makes a small outside call every 30 s so it
# is not put to sleep mid-job.
JOB_DIR = f'{DATA}/jobs'

def save(J):
    try:
        os.makedirs(JOB_DIR, exist_ok=True); t = f'{JOB_DIR}/{J["id"]}.tmp'
        with open(t, 'w') as f: json.dump(J, f)
        os.replace(t, f'{JOB_DIR}/{J["id"]}.json')
    except Exception: pass

def keep_awake():
    while True:
        time.sleep(30)
        if any(j.get('status') in ('queued', 'running') for j in list(JOBS.values())):
            try: requests.head('https://cdn.shopify.com/', timeout=10)
            except Exception: pass
threading.Thread(target=keep_awake, daemon=True).start()

def get(url, path):
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with requests.get(url, stream=True, timeout=600) as r:
        r.raise_for_status()
        with open(path, 'wb') as f:
            for chunk in r.iter_content(1 << 20): f.write(chunk)

def ensure_assets():
    for rel, url in ASSETS.items():
        p = f'{ASSET_DIR}/{rel}'
        if not os.path.exists(p): get(url, p)

def store(paths, prefix):
    """Puts files in the Shopify store's Files: upload addresses from SC - File Store, the bytes go straight to
    Shopify's storage, then the files are registered and their cdn.shopify.com links read back. {path: url or 'ERROR ...'}"""
    out = {p: 'ERROR not stored' for p in paths}
    H = {'x-file-key': FILE_KEY}
    def call(body):
        for i in range(4):
            try:
                r = requests.post(FILE_STORE, json=body, headers=H, timeout=120); d = r.json()
                if d.get('ok'): return d
                err = d.get('error')
            except Exception as e: err = f'{type(e).__name__}: {e}'
            time.sleep(5 * (i + 1))
        raise RuntimeError(f'file store: {err}')
    for k in range(0, len(paths), 25):
        part = paths[k:k + 25]
        names = [(prefix + '_' + os.path.basename(p)).replace('/', '_')[-180:] for p in part]
        mimes = [MIME.get(os.path.splitext(p)[1].lower(), 'application/octet-stream') for p in part]
        try:
            tg = call({'action': 'targets', 'files': [{'name': n, 'mime': m} for n, m in zip(names, mimes)]})['targets']
            for p, t, m in zip(part, tg, mimes):
                with open(p, 'rb') as f:
                    r = requests.put(t['url'], data=f, headers={'Content-Type': m}, timeout=600)
                if r.status_code >= 300: raise RuntimeError(f'upload {os.path.basename(p)}: {r.status_code}')
            files = call({'action': 'create', 'items': [{'source': t['source'], 'name': n, 'alt': n} for t, n in zip(tg, names)]})['files']
            ids = {f['id']: p for f, p in zip(files, part)}
            deadline = time.time() + 600
            while ids and time.time() < deadline:
                time.sleep(3)
                for f in call({'action': 'status', 'ids': list(ids)})['files']:
                    if not f: continue
                    if f.get('url'): out[ids.pop(f['id'])] = f['url']
                    elif f.get('status') == 'FAILED': out[ids.pop(f['id'])] = 'ERROR ' + (f.get('error') or 'Shopify could not process the file')
        except Exception as e:
            for p in part:
                if not out[p].startswith('https'): out[p] = f'ERROR {e}'
    return out

class Job(BaseModel):
    script: str
    args: list = []
    inputs: dict = {}
    outputs: list = []
    key: str = ''

def run(jid, job):
    J = JOBS[jid]; d = f'{WORK}/{jid}'
    try:
        with LOCK:
            J['status'] = 'running'; save(J); ensure_assets(); os.makedirs(d)
            for src in (APP, ASSET_DIR):                      # tool files + assets visible in the job folder
                for n in os.listdir(src):
                    if not os.path.exists(f'{d}/{n}'): os.symlink(f'{src}/{n}', f'{d}/{n}')
            for name, url in job.inputs.items(): get(url, f'{d}/{name}')
            p = subprocess.run(['python3', SCRIPTS[job.script], *map(str, job.args)], cwd=d, capture_output=True, text=True, timeout=3600)
            J['log'] = (p.stdout + p.stderr)[-6000:]; J['code'] = p.returncode
            files = sorted({f for g in job.outputs for f in glob.glob(f'{d}/{g}', recursive=True)})
            got = store(files, job.key or jid) if files else {}
            J['files'] = {os.path.relpath(f, d): got[f] for f in files}
            J['status'] = 'done' if p.returncode == 0 else 'failed'
    except Exception as e:
        J['status'] = 'failed'; J['log'] = J.get('log', '') + f'\n{type(e).__name__}: {e}'
    finally:
        J['ended'] = time.time(); save(J); shutil.rmtree(d, ignore_errors=True)

@app.get('/health')
def health(): return {'ok': True, 'jobs': len(JOBS)}

@app.post('/jobs')
def create(job: Job, x_studio_key: str = Header('')):
    if not KEY or x_studio_key != KEY: raise HTTPException(401, 'bad key')
    if job.script not in SCRIPTS: raise HTTPException(400, f'script must be one of {sorted(SCRIPTS)}')
    jid = uuid.uuid4().hex[:12]; JOBS[jid] = {'id': jid, 'status': 'queued', 'script': job.script, 'started': time.time()}; save(JOBS[jid])
    threading.Thread(target=run, args=(jid, job), daemon=True).start(); return JOBS[jid]

@app.get('/jobs/{jid}')
def status(jid: str, x_studio_key: str = Header('')):
    if not KEY or x_studio_key != KEY: raise HTTPException(401, 'bad key')
    if jid in JOBS: return JOBS[jid]
    try: J = json.load(open(f'{JOB_DIR}/{jid}.json'))
    except Exception: raise HTTPException(404, 'no such job')
    if J.get('status') in ('queued', 'running'): J['status'] = 'failed'; J['log'] = J.get('log', '') + '\nThe studio restarted while this job was running.'   # a job cut off by a restart never finishes
    return J
