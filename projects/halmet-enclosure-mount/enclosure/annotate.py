import sys
from PIL import Image, ImageDraw, ImageFont
im=Image.open(sys.argv[1]).convert('RGB'); d=ImageDraw.Draw(im)
try: f=ImageFont.truetype("DejaVuSans-Bold.ttf",22); fs=ImageFont.truetype("DejaVuSans.ttf",18)
except: f=fs=ImageFont.load_default()
# pixel centres read off 3x zoom crops
posts=[(455.7,235),(1012.7,235),(458.3,716.7),(1012.7,716.7)]
holed=[(248.3,322.7),(246.7,629),(1226.7,319.3)]
G=(0,170,60); O=(230,110,0)
for x,y in posts:
    d.ellipse([x-30,y-30,x+30,y+30],outline=G,width=5)
for x,y in [(248,323),(247,476),(247,629),(1227,319),(1227,472),(1227,625)]:
    d.ellipse([x-26,y-26,x+26,y+26],outline=O,width=3)
# dims
d.line([(456,180),(1013,180)],fill=G,width=3); d.text((620,150),"posts: 557 px",fill=G,font=f)
d.line([(1060,235),(1060,717)],fill=G,width=3); d.text((1070,460),"482 px",fill=G,font=f)
d.line([(248,850),(1227,850)],fill=O,width=3); d.text((560,858),"screw bosses: 978 px",fill=O,font=f)
d.text((470,262),"no-hole post",fill=G,font=fs); d.text((262,360),"screw boss",fill=O,font=fs)
im.save(sys.argv[2])
span=978.4; px=557.0; py=481.7; pitch=153.2; floor=1053
for name,k in [("boss span = 136 (owner)",136/span),("floor = 151 (owner)",151/floor)]:
    print(f"{name}: k={k:.4f} mm/px  posts {px*k:.1f} x {py*k:.1f}  boss span {span*k:.1f}  pitch {pitch*k:.1f}  post dia {35.7*k:.1f}")
print("ratios: post_x/boss_span", round(px/span,3), " post_y/post_x", round(py/px,3))
