#!/usr/bin/env python3
"""Free background maker (Hugging Face FLUX.1-schnell space). Usage: free_bg.py JOB.json OUT.png
JOB.json: {"prompt": "...", "seed": 1}. Runs on a GitHub runner (its own internet address, own free allowance)."""
import json, sys, shutil
from gradio_client import Client
job = json.load(open(sys.argv[1]))
c = Client('black-forest-labs/FLUX.1-schnell')
res = c.predict(job['prompt'], job.get('seed', 0), False, 896, 1024, 4, api_name='/infer')
path = res[0] if isinstance(res, (list, tuple)) else res
shutil.copy(path, sys.argv[2]); print('OK', sys.argv[2])
