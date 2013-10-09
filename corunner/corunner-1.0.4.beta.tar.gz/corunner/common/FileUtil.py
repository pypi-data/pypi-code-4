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

def getParent(path):
	return os.path.normpath(path)[:path.rfind(os.path.sep)]

def mkdirs(path):
	tmpPath = path
	pathStack = []
	while not os.path.lexists(tmpPath):
		pathStack.insert(0, tmpPath)
		tmpPath = os.path.normpath(tmpPath)[:tmpPath.rfind(os.path.sep)]
	for tmpPath in pathStack:
		try:
			os.mkdir(tmpPath)
		except IOError:
			if os.path.lexists(tmpPath):
				continue
			else:
				raise
