import abc

class Package(object):
	__metaclass__ = abc.ABCMeta

	@abc.abstractproperty
	def name(self):
		pass

	@abc.abstractproperty
	def version(self):
		pass

	@abc.abstractproperty
	def dependencies(self):
		pass

	# payload = None

	# @abc.abstractmethod
	# def validate(self):
	# 	"""Check if the payload of the package matches it's required template"""
	# 	pass

	@abc.abstractmethod
	def __init__(self, path):
		pass

	@abc.abstractmethod
	def install(self):
		pass

	@abc.abstractmethod
	def uninstall(self):
		pass


class PythonScriptPackage(Package):
	name = 'hello'
	version = '0.1.0'
	dependencies = []

	def install(self):
		pass

	def uninstall(self):
		pass


if __name__ == '__main__':
	p = PythonScriptPackage()
