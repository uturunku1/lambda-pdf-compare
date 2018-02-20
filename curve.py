from pdfobj import PDFObj

class Curve(PDFObj):
	pts = ''

	def __init__(self, curve, page):
		self.setPts(curve)
		super().__init__(curve['bbox'], page)

	def setPts(self, curve):
		try:
			self.pts = curve['pts']
		except Exception:
			pass
		return self.pts