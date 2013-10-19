# Copyright 2008 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Author: zwsun<sun33170161@gmail.com>


import socket
import asyncore
import sys
import Queue
import threading
import time
import logging
import common.NetUtil as netutil

class NodeStatus():
	def __init__(self, addr, status):
		self.addr = addr
		self.status = status

'''
Heartbeat format: Content-Length[4]Content[$Content-Length]
'''
class HeartBeatHandler(asyncore.dispatcher_with_send):
	
	def __init__(self, sock, addr, queue):
		self.logger = logging.getLogger()
		asyncore.dispatcher_with_send.__init__(self, sock)
		self.__addr = addr
		self.__queue = queue
		self.__bufData = ''
		self.__contentLen = -1
		self.end = False

	def handle_read(self):
		data = self.recv(8192)
		if data:
			self.__bufData += data
			while len(self.__bufData) > 0:
				if self.__contentLen < 0 : 
					finished, strdata = self.__processData(4)
					if not finished :
						return
					self.__contentLen = int(strdata)
					if self.__contentLen < 0 :
						raise IOError("Content length is negative %d"%self.contentLen)
				finished, strdata = self.__processData(self.__contentLen)
				if not finished :
					return
				if self.logger.isEnabledFor(logging.DEBUG):
					self.logger.debug("Get report from %s with status %s", repr(self.__addr), strdata)
				if strdata == 'END':
					self.end = True
				self.__queue.put(NodeStatus(self.__addr, strdata))
				self.__contentLen = -1

	def handle_close(self):
		if self.end:
			return
		if self.logger.isEnabledFor(logging.DEBUG):
			self.logger.debug("Connection close %s, add status %s", repr(self.__addr), "DEAD")
		self.end = True
		self.__queue.put(NodeStatus(self.__addr, "DEAD"))

	def __processData(self, dataLen):
		bufLen = len(self.__bufData)
		if bufLen < dataLen :
			return (False, None)
		data = self.__bufData[0:dataLen]
		self.__bufData = self.__bufData[dataLen:]
		return (True, data) 

class HeartBeatReceiver(asyncore.dispatcher, threading.Thread):
	
	def __init__(self, port):
		self.logger = logging.getLogger()
		threading.Thread.__init__(self)
		asyncore.dispatcher.__init__(self)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		#self.set_reuse_addr()
		self.queue = Queue.Queue()
		self.port = port
		self.bind((netutil.getLocalIP(), port))
		self.listen(100)
		self.setDaemon(True)
		self.setName("HeartbeatReceiver")
	
	def handle_accept(self):
		pair = self.accept()
		if pair is not None:
			sock, addr = pair
			handler = HeartBeatHandler(sock, addr, self.queue)
	
	def handle_close(self):
		pass	

	def run(self):
		self.logger.info("Start HearbeatReceiver at port %d", self.port)
		asyncore.loop()

	def get(self, timeout):
		try:
			return self.queue.get(True, timeout)
		except Queue.Empty:
			return None
