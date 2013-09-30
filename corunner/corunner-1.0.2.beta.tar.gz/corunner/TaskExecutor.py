import sys
import time
import subprocess
import os
import asyncore, socket
import threading
import logging, logging.handlers, logging.config

class HeartBeatReporter(threading.Thread):

        def __init__(self, host, port, interval, executor):
		self.logger = logging.getLogger("root")
		threading.Thread.__init__(self)
		self.host = host
		self.port = port
		self.interval = interval
		self.__end = False
		self.executor = executor
		try:
			self.__connect()	
		except socket.error:
			raise
	
	def run(self):
		try:
			count = 0
			while not self.__end:
				self.__write("ALIVE", count)
				count += 1
				time.sleep(self.interval)
			self.__write("END")
		except:
			self.executor.kill()
		try:
			self.__client.close()
		except socket.error:
			pass

	def end(self):
		self.__end = True

	def __connect(self, retry=3):
		try:
			self.__client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.__client.settimeout(self.interval)
			self.__client.connect((self.host, self.port))
		except socket.error as e:
			if retry > 0:
				time.sleep(1)
				retry -= 1
				self.__connect(retry)
			elif retry == 0:
				self.logger.error("Net connect error[%s:%s]: %s"%(self.host, str(self.port), repr(e.strerror)))
				raise e

	def __write(self, data, count, retry=3):
		if self.logger.isEnabledFor(logging.INFO):
			self.logger.debug("Send %s to [%s:%d]"%(data, self.host, self.port))
		if len(data)>9999:
			raise ValueError("Too long data, max 9999, real %d"%len(data))
		while retry >= 0:
			try:
				self.__client.sendall("%4d%s"%(len(data), data))
				break
			except socket.error as e:
				if retry == 0:
					self.logger.error("Net write error[%s:%s]: %s"%(self.host, str(self.port), repr(e.strerror)))
					raise
				try:
					self.__client.close()
				except socket.error:
					pass
				retry -= 1	
				time.sleep(1)
				try:
					self.__connect(-1)
				except socket.error:
					continue

class TaskExecutor():
	def __init__(self, program, args, reportInterval=-1, controller=None, outputDir=None):
		self.program = program
		self.args = args
		self.outputDir = outputDir
		self.reportInterval = reportInterval
		self.controller = controller
		self.killSignal = False
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
			self.logger.info("Execute task from %s [%s %s], output %s"%(controller, self.program, " ".join(self.args), self.outputDir))
		if reportInterval > 0:
			if controller is None:
				raise ValueError("Argument missed, controller is required")
			pair = controller.split(":")
			if len(pair) != 2:
				raise ValueError("Argument bad format, controller should be ip:port")
			if self.logger.isEnabledFor(logging.INFO):
				self.logger.info("Report to %s, interval %ds"%(controller, self.reportInterval))
			self.reporter = HeartBeatReporter(pair[0], int(pair[1]), reportInterval, self)
			self.reporter.start()
	
	def run(self):
		try:
			command = [self.program]
			for arg in self.args:
				command.append(arg)
			with open(os.path.join(self.outputDir, "__out__"), "w") as out:
				with open(os.path.join(self.outputDir, "__err__"), "w") as err:
					p = subprocess.Popen(command, stdout = out, stderr = err)
					while p.poll() is None:
						if self.killSignal:
							p.kill()
							break
						time.sleep(1)
					if self.logger.isEnabledFor(logging.INFO):
						self.logger.info("Execute task from %s end, return %s"%(self.controller, repr(p.poll())))
		finally:
			if self.reportInterval > 0:
				self.reporter.end()
	
	def kill(self):
		self.killSignal = True


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
