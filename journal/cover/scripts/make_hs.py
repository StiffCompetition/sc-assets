# head close-ups from the 05 Head and Shoulders references, on pop-art dot backgrounds
from PIL import Image, ImageDraw
src=open('scripts/prep_panels.py').read(); exec(src[src.index('def popbg'):src.index('FACES=')])
C={'TG':((0,174,224),(0.18,0,0.82,0.59)),'MW':((0,174,224),(0.12,0,0.88,0.70)),'HH':((0,174,224),(0.22,0,0.78,0.52)),
   'RA':((255,214,0),(0.10,0,0.90,0.74)),'SW':((0,174,224),(0.16,0,0.84,0.63))}
sh=Image.new('RGB',(5*300,280),'white')
for i,(k,(c,fr)) in enumerate(C.items()):
    f=f'refs/{k}_hs_src.png' if k in('TG','MW') else f'refs/{k}_hs.png'
    im=Image.open(f).convert('RGBA'); im=im.crop(im.getchannel('A').getbbox()); w,h=im.size
    im=im.crop((int(w*fr[0]),int(h*fr[1]),int(w*fr[2]),int(h*fr[3]))); im=im.resize((1040,int(im.height*1040/im.width)),Image.LANCZOS)
    bg=popbg(im.size,c); bg.paste(im,(0,0),im); bg.save(f'refs/up_{k}_hs.png')
    t=bg.copy(); t.thumbnail((300,280)); sh.paste(t,(i*300,0))
sh.save('cover/_hs.png')
# wide versions for the shorter back-cover cells (whole head fits, chin included)
W={'MW':((255,214,0),(0.08,0.0,0.92,0.60)),'RA':((255,214,0),(0.0,0.04,1.0,0.70)),'SW':((0,174,224),(0.0,0.0,1.0,0.64))}
for k,(c,fr) in W.items():
    im=Image.open(f'refs/{k}_hs_src.png' if k=='MW' else f'refs/{k}_hs.png').convert('RGBA'); im=im.crop(im.getchannel('A').getbbox()); w,h=im.size
    im=im.crop((int(w*fr[0]),int(h*fr[1]),int(w*fr[2]),int(h*fr[3]))); im=im.resize((1400,int(im.height*1400/im.width)),Image.LANCZOS)
    bg=popbg(im.size,c); bg.paste(im,(0,0),im); bg.save(f'refs/up_{k}_hsw.png')
# whole-head versions for the wide back-cover cells: top of hat/head to just under the chin, centred on dots
HEAD={'RA':((255,214,0),0.02,0.79),'MW':((255,214,0),0.07,0.74),'SW':((0,174,224),0.0,0.72)}
for k,(c,y0,y1) in HEAD.items():
    im=Image.open(f'refs/{k}_hs_src.png' if k=='MW' else f'refs/{k}_hs.png').convert('RGBA'); im=im.crop(im.getchannel('A').getbbox()); w,h=im.size
    im=im.crop((0,int(h*y0),w,int(h*y1))); H=im.height; Wc=int(H*1.95)
    bg=popbg((Wc,H),c); bg.paste(im,((Wc-w)//2,0),im); bg=bg.resize((1600,int(1600*H/Wc)),Image.LANCZOS); bg.save(f'refs/up_{k}_hsw.png')
