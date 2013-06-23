import base
import rarfile

class RarPumpingStrategy(base.PumpingStrategy):
	def open(self, filepath):
		try:
			return RarFileReference(rarfile.RarFile(filepath, 'r'))
		except Exception, e:
			raise base.FileCouldNotBeInflatedException(filepath, str(e))

	def inflate_at(self, file_ref, target_path):
		try:
			file_ref.ref().extractall(target_path)
			return base.BaseInflateDefails(target_path)
		except Exception, e:
			raise base.InflateException(target_path, str(e))

class RarFileReference(base.InflatedFileReference):
	def __init__(self, rar_file):
		self.__rarfile=rar_file

	def close(self):
		self.__rarfile.close()

	def ref(self):
		return self.__rarfile