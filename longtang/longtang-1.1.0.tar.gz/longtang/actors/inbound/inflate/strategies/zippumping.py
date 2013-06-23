import base
import zipfile


class ZipPumpingStrategy(base.PumpingStrategy):
	def open(self, filepath):
		try:
			return ZipFileReference(zipfile.ZipFile(filepath, 'r'))
		except Exception, e:
			raise base.FileCouldNotBeInflatedException(filepath, str(e))

	def inflate_at(self, file_ref, target_path):
		try:
			file_ref.ref().extractall(target_path)
			return base.BaseInflateDefails(target_path)
		except Exception, e:
			raise base.InflateException(target_path, str(e))

class ZipFileReference(base.InflatedFileReference):
	def __init__(self, zipfile):
		self.__zipfile=zipfile

	def close(self):
		self.__zipfile.close()

	def ref(self):
		return self.__zipfile
