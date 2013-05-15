
################################################################################

from types import ModuleType

################################################################################

# A Class to simulate dynamic inheritance
# Allows to change behaviour of multiple modules or classes, with the same
	# interface
# Note: Class wrapping not tested
class GenericWrapper:

	# object_to_wrap can be:
	# A Module
	# A Class Instance
	def __init__(self, object_to_wrap):
		if isinstance(object_to_wrap, ModuleType):
			self.is_module = True
		elif isinstance(object_to_wrap, object):
			self.is_module = False
		else:
			raise TypeError("Expected a Module or a Class Instance")
		self.object_to_wrap = object_to_wrap

	# Fallback lookup for undefined methods
	def __getattr__(self, name):
		if self.is_module:
			return self.object_to_wrap.__dict__[name]
		else:
			return self.object_to_wrap.__getattr__(name)

################################################################################
