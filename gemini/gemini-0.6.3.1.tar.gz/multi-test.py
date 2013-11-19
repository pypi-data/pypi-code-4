#! /usr/bin/env python
import random
import multiprocessing
import Queue
import time
import vcf
import sys
#  
# class Worker(multiprocessing.Process):
#  
#     def __init__(self, work_queue):
#  
#         # base class initialization
#         multiprocessing.Process.__init__(self)
#  
#         # job management stuff
#         self.work_queue    = work_queue
#         # self.result_queue  = result_queue
#         # self.kill_received = False
#  
#     def run(self):
#         while 1:
#  
#             # get a task
#             #job = self.work_queue.get_nowait()
#             try:
#                 var = self.work_queue.get_nowait()
#             except:
#                 break
#  
#             # the actual processing
#             print("Starting " + str(var.POS) + " ...")
#             # delay = random.randrange(1,3)
#             # time.sleep(delay)
#  
#             # store the result
#             #self.result_queue.put(var)
# 
# if __name__ == "__main__":
#  
#     num_jobs = 20
#     num_processes=4
# 
#     work_queue = multiprocessing.JoinableQueue()
#     vcf_reader = vcf.VCFReader(open(sys.argv[1]), 'rb')
#     for var in vcf_reader:
#         work_queue.put(var)
# 
#     for i in range(num_processes):
#         worker = Worker(work_queue)
#         worker.start()
#     
#     work_queue.join()
# 
#     # # collect the results off the queue
#     # results = []
#     # for i in range(num_jobs):
#     #     print(result_queue.get())
#     
#     import multiprocessing
#     import time

class ProcessConsumer(multiprocessing.Process):

    def __init__(self, task_queue, result_queue):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue

    def run(self):
        proc_name = self.name
        while True:
            next_task = self.task_queue.get()
            if next_task is None:
                # Poison pill means shutdown
                self.task_queue.task_done()
                break
            self.task_queue.task_done()
            # add the result of the Task's __call__
            # to the result queue
            self.result_queue.put(next_task())
        return


class Task(object):
    def __init__(self, var):
        self.var = var
    def __call__(self):
        return '%s' % (self.var)
    def __str__(self):
        return '%s' % (self.var)


if __name__ == '__main__':
    # Establish communication queues
    tasks = multiprocessing.JoinableQueue()
    results = multiprocessing.Queue()

    # Start consumers
    num_consumers = multiprocessing.cpu_count()
    print 'Creating %d consumers' % num_consumers
    consumers = [ ProcessConsumer(tasks, results)
                  for i in xrange(num_consumers) ]
    for w in consumers:
        w.start()

    # Enqueue jobs
    # num_jobs = 10
    # for i in xrange(num_jobs):
    #     tasks.put(Task(i, i))
    # Enqueue jobs        
    vcf_reader = vcf.VCFReader(open(sys.argv[1]), 'rb')
    for var in vcf_reader:
        tasks.put(Task(var))

    # Add a poison pill for each consumer
    for i in xrange(num_consumers):
        tasks.put(None)

    # Wait for all of the tasks to finish
    tasks.join()

    # Start printing results
    while 1:
        try: 
            result = results.get(False)
            print 'Result:', result
        except:
            break