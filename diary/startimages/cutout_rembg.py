import sys
from rembg import remove,new_session
from PIL import Image
s=new_session('isnet-general-use')
im=Image.open('MW_plain_2160.jpg').convert('RGB')
o=remove(im,session=s,alpha_matting=True,alpha_matting_foreground_threshold=240,alpha_matting_background_threshold=15,alpha_matting_erode_size=8)
o.save('MW_cut.png')
bg=Image.new('RGB',o.size,(255,0,255));bg.paste(o,mask=o.split()[3]);bg.resize((540,968)).save('MW_cut_view.jpg')
