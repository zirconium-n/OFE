#OFE_Buttoms
import sys, os
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5 import QtGui, QtWidgets, QtCore
from OFE_Panels import Panel_Int, Panel_Name

#根目录
path0 = os.path.dirname(os.path.realpath(sys.argv[0]))
#图片格式转换
def ICON(img):
	ImgQt = ImageQt(img)
	pixmap = QtGui.QPixmap.fromImage(ImgQt)
	icon = QtGui.QIcon(pixmap)
	return icon

class ButtonWindow(QtWidgets.QWidget):
	ButtonApp = QtCore.pyqtSignal(int)
	def __init__(self, PARAMETER, App = None, parent = None):
		QtWidgets.QWidget.__init__(self, parent)
		
		#初始化
		self.PARAMETER = PARAMETER
		self.App = App
		graphics = PARAMETER['Graphics']
		print(PARAMETER)
		###设置按钮(新)
		
		#按钮窗口layout
		layout_main = QtWidgets.QVBoxLayout()
		#按钮图标
		self.Button_icon = {}
		#总QButtonGroup
		self.ButtonGroup = QtWidgets.QButtonGroup()
		self.ButtonGroup.buttonClicked.connect(self.Button_Click)
		#设置窗口
		self.ButtonWidget = []
		#PX
		zoom = self.PARAMETER['Img_parameter']['Button_Zoom']
		PX = 128
		px = int(PX * zoom)
		#创建各个窗口和按钮
		'''
		for i, type_ in enumerate(self.PARAMETER['Button']['Type']):
			self.ButtonWidget.append(QtWidgets.QWidget())
			grid = QtWidgets.QGridLayout()
			for j, name in enumerate(self.PARAMETER['Button']['Specific'][i]):
				id = 100 * i + j
				self.Button_icon[id] = []
				
				#按钮图标加载：0 不处理，1 按下， 2 低光， 3 无图
				img_o = graphics.get_image(type_ + '_' + name)
				img0 = Image.new("RGBA", (PX,PX),(0,0,0,256))
				img0.paste(img_o, (0,0), img_o.split()[3])
				self.Button_icon[id].append(img0)
				img1 = Image.new("RGBA", (PX,PX),(256,256,256,256))
				img1.paste(img_o, (2,2), img_o.split()[3])
				self.Button_icon[id].append(img1)
				mask = Image.new("RGBA", (PX,PX),(0,0,0,64))
				img2 = Image.new("RGBA", (PX,PX),(256,256,256,256))
				img2.paste(img_o, (0,0), img_o.split()[3])
				img2.paste(mask, (0,0), mask.split()[3])
				self.Button_icon[id].append(img2)
				img3 = Image.new("RGBA", (PX,PX),(0,0,0,0))
				self.Button_icon[id].append(img3)
				
				#创建按钮
				button = QtWidgets.QPushButton()
				button.setFixedWidth(px)
				button.setFixedHeight(px)
				button.setIcon(ICON(self.Button_icon[id][2])) #默认低光
				button.setIconSize(QtCore.QSize(px,px))
				
				#绑定group
				self.ButtonGroup.addButton(button, id)
				
				#grid位置
				y = j/6
				x = j%6
				grid.addWidget(button, y, x)
				
			grid.setHorizontalSpacing(0)
			grid.setVerticalSpacing(0)
			self.ButtonWidget[i].setLayout(grid)
			layout_main.addWidget(self.ButtonWidget[i])
			
		self.setLayout(layout_main)
		'''
		
		#设置按钮(旧)
				
		#设置刷子类按钮
		Button_Brush_Int = [0,2,5,9,6,
							10,3,20,4,8,
							21,22,23,24,7,
							25,1,18,26,27
							,28,31,32,33]
		#鼠标类映射表
		Mouse_Name = ['Mouse', 'ArrowDelete', 'ArrowLine', 'ArrowLineDelete', 'OK', 'Cancel']
		#变换类映射表
		Transform_Name = ['Clock_test', 'AntiClock_test', 'Vertical_test', 'Horizonal_test', 'OK', 'Cancel']
			
		#按钮多种图片
		
		
		#普通
		self.Button_0 = []
		#按下
		self.Button_1 = []
		#低光
		self.Button_2 = []
		#无
		self.Button_3 = []
		panel_count = len(Panel_Int)
		button_count = 6
		transform_count = 6
		for id in range(panel_count + button_count + transform_count):
			if id < panel_count:
				img_o = graphics.get_image('Panel_' + Panel_Name[Panel_Int.index(Button_Brush_Int[id])]) 
				#Image.open(path0 + r'\panels\Panel_' + Panel_Name[Panel_Int.index(Button_Brush_Int[id])] + '.png')
				img0 = Image.new("RGBA", (PX,PX),(0,0,0,256))
				img0.paste(img_o, (0,0), img_o.split()[3])
				self.Button_0.append(img0)
				img1 = Image.new("RGBA", (PX,PX),(256,256,256,256))
				img1.paste(img_o, (2,2), img_o.split()[3])
				self.Button_1.append(img1)
				mask = Image.new("RGBA", (PX,PX),(0,0,0,64))
				img2 = Image.new("RGBA", (PX,PX),(256,256,256,256))
				img2.paste(img_o, (0,0), img_o.split()[3])
				img2.paste(mask, (0,0), mask.split()[3])
				self.Button_2.append(img2)
				img3 = Image.new("RGBA", (PX,PX),(0,0,0,0))
				self.Button_3.append(img3)
			elif id < panel_count + button_count:
				id -= panel_count
				img_o = graphics.get_image('Button_' + Mouse_Name[id]) #Image.open(path0 + r'\panels\Button_' + Mouse_Name[id] + '.png')
				print(Mouse_Name[id], id)
				img0 = Image.new("RGBA", (PX,PX),(0,0,0,256))
				img0.paste(img_o, (0,0), img_o.split()[3])
				self.Button_0.append(img0)
				img1 = Image.new("RGBA", (PX,PX),(256,256,256,256))
				img1.paste(img_o, (2,2), img_o.split()[3])
				self.Button_1.append(img1)
				mask = Image.new("RGBA", (PX,PX),(0,0,0,64))
				img2 = Image.new("RGBA", (PX,PX),(256,256,256,256))
				img2.paste(img_o, (0,0), img_o.split()[3])
				img2.paste(mask, (0,0), mask.split()[3])
				self.Button_2.append(img2)
				img3 = Image.new("RGBA", (PX,PX),(0,0,0,0))
				self.Button_3.append(img3)
			elif id < panel_count + button_count + transform_count:
				id -= panel_count + button_count
				img_o = graphics.get_image('Transform_' + Transform_Name[id]) #Image.open(path0 + r'\panels\Transform_' + Transform_Name[id] + '.png')
				print(Transform_Name[id], id)
				img0 = Image.new("RGBA", (PX,PX),(0,0,0,256))
				img0.paste(img_o, (0,0), img_o.split()[3])
				self.Button_0.append(img0)
			
		#按钮List
		self.Button_List = []
		button_grid_all = QtWidgets.QVBoxLayout()
		#刷子类
		brush_grid = QtWidgets.QGridLayout()

		def wrapper(ind):
			def q():
				self.Button_Click(ind)
			return q		
		for id in range(panel_count):
			self.Button_List.append(QtWidgets.QPushButton())
			self.Button_List[id].setFixedWidth(px)
			self.Button_List[id].setFixedHeight(px)
			self.Button_List[id].setIcon(ICON(self.Button_2[id]))
			self.Button_List[id].setIconSize(QtCore.QSize(px,px))
			self.Button_List[id].setStatusTip('Draw ' + Panel_Name[Panel_Int.index(Button_Brush_Int[id])]  + ' Panel')	
			self.Button_List[id].clicked.connect(wrapper(id))
		
		brush_grid.setHorizontalSpacing(0)
		brush_grid.setVerticalSpacing(0)
		
		#设置鼠标类按钮
		#鼠标工具#强删箭头工具#画箭头工具#擦除箭头工具#确认#取消
		mouse_grid = QtWidgets.QGridLayout()
		print("INIT", len(self.Button_List), panel_count)

		for id in range(6):
			buttonid = panel_count + id

			self.Button_List.append(QtWidgets.QPushButton())
			self.Button_List[buttonid].setFixedWidth(px)
			self.Button_List[buttonid].setFixedHeight(px)
			self.Button_List[buttonid].setIcon(ICON(self.Button_2[buttonid]))
			self.Button_List[buttonid].setIconSize(QtCore.QSize(px,px))
			self.Button_List[buttonid].setStatusTip(Mouse_Name[id])
			self.Button_List[buttonid].clicked.connect(wrapper(buttonid))


		
		#设置变换类按钮
		transform_grid = QtWidgets.QGridLayout()
		CONST = panel_count + button_count
		
		for id in range(6):
			buttonid = CONST + id
			self.Button_List.append(QtWidgets.QPushButton())
			self.Button_List[buttonid].setFixedWidth(px)
			self.Button_List[buttonid].setFixedHeight(px)
			self.Button_List[buttonid].setIcon(ICON(self.Button_0[buttonid]))
			self.Button_List[buttonid].setIconSize(QtCore.QSize(px,px))
			self.Button_List[buttonid].setStatusTip(Mouse_Name[id])
			self.Button_List[buttonid].clicked.connect(wrapper(buttonid))


		for id in range(CONST + transform_count):
			y, x = id // 6, id % 6
			if (id < panel_count):
				brush_grid.addWidget(self.Button_List[id], y, x)
			elif (id < CONST):
				mouse_grid.addWidget(self.Button_List[id], 0, id - panel_count)
			else:
				transform_grid.addWidget(self.Button_List[id], 0, id - CONST)
		
		button_grid_all.addLayout(brush_grid)
		button_grid_all.addLayout(mouse_grid)
		button_grid_all.addLayout(transform_grid)
		#设置整体框架
		
		self.setLayout(button_grid_all)
		
		#初始化按钮图标
		self.Button_Icon_Change()
		
		#快捷键
		self.Button_List[0].setShortcut('Delete')
		self.Button_List[panel_count + 10].setShortcut('Return')
		self.Button_List[panel_count + 5].setShortcut('Esc')
		self.Button_List[panel_count + 11].setShortcut('Esc')
	
		
		#测试
		
	def Button_Click(self, id):
		
		#print
		print(id)
		
		#旧按钮标记
		id_old = self.PARAMETER['Command']['Button']
		
		#按钮按下发射信号
		self.App['Button'].emit(id)
		
		id_new = self.PARAMETER['Command']['Button']
		
		#A_Command
		a_command = {}
		#状态变更
		a_command['Status'] = {}
		#按钮图标变更
		a_command['Button'] = {'Icon':{}}
		#A_Command信号发射
		self.App['Command'].emit(a_command)
		
	def A_Button(self, command):
		if 'Zoom' in command:
			self.Button_Zoom_Change()
		if 'Icon' in command:
			self.Button_Icon_Change(command['Icon'])
		
	def Button_Icon_Change(self, command = {'Type': 'None'}):
		#设置图标
		#选择按钮样式初始化
		magic = len(Panel_Int)
		def Selected_Button_Icon():
			list = []
			for i in range(magic + 6):
				list.append(0)
			list[magic] = 1
			list[magic + 2] = 3
			list[magic + 3] = 3
			return list
		def Init_Button_Icon():
			list = []
			for i in range(magic + 6):
				list.append(2)
			list[magic + 4] = 3
			list[magic + 5] = 3
			return list
		
		button_icon = []
		#处于选定状态下
		if command['Type'] == 'Selected':
			button_icon = Selected_Button_Icon()
		#处于一般状态下
		elif command['Type'] == 'None':
			button_icon = Init_Button_Icon()
			button_id = self.PARAMETER['Command']['Button']
			button_icon[button_id] = 1
		
		#更换图标
		for i, type in enumerate(button_icon):
			if type == 0:
				self.Button_List[i].setIcon(ICON(self.Button_0[i]))
			if type == 1:
				self.Button_List[i].setIcon(ICON(self.Button_1[i]))
			if type == 2:
				self.Button_List[i].setIcon(ICON(self.Button_2[i]))
			if type == 3:
				self.Button_List[i].setIcon(ICON(self.Button_3[i]))
				
		#Transform按钮在Transform形态下显示
		if command['Type'] == 'Transform':
			for i in range(magic + 6):
				self.Button_List[i].hide()
			for i in range(magic + 6, magic + 12):
				self.Button_List[i].show()
		else:
			for i in range(magic + 6):
				self.Button_List[i].show()
			for i in range(magic + 6, magic + 12):
				self.Button_List[i].hide()
				
	#更换按钮大小
	def Button_Zoom_Change(self):
		PX = 128
		Button_Zoom = self.PARAMETER['Img_parameter']['Button_Zoom']
		px = int(PX * Button_Zoom)
		for button in self.Button_List:
			button.setFixedWidth(px)
			button.setFixedHeight(px)
			button.setIconSize(QtCore.QSize(px,px))
