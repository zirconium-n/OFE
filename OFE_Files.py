import sys, os
import zipfile
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5 import QtWidgets, QtCore, QtGui

from OFE_Field import OFE_Field
from OFE_Image import OFE_Image

import tempfile
import shutil

#移除pak中的指定文件
def remove_from_zip(zipfname, *filenames):
	tempdir = tempfile.mkdtemp()
	try:
		tempname = os.path.join(tempdir, 'new.zip')
		with zipfile.ZipFile(zipfname, 'r') as zipread:
			with zipfile.ZipFile(tempname, 'w') as zipwrite:
				for item in zipread.infolist():
					if item.filename not in filenames:
						data = zipread.read(item.filename)
						zipwrite.writestr(item, data)
		shutil.move(tempname, zipfname)
	finally:
		shutil.rmtree(tempdir)

#根目录
path0 = os.path.dirname(os.path.realpath(sys.argv[0]))

class OFE_Upload(QtWidgets.QDialog):
	def __init__(self, game_path, field, parent = None):
		super(OFE_Upload, self).__init__()
		
		self.game_path = game_path
		self.field_now = field
		#初始化
		self.setWindowTitle("Upload Manager")
		self.setGeometry(600, 100, 900, 600)
		#本地地图列表
		self.Local_Field_Dict = self.Open_Fields(path = path0 + '\\' + 'fields.pak')
		#游戏地图列表
		self.Game_Field_Dict = self.Open_Fields(path = game_path)
		
		def ICON(img):
			ImgQt = ImageQt(img)
			pixmap = QtGui.QPixmap.fromImage(ImgQt)
			icon = QtGui.QIcon(pixmap)
			return icon
		
		#主框架
		layout_main = QtWidgets.QVBoxLayout()
		
		
		#从本地文件中获得排序的文件名列表
		self.Name_List = []
		for name in self.Local_Field_Dict:
			self.Name_List.append(name)
			
		self.Name_List.sort()
		
		#grid的layout
		grid_layout = QtWidgets.QGridLayout()
		#各种组
		self.label_img_list = []
		self.label_size_list = []
		self.label_state_list = []
		self.reset_group = QtWidgets.QButtonGroup()
		self.reset_group.buttonClicked.connect(self.Reset)
		self.upload_group = QtWidgets.QButtonGroup()
		self.upload_group.buttonClicked.connect(self.Upload)
		# upload_group = QtWidgets.QButtonGroup()
		#开始做Grid。当前图标、本地文件名、当前大小、状态
		for i, name in enumerate(self.Name_List):
			#是否存在该文件
			Exist = 0
			if name in self.Game_Field_Dict:
				Exist = 1
				
			#0本地文件名
			label_name = QtWidgets.QLabel(name)
			grid_layout.addWidget(label_name, i, 0)
				
			#1应该的大小
			size_o = self.Local_Field_Dict[name].size()
			label_size_o = QtWidgets.QLabel(str(size_o[0])+'x'+str(size_o[1]))
			grid_layout.addWidget(label_size_o, i, 1)
				
			#2图标
			if Exist:
				img = OFE_Image(self.Game_Field_Dict[name]).PX_Image()
			else:
				img = Image.open(path0+r'\panels\Panel_Void.png')
				
			SIZE = (32,32)
			img = img.resize(SIZE, Image.BICUBIC)
			
			def PIXMAP(img):
				ImgQt = ImageQt(img)
				pixmap = QtGui.QPixmap.fromImage(ImgQt)
				return pixmap
			
			label_img = QtWidgets.QLabel()
			label_img.setPixmap(PIXMAP(img))
			label_img.setFixedSize(SIZE[0],SIZE[1])
			grid_layout.addWidget(label_img, i, 2)
			
			self.label_img_list.append(label_img)
			
			#3当前的大小
			if Exist:
				size = self.Game_Field_Dict[name].size()
			else:
				size = (0, 0)
			if size == size_o:
				label_size = QtWidgets.QLabel("<font color='green'>" + str(size[0])+'x'+str(size[1]) + "</font>")
			else:
				label_size = QtWidgets.QLabel("<font color='red'>" + str(size[0])+'x'+str(size[1]) + "</font>")
			grid_layout.addWidget(label_size, i, 3)
			
			self.label_size_list.append(label_size)
			
			#4状态
			if Exist:
				if self.Game_Field_Dict[name].data == self.Local_Field_Dict[name].data:
					text = 'Original'
				else:
					text = 'Custom'
			else:
				text = 'Lost'
				
			label_state = QtWidgets.QLabel()
			if text == 'Original':
				label_state.setText("<font color='green'>Original</font>")
			if text == 'Custom':
				label_state.setText("<font color='blue'>Custom</font>")
			if text == 'Lost':
				label_state.setText("<font color='red'>Lost</font>")
			grid_layout.addWidget(label_state, i, 4)
			
			self.label_state_list.append(label_state)
			
			#5 Reset按钮
			reset_button = QtWidgets.QPushButton('Reset')
			self.reset_group.addButton(reset_button, i)
			grid_layout.addWidget(reset_button, i, 5)
			
			#6 Upload按钮
			upload_button = QtWidgets.QPushButton('Upload')
			self.upload_group.addButton(upload_button, i)
			grid_layout.addWidget(upload_button, i, 6)
			
			
		#滚动条
		scroll_widget = QtWidgets.QWidget()
		scroll_widget.setLayout(grid_layout)
		scroll = QtWidgets.QScrollArea()
		scroll.setWidget(scroll_widget)
		scroll.setAutoFillBackground(True)  
		scroll.setWidgetResizable(True)
		
		layout_main.addWidget(scroll)
			
		#总布局
		self.setLayout(layout_main)
		#重置窗口大小
		width = self.sizeHint().width() + 20
		height = self.sizeHint().height() + 200
		self.resize(QtCore.QSize(width, height))
		
	def Upload(self, button):
		#当前按钮id和对应的文件名
		id = self.upload_group.id(button)
		name = self.Name_List[id]
		####将本地文件替换到游戏文件
		if self.field_now:
			if self.field_now.data:
				##生成一个临时文件
				#临时目录
				path_temporary = path0 + r'\temporary'
				file_temporary = open(path_temporary, 'wb')
				file_temporary.write(self.field_now.get_bin())
				file_temporary.close()
				
				#写入
				remove_from_zip(self.game_path, name)
				with zipfile.ZipFile(self.game_path, 'a') as pak_file:
					pak_file.write(path_temporary, arcname=name)
		
		#更新
		self.Update()
		
	def Reset(self, button):
		#当前按钮id和对应的文件名
		id = self.reset_group.id(button)
		name = self.Name_List[id]
		####将本地文件替换到游戏文件
		##生成一个临时文件
		#临时目录
		path_temporary = path0 + r'\temporary'
		file_temporary = open(path_temporary, 'wb')
		file_temporary.write(self.Local_Field_Dict[name].get_bin())
		file_temporary.close()
		
		#写入
		remove_from_zip(self.game_path, name)
		with zipfile.ZipFile(self.game_path, 'a') as pak_file:
			pak_file.write(path_temporary, arcname=name)
		
		#更新
		self.Update()
		
	def Update(self):
		
		#看文件个数
		with zipfile.ZipFile(self.game_path) as pak_file:
			name_list_o = pak_file.namelist()
		count = 0
		for name in name_list_o:
			if name[-4:] == '.fld':
				count += 1
				
		print(count)
		
		#游戏地图列表重新加载
		self.Game_Field_Dict = self.Open_Fields(path = self.game_path)
		for i, name in enumerate(self.Name_List):
			#是否存在该文件
			Exist = 0
			if name in self.Game_Field_Dict:
				Exist = 1
				
			#2图标
			if Exist:
				img = OFE_Image(self.Game_Field_Dict[name]).PX_Image()
			else:
				img = Image.open(path0+r'\panels\Panel_Void.png')
				
			SIZE = (32,32)
			img = img.resize(SIZE, Image.BICUBIC)
			
			def PIXMAP(img):
				ImgQt = ImageQt(img)
				pixmap = QtGui.QPixmap.fromImage(ImgQt)
				return pixmap
			
			self.label_img_list[i].setPixmap(PIXMAP(img))
			
			#3当前的大小
			size_o = self.Local_Field_Dict[name].size()
			if Exist:
				size = self.Game_Field_Dict[name].size()
			else:
				size = (0, 0)
			if size == size_o:
				self.label_size_list[i].setText("<font color='green'>" + str(size[0])+'x'+str(size[1]) + "</font>")
			else:
				self.label_size_list[i].setText("<font color='red'>" + str(size[0])+'x'+str(size[1]) + "</font>")
			
			#4状态
			if Exist:
				if self.Game_Field_Dict[name].data == self.Local_Field_Dict[name].data:
					text = 'Original'
				else:
					text = 'Custom'
			else:
				text = 'Lost'
				
			if text == 'Original':
				self.label_state_list[i].setText("<font color='green'>Original</font>")
			if text == 'Custom':
				self.label_state_list[i].setText("<font color='blue'>Custom</font>")
			if text == 'Lost':
				self.label_state_list[i].setText("<font color='red'>Lost</font>")
		
	def Upload_Main(app, game_path = '', field = None, parent = None):
	
		#检查本地文件是否正常
		path = path0 + '\\' + 'fields.pak'
		path = QtCore.QFileInfo(path).absoluteFilePath()
		try:
			pak_file = zipfile.ZipFile(path)
		except:
			QtWidgets.QMessageBox.critical(app, 'Error','Can not find fields.pak in '+path0, QtWidgets.QMessageBox.Ok)
			return
		else:
			#检查游戏文件目录是否匹配
			def Get_Game_Pak(app, game_path):
				
				game_path = QtCore.QFileInfo(game_path).absoluteFilePath()
				#检查名称准确
				file_name = QtCore.QFileInfo(game_path).fileName()
				if file_name == 'fields.pak':
					Name_Error = False
				else:
					Name_Error = True
					
				#检查是否是合法的压缩文件
				try:
					game_zip = zipfile.ZipFile(game_path)
				except:
					Pak_Error = True
				else:
					Pak_Error = False
					
				#检查路径是否是本地的路径
				if path == game_path:
					Path_Error = True
				else:
					Path_Error = False
					
				#如果出错，则重新选择路径
				if Name_Error or Path_Error or Pak_Error:
					options = QtWidgets.QFileDialog.Options()
					game_path, _ = QtWidgets.QFileDialog.getOpenFileName(app,"Open the fields.pak in game data", path0 ,"Pak (*.pak);;All Files (*)", options=options)
					
					#再次
					#检查名称准确
					file_name = QtCore.QFileInfo(game_path).fileName()
					if file_name == 'fields.pak':
						Name_Error = False
					else:
						Name_Error = True
						
					#检查是否是合法的压缩文件
					try:
						game_zip = zipfile.ZipFile(game_path)
					except:
						Pak_Error = True
					else:
						Pak_Error = False
						
					#检查路径是否是本地的路径
					if path == game_path:
						Path_Error = True
					else:
						Path_Error = False
					
				#通过/否决
				if Name_Error or Path_Error or Pak_Error:
					if Name_Error:
						QtWidgets.QMessageBox.critical(app, 'Error','You must find pak with name fields.pak', QtWidgets.QMessageBox.Ok)
					elif Pak_Error:
						QtWidgets.QMessageBox.critical(app, 'Error','Not a pak file', QtWidgets.QMessageBox.Ok)
					elif Path_Error:
						QtWidgets.QMessageBox.critical(app, 'Error','You must find fields.pak in game data', QtWidgets.QMessageBox.Ok)
				else:
					return game_path
			
			#真实游戏地图目录，如有问题则返回
			game_path = Get_Game_Pak(app, game_path)
			if not game_path:
				return
			
			#对话框开始
			dialog = OFE_Upload(game_path, field, parent)
			result = dialog.exec_()
			
			pak_file.close()
			return game_path
		
	#从本地的pak中获得地图dict
	def Open_Fields(self, path):
		with zipfile.ZipFile(path) as pak_file:
			#文件列表
			name_list_o = pak_file.namelist()
			name_fld = []
			for name in name_list_o:
				if name[-4:] == '.fld':
					name_fld.append(name)
					
			field_dict = {}
			for name in name_fld:
				fld_bin = pak_file.read(name)
				field = OFE_Field('bin', fld_bin)
				field_dict[name] = field
			
		return field_dict

class OFE_New(QtWidgets.QDialog):
	def __init__(self, parent = None):
		super(OFE_New, self).__init__()
		
		#初始化
		self.setWindowTitle("New")
		# self.setGeometry(300, 100, 400, 600)
		
		#地图文件列表
		self.Field_Dict = self.Open_Fields()
		
		#主框架
		layout_main = QtWidgets.QVBoxLayout()
		
		#Title
		title_label = QtWidgets.QLabel('Select a field size:')
		layout_main.addWidget(title_label)
		
		#Radio按钮layout
		radio_layout = QtWidgets.QGridLayout()
		self.radio_group = QtWidgets.QButtonGroup()
		
		self.size_list = []
		for i, name in enumerate(self.Field_Dict):
			field = self.Field_Dict[name]
			size = field.size()
			
			if not size in self.size_list:
				self.size_list.append(size)
		
		self.size_list.sort()
		
		for i, size in enumerate(self.size_list):
			radio = QtWidgets.QRadioButton(str(size[0])+'x'+str(size[1]))
			self.radio_group.addButton(radio, i)
			radio_layout.addWidget(radio, i, 0)
		
		layout_main.addLayout(radio_layout)
		
		#确认取消按钮
		ok_cancel = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
		ok_cancel.accepted.connect(self.accept)
		ok_cancel.rejected.connect(self.reject)
		layout_main.addWidget(ok_cancel)
		
		#总布局
		self.setLayout(layout_main)
		
	def Get_Size(app, parent = None):
		path = path0 + '\\' + 'fields.pak'
		try:
			pak_file = zipfile.ZipFile(path)
		except:
			QtWidgets.QMessageBox.critical(app, 'Error','Can not find fields.pak in '+path0, QtWidgets.QMessageBox.Ok)
			return
		else:
			dialog = OFE_New(parent)
			result = dialog.exec_()
			if result:
				id = dialog.radio_group.checkedId()
				if id >= 0:
					size = dialog.size_list[id]
					return size
				else:
					return
			else:
				return 
		
	def Open_Fields(self):
		path = path0 + '\\' + 'fields.pak'
		with zipfile.ZipFile(path) as pak_file:
		
			#文件列表
			name_list_o = pak_file.namelist()
			name_fld = []
			for name in name_list_o:
				if name[-4:] == '.fld':
					name_fld.append(name)
					
			field_dict = {}
			for name in name_fld:
				fld_bin = pak_file.read(name)
				field = OFE_Field('bin', fld_bin)
				field_dict[name] = field
			
		
		return field_dict

class OFE_Files(QtWidgets.QDialog):
	def __init__(self, parent = None):
		super(OFE_Files, self).__init__()
		
		#初始化
		self.setWindowTitle("Open Official Field")
		self.setGeometry(300, 100, 350, 600)
		
		#地图文件列表
		self.Field_Dict = self.Open_Fields()
		if self.Field_Dict:
		
			def ICON(img):
				ImgQt = ImageQt(img)
				pixmap = QtGui.QPixmap.fromImage(ImgQt)
				icon = QtGui.QIcon(pixmap)
				return icon
			
			#主框架
			layout_main = QtWidgets.QVBoxLayout()
			
			#Title
			title_label = QtWidgets.QLabel('Select a official field:')
			layout_main.addWidget(title_label)
			
			#Radio按钮layout
			radio_layout = QtWidgets.QGridLayout()
			self.radio_group = QtWidgets.QButtonGroup()
			
			self.Name_List = []
			for name in self.Field_Dict:
				self.Name_List.append(name)
				
			self.Name_List.sort()
			
			for i, name in enumerate(self.Name_List):
				#图片
				SIZE = (32, 32)
				img = OFE_Image(self.Field_Dict[name]).PX_Image()
				def PIXMAP(img):
					ImgQt = ImageQt(img)
					pixmap = QtGui.QPixmap.fromImage(ImgQt)
					return pixmap
				label_img = QtWidgets.QLabel()
				label_img.setPixmap(PIXMAP(img))
				label_img.setFixedSize(SIZE[0],SIZE[1])
				radio_layout.addWidget(label_img, i, 1)
				
				#radio，名字
				radio = QtWidgets.QRadioButton(name)
				self.radio_group.addButton(radio, i)
				radio_layout.addWidget(radio, i, 0)
				
				#大小
				size = self.Field_Dict[name].size()
				label = QtWidgets.QLabel(str(size[0])+'x'+str(size[1]))
				radio_layout.addWidget(label, i, 2)
			
			#滚动条
			scroll_widget = QtWidgets.QWidget()
			scroll_widget.setLayout(radio_layout)
			scroll = QtWidgets.QScrollArea()
			scroll.setWidget(scroll_widget)
			scroll.setAutoFillBackground(True)  
			scroll.setWidgetResizable(True)
			
			layout_main.addWidget(scroll)
			
			#确认取消按钮
			ok_cancel = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
			ok_cancel.accepted.connect(self.accept)
			ok_cancel.rejected.connect(self.reject)
			layout_main.addWidget(ok_cancel)
			
			#总布局
			self.setLayout(layout_main)
			
			#重置窗口大小
			width = self.sizeHint().width() + 20
			height = self.sizeHint().height() + 200
			self.resize(QtCore.QSize(width, height))
			
		
	def Get_Field(app, parent = None):
		
		path = path0 + '\\' + 'fields.pak'
		try:
			pak_file = zipfile.ZipFile(path)
		except:
			QtWidgets.QMessageBox.critical(app, 'Error','Can not find fields.pak in '+path0, QtWidgets.QMessageBox.Ok)
			return
		else:
		
			dialog = OFE_Files(parent)
			result = dialog.exec_()
			if result:
				id = dialog.radio_group.checkedId()
				if id >= 0:
					name = dialog.Name_List[id]
					field = dialog.Field_Dict[name]
					return field, name
				else:
					return
			else:
				return 
		
	def Open_Fields(self):
		path = path0 + '\\' + 'fields.pak'
		pak_file = zipfile.ZipFile(path)
		#文件列表
		name_list_o = pak_file.namelist()
		name_fld = []
		for name in name_list_o:
			if name[-4:] == '.fld':
				name_fld.append(name)
				
		field_dict = {}
		for name in name_fld:
			fld_bin = pak_file.read(name)
			field = OFE_Field('bin', fld_bin)
			field_dict[name] = field
			
		return field_dict

if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	field = OFE_Files.Get_Field(app)
	print(field)
	sys.exit(app.exec_())