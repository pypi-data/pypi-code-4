from longtang.common.mediatracking import events as mt_events

class FilePackagingFinished(mt_events.MediaFileTrackingEvent):
	def __init__(self, packaged_file):
		mt_events.MediaFileTrackingEvent.__init__(self, "FILE_PACKAGING_DONE", "File has been successfully packaged")
		self.__packaged_file=packaged_file

	def process(self, file_descriptor):

		file_descriptor.destinationpath=self.__packaged_file
		return file_descriptor

class FileCopyFailed(mt_events.MediaFileTrackingEvent):
	def __init__(self):
		mt_events.MediaFileTrackingEvent.__init__(self, "FILE_COPY_FAILURE", "File could not be copied")

class FolderCreationFailed(mt_events.MediaFileTrackingEvent):
	def __init__(self):
		mt_events.MediaFileTrackingEvent.__init__(self, "FOLDER_CREATION_FAILURE", "Target folder could not be created")

class MetadataWritingFailed(mt_events.MediaFileTrackingEvent):
	def __init__(self):
		mt_events.MediaFileTrackingEvent.__init__(self, "METADATA_WRITING_FAILURE", "Metadata could not be persisted")

class PackagingStarted(mt_events.MediaFileTrackingEvent):
	def __init__(self):
		mt_events.MediaFileTrackingEvent.__init__(self, "PACKAGING_STARTED", "File packaging process started")
		
class TargetFolderCreated(mt_events.MediaFileTrackingEvent):
	def __init__(self):
		mt_events.MediaFileTrackingEvent.__init__(self, "TARGET_FOLDER_CREATED", "Target folder created")

class MediaFileCopied(mt_events.MediaFileTrackingEvent):
	def __init__(self):
		mt_events.MediaFileTrackingEvent.__init__(self, "MEDIAFILE_COPIED", "Media file copied")

class MetadataUpdated(mt_events.MediaFileTrackingEvent):
	def __init__(self):
		mt_events.MediaFileTrackingEvent.__init__(self, "METADATA_UPDATED", "Media file metadata updated")

class FileRenamingFailed(mt_events.MediaFileTrackingEvent):
	def __init__(self):
		mt_events.MediaFileTrackingEvent.__init__(self, "FILE_RENAMING_FAILURE", "Media file renaming process failed")

