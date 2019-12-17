#OFE_图片素材辅助

import sys, os
from PIL import Image

#根目录
path0 = os.path.dirname(os.path.realpath(sys.argv[0]))

def New_Px(DATA):
	
	type = "RGBA"
	if len(DATA[0][0]) == 3:
		type = "RGB"
		
	Y = len(DATA)
	X = len(DATA[0])
	
	Img = Image.new("RGBA", (X,Y),(0,0,0,0))
	
	PUT_DATA = []
	
	for raw in DATA:
		PUT_DATA += raw
		
	Img.putdata(PUT_DATA)
	
	return Img

#生成按钮样例
def To_Button(img_o, type_ = 0):
	
	#新图尺寸（默认旧图为128大小）
	PX = 128
	Size = 132
	
	#颜色
	Black = (0,0,0,256)
	Gray1 = (100,100,100,256)
	Gray2 = (150,150,150,256)
	
	#补正
	FIX_W = 6
	FIX_H = -4
	
	#制图
	if type_ == 0:
		Data = []
		for y in range(Size):
			Data.append([])
			for x in range(Size):
				if (x >= PX + FIX_H or y >= PX + FIX_H) and abs(x-y) < PX + FIX_W:
					Data[y].append(Black)
				else:
					Data[y].append((0,0,0,0))
					
		Img = New_Px(Data)
		Img.paste(img_o, (0,0), img_o.split()[3])
		
	elif type_ == 1:
		Data = []
		for y in range(Size):
			Data.append([])
			for x in range(Size):
				if (x <= Size - PX - FIX_H or y <= Size - PX - FIX_H) and abs(x-y) < PX + FIX_W:
					Data[y].append(Gray2)
				else:
					Data[y].append((0,0,0,0))
					
		Img = New_Px(Data)
		Img.paste(img_o, (Size - PX, Size - PX), img_o.split()[3])
		
	return Img
		
img_o = Image.open(path0 + r'\Panel_Bonus.png')
Img = To_Button(img_o)
Img.save(path0 + r'\testbutton1.png', 'PNG')
Img.show()
	
	