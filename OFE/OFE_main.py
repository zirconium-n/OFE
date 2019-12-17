import sys, os
import re, struct
from PyQt5 import QtGui, QtWidgets, QtCore
from PIL import Image
from PIL.ImageQt import ImageQt

from OFE.OFE_Field import OFE_Field
from OFE import ButtonWindow
from OFE import StatusWindow
from OFE import Canvas_Tab
from OFE import OFE_Upload, OFE_New, OFE_Files
from OFE.OFE_Graphics import OFE_Graphics

#根目录
path0 = os.path.dirname(__file__)
		
#版本号
VERSION = ' v0.3'

class OFE_MainWindow(QtWidgets.QMainWindow):
	
	#命令处理信号，当需要处理命令并因此改变界面等信息时，发射给OFE_MainWindow::A_Command，参数为字典，装着需要执行的命令。
	CommandEmitApp = QtCore.pyqtSignal(dict)
	#按钮按下信号，当按钮被按下时，从ButtonWindow::Button_Click发射，参数为按钮id
	ButtonEmitApp = QtCore.pyqtSignal(int)
	
	def __init__(self):
		super(OFE_MainWindow, self).__init__()
		self.initUI() #界面绘制交给InitUi方法
		
	def initUI(self):
	
		#标题和图标
		self.setWindowTitle("100oj Fields Editor" + VERSION) 
		self.setWindowIcon(QtGui.QIcon(path0 + '/'+ 'panels/Panel_Check.png')) 
		
		##加载全局参数
		self.PARAMETER = self.Init_PARAMETER()
		
		#窗口位置（来自全局参数）
		window_pos = self.PARAMETER['Img_parameter']['Window_Pos']
		self.setGeometry(window_pos[0], window_pos[1], 1000, 600)
		
		##控件布局
		main_ground = QtWidgets.QWidget(self)
		self.setCentralWidget(main_ground)
		self.layout_main = QtWidgets.QHBoxLayout(main_ground)
		layout_sub = QtWidgets.QVBoxLayout()
		
		#画板区
		self.canvaswindow = Canvas_Tab(self.PARAMETER, App = {'Command':self.CommandEmitApp}) 
		
		#侧边栏
		self.statuswindow = StatusWindow()
		verticalSpacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
		self.buttonwindow = ButtonWindow(self.PARAMETER, App = {'Command':self.CommandEmitApp, 'Button':self.ButtonEmitApp})
		
		layout_sub.addWidget(self.statuswindow)
		layout_sub.addItem(verticalSpacer)
		layout_sub.addWidget(self.buttonwindow)
		layout_sub.addItem(verticalSpacer)
		
		self.layout_main.addWidget(self.canvaswindow)
		self.layout_main.addLayout(layout_sub)
		
		main_ground.setLayout(self.layout_main)
		
		##菜单栏
		
		self.Set_Menu()
		
		###总Command连接###
		self.CommandEmitApp.connect(self.A_Command)
		
		#按钮按下信号
		self.ButtonEmitApp.connect(self.Button_Click)
		
		#主更新
		self.A_Command({'Menu': None, 'Status': {}, 'Resize': None})
		
	#设置菜单栏
	def Set_Menu(self):
		menubar = self.menuBar()
		self.Menu_All = {}
		
		def set_menu(name, connect, shortcut = '', StatusTip = '', checkable=False):
			menu = QtWidgets.QAction(name,self,checkable = checkable)
			menu.setShortcut(shortcut)
			menu.setStatusTip(StatusTip)
			menu.triggered.connect(connect)
			
			return menu
		
		##文件
		file = menubar.addMenu("File")
		#新建
		new_menu = set_menu('New...', self.New, 'Ctrl+N', 'Open a new field')
		file.addAction(new_menu)
		self.Menu_All['New'] = new_menu
		#打开
		open_menu = set_menu('Open...', self.Open, 'Ctrl+O', 'Open an existing field')
		file.addAction(open_menu)
		self.Menu_All['Open'] = open_menu
		#打开
		open_official_menu = set_menu('Open Official', self.Open_Official, 'Open an official field')
		file.addAction(open_official_menu)
		self.Menu_All['Open_Official'] = open_official_menu
		#关闭
		close_menu = set_menu('Close', self.Close, 'Ctrl+W', 'Close the current field')
		file.addAction(close_menu)
		self.Menu_All['Close'] = close_menu
		#--
		file.addSeparator()
		#保存
		save_menu = set_menu('Save Field', self.Save, 'Ctrl+S', 'Save the field in its current field name')
		file.addAction(save_menu)
		self.Menu_All['Save'] = save_menu
		#另存为
		save_as_menu = set_menu('Save Field As...', self.Save_As, 'Save the field with a new name')
		file.addAction(save_as_menu)
		self.Menu_All['Save_As'] = save_as_menu
		#--
		file.addSeparator()
		#上传
		upload_menu = set_menu('Upload', self.Upload, 'Ctrl+U', 'Upload the field to the game')
		file.addAction(upload_menu)
		self.Menu_All['Upload'] = upload_menu
		#--
		file.addSeparator()
		#退出
		exit_menu = set_menu('Exit', QtWidgets.qApp.quit, "Alt+F4", "Exit")
		file.addAction(exit_menu)
		self.Menu_All['Exit'] = exit_menu
		
		##编辑
		edit = menubar.addMenu("Edit")
		#撤销
		undo_menu = set_menu('Undo', self.Undo, 'Ctrl+Z', 'Undo the last action')
		edit.addAction(undo_menu)
		self.Menu_All['Undo'] = undo_menu
		#重做
		redo_menu = set_menu('Redo', self.Redo, 'Ctrl+Y', 'Redo the last action')
		edit.addAction(redo_menu)
		self.Menu_All['Redo'] = redo_menu
		#--
		edit.addSeparator()
		#剪切
		cut_menu = set_menu('Cut', self.Cut, 'Ctrl+X', 'Cut the section and put it on the Clipboard')
		edit.addAction(cut_menu)
		self.Menu_All['Cut'] = cut_menu
		#复制
		copy_menu = set_menu('Copy', self.Copy, 'Ctrl+C', 'Copy the section and put it on the Clipboard')
		edit.addAction(copy_menu)
		self.Menu_All['Copy'] = copy_menu
		#粘贴
		paste_menu = set_menu('Paste', self.Paste, 'Ctrl+V', 'Insert Clipboard contents')
		edit.addAction(paste_menu)
		self.Menu_All['Paste'] = paste_menu
		#--
		edit.addSeparator()
		#变换
		transform_menu = set_menu('Transform', self.Transform, 'Ctrl+T', 'Transform the section')
		edit.addAction(transform_menu)
		self.Menu_All['Transform'] = transform_menu
		#duplicate
		duplicate_menu = set_menu('Duplicate', self.Duplicate, 'Ctrl+D', 'Duplicate and transform the section')
		edit.addAction(duplicate_menu)
		self.Menu_All['Duplicate'] = duplicate_menu
		
		##视图
		view = menubar.addMenu("View")
		#改变背景颜色
		background_menu = set_menu('Background color', self.Background, StatusTip = 'Set background color')
		view.addAction(background_menu)
		self.Menu_All['Background'] = background_menu
		#--
		view.addSeparator()
		#界面缩放大小
		zoom_level_menu = view.addMenu("Zoom Level")
		zoom_level_menu.setStatusTip('Change Zoom Level')
		self.zoom_group = QtWidgets.QActionGroup(self, exclusive=True)
		
		for zoom in self.PARAMETER['Img_parameter']['Zoom_List']:
			action = self.zoom_group.addAction(QtWidgets.QAction(str(zoom), self, checkable=True))
			action.triggered.connect(self.Zoom_Level)
			zoom_level_menu.addAction(action)
			
			if zoom == self.PARAMETER['Img_parameter']['Zoom']:
				action.setChecked(True)
		#按钮缩放大小
		button_zoom_level_menu = view.addMenu("Button Zoom Level")
		button_zoom_level_menu.setStatusTip('Change Buttons Zoom Level')
		self.button_zoom_group = QtWidgets.QActionGroup(self, exclusive=True)
		
		for zoom in self.PARAMETER['Img_parameter']['Zoom_List']:
			action = self.button_zoom_group.addAction(QtWidgets.QAction(str(zoom), self, checkable=True))
			action.triggered.connect(self.Button_Zoom_Level)
			button_zoom_level_menu.addAction(action)
			
			if zoom == self.PARAMETER['Img_parameter']['Button_Zoom']:
				action.setChecked(True)
		#--
		view.addSeparator()
		#BackTrack
		backtrack_menu = set_menu('BackTrack', self.BackTrack, StatusTip = 'Switch BackTrack', checkable = True)
		view.addAction(backtrack_menu)
		self.Menu_All['BackTrack'] = backtrack_menu
		
		
	#初始化参数
	def Init_PARAMETER(self):
		parameter = {}
		#读取参数文件
		try:
			file_para = open(path0 + '/'+ 'user.dat', 'r')
		except:
			text_para = ''
		else:
			text_para = file_para.read()
			print(text_para)
			file_para.close()
		
		#在文本中寻找对应参数
		def find_parameter(text, name, default):
			try:
				text1 = re.search(name + '=.+', text).group()
			except:
				value = default
			else:
				pos = text1.find('=')
				value = text1[pos+1:]
				if type(default) == type(0.75):
					value = float(value)
				elif type(default) == type(1):
					value = int(value)
				elif type(default) == type((1,2,3)):
					p = re.compile(',')
					value = tuple(map(int, (p.split(value[1:-1]))))
				elif type(default) == type('path'):
					value = str(value)
			return value
		
		#文件参数
		parameter['Clipboard'] = None
		parameter['Path_Save'] = find_parameter(text_para, 'Path_Save', path0)
		parameter['Path_Game'] = find_parameter(text_para, 'Path_Game', path0)
		#视图参数
		parameter['Img_parameter'] = {}
		parameter['Img_parameter']['Window_Pos'] = find_parameter(text_para, 'Window_Pos', (600, 60))
		parameter['Img_parameter']['Zoom_List'] = (0.25, 0.375, 0.5, 0.625, 0.75, 1.0)
		parameter['Img_parameter']['Zoom'] = find_parameter(text_para, 'Zoom', 0.5)
		parameter['Img_parameter']['Background'] = find_parameter(text_para, 'Background', (52,52,52,256))
		parameter['Img_parameter']['Show_arrows'] = find_parameter(text_para, 'Show_arrows', 1)
		parameter['Img_parameter']['Button_Zoom'] = find_parameter(text_para, 'Button_Zoom', 0.5)
		parameter['Img_parameter']['BackTrack'] = 0
		parameter['Img_parameter']['Frame'] = find_parameter(text_para, 'Frame', 1)
		#菜单可用参数
		parameter['Menu_able'] = {}
		parameter['Menu_able']['Close'] = 1
		parameter['Menu_able']['Save'] = 1
		parameter['Menu_able']['Save_As'] = 1
		parameter['Menu_able']['Undo'] = 1
		parameter['Menu_able']['Redo'] = 1
		parameter['Menu_able']['Cut'] = 1
		parameter['Menu_able']['Copy'] = 1
		parameter['Menu_able']['Paste'] = 1
		parameter['Menu_able']['Transform'] = 1
		parameter['Menu_able']['Duplicate'] = 1
		#涉及命令逻辑的相关参数
		parameter['Command'] = {}
		#当前按下的按钮
		parameter['Command']['Button'] = 18
		
		#加载图片素材
		zoom_list = parameter['Img_parameter']['Zoom_List'] = (0.25, 0.375, 0.5, 0.625, 0.75, 1.0)
		parameter['Graphics'] = OFE_Graphics(zoom_list, path0 + '/'+ 'panels')
		
		#设置按钮Id
		parameter['Button'] = {}
		parameter['Button']['Type'] = ['Panel', 'Mouse', 'Transform']
		parameter['Button']['Specific'] = [['Void', 'Check', 'Bonus', 'Bonus_2', 'Drop', 'Drop_2', 'Encounter', 'Encounter_2', 
				'Draw', 'Draw_2', 'Move', 'Move_2', 'WarpMove', 'WarpMove_2', 'Warp', 'Snow', 'Neutral', 'Deck'],
				['Mouse', 'ArrowDelete', 'ArrowLine', 'ArrowLineDelete', 'OK', 'Cancel'],
				['Clock_test', 'AntiClock_test', 'Vertical_test', 'Horizonal_test', 'OK', 'Cancel']]
		parameter['Button']['Id'] = {}
		parameter['Button']['Name'] = {}
		for i, type_ in enumerate(parameter['Button']['Type']):
			for j, specific in enumerate(parameter['Button']['Specific'][i]):
				id = 100*i + j
				parameter['Button']['Id'][id] = specific
				parameter['Button']['Name'][specific] = id
				
		print(parameter['Button']['Id'])
		print(parameter['Button']['Name'])
		
		return parameter
		
	#重关闭事件
	def closeEvent(self, event):
		#写入参数文件
		file_para = open(path0 + '/'+ 'user.dat', 'w')
		text = ''
		
		def write_parameter(text, name, value):
			text += name + '=' + str(value) + '\n'
			return text
		
		text = write_parameter(text, 'Path_Save', self.PARAMETER['Path_Save'])
		text = write_parameter(text, 'Path_Game', self.PARAMETER['Path_Game'])
		text = write_parameter(text, 'Window_Pos', self.PARAMETER['Img_parameter']['Window_Pos'])
		text = write_parameter(text, 'Zoom', self.PARAMETER['Img_parameter']['Zoom'])
		text = write_parameter(text, 'Background', self.PARAMETER['Img_parameter']['Background'])
		text = write_parameter(text, 'Show_arrows', self.PARAMETER['Img_parameter']['Show_arrows'])
		text = write_parameter(text, 'Button_Zoom', self.PARAMETER['Img_parameter']['Button_Zoom'])
		text = write_parameter(text, 'Frame', self.PARAMETER['Img_parameter']['Frame'])
		
		file_para.write(text)
		file_para.close()
		
	#重写移动事件
	def moveEvent(self, event):
		pos = (event.pos().x(), event.pos().y())
		self.PARAMETER['Img_parameter']['Window_Pos'] = pos
		
	###总Command函数###
	def A_Command(self, command):
		
		#Paint，在画板上重绘，command['Paint'] = {}
		if 'Paint' in command:
			self.canvaswindow.A_Paint(command['Paint'])
		#Button，改变按钮形貌，command['Button'] = {}
		if 'Button' in command:
			#先调用下级，从而给command['Button']['Icon']赋值 = {'Type': str}
			if 'Icon' in command['Button']:
				self.canvaswindow.A_Button(command['Button']['Icon'])
			self.buttonwindow.A_Button(command['Button'])
		#Resize
		if 'Resize' in command:
			self.Resize()
		#Menu
		if 'Menu' in command:
			self.Menu_Refresh()
		#Status
		if 'Status' in command:
			#先调用下级，从而给command['Status']赋值 = {...}
			self.canvaswindow.A_Status(command['Status'])
			self.statuswindow.A_Status(command['Status'])
		#Tab
		if 'Tab' in command:
			self.canvaswindow.Tab_Refresh()
			
	#尺寸调整
	def Resize(self):
		#屏幕大小
		screen = QtWidgets.QDesktopWidget().screenGeometry()
		MaxWidth = screen.width()-200
		MaxHeight = screen.height()-100
		#推荐窗口尺寸，来自画板
		commandwidth = self.canvaswindow.width() + 86 
		commandheight = self.canvaswindow.height() + 150 
		#来自按钮
		PX = 128
		button_zoom = self.PARAMETER['Img_parameter']['Button_Zoom']
		px = int(PX * button_zoom)
		commandwidth += 6 * px
		self.resize(min(commandwidth, MaxWidth), min(commandheight,MaxHeight))
			
	def Menu_Refresh(self):
		#调用下级
		self.canvaswindow.Menu_Change()
	
		#菜单栏管理
		for key in self.PARAMETER['Menu_able']:
			if self.PARAMETER['Menu_able'][key]:
				self.Menu_All[key].setEnabled(False)
			else:
				self.Menu_All[key].setEnabled(True)
		#标题管理
		id = self.canvaswindow.currentIndex()
		if id >= 0:
			if self.canvaswindow.Canvas_List[id].Is_Field():
				text = "100oj Fields Editor" + VERSION
				file_full = self.canvaswindow.Canvas_List[id].file_path()
				if file_full != '':
					text += " - " + file_full
				self.setWindowTitle(text)
			else:
				self.setWindowTitle("100oj Fields Editor" + VERSION)
		else:
			self.setWindowTitle("100oj Fields Editor" + VERSION)
			
	#更新状态
		
	def Button_Click(self, id):
		print("Main Button Click", id)
		self.canvaswindow.Button_Click(id)
		
	def New(self):
		Size = OFE_New.Get_Size(self)
		if Size:
			
			#新建并存入画板
			field = OFE_Field('new', Size)
			self.canvaswindow.Insert_Canvas(field, 'Untitled')
			
			#A_Command
			a_command = {}
			#Last Action
			a_command['Status'] = {}
			a_command['Status']['Last_Action'] = '[New]'
			#A_Command信号发射
			self.CommandEmitApp.emit(a_command)
			
		
	def Open(self):
		options = QtWidgets.QFileDialog.Options()
		file_full, _ = QtWidgets.QFileDialog.getOpenFileName(self,"Open a field", self.PARAMETER['Path_Save'],"Fields (*.fld);;All Files (*)", options=options)
		if file_full:
			file_name = QtCore.QFileInfo(file_full).fileName()
			file_path = QtCore.QFileInfo(file_full).absolutePath()
			#重设默认路径
			self.PARAMETER['Path_Save'] = file_path
			#打开文件至画板
			field = OFE_Field('open', file_full)
			self.canvaswindow.Insert_Canvas(field, file_name, file_full)
			
			#A_Command
			a_command = {}
			#尺寸调整
			a_command['Resize'] = None
			#菜单调整
			a_command['Menu'] = None
			#Last Action
			a_command['Status'] = {}
			a_command['Status']['Last_Action'] = '[Open] ' + file_name
			#A_Command信号发射
			self.CommandEmitApp.emit(a_command)
			
	def Open_Official(self):
		Field_and_Name = OFE_Files.Get_Field(self)
		if Field_and_Name:
			field = Field_and_Name[0]
			name = Field_and_Name[1]
			
			self.canvaswindow.Insert_Canvas(field, name)
			
			#A_Command
			a_command = {}
			#尺寸调整
			a_command['Resize'] = None
			#菜单调整
			a_command['Menu'] = None
			#Last Action
			a_command['Status'] = {}
			a_command['Status']['Last_Action'] = '[Open] ' + name
			#A_Command信号发射
			self.CommandEmitApp.emit(a_command)
			
			
	def Close(self):
		file_name = self.canvaswindow.Remove_Canvas()
		
		if file_name:
			#A_Command
			a_command = {}
			#尺寸调整
			a_command['Resize'] = None
			#菜单调整
			a_command['Menu'] = None
			#Last Action
			a_command['Status'] = {}
			a_command['Status']['Last_Action'] = '[Close] '+file_name
			#A_Command信号发射
			self.CommandEmitApp.emit(a_command)
		else:
			print('Error: Can not close.')
		
	def Save(self):
		need_save = self.canvaswindow.Need_Save()
		if need_save:
			file_path = self.canvaswindow.file_path()
			if file_path == '':
				self.Save_As()
			else:
				file_full = file_path
				#初始化
				file_name = QtCore.QFileInfo(file_full).fileName()
				file_path = QtCore.QFileInfo(file_full).absolutePath()
				#重设默认路径
				self.PARAMETER['Path_Save'] = file_path
				#储存成文件
				self.canvaswindow.Save(file_full)
				
				#A_Command
				a_command = {}
				#Last Action
				a_command['Status'] = {}
				a_command['Status']['Last_Action'] = '[Save] ' + file_name
				#A_Command信号发射
				self.CommandEmitApp.emit(a_command)
		
	def Save_As(self):
		options = QtWidgets.QFileDialog.Options()
		file_full, _ = QtWidgets.QFileDialog.getSaveFileName(self,"Save Field", self.PARAMETER['Path_Save'],"Fields (*.fld);;All Files (*)", options=options)
		if file_full:
			#初始化
			file_name = QtCore.QFileInfo(file_full).fileName()
			file_path = QtCore.QFileInfo(file_full).absolutePath()
			#重设默认路径
			self.PARAMETER['Path_Save'] = file_path
			#储存成文件
			self.canvaswindow.Save(file_full)
			
			#A_Command
			a_command = {}
			#Last Action
			a_command['Status'] = {}
			a_command['Status']['Last_Action'] = '[Save] ' + file_name
			#A_Command信号发射
			self.CommandEmitApp.emit(a_command)
		
	def Upload(self):
		#获取当前field
		id = self.canvaswindow.currentIndex()
		if id >= 0:
			field_now = self.canvaswindow.Field()
				
		#打开dialog，返回game文件的新路径
		path_new = OFE_Upload.Upload_Main(self, self.PARAMETER['Path_Game'], field_now)
		if path_new:
			self.PARAMETER['Path_Game'] = path_new
		
	def Undo(self):
		self.canvaswindow.Undo()
		
	def Redo(self):
		self.canvaswindow.Redo()
		
	def Cut(self):
		self.canvaswindow.Cut()
		
	def Copy(self):
		self.canvaswindow.Copy()
		
	def Paste(self):
		self.canvaswindow.Paste()
		
	def Transform(self):
		self.canvaswindow.Transform()
		
	def Duplicate(self):
		self.canvaswindow.Duplicate()
		
	def Background(self):
		col = QtWidgets.QColorDialog.getColor()
		if col.isValid(): 
			self.PARAMETER['Img_parameter']['Background'] = (col.red(), col.green(), col.blue(), 256)
			
	def Zoom_Level(self):
		action_this = self.zoom_group.checkedAction()
		zoom = float(action_this.text())
		
		self.PARAMETER['Img_parameter']['Zoom'] = zoom
		
		#A_Command
		a_command = {}
		#图像刷新，transform刷新
		a_command['Paint'] = {'All':None, 'Transform_Redraw': None}
		#画布大小
		a_command['Resize'] = None
		#A_Command信号发射
		self.CommandEmitApp.emit(a_command)
		
	def Button_Zoom_Level(self):
		action_this = self.button_zoom_group.checkedAction()
		zoom = float(action_this.text())
		
		self.PARAMETER['Img_parameter']['Button_Zoom'] = zoom
		
		#A_Command
		a_command = {}
		#按钮大小重设
		a_command['Button'] = {'Zoom': None}
		#画布大小
		a_command['Resize'] = None
		#A_Command信号发射
		self.CommandEmitApp.emit(a_command)
			
	def BackTrack(self, state):
		if state:
			self.PARAMETER['Img_parameter']['BackTrack'] = 1
		else:
			self.PARAMETER['Img_parameter']['BackTrack'] = 0
		
		#A_Command
		a_command = {}
		#图像刷新，transform刷新
		a_command['Paint'] = {'All':None, 'Transform_Redraw': None}
		#画布大小
		a_command['Resize'] = None
		#A_Command信号发射
		self.CommandEmitApp.emit(a_command)
		
def run():
	app = QtWidgets.QApplication(sys.argv)
	ex = OFE_MainWindow()
	ex.show()
	sys.exit(app.exec_()) 

if __name__ == '__main__':
	run()