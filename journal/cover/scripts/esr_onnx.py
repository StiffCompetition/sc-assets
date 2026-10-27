import zipfile, pickle, numpy as np, onnx, sys
from onnx import helper, TensorProto, numpy_helper
def load_pth(path):
    z=zipfile.ZipFile(path); names=z.namelist(); root=names[0].split('/')[0]
    class Storage:
        def __init__(s,key,dtype): s.key=key; s.dtype=dtype
    class U(pickle.Unpickler):
        def find_class(s,mod,name):
            if name=='_rebuild_tensor_v2':
                def rb(storage,offset,size,stride,*a):
                    buf=np.frombuffer(z.read(f'{root}/data/{storage.key}'),dtype=storage.dtype)
                    n=int(np.prod(size)) if size else 1
                    return np.lib.stride_tricks.as_strided(buf[offset:],shape=size,strides=[x*buf.itemsize for x in stride]).copy() if size else buf[offset:offset+1].copy()
                return rb
            if name=='FloatStorage': return np.float32
            if name=='HalfStorage': return np.float16
            if mod=='collections' and name=='OrderedDict':
                import collections; return collections.OrderedDict
            if mod=='torch._utils' and name=='_rebuild_parameter':
                return lambda data,req,hooks: data
            return super().find_class(mod,name)
        def persistent_load(s,pid):
            _,stype,key,loc,numel=pid
            return Storage(key,stype if isinstance(stype,type) else np.float32)
    d=U(z.open(f'{root}/data.pkl')).load()
    if 'params_ema' in d: d=d['params_ema']
    elif 'params' in d: d=d['params']
    return {k:np.asarray(v,dtype=np.float32) for k,v in d.items()}
W=load_pth(sys.argv[1]); nodes=[]; inits=[]
cnt=[0]
def nm(p): cnt[0]+=1; return f'{p}_{cnt[0]}'
def conv(x,key):
    w=numpy_helper.from_array(W[key+'.weight'],key+'.weight'); b=numpy_helper.from_array(W[key+'.bias'],key+'.bias'); inits.extend([w,b])
    o=nm('c'); nodes.append(helper.make_node('Conv',[x,key+'.weight',key+'.bias'],[o],pads=[1,1,1,1],kernel_shape=[3,3])); return o
def lrelu(x): o=nm('l'); nodes.append(helper.make_node('LeakyRelu',[x],[o],alpha=0.2)); return o
def cat(xs): o=nm('cat'); nodes.append(helper.make_node('Concat',xs,[o],axis=1)); return o
consts={}
def scal(v):
    if v not in consts:
        n=f'const_{len(consts)}'; inits.append(numpy_helper.from_array(np.array(v,dtype=np.float32),n)); consts[v]=n
    return consts[v]
def mul(x,v): o=nm('m'); nodes.append(helper.make_node('Mul',[x,scal(v)],[o])); return o
def add(a,b): o=nm('a'); nodes.append(helper.make_node('Add',[a,b],[o])); return o
def rdb(x,p):
    x1=lrelu(conv(x,p+'.conv1')); x2=lrelu(conv(cat([x,x1]),p+'.conv2')); x3=lrelu(conv(cat([x,x1,x2]),p+'.conv3'))
    x4=lrelu(conv(cat([x,x1,x2,x3]),p+'.conv4')); x5=conv(cat([x,x1,x2,x3,x4]),p+'.conv5'); return add(mul(x5,0.2),x)
def up(x):
    o=nm('up'); inits.append(numpy_helper.from_array(np.array([1,1,2,2],dtype=np.float32),o+'_s'))
    nodes.append(helper.make_node('Resize',[x,'',o+'_s'],[o],mode='nearest')); return o
x='input'; feat=conv(x,'conv_first'); b=feat
for i in range(23):
    t=b
    for j in (1,2,3): t=rdb(t,f'body.{i}.rdb{j}')
    b=add(mul(t,0.2),b)
feat=add(feat,conv(b,'conv_body'))
feat=lrelu(conv(up(feat),'conv_up1')); feat=lrelu(conv(up(feat),'conv_up2'))
out=conv(lrelu(conv(feat,'conv_hr')),'conv_last')
nodes.append(helper.make_node('Identity',[out],['output']))
g=helper.make_graph(nodes,'rrdb',[helper.make_tensor_value_info('input',TensorProto.FLOAT,[1,3,None,None])],[helper.make_tensor_value_info('output',TensorProto.FLOAT,[1,3,None,None])],inits)
m=helper.make_model(g,opset_imports=[helper.make_opsetid('',13)]); m.ir_version=8; onnx.checker.check_model(m); onnx.save(m,sys.argv[2]); print('ok',len(nodes))
