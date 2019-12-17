#OFE_Canvas
import sys, os
import copy
from PyQt5 import QtGui, QtWidgets, QtCore
from PIL import Image
from PIL.ImageQt import ImageQt

from OFE.OFE_Field import OFE_Field
from OFE.OFE_Image import OFE_Image
from OFE import Panel_Int, Panel_Name, Button_Brush_Int
#根目录
path0 = os.path.dirname(__file__)


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
#图片格式转换
def PIXMAP(img):
	ImgQt = ImageQt(img)
	pixmap = QtGui.QPixmap.fromImage(ImgQt)
	return pixmap
	
#Zoom List
Zoom_List = [0.5]
	
	
#画板本体
class Canvas(QtWidgets.QLabel):
	def __init__(self, field, PARAMETER, statue, App = None, file_name = 'Title', file_path = '', parent = None):
		super(Canvas,self).__init__(parent)
		self.init(field, PARAMETER, statue, App, file_name, file_path)
		
	def init(self, field, PARAMETER, statue, App = None, file_name = 'Title', file_path = ''):
		
		#初始化
		self.setMouseTracking(True)
		self.file_name = file_name
		self.file_path = file_path

		
		#从PARAMETER中提取
		self.Graphics = PARAMETER['Graphics']
		self.file = {'Field':field, 'History':[], 'Pos':1, 'Change':0}
		self.Selected = {'Type': 'None', 'Pos_Start':(0,0), 'Pos_End':(0,0), 'Copy_Index': 0, 
				'Trans_Field': None, 'Trans_Pos': (0,0), 'Trans_Img': None, 'Trans_Dis': (0,0), 'Duplicate_Index': 0}
		if self.Is_Field():
			self.file['History'].append(copy.deepcopy(field))
			self.file['Pos'] = 1
		self.PARAMETER = PARAMETER
		self.statue = statue
		self.App = App
		
		#初始化
		self.Field_Img = None
		self.Paint_Command = {'All':None}
		self.Save_Index = 0
		
		#鼠标格子位置
		self.X = 0
		self.Y = 0
		self.X_old = 0
		self.Y_old = 0
		
		#初始画定大小
		self.Img_Draw({'All':None})
	
	#是否是地图文件
	def Is_Field(self):
		if self.file['Field'].data:
			return True
		else:
			False
			
	#返回本地图
	def Field(self):
		return self.file['Field']
	
	##鼠标
	#设置移动上下限
	def Set_XY(self, pos):
		Min = 0
		Size = self.file['Field'].size()
		MaxX = Size[0] - 1
		MaxY = Size[1] - 1
		
		return max(0, min(pos[0], MaxX)), max(0, min(pos[1], MaxY))
		
		
		
	#返回是否在格点上发生移动
	def Is_Move(self):
		if self.X != self.X_old or self.Y != self.Y_old:
			return True
		else:
			return False
			
	#位置作差
	def Pos_Minus(self, pos1, pos2):
		posnew = (pos1[0]-pos2[0], pos1[1]-pos2[1])
		return posnew
		
	#位置作和
	def Pos_Add(self, pos1, pos2):
		posnew = (pos1[0]+pos2[0], pos1[1]+pos2[1])
		return posnew
			
	#返回是否处在Transform区域中以及偏差距离
	def Distance(self):
		x1 = self.Selected['Trans_Pos'][0]
		y1 = self.Selected['Trans_Pos'][1]
		
		size_area = self.Selected['Trans_Field'].size()
		
		x2 = x1 + size_area[0]
		y2 = y1 + size_area[1]
		
		if self.X in range(x1, x2) and self.Y in range(y1, y2):
			x_dis = self.X - x1
			y_dis = self.Y - y1
			return (x_dis, y_dis)
		else:
			return None
			
	
	
	#鼠标点击
	def mousePressEvent(self, event):
		panel_count = len(Panel_Int)
		button_count = 6
		transform_count = 6

		command = {}
		if self.file['Field'].data:
			#鼠标位置
			pos = event.pos()
			x = pos.x()
			y = pos.y()
			
			PX = 128
			zoom = self.PARAMETER['Img_parameter']['Zoom']
			px = int(PX * zoom)
			
			self.X, self.Y = self.Set_XY((int(x / px), int(y / px)))
			POS = (self.X, self.Y)
		
		if event.button() == QtCore.Qt.RightButton:
			#右键按下指令
			print(event.pos())
			if self.file['Field'].data:
				Button_id = self.PARAMETER['Command']['Button']
				#Brush删除模式
				if Button_id >= 0 and Button_id < panel_count:
					panel_id = 0
					ischange = self.Point_Panel(panel_id)
					if ischange:
						command['Point'] = POS
						
				#删除箭头
				if Button_id >= panel_count + 1 and Button_id <= panel_count + 3:
					ischange = self.Point_Arrow(arrow_command = [-1,-1,-1,-1])
					if ischange:
						command['Point'] = POS
			
		elif event.button() == QtCore.Qt.LeftButton:
			#左键按下指令
			if self.file['Field'].data:
				Button_id = self.PARAMETER['Command']['Button']
				#Brush模式
				if Button_id >= 0 and Button_id < panel_count:
					B_command = self.PARAMETER['Command']['Button']
					panel_id = Button_Brush_Int[B_command]
					ischange = self.Point_Panel(panel_id)
					if ischange:
						command['Point'] = POS
						
				#删除箭头
				if Button_id == panel_count + 1 :
					ischange = self.Point_Arrow(arrow_command = [-1,-1,-1,-1])
					if ischange:
						command['Point'] = POS
						
				#选择模式
				if Button_id == panel_count:
					if self.Selected['Type'] == 'None' or self.Selected['Type'] == 'Selected':
						#取消Copy IndexError
						self.Selected['Copy_Index'] = 0
						self.Selected['Type'] = 'Selecting'
						self.Selected['Pos_Start'] = POS
						self.Selected['Pos_End'] = POS
						command['Cursor'] = None
						
				#变换模式
				if Button_id == panel_count:
					if self.Selected['Type'] == 'Transform':
						dis = self.Distance()
						if dis:
							self.Selected['Type'] = 'Transforming'
							self.Selected['Trans_Dis'] = dis
					
		if command != {}:
			self.A_Paint(command)
			
	#鼠标移动
	
	def mouseMoveEvent(self, event):
		
		if self.file['Field'].data:
			#将当前位置记录
			self.X_old = self.X
			self.Y_old = self.Y
		
		command = {}
		if self.file['Field'].data:
			#鼠标位置
			pos = event.pos()
			x = pos.x()
			y = pos.y()
			
			PX = 128
			zoom = self.PARAMETER['Img_parameter']['Zoom']
			px = int(PX * zoom)
			
			self.X, self.Y = self.Set_XY((int(x / px), int(y / px)))
			POS = (self.X, self.Y)
			
			#状态条改变
			text = ''
			text += 'size = ('+str(self.file['Field'].size()[0])+', '+str(self.file['Field'].size()[1])+')'
			text += '      |      '
			text += 'pos = ('+str(self.X)+', '+str(self.Y)+')'
			
			self.statue.showMessage(text)
			
			#刷新光标
			if self.Is_Move():
				command['Cursor'] = None
			
			
		if event.buttons() == QtCore.Qt.RightButton:
			#右键移动指令
			print(event.pos())
			if self.file['Field'].data:
				Button_id = self.PARAMETER['Command']['Button']
				#Brush删除模式
				if Button_id >= 0 and Button_id < len(Button_Brush_Int):
					panel_id = 0
					ischange = self.Point_Panel(panel_id)
					if ischange:
						command['Point'] = POS
						
				#删除箭头
				if Button_id >= len(Button_Brush_Int) + 1 and Button_id <= len(Button_Brush_Int) + 3:
					ischange = self.Point_Arrow(arrow_command = [-1,-1,-1,-1])
					if ischange:
						command['Point'] = POS
					
		elif event.buttons() == QtCore.Qt.LeftButton:
			#左键按下指令
			if self.file['Field'].data:
				Button_id = self.PARAMETER['Command']['Button']
				#Brush模式
				if Button_id >= 0 and Button_id < len(Button_Brush_Int):
					B_command = self.PARAMETER['Command']['Button']
					panel_id = Button_Brush_Int[B_command]
					ischange = self.Point_Panel(panel_id)
					if ischange:
						command['Point'] = POS
						
						
				#删除箭头
				if Button_id == len(Button_Brush_Int) + 1:
					ischange = self.Point_Arrow(arrow_command = [-1,-1,-1,-1])
					if ischange:
						command['Point'] = POS
						
				#Line箭头
				if Button_id == len(Button_Brush_Int) + 2:
					POS_old = (self.X_old, self.Y_old)
					#两个格子中有任意虚空格无效
					if not (self.file['Field'].Point_IsVoid(POS) or self.file['Field'].Point_IsVoid(POS_old)):
						Arrow_Name = ['Left', 'Up', 'Right', 'Down']
						arrow_command = [0,0,0,0]
						arrow_add = ''
						if self.X - self.X_old == -1:
							arrow_add = 'Left'
						elif self.X - self.X_old == 1:
							arrow_add = 'Right'
						elif self.Y - self.Y_old == -1:
							arrow_add = 'Up'
						elif self.Y - self.Y_old == 1:
							arrow_add = 'Down'
							
						if arrow_add != '':
							arrow_command[Arrow_Name.index(arrow_add)] = 1
							
						ischange = self.Point_Arrow(arrow_command, old = True)
						if ischange:
							command['Point'] = POS_old
						
				#Line删除箭头
				if Button_id == len(Button_Brush_Int) + 3:
					Arrow_Name = ['Left', 'Up', 'Right', 'Down']
					arrow_command = [0,0,0,0]
					arrow_add = ''
					if self.X - self.X_old == -1:
						arrow_add = 'Left'
					elif self.X - self.X_old == 1:
						arrow_add = 'Right'
					elif self.Y - self.Y_old == -1:
						arrow_add = 'Up'
					elif self.Y - self.Y_old == 1:
						arrow_add = 'Down'
						
					if arrow_add != '':
						arrow_command[Arrow_Name.index(arrow_add)] = -1
						
					ischange = self.Point_Arrow(arrow_command, old = True)
					if ischange:
						POS_old = (self.X_old, self.Y_old)
						command['Point'] = POS_old
						
				#选择模式
				if Button_id == len(Button_Brush_Int):
					if self.Selected['Type'] == 'Selecting':
						self.Selected['Pos_End'] = POS
						
				if Button_id == len(Button_Brush_Int):
					if self.Selected['Type'] == 'Transforming':
						self.Selected['Trans_Pos'] = self.Pos_Minus(POS, self.Selected['Trans_Dis'])
						
					
		if command != {}:
			self.A_Paint(command)
				
	#鼠标释放
	def mouseReleaseEvent(self, Event):
		#记录
		if self.file['Field'].data:
			self.Record()
		#结束选择
		if self.Selected['Type'] == 'Selecting':
			self.Selected_Start()
		#结束move
		if self.Selected['Type'] == 'Transforming':
			self.Selected['Type'] = 'Transform'
			
		self.A_Paint({'Cursor':None})
	
	#按钮指令变化
	def Button_Click(self, id):
		#在非选择模式，更换按钮
		if self.Selected['Type'] == 'None':
			if id >= 0 and id < len(Button_Brush_Int) + 4:
				#更换按钮
				self.PARAMETER['Command']['Button'] = id
		#在选择模式下，不更换按钮，执行fill指令
		if self.Selected['Type'] == 'Selected':
			ischange = False
			#fill panel
			if id >= 0 and id < len(Button_Brush_Int):
				panel_id = Button_Brush_Int[id]
				ischange = self.Fill(panel_id)
			#fill 删除箭头
			if id == len(Button_Brush_Int) + 1:
				#删除箭头使用特殊id = 101
				ischange = self.Fill(101)
			#取消选择
			if id == len(Button_Brush_Int) + 5:
				self.Selected_Cancel()
				
			if ischange:
				
				#储存
				self.Record()
				
				#对图像的改变
				Pos1 = self.Selected['Pos_Start']
				Pos2 = self.Selected['Pos_End']
				Rec = [Pos1, Pos2]
				command = {'Rec':Rec}
				self.A_Paint(command)
				
		#Transform模式
		
		if self.Selected['Type'] == 'Transform':
			#确认变换
			if id == len(Button_Brush_Int) + 10:
				self.Transform_Ok()
			#取消变换
			if id == len(Button_Brush_Int) + 11:
				self.Transform_Cancel()
				
			#自由变换
			if id >= len(Button_Brush_Int) + 6 and id < len(Button_Brush_Int) + 10:
				list = ['clockwise', 'anticlockwise', 'vertical', 'horizonal']
				sign = list[id - len(Button_Brush_Int) - 6]
				self.Free(sign)

	'''储存'''
	def Save(self, path):
		if self.Is_Field() and path != '':
			file_full = path
			file_name = QtCore.QFileInfo(file_full).fileName()
			
			#储存文件
			self.file['Field'].Save(file_full)
			
			#更改配置
			self.file_name = file_name
			self.file_path = file_full
			self.Save_Index = len(self.file['History']) - self.file['Pos']
			
			#A_Command
			a_command = {}
			#菜单栏更新
			a_command['Menu'] = None
			#储存标签变更
			a_command['Tab'] = None
			#A_Command信号发射
			self.App['Command'].emit(a_command)
			
		
	'''选择'''
	def Selected_Start(self):
		self.Selected['Type'] = 'Selected'
		def RePos(pos1, pos2):
			x1 = pos1[0]
			x2 = pos2[0]
			y1 = pos1[1]
			y2 = pos2[1]
			posmin = (min(x1,x2), min(y1,y2))
			posmax = (max(x1,x2), max(y1,y2))
			return posmin, posmax
			
		Pos1 = self.Selected['Pos_Start']
		Pos2 = self.Selected['Pos_End']
		self.Selected['Pos_Start'], self.Selected['Pos_End'] = RePos(Pos1, Pos2)
		
		#A_Command
		a_command = {}
		#状态变更
		a_command['Status'] = {}
		#按钮图标变更
		a_command['Button'] = {'Icon':{}}
		#菜单栏更新
		a_command['Menu'] = None
		#A_Command信号发射
		self.App['Command'].emit(a_command)
			
		
	def Selected_Cancel(self):
		#设置
		self.Selected['Type'] = 'None'
		self.Selected['Type'] = 'None'
		self.Selected['Pos_Start'] = (0,0)
		self.Selected['Pos_End'] = (0,0)
		#更换按钮
		self.PARAMETER['Command']['Button'] = len(Button_Brush_Int)
		#光标更新
		command = {'Cursor':None}
		self.A_Paint(command)
		
		#A_Command
		a_command = {}
		#状态变更
		a_command['Status'] = {}
		#按钮图标变更
		a_command['Button'] = {'Icon':{}}
		#菜单栏更新
		a_command['Menu'] = None
		#A_Command信号发射
		self.App['Command'].emit(a_command)
		
		
	'''编辑'''
	#单点格子变化
	def Point_Panel(self, panel_id):
		pos = (self.X, self.Y)
		ischange = self.file['Field'].Point_Panel(pos, panel_id)
		if ischange:
			self.file['Change'] = 1
			
			#A_Command
			a_command = {}
			#状态变更
			a_command['Status'] = {}
			if panel_id:
				a_command['Status']['Last_Action'] = 'Brush ' + Panel_Name[Panel_Int.index(panel_id)]
			else:
				a_command['Status']['Last_Action'] = 'Delete Panels'
			#A_Command信号发射
			self.App['Command'].emit(a_command)
				
		return ischange
		
	#单点箭头变化
	def Point_Arrow(self, arrow_command = [0,0,0,0], old = False):
		pos = (self.X, self.Y)
		if old:
			pos = (self.X_old, self.Y_old)
		ischange = self.file['Field'].Point_Arrow(pos, arrow_command, self.PARAMETER['Img_parameter']['BackTrack'])
		if ischange:
			self.file['Change'] = 1
			#A_Command
			a_command = {}
			#状态变更
			a_command['Status'] = {}
			if -1 in arrow_command:
				a_command['Status']['Last_Action'] = 'Delete Arrows'
			elif 1 in arrow_command:
				a_command['Status']['Last_Action'] = 'Draw Arrows'
			#A_Command信号发射
			self.App['Command'].emit(a_command)
			
		return ischange
		
	#填充
	def Fill(self, panel_id):
		Pos1 = self.Selected['Pos_Start']
		Pos2 = self.Selected['Pos_End']
		Rec = [Pos1, Pos2]
		ischange = self.file['Field'].Fill(Rec, panel_id, self.PARAMETER['Img_parameter']['BackTrack'])
		
		if ischange:
			self.file['Change'] = 1
			#A_Command
			a_command = {}
			#状态变更
			a_command['Status'] = {}
			if panel_id == 0:
				a_command['Status']['Last_Action'] = 'Delete Panels'
			elif panel_id == 101:
				a_command['Status']['Last_Action'] = 'Delete Arrows'
			else:
				a_command['Status']['Last_Action'] = 'Fill ' + Panel_Name[Panel_Int.index(panel_id)]
			#A_Command信号发射
			self.App['Command'].emit(a_command)
		
		return ischange
		
	#剪切
	def Cut(self):
		Pos1 = self.Selected['Pos_Start']
		Pos2 = self.Selected['Pos_End']
		Rec = [Pos1, Pos2]
		
		data_new = self.file['Field'].Cut(Rec)
		file_new = OFE_Field('create', data_new)
		
		self.PARAMETER['Clipboard'] = file_new
		
		#储存
		if file_new.has_value():
			self.file['Change'] = 1
			self.Record()
		#图像改变
		self.Selected['Copy_Index'] = 1
		Pos1 = self.Selected['Pos_Start']
		Pos2 = self.Selected['Pos_End']
		Rec = [Pos1, Pos2]
		command = {'Rec':Rec}
		self.A_Paint(command)
		
		#A_Command
		a_command = {}
		#状态变更
		a_command['Status'] = {}
		a_command['Status']['Last_Action'] = 'Cut'
		#菜单栏更新
		a_command['Menu'] = None
		#A_Command信号发射
		self.App['Command'].emit(a_command)
		
		
	#复制
	def Copy(self):
		Pos1 = self.Selected['Pos_Start']
		Pos2 = self.Selected['Pos_End']
		Rec = [Pos1, Pos2]
		
		data_new = self.file['Field'].Copy(Rec)
		file_new = OFE_Field('create', data_new)
		
		self.PARAMETER['Clipboard'] = file_new
		
		#图像改变
		self.Selected['Copy_Index'] = 1
		command = {'Cursor':None}
		self.A_Paint(command)
		
		#A_Command
		a_command = {}
		#状态变更
		a_command['Status'] = {}
		a_command['Status']['Last_Action'] = 'Copy'
		#菜单栏更新
		a_command['Menu'] = None
		#A_Command信号发射
		self.App['Command'].emit(a_command)
		
	#粘贴
	def Paste(self):
		Pos = self.Selected['Pos_Start']
		section = self.PARAMETER['Clipboard']
		
		self.file['Field'].Paste(Pos, section.data)
		
		#新光标
		x_new = min(Pos[0] + section.size()[0], self.file['Field'].size()[0]) - 1
		y_new = min(Pos[1] + section.size()[1], self.file['Field'].size()[1]) - 1
		self.Selected['Pos_End'] = (x_new, y_new)
		
		#储存
		self.file['Change'] = 1
		self.Record()
		##图像改变
		self.Selected['Copy_Index'] = 0
		command = {'All':None}
		self.A_Paint(command)
		
		#A_Command
		a_command = {}
		#状态变更
		a_command['Status'] = {}
		a_command['Status']['Last_Action'] = 'Paste'
		#菜单栏更新
		a_command['Menu'] = None
		#A_Command信号发射
		self.App['Command'].emit(a_command)
		
	#变换
	def Transform(self):
		self.Selected['Type'] = 'Transform'
		self.Selected['Type'] = 'Transform'
		
		#区域剪切，写入Trans_Field
		Pos1 = self.Selected['Pos_Start']
		Pos2 = self.Selected['Pos_End']
		Rec = [Pos1, Pos2]
		
		data_new = self.file['Field'].Cut(Rec)
		file_new = OFE_Field('create', data_new)
		self.Selected['Trans_Field'] = file_new
		
		#初始化此图片
		img_area = OFE_Image(self.Selected['Trans_Field'], self.Graphics, self.PARAMETER['Img_parameter']).Main()
		self.Selected['Trans_Img'] = img_area
		
		#初始位置设定
		self.Selected['Trans_Pos'] = self.Selected['Pos_Start']
		
		##图像改变
		command = {'All':None}
		self.A_Paint(command)
		
		#A_Command
		a_command = {}
		#状态变更
		a_command['Status'] = {}
		#按钮图标变更
		a_command['Button'] = {'Icon':{}}
		#菜单栏更新
		a_command['Menu'] = None
		#A_Command信号发射
		self.App['Command'].emit(a_command)

	#Duplicate
	def Duplicate(self):
		self.Selected['Type'] = 'Transform'
		self.Selected['Type'] = 'Transform'
		
		#区域剪切，写入Trans_Field
		Pos1 = self.Selected['Pos_Start']
		Pos2 = self.Selected['Pos_End']
		Rec = [Pos1, Pos2]
		
		data_new = self.file['Field'].Copy(Rec)
		file_new = OFE_Field('create', data_new)
		self.Selected['Trans_Field'] = file_new
		
		#初始化此图片
		img_area = OFE_Image(self.Selected['Trans_Field'], self.Graphics, self.PARAMETER['Img_parameter']).Main()
		self.Selected['Trans_Img'] = img_area
		
		#初始位置设定
		self.Selected['Trans_Pos'] = self.Selected['Pos_Start']
		
		#状态临时记录
		self.Selected['Duplicate_Index'] = 1
		##图像改变
		command = {'All':None}
		self.A_Paint(command)
		
		#A_Command
		a_command = {}
		#状态变更
		a_command['Status'] = {}
		#按钮图标变更
		a_command['Button'] = {'Icon':{}}
		#菜单栏更新
		a_command['Menu'] = None
		#A_Command信号发射
		self.App['Command'].emit(a_command)
		
	#Free
	def Free(self, sign):
		self.Selected['Trans_Field'].Free(sign)
		
		#重画此图片
		img_area = OFE_Image(self.Selected['Trans_Field'], self.Graphics, self.PARAMETER['Img_parameter']).Main()
		self.Selected['Trans_Img'] = img_area
		
		##图像改变
		command = {'Cursor':None}
		self.A_Paint(command)
		
	#确认变换
	def Transform_Ok(self):
		#新地图
		self.file['Field'].Paste(self.Selected['Trans_Pos'], self.Selected['Trans_Field'].data)
	
		#参数变化
		self.Selected['Type'] = 'Selected'
		self.Selected['Pos_Start'] = self.Set_XY(self.Selected['Trans_Pos'])
		pos_add = self.Pos_Add(self.Selected['Trans_Pos'], self.Selected['Trans_Field'].size())
		pos_end = self.Set_XY((pos_add[0]-1, pos_add[1]-1))
		self.Selected['Pos_End'] = pos_end
		self.Selected['Trans_Field'] = None
		self.Selected['Trans_Img'] = None
		
		#状态变更
		self.Selected['Duplicate_Index'] = 0
		
		#储存
		self.file['Change'] = 1
		self.Record()
		#图像改变
		Pos1 = self.Selected['Pos_Start']
		Pos2 = self.Selected['Pos_End']
		Rec = [Pos1, Pos2]
		command = {'Rec':Rec}
		self.A_Paint(command)
		
		#A_Command
		a_command = {}
		#状态变更
		a_command['Status'] = {}
		if self.Selected['Duplicate_Index']:
			a_command['Status']['Last_Action'] = 'Duplicate'
		else:
			a_command['Status']['Last_Action'] = 'Transform'
		#菜单栏更新
		a_command['Menu'] = None
		#按钮图标变更
		a_command['Button'] = {'Icon': {}}
		#A_Command信号发射
		self.App['Command'].emit(a_command)
		
		
	#取消变换
	def Transform_Cancel(self):
		#初始化
		self.Selected['Type'] = 'Selected'
		self.Selected['Trans_Field'] = None
		self.Selected['Trans_Img'] = None
		
		#读取历史
		field = self.file['History'][-1]
		self.file['Field'] = copy.deepcopy(field)
		
		#重画
		self.A_Paint({'All':None})
		#状态临时记录
		self.Selected['Duplicate_Index'] = 0
		
		#A_Command
		a_command = {}
		#菜单栏更新
		a_command['Menu'] = None
		#按钮图标变更
		a_command['Button'] = {'Icon': {}}
		#A_Command信号发射
		self.App['Command'].emit(a_command)
			
	'''记录'''
	
	def Need_Save(self):
		if not self.Is_Field():
			return False
		if self.Save_Index == len(self.file['History']) - self.file['Pos']:
			return False
		return True
	
	#记录
	def Record(self):
		if self.file['Change']:
			self.file['Change'] = 0
			#删除未来史
			pos = self.file['Pos']
			if pos > 1:
				self.file['History'] = self.file['History'][:-pos+1]
				self.file['Pos'] = 1
			#写入历史
			self.file['History'].append(copy.deepcopy(self.file['Field']))
			#储存标签变更
			if len(self.file['History']) - self.file['Pos'] <= self.Save_Index:
				self.Save_Index = -1
				
				
			#A_Command
			a_command = {}
			#状态变更
			a_command['Status'] = {}
			#菜单栏更新
			a_command['Menu'] = None
			#储存标签变更
			a_command['Tab'] = None
			#A_Command信号发射
			self.App['Command'].emit(a_command)
			
			
	#撤销
	def Undo(self):
		history_len = len(self.file['History'])
		if history_len > self.file['Pos']:
			self.file['Pos'] += 1
			pos = self.file['Pos']
			field = self.file['History'][-pos]
			self.file['Field'] = copy.deepcopy(field)
			
			#重画
			self.A_Paint({'All':None})
			
			#A_Command
			a_command = {}
			#状态变更
			a_command['Status'] = {}
			a_command['Status']['Last_Action'] = 'Undo'
			#菜单栏更新
			a_command['Menu'] = None
			#储存标签变更
			a_command['Tab'] = None
			#A_Command信号发射
			self.App['Command'].emit(a_command)
			
	#重做
	def Redo(self):
		if self.file['Pos'] > 1:
			self.file['Pos'] -= 1
			pos = self.file['Pos']
			field = self.file['History'][-pos]
			self.file['Field'] = copy.deepcopy(field)
			
			#重画
			self.A_Paint({'All':None})
			
			#A_Command
			a_command = {}
			#状态变更
			a_command['Status'] = {}
			a_command['Status']['Last_Action'] = 'Redo'
			#菜单栏更新
			a_command['Menu'] = None
			#储存标签变更
			a_command['Tab'] = None
			#A_Command信号发射
			self.App['Command'].emit(a_command)
			
			
	'''绘制'''
			
	#绘制总函数
	def A_Paint(self, command = {}):
		self.Paint_Command = command
		self.repaint()
		self.Paint_Command = {}
			
	#画笔事件
	def paintEvent(self, event):
		
		#初始化
		command = self.Paint_Command
		paint = QtGui.QPainter()
		paint.begin(self)
		
		#画地图本体
		PX = 128
		zoom = self.PARAMETER['Img_parameter']['Zoom']
		px = int(PX * zoom)
		
		img = self.Img_Draw(command)
		
		#画Transform
		self.Transform_Draw(img, command)
		
		#背景
		Img_Back = Image.new("RGBA", img.size, self.PARAMETER['Img_parameter']['Background'])
		Img_Back.paste(img, (0,0), img.split()[3])
		#填充画布
		paint.drawPixmap(self.rect(), PIXMAP(Img_Back))
		
		#画线
		
		def DrawRec(px, Pen_Size, pos, posend = None):
			Shrink = int(Pen_Size/2)
			if posend == None:
				x1 = pos[0]*px + Shrink
				x2 = pos[0]*px + px - Shrink
				y1 = pos[1]*px + Shrink
				y2 = pos[1]*px + px - Shrink
			else:
				def RePos(pos1, pos2):
					x1 = pos1[0]
					x2 = pos2[0]
					y1 = pos1[1]
					y2 = pos2[1]
					posmin = (min(x1,x2), min(y1,y2))
					posmax = (max(x1,x2), max(y1,y2))
					return posmin, posmax
				pos1, pos2 = RePos(pos, posend)
				x1 = pos1[0]*px + Shrink
				x2 = pos2[0]*px + px - Shrink
				y1 = pos1[1]*px + Shrink
				y2 = pos2[1]*px + px - Shrink
				
			paint.drawLine(x1, y1, x1, y2)
			paint.drawLine(x1, y1, x2, y1)
			paint.drawLine(x2, y2, x1, y2)
			paint.drawLine(x2, y2, x2, y1)
		
		
		
		#画线开始
		if self.Is_Field():
			#在选择事项出现时绘制选择方框
			if self.Selected['Type'] == 'Selecting' or self.Selected['Type'] == 'Selected':
				Pen_Size = 2
				if self.Selected['Copy_Index']:
					pen = QtGui.QPen(QtCore.Qt.blue, Pen_Size, QtCore.Qt.SolidLine)
				else:
					pen = QtGui.QPen(QtCore.Qt.green, Pen_Size, QtCore.Qt.SolidLine)
				paint.setPen(pen)
				DrawRec(px, Pen_Size, self.Selected['Pos_Start'], self.Selected['Pos_End'])
			#在变换事项出现时绘制黄色方框
			if self.Selected['Type'] == 'Transform' or self.Selected['Type'] == 'Transforming':
				Pen_Size = 2
				pen = QtGui.QPen(QtCore.Qt.yellow, Pen_Size, QtCore.Qt.SolidLine)
				size = self.Selected['Trans_Field'].size()
				pos_start = self.Selected['Trans_Pos']
				pos_end = (pos_start[0]+size[0]-1, pos_start[1]+size[1]-1)
				paint.setPen(pen)
				DrawRec(px, Pen_Size, pos_start, pos_end)
			#只要不在选择进行中就绘制光标
			if self.Selected['Type'] == 'None' or self.Selected['Type'] == 'Selected' or self.Selected['Type'] == 'Transform':
				Pen_Size = 2
				pen = QtGui.QPen(QtCore.Qt.red, Pen_Size, QtCore.Qt.SolidLine)
				paint.setPen(pen)
				DrawRec(px, Pen_Size, (self.X, self.Y))
				
		paint.end()
		
		
	def Transform_Draw(self, img, command = {}):
		#在Transform出现时让背景变暗，并绘制被选择的区域
		if self.Selected['Type'] == 'Transform' or self.Selected['Type'] == 'Transforming':
			PX = 128
			zoom = self.PARAMETER['Img_parameter']['Zoom']
			px = int(PX * zoom)
			#根据指令重画Transform
			if 'Transform_Redraw' in command:
				img_area = OFE_Image(self.Selected['Trans_Field'], self.Graphics, self.PARAMETER['Img_parameter']).Main()
				self.Selected['Trans_Img'] = img_area
			
			mask = Image.new("RGBA", img.size,(0,0,0,128))
			img.paste(mask, (0,0), mask.split()[3])
			
			img_area = self.Selected['Trans_Img']
			pos = self.Selected['Trans_Pos']
			img.paste(img_area, (pos[0]*px, pos[1]*px), img_area.split()[3])
			
			
	# 生成Img的总函数
	def Img_Draw(self, command = {}):
		if not self.Is_Field():
			img = self.Init_Draw()
		else:
			img = None
			#重画整张图
			if 'All' in command:
				img = self.Main_Draw()
				
			#重画一个格子
			if 'Point' in command:
				Point_Pos = command['Point']
				img = self.Point_Draw(Point_Pos)
				
			#重画一个矩形区域
			if 'Rec' in command:
				Rec = command['Rec']
				img = self.Rec_Draw(Rec)
				
			#画图完毕，保存地图到self
			if img:
				self.Field_Img = img
			
			img = self.Field_Img
			
		#全部绘制完成，固定窗口大小，返回图片
		self.setFixedSize(img.size[0],img.size[1])
		return copy.deepcopy(img)
			
	
	# main画
	def Main_Draw(self):
		#画地图本体
		img = OFE_Image(self.file['Field'], self.Graphics, self.PARAMETER['Img_parameter']).Main()
		return img
		
	#单格画
	def Point_Draw(self, pos):
		#从现有图片改变单个格子
		img = OFE_Image(self.file['Field'], self.Graphics, self.PARAMETER['Img_parameter']).Point(self.Field_Img, pos)
		return img
		
	#矩形画
	def Rec_Draw(self, rec):
		#从现有图片改变一个区域（暂时全画）
		img = OFE_Image(self.file['Field'], self.Graphics, self.PARAMETER['Img_parameter']).Main()
		return img
		
	# Logo画
	def Init_Draw(self):
		img = Image.open(path0 + r'./title_logo.png')
		zoom = self.PARAMETER['Img_parameter']['Zoom'] * 3
		newsize = (int(img.size[0]*zoom), int(img.size[1]*zoom))
		img = img.resize(newsize, Image.BICUBIC)
		img_main = Image.new("RGBA", img.size,self.PARAMETER['Img_parameter']['Background'])
		img_main.paste(img,(0,0),img.split()[3])
		return img_main
	
	###状态变化###
	#菜单变化
	def Menu_Change(self):
	
		#储存
		if self.Is_Field() and self.Selected['Type'] != 'Transform':
			self.PARAMETER['Menu_able']['Save_As'] = 0
			if self.Need_Save():
				self.PARAMETER['Menu_able']['Save'] = 0
			else:
				self.PARAMETER['Menu_able']['Save'] = 1
		else:
			self.PARAMETER['Menu_able']['Save_As'] = 1
			self.PARAMETER['Menu_able']['Save'] = 1
		
		#撤销
		if len(self.file['History']) == self.file['Pos'] or len(self.file['History']) == 0:
			self.PARAMETER['Menu_able']['Undo'] = 1
		else:
			self.PARAMETER['Menu_able']['Undo'] = 0
			
		#重做
		if self.file['Pos'] <= 1:
			self.PARAMETER['Menu_able']['Redo'] = 1
		else:
			self.PARAMETER['Menu_able']['Redo'] = 0
			
			
		#剪切复制粘贴变换
		if self.Selected['Type'] == 'Selected':
			self.PARAMETER['Menu_able']['Cut'] = 0
			self.PARAMETER['Menu_able']['Copy'] = 0
			self.PARAMETER['Menu_able']['Transform'] = 0
			self.PARAMETER['Menu_able']['Duplicate'] = 0
			if self.PARAMETER['Clipboard']:
				self.PARAMETER['Menu_able']['Paste'] = 0
			else:
				self.PARAMETER['Menu_able']['Paste'] = 1
		else:
			self.PARAMETER['Menu_able']['Cut'] = 1
			self.PARAMETER['Menu_able']['Copy'] = 1
			self.PARAMETER['Menu_able']['Paste'] = 1
			self.PARAMETER['Menu_able']['Transform'] = 1
			self.PARAMETER['Menu_able']['Duplicate'] = 1
			
		#变换时全部禁用
		if self.Selected['Type'] == 'Transform':
			self.PARAMETER['Menu_able']['Undo'] = 1
			self.PARAMETER['Menu_able']['Redo'] = 1
			self.PARAMETER['Menu_able']['Cut'] = 1
			self.PARAMETER['Menu_able']['Copy'] = 1
			self.PARAMETER['Menu_able']['Paste'] = 1
			self.PARAMETER['Menu_able']['Transform'] = 1
			self.PARAMETER['Menu_able']['Duplicate'] = 1
			
		
	#A状态变化
	def A_Status(self, command = {}):
		#History数目
		command['History_Len'] = len(self.file['History'])
		command['History_Pos'] = self.file['Pos']
		#选择范围
		if self.Selected['Type'] == 'Selected':
			pos_start = self.Selected['Pos_Start']
			pos_end = self.Selected['Pos_End']
			command['Selected'] = [pos_start, pos_end]
		elif self.Selected['Type'] == 'None':
			command['Selected'] = []
		
		return command
		
	#A按钮图标更新
	def A_Button(self, command = {}):
		#总状态
		command['Type'] = self.Selected['Type']
		return command

#画板框架
class Canvas_Frame(QtWidgets.QWidget):
	def __init__(self, field, PARAMETER, App = None, file_name = 'Title', file_path = '', parent = None):
		super(Canvas_Frame,self).__init__(parent)
		self.init(field, PARAMETER, App, file_name, file_path)
		
	def init(self, field, PARAMETER, App = None, file_name = 'Title', file_path = ''):
				
		# Label 原代码
		
		#状态条
		self.statue = QtWidgets.QStatusBar(self)
		self.statue.showMessage("")
		
		#画板
		self.canvas = Canvas(field, PARAMETER, self.statue, App, file_name, file_path)
		
		#滚动条
		scroll = QtWidgets.QScrollArea()
		scroll.setWidget(self.canvas)
		scroll.setAutoFillBackground(True)  
		scroll.setWidgetResizable(True)
		
		#打包
		vbox = QtWidgets.QVBoxLayout()  
		vbox.addWidget(scroll) 
		vbox.addWidget(self.statue)
		self.setLayout(vbox)
		
	def Is_Field(self):
		return self.canvas.Is_Field()
		
	def Field(self):
		return self.canvas.Field()
		
	def file_name(self):
		return self.canvas.file_name
		
	def file_path(self):
		return self.canvas.file_path
		
	def Need_Save(self):
		return self.canvas.Need_Save()
		
	def Menu_Change(self):
		self.canvas.Menu_Change()
		
	def A_Status(self, command = {}):
		self.canvas.A_Status(command)
		
	def Button_Click(self ,id):
		self.canvas.Button_Click(id)
		
	def A_Button(self, command = {}):
		self.canvas.A_Button(command)
		
	def Save(self, path):
		self.canvas.Save(path)
		
	def Undo(self):
		self.canvas.Undo()
		
	def Redo(self):
		self.canvas.Redo()
		
	def Cut(self):
		self.canvas.Cut()
		
	def Copy(self):
		self.canvas.Copy()
		
	def Paste(self):
		self.canvas.Paste()
		
	def Transform(self):
		self.canvas.Transform()		
		
	def Duplicate(self):
		self.canvas.Duplicate()
		
		
	def width(self):
		return self.canvas.width()
		
	def height(self):
		return self.canvas.height()

#画板Tab
		
class Canvas_Tab(QtWidgets.QTabWidget):
	
	TabEmitApp = QtCore.pyqtSignal()
	
	def __init__(self, PARAMETER, App = None, parent = None):
		super(Canvas_Tab,self).__init__(parent)
		self.init(PARAMETER, App)
	
	def init(self, PARAMETER, App = None):
	
		#初始化
		self.PARAMETER = PARAMETER
		self.App = App
		
		#初始画板
		self.Canvas_List = []
		self.Insert_Canvas()
		
		#检测Tab发生变化
		self.currentChanged.connect(self.OnChange)
		
		#更新Tab文本
		self.TabEmitApp.connect(self.Tab_Refresh)
		
		
	def Insert_Canvas(self, field = None, file_name = 'Title', file_path = ''):
		if field:
			self.PARAMETER['Menu_able']['Close'] = 0
		else:
			field = OFE_Field()
			
		#新画板
		canvas_new = Canvas_Frame(field, self.PARAMETER, self.App, file_name, file_path)
		
		#第一个非地图去掉
		if self.Canvas_List != []:
			if not self.Canvas_List[0].Is_Field():
				self.removeTab(0)
				self.Canvas_List = []
				
		#创建新Tab
		id = self.count()
		self.Canvas_List.append(canvas_new)
		self.insertTab(id, canvas_new, file_name)
		
		#将新窗口对准
		self.setCurrentIndex(id)
		
		#A_Command
		a_command = {}
		#菜单栏更新
		a_command['Menu'] = None
		#储存标签变更
		a_command['Tab'] = None
		#A_Command信号发射
		self.App['Command'].emit(a_command)
		
		
	def Remove_Canvas(self):
		if self.Canvas_List == []:
			return
		if not self.Canvas_List[0].Is_Field():
			return
			
		current_id = self.currentIndex()
		file_name = self.Canvas_List[current_id].file_name()
		self.Canvas_List.pop(current_id)
		self.removeTab(current_id)
		
		if self.Canvas_List == []:
			self.Insert_Canvas()
			
		#A_Command
		a_command = {}
		#菜单栏更新
		a_command['Menu'] = None
		#A_Command信号发射
		self.App['Command'].emit(a_command)
		
		return file_name
		
	def Is_Field(self):
		current_id = self.currentIndex()
		return self.Canvas_List[current_id].Is_Field()
		
	def Field(self):
		current_id = self.currentIndex()
		return self.Canvas_List[current_id].Field()
		
	def file_name(self):
		current_id = self.currentIndex()
		return self.Canvas_List[current_id].file_name()
		
	def file_path(self):
		current_id = self.currentIndex()
		return self.Canvas_List[current_id].file_path()
		
	def Need_Save(self):
		current_id = self.currentIndex()
		return self.Canvas_List[current_id].Need_Save()
		
	def Save(self, path):
		current_id = self.currentIndex()
		self.Canvas_List[current_id].Save(path)
			
	def Undo(self):
		current_id = self.currentIndex()
		self.Canvas_List[current_id].Undo()
		
	def Redo(self):
		current_id = self.currentIndex()
		self.Canvas_List[current_id].Redo()
		
	def Cut(self):
		current_id = self.currentIndex()
		self.Canvas_List[current_id].Cut()
		
	def Copy(self):
		current_id = self.currentIndex()
		self.Canvas_List[current_id].Copy()
		
	def Paste(self):
		current_id = self.currentIndex()
		self.Canvas_List[current_id].Paste()
		
	def Transform(self):
		current_id = self.currentIndex()
		self.Canvas_List[current_id].Transform()
		
	def Duplicate(self):
		current_id = self.currentIndex()
		self.Canvas_List[current_id].Duplicate()
		
	def width(self):
		current_id = self.currentIndex()
		return self.Canvas_List[current_id].width()
		
	def height(self):
		current_id = self.currentIndex()
		return self.Canvas_List[current_id].height()
		
	def A_Paint(self, command):
		current_id = self.currentIndex()
		self.Canvas_List[current_id].canvas.A_Paint(command)
		
	def Menu_Change(self):
		if self.Canvas_List != []:
			if not self.Canvas_List[0].Is_Field():
				#关闭菜单变动
				self.PARAMETER['Menu_able']['Close'] = 1
				
		#调用下级
		current_id = self.currentIndex()
		self.Canvas_List[current_id].Menu_Change()
		
	def A_Status(self, command = {}):
		#调用下级
		current_id = self.currentIndex()
		self.Canvas_List[current_id].A_Status(command)
		
	def Button_Click(self, id):
		#调用下级
		current_id = self.currentIndex()
		self.Canvas_List[current_id].Button_Click(id)
		
	def A_Button(self, command = {}):
		#调用下级
		current_id = self.currentIndex()
		self.Canvas_List[current_id].A_Button(command)
		
	#改变Tab文本
	def Tab_Refresh(self):
		current_id = self.currentIndex()
		text = self.Canvas_List[current_id].file_name()
		if self.Canvas_List[current_id].Need_Save():
			text += '*'
		self.setTabText(current_id, text)
		
	#Tab切换时
	def OnChange(self, Event):
		#改变文件index
		if Event >= 0:
			#A_Command
			a_command = {}
			#状态变更
			a_command['Status'] = {}
			#按钮图标变更
			a_command['Button'] = {'Icon':{}}
			#菜单栏更新
			a_command['Menu'] = None
			#A_Command信号发射
			self.App['Command'].emit(a_command)
		
