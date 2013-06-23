import hashlib
import sys

class MessageTrackingGenerator:

	@staticmethod
	def generate(message):
		return MessageTrackingGenerator.__create_id(message.sourcepath())

	@staticmethod
	def generate_parent(message):
		return MessageTrackingGenerator.__create_id(message.parent_sourcepath())

	@staticmethod
	def __create_id(from_value):
		return hashlib.sha224(from_value.encode(sys.getdefaultencoding(),'replace')).hexdigest()