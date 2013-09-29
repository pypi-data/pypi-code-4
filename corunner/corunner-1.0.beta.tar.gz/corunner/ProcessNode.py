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


import time, logging

PROCESS_STATUS_NONE = 0
PROCESS_STATUS_STARTED = 1
PROCESS_STATUS_ALIVE = 2
PROCESS_STATUS_DEAD = 3 
PROCESS_STATUS_END = 9 

class ProcessNode:
	def __init__(self, node, port=22):
		self.logger = logging.getLogger()	
		self.node = node
		self.port = port
		self.status = PROCESS_STATUS_NONE
		self.lastAccessTime = time.time()

	def updateStatus(self, status):
		if self.logger.isEnabledFor(logging.DEBUG):
			self.logger.debug("Update node %s status %s", self.node, self.toStr(status))
		self.status = status
		self.lastAccessTime = time.time()

	def toStr(self, status):
		if status == 0:
			return "NONE"
		elif status == 1:
			return "STARTED"
		elif status == 2:
			return "ALIVE"
		elif status == 3:
			return "DEAD"
		elif status == 9:
			return "END"
		else:
			return "UNKNOWN"
			
