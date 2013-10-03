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


import os,sys,threading, time, logging, logging.config
from ProcessNode import *
from TaskExecutorProxy import *
from Config import *
import HeartBeatReceiver as hb
from common.FileDispatcher import *
import common.SimpleThreadPool as threadpool
import common.ArgumentParser as parser

class ExecuteTask(threadpool.Task):
	def __init__(self, processNode, programFile, mainProgram, args, config):
		self.logger = logging.getLogger()
		self.programFile = programFile
		self.config = config
		self.processNode = processNode
		self.mainProgram = mainProgram
		self.args = args
	def run(self):
		dispatcher = FileDispatcher(self.processNode.node, self.processNode.port)
		try:
			home = os.path.dirname(__file__)
			dispatcher.copyTo(os.path.join(home, "TaskExecutor.py"), self.config.nodeBinRoot())
			if self.programFile is not None:
				dispatcher.copyTo(self.programFile, self.config.nodeRootDir, False)
			proxy = TaskExecutorProxy(
				self.config, 
				self.processNode.node, 
				self.processNode.port)
			proxy.run(self.mainProgram, self.args)
			if self.config.reportInterval > 0:
				self.processNode.updateStatus(PROCESS_STATUS_STARTED)
		except IOError as e:
			self.logger.error("Error execute in %s: %s", self.processNode.node, e.message)
			if self.config.reportInterval > 0:
				self.processNode.updateStatus(PROCESS_STATUS_DEAD)

class TaskController:
	'''
	nodes: ip:port list,
	config: configuration, load from conf/corunner.properties by default, or specified through arguments.
	programFile: a file or directory required to run in the remote node, this can be None if no program file needs to be delivered.
	'''
	def __init__(self, hosts, config, programFile=None):
		self.logger = logging.getLogger()
		self.programFile = programFile
		self.config = config
		self.snodes = []
		self.snodemap = {}
		nodes = parser.parseHosts(hosts)
		for node in nodes:
			if node.find(":") > 0:
				pair = node.split(":")
				processNode = ProcessNode(pair[0], pair[1])
				self.snodes.append(processNode)
			else:
				processNode = ProcessNode(node)
				self.snodes.append(processNode)
			self.snodemap[processNode.node] = processNode
		if self.config.reportInterval>0 :
			self.__hbReceiver = hb.HeartBeatReceiver(self.config.listenPort)
			self.__hbReceiver.start()
		self.logger.info("TaskController init. Config: %s.\nArguments:\n\tnodes: %s\n\tprogramFile: %s", config.string(), hosts, programFile)
	
	'''
	Execute the mainProgram with args in remote nodes
	'''
	def execute(self, mainProgram, args):
		pool = threadpool.SimpleThreadPool(self.config.nWorker)
		try:	
			# None blocking, the queue size is unlimited. This is resonable for the node number can not be too large(ten thousands of?). 
			for snode in self.snodes:
				pool.addTask(ExecuteTask(snode, self.programFile, mainProgram, args, self.config))
			if self.config.reportInterval > 0:
				while True:
					status = self.queryStatus()	
					if self.logger.isEnabledFor(logging.INFO):
						self.logger.info("NONE:%5d  STARTED:%5d  ALIVE:%5d  DEAD:%5d  END:%5d"%(status["NONE"], status["STARTED"], status["ALIVE"], status["DEAD"], status["END"]))
					if status["NONE"] == 0 and status["STARTED"] == 0 and status["ALIVE"] == 0:
						break
					now = time.time()
					while True:
						if time.time() - now > 10:
							break
						nodeStatus = self.__hbReceiver.get(1)
						if nodeStatus is None:
							if time.time() - now < 3:
								time.sleep(1)
								continue
							else:
								break
						snode = self.snodemap[nodeStatus.addr[0]]
						if nodeStatus.status == "ALIVE":
							snode.updateStatus(PROCESS_STATUS_ALIVE)
						elif nodeStatus.status == "END":
							snode.updateStatus(PROCESS_STATUS_END)
		finally:
			pool.close()
		self.logger.info("Task controller end.")

	'''
	Query status of all nodes, also mark those timed out nodes.
	'''
	def queryStatus(self):
		now = time.time()
		status = {"NONE": 0, "STARTED": 0, "ALIVE": 0, "DEAD": 0, "END": 0}
		for snode in self.snodes:
			if snode.status == PROCESS_STATUS_NONE:
				status["NONE"] = status["NONE"] + 1
			elif snode.status == PROCESS_STATUS_STARTED or snode.status == PROCESS_STATUS_ALIVE :
				if snode.status == PROCESS_STATUS_STARTED:
					status["STARTED"] = status["STARTED"] + 1
				else:
					status["ALIVE"] = status["ALIVE"] + 1
				if now - snode.lastAccessTime > self.config.reportInterval * 3:
					self.logger.error("Timeout %s, over %ds", snode.node, now - snode.lastAccessTime)
					snode.updateStatus(PROCESS_STATUS_DEAD)
			elif snode.status == PROCESS_STATUS_END:
				status["END"] = status["END"] + 1
			else:
				status["DEAD"] = status["DEAD"] + 1
		return status
	
def usage():
	print "Usage: %s -n [nodes] <-f [programFile]> <-r [nodeRootDir]> <-i [reportInterval]> command"%sys.argv[0]
	print '''Dispatch program files to remote nodes and execute in remote concurrently

-h, --help	show usage
-c		config file, default conf/corunner.properties. If this is not specified, the arguments 
		can overwrite the default config.
-n		remote nodes to run concurrently, this is mandatory
-f		program files need to be transfered to the remote nodes, this can be a file or directory.
-r		root directory in remote to put the program files in, default "/tmp/corunner" 
-t		worker thread number, default 3
-l		listen port to receive heartbeat report, default 9000
-i		heartbeat interval of remote nodes. There will be no heartbeat if this is not set

Examples:
Search characters "abc" in the remote file log.txt:'''
	print sys.argv[0] + ' -n 127.0.0.1:2222..3,127.0.1.1..2,127.0.2.1 grep "abc" log.txt'

def main():
	configDir = os.path.join(os.path.dirname(__file__), "conf")
	logging.config.fileConfig(os.path.join(configDir, "logging.properties"))
	hosts = None
	programFile = None
	commandList = []
	configFile = None
	nIdx = 1
	config = Config()
	config.load(os.path.join(configDir, "corunner.properties"))
	while nIdx < len(sys.argv):
		if sys.argv[nIdx] == "-h" or sys.argv[nIdx] == "--help":
			break
		elif sys.argv[nIdx] == "-n":
			nIdx += 1
			hosts = sys.argv[nIdx]
		elif sys.argv[nIdx] == "-f":
			nIdx += 1
			programFile = sys.argv[nIdx] 
		elif sys.argv[nIdx] == "-c":
			nIdx += 1
			configFile = sys.argv[nIdx] 
		elif sys.argv[nIdx] == "-r":
			nIdx += 1
			config.nodeRootDir = sys.argv[nIdx] 
		elif sys.argv[nIdx] == "-l":
			nIdx += 1
			config.listenPort = int(sys.argv[nIdx])
		elif sys.argv[nIdx] == "-i":
			nIdx += 1
			config.reportInterval = int(sys.argv[nIdx])
		elif sys.argv[nIdx] == "-t":
			nIdx += 1
			config.nWorker = int(sys.argv[nIdx])
		else:
			while nIdx < len(sys.argv):
				commandList.append(sys.argv[nIdx])
				nIdx += 1
			break
		nIdx += 1
	if hosts is None:
		usage()
		sys.exit(0)
	if configFile is not None:
		config.load(configFile)
	TaskController(hosts, config, programFile).execute(commandList[0], commandList[1:])

if __name__ == "__main__":
	main()


