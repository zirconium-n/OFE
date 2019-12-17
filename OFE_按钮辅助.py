#按钮辅助

Button_name = ['Void', 'Check', 'Bonus', 'Bonus_2', 'Drop', 'Drop_2',
			'Encounter', 'Encounter_2', 'Draw', 'Draw_2', 'Move', 'Move_2',
			'WarpMove', 'WarpMove_2', 'Warp', 'Snow', 'Neutral', 'Deck']
			

			
			
#开始
text = ''

for id in range(18):
	text += 'self.brush_list[' +str(id) + '].clicked.connect(lambda: self.Brush_Click(' + str(id) + '))' + '\n'

print(text)