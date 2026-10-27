import json,base64,sys
d=json.loads(open(sys.argv[1]).read())
def find(o):
  if isinstance(o,dict):
    if isinstance(o.get('content'),str) and len(o['content'])>1000: return o['content']
    for v in o.values():
      r=find(v)
      if r: return r
  if isinstance(o,list):
    for v in o:
      r=find(v)
      if r: return r
  if isinstance(o,str) and o.strip().startswith('{'): return find(json.loads(o))
c=find(d).replace('-','+').replace('_','/'); c+='='*(-len(c)%4)
open(sys.argv[2],'wb').write(base64.b64decode(c))
