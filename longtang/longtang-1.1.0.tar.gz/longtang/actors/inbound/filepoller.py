#http://docs.python.org/2/howto/unicode

# -*- coding: utf-8 -*-

import os
import messages
import types
import re

from longtang.actors import actors
from longtang.actors.inbound.inflate import filepump, messages as fp_messages

class FilePoller(actors.Actor):

	def __init__(self, system_ref, unique_id):
		actors.Actor.__init__(self, system_ref, unique_id)

		self.__inflate_requests = {}
		self.__caller = []

		self.__filter_criteria = lambda types: lambda y: re.search(types, y) is not None
		self.__compressed_file_criteria = self.__filter_criteria('(.zip|.rar|.7z)$')
		self.__audio_file_criteria = self.__filter_criteria('.mp3$')

	def pre_setup(self):
		
		self.logger().info('Initializing actors...')

		self.__filepump_ref = self.context().from_type(filepump.FilePumpActor,'filepump-actor')

	def receive(self, message):

		if isinstance(message, messages.StartPolling):

			self.__caller.append(self.sender())
			source = message.source()

			if type(source) is not types.UnicodeType:
				source = unicode(message.source(), encoding='utf-8', errors='replace')

			self.logger().info(u'Polling request recieved. Polling source: {0}'.format(source))

			try:
				for root, dirnames, filenames in os.walk(source):

	  				for filename in filter(self.__audio_file_criteria, filenames):
	  					full_path = os.path.join(root, filename)
						self.logger().info(u'New file found: {0}'.format(full_path))
						self.sender().tell(messages.AudioFileFound(full_path), self.myself())

					for filename in filter(self.__compressed_file_criteria, filenames):
						full_path = os.path.join(root, filename)
						self.logger().info(u'New compressed file found: {0}. Requesting to be inflate'.format(full_path))

						self.__inflate_requests[full_path]=None

						self.context().get_by_id('filepump-actor').tell(fp_messages.InflateFile(full_path), self.myself())

				self.__notify_polling_done_if_possible()

			except Exception as e:
				self.logger().warn(u'Polling process interrupted. Reason: {0}'.format(str(e)))
				self.__caller[0].tell(messages.FilePollingDone(), self.myself())
		
		elif isinstance(message, fp_messages.InflateFileDone):
			self.__notify_polling_done_if_possible(message)
		elif isinstance(message, fp_messages.InflateFileFailed):
			self.__caller[0].tell(messages.CompressedFileCouldNotBeOpened(message.filepath()), self.myself())
			self.__notify_polling_done_if_possible(message)
		elif isinstance(message, fp_messages.InflatedFileAvailable):

			if self.__audio_file_criteria(message.filepath()):
				self.__caller[0].tell(messages.CompressedAudioFileFound(message.filepath(), message.parent_filepath()), self.myself())
			else:
				self.logger().debug(u'Inflated file \'{0}\' discarded'.format(message.filepath()))
		else: 
			self.notify_marooned_message(message)

	def __notify_polling_done_if_possible(self, message=None):

		if message is not None:
			self.__inflate_requests.pop(message.filepath())

		if len(self.__inflate_requests) == 0:
			self.__caller[0].tell(messages.FilePollingDone(), self.myself())