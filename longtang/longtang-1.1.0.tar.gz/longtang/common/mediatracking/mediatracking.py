class MediaFileTracking():
	def __init__(self, descriptor):
		self.__descriptor=descriptor
		self.__events_container=TrackingEventsProcessor([])

	@staticmethod
	def create_from(descriptor):
		return MediaFileTracking(descriptor)

	@property
	def mediafile(self):
		return self.__descriptor

	@property
	def tracking_events(self):
		return self.__events_container.events_registry()

	def track_activity(self, track_event):
		self.__descriptor = self.__events_container.process(self.__descriptor, track_event)

class FileDescriptor:
	def __init__(self):
		self.__sourcepath=None
		self.__destinationpath=None

	@property
	def sourcepath(self):
		return self.__sourcepath

	@sourcepath.setter
	def sourcepath(self, value):
		self.__sourcepath=value

class AudioFileDescriptor(FileDescriptor):
	def __init__(self):
		FileDescriptor.__init__(self)
		self.__destinationpath=None

	@property
	def destinationpath(self):
		return self.__destinationpath

	@destinationpath.setter
	def destinationpath(self, value):
		self.__destinationpath=value

class CompressedAudioFileDescriptor(AudioFileDescriptor):
	def __init__(self):
		AudioFileDescriptor.__init__(self)
		self.__compressed_file=None

	@property
	def compressed_file(self):
		return self.__compressed_file

class CompressedFileDescriptor(FileDescriptor):
	def __init__(self):
		FileDescriptor.__init__(self)
		self.__audiofiles=[]
		self.__inflated=True

	@property
	def audiofiles(self):

		class AudioFilesBrowser:
			def __init__(self, audiofiles):
				self.__audiofiles = audiofiles

			def size(self):
				return len(self.__audiofiles)

			def append(self, related_tracking_id):
				self.__audiofiles.append(related_tracking_id)

			def all(self):
				return self.__audiofiles

		return AudioFilesBrowser(self.__audiofiles)

	@property
	def inflated(self):
		return self.__inflated

	@inflated.setter
	def inflated(self, value):
		self.__inflated=value

class AudioFileDescriptorBuilder:
	def __init__(self):
		self.__sourcepath=None

	def sourcepath(self, sourcepath):
		self.__sourcepath=sourcepath
		return self

	def build(self):
		descriptor=AudioFileDescriptor()
		descriptor.sourcepath=self.__sourcepath

		return descriptor

class CompressedAudioFileDescriptorBuilder:
	def __init__(self):
		self.__compressed_file_id=None
		self.__sourcepath=None

	def sourcepath(self, sourcepath):
		self.__sourcepath=sourcepath
		return self

	def compressed_file(self, compressed_file_tracking_id):
		self.__compressed_file_id=compressed_file_tracking_id
		return self

	def build(self):
		descriptor=CompressedAudioFileDescriptor()
		descriptor.sourcepath=self.__sourcepath
		descriptor.compressed_file=self.__compressed_file_id

		return descriptor		

class CompressedFileDescriptorBuilder:
	def __init__(self):
		self.__sourcepath=None

	def sourcepath(self, sourcepath):
		self.__sourcepath=sourcepath
		return self

	def build(self):
		descriptor=CompressedFileDescriptor()
		descriptor.sourcepath=self.__sourcepath

		return descriptor

class TrackingEventsBrowser:
	def __init__(self, entries):
		self.__tracking_groups={}
		self.__tracking_entries=entries

		self.__group_entries(entries)

	def __group_entries(self, entries):
		for entry in entries:
			self.__assign_event_to_group(entry)

	def __assign_event_to_group(self, tracking_entry):
		if self.__tracking_groups.has_key(tracking_entry.type()):
			self.__tracking_groups[tracking_entry.type()].append(tracking_entry)
		else:
			self.__tracking_groups[tracking_entry.type()]=[tracking_entry]			

	def size(self):
		return len(self.__tracking_entries)

	def is_empty(self):
		return self.size() == 0

	def all(self):
		return TrackingEventsBrowser(self.__tracking_entries)

	def get(self, index):
		return self.__tracking_entries[index]

	def of_type(self, event_type):
		if self.__tracking_groups.has_key(event_type):
			return TrackingEventsBrowser(self.__tracking_groups[event_type])
		else:
			return TrackingEventsBrowser([])

	def __iter__(self):
		return iter(self.__tracking_entries)

class TrackingEventsProcessor():
	def __init__(self, entries):
		self.__tracking_entries=entries

	def process(self, current_descriptor, tracking_entry):
		self.__tracking_entries.append(tracking_entry)
		return tracking_entry.process(current_descriptor)

	def events_registry(self):
		return TrackingEventsBrowser(self.__tracking_entries)
