#https://github.com/hamcrest/PyHamcrest
#http://packages.python.org/PyHamcrest/

import gevent
import unittest
import os

from hamcrest import *
from longtang.system import system, domain as sys_domain
from longtang.actors import actorstestutils
from longtang.actors.tracking import facade, tracking
from longtang.common.mediatracking import events as mt_events

class TestTrackingActorFacade(unittest.TestCase):

	def test_create_audio_tracking(self):
		actor_system = system.ActorSystem()
		tracking_actor = actor_system.from_type(tracking.TrackingActor,'mediatracking-actor')

		tracking_facade = facade.MediaTrackingFacade.from_system(sys_domain.SystemRef(actor_system))

		tracking_id = tracking_facade.create_audio_tracking('/dummy.mp3')

		assert_that(tracking_id, is_(not_none()),'Tracking identifier is empty')

		actor_system.shutdown()	

	def test_create_compressed_audio_tracking(self):
		actor_system = system.ActorSystem()
		tracking_actor = actor_system.from_type(tracking.TrackingActor,'mediatracking-actor')

		tracking_facade = facade.MediaTrackingFacade.from_system(sys_domain.SystemRef(actor_system))

		tracking_id, parent_tracking_id = tracking_facade.create_compressed_audio_tracking('/dummy.mp3', '/compressed.zip')

		assert_that(tracking_id, is_(not_none()),'Tracking identifier is empty')
		assert_that(parent_tracking_id, is_(not_none()),'Parent tracking identifier is empty')

		actor_system.shutdown()	

	def test_create_compressed_file_tracking(self):
		actor_system = system.ActorSystem()
		tracking_actor = actor_system.from_type(tracking.TrackingActor,'mediatracking-actor')

		tracking_facade = facade.MediaTrackingFacade.from_system(sys_domain.SystemRef(actor_system))

		tracking_id = tracking_facade.create_compressed_file_tracking('/compressed.zip')

		assert_that(tracking_id, is_(not_none()),'Tracking identifier is empty')

		actor_system.shutdown()			

	def test_lookup(self):
		actor_system = system.ActorSystem()
		tracking_actor = actor_system.from_type(tracking.TrackingActor,'mediatracking-actor')

		tracking_facade = facade.MediaTrackingFacade.from_system(sys_domain.SystemRef(actor_system))

		tracking_id = tracking_facade.create_audio_tracking('/dummy.mp3')
		tracking_info = tracking_facade.lookup(tracking_id)

		assert_that(tracking_info, is_(not_none()),'Tracking information is empty')
		assert_that(tracking_info.mediafile.sourcepath, is_('/dummy.mp3'),'Tracking sourcepath information is not right')

	def test_notify(self):
		actor_system = system.ActorSystem()
		tracking_actor = actor_system.from_type(tracking.TrackingActor,'mediatracking-actor')

		tracking_facade = facade.MediaTrackingFacade.from_system(sys_domain.SystemRef(actor_system))		

		tracking_id = tracking_facade.create_audio_tracking('/dummy.mp3')

		event = mt_events.MediaFileTrackingEvent('NONALTERING', 'This is a non-altering event')

		tracking_facade.notify(tracking_id, event)

		tracking_info = tracking_facade.lookup(tracking_id)

		assert_that(tracking_info.tracking_events.of_type('NONALTERING').is_empty(), is_(False),'Tracking events of type NONALTERING are empty')
		assert_that(tracking_info.tracking_events.of_type('NONALTERING').get(0), is_(not_none()),'Tracked events does not exist')

	def test_notify_compressed(self):
		actor_system = system.ActorSystem()
		tracking_actor = actor_system.from_type(tracking.TrackingActor,'mediatracking-actor')

		tracking_facade = facade.MediaTrackingFacade.from_system(sys_domain.SystemRef(actor_system))

		tracking_id = tracking_facade.create_compressed_file_tracking('/compressed.zip')

		event = mt_events.FileCouldNotBeInflated()

		tracking_facade.notify_inflate_failure(tracking_id)

		tracking_info = tracking_facade.lookup(tracking_id)

		assert_that(tracking_info.tracking_events.of_type(event.type()).is_empty(), is_(False),'Tracking events of type {0} are empty'.format(event.type()))
		assert_that(tracking_info.tracking_events.of_type(event.type()).get(0), is_(not_none()),'Tracked event does not exist')