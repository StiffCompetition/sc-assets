import sys, calendar, os
sys.path.insert(0,'/tmp/pg')
import icons as IC
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS=None
pic,out,month,caption,name,cry,monday,accent=sys.argv[1],sys.argv[2],int(sys.argv[3]),sys.argv[4],sys.argv[5],sys.argv[6],sys.argv[7]=='mon',sys.argv[8]
MM=300/25.4; mm=lambda v:round(v*MM)
W,H=mm(float(os.environ.get('PW','287.4'))),mm(float(os.environ.get('PH','427.1'))); B=mm(4)
INK=(30,30,30); LINE=(190,190,190); GRY=(110,110,110); ACC=tuple(int(accent[i:i+2],16) for i in (0,2,4))
F='/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'; R='/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
f=lambda s,p=F: ImageFont.truetype(p,s)
im=Image.new('RGB',(W,H),(255,255,255)); d=ImageDraw.Draw(im)
p=Image.open(pic).convert('RGB'); ph=round(p.height*W/p.width)
im.paste(p.resize((W,ph),Image.LANCZOS),(0,0))
L=B+mm(12); Rr=W-B-mm(12)   # 12 mm inside trim
y=ph+mm(7)
d.text((L,y),calendar.month_name[month].upper(),font=f(mm(17)),fill=INK)
mw=d.textlength(calendar.month_name[month].upper(),font=f(mm(17)))
d.text((L+mw+mm(5),y+mm(5)),'2027',font=f(mm(12)),fill=ACC)
ft=f(mm(9)); cs=mm(9)
while d.textlength(caption,font=ft)>(Rr-L-mw-mm(40)): cs-=2; ft=f(cs)
d.text((Rr,y+mm(8)),caption,font=ft,fill=ACC,anchor='ra')
gy=y+mm(24); hdr=['MON','TUE','WED','THU','FRI','SAT','SUN'] if monday else ['SUN','MON','TUE','WED','THU','FRI','SAT']
cw=(Rr-L)/7; rh=mm(float(os.environ.get('ROWH','19.5')))
for i,h in enumerate(hdr): d.text((L+cw*i+cw/2,gy+mm(4)),h,font=f(mm(3.6)),fill=GRY,anchor='mm')
top=gy+mm(8)
weeks=calendar.Calendar(0 if monday else 6).monthdayscalendar(2027,month)
d.line([L,top,Rr,top],fill=INK,width=5)
for r in range(len(weeks)+1): d.line([L,top+rh*r,Rr,top+rh*r],fill=LINE,width=3)
for c in range(8): d.line([L+cw*c,top,L+cw*c,top+rh*len(weeks)],fill=LINE,width=3)
for r,wk in enumerate(weeks):
    for c,day in enumerate(wk):
        if day: d.text((L+cw*c+mm(2),top+rh*r+mm(1.5)),str(day),font=f(mm(5.5)),fill=INK)
        if day==IC.DATES[month]:
            isz=mm(13.5); ic=IC.ICONS[month]().resize((isz,isz),Image.LANCZOS)
            im.paste(ic,(round(L+cw*(c+1)-isz-mm(1.5)),round(top+rh*r+mm(3))),ic)
sy=H-B-mm(23)
d.line([L,sy,Rr,sy],fill=INK,width=4)
d.text((L,sy+mm(3)),name.upper(),font=f(mm(8)),fill=ACC)
d.text((L,sy+mm(13.5)),'\u201c'+cry+'\u201d',font=f(mm(6),R),fill=INK)
d.text((Rr,sy+mm(4)),'STIFF COMPETITION',font=f(mm(6)),fill=INK,anchor='ra'); d.text((Rr,sy+mm(13.5)),'stiffcompetition.shop',font=f(mm(5.5),R),fill=GRY,anchor='ra')
im.save(out,quality=95,dpi=(300,300))
print(W,H,ph,'grid end mm',(top+rh*len(weeks))/MM,'strip',sy/MM)
