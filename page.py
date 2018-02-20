from pdfobj import PDFObj

class Page(PDFObj):
	def __init__(self, page, page_num):
		super().__init__(page['bbox'], page_num)