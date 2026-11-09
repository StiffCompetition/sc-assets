import json,base64,sys
t=open(sys.argv[1]).read();j=json.loads(t[t.index('{'):])
def find(o):
    if isinstance(o,dict):
        for k,v in o.items():
            if k=='content' and isinstance(v,str):return v
            r=find(v)
            if r:return r
    elif isinstance(o,list):
        for v in o:
            r=find(v)
            if r:return r
c=find(j).replace('-','+').replace('_','/');c+='='*(-len(c)%4)
open(sys.argv[2],'wb').write(base64.b64decode(c))
