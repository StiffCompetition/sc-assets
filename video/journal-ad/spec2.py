import sys; sys.argv=['x']
exec(open('specimen.py').read().split("opts=[")[0])
CAPS=[("DEAR\nSANTA,","SANTA,"),("I'D LIKE\nTO ENLIST","ENLIST"),("PLEASE SEND\nTHE SQUAD","SQUAD"),("AND MY OWN\nMISSIONS","MISSIONS"),("AND A\nCERTIFICATE.","CERTIFICATE.")]
def stick(im,text,key):
    f,sz=fit(text,'archivo-black/400Regular/ArchivoBlack_400Regular.ttf',780,120)
    n=len(text.split("\n")); pw,ph=W-150,int(sz*1.12*n)+70
    st=Image.new('RGBA',(pw+80,ph+80),(0,0,0,0)); d=ImageDraw.Draw(st)
    d.rounded_rectangle((40,52,40+pw,52+ph),30,fill=(0,0,0,120)); d.rounded_rectangle((40,40,40+pw,40+ph),30,fill=WHITE); d.rounded_rectangle((58,58,22+pw,22+ph),22,fill=RED)
    lines(d,text,key,f,sz,st.width//2,40+30,int(sz*1.12),WHITE,GOLD)
    st=st.rotate(-3,resample=Image.BICUBIC,expand=True); im=im.convert('RGBA'); im.alpha_composite(st,((W-st.width)//2,1246-st.height+20)); return im
def page(n,cx,up):
    cw=940; ch=cw*16//9; cy=min(3840-ch//2,1593+up); cx=max(cw//2,min(2160-cw//2,cx))
    return b.b9.imgs[n].crop((cx-cw//2,cy-ch//2,cx+cw//2,cy+ch//2)).resize((W,H),Image.LANCZOS)
shots=[('01-card',1560,0),('02-squad',1560,2),('05-day-tue',625,3),('08-certificate',1560,4)]
UP=430
sheet=Image.new('RGB',(4*540+50,960+60),(20,20,20)); sd=ImageDraw.Draw(sheet)
for i,(n,cx,c) in enumerate(shots):
    im=stick(page(n,cx,UP),*CAPS[c]); im.convert('RGB').save(f'spec2_{i}.png')
    sheet.paste(im.convert('RGB').resize((540,960),Image.LANCZOS),(10+i*550,50))
    sd.text((10+i*550,8),f'{n}',font=ImageFont.truetype('/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf',28),fill=(255,255,255))
sheet.save('sheet_E.png'); print('ok')
