class summing_list:
	layers = [[0]]
	size = 0
	
	def __init__(self, iter = None):
		if iter != None:
			for i in iter:
				self.append(i)

	def _sum(self, i):
		t = 0
		for r in self.layers:
			if i % 2:
				t += r[i - 1]
			i >>= 1
		return t
		
	def sum_elements(self, i = None, j = None):
		if j == None:
			if i == None:
				i = self.size
			return self._sum(i)
		else:
			return self._sum(max(i, j)) - self._sum(min(i, j))
				
	def __getitem__(self, i):
		if i < self.size:
			return self.layers[0][i]
		else:
			raise ValueError()
		
	def __setitem__(self, i, v):
		d = v - self.layers[0][i]
		for r in self.layers:
			r[i] += d
			i >>= 1
	
	def _double_size(self):
		for r in self.layers:
			r += [0] * len(r)
		self.layers += [[self.layers[-1][0]]]
	
	def __iadd__(self, iter):
		for i in iter:
			self.append(i)
		return self
		
	def __add__(self, x):
		both = summing_list(self)
		both += x
		return both
	
	def append(self, x):
		self.size += 1
		if self.size > len(self.layers[0]):
			self._double_size()
		self[self.size - 1] = x
		
	def __repr__(self):
		return self.layers[0][:self.size].__repr__()
		
	def __iter__(self):
		return iter(self.layers[0][:self.size])
