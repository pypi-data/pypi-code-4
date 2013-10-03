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


import os

class Config():
	def __init__(self):
		self.listenPort = 9000
		self.reportInterval = 3
		self.nWorker = 3
		self.nodeRoorDir = "/tmp/corunner"

	def load(self, configFile):
		with open(configFile, "r") as f:
			lines = f.readlines()
			for line in lines:
				line = line.strip()
				if line.startswith("#") or len(line) == 0:
					continue
				s = line.split("=")
				if len(s) != 2:
					raise ValueError("Bad config item %s"%line)
				if s[0].strip() == "controller.worker.count":
					v = int(s[1].strip())
					if v < 1:
						raise ValueError("controller.worker.count should be at least 1, while get %d"%w)
					self.nWorker = v
				elif s[0].strip() == "executor.report.interval":
					v = int(s[1].strip())
					self.reportInterval = v	
				elif s[0].strip() == "controller.listen.port":
					v = int(s[1].strip())
					if v < 1:
						raise ValueError("controller.listen.port should be positive, while get %d"%w)
					self.listenPort = v
				elif s[0].strip() == "executor.root.default":
					self.nodeRootDir = s[1].strip()

	def nodeBinRoot(self):
		return os.path.join(self.nodeRootDir, "bin")

	def nodeOutputRoot(self):
		return os.path.join(self.nodeRootDir, "output")

	def string(self):
		return "[listenPort=%d, reportInterval=%d, nWorker=%d, nodeRootDir=%s]"%(self.listenPort, self.reportInterval, self.nWorker, self.nodeRootDir)
