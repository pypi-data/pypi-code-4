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


import subprocess, logging

def execute(commandList, printOutput=False):
	logger = logging.getLogger()
	strCommandList = []
	for c in commandList:
		strCommandList.append(str(c))
	if logger.isEnabledFor(logging.DEBUG):
		logger.debug("Run command [%s]", " ".join(strCommandList))
	p = subprocess.Popen(strCommandList, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#	This may cause OutOfMemory.
#	if printOutput:
#		print >> sys.stdout, p.stdout.read()
#	p.wait()
#	if printOutput:
#		print >> sys.stderr, p.stderr.read()
#	p.stdout.close()
#	p.stderr.close()
	try:
		# When printOuput, this child process can become zombie when the child process fork another process and exit.
		# Probably this is caused by the shared stdout object, which is occupied by the new forked process. 
		if printOutput:
			while True:
				line = p.stdout.readline()
				if not line:
					break
				print line,
		r = p.wait()
		if logger.isEnabledFor(logging.DEBUG):
			logger.debug("Run command [%s], Return %d", " ".join(strCommandList), r)
		if r != 0 or printOutput:
			errMessage = p.stderr.readline()
			errline = errMessage
			while True:
				if errline:
					print errline,
				else:
					break
				errline = p.stderr.readline()
		if r !=0 :
			raise IOError(errMessage.strip())
	finally:
		p.stderr.close()
		p.stdout.close()
