from math import ceil

class Paginator():
	def __init__(self, query, per_page):
		self.query = query
		self.per_page = float(per_page)
		self.obj_count = self._count()
		self.nb_pages = self._pages()

	def _count(self):
		return int(self.query.count())


	def _pages(self):
		return int(ceil(self.obj_count/self.per_page))

	def page(self, page_num):
		return Page(self, page_num)

	def page_exists(self, page_num):
		if 0 < page_num <= self.nb_pages:
			return True
		else:
			return False

class Page():
	def __init__(self, paginator, num):
		self.paginator = paginator
		self.num = num
		self.total_pages = paginator.nb_pages
		self.query = paginator.query.paginate(self.num, paginator.per_page)

	def next_page(self):
		return self._page_exists(self.num + 1)

	def previous_page(self):
		return self._page_exists(self.num - 1)

	def _page_exists(self, page):
		if 0 < page <= self.total_pages:
			return page
		else:
			return False

	def objects(self):
		return self.query

