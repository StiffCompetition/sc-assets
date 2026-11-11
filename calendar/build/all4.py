import sys
OUT=sys.argv[1]; MON=sys.argv[2]
import subprocess, colorsys
from PIL import Image
M=[(1,'jan','STANDING TO ATTENTION','Major Wood',"Reporting for duty, all year long."),
(2,'feb','BEHIND THE VELVET ROPE','Velvet Python',"Roses are red. The rope is velvet."),
(3,'mar','ROLL OUT THE BARREL','The Grip',"Lucky for some. Lucky for you."),
(4,'apr','EGG-STRA SPECIAL DELIVERY','Slick Willy',"Delivered fresh, handled with care."),
(5,'may','IN FULL BLOOM',"Hammerin' Hanky","Everything comes up rigid in spring."),
(6,'jun','MASKS OFF','Velvet Python',"A little mystery goes a long way."),
(7,'jul','LICK IT BEFORE IT MELTS','Major Wood',"At ease, soldiers. Ice lollies are in."),
(8,'aug','GRAB YOUR BUNS','The Grip',"Hot, fresh and held just right."),
(9,'sep','ROLL IN THE LEAVES','Slick Willy',"Autumn suits a smooth finish."),
(10,'oct','PERMISSION TO COME ABOARD','Rear Admiral',"Steady as she goes, sailors."),
(11,'nov','SPARKS FLY',"Hammerin' Hanky","I swing hard and I never miss."),
(12,'dec','NAUGHTY LIST: ALL SIX','All six',"Santa checked it twice. We're all on it.")]
import glob
for n,k,cap,ch,cry in M:
    src=glob.glob(f'/tmp/pr2/cal2027_print_{n:02d}_*.jpg') or glob.glob(f'/tmp/pr/cal2027_print_{n:02d}_*.jpg')
    src=src[0]
    im=Image.open(src).convert('RGB').resize((200,160))
    best=None
    for (cnt,px) in im.getcolors(40000):
        h,s,v=colorsys.rgb_to_hsv(*[c/255 for c in px])
        if s>0.55 and 0.25<v<0.95:
            sc=cnt*s
            if not best or sc>best[0]: best=(sc,h,s,v)
    h,s,v=best[1],best[2],best[3]
    r,g,b=colorsys.hsv_to_rgb(h,max(s,0.75),min(v,0.62))
    acc='%02X%02X%02X'%(round(r*255),round(g*255),round(b*255))
    if k=='may': acc='C2185B'
    import os
    env=dict(os.environ); env['MARK']={2:'14:heart',3:'17:shamrock'}.get(n,''); env['PW']=sys.argv[3]; env['PH']=sys.argv[4]; env['ROWH']=sys.argv[5]; env['TOPBAND']='14'; env.setdefault('TITLE','2'); env.setdefault('NOYEAR','1'); env['MARKTXT']={2:"Valentine's Day",3:"St Patrick's Day"}.get(n,'')
    subprocess.run(['python3','page6.py',src,f'{OUT}/{n:02d}_{k}.jpg',str(n),cap,ch,cry,MON,acc],check=True,capture_output=True,env=env)
    print(n,k,acc,src.split('/')[-1])
