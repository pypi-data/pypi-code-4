#https://github.com/hamcrest/PyHamcrest
#http://packages.python.org/PyHamcrest/

from longtang.common.mediatracking import mediatracking, events as media_events
import unittest

from hamcrest import *

class MediaTrackingTest(unittest.TestCase):

	def test_creation(self):

		full_filepath = '/dummy_path.mp3'
		descriptor = mediatracking.AudioFileDescriptorBuilder().sourcepath(full_filepath).build()
		file_tracking = mediatracking.MediaFileTracking.create_from(descriptor)

		assert_that(file_tracking.mediafile.sourcepath, is_(not_none()), 'Media file path is empty')
		assert_that(file_tracking.mediafile.sourcepath, is_(equal_to(full_filepath)), 'Media file path value is wrong')
		assert_that(file_tracking.tracking_events, is_(not_none()), 'Tracking events has not being initialized')
		assert_that(file_tracking.tracking_events.is_empty(), is_(True), 'Tracking events is not empty')

	def test_add_tracking_event(self):

		full_filepath = '/dummy_path.mp3'
		descriptor = mediatracking.AudioFileDescriptorBuilder().sourcepath(full_filepath).build()
		file_tracking = mediatracking.MediaFileTracking.create_from(descriptor)

		file_tracking.track_activity(media_events.MediaFileTrackingEvent('my-unique-type', 'short description', {'value-of-interest1':1000, 'value-of-interes2':'testing'}))		

		assert_that(file_tracking.tracking_events.is_empty(), is_(False), 'Tracking events is empty')
		assert_that(file_tracking.tracking_events.all(), is_(not_none()), 'All tracking event list is empty')
		assert_that(file_tracking.tracking_events.all().size(), is_(equal_to(1)), 'All tracking event list has not the right size')
		assert_that(file_tracking.tracking_events.of_type('my-unique-type').is_empty(), is_(False), 'Tracking events of type \'my-unique-type\' is empty')
		assert_that(file_tracking.tracking_events.of_type('my-unique-type').get(0), is_(not_none()), 'First tracking event could not be found')
		assert_that(file_tracking.tracking_events.of_type('my-unique-type').all(), is_(not_none()), 'First tracking event could not be found')
		assert_that(file_tracking.tracking_events.of_type('my-unique-type').all().size(), is_(equal_to(1)), 'Tracking event list of type \'my-unique-type\' has not the right size')

	def test_add_altering_tracking_event(self):

		class DestinationUpdateTrackingEvent(media_events.MediaFileTrackingEvent):
			def __init__(self, entry_type, description, destination):
				media_events.MediaFileTrackingEvent.__init__(self, entry_type, description,{"destination": destination})

			def process(self, file_descriptor):
				file_descriptor.destinationpath=self.context_information()["destination"]
				return file_descriptor

		full_filepath = '/dummy_path.mp3'
		descriptor = mediatracking.AudioFileDescriptorBuilder().sourcepath(full_filepath).build()
		file_tracking = mediatracking.MediaFileTracking.create_from(descriptor)

		file_tracking.track_activity(media_events.MediaFileTrackingEvent('my-unique-type', 'short description', {'value-of-interest1':1000, 'value-of-interes2':'testing'}))

		assert_that(file_tracking.mediafile.destinationpath, is_(none()), "Destination path is not empty as expected")

		file_tracking.track_activity(DestinationUpdateTrackingEvent('destination-update', 'This is an altering event', '/target/path/dummy.mp3'))

		assert_that(file_tracking.mediafile.destinationpath, is_(equal_to('/target/path/dummy.mp3')), "Destination path has not been updated")
		assert_that(file_tracking.tracking_events.all().size(), is_(equal_to(2)), 'All tracking event list has not the right size')
		assert_that(file_tracking.tracking_events.of_type('destination-update').is_empty(), is_(False), 'Tracking events of type \'my-unique-type\' is empty')
		assert_that(file_tracking.tracking_events.of_type('destination-update').all().size(), is_(equal_to(1)), 'Tracking event list of type \'my-unique-type\' has not the right size')

	def test_add_compressed_file_tracking_event(self):
		full_filepath = '/dummy_path.rar'

		descriptor = mediatracking.CompressedFileDescriptorBuilder().sourcepath(full_filepath).build()

		file_tracking = mediatracking.MediaFileTracking.create_from(descriptor)

		assert_that(file_tracking.mediafile.sourcepath, is_(not_none()), 'Media file path is empty')
		assert_that(file_tracking.mediafile.sourcepath, is_(equal_to(full_filepath)), 'Media file path value is wrong')
		assert_that(file_tracking.tracking_events, is_(not_none()), 'Tracking events has not being initialized')
		assert_that(file_tracking.tracking_events.is_empty(), is_(True), 'Tracking events is not empty')
		assert_that(file_tracking.mediafile.audiofiles, is_(not_none()), 'Related audiofile list has not been initialized')
		assert_that(file_tracking.mediafile.inflated, is_(equal_to(True)), 'Related inflated status is not initialized')		

	def test_relate_audiofile_to_compressed_file_tracking(self):
		full_filepath = '/dummy_path.rar'

		descriptor = mediatracking.CompressedFileDescriptorBuilder().sourcepath(full_filepath).build()

		file_tracking = mediatracking.MediaFileTracking.create_from(descriptor)

		file_tracking.track_activity(media_events.CompressedAudioFileFound('tracking-id1'))
		file_tracking.track_activity(media_events.CompressedAudioFileFound('tracking-id2'))

		assert_that(file_tracking.tracking_events.of_type('COMPRESSED_AUDIOFILE_FOUND').is_empty(), is_(False), 'Tracking events of type \'COMPRESSED_AUDIOFILE_FOUND\' is empty')		
		assert_that(file_tracking.tracking_events.of_type('COMPRESSED_AUDIOFILE_FOUND').all().size(), is_(equal_to(2)), 'Tracking event list of type \'COMPRESSED_AUDIOFILE_FOUND\' has not the right size')
		assert_that(file_tracking.mediafile.audiofiles.size(), is_(equal_to(2)), 'Related audiofile list has not been initialized')
		assert_that(file_tracking.mediafile.audiofiles.all(), has_items('tracking-id1','tracking-id2'), 'Related audiofile list has not the expected items')

	def test_altering_tracking_event_on_compressed_file(self):
		full_filepath = '/dummy_path.rar'

		descriptor = mediatracking.CompressedFileDescriptorBuilder().sourcepath(full_filepath).build()

		file_tracking = mediatracking.MediaFileTracking.create_from(descriptor)

		file_tracking.track_activity(media_events.FileCouldNotBeInflated())

		assert_that(file_tracking.mediafile.sourcepath, is_(not_none()), 'Media file path is empty')
		assert_that(file_tracking.mediafile.sourcepath, is_(equal_to(full_filepath)), 'Media file path value is wrong')
		assert_that(file_tracking.tracking_events, is_(not_none()), 'Tracking events has not being initialized')
		assert_that(file_tracking.tracking_events.is_empty(), is_(equal_to(False)), 'Tracking events is empty')
		assert_that(file_tracking.tracking_events.of_type('INFLATE_PROCESS_FAILURE').is_empty(), is_(False), 'Tracking events of type \'INFLATE_PROCEDURE_FAILED\' is empty')	
		assert_that(file_tracking.mediafile.inflated, is_(equal_to(False)), 'Related inflated status is not initialized')		

	def test_add_compressed_mediafile_tracking_event(self):
		full_filepath = '/dummy_path.mp3'
		descriptor = mediatracking.CompressedAudioFileDescriptorBuilder().sourcepath(full_filepath)\
																		 .compressed_file('parent-tracking-id').build()
		
		file_tracking = mediatracking.MediaFileTracking.create_from(descriptor)

		file_tracking.track_activity(media_events.MediaFileTrackingEvent('my-unique-type', 'short description', {'value-of-interest1':1000, 'value-of-interes2':'testing'}))		

		assert_that(file_tracking.tracking_events.is_empty(), is_(False), 'Tracking events is empty')
		assert_that(file_tracking.tracking_events.all(), is_(not_none()), 'All tracking event list is empty')
		assert_that(file_tracking.tracking_events.all().size(), is_(equal_to(1)), 'All tracking event list has not the right size')
		assert_that(file_tracking.tracking_events.of_type('my-unique-type').is_empty(), is_(False), 'Tracking events of type \'my-unique-type\' is empty')
		assert_that(file_tracking.tracking_events.of_type('my-unique-type').get(0), is_(not_none()), 'First tracking event could not be found')
		assert_that(file_tracking.tracking_events.of_type('my-unique-type').all(), is_(not_none()), 'First tracking event could not be found')
		assert_that(file_tracking.tracking_events.of_type('my-unique-type').all().size(), is_(equal_to(1)), 'Tracking event list of type \'my-unique-type\' has not the right size')
		assert_that(file_tracking.mediafile.compressed_file, is_(equal_to('parent-tracking-id')), 'Parent compressed file has not been informed')

	def test_add_altering_tracking_event_on_compressed_mediafile(self):

		class DestinationUpdateTrackingEvent(media_events.MediaFileTrackingEvent):
			def __init__(self, entry_type, description, destination):
				media_events.MediaFileTrackingEvent.__init__(self, entry_type, description,{"destination": destination})

			def process(self, file_descriptor):
				file_descriptor.destinationpath=self.context_information()["destination"]
				return file_descriptor

		full_filepath = '/dummy_path.mp3'
		descriptor = mediatracking.CompressedAudioFileDescriptorBuilder().sourcepath(full_filepath)\
																		 .compressed_file('parent-tracking-id').build()
																		 
		file_tracking = mediatracking.MediaFileTracking.create_from(descriptor)

		file_tracking.track_activity(media_events.MediaFileTrackingEvent('my-unique-type', 'short description', {'value-of-interest1':1000, 'value-of-interes2':'testing'}))

		assert_that(file_tracking.mediafile.destinationpath, is_(none()), "Destination path is not empty as expected")

		file_tracking.track_activity(DestinationUpdateTrackingEvent('destination-update', 'This is an altering event', '/target/path/dummy.mp3'))

		assert_that(file_tracking.mediafile.destinationpath, is_(equal_to('/target/path/dummy.mp3')), "Destination path has not been updated")
		assert_that(file_tracking.tracking_events.all().size(), is_(equal_to(2)), 'All tracking event list has not the right size')
		assert_that(file_tracking.tracking_events.of_type('destination-update').is_empty(), is_(False), 'Tracking events of type \'my-unique-type\' is empty')
		assert_that(file_tracking.tracking_events.of_type('destination-update').all().size(), is_(equal_to(1)), 'Tracking event list of type \'my-unique-type\' has not the right size')