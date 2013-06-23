#http://docs.python.org/2/howto/unicode

# -*- coding: utf-8 -*-

import os
import messages
import types

from pumpingclerk import PumpingClerkFactory
from longtang.actors import actors

class FilePumpActor(actors.Actor):
	def receive(self, message):
		if isinstance(message, messages.InflateFile):

			filepath = message.filepath()

			if type(filepath) is not types.UnicodeType:
				filepath = unicode(filepath, encoding='utf-8', errors='replace')

			self.logger().info(u'Inflate file request recieved. Compressed source file: {0}'.format(filepath))

			try:
				clerk = PumpingClerkFactory.from_file(filepath)

				for entry in clerk.inflate().entries():
					self.logger().debug(u'Inflated entry \'{0}\' retrieved from file {1}'.format(entry, filepath))
					self.sender().tell(messages.InflatedFileAvailable(entry, filepath), self.myself())

				self.sender().tell(messages.InflateFileDone(filepath), self.myself())

			except Exception,e:

				self.logger().error('File pumping failed. Source: {0}'.format(str(e)))
				self.sender().tell(messages.InflateFileFailed(filepath), self.myself())


		else: 
			self.notify_marooned_message(message)