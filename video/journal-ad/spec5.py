exec(open('spec3.py').read().split("rows=[]")[0])
print(list(b.b9.imgs.keys()))
def face3(i,top=170):
    im=b.faces[i]; w=900; h=int(im.height*w/im.width)
    p=im.resize((w,h),Image.LANCZOS); B=16
    pan=Image.new('RGBA',(w+2*B,h+2*B),(255,255,255,255)); pan.paste(p,(B,B))
    lay=Image.new('RGBA',(pan.width+160,pan.height+160),(0,0,0,0))
    sh=Image.new('RGBA',lay.size,(0,0,0,0)); ImageDraw.Draw(sh).rectangle((80,100,80+pan.width,100+pan.height),fill=(0,0,0,170))
    lay.alpha_composite(sh.filter(ImageFilter.GaussianBlur(20))); lay.alpha_composite(pan,(80,80))
    lay=lay.rotate(2.5 if i%2==0 else -2.5,resample=Image.BICUBIC,expand=True)
    fr=b.RAYS.copy().convert('RGBA'); fr.alpha_composite(lay,((W-lay.width)//2,top)); return fr,h
def cover3():
    full=b.cover(b.desk,940,800,0.0); s=0.80
    bgi=full.crop((0,0,36,H)).resize((W,H),Image.BICUBIC).filter(ImageFilter.GaussianBlur(24))
    fw,fh=int(W*s),int(H*s); fg=full.resize((fw,fh),Image.LANCZOS)
    m=Image.new('L',(fw,fh),0); ImageDraw.Draw(m).rectangle((34,34,fw-34,fh-34),fill=255); m=m.filter(ImageFilter.GaussianBlur(18))
    bgi.paste(fg,((W-fw)//2,60),m); return bgi.convert('RGBA')
beats=[('cover',cover3(),"DEAR\nSANTA,","SANTA,"),
('card',page('01-card',1560,230),"I'D LIKE\nTO ENLIST","ENLIST"),
('squad',page('02-squad',1560,230),"SIX FILES.\nONE IS YOU.","ONE IS YOU."),
('grip',face3(5)[0],"THE GRIP CRIES\nAT ANIMAL VIDEOS","AT ANIMAL VIDEOS"),
('admiral',face3(3)[0],"FIRST MATE:\nA RUBBER DUCK","A RUBBER DUCK"),
('missions',page('03-map',1560,230) if '03-map' in b.b9.imgs else page('05-day-tue',625,230),"12 MISSIONS.\nBRIEF. DEBRIEF.","BRIEF. DEBRIEF."),
('cert',page('08-certificate',1560,230),"SIGN HERE.\nSTAND TALL.","STAND TALL.")]
sheet=Image.new('RGB',(4*540+50,2*960+120),(20,20,20)); sd=ImageDraw.Draw(sheet)
for i,(n,im,t,k) in enumerate(beats):
    o=stick_at(im,t,k,top=1020).convert('RGB'); o.save(f'spec5_{i}.png')
    sheet.paste(o.resize((540,960),Image.LANCZOS),(10+(i%4)*550,10+(i//4)*990))
sheet.save('sheet_E4.png'); print('ok')
