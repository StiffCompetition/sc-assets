from PIL import Image,ImageDraw,ImageFont,ImageFilter
import math,random
F="/home/claude/fonts_work/"
W,H=1600,1100
chars=[
 ("major_wood","just-another-hand",(84,92,56),(200,168,70),(244,238,222),"grid",
  "DAILY ORDERS LOG",
  ["0600 HOURS. ROSE. STOOD.","0601 HOURS. STOOD SOME MORE.","0615 HOURS. ORDER: BUY MILK.","0640 HOURS. MILK NOT FOUND.","0641 HOURS. SEARCHING AISLES.","STATUS: EXCELLENT."],60,(30,34,22)),
 ("rear_admiral","parisienne",(24,40,84),(206,170,70),(246,240,224),"plain",
  "Ship's Log",
  ["Day 1 on dry land.","Set sail at dawn for the","post office. Returned with","one stamp. A fine haul.","The duck is unimpressed."],60,(22,32,70)),
 ("hanky","permanent-marker",(230,196,30),(60,60,60),(240,236,222),"lined",
  "SITE NOTES",
  ["Mon. Fixed it. Again.","Heavy tool ready by 7.","Boss says stop saying that.","Cups of tea: 6"],46,(50,50,56)),
 ("slick_willy","kaushan-script",(244,200,20),(255,255,255),(250,248,240),"lined",
  "My Brand Journal",
  ["Dear Diary,","14 views today. Up 3.","Quit job number 3.","It slid right off me.","Dream big. Sell bigger."],58,(36,36,44)),
 ("velvet_python","great-vibes",(78,34,92),(206,170,70),(248,240,230),"plain",
  "Dear Diary",
  ["Everyone was rushing again.","I strolled. A velvet pace.","Pressed one leaf.","Shoes still absent.","Yours, the Velvet Python"],60,(62,28,76)),
 ("the_grip","gloria-hallelujah",(24,42,92),(244,206,40),(244,240,230),"lined",
  "Dear Diary",
  ["Helped a man open a jar.","The jar is now in 3 pieces.","Bought him a new jar.","He was nice! Hugged my bear."],38,(30,36,70)),
]
for slug,font,cover,accent,paper,rule,title,lines,size,ink in chars:
    im=Image.new('RGB',(W,H),(244,236,220)); d=ImageDraw.Draw(im)
    # shadow
    sh=Image.new('L',(W,H),0); ImageDraw.Draw(sh).rounded_rectangle((90,110,W-70,H-50),30,fill=120)
    sh=sh.filter(ImageFilter.GaussianBlur(18)); im.paste((120,110,95),(0,0),sh); d=ImageDraw.Draw(im)
    d.rounded_rectangle((70,70,W-70,H-90),28,fill=cover)
    px0,py0,px1,py1=110,110,W-110,H-130
    cx=W//2
    d.rectangle((px0,py0,cx,py1),fill=paper); d.rectangle((cx,py0,px1,py1),fill=paper)
    # gutter shading
    g=Image.new('L',(W,H),0); gd=ImageDraw.Draw(g)
    for i in range(70):
        a=int(110*(1-i/70)**2); gd.line((cx-i,py0,cx-i,py1),fill=a); gd.line((cx+i,py0,cx+i,py1),fill=a)
    im.paste((90,80,60),(0,0),g); d=ImageDraw.Draw(im)
    # rules
    def ruling(x0,x1):
        if rule=="lined":
            y=py0+150+int(size*1.05)
            while y<py1-40: d.line((x0+50,y,x1-50,y),fill=(190,200,215),width=2); y+=size+14
        elif rule=="grid":
            for x in range(x0+50,x1-40,40): d.line((x,py0+140,x,py1-40),fill=(214,208,190),width=1)
            for y in range(py0+140,py1-40,40): d.line((x0+50,y,x1-50,y),fill=(214,208,190),width=1)
    ruling(px0,cx); ruling(cx,px1)
    # accent trim
    d.line((px0,py0,px1,py0),fill=accent,width=4)
    ft=ImageFont.truetype(F+font+".ttf",size+8)
    d.text((cx+60,py0+40),title,font=ft,fill=ink)
    f=ImageFont.truetype(F+font+".ttf",size)
    # wrap lines
    y=py0+150; x=cx+60; maxw=px1-cx-120
    for ln in lines:
        words=ln.split(); cur=""
        for w in words:
            t=(cur+" "+w).strip()
            if d.textlength(t,font=f)>maxw: d.text((x,y),cur,font=f,fill=ink); y+=size+14; cur=w
            else: cur=t
        d.text((x,y),cur,font=f,fill=ink); y+=size+14
    # left page: date
    fl=ImageFont.truetype(F+font+".ttf",size)
    d.text((px0+60,py0+40),"6 November 2026",font=fl,fill=ink)
    im.save(f"pages/diary_open_{slug}_v1.png")
sheet=Image.new('RGB',(3*640,2*440),'white')
for i,c in enumerate(chars):
    sheet.paste(Image.open(f"pages/diary_open_{c[0]}_v1.png").resize((640,440)),((i%3)*640,(i//3)*440))
sheet.save('pages_sheet.jpg',quality=88)
