class PDFObj(object):
	page = 0
	bbox = ''
	x1 = 0.0
	y1 = 0.0
	x2 = 0.0
	y2 = 0.0
	dpi = 96.0
	offsetstart = 0
	offsetend = 0
	offsetdiff = 0
	start = 0
	end = 0
	diff = 0

	def __init__(self, bbox='0,0,0,0', page=0):
		self.page = page
		self.setBBOX(bbox)

	def setBBOX(self, bbox):
		try:
			self.bbox = bbox
			(self.x1, self.y1, self.x2, self.y2) = bbox.split(',')
			self.x1 = float(self.x1)
			self.y1 = float(self.y1)
			self.x2 = float(self.x2)
			self.y2 = float(self.y2)
		except Exception:
			pass

	def toPTS(self):
		return (self.x1, self.y1, self.x2, self.y2)

	def toPX(self):
		return (self.ptToPX(self.x1), self.ptToPX(self.y1), self.ptToPX(self.x2), self.ptToPX(self.y2))

	def pxToPT(self, px):
		return int(px * 3 / 4)

	def ptToPX(self, pt):
		return int(pt * 4 / 3)

	def sort_data(self,data,desc_flag):
		for i in range(len(data)-1):
			for j in range(i+1,len(data)):
				if ((int(data[i]['y1']) < int(data[j]['y1']) and desc_flag) or (int(data[i]['y1']) > int(data[j]['y1']) and not desc_flag)):
					tmp = data[i]
					data[i] = data[j]
					data[j] = tmp
		return data

	def set_offsets(self,offsets):
		if(len(offsets)>0):
			self.offsetstart = offsets[0]
			self.offsetend = offsets[1]
			self.offsetdiff = int(self.offsetend)-int(self.offsetstart)
			self.start = self.ptToPX(int(offsets[2]))
			self.end = self.ptToPX(int(offsets[3]))
			self.diff = int(self.start)-int(self.end)

	def calculate_offset(self,y1,y2):
		difference = int(self.start)-int(y1)
		step = float((int(difference)*int(self.offsetdiff ))/int(self.diff))
		y_offset = int(int(self.offsetstart)+float(step))
		# print(y_offset,'\t',y1,'\t',y2)
		y1 = int(y1)-int(y_offset)
		y2 = int(y2)-int(y_offset)
		return (y1,y2)

	# def __str__(self):
	# 	return str(dict(self))
	def __repr__(self):
		return str(self.__class__) + str(self.__dict__)
