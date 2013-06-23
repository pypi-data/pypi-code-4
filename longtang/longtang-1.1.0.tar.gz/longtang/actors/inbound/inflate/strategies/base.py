import os

class PumpingStrategy:
	def open(self, filepath):
		pass

	def inflate_at(self, file_ref, target_path):
		pass

class InflatedFileReference:
	def close(self):
		pass

	def ref(self):
		pass

class BaseInflateDefails:
	def __init__(self, inflated_at):
		self.__inflated_at=inflated_at

	def entries(self):
		for root, dirnames, filenames in os.walk(self.__inflated_at):
			for filename in filenames:
				yield os.path.join(root, filename)

class FileCouldNotBeOpenException(Exception):
	def __init__(self, filename, msg=None):
		self.__filename = filename
		self.__msg = msg		

	def __str__(self):
		return repr("File '{0}' could not be open. Reason: {1}".format(self.__filename, self.__msg if self.__msg is not None else ''))

	def filename(self):
		return self.__filename

class InflateException(Exception):
	def __init__(self, filename, msg=None):
		self.__filename = filename
		self.__msg = msg		

	def __str__(self):
		return repr("File '{0}' could not be inflated. Reason: {1}".format(self.__filename, self.__msg if self.__msg is not None else ''))

	def filename(self):
		return self.__filename		