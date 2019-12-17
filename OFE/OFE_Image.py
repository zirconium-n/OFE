#OFE_Image
from PIL import Image
import sys, os
from OFE import Panel_Int, Panel_Name

import time

#根目录
path0 = os.path.dirname(__file__)

##初始加载图片
# 图片映射表



Panel_Dict = {}
for i, id in enumerate(Panel_Int):
	Panel_Dict[id] = Panel_Name[i]

Arrow_Name = ['Left', 'Up', 'Right', 'Down']
		

class OFE_Image():
	def __init__(self, field, Graphics = None, Img_parameter = None):
		self.field = field
		self.Graphics = Graphics
		self.Img_parameter = Img_parameter
		
	def PX_Image(self):
	
		#按照list[y][x]制作新Img
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
		
		#颜色列表
		COLOR = {}
		COLOR['Neutral'] = (214,214,214,256)
		COLOR['Encounter'] = (255,115,109,256)
		COLOR['Encounter_2'] = (255,115,109,256)
		COLOR['Draw'] =(104,255,138,256)
		COLOR['Draw_2'] = (0,246,88,256)
		COLOR['Bonus'] = (254,222,110,256)
		COLOR['Bonus_2'] = (253,186,31,256)
		COLOR['Drop'] = (109,164,255,256)
		COLOR['Drop_2'] = (0,96,246,256)
		COLOR['Warp'] = (198,61,255,256)
		COLOR['WarpMove'] = (198,61,255,256)
		COLOR['WarpMove_2'] = (198,61,255,256)
		COLOR['Move'] = (73,206,180,256)
		COLOR['Move_2'] = (73,206,180,256)
		COLOR['PLAYER1'] = (254,198,149,256)
		COLOR['PLAYER2'] = (187,223,255,256)
		COLOR['PLAYER3'] = (181,255,178,256)
		COLOR['PLAYER4'] = (254,242,156,256)
		
		px = 2
		
		DATA = []
		size = self.field.size()
		#预填充
		for y in range(px*size[1]):
			DATA.append([])
			for x in range(px*size[0]):
				DATA[y].append((0,0,0,0))
		
		#填充
		for y in range(size[1]):
			for x in range(size[0]):
				panel_id = self.field.data[y][x][0]
				panel_name = Panel_Name[Panel_Int.index(panel_id)]
				if panel_name in COLOR:
					for j in range(px):
						for i in range(px):
							DATA[y*px+j][x*px+i] = COLOR[panel_name]
				elif panel_name == 'Check':
					DATA[y*px+0][x*px+0] = COLOR['PLAYER1']
					DATA[y*px+1][x*px+0] = COLOR['PLAYER2']
					DATA[y*px+0][x*px+1] = COLOR['PLAYER3']
					DATA[y*px+1][x*px+1] = COLOR['PLAYER4']
					
		img = New_Px(DATA)
		return img
		
	def Main(self):
		
		Img = self.Panels()
		if self.Img_parameter['Show_arrows'] == 1:
			Arrow = self.Arrows()
			Img.paste(Arrow,(0,0),Arrow.split()[3])
		return Img
		
	def Point(self, Img, pos):
	
		zoom = self.Img_parameter['Zoom']
		
		PX = 128
		px = int(PX * zoom)
		
		size = self.field.size()
		size_img = map(lambda x: x * px, size)
		
		x = pos[0]
		y = pos[1]
		
		#画单个格子
		Img_this = Image.new("RGBA", (px, px), self.Img_parameter['Background'])
		panel_id = self.field.data[y][x][0]
		if panel_id:
			Img_Panel = self.Graphics.get_image('Panel_' + Panel_Dict[panel_id], zoom)
			Img_this.paste(Img_Panel, (0,0), Img_Panel.split()[3])
		
		if self.Img_parameter['Show_arrows'] == 1:
			#需要画的箭头
			#是否反向
			backtrack = self.Img_parameter['BackTrack']
			if backtrack:
				CONST = 16
			else:
				CONST = 1
			
			Arrows = []
			for i in range(4):
				if int(self.field.data[y][x][1] / (2**i) / CONST) % 2:
					Arrows.append(i)
					
			for arrow_num in Arrows:
				Img_Arrow = self.Graphics.get_image('Arrow_' + Arrow_Name[arrow_num], zoom)
				Img_this.paste(Img_Arrow, (0,0) ,Img_Arrow.split()[3])
				
		Img.paste(Img_this, (px*x,px*y))
		return Img
		
		
	def Panels(self):
		
		zoom = self.Img_parameter['Zoom']
		
		PX = 128
		px = int(PX * zoom)
		
		size = self.field.size()
		size_img = map(lambda x: x * px, size)
		
		#作图
		Img = Image.new("RGBA", tuple(size_img), (0,0,0,0))
		for y in range(size[1]):
			for x in range(size[0]):
				panel_id = self.field.data[y][x][0]
				if panel_id != 0 :
					Img_Panel = self.Graphics.get_image('Panel_' + Panel_Dict[panel_id], zoom)
					Img.paste(Img_Panel,(px*x,px*y),Img_Panel.split()[3])
		return Img
		
	def Arrows(self):
		
		zoom = self.Img_parameter['Zoom']
		
		PX = 128
		px = int(PX * zoom)
		
		size = self.field.size()
		size_img = map(lambda x: x * px, size)
		
		#作图
		Img = Image.new("RGBA", tuple(size_img), (0,0,0,0))
		
		#偏移关系
		# shift = 18
		# x_shift = [-shift, 0, shift, 0]
		# y_shift = [0, -shift, 0, shift]
		
		#是否反向
		backtrack = self.Img_parameter['BackTrack']
		
		if backtrack:
			CONST = 16
		else:
			CONST = 1
		
		for y in range(size[1]):
			for x in range(size[0]):
				#需要画的箭头
				Arrows = []
				for i in range(4):
					if int(self.field.data[y][x][1] / (2**i) / CONST) % 2:
						Arrows.append(i)
						
				for arrow_num in Arrows:
					Img_Arrow = self.Graphics.get_image('Arrow_' + Arrow_Name[arrow_num], zoom)
					Img.paste(Img_Arrow,(px*x,px*y),Img_Arrow.split()[3])
		
		return Img
		
		
		
		
		
		
		
