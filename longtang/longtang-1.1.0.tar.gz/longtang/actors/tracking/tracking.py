import messages
import summary
import tracking_generator as tg

from longtang.actors import actors
from longtang.common.mediatracking import mediatracking, events as media_events

class TrackingActor(actors.Actor):

	def __init__(self, system_ref, unique_id):
		actors.Actor.__init__(self, system_ref, unique_id)

		self.__audio_trackings={}
		self.__compressed_files_trackings={}

	def receive(self, message):
		if isinstance(message, messages.CreateCompressedFileTrackingEntry):

			self.logger().info(u'Creating compressed file tracking entry for source path \'{0}\' .....'.format(message.sourcepath()))

			descriptor = mediatracking.CompressedFileDescriptorBuilder().sourcepath(message.sourcepath()).build()
			file_tracking = mediatracking.MediaFileTracking.create_from(descriptor)
			trackingid = tg.MessageTrackingGenerator.generate(message)

			self.__compressed_files_trackings[trackingid]=file_tracking

			self.sender().tell(messages.CompressedFileTrackingEntryCreated(trackingid), self.myself())

		elif isinstance(message, messages.CreateCompressedAudioFileTrackingEntry):
			
			self.logger().info(u'Creating compressed audio file tracking entry [path={0}, parent={1}] .....'.format(message.sourcepath(), message.parent_sourcepath()))

			compressedfile_tracking = None
			compressedfile_trackingid = tg.MessageTrackingGenerator.generate_parent(message)

			if compressedfile_trackingid not in self.__compressed_files_trackings:
				descriptor = mediatracking.CompressedFileDescriptorBuilder().sourcepath(message.parent_sourcepath()).build()
				compressedfile_tracking = mediatracking.MediaFileTracking.create_from(descriptor)
				self.__compressed_files_trackings[compressedfile_trackingid]=compressedfile_tracking				
			else:
				compressedfile_tracking = self.__compressed_files_trackings[compressedfile_trackingid]

			audiofile_descriptor = mediatracking.CompressedAudioFileDescriptorBuilder().sourcepath(message.sourcepath())\
																			 			.compressed_file(compressedfile_trackingid)\
																			 		    .build()
		
			audiofile_tracking = mediatracking.MediaFileTracking.create_from(audiofile_descriptor)
			audiofile_trackingid = tg.MessageTrackingGenerator.generate(message)

			#Register parent's audio file
			compressedfile_tracking.track_activity(media_events.CompressedAudioFileFound(audiofile_trackingid))
			#Register compressed audio file
			self.__audio_trackings[audiofile_trackingid]=audiofile_tracking

			self.logger().debug(u'Compressed audio file tracked under id {0}.....'.format(audiofile_trackingid))

			self.sender().tell(messages.CompressedAudioFileTrackingEntryCreated(audiofile_trackingid, compressedfile_trackingid), self.myself())

		elif isinstance(message, messages.CreateTrackingEntry):
			self.logger().info(u'Creating tracking entry for source path {0} .....'.format(message.sourcepath()))

			descriptor = mediatracking.AudioFileDescriptorBuilder().sourcepath(message.sourcepath()).build()
			file_tracking = mediatracking.MediaFileTracking.create_from(descriptor)

			trackingid = tg.MessageTrackingGenerator.generate(message)

			self.__audio_trackings[trackingid]=file_tracking

			self.sender().tell(messages.TrackingEntryCreated(trackingid), self.myself())

		elif isinstance(message, messages.LookupTrackingEntry):
			self.logger().info(u'Looking up tracking entry {0} .....'.format(message.tracking_id()))
			
			if self.__audio_trackings.has_key(message.tracking_id()):
				self.sender().tell(messages.TrackingEntryFound(self.__audio_trackings[message.tracking_id()]), self.myself())
			elif message.tracking_id() in self.__compressed_files_trackings:
				self.sender().tell(messages.TrackingEntryFound(self.__compressed_files_trackings[message.tracking_id()]), self.myself())
			else:
				self.sender().tell(messages.TrackingEntryNotFound(message.tracking_id()), self.myself())	

		elif isinstance(message, messages.RegisterTrackingEvent):
			self.logger().info(u'Event of type \'{1}\' recieved for tracking id \'{0}\' .....'.format(message.tracking_id(),message.tracking_event().type()))

			trackings = self.__audio_trackings 

			if isinstance(message, messages.RegisterCompressedFileTrackingEvent):
				trackings = self.__compressed_files_trackings

			if trackings.has_key(message.tracking_id()):
				trackings[message.tracking_id()].track_activity(message.tracking_event())

				if self.sender() is not None:
					self.sender().tell(messages.TrackingEventSuccessfullyRegistered(), self.myself())
			else:

				if self.sender() is not None:
					self.sender().tell(messages.TrackingEntryNotFound(message.tracking_id()), self.myself())

		elif isinstance(message, messages.GenerateSummary):
			self.sender().tell(messages.SummarySuccessfullyGenerated(summary.ActivitySummary.create(self.__audio_trackings, self.__compressed_files_trackings)), self.myself())			
		else: 
			self.notify_marooned_message(message)