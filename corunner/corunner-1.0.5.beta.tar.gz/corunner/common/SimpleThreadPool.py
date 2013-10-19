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


import threading
import Queue

class Task():
	def run(self):
		pass

class Worker(threading.Thread):
	def __init__(self, queue):
		threading.Thread.__init__(self)
		self.queue = queue
		self.end = False

	def run(self):
		while True:
			task = None
			try:
				task = self.queue.get(True, 1)
			except Exception:
				pass
			if task is not None:
				task.run()
				self.queue.task_done()
			if self.end:
				break

class SimpleThreadPool():
	def __init__(self, nWorker, nQueue=0):
		self.nWorker= nWorker
		self.nQueue = nQueue
		self.queue = Queue.Queue(nQueue)
		self.workers = []
		for i in range(nWorker):
			self.workers.append(self.__newWorker())
	
	def __newWorker(self):
		worker = Worker(self.queue)
		worker.setName("pool-worker-" + str(len(self.workers)))
		worker.setDaemon(True)
		worker.start()
		return worker
	
	def addTask(self, task, block=True, timeout=None):
		self.queue.put(task, block, timeout)

	def await(self):
		self.queue.join()

	def close(self):
		self.await()	
		for w in self.workers:
			w.end = True
