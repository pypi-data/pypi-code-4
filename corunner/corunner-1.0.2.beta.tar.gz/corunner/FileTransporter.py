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
from common.FileDispatcher import *
import common.SimpleThreadPool as threadpool
import common.ArgumentParser as parser

class TransportTask(threadpool.Task):
	def __init__(self, processNode, source, target, isOut, divideTarget):
		self.logger = logging.getLogger()
		self.processNode = processNode
		self.source = source
		self.target = target
		self.isOut = isOut
		self.divideTarget = divideTarget

	def run(self):
		dispatcher = FileDispatcher(self.processNode.node, self.processNode.port)
		try:
			if self.isOut:
				dispatcher.copyTo(self.source, self.target)
			else:
				target = self.target
				if self.divideTarget:
					FileUtil.mkdirs(target)
					target = os.path.join(self.target, self.processNode.node)
				else:
					FileUtil.mkdirs(FileUtil.getParent(target))
				dispatcher.copyFrom(self.source, target)
		except IOError as e:
			self.logger.error("Error transport from %s: %s", self.processNode.node, e.message)

class FileTransporter:
	'''
	nodes: ip:port list
	source: source file or directory
	target: target file or directory
	isOut: direction of transport
	nWorker: thread number
	'''
	def __init__(self, hosts, source, target, isOut, divideTarget, nWorker):
		self.logger = logging.getLogger()
		self.source = source
		self.target = target
		self.isOut = isOut
		self.divideTarget = divideTarget
		self.nWorker = nWorker
		self.snodes = []
		if os.path.lexists(target) and not os.path.isdir(target):
			raise ValueError("Target should be a directory, path %s"%target)
		nodes = parser.parseHosts(hosts)
		for node in nodes:
			if node.find(":") > 0:
				pair = node.split(":")
				processNode = ProcessNode(pair[0], pair[1])
				self.snodes.append(processNode)
			else:
				processNode = ProcessNode(node)
				self.snodes.append(processNode)
		direction = "IN"
		if isOut:
			direction = "OUT"
		self.logger.info("FileTransporter init. Arguments:\n\tnodes:\t%s\n\tsource:\t%s\n\ttarget:\t%s\n\tdirect:\t%s\n\tthread:\t%d", hosts, source, target, direction, nWorker)
	
	'''
	Transport files.
	'''
	def execute(self):
		pool = threadpool.SimpleThreadPool(self.nWorker)
		try:	
			for snode in self.snodes:
				pool.addTask(TransportTask(snode, self.source, self.target, self.isOut, self.divideTarget))
		finally:
			pool.close()
		self.logger.info("FileTransporter end.")
		
def usage():
	print "Usage: %s -n [nodes] -s [sourceFile] -d [targetDir] -o|-i <--divide>"
	print '''Transport files from or to nodes concurrently.

-h, --help	show usage
-n		remote nodes to run concurrently, this is mandatory
-s		source file or directory
-d		target directory 
-i|-o		direction, -i means in, -o means out
-t		optional, thread number, 3 by default
--divide	optional, if set combined with -i, the target will be divided by the node's ip addr

Examples:
Copy file from /home/tom/log in remote nodes to local directory /home/tom/workspace/log:'''
	print sys.argv[0] + ' -n 127.0.0.1:2222..3,127.0.1.1..2,127.0.2.1 -s /home/tom/log -d /home/tom/workspace/log'

def main():
	configDir = os.path.join(os.path.dirname(__file__), "conf")
	logging.config.fileConfig(os.path.join(configDir, "logging.properties"))
	hosts = None
	source = None
	target = None
	isOut = False
	isIn = False
	divide = False
	nWorker = 3
	nIdx = 1
	while nIdx < len(sys.argv):
		if sys.argv[nIdx] == "-h" or sys.argv[nIdx] == "--help":
			break
		elif sys.argv[nIdx] == "-n":
			nIdx += 1
			hosts = sys.argv[nIdx]
		elif sys.argv[nIdx] == "-s":
			nIdx += 1
			source = sys.argv[nIdx] 
		elif sys.argv[nIdx] == "-d":
			nIdx += 1
			target = sys.argv[nIdx] 
		elif sys.argv[nIdx] == "-t":
			nIdx += 1
			nWorker = int(sys.argv[nIdx]) 
		elif sys.argv[nIdx] == "-i":
			isIn = True
		elif sys.argv[nIdx] == "-o":
			isOut = True
		elif sys.argv[nIdx] == "--divide":
			divide = True
		nIdx += 1
	if hosts is None or source is None or target is None or isIn == isOut:
		usage()
		sys.exit(0)
	FileTransporter(hosts, source, target, isOut, divide, nWorker).execute()

if __name__ == "__main__":
	main()	
