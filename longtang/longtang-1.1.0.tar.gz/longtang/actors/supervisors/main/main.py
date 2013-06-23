import messages

from longtang.actors import actors
from longtang.actors.tracking import tracking, facade
from longtang.actors.inbound import filepoller, messages as fp_messages
from longtang.actors.supervisors.flowconductor import flowconductor, factory, messages as fc_messages
from longtang.common.mediatracking import events as mt_events

class MainSupervisor(actors.Actor):

	def __init__(self, config, system_ref, unique_id):
		actors.Actor.__init__(self, system_ref, unique_id)

		self.__config=config
		self.__filecount = {}
		self.__caller = []

	def pre_setup(self):
		
		self.logger().info('Initializing actors...')
		self.logger().info('Initializing file-poller-actor...')

		self.__file_poller_ref = self.context().from_type(filepoller.FilePoller,'file-poller-actor')

		self.logger().info('Initializing flowconductor-actor...')

		self.__flowconductor_ref = self.context().with_factory(factory.FlowConductorSupervisorFactory(self.__config),'flowconductor-actor')

		self.logger().info('Initializing tracking-actor...')
		self.__tracking_facade = facade.MediaTrackingFacade.create_within(self.context())

	
	def receive(self, message):
		if isinstance(message, messages.KickOffMediaProcessing):
			self.__caller.append(self.sender())
			self.logger().info('Media processing has just started. [From: {0}, To: {1}]'.format(self.__config.read_from, self.__config.generate_at))
			self.context().get_by_id('file-poller-actor').tell(fp_messages.StartPolling(self.__config.read_from), self)

		elif isinstance(message, fp_messages.CompressedAudioFileFound):
			tracking_id, parent_tracking_id = facade.MediaTrackingFacade.from_context(self.context()).create_compressed_audio_tracking(message.filepath(), message.compressed_parent_filepath())
			self.__filecount[tracking_id] = None

			self.logger().debug(u'Compressed audio file tracked. [path: {0}, parent: {1}, tracking_id: {2}]'.format(message.filepath(),\
																												  message.compressed_parent_filepath(),\
																												  tracking_id))

			self.context().get_by_id('flowconductor-actor').tell(fc_messages.MediaFileAvailable(message.filepath(), tracking_id), self)

		elif isinstance(message, fp_messages.AudioFileFound):
			tracking_id = facade.MediaTrackingFacade.from_context(self.context()).create_audio_tracking(message.filepath())
			self.__filecount[tracking_id] = None

			self.logger().debug(u'Audio file tracked. [path: {0}, tracking_id: {1}]'.format(message.filepath(), tracking_id))

			self.context().get_by_id('flowconductor-actor').tell(fc_messages.MediaFileAvailable(message.filepath(), tracking_id), self)

		elif isinstance(message, fp_messages.CompressedFileCouldNotBeOpened):

			self.logger().debug(u'Compressed file {0} could not be inflated'.format(message.filepath()))

			tracking_id=facade.MediaTrackingFacade.from_context(self.context()).create_compressed_file_tracking(message.filepath())
			facade.MediaTrackingFacade.from_context(self.context()).notify_inflate_failure(tracking_id)
		
		elif isinstance(message, fc_messages.MediaFileHasBeenProcessed):
			self.terminate_if_done(message)
		elif isinstance(message, fc_messages.MediaFileProcessingFailed):
			self.terminate_if_done(message)
		else: 
			self.notify_marooned_message(message)		

	def terminate_if_done(self, message):

		self.__filecount.pop(message.tracking())

		if len(self.__filecount) == 0:
			self.logger().info('Terminating execution.....')
			summary = facade.MediaTrackingFacade.from_context(self.context()).retrieve_summary()
			self.__caller[0].tell(messages.MediaProcessingFinished(summary), self)
