from longtang.actors import messages

class InflateFile(messages.ActorMessage):

	def __init__(self, filepath):
		messages.ActorMessage.__init__(self)
		self.__filepath=filepath

	def filepath(self):
		return self.__filepath

class InflatedFileAvailable(messages.ActorMessage):

	def __init__(self, filepath, parent):
		messages.ActorMessage.__init__(self)
		self.__filepath=filepath
		self.__parent=parent

	def filepath(self):
		return self.__filepath		

	def parent_filepath(self):
		return self.__parent

class InflateFileDone(messages.ActorMessage):

	def __init__(self, filepath):
		messages.ActorMessage.__init__(self)
		self.__filepath=filepath

	def filepath(self):
		return self.__filepath

class InflateFileFailed(messages.ActorMessage):

	def __init__(self, filepath):
		messages.ActorMessage.__init__(self)
		self.__filepath=filepath

	def filepath(self):
		return self.__filepath