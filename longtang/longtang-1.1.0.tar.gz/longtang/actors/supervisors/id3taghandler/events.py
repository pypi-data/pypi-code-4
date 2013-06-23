from longtang.common.mediatracking import events as mt_events

class MetadataAvailable(mt_events.MediaFileTrackingEvent):
	def __init__(self):
		mt_events.MediaFileTrackingEvent.__init__(self, "METADATA_AVAILABLE", "Metadata is fully available")

class MetadataNotAvailable(mt_events.MediaFileTrackingEvent):
	def __init__(self):
		mt_events.MediaFileTrackingEvent.__init__(self, "METADATA_NOT_AVAILABLE_FAILURE", "Metadata could not be completed")

class MetadataEvaluationFailed(mt_events.MediaFileTrackingEvent):
	def __init__(self):
		mt_events.MediaFileTrackingEvent.__init__(self, "METADATA_EVALUATION_FAILURE", "Metadata could not be evaluated from file")		

class MetadataInspectionStarted(mt_events.MediaFileTrackingEvent):
	def __init__(self):
		mt_events.MediaFileTrackingEvent.__init__(self, "METADATA_INSPECTION_STARTED", "Metadata inspection from file started")

class FileMetadataIncomplete(mt_events.MediaFileTrackingEvent):
	def __init__(self):
		mt_events.MediaFileTrackingEvent.__init__(self, "FILE_METADATA_INCOMPLETE", "Metadata is incomplete. Trying MusicBrainz")

class MusicbrainzServiceFailed(mt_events.MediaFileTrackingEvent):
	def __init__(self):
		mt_events.MediaFileTrackingEvent.__init__(self, "MUSICBRAINZ_SERVICE_FAILURE", "Musicbrainz service is not responding")	
