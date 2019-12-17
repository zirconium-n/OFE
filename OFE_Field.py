#OFE_Field

import struct
import math

class OFE_Field:
	def __init__(self, order = None, parameter = None):
		self.data = None
		
		#新建
		if order == 'new':
			X, Y = parameter
			self.data = []
			for j in range(Y):
				self.data.append([])
				for i in range(X):
					self.data[j].append([0,0])
		
		#从文件读取
		if order == 'open':
			file = open(parameter, 'rb')
			text = file.read()
			file.close()
			int_num = len(text)/4
			int_list = struct.unpack('%di'%int_num, text)
			
			field_o = list(int_list)
			
			#地图尺寸
			num = int(len(field_o)/2)
			size = int(math.sqrt(num))
			if size*size == num:
				x = size
				y = size
			else:
				while num % size != 0:
					size -= 1
				y = size
				x = int(num/size)
			
			self.data = []
			for i in range(y):
				self.data.append([])
				for j in range(x):
					self.data[i].append([field_o[2*(i*x+j)], field_o[2*(i*x+j)+1]])
					
		#从二进制导入
		if order == 'bin':
			text = parameter
			int_num = len(text)/4
			int_list = struct.unpack('%di'%int_num, text)
			
			field_o = list(int_list)
			
			#地图尺寸
			num = int(len(field_o)/2)
			size = int(math.sqrt(num))
			if size*size == num:
				x = size
				y = size
			else:
				while num % size != 0:
					size -= 1
				y = size
				x = int(num/size)
			
			self.data = []
			for i in range(y):
				self.data.append([])
				for j in range(x):
					self.data[i].append([field_o[2*(i*x+j)], field_o[2*(i*x+j)+1]])
					
		#从数据生成
		if order == 'create':
			self.data = parameter
			
	def get_bin(self):
		int_list = []
		X, Y = self.size()
		
		for y in range(Y):
			for x in range(X):
				int_list.append(self.data[y][x][0])
				int_list.append(self.data[y][x][1])
				
		num = len(int_list)
		text = struct.pack('%di'%num, *int_list)
		return text
			
	def Save(self, path = ''):
		if path != '' and self.data:
			text = self.get_bin()
			
			file = open(path, 'wb')
			file.write(text)
			file.close()
			
	def size(self):
		if self.data:
			x = len(self.data[0])
			y = len(self.data)
			return (x, y)
			
	def has_value(self):
		size = self.size()
		X = size[0]
		Y = size[1]
		
		for y in range(Y):
			for x in range(X):
				if self.data[y][x][0] != 0:
					return True
		
		return False
			
	def Get_Section(self, rec):
		pos1 = rec[0]
		pos2 = rec[1]
		x1 = pos1[0]
		y1 = pos1[1]
		x2 = pos2[0]
		y2 = pos2[1]
		
		data_new = []
		for y in range(y1, y2+1):
			j = y - y1
			data_new.append([])
			for x in range(x1, x2+1):
				i = x - x1
				data_new[j].append([])
				
				data_new[j][i].append(self.data[y][x][0])
				data_new[j][i].append(self.data[y][x][1])
				
		return data_new
		
	def Cut(self, rec):
		data_new = self.Get_Section(rec)
		self.Fill(rec, 0)
		return data_new
		
	def Copy(self, rec):
		data_new = self.Get_Section(rec)
		return data_new
		
	def Paste(self, pos, data_new):
		x1 = pos[0]
		y1 = pos[1]
		I = len(data_new[0])
		J = len(data_new)
		X = self.size()[0]
		Y = self.size()[1]
		
		for j in range(J):
			y = j + y1
			for i in range(I):
				x = i + x1
				if y < Y and x < X and y >= 0 and x >= 0:
					self.data[y][x][0] = data_new[j][i][0]
					self.data[y][x][1] = data_new[j][i][1]
					
	def Arrow_Transform(self, arrow_num, type = ''):
		def horizonal(num):
			char = [0, 0, 0, 0]
			for i in range(4):
				key_num = 2**(2*i)
				value = num & key_num
				if value:
					char[i] = 1
					
			num_new = num
			for i in range(4):
				offset = 0
				if i%2:
					offset = -2
				else:
					offset = 2
				if char[i]:
					key_num = 2**(2*i + offset)
					num_new = num_new | key_num
				else:
					key_num = 2**8 - 2**(2*i + offset) - 1
					num_new = num_new & key_num
			return num_new
		def vertical(num):
			char = [0, 0, 0, 0]
			for i in range(4):
				key_num = 2**(2*i + 1)
				value = num & key_num
				if value:
					char[i] = 1
					
			num_new = num
			for i in range(4):
				offset = 0
				if i%2:
					offset = -2
				else:
					offset = 2
				if char[i]:
					key_num = 2**(2*i + 1 + offset)
					num_new = num_new | key_num
				else:
					key_num = 2**8 - 2**(2*i + 1 + offset) - 1
					num_new = num_new & key_num
			return num_new
		def cycle(num, command = 'clock'):
			num_new = 0
			if command == 'clock':
				storage = int(num / 8)
				num_new = num << 1
				num_new %= 16
				num_new += storage
				return num_new
			elif command == 'anticlock':
				storage = num % 2
				num_new = num >> 1
				num_new += storage * 8
				return num_new
		def clockwise(num):
			num1 = num % 16
			num2 = num - num1
			num1_new = cycle(num1, 'clock')
			num2_new = cycle(num2, 'clock')
			num_new = num2_new * 16 + num1_new
			return num_new
		def anticlockwise(num):
			num1 = num % 16
			num2 = num - num1
			num1_new = cycle(num1, 'anticlock')
			num2_new = cycle(num2, 'anticlock')
			num_new = num2_new * 16 + num1_new
			return num_new
			
		if type == 'horizonal':
			return horizonal(arrow_num)
		elif type == 'vertical':
			return vertical(arrow_num)
		elif type == 'clockwise':
			return clockwise(arrow_num)
		elif type == 'anticlockwise':
			return anticlockwise(arrow_num)
			
					
	def Horizonal(self):
		X, Y = self.size()
		data_new = []
		for y in range(Y):
			data_new.append([])
			for x in range(X):
				data_new[y].append([])
				data_new[y][x].append(self.data[y][X-x-1][0])
				data_new[y][x].append(self.Arrow_Transform(self.data[y][X-x-1][1], 'horizonal'))
		self.data = data_new
		
	def Vertical(self):
		X, Y = self.size()
		data_new = []
		for y in range(Y):
			data_new.append([])
			for x in range(X):
				data_new[y].append([])
				data_new[y][x].append(self.data[Y-y-1][x][0])
				data_new[y][x].append(self.Arrow_Transform(self.data[Y-y-1][x][1], 'vertical'))
		self.data = data_new
		
	def Clockwise(self):
		X, Y = self.size()
		X_new = Y
		Y_new = X
		data_new = []
		for y in range(Y_new):
			data_new.append([])
			for x in range(X_new):
				data_new[y].append([])
				data_new[y][x].append(self.data[Y-x-1][y][0])
				data_new[y][x].append(self.Arrow_Transform(self.data[Y-x-1][y][1], 'clockwise'))
		self.data = data_new
		
	def AntiClockwise(self):
		X, Y = self.size()
		X_new = Y
		Y_new = X
		data_new = []
		for y in range(Y_new):
			data_new.append([])
			for x in range(X_new):
				data_new[y].append([])
				data_new[y][x].append(self.data[x][X-y-1][0])
				data_new[y][x].append(self.Arrow_Transform(self.data[x][X-y-1][1], 'anticlockwise'))
		self.data = data_new
		
	def Free(self, command):
		if command == 'clockwise':
			self.Clockwise()
		elif command == 'anticlockwise':
			self.AntiClockwise()
		elif command == 'vertical':
			self.Vertical()
		elif command == 'horizonal':
			self.Horizonal()
			
	def Point_IsVoid(self, pos):
		x = pos[0]
		y = pos[1]
		old_panel = self.data[y][x][0]
		
		if old_panel == 0 or old_panel == 18:
			return True
		return False
			
	def Point_Panel(self, pos, panel_id, setting = 'Default'):
		
		x = pos[0]
		y = pos[1]
		old_panel = self.data[y][x][0]
		old_arrow = self.data[y][x][1]
		
		self.data[y][x][0] = panel_id
		if setting == 'Default':
			if panel_id == 0 or panel_id == 18:
				self.data[y][x][1] = 0
		
		if old_panel != self.data[y][x][0] or old_arrow != self.data[y][x][1]:
			return True
		else:
			return False
			
	def Point_Arrow(self, pos, arrow_command = [0,0,0,0], BackTrack = 0):
		
		x = pos[0]
		y = pos[1]
		old_arrow = self.data[y][x][1]
		
		new_arrow = old_arrow
		
		def If_Arrow(arrow, index):
			return int(arrow / (2**index)) % 2
			
		def Change_Arrow(arrow, index, command):
			new_arrow = arrow
			if command == 1 and not If_Arrow(arrow, index):
				new_arrow += 2**index
			elif command == -1 and If_Arrow(arrow, index):
				new_arrow -= 2**index
				
			return new_arrow
		
		Back_Index = 0
		if BackTrack:
			Back_Index = 4
			
		for i in range(4):
			index = i + Back_Index
			new_arrow = Change_Arrow(new_arrow, index, arrow_command[i])
			
		self.data[y][x][1] = new_arrow
		
		if old_arrow != new_arrow:
			return True
		else:
			return False
			
	def Fill(self, rec, panel_id, BackTrack = 0):
		pos1 = rec[0]
		pos2 = rec[1]
		x1 = pos1[0]
		y1 = pos1[1]
		x2 = pos2[0]
		y2 = pos2[1]
		
		for y in range(y1, y2+1):
			for x in range(x1, x2+1):
				if panel_id < 100:
					self.data[y][x][0] = panel_id
				if panel_id == 0 or panel_id == 18:
					self.data[y][x][1] = 0
				if panel_id == 101:
					self.Point_Arrow((x,y), [-1,-1,-1,-1], BackTrack)
			
		return True
			
			
			
			
			
			
			
			
