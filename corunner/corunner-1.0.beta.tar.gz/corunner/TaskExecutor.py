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


import sys
import time
import subprocess
import os
import asyncore, socket
import threading
import logging, logging.handlers, logging.config

class NetClient(asyncore.dispatcher):
	
	def __init__(self, host, port):
		asyncore.dispatcher.__init__(self)
                self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
                self.connect( (host, port) )
	
	def write(self, data):
		if len(data)>9999:
			raise ValueError("Too long data, max 9999, real %d"%len(data))
		self.send("%4d%s"%(len(data), data))

class HeartBeatReporter(threading.Thread):

        def __init__(self, host, port, interval):
		self.logger = logging.getLogger("root")
		threading.Thread.__init__(self)
		self.host = host
		self.port = port
		self.interval = interval
		self.__end = False
		self.__connect()	
	
	def run(self):
		while not self.__end:
			self.__write("ALIVE")
			time.sleep(self.interval)
		self.__write("END")
		try:
			self.__client.close()
		except socket.error:
			pass

	def end(self):
		self.__end = True

	def __connect(self):
		try:
			self.__client = NetClient(self.host, self.port)
		except socket.error as e:
			self.logger.error("Net error[%s:%d]: %s", self.host, self.port, e.strerror)
			raise e

	def __write(self, data):
		if self.logger.isEnabledFor(logging.INFO):
			self.logger.debug("Send %s to [%s:%d]", data, self.host, self.port)
		try:
			self.__client.write(data)
		except socket.error as e:
			self.logger.warn("Net error[$s:%d]: %s", self.host, self.port, e.strerror)
			try:
				self.__client.close()
			except socket.error:
				pass
			time.sleep(1)
			self.__connect()
			self.__client.write(data)

class TaskExecutor():
	def __init__(self, program, args, reportInterval=-1, controller=None, outputDir=None):
		self.program = program
		self.args = args
		self.outputDir = outputDir
		self.reportInterval = reportInterval
		self.controller = controller
		tmpPath = outputDir
		pathStack = []
		while not os.path.lexists(tmpPath):
			pathStack.insert(0, tmpPath)
			tmpPath = os.path.normpath(tmpPath)[:tmpPath.rfind(os.path.sep)]
		for tmpPath in pathStack:
			os.mkdir(tmpPath)
		initLogger(os.path.join(outputDir, 'executer.log'))
		self.logger = logging.getLogger("root")
		if self.logger.isEnabledFor(logging.INFO):
			self.logger.info("Execute task from %s [%s %s], output %s", controller, self.program, " ".join(self.args), self.outputDir)
		if reportInterval > 0:
			if controller is None:
				raise ValueError("Argument missed, controller is required")
			pair = controller.split(":")
			if len(pair) != 2:
				raise ValueError("Argument bad format, controller should be ip:port")
			if self.logger.isEnabledFor(logging.INFO):
				self.logger.info("Report to %s, interval %ds", controller, self.reportInterval)
			self.reporter = HeartBeatReporter(pair[0], int(pair[1]), reportInterval)
			self.reporter.start()
	
	def run(self):
		try:
			command = [self.program]
			for arg in self.args:
				command.append(arg)
			with open(os.path.join(self.outputDir, "__out__"), "w") as out:
				with open(os.path.join(self.outputDir, "__err__"), "w") as err:
					p = subprocess.Popen(command, stdout = out, stderr = err)
					r = p.wait()
					if self.logger.isEnabledFor(logging.INFO):
						self.logger.info("Execute task from %s end, return %d", self.controller, r)
		finally:
			if self.reportInterval > 0:
				self.reporter.end()

def initLogger(logFilePath):
#	Not supported in 2.6
#	config = {
#		'version': 1,
#		'disable_existing_loggers': True,
#		'formatters': {
#			'simple': {
#				'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
#			},
#		},
#		'handlers': {
#			'file': {
#				'level':'DEBUG',
#				'class':'logging.handlers.RotatingFileHandler',
#				'filename': logFilePath,
#				'formatter': 'simple',
#				'maxBytes': 1024*1024*20,  # 20MB
#				'backupCount': 1,
#			},
#		},
#		'loggers': {
#			'root': {
#				'handlers': ['file',],
#				'level': 'DEBUG',
#			},			
#		},
#		}
#	logging.config.dictConfig(config)
	simpleFormat = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
	logging.basicConfig(filename=logFilePath, format=simpleFormat, level=logging.DEBUG)

outputDir = None
reportInterval = -1
controller = None
index = 1
argc = len(sys.argv)
spawn = True
while index < argc:
	if sys.argv[index] == "--exec":
		index += 1
		break
	if sys.argv[index] == "--nospawn":
		spawn = False
	elif sys.argv[index] == "--output":
		index += 1
		outputDir = sys.argv[index]
	elif sys.argv[index] == "--controller":
		index += 1
		controller = sys.argv[index]
	elif sys.argv[index] == "--reportInterval":
		index += 1
		reportInterval = int(sys.argv[index])
	index += 1

if spawn:
	command = []
	command.append("python")
	command.append(sys.argv[0])
	command.append("--nospawn")
	for arg in sys.argv[1:]:
		command.append(arg)
	print "Spawn command [%s]"%" ".join(command)
	subprocess.Popen(command)
	#os.spawnvp(os.P_NOWAIT, command[0], command)
else:
	TaskExecutor(sys.argv[index], sys.argv[index+1:], reportInterval, controller, outputDir).run()		 
