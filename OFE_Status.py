from PyQt5 import QtGui, QtWidgets, QtCore

class StatusWindow(QtWidgets.QWidget):
	def __init__(self, parent = None):
		QtWidgets.QWidget.__init__(self, parent)
		
		#初始化
		self.Status = {}
		#初始参数
		self.Status['History_Len'] = 0
		self.Status['History_Pos'] = 1
		self.Status['Last_Action'] = 'None'
		self.Status['Selected'] = []
		self.Status['Button'] = 18
		self.Status['BackTrack'] = 0
		
		self.Status['Test'] = ''
		
		#主框架
		layout_main = QtWidgets.QVBoxLayout()
		
		#主文本
		self.label_main = QtWidgets.QLabel(self)
		self.label_main.setText('test') 
		
		layout_main.addWidget(self.label_main)
		self.setLayout(layout_main)
		
	def A_Status(self, command):
		
		for key in command:
			self.Status[key] = command[key]
			
		self.Text_Refresh()
		
	def Status_Refresh(self):
		self.Text_Refresh()
		
	def Text_Refresh(self):
	
		text = ''
		# text += '--------Status--------' + '\n'
		###Command
		text += '----Command----' + '\n'
		#last action
		text += 'Last Action : '
		last_action = self.Status['Last_Action']
		text += last_action
		text += '\n'
		#Selected
		text += 'Selected : '
		selected = self.Status['Selected']
		if selected == []:
			text += 'None'
		else:
			x = selected[1][0] - selected[0][0] +1
			y = selected[1][1] - selected[0][1] +1
			text += str(x) + ' x ' + str(y)
			text += '; '
			text += str(selected[0]) + '-' + str(selected[1])
		text += '\n'
		#button
		text += 'Button : '
		button_id = self.Status['Button']
		Button_Name = ['Void', 'Check', 'Bonus', 'Bonus_2', 'Drop', 'Drop_2', 'Encounter', 'Encounter_2', 'Draw', 'Draw_2', 
				'Move', 'Move_2', 'WarpMove', 'WarpMove_2', 'Warp', 'Snow', 'Neutral', 'Deck'] + ['Mouse', 'ArrowDelete', 'ArrowLine', 'ArrowLineDelete', 'OK', 'Cancel']
		text += Button_Name[button_id]
		text += '\n'
		
		###View
		text += '----View----' + '\n'
		#backtrack
		text += 'BackTrack : '
		backtrack = self.Status['BackTrack']
		if backtrack:
			text += 'On'
		else:
			text += 'Off'
		text += '\n'
		
		###Parameter
		text += '----Parameter----' + '\n'
		#history
		text += 'History : '
		history_now = self.Status['History_Len']-self.Status['History_Pos']
		history_abs = self.Status['History_Len'] - 1
		text += str(history_now)
		if history_now != history_abs:
			text += '('+str(history_abs)+')'
		text += '\n'
		
		###Test
		text += '----Test----' + '\n'
		test = self.Status['Test']
		text += test
		text += '\n'
		
		self.label_main.setText(text)
		
		
		
		