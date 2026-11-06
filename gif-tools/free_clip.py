#!/usr/bin/env python3
"""Free clip maker (Hugging Face Wan 2.2 ZeroGPU space). Usage: free_clip.py JOB.json OUT.mp4
JOB.json: {"image_url": "...raw link...", "prompt": "...", "seed": 42 (optional)}
Each anonymous internet address gets a few clips a day, so this runs on any machine with its own address
(n8n server, Composio sandbox, GitHub runner) to spread the allowance."""
import json, sys, random, string, requests
SP = 'https://zerogpu-aoti-wan2-2-fp8da-aoti-faster.hf.space'
NEG = '色调艳丽, 过曝, 静态, 细节模糊不清, 字幕, 风格, 作品, 画作, 画面, 静止, 整体发灰, 最差质量, 低质量, JPEG压缩残留, 丑陋的, 残缺的, 多余的手指, 画得不好的手部, 画得不好的脸部, 畸形的, 毁容的, 形态畸形的肢体, 手指融合, 静止不动的画面, 杂乱的背景, 三条腿, 背景人很多, 倒着走'
job = json.load(open(sys.argv[1])); out = sys.argv[2]
h = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
img = {'path': job['image_url'], 'url': job['image_url'], 'orig_name': 'start.jpg', 'meta': {'_type': 'gradio.FileData'}}
data = [img, job['prompt'], 6, NEG, job.get('duration', 3.5), 1, 1, job.get('seed', 42), 'seed' not in job]
r = requests.post(SP + '/gradio_api/queue/join', json={'data': data, 'event_data': None, 'fn_index': 0, 'trigger_id': None, 'session_hash': h}, timeout=60)
r.raise_for_status()
s = requests.get(SP + '/gradio_api/queue/data', params={'session_hash': h}, stream=True, timeout=600)
for line in s.iter_lines():
    if line and line.startswith(b'data:'):
        d = json.loads(line[5:])
        if d.get('msg') == 'process_completed':
            if not d.get('success'): sys.exit('FAILED: ' + json.dumps(d.get('output'))[:400])
            url = d['output']['data'][0]['url']
            open(out, 'wb').write(requests.get(url, timeout=120).content); print('OK', out); sys.exit(0)
sys.exit('FAILED: stream ended')
