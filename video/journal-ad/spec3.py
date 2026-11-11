exec(open('spec2.py').read().split("shots=[")[0])
def stick_at(im,text,key,top):
    f,sz=fit(text,'archivo-black/400Regular/ArchivoBlack_400Regular.ttf',780,120)
    n=len(text.split("\n")); pw,ph=W-150,int(sz*1.12*n)+70
    st=Image.new('RGBA',(pw+80,ph+80),(0,0,0,0)); d=ImageDraw.Draw(st)
    d.rounded_rectangle((40,52,40+pw,52+ph),30,fill=(0,0,0,120)); d.rounded_rectangle((40,40,40+pw,40+ph),30,fill=WHITE); d.rounded_rectangle((58,58,22+pw,22+ph),22,fill=RED)
    lines(d,text,key,f,sz,st.width//2,40+30,int(sz*1.12),WHITE,GOLD)
    st=st.rotate(-3,resample=Image.BICUBIC,expand=True); im=im.convert('RGBA'); im.alpha_composite(st,((W-st.width)//2,top)); return im
rows=[]
cols=[('01-card',1560,0),('02-squad',1560,2),('05-day-tue',625,3),('08-certificate',1560,4)]
sheet=Image.new('RGB',(4*540+50,2*960+120),(20,20,20)); sd=ImageDraw.Draw(sheet); lf=ImageFont.truetype('/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf',28)
for r,(lab,up,top) in enumerate([('1  Sticker at top, book below',-60,292),('2  Book filled up, sticker at bottom edge',230,1020)]):
    sd.text((10,8+r*1010),lab,font=lf,fill=(255,255,255))
    for i,(n,cx,c) in enumerate(cols):
        im=stick_at(page(n,cx,up),*CAPS[c],top=top)
        sheet.paste(im.convert('RGB').resize((540,960),Image.LANCZOS),(10+i*550,50+r*1010))
sheet.save('sheet_E2.png'); print('ok')
