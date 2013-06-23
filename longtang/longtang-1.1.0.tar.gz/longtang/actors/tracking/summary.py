from longtang.common.mediatracking import mediatracking

class ActivitySummary():

	def __init__(self, tracking_info, compressed_files_info):
		self.__tracking_info=tracking_info
		self.__compressed_files_info=compressed_files_info

	@staticmethod
	def create(tracking_info, compressed_files_info):
		return ActivitySummary(tracking_info, compressed_files_info)

	def compressed(self):
		return ActivityEntriesClassifier(self.__compressed_files_info)

	def audio(self):
		return ActivityEntriesClassifier(self.__tracking_info)

class ActivityEntriesBrowser():

	def __init__(self, entries):
		self.__entries=entries

	def total(self):
		return len(self.__entries)

	def all(self):
		return self.__entries

	def find(self, tracking_id):
		#I think I need to review go to perform this instead of linear cost
		result = [entry for entry in self.__entries if entry[0] is tracking_id]

		if len(result) > 0:
			return result[0]
		else:
			None

class ActivityEntriesClassifier():

	def __init__(self, tracking_info):
		self.__tracking_info=tracking_info

	def total(self):
		return len(self.__tracking_info)

	def __is_failure(self, event):
		return 'FAILURE' in event.type()

	def __is_success(self, event):
		return not self.__is_failure(event)

	def __mediafile_failed(self, mediafile_tracking):
		for event in mediafile_tracking.tracking_events:
			if self.__is_failure(event):
				return True

		return False

	def __is_compressed_audio(self, mediafile_tracking):
		return isinstance(mediafile_tracking.mediafile, mediatracking.CompressedAudioFileDescriptor)

	def successes(self, include_compressed=True):

		successful_file_criteria=lambda mediatracking_info: not self.__mediafile_failed(mediatracking_info[1])
		non_compressed_successful_files_criteria=lambda mediatracking_info: successful_file_criteria(mediatracking_info) and not self.__is_compressed_audio(mediatracking_info[1])

		if include_compressed:
			entries=filter(successful_file_criteria,self.__tracking_info.items())
		else:
			entries=filter(non_compressed_successful_files_criteria,self.__tracking_info.items())

		return ActivityEntriesBrowser(entries)

	def failures(self, include_compressed=True):
		failed_file_criteria=lambda mediatracking_info: self.__mediafile_failed(mediatracking_info[1])
		non_compressed_successful_files_criteria=lambda mediatracking_info: failed_file_criteria(mediatracking_info) and not self.__is_compressed_audio(mediatracking_info[1])

		if include_compressed:
			entries=filter(failed_file_criteria,self.__tracking_info.items())
		else:
			entries=filter(non_compressed_successful_files_criteria,self.__tracking_info.items())

		return ActivityEntriesBrowser(entries)

	def all(self):
		return self.__tracking_info.items()