from errors import Error500


class HTTPContext(object):
	def __enter__(self):
		pass
	
	def __exit__(self, e_type, e_value, e_tb):
		if e_type is not None:
			raise Error500
			return True