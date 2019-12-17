import os
from PIL import Image

class OFE_Graphics:
	def __init__(self, zoom_list, path):
		
		#初始化
		self.zoom_list = zoom_list
		#将path目录下所有文件（不包含其下级目录），若能打开，全部存入。
		print('[Loading images...]')
		self.img_o_dict = {}
		bad_img = []
		for file_name in os.listdir(path):
			try:
				img = Image.open(path + '\\' + file_name)
			except:
				bad_img.append(file_name)
			else:
				dot_pos = file_name.index('.')
				name = file_name[:dot_pos]
				self.img_o_dict[name] = img
		#汇报加载结果
		img_count = len(self.img_o_dict)
		print(img_count, 'images have been loaded.')
		for file_name in bad_img:
			print('Warning: ' + file_name + ' is not a image')
			
		#将不同zoom level的图生成出来
		print('[Creating zooming images...]')
		self.img_zoom_dict = self.Img_Zoom(self.img_o_dict, zoom_list)
		
		#汇报生成的zoom总计
		print(zoom_list, 'zoom levels have been created')
		
	def get_image(self, name, zoom = 1.0):
		try:
			img = self.img_zoom_dict[name][zoom]
		except:
			if not name in self.img_zoom_dict:
				print('Error: ', name, ' is not in graphics')
			if not zoom in self.zoom_list:
				print('Error: ', zoom, ' is not in zoom_list')
		else:
			return img
		
	def Img_Zoom(self, img_o_dict, zoom_list):
		new_dict = {}
		PX = 128
		for name in img_o_dict:
			new_dict[name] = {}
			img = img_o_dict[name]
			for zoom in zoom_list:
				px = int(PX * zoom)
				img_new = img.resize((px,px), Image.BICUBIC)
				new_dict[name][zoom] = img_new
				
		return new_dict
			
		
		
		
if __name__ == '__main__':
	graphics = OFE_Graphics([0.5, 0.75], r'D:\OneDrive\个人\100oj\橙汁地图编辑器\OFE正式v1.0\panels')
	graphics.get_image('Panel_Bonus', 0.5)