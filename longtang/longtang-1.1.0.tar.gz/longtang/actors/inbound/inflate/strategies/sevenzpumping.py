#http://docs.python.org/2/library/subprocess.html#frequently-used-arguments
#7z x pump_3CL0Nm.7z -o./test

import base
import subprocess

class SevenzPumpingStrategy(base.PumpingStrategy):
	def open(self, filepath):
		try:
			return SevenzFileReference(filepath)
		except Exception, e:
			raise base.FileCouldNotBeOpenException(filepath, str(e))

	def inflate_at(self, file_ref, target_path):
		try:
			captured_output = subprocess.check_output(["7z", "x", file_ref.ref(), "-o" + target_path])
			return base.BaseInflateDefails(target_path)
		except subprocess.CalledProcessError, e:
			raise base.InflateException(target_path, str(e))

class SevenzFileReference(base.InflatedFileReference):
	def __init__(self, sevenz_file):
		self.__7z_file=sevenz_file

	def close(self):
		pass

	def ref(self):
		return self.__7z_file