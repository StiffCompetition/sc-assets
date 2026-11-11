import math
from PIL import Image, ImageDraw
S=400
def new(): 
    im=Image.new('RGBA',(S,S),(0,0,0,0)); return im,ImageDraw.Draw(im)
def heart():
    im,d=new(); c=(205,25,70)
    d.ellipse([40,50,210,220],fill=c); d.ellipse([190,50,360,220],fill=c)
    d.polygon([(48,160),(352,160),(200,350)],fill=c); d.polygon([(70,190),(330,190),(200,345)],fill=c)
    d.ellipse([85,85,135,120],fill=(255,150,170)); return im
def shamrock():
    im,d=new(); g=(14,140,70); dk=(8,100,50)
    for ang in (0,90,-90):
        t=Image.new('RGBA',(S,S),(0,0,0,0)); dd=ImageDraw.Draw(t)
        dd.ellipse([105,30,205,135],fill=g); dd.ellipse([195,30,295,135],fill=g)
        dd.polygon([(110,100),(290,100),(200,235)],fill=g)
        dd.line([(200,225),(200,70)],fill=(40,170,95),width=6)
        t=t.rotate(ang,center=(200,230)); im.alpha_composite(t)
    d=ImageDraw.Draw(im)
    d.line([(200,230),(215,300),(250,370)],fill=dk,width=22,joint='curve')
    return im
def champagne():
    im,d=new(); gl=(240,200,60); rim=(190,150,30)
    for cx,ang in ((125,-16),(275,16)):
        t=Image.new('RGBA',(S,S),(0,0,0,0)); dd=ImageDraw.Draw(t)
        dd.polygon([(cx-48,60),(cx+48,60),(cx+30,200),(cx-30,200)],fill=gl)
        dd.polygon([(cx-48,60),(cx+48,60),(cx+42,105),(cx-42,105)],fill=(250,225,120))
        dd.rectangle([cx-6,200,cx+6,320],fill=rim); dd.ellipse([cx-48,314,cx+48,342],fill=rim)
        t=t.rotate(ang,center=(cx,330)); im.alpha_composite(t)
    d=ImageDraw.Draw(im)
    for x,y,r in ((200,48,15),(175,22,9),(230,26,10),(205,95,7)): d.ellipse([x-r,y-r,x+r,y+r],fill=(255,240,180))
    return im
def globe():
    im,d=new()
    d.ellipse([45,45,355,355],fill=(40,120,200)); 
    g=(60,170,90)
    d.polygon([(110,120),(190,100),(215,150),(170,200),(185,260),(140,270),(100,200)],fill=g)
    d.polygon([(250,150),(310,170),(320,230),(270,300),(240,240),(260,200)],fill=g)
    d.ellipse([45,45,355,355],outline=(20,70,140),width=10)
    d.ellipse([120,80,170,115],fill=(120,190,235)); return im
def tulip():
    im,d=new(); r=(215,35,90)
    d.line([(200,200),(200,370)],fill=(40,140,60),width=18)
    d.polygon([(200,330),(110,230),(140,310)],fill=(50,160,70)); d.polygon([(200,340),(290,250),(262,330)],fill=(50,160,70))
    d.ellipse([105,60,295,285],fill=r)
    d.polygon([(105,150),(135,40),(175,120),(200,30),(225,120),(265,40),(295,150),(200,150)],fill=r)
    d.polygon([(175,120),(200,30),(225,120),(200,200)],fill=(240,90,130)); return im
def sun():
    im,d=new(); c=(250,175,20)
    for i in range(12):
        a=math.radians(i*30); 
        d.polygon([(200+math.cos(a-0.12)*120,200+math.sin(a-0.12)*120),(200+math.cos(a)*185,200+math.sin(a)*185),(200+math.cos(a+0.12)*120,200+math.sin(a+0.12)*120)],fill=c)
    d.ellipse([90,90,310,310],fill=(255,200,40)); d.ellipse([125,115,190,165],fill=(255,230,130)); return im
def fireworks():
    im,d=new()
    cols=[(220,40,50),(40,90,210),(250,190,20)]
    for (cx,cy,col,n) in ((140,150,cols[0],12),(280,230,cols[1],12),(250,90,cols[2],10)):
        for i in range(n):
            a=2*math.pi*i/n; x1,y1=cx+math.cos(a)*25,cy+math.sin(a)*25; x2,y2=cx+math.cos(a)*85,cy+math.sin(a)*85
            d.line([(x1,y1),(x2,y2)],fill=col,width=14); d.ellipse([x2-12,y2-12,x2+12,y2+12],fill=col)
        d.ellipse([cx-16,cy-16,cx+16,cy+16],fill=(255,245,200))
    return im
def beer():
    im,d=new()
    d.rounded_rectangle([90,110,290,350],radius=18,fill=(245,180,30))
    for x in (130,185,240): d.rectangle([x,140,x+22,325],fill=(255,205,70))
    d.rounded_rectangle([282,160,360,300],radius=30,outline=(200,200,210),width=20)
    d.rounded_rectangle([90,110,290,350],radius=18,outline=(215,225,235),width=12)
    for x,y,r in ((120,95,38),(180,70,48),(245,90,40),(290,100,28)): d.ellipse([x-r,y-r,x+r,y+r],fill=(255,255,255))
    return im
def leaf():
    im,d=new(); c=(215,95,15)
    d.polygon([(200,35),(250,95),(320,85),(295,160),(350,200),(285,235),(305,300),(235,285),(200,340),(165,285),(95,300),(115,235),(50,200),(105,160),(80,85),(150,95)],fill=c)
    d.line([(200,70),(200,385)],fill=(120,50,10),width=14)
    for y,dx in ((140,60),(190,80),(240,60)): 
        d.line([(200,y+30),(200-dx,y)],fill=(120,50,10),width=8); d.line([(200,y+30),(200+dx,y)],fill=(120,50,10),width=8)
    return im
def pumpkin():
    im,d=new(); o=(240,120,15); dk=(205,90,10)
    d.ellipse([30,110,200,350],fill=dk); d.ellipse([200,110,370,350],fill=dk); d.ellipse([85,95,315,360],fill=o); d.ellipse([140,100,260,360],fill=(255,140,30))
    d.polygon([(185,115),(215,115),(235,60),(200,50)],fill=(70,120,40))
    k=(60,25,5)
    d.polygon([(125,190),(175,190),(150,235)],fill=k); d.polygon([(225,190),(275,190),(250,235)],fill=k)
    d.polygon([(130,275),(160,300),(200,285),(240,300),(270,275),(250,325),(200,335),(150,325)],fill=k)
    return im
def turkey():
    im,d=new()
    cols=[(200,50,40),(240,130,20),(250,190,30),(60,150,70),(40,110,190)]
    for i,c in enumerate(cols):
        a=math.radians(-160+i*35); 
        d.pieslice([30,10,370,350],-180+i*36,-180+(i+1)*36,fill=c)
    d.ellipse([110,170,290,350],fill=(130,75,35))
    d.ellipse([215,120,315,220],fill=(130,75,35))
    d.ellipse([270,150,282,162],fill=(255,255,255)); d.ellipse([274,153,280,159],fill=(0,0,0))
    d.polygon([(310,165),(345,180),(310,195)],fill=(250,190,30)); d.ellipse([290,190,318,235],fill=(210,30,40))
    d.line([(170,350),(165,385)],fill=(240,170,40),width=12); d.line([(230,350),(235,385)],fill=(240,170,40),width=12)
    return im
def tree():
    im,d=new(); g=(25,130,60)
    d.rectangle([180,300,220,365],fill=(110,65,30))
    for top,hw,bot in ((40,80,140),(100,115,215),(160,150,310)):
        d.polygon([(200,top),(200-hw,bot),(200+hw,bot)],fill=g)
    d.polygon([(200,15),(212,42),(240,46),(218,64),(225,92),(200,76),(175,92),(182,64),(160,46),(188,42)],fill=(250,200,30))
    for x,y,c in ((165,150,(220,40,50)),(235,180,(250,200,30)),(150,250,(60,100,220)),(215,250,(220,40,50)),(255,285,(250,200,30)),(130,290,(250,200,30))): d.ellipse([x-14,y-14,x+14,y+14],fill=c)
    return im
ICONS={1:champagne,2:heart,3:shamrock,4:globe,5:tulip,6:sun,7:fireworks,8:beer,9:leaf,10:pumpkin,11:turkey,12:tree}
DATES={1:1,2:14,3:17,4:22,5:9,6:21,7:4,8:6,9:23,10:31,11:25,12:25}
if __name__=='__main__':
    sh=Image.new('RGBA',(4*210,3*210),(255,255,255,255))
    for m in range(1,13):
        ic=ICONS[m]().resize((200,200),Image.LANCZOS); sh.alpha_composite(ic,(((m-1)%4)*210+5,((m-1)//4)*210+5))
    sh.convert('RGB').save('/tmp/pg/icons.jpg',quality=92)
