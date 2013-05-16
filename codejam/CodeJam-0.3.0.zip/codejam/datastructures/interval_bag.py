import collections as co

class interval_bag:
	_intervals = co.defaultdict(int)
	_root = None
	_size = 1
	
	def __init__(self, n = 1):
		self._size = n
		self._root = _interval_bag_node(0, self._size, None)
	
	def add(self, r):
		while r[1] >= self._size:
			self._double_size()
		self._intervals[r] += 1
		self._root.add(r[0], r[1] + 1, 1)
		
	def remove(self, r):
		if r not in self._intervals:
			raise ValueError()
		self._intervals[r] -= 1
		self._root.add(r[0], r[1] + 1, -1)
	
	def covered_length(self):
		return self._root.covered
		
	def __iadd__(self, x):
		for r in x:
			self.add(r)
		return self
	
	def _double_size(self):
		old_root, old_size = self._root, self._size
		self._size <<= 1
		self._root = _interval_bag_node(0, self._size, None, False)
		self._root.covered = old_root.covered
		old_root.p = self._root
		self._root.l = old_root
		self._root.r = _interval_bag_node(old_size, self._size, self._root)
	
	def __repr__(self):
		values = sum([[k] * self._intervals[k] for k in self._intervals], [])
		strings = ['(%i, %i)' % (a, b) for (a, b) in values]
		return '[' + ', '.join(strings) + ']'
		
class _interval_bag_node:
	p, l, r = None, None, None
	depth, covered, s, e = 0, 0, 0, 0
	
	def __init__(self, a, b, parent, add_children = True):
		self.s, self.e, self.p = a, b, parent
		if add_children and a < b - 1:
			self.l = _interval_bag_node(a, (a + b) / 2, self)
			self.r = _interval_bag_node((a + b) / 2, b, self)
	
	def add(self, a, b, v):
		if a < b:
			if self.s == a and self.e == b:
				self.depth += v
				self.recalc()
			else:
				self.l.add(a, min(b, self.l.e), v)
				self.r.add(max(a, self.r.s), b, v)
				
	def recalc(self):
		if self.depth > 0:		self.covered = self.e - self.s
		elif self.l != None:	self.covered = self.l.covered + self.r.covered
		else:					self.covered = 0
		if self.p != None:		self.p.recalc()