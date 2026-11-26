"""Draw 1920x1080 color-block sketches for each shot + grayscale check + overview."""
from PIL import Image, ImageDraw, ImageFont, ImageOps
import os, numpy as np
W,H=1920,1080
OUT=os.path.join(os.path.dirname(__file__),'..','02_storyboard','sketches')
os.makedirs(OUT,exist_ok=True)
SKIN='#F0B184'; HAIR='#241914'; NAVY='#1F2E4A'; BLK='#19181D'; RED='#D7322B'
OLDW='#E6DFD1'; OLDB='#4A6FA5'; GAUZE='#F4F1EA'; CARD='#CDB48A'
try: FONT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',36)
except: FONT=ImageFont.load_default()

def person(d,cx,top,h,body,legs=BLK,skin=SKIN,hair=HAIR,shoes=None,mask=None):
    hr=h*0.09
    d.rectangle([cx-hr*1.1,top+hr*1.6,cx+hr*1.1,top+h*0.55],fill=body)          # torso
    d.rectangle([cx-hr*0.9,top+h*0.55,cx+hr*0.9,top+h*0.92],fill=legs)          # legs
    d.ellipse([cx-hr,top,cx+hr,top+hr*2],fill=skin)                              # head
    d.pieslice([cx-hr,top-hr*0.1,cx+hr,top+hr*1.6],180,360,fill=hair)            # hair
    if shoes: d.rectangle([cx-hr*1.1,top+h*0.92,cx+hr*1.1,top+h],fill=shoes)
    if mask is not None:
        mask.rectangle([cx-hr*1.1,top,cx+hr*1.1,top+h],fill=255)

def base(bg_top,bg_bot,split):
    im=Image.new('RGB',(W,H),bg_top); d=ImageDraw.Draw(im)
    d.rectangle([0,int(H*split),W,H],fill=bg_bot)
    m=Image.new('L',(W,H),0); return im,d,m,ImageDraw.Draw(m)

def guides(im,label):
    d=ImageDraw.Draw(im)
    for x in (int(W*.38),int(W*.62)):
        for y in range(0,H,24): d.line([x,y,x,y+12],fill='#FFFFFF',width=3)
    d.rectangle([0,0,W,56],fill='#000000'); d.text((16,8),label,fill='#FFFFFF',font=FONT)

shots={}
# S1 rainy night, low angle, girl at 62%, backlight
im,d,m,md=base('#2A2028','#4A3C32',0.62)
d.ellipse([820,60,1560,820],fill='#C27A40')                        # lit rain mist halo behind girl
d.ellipse([1050,80,1350,330],fill='#F2A24A')                       # streetlight glow behind
person(d,1190,300,620,'#14101A',legs='#14101A',skin='#5A3828',shoes='#2A2A30',mask=md)  # backlit silhouette
d.rectangle([1150,300,1230,920],outline='#F2A24A',width=6)          # rim light
for x in range(0,W,70): d.line([x,60,x-30,H*0.62],fill='#FFD08A',width=1)  # rain
for x in (1050,1300,1120): d.ellipse([x,900,x+90,950],fill='#FFD08A')       # splashes
shots['S1']=(im,m,'S1 0:00 rainy night | low angle MS-full | girl head 62% | falls forward ~1.2s')
# S2 bedroom
im,d,m,md=base('#5E4232','#4E3424',0.72)
d.rectangle([0,430,820,780],fill='#3A3550')                        # bed left
d.ellipse([480,420,640,560],fill=SKIN); md.ellipse([480,420,640,560],fill=255)   # sleeping face ~30%
d.rectangle([600,470,820,600],fill='#BDB6AE'); md.rectangle([600,470,820,600],fill=255)
d.rectangle([650,600,720,640],fill=GAUZE); d.rectangle([740,600,810,640],fill=GAUZE)
d.ellipse([160,40,420,300],fill='#F5B65E')                         # lamp glow
person(d,1190,420,560,CARD,legs='#5A4A3A',mask=md)                  # mom crouch at 62%
d.rectangle([1080,700,1160,760],fill=RED); d.rectangle([1230,700,1310,760],fill=RED); d.rectangle([1080,750,1160,762],fill='#F4F1EA'); d.rectangle([1230,750,1310,762],fill='#F4F1EA')
d.rectangle([700,880,840,960],fill=OLDW); d.rectangle([860,880,1000,960],fill=OLDW)
d.ellipse([965,895,995,925],fill='#2A1D18')                        # hole right shoe
d.rectangle([1030,880,1310,960],outline='#F5B65E',width=3)          # landing space
shots['S2']=(im,m,'S2 0:05 bedroom | floor-level side MS | mom head 62% | new shoes -> right of old')
# S3 winter dawn fog tracking
im,d,m,md=base('#E6C49B','#D2B48C',0.74)
d.ellipse([1500,60,1800,360],fill='#FFE3A8')
for x in range(80,W,260): d.rectangle([x,560,x+14,800],fill='#8A6A55')   # fence posts
d.rectangle([0,640,W,652],fill='#8A6A55')
person(d,730,380,560,NAVY,shoes=RED,mask=md); d.rectangle([730-56,380+560-8,730+56,380+560],fill='#F4F1EA')
d.ellipse([800,430,900,480],fill='#FFFFFF')                         # breath
d.text((1400,980),'<< background flows left',fill='#000000',font=FONT)
shots['S3']=(im,m,'S3 0:11 winter dawn | side tracking LS | girl head 38% | jog left->right')
# S4 top-down face
im,d,m,md=base('#3E4820','#3E4820',1.0)
for x in range(0,W,40): d.line([x,0,x+15,H],fill='#3B3A1E',width=2)
d.ellipse([1000,250,1380,700],fill='#F7C49A'); md.ellipse([1000,250,1380,700],fill=255)
d.ellipse([1030,80,1350,330],fill=HAIR)                             # hair spread above head
d.ellipse([1110,420,1160,450],fill=HAIR); d.ellipse([1220,420,1270,450],fill=HAIR)
d.polygon([(1380,300),(1920,180),(1920,700),(1380,640)],fill='#5A5A26')   # long warm light from right, no sun
d.polygon([(400,280),(1000,330),(1000,620),(400,680)],fill='#2A3014')       # long shadow to left
d.rectangle([1000,700,1380,H],fill=NAVY); md.rectangle([1000,700,1380,H],fill=255)
shots['S4']=(im,m,'S4 0:16 sunset grass | top-down CU | eyes at 62% | eyes open ~0:18.67')
# S5 finish
im,d,m,md=base('#F3D28C','#D2B48C',0.55)
person(d,1500,420,300,'#8C6A5A',legs='#8C6A5A');person(d,1650,440,280,'#9C7A6A',legs='#9C7A6A')
person(d,730,300,520,NAVY,shoes=RED,mask=md); d.rectangle([730-52,300+520-8,730+52,300+520],fill='#F4F1EA')
d.rectangle([700,420,760,470],fill='#FFFFFF')                       # plain bib
d.line([0,560,W,520],fill='#FFFFFF',width=8)                        # tape far
shots['S5']=(im,m,'S5 0:21 finish | low tele 30deg, slow-mo LS | girl head 38% | tape break 0:24.00')
# S6 stands
im,d,m,md=base('#9C6A44','#A87850',0.7)
for x in (300,900,1600): person(d,x,200,260,'#C89A6A',legs='#C89A6A')  # far blurred crowd
person(d,730,180,1100,CARD,mask=md)
d.rectangle([600,560,860,700],fill=OLDW); d.ellipse([800,600,840,640],fill='#2A1D18')
person(d,1340,430,800,'#4F6B3F',hair='#B9B4AC',mask=md)
shots['S6']=(im,m,'S6 0:26 stands | eye-level front MCU | mom head 38%, aunt ~70%')

rows=[]
for k,(im,m,label) in shots.items():
    gray=ImageOps.grayscale(im); a=np.asarray(gray,float); mk=np.asarray(m)>0
    import cv2
    ring=cv2.dilate(np.asarray(m),np.ones((151,151),np.uint8))>0   # local surround (~75px) of the subject
    fg,bg=a[mk].mean(),a[ring&~mk].mean()
    rows.append((k,fg,bg,abs(fg-bg)))
    guides(im,label); im.save(f'{OUT}/{k}_color.png')
    g=gray.convert('RGB'); guides(g,f'{k} grayscale | fg {fg:.0f} vs bg {bg:.0f}'); g.save(f'{OUT}/{k}_gray.png')
def sheet(suffix,name):
    s=Image.new('RGB',(960*3,540*2))
    for i,k in enumerate(shots): s.paste(Image.open(f'{OUT}/{k}_{suffix}.png').resize((960,540)),((i%3)*960,(i//3)*540))
    s.save(f'{OUT}/../{name}')
sheet('color','overview_color.png'); sheet('gray','overview_gray.png')
def lum(h): h=h.lstrip('#'); r,g,b=[int(h[i:i+2],16) for i in (0,2,4)]; return .299*r+.587*g+.114*b
print('red shoe %.0f vs dry track %.0f / S2 floor %.0f'%(lum(RED),lum('#D2B48C'),lum('#4E3424')))
for r in rows: print('%s  fg=%.0f bg=%.0f diff=%.0f %s'%(*r,'OK' if r[3]>=40 else 'LOW'))
