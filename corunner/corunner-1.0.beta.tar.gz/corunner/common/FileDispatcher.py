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


import os, logging
import shutil
import NetUtil
import FileUtil
import ShellUtil

class FileDispatcher:
	def __init__(self, targetIP, targetPort=22):
		self.logger = logging.getLogger()
		self.targetIP = targetIP
		self.targetPort = targetPort	

	def copyTo(self, localPath, remotePath):
		self.__copy(localPath, remotePath, self.targetIP, self.targetPort, True)
	
	def copyFrom(self, remotePath, localPath):
		self.__copy(localPath, remotePath, self.targetIP, self.targetPort, False)
	
	def __copy(self, localPath, remotePath, targetIP, targetPort, isOut):
		if NetUtil.isLocal(targetIP):
			if isOut:
				ShellUtil.execute(["mkdir", "-p", remotePath])
				ShellUtil.execute(["cp", "-r", localPath, remotePath])
			else:
				ShellUtil.execute(["mkdir", "-p", localPath])
				ShellUtil.execute(["cp", "-r", remotePath, localPath])
			#if FileUtil.getParent(localPath) == os.path.normpath(remotePath):
			#	self.logger.warn("Ignored same path %s %s", localPath, remotePath)
			#	return
						#if os.path.isdir(localPath):
				#if os.path.lexists(remotePath):
				#	self.logger.warn("Skip copying existed path %s %s", localPath, remotePath)
				#	return;
				#if self.logger.isEnabledFor(logging.DEBUG):
				#	self.logger.debug("cp -r %s %s", localPath, remotePath)
				#shutil.copytree(localPath, remotePath, True)
				#ShellUtil.execute(["cp", "-r", localPath, remotePath])
			#else:
				#if self.logger.isEnabledFor(logging.DEBUG):
				#	self.logger.debug("cp %s %s", localPath, remotePath)
				#shutil.copy(localPath, remotePath)
				#ShellUtil.execute(["cp", localPath, remotePath])
			return
		if isOut:
			mkdirCommand = ["ssh", "-p", str(targetPort), targetIP, "mkdir", "-p", remotePath]
			ShellUtil.execute(mkdirCommand)
		else:
			ShellUtil.execute(["mkdir", "-p", localPath])
		command = ["scp", "-P", str(targetPort)]
		if os.path.isdir(localPath):
			command.append("-r")
		if isOut:
			command.append(localPath)
		command.append("%s:%s"%(targetIP, remotePath))
		if not isOut:
			command.append(localPath)
		ShellUtil.execute(command)	
