Panel_Name = ['Void', 'Neutral', 'Check', 'Encounter', 'Draw', 'Bonus', 'Drop', 'Warp', 'Draw_2', 'Bonus_2', 'Drop_2', 'Deck', 
	'Encounter_2', 'Move', 'Move_2', 'WarpMove', 'WarpMove_2', 'Snow', 'Ice', 'Heal', 'Heal_2','Boss','Damage','Damage_2']
Panel_Int = [0,1,2,3,4,5,6,7,8,9,10,18,20,21,22,23,24,25,26,27,28,31,32,33]
Button_Brush_Int = [0,2,5,9,6,10,3,20,4,8,21,22,23,24,7,25,1,18,26,27,28,31,32,33]

assert(len(Panel_Name) == len(Panel_Int))
assert(len(Panel_Name) == len(Button_Brush_Int))