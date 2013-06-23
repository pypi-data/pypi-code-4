import os
import tempfile

from longtang.actors.inbound.inflate.strategies.registry import available_formats

class PumpingClerkFactory:

	@staticmethod
	def from_file(filepath):
		filename, fileext_original = os.path.splitext(filepath.lower())

		fileext = fileext_original[1:]

		if fileext in available_formats:
			return PumpingClerk(filepath, available_formats[fileext])
		else:
			class PumpingClerkNotAvailable(Exception):
				pass
			
			raise PumpingClerkNotAvailable('Pumping clerk for type \'{0}\' not found'.format(fileext))

class PumpingClerk:
	def __init__(self, filepath, pump_strategy):
		self.__filepath=filepath
		self.__strategy=pump_strategy
		self.__inflate_details=None

	def inflate(self):
		file_ref = self.__strategy.open(self.__filepath)
		self.__inflate_details = self.__strategy.inflate_at(file_ref, tempfile.mkdtemp(prefix=u'pump_'))
		file_ref.close()

		return self

	def entries(self):
		return self.__inflate_details.entries()