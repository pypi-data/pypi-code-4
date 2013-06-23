#https://github.com/hamcrest/PyHamcrest
#http://packages.python.org/PyHamcrest/

import gevent
import unittest
import os

from hamcrest import *
from longtang.actors.tracking import tracking, messages
from longtang.system import system
from longtang.actors import actorstestutils
from longtang.common import interactions
from longtang.common.mediatracking import mediatracking, events as mt_events

class TestMediaTrackingActor(unittest.TestCase):

	def test_creation(self):
		actor_system = system.ActorSystem()
		tracking_actor = actor_system.from_type(tracking.TrackingActor,'tracking-actor')

		try:
			assert_that(actor_system.find_by_id('tracking-actor'), is_not(None), 'Tracking actor does not exist within system')
		except exceptions.ActorNotFound as e:
			self.fail(str(e))
						
		actor_system.shutdown()

	def test_add_single_tracking(self):
		actor_system = system.ActorSystem()
		tracking_actor = actor_system.from_type(tracking.TrackingActor,'tracking-actor')

		response = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.CreateTrackingEntry('/dummy.mp3'))

		assert_that(response, is_(not_none()),'Tracking identifier message is empty')
		assert_that(response, is_(instance_of(messages.TrackingEntryCreated)),'Tracking response message is not of the right type')
		assert_that(response.tracking_id(), is_(not_none()),'Tracking identifier is missing')

		actor_system.shutdown()

	def test_retrieve_single_tracking(self):
		actor_system = system.ActorSystem()
		tracking_actor = actor_system.from_type(tracking.TrackingActor,'tracking-actor')		

		tracking_id = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.CreateTrackingEntry('/dummy-2.mp3')).tracking_id()

		response = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.LookupTrackingEntry(tracking_id))

		assert_that(response, is_(not_none()),'Tracking information message is empty')
		assert_that(response, is_(instance_of(messages.TrackingEntryFound)),'Tracking information message is not of the right type')
		assert_that(response.tracking_info().mediafile.sourcepath, is_(equal_to('/dummy-2.mp3')),'Tracking identifier is missing')

		actor_system.shutdown()

	def test_retrieve_single_tracking_notfound(self):
		actor_system = system.ActorSystem()
		tracking_actor = actor_system.from_type(tracking.TrackingActor,'tracking-actor')		

		tracking_id = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.CreateTrackingEntry('/dummy-2.mp3')).tracking_id()

		response = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.LookupTrackingEntry('nonexistingid'))

		assert_that(response, is_(not_none()),'Tracking information message is empty')
		assert_that(response, is_(instance_of(messages.TrackingEntryNotFound)),'Tracking information message is not of the right type')
		assert_that(response.tracking_id(), is_(equal_to('nonexistingid')),'Tracking identifier is missing')		

		actor_system.shutdown()

	def test_notify_non_altering_tracking_event(self):
		actor_system = system.ActorSystem()
		tracking_actor = actor_system.from_type(tracking.TrackingActor,'tracking-actor')		

		tracking_id = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.CreateTrackingEntry('/dummy-non-tracking.mp3')).tracking_id()

		event = mt_events.MediaFileTrackingEvent('NONALTERING', 'This is a non-altering event')

		response = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.RegisterTrackingEvent(tracking_id,event))

		assert_that(response, is_(not_none()),'Tracking information message is empty')
		assert_that(response, is_(instance_of(messages.TrackingEventSuccessfullyRegistered)),'Tracking event response is not of the right type')

		response = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.LookupTrackingEntry(tracking_id))

		assert_that(response.tracking_info().tracking_events.of_type('NONALTERING').is_empty(), is_(False),'Tracking events of type NONALTERING are empty')
		assert_that(response.tracking_info().tracking_events.of_type('NONALTERING').get(0), is_(not_none()),'Tracked events does not exist')

		actor_system.shutdown()

	def test_notify_altering_tracking_event(self):
		actor_system = system.ActorSystem()
		tracking_actor = actor_system.from_type(tracking.TrackingActor,'tracking-actor')		

		tracking_id = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.CreateTrackingEntry('/dummy-non-tracking.mp3')).tracking_id()

		event = DestinationUpdateTrackingEvent('DESTINATION', 'This is an altering event', '/target/path/dummy.mp3')

		response = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.RegisterTrackingEvent(tracking_id,event))

		assert_that(response, is_(not_none()),'Tracking information message is empty')
		assert_that(response, is_(instance_of(messages.TrackingEventSuccessfullyRegistered)),'Tracking event response is not of the right type')

		response = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.LookupTrackingEntry(tracking_id))

		assert_that(response.tracking_info().tracking_events.of_type('DESTINATION').is_empty(), is_(False),'Tracking events of type NONALTERING are empty')
		assert_that(response.tracking_info().tracking_events.of_type('DESTINATION').get(0), is_(not_none()),'Tracked events does not exist')
		assert_that(response.tracking_info().mediafile.destinationpath, is_(equal_to('/target/path/dummy.mp3')),'Mediafile information has not been updated')

		actor_system.shutdown()
	
	def test_add_compressed_file_tracking(self):
		actor_system = system.ActorSystem()
		tracking_actor = actor_system.from_type(tracking.TrackingActor,'tracking-actor')

		response = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.CreateCompressedFileTrackingEntry('/dummy.zip'))

		assert_that(response, is_(not_none()),'Tracking identifier message is empty')
		assert_that(response, is_(instance_of(messages.CompressedFileTrackingEntryCreated)),'Tracking response message is not of the right type')
		assert_that(response.tracking_id(), is_(not_none()),'Tracking identifier is missing')
		assert_that(response.tracking_id(), is_(has_length(greater_than(0))),'Tracking identifier is empty')

		actor_system.shutdown()

	def test_add_compressed_audio_file_tracking(self):
		actor_system = system.ActorSystem()
		tracking_actor = actor_system.from_type(tracking.TrackingActor,'tracking-actor')

		response = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.CreateCompressedAudioFileTrackingEntry('mymusic.mp3', '/dummy.zip'))

		assert_that(response, is_(not_none()),'Tracking identifier message is empty')
		assert_that(response, is_(instance_of(messages.CompressedAudioFileTrackingEntryCreated)),'Tracking response message is not of the right type')
		assert_that(response.tracking_id(), is_(not_none()),'Tracking identifier is missing')
		assert_that(response.tracking_id(), is_(has_length(greater_than(0))),'Tracking identifier is empty')
		assert_that(response.parent_tracking_id(), is_(not_none()),'Tracking identifier is missing')
		assert_that(response.parent_tracking_id(), is_(has_length(greater_than(0))),'Tracking identifier is empty')

		actor_system.shutdown()

	def test_notity_compressed_file_tracking_event(self):
		actor_system = system.ActorSystem()
		tracking_actor = actor_system.from_type(tracking.TrackingActor,'tracking-actor')

		tracking_id = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.CreateCompressedFileTrackingEntry('/dummy.zip')).tracking_id()

		event = mt_events.MediaFileTrackingEvent('NONALTERING', 'This is a non-altering event')

		response = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.RegisterCompressedFileTrackingEvent(tracking_id,event))

		assert_that(response, is_(not_none()),'Tracking information message is empty')
		assert_that(response, is_(instance_of(messages.TrackingEventSuccessfullyRegistered)),'Tracking event response is not of the right type')

		response = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.LookupTrackingEntry(tracking_id))

		assert_that(response, is_(instance_of(messages.TrackingEntryFound)), 'Compressed file tracking information was not found')
		assert_that(response.tracking_info().tracking_events.of_type('NONALTERING').is_empty(), is_(False),'Tracking events of type NONALTERING are empty')
		assert_that(response.tracking_info().tracking_events.of_type('NONALTERING').get(0), is_(not_none()),'Tracked events does not exist')

		actor_system.shutdown()

	def test_check_audiofiles_list_from_compressed_file(self):
		actor_system = system.ActorSystem()
		tracking_actor = actor_system.from_type(tracking.TrackingActor,'tracking-actor')

		audio1_response = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.CreateCompressedAudioFileTrackingEntry('mymusic1.mp3', '/dummy.zip'))
		audio2_response = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.CreateCompressedAudioFileTrackingEntry('mymusic2.mp3', '/dummy.zip'))

		assert_that(audio1_response.parent_tracking_id(), is_(equal_to(audio2_response.parent_tracking_id())), 'Parent compressed file tracking id does not match')

		response = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.LookupTrackingEntry(audio2_response.parent_tracking_id()))

		assert_that(response.tracking_info().mediafile.audiofiles.size(), is_(equal_to(2)),'Audio files are not registered at compressed file tracking')
		assert_that(response.tracking_info().mediafile.audiofiles.all(), has_items(audio1_response.tracking_id(), audio2_response.tracking_id()), 'Compressed audio files are not accurately related to the compressed file')

	def test_notify_compressed_audio_file_non_altering_tracking_event(self):
		actor_system = system.ActorSystem()
		tracking_actor = actor_system.from_type(tracking.TrackingActor,'tracking-actor')		

		tracking_id = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.CreateCompressedAudioFileTrackingEntry('mymusic.mp3', '/dummy.zip')).tracking_id()

		event = mt_events.MediaFileTrackingEvent('NONALTERING', 'This is a non-altering event')

		response = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.RegisterTrackingEvent(tracking_id,event))

		assert_that(response, is_(not_none()),'Tracking information message is empty')
		assert_that(response, is_(instance_of(messages.TrackingEventSuccessfullyRegistered)),'Tracking event response is not of the right type')

		response = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.LookupTrackingEntry(tracking_id))

		assert_that(response.tracking_info().tracking_events.of_type('NONALTERING').is_empty(), is_(False),'Tracking events of type NONALTERING are empty')
		assert_that(response.tracking_info().tracking_events.of_type('NONALTERING').get(0), is_(not_none()),'Tracked events does not exist')

		actor_system.shutdown()

	def test_notify_compressed_audio_file_altering_tracking_event(self):
		actor_system = system.ActorSystem()
		tracking_actor = actor_system.from_type(tracking.TrackingActor,'tracking-actor')		

		tracking_id = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.CreateCompressedAudioFileTrackingEntry('mymusic.mp3', '/dummy.zip')).tracking_id()

		event = DestinationUpdateTrackingEvent('DESTINATION', 'This is an altering event', '/target/path/dummy.mp3')

		response = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.RegisterTrackingEvent(tracking_id,event))

		assert_that(response, is_(not_none()),'Tracking information message is empty')
		assert_that(response, is_(instance_of(messages.TrackingEventSuccessfullyRegistered)),'Tracking event response is not of the right type')

		response = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.LookupTrackingEntry(tracking_id))

		assert_that(response.tracking_info().tracking_events.of_type('DESTINATION').is_empty(), is_(False),'Tracking events of type NONALTERING are empty')
		assert_that(response.tracking_info().tracking_events.of_type('DESTINATION').get(0), is_(not_none()),'Tracked events does not exist')
		assert_that(response.tracking_info().mediafile.destinationpath, is_(equal_to('/target/path/dummy.mp3')),'Mediafile information has not been updated')

	def test_retrieve_summary_without_compressed_files(self):
		actor_system = system.ActorSystem()
		tracking_actor = actor_system.from_type(tracking.TrackingActor,'tracking-actor')		

		audio1_tracking_id = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.CreateTrackingEntry('/dummy1.mp3')).tracking_id()
		audio2_tracking_id = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.CreateTrackingEntry('/dummy2.mp3')).tracking_id()
		audio3_tracking_id = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.CreateTrackingEntry('/dummy3.mp3')).tracking_id()

		summary = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.GenerateSummary()).summary()

		assert_that(summary.audio().total(), is_(equal_to(3)), 'Number of files in the summary is wrong')
		assert_that(summary.audio().successes().total(), is_(equal_to(3)), 'Number of summary successes is wrong')
		assert_that(summary.audio().failures().total(), is_(equal_to(0)), 'Number of failures successes is wrong')

		total = summary.audio().total()

		assert_that(summary.audio().successes().find(audio1_tracking_id), is_(not_none()), 'Audio1 tracking id could not be found')
		assert_that(summary.audio().successes().find(audio2_tracking_id), is_(not_none()), 'Audio2 tracking id could not be found')
		assert_that(summary.audio().successes().find(audio3_tracking_id), is_(not_none()), 'Audio3 tracking id could not be found')

	def test_retrieve_summary_without_compressed_files_and_single_failure(self):
		actor_system = system.ActorSystem()
		tracking_actor = actor_system.from_type(tracking.TrackingActor,'tracking-actor')		

		audio1_tracking_id = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.CreateTrackingEntry('/dummy1.mp3')).tracking_id()
		audio2_tracking_id = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.CreateTrackingEntry('/dummy2.mp3')).tracking_id()
		audio3_tracking_id = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.CreateTrackingEntry('/dummy3.mp3')).tracking_id()

		event = mt_events.MediaFileTrackingEvent('THIS_IS_A_FAILURE', 'This is a non-altering event')

		response = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.RegisterTrackingEvent(audio1_tracking_id,event))

		summary = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.GenerateSummary()).summary()

		assert_that(summary.audio().total(), is_(equal_to(3)), 'Number of files in the summary is wrong')
		assert_that(summary.audio().successes().total(), is_(equal_to(2)), 'Number of summary successes is wrong')
		assert_that(summary.audio().failures().total(), is_(equal_to(1)), 'Number of failures successes is wrong')

		assert_that(summary.audio().successes().find(audio1_tracking_id), is_(none()), 'Audio1 tracking id was found within success!!')
		assert_that(summary.audio().successes().find(audio2_tracking_id), is_(not_none()), 'Audio2 tracking id could not be found within successes')
		assert_that(summary.audio().successes().find(audio3_tracking_id), is_(not_none()), 'Audio3 tracking id could not be found within successes')

		assert_that(summary.audio().failures().find(audio1_tracking_id), is_(not_none()), 'Audio1 tracking id could not be found within failures')
		assert_that(summary.audio().failures().find(audio2_tracking_id), is_(none()), 'Audio2 tracking id was found within failures!!')
		assert_that(summary.audio().failures().find(audio3_tracking_id), is_(none()), 'Audio3 tracking id was found within failures!!')		

	def test_retrieve_summary_with_compressed_files(self):
		actor_system = system.ActorSystem()
		tracking_actor = actor_system.from_type(tracking.TrackingActor,'tracking-actor')		

		audio1_tracking_id = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.CreateTrackingEntry('/dummy1.mp3')).tracking_id()
		audio2_tracking_id = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.CreateTrackingEntry('/dummy2.mp3')).tracking_id()
		audio3_tracking_id = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.CreateTrackingEntry('/dummy3.mp3')).tracking_id()
		compressed1_audio1_tracking_id = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.CreateCompressedAudioFileTrackingEntry('mymusic1.mp3', '/dummy1.zip')).tracking_id()
		compressed1_audio2_tracking_id = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.CreateCompressedAudioFileTrackingEntry('mymusic2.mp3', '/dummy1.zip')).tracking_id()		
		compressed2_audio1_tracking_id = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.CreateCompressedAudioFileTrackingEntry('myothermusic1.mp3', '/dummy2.zip')).tracking_id()		
		compressed2_audio2_tracking_id = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.CreateCompressedAudioFileTrackingEntry('myothermusic2.mp3', '/dummy2.zip')).tracking_id()

		summary = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.GenerateSummary()).summary()

		assert_that(summary.audio().total(), is_(equal_to(7)), 'Number of files in the summary is wrong')
		assert_that(summary.audio().successes().total(), is_(equal_to(7)), 'Number of summary successes is wrong')
		assert_that(summary.audio().successes(False).total(), is_(equal_to(3)), 'Number of summary successes without compressed audio files is wrong')
		assert_that(summary.audio().failures().total(), is_(equal_to(0)), 'Number of failures successes is wrong')
		assert_that(summary.audio().failures(False).total(), is_(equal_to(0)), 'Number of failures successes without compressed audio files is wrong')
		assert_that(summary.compressed().successes().total(), is_(equal_to(2)), 'Number of success uncompressed files is wrong')
		assert_that(summary.compressed().failures().total(), is_(equal_to(0)), 'Number of success uncompressed files is wrong')

		for tracking_id, mediatracking in summary.compressed().all():
			assert_that(mediatracking.mediafile.inflated, is_(equal_to(True)), 'All compressed files are not marked as inflated')

	def test_retrieve_summary_with_compressed_files_and_single_compressed_file_failure(self):
		actor_system = system.ActorSystem()
		tracking_actor = actor_system.from_type(tracking.TrackingActor,'tracking-actor')		

		audio1_tracking_id = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.CreateTrackingEntry('/dummy1.mp3')).tracking_id()
		audio2_tracking_id = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.CreateTrackingEntry('/dummy2.mp3')).tracking_id()
		audio3_tracking_id = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.CreateTrackingEntry('/dummy3.mp3')).tracking_id()

		compressedfile1_tracking_id = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.CreateCompressedFileTrackingEntry('/dummy1.zip')).tracking_id()
		
		compressed2_audio1_tracking_id = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.CreateCompressedAudioFileTrackingEntry('myothermusic1.mp3', '/dummy2.zip')).tracking_id()
		compressed2_audio2_tracking_id = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.CreateCompressedAudioFileTrackingEntry('myothermusic2.mp3', '/dummy2.zip')).tracking_id()

		response = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.RegisterCompressedFileTrackingEvent(compressedfile1_tracking_id,mt_events.FileCouldNotBeInflated()))

		summary = interactions.InteractionPatterns.ask(actor_system,tracking_actor, messages.GenerateSummary()).summary()

		assert_that(summary.audio().total(), is_(equal_to(5)), 'Number of files in the summary is wrong')
		assert_that(summary.audio().successes().total(), is_(equal_to(5)), 'Number of summary successes is wrong')
		assert_that(summary.audio().successes(False).total(), is_(equal_to(3)), 'Number of summary successes without compressed audio files is wrong')
		assert_that(summary.audio().failures().total(), is_(equal_to(0)), 'Number of failures successes is wrong')
		assert_that(summary.audio().failures(False).total(), is_(equal_to(0)), 'Number of failures successes without compressed audio files is wrong')
		assert_that(summary.compressed().successes().total(), is_(equal_to(1)), 'Number of success uncompressed files is wrong')
		assert_that(summary.compressed().failures().total(), is_(equal_to(1)), 'Number of success uncompressed files is wrong')

		assert_that(summary.compressed().failures().find(compressedfile1_tracking_id)[1].mediafile.inflated, is_(equal_to(False)), 'Failed compressed file is still marked as inflated')

class DestinationUpdateTrackingEvent(mt_events.MediaFileTrackingEvent):
	def __init__(self, entry_type, description, destination):
		mt_events.MediaFileTrackingEvent.__init__(self, entry_type, description,{"destination": destination})

	def process(self, file_descriptor):
		file_descriptor.destinationpath=self.context_information()["destination"]
		return file_descriptor