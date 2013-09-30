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


import common.NetUtil as netutil
import common.ShellUtil as shellutil
import os

class TaskExecutorProxy:
	
	def __init__(self, config, targetIP, targetPort=22):
		self.targetIP = targetIP
		self.targetPort = targetPort
		self.config = config	

	def run(self, mainProgram, args):
		command = []
		if not netutil.isLocal(self.targetIP):
			command.append("ssh")
			command.append("-p")
			command.append(self.targetPort)
			command.append(self.targetIP)
		#command.append("nohup")
		command.append("python")
		command.append(os.path.join(self.config.nodeBinRoot(), "TaskExecutor.py"))
		command.append("--output")
		command.append(self.config.nodeOutputRoot())
		command.append("--reportInterval")
		command.append(str(self.config.reportInterval))
		command.append("--controller")
		command.append("%s:%d"%(netutil.getLocalIP(), self.config.listenPort))
		command.append("--exec")
		command.append(mainProgram)
		for arg in args:
			command.append(arg)
		shellutil.execute(command, nohup=True)
		
			
		
