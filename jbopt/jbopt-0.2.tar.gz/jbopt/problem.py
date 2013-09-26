

class Problem(object):
	start = None
	ndim = None
	def transform(self, cube):
		params = cube
		return params
	def likelihood(self, params):
		return -params**2
	def prior(self, params):
		return 0
	def viz(self, params):
		return
	def output(self, params):
		print 'candidate:', params


