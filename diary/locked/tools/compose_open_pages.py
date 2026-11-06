from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageChops
import numpy as np
from scipy.signal import find_peaks
F="/home/claude/fonts_work/"
cfg={
 "major_wood":("just-another-hand",(28,30,26),(650,150,1040,760),"DAILY ORDERS LOG",["0600 HOURS. ROSE. STOOD.","0601 HOURS. STOOD SOME MORE.","0615 HOURS. ORDER: BUY MILK.","0640 HOURS. MILK NOT FOUND.","0641 HOURS. SEARCHING AISLES.","STATUS: EXCELLENT."],44),
 "rear_admiral":("parisienne",(24,36,92),(650,150,1030,750),"Ship's Log",["Day 1 on dry land.","Set sail at dawn for the","post office. Returned with","one stamp. A fine haul.","The duck is unimpressed."],38),
 "hanky":("permanent-marker",(60,60,66),(130,150,540,740),"SITE NOTES",["Mon. Fixed it. Again.","Heavy tool ready by 7.","Boss says stop saying that.","Cups of tea: 6"],30),
 "slick_willy":("kaushan-script",(30,30,36),(630,190,980,720),"My Brand Journal",["Dear Diary,","14 views today. Up 3.","Quit job number 3.","It slid right off me.","Dream big. Sell bigger."],34),
 "velvet_python":("great-vibes",(70,30,110),(660,150,1040,760),"Dear Diary",["Everyone was rushing again.","I strolled. A velvet pace.","Pressed one leaf.","Shoes still absent.","Yours, the Velvet Python"],42),
 "the_grip":("gloria-hallelujah",(34,40,72),(625,170,980,730),"Dear Diary",["Helped a man open a jar.","The jar is now in 3 pieces.","Bought him a new jar.","Hugged my bear. Good day."],28),
}
out=[]
for k,(font,ink,box,title,lines,size) in cfg.items():
    im=Image.open(f'photos/{k}.png').convert('RGB'); W,H=im.size
    x0,y0,x1,y1=box
    g=np.array(im.convert('L').crop(box)).astype(float)
    prof=g[:,20:-20].mean(axis=1); prof=prof-np.convolve(prof,np.ones(41)/41,'same')
    pk,_=find_peaks(-prof,distance=12,prominence=1.2)
    f=ImageFont.truetype(F+font+".ttf",size)
    layer=Image.new('L',(W,H),0); d=ImageDraw.Draw(layer)
    SW=1 if k=='major_wood' else 0
    ys=[y0+int(p) for p in pk]
    ruled=len(ys)>=8
    # title then lines
    if ruled:
        sp=float(np.median(np.diff(ys))); kstep=max(1,int(np.ceil(size*1.25/sp)))
        start=next(i for i,y in enumerate(ys) if y>y0+size*2)
        base=[ys[start+i*kstep] for i in range(len(lines)+1) if start+i*kstep<len(ys)]
        while len(base)<len(lines)+1: base.append(base[-1]+sp*kstep)
        # shift so text sits on rules
        d.text((x0+10,base[0]-3),title,font=ImageFont.truetype(F+font+".ttf",size+4),fill=255,anchor='ls',stroke_width=SW,stroke_fill=255)
        for i,l in enumerate(lines): d.text((x0+10,base[i+1]-3),l,font=f,fill=255,anchor='ls',stroke_width=SW,stroke_fill=255)
    else:
        y=y0+60
        d.text((x0+10,y),title,font=ImageFont.truetype(F+font+".ttf",size+6),fill=255,anchor='ls',stroke_width=SW,stroke_fill=255); y+=size*1.8
        for l in lines: d.text((x0+10,y),l,font=f,fill=255,anchor='ls',stroke_width=SW,stroke_fill=255); y+=size*1.4
    layer=layer.filter(ImageFilter.GaussianBlur(0.7))
    ink_img=Image.new('RGB',(W,H),ink)
    res=Image.composite(ImageChops.multiply(im,Image.new('RGB',(W,H),tuple(int(c*0.35+165) for c in ink))) ,im,layer.point(lambda v:int(v*0.0)))
    res=im.copy(); res.paste(ink_img,(0,0),layer.point(lambda v:int(v*0.88)))
    res.save(f'photos/{k}_final.png'); out.append(res)
sheet=Image.new('RGB',(3*600,2*450),'white')
for i,r in enumerate(out): sheet.paste(r.resize((600,448)),((i%3)*600,(i//3)*450))
sheet.save('open_final_sheet.jpg',quality=90)
