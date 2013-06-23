from longtang.actors import messages

class StartPolling(messages.ActorMessage):

	def __init__(self, source):
		messages.ActorMessage.__init__(self)
		self.__source=source

	def source(self):
		return self.__source

class FilePollingDone(messages.ActorMessage):
	def __init__(self):
		messages.ActorMessage.__init__(self)	

class AudioFileFound(messages.ActorMessage):

	def __init__(self, full_filepath):
		self.__full_filepath = full_filepath

	def filepath(self):
		return self.__full_filepath

class CompressedAudioFileFound(AudioFileFound):
	def __init__(self, full_filepath, compressed_parent_filepath):
		AudioFileFound.__init__(self, full_filepath)
		self.__compressed_parent_filepath=compressed_parent_filepath

	def compressed_parent_filepath(self):
		return self.__compressed_parent_filepath

class CompressedFileCouldNotBeOpened(messages.ActorMessage):
	def __init__(self, filepath):
		self.__filepath=filepath

	def filepath(self):
		return self.__filepath
