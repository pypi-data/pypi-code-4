class MediaFileTrackingEvent():

	def __init__(self, entry_type, description, context_information={}):
		self.__type=entry_type
		self.__description=description
		self.__context_info=context_information

	def type(self):
		return self.__type

	def description(self):
		return self.__description

	def context_information(self):
		return self.__context_info

	def process(self, file_descriptor):
		return file_descriptor

class CompressedAudioFileFound(MediaFileTrackingEvent):
	def __init__(self, tracking_id):
		MediaFileTrackingEvent.__init__(self, "COMPRESSED_AUDIOFILE_FOUND", "Related compressed audio file found")
		self.__tracking_id=tracking_id

	def process(self, file_descriptor):
		file_descriptor.audiofiles.append(self.__tracking_id)
		return file_descriptor

class FileCouldNotBeInflated(MediaFileTrackingEvent):		
	def __init__(self):
		MediaFileTrackingEvent.__init__(self, "INFLATE_PROCESS_FAILURE", "File could not be inflated")

	def process(self, file_descriptor):
		file_descriptor.inflated=False
		return file_descriptor	